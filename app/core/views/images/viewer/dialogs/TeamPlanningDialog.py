"""
TeamPlanningDialog - Dialog for assigning flagged AOIs to field verification teams.

Provides a split-pane UI with an interactive map on the left and team/AOI
management on the right.  Follows the same non-modal dialog pattern used
by GPSMapDialog.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QInputDialog,
    QWidget, QFrame, QMessageBox, QToolButton, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtGui import QKeySequence, QShortcut, QColor, QIcon, QPixmap, QPainter

from core.views.images.viewer.widgets.TeamPlanningMapView import TeamPlanningMapView
from helpers.TranslationMixin import TranslationMixin

# Predefined palette for auto-assigned team colours
TEAM_PALETTE = [
    '#E74C3C', '#3498DB', '#2ECC71', '#F39C12', '#9B59B6',
    '#1ABC9C', '#E67E22', '#2980B9', '#27AE60', '#C0392B',
    '#8E44AD', '#16A085', '#D35400', '#2C3E50', '#F1C40F',
]


def _color_icon(hex_color: str, size: int = 16) -> QIcon:
    """Create a small square icon filled with the given colour."""
    px = QPixmap(size, size)
    px.fill(QColor(hex_color))
    painter = QPainter(px)
    painter.setPen(QColor(0, 0, 0))
    painter.drawRect(0, 0, size - 1, size - 1)
    painter.end()
    return QIcon(px)


class TeamPlanningDialog(TranslationMixin, QDialog):
    """Dialog for dividing flagged AOIs among field teams.

    Signals:
        teams_changed: Emitted whenever teams or assignments change.
        export_team_pdf(str): Request PDF export for the named team.
        export_all_pdfs: Request batch PDF export for every team + master.
    """

    teams_changed = Signal()
    export_team_pdf = Signal(str)
    export_all_pdfs = Signal()

    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle(self.tr("Plan Verification"))
        self.setModal(False)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.resize(1100, 700)

        self._teams: list[dict] = []  # [{name, color}]
        self._palette_idx = 0

        self._setup_ui()
        self._apply_translations()
        self.setWindowTitle(self.tr("Plan Verification"))
        self._setup_shortcuts()

    # ------------------------------------------------------------------ UI
    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(6, 6, 6, 6)

        splitter = QSplitter(Qt.Orientation.Horizontal, self)

        # --- left: map ---
        map_container = QWidget()
        map_layout = QVBoxLayout(map_container)
        map_layout.setContentsMargins(0, 0, 0, 0)

        self.map_view = TeamPlanningMapView(self)
        self.map_view.tile_loader.tile_error.connect(self._on_tile_error)
        map_layout.addWidget(self.map_view)

        # Map toolbar
        map_toolbar = QHBoxLayout()
        self.btn_zoom_in = QPushButton(self.tr("Zoom In (+)"))
        self.btn_zoom_in.clicked.connect(self.map_view.zoom_in)
        self.btn_zoom_out = QPushButton(self.tr("Zoom Out (-)"))
        self.btn_zoom_out.clicked.connect(self.map_view.zoom_out)
        self.btn_fit = QPushButton(self.tr("Fit All (F)"))
        self.btn_fit.clicked.connect(self.map_view.fit_all_points)

        self.btn_select_mode = QPushButton(self.tr("Rectangle Select"))
        self.btn_select_mode.setCheckable(True)
        self.btn_select_mode.setToolTip(
            self.tr("Draw a rectangle on the map to select multiple AOIs")
        )
        self.btn_select_mode.toggled.connect(self.map_view.set_select_mode)

        self.btn_satellite = QPushButton(self.tr("Satellite View"))
        self.btn_satellite.setCheckable(True)
        self.btn_satellite.toggled.connect(self._toggle_tile_source)

        map_toolbar.addWidget(self.btn_zoom_in)
        map_toolbar.addWidget(self.btn_zoom_out)
        map_toolbar.addWidget(self.btn_fit)
        map_toolbar.addSpacing(10)
        map_toolbar.addWidget(self.btn_select_mode)
        map_toolbar.addStretch()
        map_toolbar.addWidget(self.btn_satellite)
        map_layout.addLayout(map_toolbar)

        splitter.addWidget(map_container)

        # --- right: team panel ---
        panel = QWidget()
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(4, 0, 4, 0)

        # Teams header
        teams_header = QHBoxLayout()
        teams_label = QLabel(self.tr("Teams"))
        teams_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        self.btn_add_team = QPushButton(self.tr("+ New"))
        self.btn_add_team.setToolTip(self.tr("Create a new field team"))
        self.btn_add_team.clicked.connect(self._on_add_team)
        self.btn_remove_team = QPushButton(self.tr("✕ Remove"))
        self.btn_remove_team.setToolTip(self.tr("Remove the selected team"))
        self.btn_remove_team.clicked.connect(self._on_remove_team)
        teams_header.addWidget(teams_label)
        teams_header.addStretch()
        teams_header.addWidget(self.btn_add_team)
        teams_header.addWidget(self.btn_remove_team)
        panel_layout.addLayout(teams_header)

        # Team list
        self.team_list = QListWidget()
        self.team_list.setMaximumHeight(180)
        self.team_list.currentRowChanged.connect(self._on_team_selected)
        panel_layout.addWidget(self.team_list)

        # Assign button
        self.btn_assign = QPushButton(self.tr("Assign Selection ▶"))
        self.btn_assign.setToolTip(
            self.tr("Assign the selected AOIs on the map to the chosen team")
        )
        self.btn_assign.setStyleSheet("font-weight: bold; padding: 6px;")
        self.btn_assign.clicked.connect(self._on_assign_clicked)
        panel_layout.addWidget(self.btn_assign)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        panel_layout.addWidget(sep)

        # AOI list for selected team
        aoi_header = QLabel(self.tr("Team AOIs"))
        aoi_header.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 4px;")
        panel_layout.addWidget(aoi_header)

        self.aoi_list = QListWidget()
        self.aoi_list.currentRowChanged.connect(self._on_aoi_list_item_clicked)
        panel_layout.addWidget(self.aoi_list)

        # Export buttons
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setFrameShadow(QFrame.Shadow.Sunken)
        panel_layout.addWidget(sep2)

        self.btn_export_team = QPushButton(self.tr("Export Team PDF"))
        self.btn_export_team.setToolTip(
            self.tr("Generate a PDF report for the selected team only")
        )
        self.btn_export_team.clicked.connect(self._on_export_team)
        panel_layout.addWidget(self.btn_export_team)

        self.btn_export_all = QPushButton(self.tr("Export All PDFs"))
        self.btn_export_all.setToolTip(
            self.tr("Generate one PDF per team plus a master summary PDF")
        )
        self.btn_export_all.clicked.connect(self._on_export_all)
        panel_layout.addWidget(self.btn_export_all)

        splitter.addWidget(panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        root_layout.addWidget(splitter)

        # Status / help label at bottom
        help_label = QLabel(
            self.tr(
                "Click to select AOI • Ctrl+Click to multi-select • "
                "Use Rectangle Select for area selection • Scroll to zoom"
            )
        )
        help_label.setStyleSheet("font-size: 10px; color: gray;")
        help_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root_layout.addWidget(help_label)

    def _setup_shortcuts(self):
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.close)
        QShortcut(QKeySequence(Qt.Key.Key_Plus), self, self.map_view.zoom_in)
        QShortcut(QKeySequence(Qt.Key.Key_Minus), self, self.map_view.zoom_out)
        QShortcut(QKeySequence(Qt.Key.Key_Equal), self, self.map_view.zoom_in)
        QShortcut(QKeySequence(Qt.Key.Key_F), self, self.map_view.fit_all_points)

    # ----------------------------------------------------------- team mgmt
    def set_teams(self, teams: list[dict]):
        """Populate the team list from saved data."""
        self._teams = list(teams)
        self._palette_idx = len(teams) % len(TEAM_PALETTE)
        self._refresh_team_list()

    def get_teams(self) -> list[dict]:
        return list(self._teams)

    def _next_default_name(self) -> str:
        """Auto-generate a team name like 'Team 1', 'Team 2', …"""
        base = self.tr("Team")
        idx = len(self._teams) + 1
        name = f"{base} {idx}"
        existing = {t['name'] for t in self._teams}
        while name in existing:
            idx += 1
            name = f"{base} {idx}"
        return name

    def _next_color(self) -> str:
        color = TEAM_PALETTE[self._palette_idx % len(TEAM_PALETTE)]
        self._palette_idx += 1
        return color

    def _on_add_team(self):
        default = self._next_default_name()
        name, ok = QInputDialog.getText(
            self, self.tr("New Team"), self.tr("Team name:"), text=default
        )
        if not ok or not name.strip():
            return
        name = name.strip()
        if any(t['name'] == name for t in self._teams):
            QMessageBox.warning(
                self, self.tr("Duplicate Name"),
                self.tr("A team named '{name}' already exists.").format(name=name),
            )
            return
        self._teams.append({'name': name, 'color': self._next_color()})
        self._refresh_team_list()
        self.team_list.setCurrentRow(len(self._teams))  # +1 because of "Unassigned"
        self.teams_changed.emit()

    def _on_remove_team(self):
        row = self.team_list.currentRow()
        if row <= 0:
            return  # "Unassigned" row or nothing selected
        self._teams.pop(row - 1)
        self._refresh_team_list()
        self.teams_changed.emit()

    def _refresh_team_list(self):
        self.team_list.clear()
        unassigned = QListWidgetItem(_color_icon('#BBBBBB'), self.tr("Unassigned"))
        unassigned.setData(Qt.ItemDataRole.UserRole, '')
        self.team_list.addItem(unassigned)
        for t in self._teams:
            item = QListWidgetItem(_color_icon(t['color']), t['name'])
            item.setData(Qt.ItemDataRole.UserRole, t['name'])
            self.team_list.addItem(item)

    def get_selected_team_name(self) -> str | None:
        """Return currently selected team name, or '' for Unassigned, or None if nothing."""
        item = self.team_list.currentItem()
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def _on_team_selected(self, row):
        """Refresh the AOI sub-list and map highlight when team selection changes."""
        pass  # Wired by the controller

    def _on_assign_clicked(self):
        """Placeholder — wired externally by controller."""
        pass

    def _on_aoi_list_item_clicked(self, row):
        """Placeholder — wired externally by controller."""
        pass

    def _on_export_team(self):
        team_name = self.get_selected_team_name()
        if team_name:
            self.export_team_pdf.emit(team_name)
        else:
            QMessageBox.information(
                self, self.tr("No Team Selected"),
                self.tr("Please select a team to export."),
            )

    def _on_export_all(self):
        if not self._teams:
            QMessageBox.information(
                self, self.tr("No Teams"),
                self.tr("Create at least one team before exporting."),
            )
            return
        self.export_all_pdfs.emit()

    def _toggle_tile_source(self, checked):
        if checked:
            self.btn_satellite.setText(self.tr("Map View"))
            self.map_view.set_tile_source('satellite')
        else:
            self.btn_satellite.setText(self.tr("Satellite View"))
            self.map_view.set_tile_source('map')

    def get_map_tile_source(self) -> str:
        """Return the currently active tile source ('map' or 'satellite')."""
        return getattr(self.map_view, '_current_tile_source', 'map')

    def _on_tile_error(self, msg):
        pass  # Silently degrade; tiles will use cache

    # ------------------------------------------------ AOI list management
    def set_aoi_list_items(self, items: list[dict]):
        """Populate the AOI sub-list in the right panel.

        Args:
            items: list of dicts with 'label' and 'uid'.
        """
        self.aoi_list.clear()
        for entry in items:
            item = QListWidgetItem(entry['label'])
            item.setData(Qt.ItemDataRole.UserRole, entry['uid'])
            self.aoi_list.addItem(item)

    def update_unassigned_count(self, count: int):
        """Update the (N) count displayed next to 'Unassigned'."""
        if self.team_list.count() > 0:
            item = self.team_list.item(0)
            item.setText(f"{self.tr('Unassigned')} ({count})")

    def update_team_count(self, team_name: str, count: int):
        """Update the (N) count displayed next to a team name."""
        for i in range(1, self.team_list.count()):
            item = self.team_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == team_name:
                item.setText(f"{team_name} ({count})")
                break

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(100, self.map_view.fit_all_points)
