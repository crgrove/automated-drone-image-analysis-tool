"""
AlignImageDialog - modal dialog for manually aligning a drone image's FOV.

Hosts an AlignImageView plus controls for rotating the drone image, fading the
map and FOV layers, toggling between satellite and street-map base layers, and
adding tie points. On accept it returns the four refined corner coordinates,
any tie points, and the viewing rotation.
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QSlider,
    QDoubleSpinBox, QPushButton, QDialogButtonBox, QMessageBox
)

from helpers.TranslationMixin import TranslationMixin
from helpers.PhotogrammetryHelper import corners_are_mirrored
from core.views.images.viewer.widgets.AlignImageView import AlignImageView


class AlignImageDialog(TranslationMixin, QDialog):
    """Modal dialog for refining a drone image's FOV against map imagery."""

    def __init__(self, parent, image_path, estimated_corners, bearing=0.0,
                 offline_only=False, saved_alignment=None):
        """
        Args:
            parent: Parent widget.
            image_path (str): Path to the drone image.
            estimated_corners (list): Four (lat, lon) corner estimates, TL TR BR BL.
            bearing (float): Camera bearing in degrees (initial drone rotation).
            offline_only (bool): Whether map tiles must come from cache only.
            saved_alignment (dict): Optional previously saved alignment to resume.
        """
        super().__init__(parent)
        self._showing_satellite = True
        self._setup_ui(offline_only)
        self._apply_translations()
        self._connect_signals()

        self.view.load(image_path, estimated_corners, bearing, saved_alignment)
        self._initial_rotation = self.view.get_rotation()
        self._set_rotation_controls(self._initial_rotation)

        # Apply the initial layer opacities so all three layers are visible.
        self.view.set_tile_opacity(self.tile_opacity_slider.value())
        self.view.set_fov_opacity(self.fov_slider.value())

        # Warn up front if a previously saved alignment was stored mirrored.
        if (saved_alignment and saved_alignment.get('corners')
                and corners_are_mirrored(saved_alignment['corners'])):
            self.status_label.setText(self.tr(
                "This saved alignment looks mirrored - re-place each corner "
                "handle on its matching photo corner (coloured squares)."
            ))
            self.status_label.setVisible(True)

    def _setup_ui(self, offline_only):
        """Build the dialog widgets."""
        self.setWindowTitle(self.tr("Align Image"))
        self.setModal(True)
        self.resize(960, 720)

        layout = QVBoxLayout(self)

        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #d9822b;")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        self.view = AlignImageView(self, offline_only=offline_only)
        layout.addWidget(self.view, stretch=1)

        controls = QGridLayout()

        self.rotation_label = QLabel()
        self.rotation_slider = QSlider(Qt.Horizontal)
        self.rotation_slider.setRange(0, 359)
        self.rotation_spin = QDoubleSpinBox()
        self.rotation_spin.setRange(0.0, 359.9)
        self.rotation_spin.setDecimals(1)
        self.rotation_spin.setSingleStep(1.0)
        self.rotation_spin.setSuffix("°")
        controls.addWidget(self.rotation_label, 0, 0)
        controls.addWidget(self.rotation_slider, 0, 1)
        controls.addWidget(self.rotation_spin, 0, 2)

        self.tile_opacity_label = QLabel()
        self.tile_opacity_slider = QSlider(Qt.Horizontal)
        self.tile_opacity_slider.setRange(0, 100)
        # Start partly transparent so the drone image behind it is visible.
        self.tile_opacity_slider.setValue(60)
        self.tile_opacity_value = QLabel("60%")
        controls.addWidget(self.tile_opacity_label, 1, 0)
        controls.addWidget(self.tile_opacity_slider, 1, 1)
        controls.addWidget(self.tile_opacity_value, 1, 2)

        self.fov_label = QLabel()
        self.fov_slider = QSlider(Qt.Horizontal)
        self.fov_slider.setRange(0, 100)
        self.fov_slider.setValue(100)
        self.fov_value = QLabel("100%")
        controls.addWidget(self.fov_label, 2, 0)
        controls.addWidget(self.fov_slider, 2, 1)
        controls.addWidget(self.fov_value, 2, 2)

        layout.addLayout(controls)

        button_row = QHBoxLayout()
        self.basemap_button = QPushButton()
        self.add_tie_button = QPushButton()
        self.reset_button = QPushButton()
        button_row.addWidget(self.basemap_button)
        button_row.addWidget(self.add_tie_button)
        button_row.addWidget(self.reset_button)
        button_row.addStretch(1)
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_row.addWidget(self.button_box)
        layout.addLayout(button_row)

    def _apply_translations(self):
        """Apply translatable strings to the widgets."""
        self.info_label.setText(self.tr(
            "Rotate the drone image to line it up with the map. The small "
            "coloured squares mark the photo's corners - drag each corner "
            "handle onto the map where its matching-coloured photo corner "
            "belongs. For extra accuracy, add tie points: put the IMAGE end on "
            "a feature in the drone photo and the MAP end on the same feature "
            "on the map."
        ))
        self.rotation_label.setText(self.tr("Rotation:"))
        self.tile_opacity_label.setText(self.tr("Map opacity:"))
        self.fov_label.setText(self.tr("FOV overlay opacity:"))
        self.basemap_button.setText(self.tr("Show Street Map"))
        self.add_tie_button.setText(self.tr("Add Tie Point"))
        self.reset_button.setText(self.tr("Reset"))

    def _connect_signals(self):
        """Wire up the control signals."""
        self.rotation_slider.valueChanged.connect(self._on_rotation_slider)
        self.rotation_spin.valueChanged.connect(self._on_rotation_spin)
        self.tile_opacity_slider.valueChanged.connect(self._on_tile_opacity)
        self.fov_slider.valueChanged.connect(self._on_fov_opacity)
        self.basemap_button.clicked.connect(self._on_toggle_basemap)
        self.add_tie_button.clicked.connect(self.view.add_tie_point)
        self.reset_button.clicked.connect(self._on_reset)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.view.tile_loader.tile_error.connect(self._on_tile_error)

    def _set_rotation_controls(self, degrees):
        """Set both rotation controls without re-triggering the view."""
        degrees = degrees % 360.0
        self.rotation_slider.blockSignals(True)
        self.rotation_spin.blockSignals(True)
        self.rotation_slider.setValue(int(round(degrees)) % 360)
        self.rotation_spin.setValue(min(degrees, 359.9))
        self.rotation_slider.blockSignals(False)
        self.rotation_spin.blockSignals(False)

    def _on_rotation_slider(self, value):
        self.rotation_spin.blockSignals(True)
        self.rotation_spin.setValue(float(value))
        self.rotation_spin.blockSignals(False)
        self.view.set_image_rotation(float(value))

    def _on_rotation_spin(self, value):
        self.rotation_slider.blockSignals(True)
        self.rotation_slider.setValue(int(round(value)) % 360)
        self.rotation_slider.blockSignals(False)
        self.view.set_image_rotation(value)

    def _on_tile_opacity(self, value):
        self.tile_opacity_value.setText(f"{value}%")
        self.view.set_tile_opacity(value)

    def _on_fov_opacity(self, value):
        self.fov_value.setText(f"{value}%")
        self.view.set_fov_opacity(value)

    def _on_toggle_basemap(self):
        """Toggle the base layer between satellite imagery and a street map."""
        self._showing_satellite = not self._showing_satellite
        if self._showing_satellite:
            self.view.set_tile_source('satellite')
            self.basemap_button.setText(self.tr("Show Street Map"))
        else:
            self.view.set_tile_source('map')
            self.basemap_button.setText(self.tr("Show Satellite"))

    def _on_reset(self):
        """Restore the corners, tie points and rotation to the metadata estimate."""
        self.view.reset_to_estimate()
        self._set_rotation_controls(self.view.get_rotation())

    def _on_tile_error(self, message):
        """Briefly surface a map tile loading error."""
        self.status_label.setText(message)
        self.status_label.setVisible(True)
        QTimer.singleShot(6000, lambda: self.status_label.setVisible(False))

    def accept(self):
        """Warn before saving if the placed corners look mirrored.

        Mirrored corners would map the drone image onto the ground flipped, so
        the user is given a chance to fix them before the alignment is saved.
        """
        corners = self.view.get_corner_gps()
        if corners and corners_are_mirrored(corners):
            box = QMessageBox(self)
            box.setIcon(QMessageBox.Icon.Warning)
            box.setWindowTitle(self.tr("Corners look mirrored"))
            box.setText(self.tr(
                "The four corners appear mirrored - the drone image would map "
                "to the ground flipped.\n\nEach corner handle is colour-matched "
                "to a corner of the drone photo (the small coloured squares). "
                "Make sure every handle sits where its matching photo corner "
                "belongs."
            ))
            box.setStandardButtons(
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel
            )
            cancel_button = box.button(QMessageBox.StandardButton.Cancel)
            cancel_button.setText(self.tr("Go Back and Fix"))
            box.setDefaultButton(cancel_button)
            if box.exec() != QMessageBox.StandardButton.Save:
                return
        super().accept()

    def get_result(self):
        """Return the refined alignment after the dialog is accepted.

        Returns:
            dict with 'corners' (4 (lat, lon) tuples), 'tie_points'
            (list of (u, v, lat, lon)) and 'rotation' (float degrees).
        """
        return {
            'corners': self.view.get_corner_gps(),
            'tie_points': self.view.get_tie_points(),
            'rotation': self.view.get_rotation(),
        }
