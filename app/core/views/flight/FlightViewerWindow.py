"""Main window for the Flight Viewer.

Per plan §4 *Container*, this is a ``QMainWindow`` whose central widget
hosts a ``QMdiArea`` for the per-feed tiles. Each :class:`FlightTile`
is embedded in a :class:`_TileSubWindow` inside that area so it's a
true child widget of the viewer — it cannot escape the parent frame,
follows the parent on resize, and gets native min / max / close
chrome. The Mission Gallery and Map continue to live as right-side
``QDockWidget`` siblings.

The window is a pure view: it carries the toolbar/menu structure and
forwards user actions to its controller via Qt signals.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QMainWindow,
    QMdiArea,
    QMdiSubWindow,
    QSizePolicy,
    QStackedWidget,
)

from core.views.flight.flight_viewer_ui import Ui_FlightViewerWindow
from core.views.flight.MapDock import MapDock
from core.views.flight.MissionGalleryDock import MissionGalleryDock
from helpers.TranslationMixin import TranslationMixin


def _empty_icon() -> QIcon:
    """Return a 1×1 fully-transparent ``QIcon``.

    ``QMdiSubWindow`` displays an icon area in its title bar even when
    ``setWindowIcon(QIcon())`` is called; Qt falls back to the
    ``QApplication.windowIcon()`` or, on some platforms, a default Qt
    logo. A real-but-transparent icon displaces both without changing
    the title bar layout.
    """
    pm = QPixmap(1, 1)
    pm.fill(Qt.transparent)
    return QIcon(pm)


class _TileSubWindow(QMdiSubWindow):
    """``QMdiSubWindow`` that forwards its close to the embedded
    :class:`~core.views.flight.FlightTile.FlightTile`.

    A bare ``QMdiSubWindow.closeEvent`` would destroy the subwindow
    (and, via ``WA_DeleteOnClose``, its embedded widget) without ever
    invoking the child's ``closeEvent``. That would leak the per-tile
    ``FlightTileController`` lifecycle — its ``closeRequested`` slot
    wouldn't fire and the underlying ``WebRTCStreamService`` wouldn't
    stop. Forwarding the close lets the controller tear down cleanly
    before the subwindow goes away.
    """

    def closeEvent(self, event):  # noqa: N802 - Qt name
        widget = self.widget()
        if widget is not None:
            # Stop any in-flight recording so the MP4 segment is finalized
            # before the embedded tile is destroyed.
            if getattr(widget, "is_recording", False):
                try:
                    widget._stop_recording()
                except Exception:  # pragma: no cover - never block teardown
                    pass
            # Forward the close to the embedded tile's signal chain so
            # the controller's ``_on_tile_close`` → ``tear_down`` path
            # runs before the subwindow disappears.
            if hasattr(widget, "closeRequested"):
                try:
                    widget.closeRequested.emit(widget)
                except Exception:  # pragma: no cover - never block teardown
                    pass
        super().closeEvent(event)

    def mouseDoubleClickEvent(self, event):  # noqa: N802 - Qt name
        """Double-click on the title bar opens the rename dialog.

        Qt's default behavior toggles maximize on title-bar double-click;
        most operators expect double-click-to-rename (Windows Explorer,
        VS Code editor tabs, etc.). Maximize is still one click away on
        the title bar's maximize button.
        """
        # Only the title bar — clicks on the embedded widget land
        # elsewhere. ``Qt.LeftButton`` only; right-click double doesn't
        # carry the same convention.
        if event.button() == Qt.LeftButton:
            from PySide6.QtWidgets import QStyle
            title_height = self.style().pixelMetric(
                QStyle.PM_TitleBarHeight, None, self
            )
            if event.position().y() <= title_height:
                widget = self.widget()
                if widget is not None and hasattr(widget, "_prompt_rename"):
                    widget._prompt_rename()
                    event.accept()
                    return
        super().mouseDoubleClickEvent(event)


class FlightViewerWindow(TranslationMixin, QMainWindow, Ui_FlightViewerWindow):
    """Top-level Flight Viewer window."""

    addFeedRequested = Signal()
    toggleGalleryRequested = Signal(bool)
    toggleMapRequested = Signal(bool)
    saveLayoutRequested = Signal()
    restoreLayoutRequested = Signal()
    closeViewerRequested = Signal()
    openImageAnalysisRequested = Signal()
    openStreamingDetectorRequested = Signal()
    helpRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Tile widgets — kept as a set so look-ups by identity stay O(1).
        # The QMdiArea is the authoritative parent; this set just gives
        # the controller a quick "do we still have any?" check.
        self._tiles: set = set()
        # First-reveal flag for the Map dock. ``restoreState`` runs
        # *after* ``__init__`` and may bring the map back at a tiny
        # height from a previous session; we force-size on the first
        # ``show_map_dock`` call of the session regardless of whether
        # the dock is already visible.
        self._map_dock_sized: bool = False

        # The main toolbar (Add Feed / Toggle Gallery / Save / Restore) is
        # part of the window chrome — only the per-feed dock tiles should
        # be draggable. Locking it down avoids accidental drags during
        # operator handoff.
        self.mainToolBar.setMovable(False)
        self.mainToolBar.setFloatable(False)

        # Tile workspace: a ``QMdiArea`` replaces the placeholderLabel
        # central widget. Each feed becomes a ``QMdiSubWindow`` inside
        # the area so it's a *true child* of the viewer — it cannot
        # escape the parent's frame, it follows the parent on resize,
        # and it gets free min / max / close chrome courtesy of Qt's
        # built-in MDI sub-window machinery. The previous "floating
        # QDockWidget" pattern made the tile a top-level OS window
        # which doesn't honor parent-child containment.
        self._mdi_area = QMdiArea(self)
        self._mdi_area.setViewMode(QMdiArea.SubWindowView)
        self._mdi_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._mdi_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # A two-page stack toggles between the "no feeds yet" placeholder
        # text and the MDI workspace. Cleaner than overlaying widgets
        # on the MDI viewport.
        self._central_stack = QStackedWidget(self.centralwidget)
        # Force the stack to grab all available vertical + horizontal
        # space so the MDI area inside it can host full-size sub-windows.
        # ``QStackedWidget`` defaults to Expanding/Expanding but stating
        # it explicitly insulates us from cross-Qt-version surprises.
        self._central_stack.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.centralLayout.setContentsMargins(0, 0, 0, 0)
        self.centralLayout.removeWidget(self.placeholderLabel)
        self._central_stack.addWidget(self.placeholderLabel)  # index 0
        self._central_stack.addWidget(self._mdi_area)         # index 1
        self._central_stack.setCurrentIndex(0)
        self.centralLayout.addWidget(self._central_stack)

        self.setDockOptions(
            QMainWindow.AnimatedDocks
            | QMainWindow.AllowNestedDocks
            | QMainWindow.AllowTabbedDocks
            | QMainWindow.GroupedDragging
        )

        self.mission_gallery = MissionGalleryDock(self)
        # Detection rows pack a 96px thumbnail, ~140px of meta text, AND
        # the View / Copy GPS buttons. Anything under ~440px cuts the
        # buttons off the right edge.
        self.mission_gallery.setMinimumWidth(440)
        self.addDockWidget(Qt.RightDockWidgetArea, self.mission_gallery)
        self.mission_gallery.setVisible(True)

        # Map dock sits underneath the Mission Gallery on the right side
        # by default (plan §15 M3 — single dock; clicking a gallery row
        # centers the map). Hidden until the first detection arrives so
        # the operator isn't faced with an empty map at startup.
        self.map_dock = MapDock(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.map_dock)
        self.splitDockWidget(self.mission_gallery, self.map_dock, Qt.Vertical)
        self.map_dock.setVisible(False)

        # Initial right-dock sizing — give the gallery enough width for
        # multi-word detection labels + thumb + buttons. The vertical
        # split with the map dock can't be sized here because the map
        # starts hidden and Qt ignores ``resizeDocks`` on a non-visible
        # widget; we re-issue the call inside :meth:`show_map_dock` the
        # first time the map is revealed.
        self.resizeDocks([self.mission_gallery], [500], Qt.Horizontal)

        self.actionAddFeed.triggered.connect(self.addFeedRequested.emit)
        self.actionToggleGallery.toggled.connect(self.toggleGalleryRequested.emit)
        self.actionToggleMap.toggled.connect(self.toggleMapRequested.emit)
        self.actionSaveLayout.triggered.connect(self.saveLayoutRequested.emit)
        self.actionRestoreLayout.triggered.connect(self.restoreLayoutRequested.emit)
        self.actionOpenImageAnalysis.triggered.connect(
            self.openImageAnalysisRequested.emit
        )
        self.actionOpenStreamingDetector.triggered.connect(
            self.openStreamingDetectorRequested.emit
        )
        self.actionHelp.triggered.connect(self.helpRequested.emit)
        self.actionClose.triggered.connect(self.closeViewerRequested.emit)
        self.actionClose.triggered.connect(self.close)

        # Keep the menu check-states in sync if the operator closes
        # the docks via their own X buttons.
        self.mission_gallery.visibilityChanged.connect(self._on_gallery_visibility)
        self.map_dock.visibilityChanged.connect(self._on_map_visibility)

    # ------------------------------------------------------------------
    # gallery / map sync helpers
    # ------------------------------------------------------------------

    def _on_gallery_visibility(self, visible: bool) -> None:
        if self.actionToggleGallery.isChecked() != visible:
            self.actionToggleGallery.blockSignals(True)
            self.actionToggleGallery.setChecked(visible)
            self.actionToggleGallery.blockSignals(False)

    def _on_map_visibility(self, visible: bool) -> None:
        if self.actionToggleMap.isChecked() != visible:
            self.actionToggleMap.blockSignals(True)
            self.actionToggleMap.setChecked(visible)
            self.actionToggleMap.blockSignals(False)

    # ------------------------------------------------------------------
    # docking convenience
    # ------------------------------------------------------------------

    def dock_tile(self, tile) -> None:
        """Embed a :class:`FlightTile` as a sub-window of the MDI area.

        The tile becomes a true child widget of the viewer — it cannot
        leave the MDI area, the system min/max/close buttons in its
        title bar work natively, and resizing/moving the parent viewer
        clips children correctly without any manual clamping logic.
        """
        self._central_stack.setCurrentWidget(self._mdi_area)
        subwindow = _TileSubWindow(self._mdi_area)
        # Inherit the tile's translated title (set in ``FlightTile.__init__``)
        # and let the subwindow own destruction of its child widget.
        subwindow.setAttribute(Qt.WA_DeleteOnClose, True)
        subwindow.setWindowTitle(tile.windowTitle())
        # Suppress the inherited app icon — the QMdiSubWindow title bar
        # picks up the parent QMainWindow's icon by default, which puts
        # an ADIAT mark in every tile's chrome. A null QIcon falls back
        # to the Qt logo on some platforms; a 1×1 transparent icon
        # reliably blanks the slot.
        subwindow.setWindowIcon(_empty_icon())
        subwindow.setWidget(tile)
        # Add a "Rename Feed..." entry at the top of the subwindow's
        # system menu (the one that pops when the operator clicks the
        # title bar's icon or right-clicks the title bar). The same
        # action lives on the tile body's right-click menu, but the
        # title bar is the more natural place to look.
        system_menu = subwindow.systemMenu()
        if system_menu is not None:
            from PySide6.QtGui import QAction
            rename_action = QAction(
                self.tr("Rename Feed..."), system_menu
            )
            rename_action.triggered.connect(tile._prompt_rename)
            first_action = system_menu.actions()[0] if system_menu.actions() else None
            system_menu.insertAction(first_action, rename_action)
            if first_action is not None:
                system_menu.insertSeparator(first_action)
        # Remember the wrapper so ``remove_tile`` can find it from the
        # bare ``FlightTile`` reference the controller hands us.
        tile.setProperty("_mdi_subwindow", subwindow)
        # Default to a reasonable visible size; user can resize / maximize.
        subwindow.resize(800, 540)
        self._mdi_area.addSubWindow(subwindow)
        subwindow.show()
        self._tiles.add(tile)

    # ------------------------------------------------------------------
    # map dock helpers — sized lazily because the dock starts hidden
    # ------------------------------------------------------------------

    def show_map_dock(self) -> None:
        """Reveal the Map dock and split its height with the gallery.

        ``resizeDocks`` is a no-op on hidden widgets, so we can't size
        the gallery/map vertical split in ``__init__``. We also can't
        size it during ``restoreState`` because that runs after
        ``__init__`` and may revive the dock at a tiny height. The
        ``_map_dock_sized`` flag guarantees we force the split exactly
        once per session — on the first user-facing reveal. After that
        the operator's manual splitter drags stick.
        """
        self.map_dock.setVisible(True)
        if not self._map_dock_sized:
            self._map_dock_sized = True
            # Split ~55/45 so the map is usable at first glance instead
            # of a 30 px sliver under the gallery.
            self.resizeDocks(
                [self.mission_gallery, self.map_dock],
                [450, 350],
                Qt.Vertical,
            )

    def remove_tile(self, tile) -> None:
        """Close the sub-window wrapping ``tile`` and dispose it.

        ``QMdiSubWindow.close()`` honors ``WA_DeleteOnClose`` (set in
        :meth:`dock_tile`), which deletes both the wrapper and the
        embedded tile in one shot. We pop the tile from our tracking
        set first so the placeholder shows promptly.
        """
        self._tiles.discard(tile)
        subwindow = tile.property("_mdi_subwindow")
        try:
            if isinstance(subwindow, QMdiSubWindow):
                subwindow.close()
            else:
                tile.deleteLater()
        except RuntimeError:
            # Widget already deleted by Qt — fine.
            pass
        if not self._tiles:
            self._central_stack.setCurrentWidget(self.placeholderLabel)

    # ------------------------------------------------------------------
    # close handling — auto-save layout
    # ------------------------------------------------------------------

    def closeEvent(self, event):  # noqa: N802 - Qt name
        """Emit ``closeViewerRequested`` on any close path.

        The toolbar/menu Close action also fires this signal explicitly,
        but the user clicking the window's X button only triggers a
        ``QCloseEvent`` — without this override the layout/geometry save
        wired in :class:`FlightViewerController.shutdown` would be skipped
        on the most common exit path.
        """
        try:
            self.closeViewerRequested.emit()
        finally:
            super().closeEvent(event)
