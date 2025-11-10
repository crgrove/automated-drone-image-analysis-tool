"""
BearingRecoveryController - Handles bearing recovery for images missing orientation data.

This controller checks for missing bearings and orchestrates the recovery process
through the BearingRecoveryDialog.
"""

from core.services.LoggerService import LoggerService
from core.services.image.ImageService import ImageService
from core.views.images.viewer.dialogs.BearingRecoveryDialog import BearingRecoveryDialog
from PySide6.QtWidgets import QDialog


class BearingRecoveryController:
    """
    Controller for managing bearing recovery operations.
    
    Handles checking for missing bearings and orchestrating the recovery dialog.
    """

    def __init__(self, parent_viewer):
        """
        Initialize the bearing recovery controller.
        
        Args:
            parent_viewer: The main Viewer instance
        """
        self.parent = parent_viewer
        self.logger = LoggerService()

    def check_and_recover_bearings(self, images, xml_service, xml_path):
        """
        Check if images are missing bearings and offer recovery options.
        
        Args:
            images: List of image dictionaries
            xml_service: XmlService instance for updating bearings
            xml_path: Path to XML file for saving
        """
        # Check how many images are missing bearings
        images_missing_bearings = []

        # Quick check: do ANY images have bearing in XML?
        # If all have bearings, skip recovery entirely
        any_has_xml_bearing = any(img.get('bearing') is not None for img in images)

        if any_has_xml_bearing:
            # Some images have bearings already, skip recovery
            self.logger.info("Bearing data found in XML, skipping recovery")
            return 0

        # No XML bearings found - check if first image has bearing in EXIF data
        # Use the same logic as the "Gimbal Orientation" display in the viewer
        if len(images) > 0:
            first_image_path = images[0]['path']
            try:
                # Create ImageService WITHOUT calculated_bearing to check EXIF/XMP only
                # This uses the same logic as the "Gimbal Orientation" display
                image_service = ImageService(first_image_path, calculated_bearing=None)

                # get_camera_yaw() checks Gimbal Yaw first, then Flight Yaw, then calculated_bearing
                # Since we passed calculated_bearing=None, it only checks EXIF/XMP data
                camera_yaw = image_service.get_camera_yaw()

                if camera_yaw is not None:
                    self.logger.info(f"First image has gimbal orientation in EXIF ({camera_yaw}°), skipping recovery")
                    return 0
                else:
                    self.logger.info("First image does not have gimbal orientation in EXIF, showing recovery dialog")
            except Exception as e:
                self.logger.warning(f"Could not check first image EXIF for bearing: {e}")
                # Continue to show recovery dialog if EXIF check fails

        # No XML bearings found - prepare lightweight image list for dialog
        # The actual GPS/timestamp extraction happens in the calculation service
        self.logger.info(f"No bearing data in XML, preparing recovery for {len(images)} images")

        for image in images:
            # Just add the image path - GPS/timestamp will be extracted during calculation
            images_missing_bearings.append({
                'path': image['path'],
                'lat': None,  # Will be extracted during calculation
                'lon': None,  # Will be extracted during calculation
                'timestamp': None  # Will be extracted during calculation
            })

        # Show recovery dialog immediately (no slow EXIF check needed)
        if len(images_missing_bearings) > 0:
            self.logger.info(f"Found {len(images_missing_bearings)}/{len(images)} images missing bearings")

            # Show bearing recovery dialog
            dialog = BearingRecoveryDialog(self.parent, images_missing_bearings)
            result = dialog.exec()

            if result == QDialog.Accepted:
                # Get results and save to XML
                bearing_results = dialog.get_results()

                if bearing_results:
                    # Update XML with calculated bearings
                    updated_count = xml_service.set_multiple_bearings(bearing_results)

                    # Save XML file
                    xml_service.save_xml_file(xml_path)

                    self.logger.info(f"Saved {updated_count} calculated bearings to XML")
                    return updated_count
        else:
            self.logger.info("All images have bearing information")
        
        return 0

