import operator
import cv2
import os
import numpy as np
from PIL import Image, UnidentifiedImageError
import shutil
import xml.etree.ElementTree as ET
import time
import traceback
import hashlib
from importlib import import_module

from pathlib import Path
from multiprocessing import Pool, pool, TimeoutError as MPTimeoutError
from PySide6.QtCore import QObject, Signal, Slot

from algorithms.AlgorithmService import AnalysisResult
from core.services.LoggerService import LoggerService
from core.services.advancedFeatures.HistogramNormalizationService import HistogramNormalizationService
from core.services.advancedFeatures.KMeansClustersService import KMeansClustersService
from core.services.XmlService import XmlService
# Algorithm services imported lazily in process_file() to avoid worker startup overhead


# Maximum wall-clock time to wait for any single image's analysis result. A
# worker process that crashes or wedges on a problematic image hits this
# limit; that image is recorded as failed and the run continues, instead of
# the whole analysis hanging forever.
PROCESS_TIMEOUT_SECONDS = 300

# Granularity for polling a worker result. Cancellation terminates the pool,
# which leaves any in-flight AsyncResult permanently unset; waiting for it with
# one long get(timeout=PROCESS_TIMEOUT_SECONDS) would stall the whole run for
# the full timeout before the cancel is noticed. Polling in short slices lets
# the retrieval loop react to a cancel within a fraction of a second while
# still enforcing the real per-image timeout budget for a wedged worker.
RESULT_POLL_INTERVAL_SECONDS = 0.2


class _AnalysisCancelled(Exception):
    """Internal signal that the run was cancelled while awaiting a result."""


class AnalyzeService(QObject):
    """Service to process images using a selected algorithm.

    Coordinates multi-process image analysis with progress tracking, caching,
    and result export. Supports various algorithms and processing options.

    Attributes:
        sig_msg: Signal emitted with status messages (str).
        sig_aois: Signal emitted when AOIs are found.
        sig_done: Signal emitted when processing completes (id, total, message).
    """

    # Signals to send info back to the GUI
    sig_msg = Signal(str)
    sig_aois = Signal()
    sig_done = Signal(int, int, str)
    # Emitted as images finish: (completed_count, total_count, eta_seconds).
    sig_progress = Signal(int, int, float)

    def __init__(self, id, algorithm, input, output, identifier_color, min_area, num_processes,
                 max_aois, aoi_radius, histogram_reference_path, kmeans_clusters, options, max_area,
                 processing_resolution=1.0, recursive=True):
        """Initialize the AnalyzeService with parameters for processing images.

        Args:
            id: Numeric ID for this analysis session.
            algorithm: Dictionary specifying the algorithm for analysis.
            input: Path to the input directory containing images.
            output: Path to the output directory where processed images will be stored.
            identifier_color: RGB values to highlight areas of interest.
            min_area: Minimum size in pixels for an object to be considered an area of interest.
            num_processes: Number of concurrent processes for image processing.
            max_aois: Maximum areas of interest threshold in a single image before issuing a warning.
            aoi_radius: Radius added to the minimum enclosing circle around areas of interest.
            histogram_reference_path: Path to the histogram reference image.
            kmeans_clusters: Number of clusters (colors) to retain in the image.
            options: Additional algorithm-specific options.
            max_area: Maximum area in pixels for an object to qualify as an area of interest.
            processing_resolution: Percentage to scale images (0.1 to 1.0).
                1.0 means process at original resolution (no scaling). Defaults to 1.0.
            recursive: When True, images are collected from the input directory and
                all of its subdirectories. When False, only files directly inside the
                input directory are processed -- used by batch mode so each folder is
                analyzed as an independent batch. Defaults to True.
        """
        self.logger = LoggerService()
        self.xmlService = XmlService()
        super().__init__()
        self.algorithm = algorithm
        self.input = input
        self.output_dir = output
        self.output = os.path.join(output, "ADIAT_Results")
        self.identifier_color = identifier_color
        self.options = options
        self.min_area = min_area
        self.max_area = max_area
        self.processing_resolution = processing_resolution
        self.recursive = recursive
        self.aoi_radius = aoi_radius
        self.num_processes = num_processes
        self.max_aois = max_aois
        self.max_aois_limit_exceeded = False
        self.hist_ref_path = histogram_reference_path
        self.kmeans_clusters = kmeans_clusters
        self.__id = id
        self.images_with_aois = []
        self.cancelled = False
        # Wall-clock start of process_files(), used for ETA calculation.
        self._start_time = time.time()
        self._completed_images = 0
        self.ttl_images = 0
        self.is_thermal = (self.algorithm['type'] == 'Thermal')
        self.pool = Pool(self.num_processes)

    @Slot()
    def process_files(self):
        """Process all files in the input directory using the selected algorithm and settings.

        Sets up output directories, processes images in parallel, generates AOI
        caches, and exports results to XML. Emits progress signals throughout.
        """
        try:
            self._setup_output_dir()
            self.xmlService.add_settings_to_xml(
                input_dir=self.input,
                output_dir=self.output_dir,
                identifier_color=self.identifier_color,
                aoi_radius=self.aoi_radius,
                algorithm=self.algorithm['name'],
                thermal=self.is_thermal,
                num_processes=self.num_processes,
                min_area=self.min_area,
                max_area=self.max_area,
                hist_ref_path=self.hist_ref_path,
                kmeans_clusters=self.kmeans_clusters,
                options=self.options
            )

            image_files = []

            self._start_time = time.time()
            # In batch mode each folder is analyzed independently, so collection
            # can be scoped to the input directory itself (no recursion).
            if self.recursive:
                walker = os.walk(self.input)
            else:
                walker = [(self.input, [], os.listdir(self.input))]
            for subdir, dirs, files in walker:
                for file in files:
                    file_path = Path(file)
                    if self.is_thermal and file_path.suffix != 'irg':
                        image_files.append(os.path.join(subdir, file))
                    elif not self.is_thermal:
                        image_files.append(os.path.join(subdir, file))

            self.ttl_images = len(image_files)
            self.sig_msg.emit(
                self.tr("Processing {count} files").format(count=self.ttl_images)
            )

            self._completed_images = 0
            self._total_aois = 0

            # Queue each image for multiprocessing, keeping its AsyncResult so
            # the result can later be retrieved with a timeout.
            pending = []
            for file in image_files:
                if os.path.isdir(file):
                    self.ttl_images -= 1
                    continue
                if self.pool._state == pool.RUN:
                    try:
                        with Image.open(file) as img:
                            img.verify()  # Check if it's a valid image
                        is_valid_image = True
                    except (UnidentifiedImageError, OSError):
                        is_valid_image = False

                    if is_valid_image and self.pool._state == pool.RUN:
                        async_result = self.pool.apply_async(
                            AnalyzeService.process_file,
                            (
                                self.algorithm,
                                self.identifier_color,
                                self.min_area,
                                self.max_area,
                                self.aoi_radius,
                                self.options,
                                file,
                                self.input,
                                self.output,
                                self.hist_ref_path,
                                self.kmeans_clusters,
                                self.is_thermal,
                                self.processing_resolution
                            )
                        )
                        pending.append((file, async_result))
                    else:
                        self.ttl_images -= 1
                        self.sig_msg.emit(
                            self.tr("Skipping {file} :: File is not an image").format(file=file)
                        )

            # Notify that images are queued and processing has started
            self.sig_msg.emit(
                self.tr("All {count} images queued, processing started...").format(count=self.ttl_images)
            )

            # No more tasks will be submitted; workers drain the queue.
            self.pool.close()

            # Retrieve each result with a per-image timeout. Doing the wait
            # here -- instead of a fire-and-forget callback plus an unbounded
            # pool.join() -- means a single image whose worker crashes or
            # never returns can no longer wedge the entire run. Such an image
            # is recorded as a failure and processing continues with the rest.
            for file, async_result in pending:
                if self.cancelled:
                    break
                try:
                    result = self._await_result(async_result)
                except _AnalysisCancelled:
                    # Cancel was requested while waiting; stop retrieving
                    # results and fall through to pool teardown below.
                    break
                except MPTimeoutError:
                    self._handle_failed_image(
                        file, f"Processing exceeded {PROCESS_TIMEOUT_SECONDS}s and was skipped"
                    )
                    continue
                except Exception as e:
                    if self.cancelled:
                        break
                    self._handle_failed_image(file, str(e))
                    continue
                if result is None:
                    self._handle_failed_image(file, "No result returned (see log for details)")
                    continue
                self._process_complete(result)

            # terminate() rather than join(): a worker still stuck on a bad
            # image would make join() hang forever -- the exact failure being
            # fixed here. The stuck worker is killed; finished work is kept.
            self.pool.terminate()
            self.pool.join()

            # Generate the output XML with the information gathered during processing
            self.images_with_aois = sorted(self.images_with_aois, key=operator.itemgetter('path'))

            # Set the XML path before adding images so relative paths can be calculated
            file_path = os.path.join(self.output, "ADIAT_Data.xml")
            self.xmlService.xml_path = file_path

            # Assign persisted run-wide unique AOI numbers before serialisation.
            self.assign_aoi_numbers(self.images_with_aois)

            for img in self.images_with_aois:
                self.xmlService.add_image_to_xml(img)

            self.xmlService.save_xml_file(file_path)
            ttl_time = round(time.time() - self._start_time, 3)
            self.sig_done.emit(self.__id, len(self.images_with_aois), file_path)
            self.sig_msg.emit(
                self.tr("{images} images with {aois} areas of interest identified").format(
                    images=len(self.images_with_aois),
                    aois=self._total_aois,
                )
            )
            self.sig_msg.emit(
                self.tr("Total Processing Time: {seconds} seconds").format(seconds=ttl_time)
            )
            self.sig_msg.emit(
                self.tr("Total Images Processed: {count}").format(count=self.ttl_images)
            )

        except Exception as e:
            self.logger.error(traceback.format_exc())
            self.logger.error(f"An error occurred during processing: {e}")

    @staticmethod
    def assign_aoi_numbers(images_with_aois):
        """Assign run-wide unique AOI numbers across all analyzed images.

        Numbers are 1-based and increase in image order, then in the order
        AOIs appear within each image, matching the sequence the viewer
        displays them. The number is persisted with each AOI so reviewers
        can track a specific AOI across sort changes and view switches.

        Args:
            images_with_aois: List of image dicts, each carrying an 'aois' list.
        """
        aoi_number = 1
        for image in images_with_aois or []:
            for aoi in image.get('aois', []):
                aoi['number'] = aoi_number
                aoi_number += 1

    @staticmethod
    def _resolve_algorithm_service_class(algorithm):
        """Resolve an algorithm service class using naming conventions.

        Args:
            algorithm: Algorithm configuration dictionary.

        Returns:
            The resolved algorithm service class.

        Raises:
            ValueError: If configuration is incomplete or the service cannot be resolved.
        """
        algorithm_name = algorithm.get('name')
        service_name = algorithm.get('service')
        if not algorithm_name or not service_name:
            raise ValueError(
                "Algorithm config missing required fields: 'name' and 'service'"
            )

        # Backward-compatibility alias for legacy typo in historical configs.
        name_aliases = {
            'AIPersonDetetor': 'AIPersonDetector',
        }
        candidate_names = [algorithm_name]
        if algorithm_name in name_aliases:
            candidate_names.append(name_aliases[algorithm_name])

        last_error = None
        for candidate_name in candidate_names:
            module_name = f'algorithms.images.{candidate_name}.services.{service_name}'
            try:
                module = import_module(module_name)
                service_cls = getattr(module, service_name, None)
                if service_cls is None:
                    last_error = AttributeError(
                        f"Service class '{service_name}' not found in module '{module_name}'"
                    )
                    continue
                return service_cls
            except Exception as exc:
                last_error = exc

        raise ValueError(f"Unknown algorithm service: {service_name}") from last_error

    @staticmethod
    def process_file(algorithm, identifier_color, min_area, max_area, aoi_radius, options, full_path, input_dir, output_dir, hist_ref_path, kmeans_clusters,
                     thermal, processing_resolution=1.0):
        """Process a single image using the selected algorithm and settings.

        Applies histogram normalization and k-means clustering if specified,
        then processes the image with the selected algorithm. Generates
        thumbnails and caches for detected areas of interest.

        Args:
            algorithm: Dictionary specifying the algorithm for analysis.
            identifier_color: RGB values for highlighting areas of interest.
            min_area: Minimum size in pixels for an object to be considered an area of interest.
            max_area: Maximum size in pixels for an object to be considered an area of interest.
            aoi_radius: Radius added to the minimum enclosing circle around areas of interest.
            options: Additional algorithm-specific options.
            full_path: Path to the image file being analyzed.
            input_dir: Path to the input directory containing images.
            output_dir: Path to the output directory for processed images.
            hist_ref_path: Path to the histogram reference image.
            kmeans_clusters: Number of clusters (colors) to retain in the image.
            thermal: Whether this is a thermal image algorithm.
            processing_resolution: Percentage to scale images (0.1 to 1.0).
                1.0 = no scaling. Defaults to 1.0.

        Returns:
            AnalysisResult containing processed image path, areas of interest,
            and error message if any.
        """
        try:
            img = cv2.imdecode(np.fromfile(full_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            if img is None:
                raise ValueError(f"Could not load image: {full_path}")

            # Store original image for thumbnail generation (before scaling)
            original_img = img.copy()

            # Store original dimensions for coordinate transformation
            original_height, original_width = img.shape[:2]
            scale_factor = 1.0

            # Apply percentage-based resolution scaling if specified
            if processing_resolution is not None and processing_resolution < 1.0:
                scale_factor = processing_resolution
                new_width = int(original_width * scale_factor)
                new_height = int(original_height * scale_factor)

                # Ensure minimum dimensions of at least 10 pixels
                if new_width >= 10 and new_height >= 10:
                    # Use INTER_AREA for best quality when downscaling
                    img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)

                    # Scale area thresholds to match processing resolution (area scales by factor²)
                    min_area = int(min_area * scale_factor * scale_factor)
                    max_area = int(max_area * scale_factor * scale_factor) if max_area > 0 else 0
                else:
                    # Image too small to scale, process at original resolution
                    scale_factor = 1.0

            if not thermal:
                # Apply histogram normalization if a reference image is provided
                histogram_service = None
                if hist_ref_path is not None:
                    histogram_service = HistogramNormalizationService(hist_ref_path)
                    img = histogram_service.match_histograms(img)

                # Apply k-means clustering if specified
                kmeans_service = None
                if kmeans_clusters is not None:
                    kmeans_service = KMeansClustersService(kmeans_clusters)
                    img = kmeans_service.generate_clusters(img)

            # Instantiate the algorithm service lazily in the worker process.
            cls = AnalyzeService._resolve_algorithm_service_class(algorithm)
            instance = cls(identifier_color, min_area, max_area, aoi_radius, algorithm['combine_overlapping_aois'], options)
            instance.set_scale_factor(scale_factor)  # Pass scale factor to algorithm for coordinate transformation
            result = instance.process_image(img, full_path, input_dir, output_dir)

            # Store original image dimensions on the result
            if result:
                result.image_width = original_width
                result.image_height = original_height

            # Transform AOI coordinates from processing resolution back to original resolution
            if result and result.areas_of_interest and scale_factor < 1.0:
                result.areas_of_interest = instance.transform_aois_to_original_resolution(result.areas_of_interest)

            if result and result.areas_of_interest:
                # Generate main image thumbnail (using original resolution image)
                try:
                    AnalyzeService._generate_main_image_thumbnail(original_img, full_path, output_dir, input_root=input_dir)
                except Exception as thumb_error:
                    logger = LoggerService()
                    logger.warning(f"Main thumbnail generation failed for {full_path}: {thumb_error}")
                # Generate thumbnail and color cache for detected AOIs (using original resolution image)
                try:
                    # Call cache generation with original (unscaled) image for best quality thumbnails
                    instance.generate_aoi_cache(
                        img=original_img,
                        image_path=full_path,
                        areas_of_interest=result.areas_of_interest,
                        output_dir=output_dir,
                        thermal=thermal
                    )
                except Exception as cache_error:
                    # Don't fail detection if cache generation fails
                    logger = LoggerService()
                    logger.warning(f"Cache generation failed for {full_path}: {cache_error}")

            return result

        except Exception as e:
            logger = LoggerService()
            logger.error(traceback.format_exc())
            logger.error(f"Error processing image {full_path}: {e}")
            return AnalysisResult(input_path=full_path, error_message=str(e))

    @Slot()
    def _process_complete(self, result):
        """Handle completion of an image processing task.

        Updates progress counters, checks for max AOI limits, and emits
        signals for GUI updates.

        Args:
            result: Result object from the process_file method. A None result
                is tolerated and ignored -- it previously raised here and, on
                the pool's result thread, hung the run.
        """
        # process_file returns None on a caught error. A None used to raise an
        # AttributeError below; on the pool's result thread that killed the
        # thread and hung pool.join() forever.
        if result is None:
            return

        file_name = "Unknown"
        if result.input_path is not None:
            file_name = Path(result.input_path).name

        # Every finished image -- success or error -- counts toward progress so
        # the reported percentage reaches 100%.
        self._completed_images += 1
        percent_complete = int(100 * self._completed_images / self.ttl_images) if self.ttl_images else 100
        self._emit_progress()

        # Handle errors reported by the algorithm.
        if result.error_message is not None:
            self.sig_msg.emit(
                self.tr("Unable to process {file} :: {error} ({percent}%)").format(
                    file=file_name,
                    error=result.error_message,
                    percent=percent_complete,
                )
            )
            return

        # Add successfully processed image to results
        if result.areas_of_interest:
            # Include original path for mask-based approach
            image_data = {
                "path": result.output_path,  # This will be the mask path
                "original_path": result.input_path,  # Original image path
                "aois": result.areas_of_interest,
                "width": result.image_width,
                "height": result.image_height
            }
            self.images_with_aois.append(image_data)

            num_aois = len(result.areas_of_interest)
            self._total_aois += num_aois
            self.sig_msg.emit(
                self.tr("{count} areas of interest identified in {file} ({percent}%)").format(
                    count=num_aois,
                    file=file_name,
                    percent=percent_complete,
                )
            )

            # Guard against None and ensure integers for comparison
            if (result.base_contour_count is not None
                    and isinstance(result.base_contour_count, (int, np.integer))
                    and isinstance(self.max_aois, (int, np.integer))
                    and result.base_contour_count > int(self.max_aois)
                    and not self.max_aois_limit_exceeded):
                self.sig_aois.emit()
                self.max_aois_limit_exceeded = True
        else:
            self.sig_msg.emit(
                self.tr("No areas of interest identified in {file} ({percent}%)").format(
                    file=file_name,
                    percent=percent_complete,
                )
            )

    def _handle_failed_image(self, file_path, reason):
        """Record an image that could not be processed and keep the run going.

        Used when a worker times out, crashes, or returns no result. The image
        still counts toward the completion total so progress reporting reaches
        100%; it simply contributes no areas of interest.

        Args:
            file_path: Path to the image that failed.
            reason: Human-readable explanation, written to the log and the GUI.
        """
        self._completed_images += 1
        percent_complete = int(100 * self._completed_images / self.ttl_images) if self.ttl_images else 100
        self._emit_progress()
        file_name = Path(file_path).name
        message = f"Unable to process {file_name} :: {reason} ({percent_complete}%)"
        self.sig_msg.emit(message)
        self.logger.error(message)

    def _emit_progress(self):
        """Emit sig_progress with the current count and an ETA estimate.

        The ETA assumes each remaining image takes, on average, as long as the
        images already processed.
        """
        elapsed = time.time() - self._start_time
        remaining = max(0, self.ttl_images - self._completed_images)
        if self._completed_images > 0 and remaining > 0 and elapsed > 0:
            eta = elapsed / self._completed_images * remaining
        else:
            eta = 0.0
        self.sig_progress.emit(self._completed_images, self.ttl_images, eta)

    def _await_result(self, async_result):
        """Wait for a worker's result while staying responsive to cancellation.

        Polls the AsyncResult in short slices (RESULT_POLL_INTERVAL_SECONDS)
        instead of a single long blocking get(). Cancellation terminates the
        pool, which leaves an in-flight AsyncResult permanently unset; without
        polling, the retrieval loop would block for the full
        PROCESS_TIMEOUT_SECONDS before noticing the cancel, leaving the UI
        stuck on "Cancelling Image Processing". The real per-image timeout
        budget is still enforced for a genuinely wedged worker.

        Args:
            async_result: The multiprocessing AsyncResult to wait on.

        Returns:
            The worker's return value.

        Raises:
            _AnalysisCancelled: If cancellation was requested while waiting.
            multiprocessing.TimeoutError: If PROCESS_TIMEOUT_SECONDS elapses.
            Exception: Whatever the worker raised, propagated by get().
        """
        deadline = time.monotonic() + PROCESS_TIMEOUT_SECONDS
        while True:
            if self.cancelled:
                raise _AnalysisCancelled()
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise MPTimeoutError()
            try:
                return async_result.get(timeout=min(RESULT_POLL_INTERVAL_SECONDS, remaining))
            except MPTimeoutError:
                # This poll slice elapsed with no result; loop to re-check the
                # cancel flag and the real per-image deadline.
                continue

    @Slot()
    def process_cancel(self):
        """Cancel any ongoing asynchronous processes.

        Sets cancellation flag and terminates the process pool.
        """
        self.cancelled = True
        self.sig_msg.emit(self.tr("--- Cancelling Image Processing ---"))
        self.pool.terminate()

    @staticmethod
    def _generate_main_image_thumbnail(img, image_path, output_dir, input_root=None):
        """Generate a thumbnail for the main image to speed up viewer loading.

        Creates a thumbnail image (max 100x56) maintaining aspect ratio and
        stores it in the .thumbnails directory with a hash-based filename.

        Args:
            img: Original image array (before any scaling).
            image_path: Path to the source image.
            output_dir: Output directory where thumbnail folder will be created.
            input_root: Optional input root directory for generating relative paths.
        """
        try:
            # Create thumbnail directory
            thumb_dir = Path(output_dir) / '.thumbnails'
            thumb_dir.mkdir(parents=True, exist_ok=True)

            # Generate stable key by hashing the relative input path to avoid collisions
            rel_key_source = None
            try:
                if input_root:
                    rel = Path(image_path)
                    rel_key_source = str(rel.relative_to(Path(input_root)))
            except Exception:
                try:
                    rel_key_source = os.path.relpath(image_path, input_root) if input_root else None
                except Exception:
                    rel_key_source = None

            if not rel_key_source:
                rel_key_source = os.path.basename(image_path)

            norm_key = rel_key_source.replace('\\', '/').lower()
            path_hash = hashlib.md5(norm_key.encode()).hexdigest()
            thumb_filename = f"{path_hash}.jpg"
            thumb_path = thumb_dir / thumb_filename

            # Convert to RGB if needed
            if len(img.shape) == 2:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            elif img.shape[2] == 4:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
            else:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Calculate thumbnail dimensions maintaining aspect ratio (max 100x56)
            max_width, max_height = 100, 56
            height, width = img_rgb.shape[:2]
            aspect_ratio = width / height

            if aspect_ratio > (max_width / max_height):
                # Image is wider - fit to width
                thumb_width = max_width
                thumb_height = int(max_width / aspect_ratio)
            else:
                # Image is taller - fit to height
                thumb_height = max_height
                thumb_width = int(max_height * aspect_ratio)

            # Resize using cv2 - use INTER_AREA for downscaling (faster and better quality)
            thumb_img = cv2.resize(img_rgb, (thumb_width, thumb_height), interpolation=cv2.INTER_AREA)

            # Convert RGB back to BGR for cv2.imwrite (cv2 expects BGR format)
            thumb_img_bgr = cv2.cvtColor(thumb_img, cv2.COLOR_RGB2BGR)

            # Save as JPEG with balanced quality (80 = good balance of quality and speed)
            cv2.imwrite(str(thumb_path), thumb_img_bgr, [cv2.IMWRITE_JPEG_QUALITY, 80])

        except Exception:
            # Don't fail processing if thumbnail generation fails
            pass

    def _setup_output_dir(self):
        """Create the output directory for storing processed images.

        Removes existing output directory if present and creates a new one.
        Logs errors if directory creation fails.
        """
        try:
            if os.path.exists(self.output):
                shutil.rmtree(self.output)
            os.makedirs(self.output)
        except Exception as e:
            self.logger.error(e)
