"""
ZipExportController - Handles ZIP file generation for the image viewer.

This controller manages the export of image files to ZIP format for
easy distribution and archiving.
"""

import os
import shutil
import tempfile
import platform

import cv2
import numpy as np

from PySide6.QtWidgets import QFileDialog, QMessageBox, QApplication, QDialog
from PySide6.QtCore import QThread, Signal
from core.services.ZipBundleService import ZipBundleService
from core.services.LoggerService import LoggerService
from core.services.XmlService import XmlService
from core.services.ImageService import ImageService
from core.services.ImageHighlightService import ImageHighlightService
from helpers.MetaDataHelper import MetaDataHelper

from core.views.viewer.dialogs.ZipExportDialog import ZipExportDialog
from core.views.viewer.dialogs.ExportProgressDialog import ExportProgressDialog


class ZipExportThread(QThread):
    success = Signal()
    errorOccurred = Signal(str)
    progressUpdated = Signal(int, int, str)
    canceled = Signal()

    def __init__(self, controller, images, export_mode, output_zip):
        super().__init__()
        self.controller = controller
        self.images = images
        self.export_mode = export_mode
        self.output_zip = output_zip
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        staging_root = tempfile.mkdtemp(prefix="adiat_zip_")
        total = len(self.images)
        current = 0
        try:
            # Export step-by-step to update progress
            if self.export_mode == 'native':
                # Native export: copy images preserving structure; update XML
                self.controller._export_native_prepare(self.images, staging_root)
                for img in self.images:
                    if self._cancel:
                        self.canceled.emit()
                        return
                    self.controller._export_native_copy_one(img, staging_root)
                    current += 1
                    self.progressUpdated.emit(current, total, f"Copying {os.path.basename(img.get('path',''))}")
                self.controller._export_native_finalize(staging_root)
            else:
                # Augmented export: render per image
                for img in self.images:
                    if self._cancel:
                        self.canceled.emit()
                        return
                    self.controller._export_augmented_one(img, staging_root)
                    current += 1
                    self.progressUpdated.emit(current, total, f"Rendering {os.path.basename(img.get('path',''))}")

            # Inform user we're finalizing (zipping, writing XML)
            self.progressUpdated.emit(total, total, "Finalizing export...")

            # Zip directory at the end
            zip_generator = ZipBundleService()
            zip_generator.generate_zip_from_directory(staging_root, self.output_zip)
            self.success.emit()
        except Exception as e:
            self.errorOccurred.emit(str(e))
        finally:
            try:
                shutil.rmtree(staging_root, ignore_errors=True)
            except Exception:
                pass


class ZipExportController:
    """
    Controller for managing ZIP export functionality.

    Handles the export of image files to ZIP format, filtering out
    hidden images from the bundle.
    """

    def __init__(self, parent_widget, logger=None):
        """
        Initialize the ZIP export controller.

        Args:
            parent_widget: The parent widget for dialogs
            logger: Optional logger instance for error reporting
        """
        self.parent = parent_widget
        self.logger = logger or LoggerService()

    def export_zip(self, images):
        """
        Export image files to ZIP format.

        Args:
            images: List of image data dictionaries

        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            # Show options dialog
            options_dialog = ZipExportDialog(self.parent)
            if options_dialog.exec() != QDialog.Accepted:
                return False

            export_mode = options_dialog.get_export_mode()  # 'native' or 'augmented'

            # Open file dialog for ZIP export
            file_name, _ = QFileDialog.getSaveFileName(
                self.parent,
                "Save Zip File",
                "",
                "Zip files (*.zip)"
            )

            if not file_name:  # User cancelled
                return False

            visible_images = [img for img in images if not img.get('hidden', False)]
            if not visible_images:
                self._show_toast("No images to export", 3000, color="#F44336")
                return False

            # Create and show progress dialog
            total_items = len(visible_images)
            self.progress_dialog = ExportProgressDialog(
                self.parent,
                title="Generating ZIP Export",
                total_items=total_items
            )
            self.progress_dialog.set_title("Preparing ZIP export...")

            # Create worker thread
            self.zip_thread = ZipExportThread(self, visible_images, export_mode, file_name)

            # Connect signals
            self.zip_thread.success.connect(self._on_zip_success)
            self.zip_thread.errorOccurred.connect(self._on_zip_error)
            self.zip_thread.progressUpdated.connect(self._on_progress_updated)
            self.zip_thread.canceled.connect(self._on_zip_cancelled)

            # Connect cancel
            self.progress_dialog.cancel_requested.connect(self.zip_thread.cancel)

            # Start
            self.zip_thread.start()

            # Show progress dialog modal
            self.progress_dialog.show()
            QApplication.processEvents()
            if self.progress_dialog.exec() == QDialog.Rejected:
                self.zip_thread.cancel()

            return True

        except Exception as e:
            self.logger.error(f"Error generating Zip file: {str(e)}")
            self._show_error(f"Failed to generate Zip file: {str(e)}")
            return False

    def _export_native_prepare(self, images, staging_root):
        """Prepare folders and load XML/settings for native export."""
        # Prepare folders
        images_root = os.path.join(staging_root, "images")
        os.makedirs(images_root, exist_ok=True)

        # Load XML and settings
        xml_path = getattr(self.parent, 'xml_path', None)
        xml_service = getattr(self.parent, 'xml_service', None)
        if xml_service is None and xml_path:
            xml_service = XmlService(xml_path)

        settings = {}
        if xml_service:
            try:
                settings, _ = xml_service.get_settings()
            except Exception:
                settings = {}

        input_dir = settings.get('input_dir', '') if settings else ''
        input_dir = input_dir if input_dir else os.path.commonpath([os.path.dirname(img['path']) for img in images])

        # Store for subsequent steps
        self._native_ctx = {
            'images_root': images_root,
            'xml_path': xml_path,
            'xml_service': xml_service,
            'mask_src_dir': os.path.dirname(xml_path) if xml_path else '',
            'input_dir': input_dir,
            'staging_root': staging_root,
            'results_root': os.path.join(staging_root, "ADIAT_Results")
        }
        os.makedirs(self._native_ctx['results_root'], exist_ok=True)

    def _export_native_copy_one(self, img, staging_root):
        ctx = getattr(self, '_native_ctx', {})
        images_root = ctx.get('images_root')
        input_dir = ctx.get('input_dir')

        # Copy images preserving relative structure
        src_path = img.get('path', '')
        if not src_path or not os.path.exists(src_path):
            return
        try:
            rel_path = os.path.relpath(src_path, input_dir) if input_dir else os.path.basename(src_path)
        except ValueError:
            rel_path = os.path.basename(src_path)
        dst_path = os.path.join(images_root, rel_path)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(src_path, dst_path)

    def _export_native_finalize(self, staging_root):
        ctx = getattr(self, '_native_ctx', {})
        images_root = ctx.get('images_root')
        xml_path = ctx.get('xml_path')
        xml_service = ctx.get('xml_service')
        input_dir = ctx.get('input_dir')
        mask_src_dir = ctx.get('mask_src_dir')

        # Copy mask TIFFs under ADIAT_Results; save XML inside ADIAT_Results
        results_root = ctx.get('results_root')
        xml_dst_path = os.path.join(results_root, os.path.basename(xml_path) if xml_path else 'ADIAT_Data.xml')
        if xml_service and xml_service.xml is not None:
            # Update XML image paths to be relative to XML location
            root = xml_service.xml.getroot()
            images_xml = root.find('images')
            if images_xml is not None:
                for image_xml in images_xml:
                    orig_path = image_xml.get('path', '')
                    if orig_path:
                        # Build rel path under images/
                        full_path = orig_path
                        # If path is relative in XML, resolve against original XML dir
                        if xml_path and not os.path.isabs(full_path):
                            full_path = os.path.join(os.path.dirname(xml_path), full_path)
                        try:
                            rel_from_input = os.path.relpath(full_path, input_dir) if input_dir else os.path.basename(full_path)
                        except ValueError:
                            rel_from_input = os.path.basename(full_path)
                        # XML sits inside ADIAT_Results, images live at ../images/
                        image_xml.set('path', os.path.join('..', 'images', rel_from_input).replace('\\', '/'))

                    mask_name = image_xml.get('mask_path', '')
                    if mask_name and mask_src_dir:
                        src_mask = os.path.join(mask_src_dir, mask_name)
                        if os.path.exists(src_mask):
                            # Preserve any relative subfolder in mask_name
                            dst_mask = os.path.join(results_root, mask_name)
                            os.makedirs(os.path.dirname(dst_mask), exist_ok=True)
                            try:
                                shutil.copy2(src_mask, dst_mask)
                            except Exception:
                                pass

            # Save updated XML into staging root
            try:
                xml_service.save_xml_file(xml_dst_path)
            except Exception:
                # Fallback: write original XML if save failed
                if xml_path and os.path.exists(xml_path):
                    shutil.copy2(xml_path, xml_dst_path)
        else:
            # No XML service available; just copy if exists
            if xml_path and os.path.exists(xml_path):
                shutil.copy2(xml_path, xml_dst_path)

    def _export_augmented_one(self, img, staging_root):
        """Render and write a single augmented image preserving metadata."""
        images_root = os.path.join(staging_root, "images")
        os.makedirs(images_root, exist_ok=True)

        # Determine input root for relative paths
        xml_service = getattr(self.parent, 'xml_service', None)
        input_dir = ''
        if xml_service:
            try:
                settings, _ = xml_service.get_settings()
                input_dir = settings.get('input_dir', '')
            except Exception:
                input_dir = ''
        if not input_dir:
            try:
                input_dir = os.path.dirname(img['path'])
            except Exception:
                input_dir = ''

        # Flags from viewer for augmentations
        show_aois = hasattr(self.parent, 'showAOIsButton') and self.parent.showAOIsButton.isChecked()
        show_pois = hasattr(self.parent, 'showPOIsButton') and self.parent.showPOIsButton.isChecked()
        identifier_color = getattr(self.parent, 'settings', {}).get('identifier_color', (255, 255, 0))

        src_path = img.get('path', '')
        if not src_path or not os.path.exists(src_path):
            return

        try:
            rel_path = os.path.relpath(src_path, input_dir) if input_dir else os.path.basename(src_path)
        except ValueError:
            rel_path = os.path.basename(src_path)

        # Force jpg extension for augmented outputs
        rel_no_ext = os.path.splitext(rel_path)[0]
        dst_rel = rel_no_ext + ".jpg"
        dst_path = os.path.join(images_root, dst_rel)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)

        # Load image and render augmentations
        try:
            calculated_bearing = img.get('bearing', None)
            image_service = ImageService(src_path, img.get('mask_path', ''), calculated_bearing=calculated_bearing)
            augmented = image_service.img_array
            if show_aois:
                augmented = image_service.circle_areas_of_interest(identifier_color, img.get('areas_of_interest', []))
            if show_pois:
                if img.get('mask_path'):
                    augmented = ImageHighlightService.apply_mask_highlight(
                        augmented,
                        img.get('mask_path', ''),
                        identifier_color,
                        img.get('areas_of_interest', [])
                    )

            # Save RGB numpy array as JPEG (convert to BGR for OpenCV)
            bgr = cv2.cvtColor(augmented, cv2.COLOR_RGB2BGR)
            cv2.imwrite(dst_path, bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

            # Transfer metadata
            try:
                if platform.system() == "Darwin":
                    MetaDataHelper.transfer_exif(src_path, dst_path)
                    xmp_xml = MetaDataHelper.get_xmp_data(src_path, parse=False)
                    if xmp_xml:
                        MetaDataHelper.embed_xmp_xml(xmp_xml.encode('utf-8'), dst_path)
                else:
                    MetaDataHelper.transfer_all_exiftool(src_path, dst_path)
                    xmp_xml = MetaDataHelper.get_xmp_data(src_path, parse=False)
                    if xmp_xml:
                        MetaDataHelper.embed_xmp_xml(xmp_xml.encode('utf-8'), dst_path)
            except Exception:
                pass

        except Exception as e:
            self.logger.error(f"Failed to render augmented image for {src_path}: {e}")

    def _on_progress_updated(self, current, total, message):
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.update_progress(current, total, message)
            QApplication.processEvents()

    def _on_zip_success(self):
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.accept()
        self._show_toast("ZIP file created", 3000, color="#00C853")

    def _on_zip_error(self, error_message):
        if hasattr(self, 'progress_dialog') and self.progress_dialog and self.progress_dialog.isVisible():
            self.progress_dialog.reject()
        self._show_error(f"Failed to generate Zip file: {error_message}")

    def _on_zip_cancelled(self):
        if hasattr(self, 'zip_thread') and self.zip_thread and self.zip_thread.isRunning():
            self.zip_thread.terminate()
            self.zip_thread.wait()
        if hasattr(self, 'progress_dialog') and self.progress_dialog and self.progress_dialog.isVisible():
            self.progress_dialog.reject()

    def _show_toast(self, text, msec=3000, color="#00C853"):
        """Show a toast message if the parent has this method."""
        if hasattr(self.parent, '_show_toast'):
            self.parent._show_toast(text, msec, color)

    def _show_error(self, text):
        """Show an error message if the parent has this method."""
        if hasattr(self.parent, '_show_error'):
            self.parent._show_error(text)
        else:
            # Fallback to message box
            QMessageBox.critical(self.parent, "Error", text)
