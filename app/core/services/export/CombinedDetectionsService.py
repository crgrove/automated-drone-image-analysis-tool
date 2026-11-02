"""CombinedDetectionsService - The detections of several scanned runs, for maps.

The results-folder scan collates many ADIAT_Data.xml runs into one PDF report
(CombinedPdfReportService). This service carries the SAME detections onto a
map: it loads the runs through the report's own loader, so reviewer copies are
merged and the AOI scope matches the report, and names each detection exactly
as the report does ("[run] image - AOI n") so a field team can find a map
marker's page in the PDF. It writes a KML with one folder per run, and flattens
the runs into the single image list the CalTopo exporter takes.
"""

import os

from core.services import AOIDuplicateService
from core.services.LoggerService import LoggerService
from core.services.export.CombinedPdfReportService import load_run_contexts
from core.services.export.KMLGeneratorService import KMLGeneratorService
from core.services.image.AOIService import AOIService
from core.services.image.ImageService import ImageService
from core.services.image.WingtraDataService import resolve_altitude_ft
from helpers.LocationInfo import LocationInfo

# RunReportContext carries the report's position format and distance unit for
# its PDF pages; map exports write raw coordinates and never read them.
_UNUSED_POSITION_FORMAT = 'Lat/Long - Decimal Degrees'
_UNUSED_DISTANCE_UNIT = 'm'


def detection_image_name(run_number, image):
    """The name the combined report gives an image: "[run] name"."""
    return f"[{run_number}] {image['name']}"


class CombinedDetectionsService:
    """Load scanned runs and export their detections for mapping."""

    def __init__(self, include_images_without_flagged_aois=False,
                 use_terrain_elevation=True, recovery_session=None, logger=None):
        """
        Args:
            include_images_without_flagged_aois: The combined report's scope
                flag. Off, a run contributes its flagged AOIs plus any
                commented unflagged ones; on, every AOI of every image.
            use_terrain_elevation: UseTerrainElevation preference, used to
                place each AOI on the ground.
            recovery_session: Optional RecoverySession from the folder scan,
                so an XML that travelled without its images can find them.
            logger: Optional LoggerService override.
        """
        self.include_images_without_flagged_aois = include_images_without_flagged_aois
        self.use_terrain_elevation = use_terrain_elevation
        self.recovery_session = recovery_session
        self.logger = logger or LoggerService()

    def load_runs(self, xml_paths):
        """The runs holding at least one AOI in scope, in report order.

        Run N here is run N in the combined PDF: both drop the runs with no
        exportable image the same way.

        Args:
            xml_paths: The ADIAT_Data.xml files from the scan.

        Returns:
            list: RunReportContext per run, each image holding only its AOIs
            in scope.
        """
        path_resolver = None
        if self.recovery_session is not None:
            path_resolver = self.recovery_session.resolve_file
        contexts = load_run_contexts(
            xml_paths, _UNUSED_POSITION_FORMAT, _UNUSED_DISTANCE_UNIT,
            include_images_without_flagged_aois=self.include_images_without_flagged_aois,
            use_terrain_elevation=self.use_terrain_elevation,
            path_resolver=path_resolver,
            logger=self.logger,
        )
        return [context for context in contexts if context.images]

    @staticmethod
    def count_detections(runs):
        """Number of AOIs across the runs."""
        return sum(run.total_aoi_count for run in runs)

    @staticmethod
    def flatten_runs(runs):
        """One image list across every run, in the shape a single run's
        exporter takes.

        Args:
            runs: RunReportContexts from load_runs.

        Returns:
            tuple: (images, flagged_aois, spans) - copies of every image dict,
            renamed "[run] name" as in the report; {image index: list of every
            AOI index}, since the runs already hold only the AOIs in scope;
            and a (run, start, stop) slice of images per run.
        """
        images = []
        flagged_aois = {}
        spans = []
        for run_number, run in enumerate(runs, start=1):
            start = len(images)
            for image in run.images:
                entry = dict(image)
                entry['name'] = detection_image_name(run_number, image)
                flagged_aois[len(images)] = list(range(len(entry.get('areas_of_interest', []))))
                images.append(entry)
            spans.append((run, start, len(images)))
        return images, flagged_aois, spans

    def generate_kml(self, output_path, runs, progress_callback=None, cancel_check=None):
        """Write every detection to a KML (or KMZ), one folder per run.

        Args:
            output_path: Destination .kml or .kmz path.
            runs: RunReportContexts from load_runs.
            progress_callback: Optional (current, total, message) callback.
            cancel_check: Optional callable returning True to abort.

        Returns:
            dict: {'exported': placemarks written, 'unplaced': AOIs skipped
            because neither they nor their image could be positioned}, or
            None when cancelled (nothing is written).
        """
        kml_service = KMLGeneratorService(use_terrain=self.use_terrain_elevation)
        # Map tools (Google Earth, CalTopo's import) title the layer with this
        kml_service.kml.document.name = os.path.splitext(os.path.basename(output_path))[0]

        images, _, spans = self.flatten_runs(runs)
        total = self.count_detections(runs)
        processed = 0
        exported = 0
        unplaced = 0

        for run_number, (run, start, stop) in enumerate(spans, start=1):
            # Same numbered heading as the run's section in the PDF
            folder = kml_service.kml.newfolder(name=f"{run_number}. {run.run_name}")
            for image in images[start:stop]:
                if cancel_check and cancel_check():
                    return None
                aoi_count = len(image.get('areas_of_interest', []))
                if progress_callback:
                    progress_callback(processed, max(total, 1), f"Placing {image['name']}...")

                for detection in self._image_detections(run, image):
                    if detection is None:
                        unplaced += 1
                        continue
                    kml_service.add_aoi_placemark(
                        detection['name'],
                        detection['latitude'],
                        detection['longitude'],
                        detection['description'],
                        detection['rgb'],
                        folder=folder,
                    )
                    exported += 1
                processed += aoi_count

        if cancel_check and cancel_check():
            return None

        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        kml_service.save_kml(output_path)
        if progress_callback:
            progress_callback(max(total, 1), max(total, 1), "KML export complete")
        return {'exported': exported, 'unplaced': unplaced}

    def _image_detections(self, run, image):
        """Placemark fields for each of one image's AOIs.

        Positions are computed as the report computes them: from the
        original image (where the GPS metadata lives), keeping the image
        dict's operator corrections (fov_alignment, recovered bearing) and
        honoring a reviewer's hand-placed AOI position.

        Args:
            run: The image's RunReportContext.
            image: Flattened image dict (named "[run] name").

        Returns:
            list: One dict per AOI ('name', 'latitude', 'longitude',
            'description', 'rgb'), or None in an AOI's slot when neither the
            AOI nor its image could be positioned.
        """
        aois = image.get('areas_of_interest', [])
        source_path = image.get('original_path') or image.get('path', '')
        image_dict = dict(image)
        image_dict['path'] = source_path
        image_dict.setdefault('mask_path', '')

        try:
            # Pixels are decoded only if a position or color needs them
            image_service = ImageService(
                source_path, image_dict['mask_path'], calculated_bearing=image.get('bearing'),
                defer_load=True)
            aoi_service = AOIService(image_dict, image_service=image_service)
            camera_gps = LocationInfo.get_gps(exif_data=image_service.exif_data)
        except Exception as e:
            self.logger.error(f"Combined KML: could not read {source_path} ({run.run_name}): {e}")
            return [None] * len(aois)

        # A Wingtra image's AGL from its geotags CSV, as the report uses
        altitude_ft = resolve_altitude_ft(image_dict, None)
        detections = []
        for aoi_index, aoi in enumerate(aois):
            position = None
            try:
                position = aoi_service.calculate_gps_with_custom_altitude(
                    image_dict, aoi, altitude_ft, self.use_terrain_elevation)
            except Exception as e:
                self.logger.warning(
                    f"Combined KML: AOI {aoi_index + 1} of {image['name']} could not be "
                    f"positioned: {e}")

            if position:
                latitude, longitude = position
                gps_note = "Estimated AOI GPS"
            elif camera_gps:
                # The camera's position is still close enough to search from
                latitude = camera_gps['latitude']
                longitude = camera_gps['longitude']
                gps_note = "Image GPS (AOI position could not be calculated)"
            else:
                detections.append(None)
                continue

            color = None
            try:
                color = aoi_service.get_cached_or_representative_color(aoi)
            except Exception:
                pass  # The placemark keeps the default pin color

            detections.append({
                'name': f"{image['name']} - AOI {aoi_index + 1}",
                'latitude': latitude,
                'longitude': longitude,
                'description': self._description(run, image, aoi, aoi_index, gps_note, color),
                'rgb': color['rgb'] if color else None,
            })
        return detections

    @staticmethod
    def _description(run, image, aoi, aoi_index, gps_note, color):
        """Placemark text: the reviewer's words first, then the facts."""
        lines = []
        comment = aoi.get('user_comment', '')
        if comment:
            lines.append(f'"{comment}"')
            lines.append("")
        lines.append(f"Run: {run.run_name}")
        lines.append(f"Image: {image['name']}")
        lines.append(gps_note)
        lines.append(f"AOI Index: {aoi_index + 1}")
        center = aoi.get('center', [0, 0])
        lines.append(f"Center: ({center[0]}, {center[1]})")
        lines.append(f"Area: {aoi.get('area', 0):.0f} pixels")
        if 'confidence' in aoi:
            lines.append(f"Confidence: {aoi['confidence']:.1f}% ({aoi.get('score_type', 'unknown')})")
        if color:
            lines.append(f"Color: Hue: {color['hue_degrees']}° {color['hex']}")
        sightings_line = AOIDuplicateService.sightings_line(aoi, run.duplicate_sightings)
        if sightings_line:
            lines.append(sightings_line)
        # Set by the multi-reviewer merge ("Flagged by 2 of 3 reviewers ...")
        review_note = aoi.get('review_note', '')
        if review_note:
            lines.append(f"Review: {review_note}")
        return "\n".join(lines)
