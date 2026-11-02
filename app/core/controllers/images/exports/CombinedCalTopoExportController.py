"""
CombinedCalTopoExportController - Sends a folder of results' detections to CalTopo.

The CalTopo exporter publishes one run's flagged AOIs and reads per-run facts
off the Viewer it was opened from. A combined export hands it every scanned
run at once, flattened into one image list (CombinedDetectionsService.
flatten_runs), and supplies per run what a Viewer would: the run's identifier
color for the report photo, its duplicate links, and the terrain preference.
One login and one map selection then cover every run.
"""

from core.controllers.images.viewer.exports.CalTopoExportController import CalTopoExportController
from core.services.export.CombinedDetectionsService import CombinedDetectionsService


class CombinedCalTopoExportController(CalTopoExportController):
    """CalTopo export of the detections from several scanned runs."""

    def __init__(self, parent_widget, runs, use_terrain_elevation=True, logger=None):
        """
        Args:
            parent_widget: Parent for the dialogs (MainWindow).
            runs: RunReportContexts from CombinedDetectionsService.load_runs.
            use_terrain_elevation: UseTerrainElevation preference.
            logger: Optional LoggerService override.
        """
        super().__init__(parent_widget, logger)
        self.images, self.flagged_aois, self._run_spans = CombinedDetectionsService.flatten_runs(runs)
        self._use_terrain_elevation = use_terrain_elevation
        # The run whose markers are being prepared; set only inside
        # _prepare_markers so the per-run hooks below can answer for it.
        self._active_run = None

    def export_detections(self, method, include_photos):
        """Publish every detection as a CalTopo marker.

        Args:
            method: 'api' (Team API credentials) or 'browser' (log in).
            include_photos: Attach each detection's report photo - the
                multi-zoom composite on its page of the combined PDF.

        Returns:
            bool: True when anything reached CalTopo.
        """
        options = dict(
            include_flagged_aois=True,
            include_locations=False,
            include_images_without_flagged_aois=False,
            include_coverage_area=False,
            include_images=include_photos,
            aoi_photo_mode='full',
        )
        if method == 'api':
            return self.export_to_caltopo_via_api(self.images, self.flagged_aois, **options)
        return self.export_to_caltopo(self.images, self.flagged_aois, **options)

    def _prepare_markers(self, images, flagged_aois, include_images=True, aoi_photo_mode='full'):
        """Prepare each run's markers in turn, with that run's own settings."""
        markers = []
        try:
            for run, start, stop in self._run_spans:
                self._active_run = run
                run_flagged = {
                    index - start: aoi_indices
                    for index, aoi_indices in flagged_aois.items()
                    if start <= index < stop
                }
                markers.extend(super()._prepare_markers(
                    images[start:stop], run_flagged,
                    include_images=include_images, aoi_photo_mode=aoi_photo_mode))
        finally:
            self._active_run = None
        return markers

    def _use_terrain(self):
        """The preference, since MainWindow carries no viewer setting."""
        return self._use_terrain_elevation

    def _identifier_color(self):
        """The active run's circle color, so the photo matches its PDF page."""
        default = super()._identifier_color()
        if self._active_run is None:
            return default
        return self._active_run.settings.get('identifier_color', default)

    def _duplicate_sightings(self, images):
        """The report's links, gathered from the run's unfiltered images.

        The exported images hold only the AOIs in scope, so duplicates (and
        with them the links) are already gone from them; and AOI numbers are
        unique per run only, so links must never be resolved across runs.
        """
        if self._active_run is None:
            return super()._duplicate_sightings(images)
        return self._active_run.duplicate_sightings
