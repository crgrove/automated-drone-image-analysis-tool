"""
AlignImageController - opens the Align Image dialog for the current image.

Gathers the current drone image and its estimated FOV, runs the modal
AlignImageDialog, and on accept persists the refined alignment to the analysis
XML and refreshes dependent views.
"""

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QDialog

from helpers.LocationInfo import LocationInfo
from helpers.MetaDataHelper import MetaDataHelper
from helpers.PhotogrammetryHelper import local_enu_to_gps
from core.services.LoggerService import LoggerService
from core.services.image.CoverageExtentService import CoverageExtentService
from core.views.images.viewer.dialogs.AlignImageDialog import AlignImageDialog

# Half-size, in metres, of the fallback footprint square used when the estimated
# FOV cannot be computed from metadata.
_DEFAULT_FOOTPRINT_HALF_M = 75.0


class AlignImageController(QObject):
    """Controller for the manual Align Image (FOV refinement) dialog."""

    def __init__(self, parent_viewer):
        """
        Args:
            parent_viewer: The main Viewer instance.
        """
        super().__init__()
        self.parent = parent_viewer
        self.logger = LoggerService()

    def open_dialog(self):
        """Open the Align Image dialog for the currently selected image."""
        images = getattr(self.parent, 'images', None)
        current = getattr(self.parent, 'current_image', -1)
        if not images or not (0 <= current < len(images)):
            return

        image = images[current]
        image_path = image.get('path')
        if not image_path:
            self._toast(self.tr("No image available to align"))
            return

        # The image needs GPS to anchor the satellite view.
        gps = self._get_image_gps(image_path)
        if gps is None:
            self._toast(self.tr("This image has no GPS data and cannot be aligned"))
            return

        estimated_corners, camera_yaw = self._get_estimated_corners(image, gps)
        # Orient the photo to the authoritative camera heading (gimbal/flight yaw)
        # used by the footprint estimate, so it starts lined up with the map;
        # fall back to the image's calculated bearing when yaw is unavailable.
        bearing = camera_yaw if camera_yaw is not None else (image.get('bearing') or 0.0)
        offline_only = self._is_offline_only()
        saved_alignment = image.get('fov_alignment')

        dialog = AlignImageDialog(
            self.parent, image_path, estimated_corners, bearing,
            offline_only=offline_only, saved_alignment=saved_alignment,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self._save_alignment(image, dialog.get_result())

    def _save_alignment(self, image, result):
        """Persist the alignment result and refresh dependent views."""
        corners = result.get('corners')
        tie_points = result.get('tie_points') or []
        rotation = result.get('rotation', 0.0)
        if not corners or len(corners) != 4:
            return

        saved = self.parent.xml_service.set_image_fov_alignment(
            image['path'], corners, tie_points, rotation
        )
        if not saved:
            self._toast(self.tr("Could not save the alignment"))
            return
        self.parent.xml_service.save_xml_file(self.parent.xml_path)

        # Update the in-memory dict so downstream calculations pick it up at once.
        image['fov_alignment'] = {
            'corners': [tuple(c) for c in corners],
            'tie_points': [tuple(t) for t in tie_points],
            'rotation': rotation,
        }

        self._toast(self.tr("Image alignment saved"), color="#4CAF50")
        self._refresh_views()

    def _refresh_views(self):
        """Refresh the GPS map FOV box if the map is currently open."""
        gps_controller = getattr(self.parent, 'gps_map_controller', None)
        if (gps_controller and getattr(gps_controller, 'map_dialog', None)
                and gps_controller.map_dialog.isVisible()):
            # show_map re-extracts GPS data (now carrying the alignment) and
            # refreshes the already-open dialog.
            gps_controller.show_map()

    def _get_image_gps(self, image_path):
        """Return {'latitude', 'longitude'} for the image, or None."""
        try:
            exif_data = MetaDataHelper.get_exif_data_piexif(image_path)
            return LocationInfo.get_gps(exif_data=exif_data)
        except Exception as e:
            self.logger.error(f"AlignImageController: GPS lookup failed - {e}")
            return None

    def _get_estimated_corners(self, image, gps):
        """Compute the raw metadata FOV estimate, with a default-square fallback.

        Any existing alignment is stripped first so the estimate reflects the
        original metadata - this is what the dialog's Reset restores to.

        Returns:
            tuple: (corners, camera_yaw) where corners is a list of four
            (lat, lon) tuples (TL, TR, BR, BL) and camera_yaw is the heading in
            degrees used to build the estimate, or None if it was unavailable.
        """
        camera_yaw = None
        try:
            custom_alt = getattr(self.parent, 'custom_agl_altitude_ft', None)
            use_terrain = getattr(self.parent, 'use_terrain_elevation', True)
            service = CoverageExtentService(custom_altitude_ft=custom_alt, logger=self.logger, use_terrain=use_terrain)
            image_for_estimate = {k: v for k, v in image.items() if k != 'fov_alignment'}
            corners = service.get_image_fov_corners(image_for_estimate)
            camera_yaw = service.last_camera_yaw
            if corners and len(corners) == 4:
                return corners, camera_yaw
        except Exception as e:
            self.logger.warning(f"AlignImageController: FOV estimate failed - {e}")

        # Fallback: a default square centred on the drone GPS.
        lat0, lon0 = gps['latitude'], gps['longitude']
        half = _DEFAULT_FOOTPRINT_HALF_M
        corners = [
            local_enu_to_gps(-half, half, lat0, lon0),   # TL
            local_enu_to_gps(half, half, lat0, lon0),    # TR
            local_enu_to_gps(half, -half, lat0, lon0),   # BR
            local_enu_to_gps(-half, -half, lat0, lon0),  # BL
        ]
        return corners, camera_yaw

    def _is_offline_only(self):
        """Return whether the OfflineOnly preference is enabled."""
        try:
            if hasattr(self.parent, 'settings_service'):
                return self.parent.settings_service.get_bool_setting("OfflineOnly", False)
        except Exception:
            pass
        return False

    def _toast(self, message, color="#F44336"):
        """Show a transient status message via the viewer's status controller."""
        try:
            self.parent.status_controller.show_toast(message, 3000, color=color)
        except Exception:
            self.logger.info(message)
