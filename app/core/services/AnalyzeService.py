import operator
import cv2
import os
import numpy as np
from PIL import Image, UnidentifiedImageError
import shutil
import xml.etree.ElementTree as ET
import time
import traceback

from pathlib import Path
from multiprocessing import Pool, pool
from PySide6.QtCore import QObject, Signal, Slot

from core.services.LoggerService import LoggerService
from core.services.HistogramNormalizationService import HistogramNormalizationService
from core.services.KMeansClustersService import KMeansClustersService
from core.services.XmlService import XmlService
from algorithms.ColorRange.services.ColorRangeService import ColorRangeService
from algorithms.RXAnomaly.services.RXAnomalyService import RXAnomalyService
from algorithms.MatchedFilter.services.MatchedFilterService import MatchedFilterService
from algorithms.MRMap.services.MRMapService import MRMapService
from algorithms.AIPersonDetector.services.AIPersonDetectorService import AIPersonDetectorService
from algorithms.HSVColorRange.services.HSVColorRangeService import HSVColorRangeService
from algorithms.ThermalRange.services.ThermalRangeService import ThermalRangeService
from algorithms.ThermalAnomaly.services.ThermalAnomalyService import ThermalAnomalyService


class AnalyzeService(QObject):
    """Service to process images using a selected algorithm."""

    # Signals to send info back to the GUI
    sig_msg = Signal(str)
    sig_aois = Signal()
    sig_done = Signal(int, int, str)

    def __init__(self, id, algorithm, input, output, identifier_color, min_area, num_processes,
                 max_aois, aoi_radius, histogram_reference_path, kmeans_clusters, options, max_area):
        """
        Initialize the AnalyzeService with parameters for processing images.

        Args:
            id (int): Numeric ID.
            algorithm (dict): Dictionary specifying the algorithm for analysis.
            input (str): Path to the input directory containing images.
            output (str): Path to the output directory where processed images will be stored.
            identifier_color (tuple[int, int, int]): RGB values to highlight areas of interest.
            min_area (int): Minimum size in pixels for an object to be considered an area of interest.
            max_area (int): Maximum area in pixels for an object to be considered an area of interest.
            num_processes (int): Number of concurrent processes for image processing.
            max_aois (int): Maximum areas of interest threshold in a single image before issuing a warning.
            aoi_radius (int): Radius added to the minimum enclosing circle around areas of interest.
            histogram_reference_path (str): Path to the histogram reference image.
            kmeans_clusters (int): Number of clusters (colors) to retain in the image.
            options (dict): Additional algorithm-specific options.
            max_area (int): Maximum area in pixels for an object to qualify as an area of interest.
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
        self.aoi_radius = aoi_radius
        self.num_processes = num_processes
        self.max_aois = max_aois
        self.max_aois_limit_exceeded = False
        self.hist_ref_path = histogram_reference_path
        self.kmeans_clusters = kmeans_clusters
        self.__id = id
        self.images_with_aois = []
        self.cancelled = False
        self.is_thermal = (self.algorithm['type'] == 'Thermal')
        self.pool = Pool(self.num_processes)

    @Slot()
    def process_files(self):
        """
        Process all files in the input directory using the selected algorithm and settings.
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

            start_time = time.time()
            for subdir, dirs, files in os.walk(self.input):
                for file in files:
                    file_path = Path(file)
                    if self.is_thermal and file_path.suffix != 'irg':
                        image_files.append(os.path.join(subdir, file))
                    elif not self.is_thermal:
                        image_files.append(os.path.join(subdir, file))

            self.ttl_images = len(image_files)
            self.sig_msg.emit(f"Processing {self.ttl_images} files")

            self._completed_images = 0
            self._last_progress_percent = 0

            # Process each image using multiprocessing
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
                        self.pool.apply_async(
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
                                self.is_thermal
                            ),
                            callback=self._process_complete
                        )
                    else:
                        self.ttl_images -= 1
                        self.sig_msg.emit(f"Skipping {file} :: File is not an image")

            # Close the pool and ensure all processes are done
            self.pool.close()
            self.pool.join()

            # Generate the output XML with the information gathered during processing
            self.images_with_aois = sorted(self.images_with_aois, key=operator.itemgetter('path'))
            
            # Set the XML path before adding images so relative paths can be calculated
            file_path = os.path.join(self.output, "ADIAT_Data.xml")
            self.xmlService.xml_path = file_path
            
            for img in self.images_with_aois:
                self.xmlService.add_image_to_xml(img)

            self.xmlService.save_xml_file(file_path)
            ttl_time = round(time.time() - start_time, 3)
            self.sig_done.emit(self.__id, len(self.images_with_aois), file_path)
            self.sig_msg.emit(f"Total Processing Time: {ttl_time} seconds")
            self.sig_msg.emit(f"Total Images Processed: {self.ttl_images}")

        except Exception as e:
            print(traceback.format_exc())
            self.logger.error(f"An error occurred during processing: {e}")

    @staticmethod
    def process_file(algorithm, identifier_color, min_area, max_area, aoi_radius, options, full_path, input_dir, output_dir, hist_ref_path, kmeans_clusters,
                     thermal):
        """
        Process a single image using the selected algorithm and settings.

        Args:
            algorithm (dict): Dictionary specifying the algorithm for analysis.
            identifier_color (tuple[int, int, int]): RGB values for highlighting areas of interest.
            min_area (int): Minimum size in pixels for an object to be considered an area of interest.
            max_area (int): Maximum size in pixels for an object to be considered an area of interest.
            aoi_radius (int): Radius added to the minimum enclosing circle around areas of interest.
            options (dict): Additional algorithm-specific options.
            full_path (str): Path to the image file being analyzed.
            input_dir (str): Path to the input directory containing images.
            output_dir (str): Path to the output directory for processed images.
            hist_ref_path (str): Path to the histogram reference image.
            kmeans_clusters (int): Number of clusters (colors) to retain in the image.
            thermal (bool): Whether this is a thermal image algorithm.

        Returns:
            tuple[numpy.ndarray, list]: Processed image with areas of interest highlighted and list of areas of interest.
        """
        img = cv2.imdecode(np.fromfile(full_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        # img = cv2.resize(img, (4000, 3000))
        try:
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

            # Instantiate the algorithm class and process the image
            cls = globals()[algorithm['service']]
            instance = cls(identifier_color, min_area, max_area, aoi_radius, algorithm['combine_overlapping_aois'], options)
            return instance.process_image(img, full_path, input_dir, output_dir)
        except Exception as e:
            logger = LoggerService()
            logger.error(e)

    @Slot()
    def _process_complete(self, result):
        """
        Handle completion of an image processing task.

        Args:
            result: Result object from the process_file method containing processed image data.
        """
        if result.input_path is not None:
            path = Path(result.input_path)
            file_name = path.name
        # Handle errors in processing
        if result.error_message is not None:
            self.sig_msg.emit("Unable to process " + file_name + " :: " + result.error_message)
            return
        # Add successfully processed image to results
        if result.areas_of_interest:
            # Include original path for mask-based approach
            image_data = {
                "path": result.output_path,  # This will be the mask path
                "original_path": result.input_path,  # Original image path
                "aois": result.areas_of_interest
            }
            self.images_with_aois.append(image_data)

            num_aois = len(result.areas_of_interest)
            self.sig_msg.emit(f'{num_aois} Areas of interest identified in ' + file_name)

            # Guard against None and ensure integers for comparison
            if (result.base_contour_count is not None
                    and isinstance(result.base_contour_count, (int, np.integer))
                    and isinstance(self.max_aois, (int, np.integer))
                    and result.base_contour_count > int(self.max_aois)
                    and not self.max_aois_limit_exceeded):
                self.sig_aois.emit()
                self.max_aois_limit_exceeded = True
        else:
            self.sig_msg.emit('No areas of interest identified in ' + file_name)

        self._completed_images += 1
        percent_complete = int(100 * self._completed_images / self.ttl_images)
        if percent_complete >= self._last_progress_percent + 10:
            self.sig_msg.emit(f"Processing Progress: {percent_complete}% complete")
            self._last_progress_percent = percent_complete - (percent_complete % 10)

    @Slot()
    def process_cancel(self):
        """
        Cancel any ongoing asynchronous processes.
        """
        self.cancelled = True
        self.sig_msg.emit("--- Cancelling Image Processing ---")
        self.pool.terminate()

    def _setup_output_dir(self):
        """
        Create the output directory for storing processed images.
        """
        try:
            if os.path.exists(self.output):
                shutil.rmtree(self.output)
            os.makedirs(self.output)
        except Exception as e:
            self.logger.error(e)
