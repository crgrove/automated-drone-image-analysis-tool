"""
PathValidationController - Handles validation and recovery of missing image and mask paths.

This controller manages the UI orchestration for validating that image and mask files exist,
and prompts users to locate missing files when paths are invalid.
"""

import os
from pathlib import Path
from PySide6.QtWidgets import QMessageBox, QFileDialog
from core.services.LoggerService import LoggerService


class PathValidationController:
    """
    Controller for managing path validation and recovery.
    
    Handles checking for missing files and prompting users to locate them.
    """

    def __init__(self, parent_viewer):
        """
        Initialize the path validation controller.
        
        Args:
            parent_viewer: The main Viewer instance
        """
        self.parent = parent_viewer
        self.logger = LoggerService()

    def validate_and_fix_paths(self, images):
        """
        Validate that all image and mask paths exist. Prompt user to select folders if missing.
        
        Args:
            images: List of image dictionaries to validate
            
        Returns:
            bool: True if all paths are valid or were fixed, False if user cancelled.
        """
        missing_images = []
        missing_masks = []

        # Check which images and masks are missing
        for image in images:
            image_path = image.get('path', '')
            mask_path = image.get('mask_path', '')

            if image_path and not os.path.exists(image_path):
                missing_images.append({
                    'image': image,
                    'filename': os.path.basename(image_path)
                })

            if mask_path and not os.path.exists(mask_path):
                missing_masks.append({
                    'image': image,
                    'filename': os.path.basename(mask_path)
                })

        # Prompt for source images folder if any are missing
        if missing_images:
            if not self._prompt_for_source_folder(missing_images):
                return False  # User cancelled

        # Prompt for masks folder if any are missing
        if missing_masks:
            if not self._prompt_for_mask_folder(missing_masks):
                return False  # User cancelled

        return True

    def _prompt_for_source_folder(self, missing_images):
        """
        Prompt user to select folder containing source images.
        
        Args:
            missing_images (list): List of dicts with 'image' and 'filename' keys.
            
        Returns:
            bool: True if successful, False if user cancelled.
        """
        # Build message with list of missing files
        file_list = '\n'.join([f"  • {item['filename']}" for item in missing_images[:10]])
        if len(missing_images) > 10:
            file_list += f"\n  ... and {len(missing_images) - 10} more"

        message = (f"{len(missing_images)} source image(s) not found at expected locations:\n\n"
                   f"{file_list}\n\n"
                   f"Please select the folder containing the source images.")

        # Show informative message
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Source Images Not Found")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg_box.setDefaultButton(QMessageBox.Ok)

        if msg_box.exec() != QMessageBox.Ok:
            return False

        # Open folder selection dialog
        folder = QFileDialog.getExistingDirectory(
            self.parent,
            "Select Source Images Folder",
            "",
            QFileDialog.ShowDirsOnly
        )

        if not folder:
            return False  # User cancelled

        # Update paths for files found in the selected folder
        files_found = 0
        still_missing = []

        for item in missing_images:
            filename = item['filename']
            new_path = os.path.join(folder, filename)

            if os.path.exists(new_path):
                item['image']['path'] = new_path
                files_found += 1
            else:
                still_missing.append(filename)

        # Report results
        if still_missing:
            still_missing_list = '\n'.join([f"  • {f}" for f in still_missing[:10]])
            if len(still_missing) > 10:
                still_missing_list += f"\n  ... and {len(still_missing) - 10} more"

            QMessageBox.warning(
                self.parent,
                "Some Images Still Missing",
                f"Found {files_found} of {len(missing_images)} images.\n\n"
                f"Still missing:\n{still_missing_list}"
            )
            return False

        return True

    def _prompt_for_mask_folder(self, missing_masks):
        """
        Prompt user to select folder containing detection masks.
        
        Args:
            missing_masks (list): List of dicts with 'image' and 'filename' keys.
            
        Returns:
            bool: True if successful, False if user cancelled.
        """
        # Build message with list of missing files
        file_list = '\n'.join([f"  • {item['filename']}" for item in missing_masks[:10]])
        if len(missing_masks) > 10:
            file_list += f"\n  ... and {len(missing_masks) - 10} more"

        message = (f"{len(missing_masks)} detection mask(s) not found at expected locations:\n\n"
                   f"{file_list}\n\n"
                   f"Please select the folder containing the mask files.")

        # Show informative message
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Detection Masks Not Found")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg_box.setDefaultButton(QMessageBox.Ok)

        if msg_box.exec() != QMessageBox.Ok:
            return False

        # Open folder selection dialog
        folder = QFileDialog.getExistingDirectory(
            self.parent,
            "Select Masks Folder",
            "",
            QFileDialog.ShowDirsOnly
        )

        if not folder:
            return False  # User cancelled

        # Update paths for files found in the selected folder
        files_found = 0
        still_missing = []

        for item in missing_masks:
            filename = item['filename']
            new_path = os.path.join(folder, filename)

            if os.path.exists(new_path):
                item['image']['mask_path'] = new_path
                files_found += 1
            else:
                still_missing.append(filename)

        # Report results
        if still_missing:
            still_missing_list = '\n'.join([f"  • {f}" for f in still_missing[:10]])
            if len(still_missing) > 10:
                still_missing_list += f"\n  ... and {len(still_missing) - 10} more"

            QMessageBox.warning(
                self.parent,
                "Some Masks Still Missing",
                f"Found {files_found} of {len(missing_masks)} masks.\n\n"
                f"Still missing:\n{still_missing_list}"
            )
            return False

        return True



