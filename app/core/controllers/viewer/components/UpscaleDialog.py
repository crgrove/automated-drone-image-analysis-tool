"""
UpscaleDialog.py - Image upscaling dialog for ADIAT Viewer

Provides progressive image upscaling of the currently visible portion of an image.
User can repeatedly upscale to see higher resolution details.

Features:
- High-quality image upscaling using Lanczos interpolation
- Progressive upscaling (2x per iteration by default)
- Interactive zoom and pan controls (same as main viewer)
- Can upscale the visible portion again for further magnification
- Displays current upscale level in title
"""

import numpy as np
import cv2
import os
import urllib.request
from pathlib import Path
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QMessageBox, QSizePolicy, QComboBox, QProgressDialog
)
from PySide6.QtCore import QThread, Signal

from core.views.viewer.components.QtImageViewer import QtImageViewer

try:
    import qimage2ndarray
except ImportError:
    qimage2ndarray = None

try:
    from cv2 import dnn_superres
    OPENCV_SR_AVAILABLE = True
except ImportError:
    OPENCV_SR_AVAILABLE = False


class UpscaleWorker(QThread):
    """Background worker for upscaling operations."""

    finished = Signal(np.ndarray)  # Emits the upscaled image
    error = Signal(str)  # Emits error message
    progress = Signal(int)  # Emits progress percentage (0-100)

    def __init__(self, image_array, factor, method, sr_model=None):
        super().__init__()
        self.image_array = image_array
        self.factor = factor
        self.method = method
        self.sr_model = sr_model
        self._cancelled = False

    def cancel(self):
        """Request cancellation of the upscaling operation."""
        self._cancelled = True

    def run(self):
        """Run the upscaling in background."""
        try:
            if self._cancelled:
                return

            if self.method == 'edsr' and self.sr_model is not None:
                # Convert RGB to BGR for OpenCV
                self.progress.emit(10)
                if self._cancelled:
                    return

                bgr_image = cv2.cvtColor(self.image_array, cv2.COLOR_RGB2BGR)

                self.progress.emit(30)
                if self._cancelled:
                    return

                # Upscale (this is the slow part)
                upscaled_bgr = self.sr_model.upsample(bgr_image)

                self.progress.emit(80)
                if self._cancelled:
                    return

                # Convert back to RGB
                upscaled_rgb = cv2.cvtColor(upscaled_bgr, cv2.COLOR_BGR2RGB)

                self.progress.emit(100)
                if self._cancelled:
                    return

                self.finished.emit(upscaled_rgb)

            elif self.method == 'lanczos':
                # Fast Lanczos upscaling
                self.progress.emit(50)
                if self._cancelled:
                    return

                height, width = self.image_array.shape[:2]
                new_width = int(width * self.factor)
                new_height = int(height * self.factor)

                upscaled = cv2.resize(
                    self.image_array,
                    (new_width, new_height),
                    interpolation=cv2.INTER_LANCZOS4
                )

                self.progress.emit(100)
                if self._cancelled:
                    return

                self.finished.emit(upscaled)

        except Exception as e:
            if not self._cancelled:
                self.error.emit(str(e))


class UpscaleDialog(QDialog):
    """
    Dialog for displaying and progressively upscaling image portions.

    Allows users to upscale the currently visible area multiple times
    to see enhanced detail.
    """

    # Maximum total upscale factor to prevent memory issues
    MAX_UPSCALE_LEVEL = 32

    # Maximum dimension in pixels (to prevent excessive memory usage)
    MAX_DIMENSION = 16384

    # Model URLs and paths for OpenCV DNN Super-Resolution
    MODELS = {
        'EDSR_x2': {
            'url': 'https://github.com/Saafke/EDSR_Tensorflow/raw/master/models/EDSR_x2.pb',
            'scale': 2
        },
        'EDSR_x3': {
            'url': 'https://github.com/Saafke/EDSR_Tensorflow/raw/master/models/EDSR_x3.pb',
            'scale': 3
        },
        'EDSR_x4': {
            'url': 'https://github.com/Saafke/EDSR_Tensorflow/raw/master/models/EDSR_x4.pb',
            'scale': 4
        }
    }

    # Cache for loaded SR models
    _sr_models = {}

    def __init__(self, parent=None, image_array=None, upscale_factor=2, current_level=1, upscale_method='auto'):
        """
        Initialize the upscale dialog.

        Args:
            parent: Parent widget (usually the Viewer)
            image_array (np.ndarray): Image data as numpy array (RGB)
            upscale_factor (int): Upscale multiplier per iteration (default 2x)
            current_level (int): Current upscale level (1 = original, 2 = 2x, 4 = 4x, etc.)
            upscale_method (str): 'auto', 'fast', 'balanced', or 'best'
        """
        super().__init__(parent)

        self.upscale_factor = upscale_factor
        self.current_level = current_level
        self.image_array = image_array
        self.original_size = image_array.shape[:2] if image_array is not None else (0, 0)
        self.upscale_method = upscale_method

        # Detect GPU availability
        self.gpu_available = self._check_gpu_available()

        # Set up the dialog
        self.setWindowTitle(f"Upscaled View - {current_level}x")
        self.setModal(False)  # Non-modal so user can interact with main window

        # Create UI
        self._setup_ui()

        # Display the image
        if image_array is not None:
            self._display_image(image_array)

        # Set initial size (will be adjusted after image is loaded)
        self.resize(1000, 800)

    def _setup_ui(self):
        """Create the dialog UI components."""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Info label showing resolution
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("QLabel { font-weight: bold; padding: 5px; }")
        main_layout.addWidget(self.info_label)

        # Method selection layout
        method_layout = QHBoxLayout()
        method_label = QLabel("Upscale Method:")
        method_layout.addWidget(method_label)

        self.method_combo = QComboBox()
        self.method_combo.addItem("Auto (Recommended)", "auto")
        self.method_combo.addItem("Fast (Lanczos)", "fast")
        if OPENCV_SR_AVAILABLE:
            self.method_combo.addItem("Balanced (OpenCV EDSR)", "balanced")
        # Don't show "Best" option until it's implemented
        # self.method_combo.addItem("Best Quality (Real-ESRGAN) - Not Implemented", "best")

        # Set current method
        for i in range(self.method_combo.count()):
            if self.method_combo.itemData(i) == self.upscale_method:
                self.method_combo.setCurrentIndex(i)
                break

        self.method_combo.currentIndexChanged.connect(self._on_method_changed)
        method_layout.addWidget(self.method_combo)
        method_layout.addStretch()

        main_layout.addLayout(method_layout)

        # Image viewer (same as main viewer - supports zoom and pan)
        self.image_viewer = QtImageViewer(window=self, parent=self)
        self.image_viewer.setMinimumSize(400, 300)
        self.image_viewer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout.addWidget(self.image_viewer)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # Upres Again button
        self.upres_button = QPushButton("Upres Again")
        self.upres_button.setMinimumHeight(40)
        self.upres_button.clicked.connect(self._on_upres_again_clicked)
        self.upres_button.setToolTip(f"Upscale the currently visible portion by {self.upscale_factor}x")
        button_layout.addWidget(self.upres_button)

        # Quit button
        quit_button = QPushButton("Quit")
        quit_button.setMinimumHeight(40)
        quit_button.clicked.connect(self.close)
        quit_button.setToolTip("Close this upscale window")
        button_layout.addWidget(quit_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def _display_image(self, image_array):
        """
        Display the image in the dialog.

        Args:
            image_array (np.ndarray): Image data as numpy array (RGB or BGR)
        """
        if image_array is None or image_array.size == 0:
            return

        # Store the image array
        self.image_array = image_array

        # Display directly in the QtImageViewer (it accepts numpy arrays)
        self.image_viewer.setImage(image_array)

        # Update info label
        height, width = image_array.shape[:2]
        orig_h, orig_w = self.original_size
        self.info_label.setText(
            f"Resolution: {width} × {height} pixels | "
            f"Original: {orig_w} × {orig_h} pixels | "
            f"Upscale: {self.current_level}x | "
            f"Use mouse wheel to zoom, right-click to pan"
        )


    def _get_visible_portion(self):
        """
        Extract the currently visible portion of the image from the viewer.

        Returns:
            np.ndarray: The visible portion of the image, or None if error
        """
        if self.image_array is None or self.image_array.size == 0:
            return None

        try:
            # Get the currently visible viewport in scene coordinates
            visible_rect = self.image_viewer.mapToScene(
                self.image_viewer.viewport().rect()
            ).boundingRect()

            # Image dimensions
            img_height, img_width = self.image_array.shape[:2]

            # Calculate visible region bounds (scene coords map to image pixels)
            x1 = max(0, int(visible_rect.left()))
            y1 = max(0, int(visible_rect.top()))
            x2 = min(img_width, int(visible_rect.right()))
            y2 = min(img_height, int(visible_rect.bottom()))

            # Ensure valid region
            if x2 <= x1 or y2 <= y1:
                return None

            # Extract visible portion
            visible_portion = self.image_array[y1:y2, x1:x2].copy()

            return visible_portion

        except Exception as e:
            print(f"Error extracting visible portion: {e}")
            return None

    def _on_upres_again_clicked(self):
        """Handle 'Upres Again' button click."""
        # Get the currently visible portion
        visible_portion = self._get_visible_portion()

        if visible_portion is None or visible_portion.size == 0:
            QMessageBox.warning(
                self,
                "Upscale Error",
                "Unable to extract visible image portion."
            )
            return

        # Check if we're at maximum upscale level
        next_level = self.current_level * self.upscale_factor
        if next_level > self.MAX_UPSCALE_LEVEL:
            QMessageBox.warning(
                self,
                "Maximum Upscale Reached",
                f"Maximum upscale level of {self.MAX_UPSCALE_LEVEL}x has been reached.\n"
                f"Further upscaling is not allowed to prevent memory issues."
            )
            return

        # Check if resulting image would be too large
        height, width = visible_portion.shape[:2]
        new_height = height * self.upscale_factor
        new_width = width * self.upscale_factor

        if new_height > self.MAX_DIMENSION or new_width > self.MAX_DIMENSION:
            QMessageBox.warning(
                self,
                "Image Too Large",
                f"Upscaling would result in an image of {new_width}×{new_height} pixels.\n"
                f"Maximum allowed dimension is {self.MAX_DIMENSION} pixels.\n\n"
                f"Try zooming in to a smaller area before upscaling."
            )
            return

        # Check minimum size
        if height < 10 or width < 10:
            QMessageBox.warning(
                self,
                "Image Too Small",
                f"Visible portion is too small ({width}×{height} pixels).\n"
                f"Please zoom in to a larger area before upscaling."
            )
            return

        # Upscale the visible portion
        self._upscale_image_async(visible_portion, self.upscale_factor, next_level)

    def _upscale_image_async(self, image_array, factor, next_level):
        """
        Upscale image asynchronously with progress dialog.

        Args:
            image_array (np.ndarray): Input image
            factor (int): Upscale factor
            next_level (int): Next upscale level for new dialog
        """
        if image_array is None or image_array.size == 0:
            return

        # Get current method
        method = self.method_combo.currentData()

        # Auto-select method based on image size and hardware
        if method == 'auto':
            method = self._auto_select_method(image_array)

        # Check if we need to show progress (only for slower methods)
        show_progress = method == 'balanced' and OPENCV_SR_AVAILABLE

        # For fast methods, just do it synchronously
        if not show_progress:
            try:
                upscaled_image = self._upscale_image(image_array, factor)
                self._create_new_dialog(upscaled_image, next_level)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Upscale Error",
                    f"An error occurred during upscaling:\n{str(e)}"
                )
            return

        # For EDSR, show progress dialog
        try:
            # Load SR model
            sr_model = self._load_sr_model(factor)
            if sr_model is None:
                # Fallback to fast method
                upscaled_image = self._upscale_lanczos(image_array, factor)
                self._create_new_dialog(upscaled_image, next_level)
                return

            # Create progress dialog with image info
            height, width = image_array.shape[:2]
            new_height, new_width = height * factor, width * factor
            progress_text = (
                f"Upscaling image with AI enhancement...\n"
                f"From {width}×{height} to {new_width}×{new_height} pixels\n"
                f"This may take a few seconds."
            )
            self.progress_dialog = QProgressDialog(
                progress_text,
                "Cancel",
                0,
                100,
                self
            )
            self.progress_dialog.setWindowTitle("Upscaling (OpenCV EDSR)")
            self.progress_dialog.setWindowModality(Qt.WindowModal)
            self.progress_dialog.setMinimumDuration(0)  # Show immediately for EDSR
            self.progress_dialog.setValue(0)

            # Create worker thread
            self.upscale_worker = UpscaleWorker(
                image_array.copy(),  # Copy to avoid threading issues
                factor,
                'edsr',
                sr_model
            )

            # Store next_level for when upscaling completes
            self._pending_next_level = next_level

            # Connect signals
            self.upscale_worker.finished.connect(self._on_upscale_finished)
            self.upscale_worker.error.connect(self._on_upscale_error)
            self.upscale_worker.progress.connect(self.progress_dialog.setValue)
            self.progress_dialog.canceled.connect(self._on_upscale_canceled)

            # Start upscaling
            self.upscale_worker.start()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Upscale Error",
                f"Failed to start upscaling:\n{str(e)}"
            )

    def _create_new_dialog(self, upscaled_image, next_level):
        """Create new dialog with upscaled image."""
        if upscaled_image is None:
            return

        new_dialog = UpscaleDialog(
            self.parent(),
            upscaled_image,
            upscale_factor=self.upscale_factor,
            current_level=next_level,
            upscale_method=self.upscale_method
        )
        new_dialog.show()

    def _on_upscale_finished(self, upscaled_image):
        """Handle upscaling completion."""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()

        self._create_new_dialog(upscaled_image, self._pending_next_level)

    def _on_upscale_error(self, error_msg):
        """Handle upscaling error."""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()

        QMessageBox.critical(
            self,
            "Upscale Error",
            f"An error occurred during upscaling:\n{error_msg}"
        )

    def _on_upscale_canceled(self):
        """Handle upscaling cancellation."""
        if hasattr(self, 'upscale_worker'):
            self.upscale_worker.cancel()
            self.upscale_worker.wait()  # Wait for thread to finish

    def _upscale_image(self, image_array, factor=2):
        """
        Upscale image using selected method.

        Args:
            image_array (np.ndarray): Input image
            factor (int): Upscale factor

        Returns:
            np.ndarray: Upscaled image
        """
        if image_array is None or image_array.size == 0:
            return None

        # Get current method
        method = self.method_combo.currentData()

        # Auto-select method based on image size and hardware
        if method == 'auto':
            method = self._auto_select_method(image_array)

        # Upscale using selected method
        try:
            if method == 'balanced' and OPENCV_SR_AVAILABLE:
                return self._upscale_opencv_edsr(image_array, factor)
            elif method == 'best':
                # Real-ESRGAN not implemented yet
                QMessageBox.warning(
                    self,
                    "Method Not Available",
                    "Real-ESRGAN is not yet implemented.\nFalling back to Lanczos interpolation."
                )
                return self._upscale_lanczos(image_array, factor)
            else:  # 'fast' or fallback
                return self._upscale_lanczos(image_array, factor)
        except Exception as e:
            print(f"Upscaling error with method '{method}': {e}")
            # Fallback to Lanczos
            return self._upscale_lanczos(image_array, factor)

    def _upscale_lanczos(self, image_array, factor=2):
        """
        Upscale using Lanczos interpolation (fast, traditional method).

        Args:
            image_array (np.ndarray): Input image
            factor (int): Upscale factor

        Returns:
            np.ndarray: Upscaled image
        """
        height, width = image_array.shape[:2]
        new_width = int(width * factor)
        new_height = int(height * factor)

        upscaled = cv2.resize(
            image_array,
            (new_width, new_height),
            interpolation=cv2.INTER_LANCZOS4
        )

        return upscaled

    def _upscale_opencv_edsr(self, image_array, factor=2):
        """
        Upscale using OpenCV DNN Super-Resolution (EDSR model).

        Args:
            image_array (np.ndarray): Input image (RGB)
            factor (int): Upscale factor (2, 3, or 4)

        Returns:
            np.ndarray: Upscaled image
        """
        if not OPENCV_SR_AVAILABLE:
            raise ImportError("OpenCV DNN Super-Resolution not available")

        # Limit to supported scales
        if factor not in [2, 3, 4]:
            print(f"EDSR doesn't support {factor}x, falling back to Lanczos")
            return self._upscale_lanczos(image_array, factor)

        # Load model
        sr = self._load_sr_model(factor)
        if sr is None:
            print("Failed to load SR model, falling back to Lanczos")
            return self._upscale_lanczos(image_array, factor)

        # Convert RGB to BGR for OpenCV
        bgr_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)

        # Upscale
        try:
            upscaled_bgr = sr.upsample(bgr_image)
            # Convert back to RGB
            upscaled_rgb = cv2.cvtColor(upscaled_bgr, cv2.COLOR_BGR2RGB)
            return upscaled_rgb
        except Exception as e:
            print(f"EDSR upscaling failed: {e}, falling back to Lanczos")
            return self._upscale_lanczos(image_array, factor)

    def _check_gpu_available(self):
        """
        Check if GPU acceleration is available.

        Returns:
            bool: True if GPU is available
        """
        try:
            # Check for CUDA
            if cv2.cuda.getCudaEnabledDeviceCount() > 0:
                return True
        except:
            pass
        return False

    def _on_method_changed(self, index):
        """Handle method selection change."""
        method = self.method_combo.currentData()
        self.upscale_method = method
        print(f"Upscale method changed to: {method}")

    def _auto_select_method(self, image_array):
        """
        Automatically select upscale method based on image size and hardware.

        Args:
            image_array (np.ndarray): Image to upscale

        Returns:
            str: Selected method ('fast', 'balanced', or 'best')
        """
        pixels = image_array.shape[0] * image_array.shape[1]

        # Large images (> 4 megapixels) or no OpenCV SR -> use fast
        if pixels > 4000000 or not OPENCV_SR_AVAILABLE:
            return 'fast'

        # Medium/small images with OpenCV SR -> use balanced
        if OPENCV_SR_AVAILABLE:
            return 'balanced'

        # Fallback
        return 'fast'

    def _get_models_dir(self):
        """
        Get the directory for storing SR models.

        Returns:
            Path: Path to models directory
        """
        # Store models in app data directory
        app_dir = Path.home() / '.adiat' / 'sr_models'
        app_dir.mkdir(parents=True, exist_ok=True)
        return app_dir

    def _download_model(self, model_name):
        """
        Download SR model if not already cached.

        Args:
            model_name (str): Model name (e.g., 'EDSR_x2')

        Returns:
            Path: Path to downloaded model file, or None if failed
        """
        if model_name not in self.MODELS:
            return None

        model_info = self.MODELS[model_name]
        model_path = self._get_models_dir() / f"{model_name}.pb"

        # Already downloaded
        if model_path.exists():
            return model_path

        # Download model
        try:
            print(f"Downloading {model_name} model...")

            # Show progress dialog
            progress = QProgressDialog(
                f"Downloading {model_name} model...",
                "Cancel",
                0,
                100,
                self
            )
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(0)

            def report_hook(block_num, block_size, total_size):
                if progress.wasCanceled():
                    raise Exception("Download cancelled")
                if total_size > 0:
                    percent = min(100, int(block_num * block_size * 100 / total_size))
                    progress.setValue(percent)

            urllib.request.urlretrieve(
                model_info['url'],
                str(model_path),
                reporthook=report_hook
            )

            progress.setValue(100)
            print(f"Model downloaded to: {model_path}")
            return model_path

        except Exception as e:
            print(f"Failed to download model {model_name}: {e}")
            if model_path.exists():
                model_path.unlink()  # Remove partial download
            return None

    def _load_sr_model(self, scale):
        """
        Load OpenCV Super-Resolution model.

        Args:
            scale (int): Upscale factor (2, 3, or 4)

        Returns:
            dnn_superres.DnnSuperResImpl: Loaded model, or None if failed
        """
        if not OPENCV_SR_AVAILABLE:
            return None

        model_name = f'EDSR_x{scale}'

        # Check cache
        if model_name in self._sr_models:
            return self._sr_models[model_name]

        # Download model if needed
        model_path = self._download_model(model_name)
        if model_path is None:
            return None

        try:
            # Create SR object
            sr = dnn_superres.DnnSuperResImpl_create()

            # Read and set model
            sr.readModel(str(model_path))
            sr.setModel("edsr", scale)

            # Cache the model
            self._sr_models[model_name] = sr

            print(f"Loaded SR model: {model_name}")
            return sr

        except Exception as e:
            print(f"Failed to load SR model {model_name}: {e}")
            return None

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        # 'E' key to upscale again
        if event.key() == Qt.Key_E:
            self._on_upres_again_clicked()
            event.accept()
        # 'Q' key to quit
        elif event.key() == Qt.Key_Q:
            self.close()
            event.accept()
        else:
            super().keyPressEvent(event)
