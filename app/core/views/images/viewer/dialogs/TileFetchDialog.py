"""
TileFetchDialog - options for downloading DEM / canopy tiles for an AOI.

Code-built (matching the MapExportDialog family) so no generated UI changes are
needed. Collects an AOI bounding box, product selection, and an output folder.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QCheckBox, QPushButton, QGroupBox, QFileDialog, QComboBox
)
from PySide6.QtGui import QDoubleValidator
from helpers.TranslationMixin import TranslationMixin


class TileFetchDialog(TranslationMixin, QDialog):
    # Emitted when the user picks an AOI fill source from the dropdown; the arg
    # is a stable key ('mission' or 'folder'). The controller owns the actual
    # fill logic (it has the mission images and the folder picker).
    fill_source_activated = Signal(str)
    # Emitted after the user manually edits any AOI bounds field, so the
    # controller can re-evaluate dataset coverage for the new area.
    aoi_changed = Signal()

    # Dataset coverage statuses (see set_dataset_status). Stable keys; the
    # controller computes them from the registered manifests.
    STATUS_COVERED = 'covered'
    STATUS_PARTIAL = 'partial'
    STATUS_NONE = 'none'
    STATUS_UNREGISTERED = 'unregistered'
    STATUS_UNKNOWN = 'unknown'

    def __init__(self, parent=None, default_bounds=None, has_mission=False,
                 default_output_dir=None, default_dem_checked=True):
        """
        Args:
            default_bounds: optional (min_lon, min_lat, max_lon, max_lat) to prefill.
            has_mission: whether a mission is loaded (enables the mission fill action).
            default_output_dir: optional folder to prefill the output field (the
                results folder, so downloaded tiles land beside the analysis).
            default_dem_checked: initial state of the USGS 3DEP DEM checkbox. The
                caller defaults it off when a usable terrain elevation source is
                already configured (see TileFetchController), since 3DEP is a
                resolution upgrade rather than a requirement.
        """
        super().__init__(parent)
        self.setWindowTitle(self.tr("Download Coverage Data"))
        self.setMinimumWidth(460)
        self._setup_ui(default_bounds, has_mission, default_output_dir,
                       default_dem_checked)
        self._apply_translations()

    def _setup_ui(self, default_bounds, has_mission, default_output_dir,
                  default_dem_checked=True):
        layout = QVBoxLayout(self)

        aoi_group = QGroupBox(self.tr("Area of Interest (WGS84)"))
        aoi_layout = QVBoxLayout()

        # Auto-fill source: a dropdown that fills the (editable) AOI fields from
        # the loaded mission or a chosen image folder. It reflects the current
        # selection like any combo box; the controller owns the fill logic (it
        # has the mission images) and connects fill_source_activated. A mission
        # item is only offered when one is loaded.
        fill_row = QHBoxLayout()
        self.fill_combo = QComboBox()
        self.fill_combo.setPlaceholderText(self.tr("Fill area from"))
        if has_mission:
            self.fill_combo.addItem(self.tr("Loaded mission extent"), "mission")
        self.fill_combo.addItem(self.tr("Image folder..."), "folder")
        self.fill_combo.setToolTip(self.tr(
            "Fill the area from the loaded mission's image GPS, or from an image folder."))
        self.fill_combo.activated.connect(self._on_fill_source_activated)
        # With a mission loaded the AOI is already auto-filled from it, so show
        # "Loaded mission extent"; otherwise show the placeholder (nothing filled).
        self.fill_combo.setCurrentIndex(0 if has_mission else -1)
        fill_row.addWidget(self.fill_combo)
        fill_row.addStretch()
        aoi_layout.addLayout(fill_row)

        grid = QGridLayout()
        self.min_lon_edit = QLineEdit()
        self.min_lat_edit = QLineEdit()
        self.max_lon_edit = QLineEdit()
        self.max_lat_edit = QLineEdit()
        for e in (self.min_lon_edit, self.min_lat_edit, self.max_lon_edit, self.max_lat_edit):
            e.setValidator(QDoubleValidator())
            # Manual edits re-evaluate what the registered tiles already cover.
            e.editingFinished.connect(self.aoi_changed.emit)
        if default_bounds:
            self.set_aoi(default_bounds)
        grid.addWidget(QLabel(self.tr("Min longitude:")), 0, 0)
        grid.addWidget(self.min_lon_edit, 0, 1)
        grid.addWidget(QLabel(self.tr("Min latitude:")), 0, 2)
        grid.addWidget(self.min_lat_edit, 0, 3)
        grid.addWidget(QLabel(self.tr("Max longitude:")), 1, 0)
        grid.addWidget(self.max_lon_edit, 1, 1)
        grid.addWidget(QLabel(self.tr("Max latitude:")), 1, 2)
        grid.addWidget(self.max_lat_edit, 1, 3)
        aoi_layout.addLayout(grid)

        buffer_row = QHBoxLayout()
        buffer_row.addWidget(QLabel(self.tr("Footprint buffer (m):")))
        self.buffer_edit = QLineEdit()
        self.buffer_edit.setValidator(QDoubleValidator(0.0, 100000.0, 1))
        self.buffer_edit.setFixedWidth(90)
        self.buffer_edit.setToolTip(self.tr(
            "Padding added around the camera positions so downloaded tiles cover the "
            "image footprints. Auto-sized from the mission; edit and re-fill to change."))
        buffer_row.addWidget(self.buffer_edit)
        buffer_row.addStretch()
        aoi_layout.addLayout(buffer_row)

        aoi_group.setLayout(aoi_layout)
        layout.addWidget(aoi_group)

        data_group = QGroupBox(self.tr("Datasets"))
        data_layout = QVBoxLayout()
        self.dem_checkbox = QCheckBox(self.tr("USGS 3DEP DEM"))
        self.dem_checkbox.setChecked(default_dem_checked)
        self.dem_checkbox.setToolTip(self.tr(
            "USGS 3DEP provides 1 m local elevation. Optional when you already "
            "have a terrain source configured (AWS Terrain Tiles online, or "
            "downloaded 3DEP) — enable it to download higher-resolution data."))
        self.dem_status_label = self._make_status_label()
        self.canopy_checkbox = QCheckBox(self.tr("Meta/WRI Canopy Height"))
        self.canopy_checkbox.setChecked(True)
        self.canopy_status_label = self._make_status_label()
        data_layout.addWidget(self.dem_checkbox)
        data_layout.addWidget(self.dem_status_label)
        data_layout.addWidget(self.canopy_checkbox)
        data_layout.addWidget(self.canopy_status_label)
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)

        # Destination: the central library is the default so downloads
        # accumulate in one mission-independent place; the results folder and
        # custom destinations remain for field kits / portability.
        self._default_output_dir = default_output_dir
        dest_row = QHBoxLayout()
        dest_row.addWidget(QLabel(self.tr("Store in:")))
        self.destination_combo = QComboBox()
        self.destination_combo.addItem(self.tr("Central tile library (recommended)"), "library")
        if default_output_dir:
            self.destination_combo.addItem(self.tr("Mission results folder"), "results")
        self.destination_combo.addItem(self.tr("Custom folder..."), "custom")
        self.destination_combo.setToolTip(self.tr(
            "The central library collects tiles from all missions in one place "
            "(they merge, nothing gets replaced) and registers automatically. "
            "Choose the results folder or a custom folder to keep tiles beside "
            "a specific mission instead."))
        self.destination_combo.currentIndexChanged.connect(self._on_destination_changed)
        dest_row.addWidget(self.destination_combo, 1)
        layout.addLayout(dest_row)

        out_row = QHBoxLayout()
        out_row.addWidget(QLabel(self.tr("Output folder:")))
        self.output_edit = QLineEdit()
        if default_output_dir:
            self.output_edit.setText(default_output_dir)
        self.output_button = QPushButton(self.tr("Browse..."))
        self.output_button.clicked.connect(self._browse_output)
        out_row.addWidget(self.output_edit, 1)
        out_row.addWidget(self.output_button)
        layout.addLayout(out_row)

        self.register_checkbox = QCheckBox(self.tr("Register in Preferences when complete"))
        self.register_checkbox.setChecked(True)
        layout.addWidget(self.register_checkbox)
        # Apply the default destination's field states (library: fixed path,
        # always registered).
        self._on_destination_changed()

        buttons = QHBoxLayout()
        buttons.addStretch()
        self.download_button = QPushButton(self.tr("Download"))
        self.download_button.setDefault(True)
        self.download_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton(self.tr("Cancel"))
        self.cancel_button.clicked.connect(self.reject)
        buttons.addWidget(self.download_button)
        buttons.addWidget(self.cancel_button)
        layout.addLayout(buttons)

    @staticmethod
    def _make_status_label():
        """Small indented caption under a dataset checkbox; hidden until set."""
        label = QLabel()
        label.setWordWrap(True)
        label.setIndent(22)
        label.setVisible(False)
        return label

    # status key -> (text builder key, color); texts live in _status_text so
    # they run through tr() at display time.
    _STATUS_COLORS = {
        'covered': "#00C853",
        'partial': "#E6A700",
        'none': "#E6A700",
        'unregistered': "#909090",
    }

    def _status_text(self, status, dataset):
        if status == self.STATUS_COVERED:
            return self.tr("This area is already covered by your registered tiles.")
        if status == self.STATUS_PARTIAL:
            return self.tr("Partially covered by your registered tiles — "
                           "downloading fills the gaps.")
        if status == self.STATUS_NONE:
            # State the consequence, not just the fact: elevation degrades to
            # the online baseline, canopy has no fallback at all.
            if dataset == 'dem':
                return self.tr("Your downloaded 1 m tiles don't include this area "
                               "— without this download, online AWS Terrain Tiles "
                               "(~30 m) are used here instead.")
            return self.tr("Your downloaded canopy tiles don't include this area "
                           "— without this download, POD runs with no canopy "
                           "attenuation here.")
        if status == self.STATUS_UNREGISTERED:
            if dataset == 'dem':
                return self.tr("No local elevation tiles registered — online AWS "
                               "Terrain Tiles (~30 m) serve as the baseline.")
            return self.tr("No canopy source is configured yet.")
        return ""

    def set_dataset_status(self, dem_status, canopy_status):
        """Show per-dataset coverage of the current AOI under each checkbox.

        Statuses are the STATUS_* keys; STATUS_UNKNOWN hides the caption.
        """
        for label, status, dataset in (
            (self.dem_status_label, dem_status, 'dem'),
            (self.canopy_status_label, canopy_status, 'canopy'),
        ):
            text = self._status_text(status, dataset)
            if not text:
                label.setVisible(False)
                continue
            label.setText(text)
            color = self._STATUS_COLORS.get(status, "#909090")
            label.setStyleSheet(f"color: {color};")
            label.setVisible(True)

    def get_destination(self):
        """Stable destination key: 'library' | 'results' | 'custom'."""
        return self.destination_combo.currentData()

    def _on_destination_changed(self):
        """Reflect the chosen destination in the output field and register row.

        The library destination pins the output to the central library path
        and always registers (that's the point of the library: one stable,
        accumulating source); the other destinations restore the manual
        field + opt-in registration.
        """
        dest = self.get_destination()
        if dest == 'library':
            from core.services.terrain.TileFetchService import library_root
            self.output_edit.setText(library_root())
            self.output_edit.setEnabled(False)
            self.output_button.setEnabled(False)
            self.register_checkbox.setChecked(True)
            self.register_checkbox.setVisible(False)
            return
        if dest == 'results' and self._default_output_dir:
            self.output_edit.setText(self._default_output_dir)
            self.output_edit.setEnabled(False)
            self.output_button.setEnabled(False)
        else:   # custom
            self.output_edit.setEnabled(True)
            self.output_button.setEnabled(True)
        self.register_checkbox.setVisible(True)

    def _browse_output(self):
        directory = QFileDialog.getExistingDirectory(self, self.tr("Select output folder"))
        if directory:
            self.output_edit.setText(directory)

    def _on_fill_source_activated(self, index):
        """Relay the chosen fill source (stable itemData key) to the controller."""
        key = self.fill_combo.itemData(index)
        if key:
            self.fill_source_activated.emit(key)

    def set_aoi(self, bounds):
        """Fill the four AOI fields from (min_lon, min_lat, max_lon, max_lat)."""
        self.min_lon_edit.setText(f"{bounds[0]:.6f}")
        self.min_lat_edit.setText(f"{bounds[1]:.6f}")
        self.max_lon_edit.setText(f"{bounds[2]:.6f}")
        self.max_lat_edit.setText(f"{bounds[3]:.6f}")

    def set_buffer(self, buffer_m):
        self.buffer_edit.setText(f"{buffer_m:.0f}")

    def get_buffer(self):
        """Buffer in meters, or None if empty/invalid."""
        try:
            v = float(self.buffer_edit.text())
            return v if v > 0 else None
        except ValueError:
            return None

    def get_bounds(self):
        """(min_lon, min_lat, max_lon, max_lat) or None if incomplete/invalid."""
        try:
            b = (float(self.min_lon_edit.text()), float(self.min_lat_edit.text()),
                 float(self.max_lon_edit.text()), float(self.max_lat_edit.text()))
        except ValueError:
            return None
        if b[0] >= b[2] or b[1] >= b[3]:
            return None
        return b

    def want_dem(self):
        return self.dem_checkbox.isChecked()

    def want_canopy(self):
        return self.canopy_checkbox.isChecked()

    def get_output_dir(self):
        return self.output_edit.text().strip()

    def should_register(self):
        return self.register_checkbox.isChecked()
