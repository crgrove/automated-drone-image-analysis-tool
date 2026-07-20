"""
GridReviewController - Orchestrates the viewer's grid review mode.

Grid review is a systematic human sweep for subjects the detection
algorithms miss (e.g. people in natural-tone clothing): the image is
divided into a grid, the reviewer steps cell-by-cell at a constant zoom
with the keyboard, each visited cell is marked reviewed, and progress is
persisted per image so a sweep can be resumed across sessions.

The controller owns the runtime state (mode active, current cell) and
coordinates the pieces that already exist elsewhere: cell math and
progress in GridReviewService, the painted grid in GridOverlayItem,
persistence via XmlService grid_* attributes on <image>, navigation via
the viewer's next/previous-image handlers, and progress display through
the status bar message dict.

Keyboard contract (keys are consumed only while the mode is active,
except S/Shift+S which work from anywhere in the viewer):
    S            toggle grid review mode
    Shift+S      open the grid settings dialog
    Space        mark current cell reviewed and advance (serpentine)
    Backspace /
    Shift+Space  step back one cell (no unmarking)
    Arrows       move one cell directionally without marking
    X            toggle reviewed state of the current cell
    Esc          exit the mode and restore the full-image view
"""

from PySide6.QtCore import QObject, Qt, QRectF, QTimer

from core.services.GridReviewService import GridReviewService
from core.services.LoggerService import LoggerService
from core.views.images.viewer.widgets.GridOverlayItem import GridOverlayItem
from helpers.TranslationMixin import TranslationMixin

# Fraction of the cell size shown beyond each cell edge when zoomed to a
# cell, so the reviewer sees slivers of the neighboring cells and objects
# straddling a boundary are not missed.
_CELL_ZOOM_MARGIN = 0.08

# Delay before persisting marked cells to the result XML. Saving rewrites
# the whole file (which can be large), so rapid Space presses are coalesced;
# the save is always flushed on image change, mode exit and window close.
_SAVE_DEBOUNCE_MS = 2000

_DEFAULT_GRID_SIZE = 4
_DEFAULT_MIN_PERSON_PX = 60
# Focus-guide subdivisions per side inside the active cell (3 -> nine).
_DEFAULT_SUBDIVISIONS = 3


class GridReviewController(TranslationMixin, QObject):
    """Controller for the grid review sweep in the results viewer."""

    def __init__(self, parent_viewer):
        """Initialize the grid review controller.

        Args:
            parent_viewer: The main Viewer instance.
        """
        super().__init__()
        self.parent = parent_viewer
        self.logger = LoggerService()
        self.active = False
        # Row-major index of the cell being reviewed, or None when inactive.
        self.current_cell = None
        # Grid dimensions for the current image's sweep. Mirrors the stored
        # grid when one exists; otherwise the suggestion/settings default.
        self._rows = _DEFAULT_GRID_SIZE
        self._cols = _DEFAULT_GRID_SIZE
        # The painted grid; created lazily once the image scene exists.
        self._overlay_item = None
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(_SAVE_DEBOUNCE_MS)
        self._save_timer.timeout.connect(self._flush_save)
        self._save_pending = False

    # ------------------------------------------------------------------ #
    #  Keyboard handling
    # ------------------------------------------------------------------ #
    def handle_key(self, e):
        """Handle a viewer key press.

        Called first from Viewer.keyPressEvent. Returns True when the key
        was consumed so every existing binding keeps working while the
        mode is inactive.

        Args:
            e (QKeyEvent): The key event.

        Returns:
            bool: True when the event was handled.
        """
        key = e.key()
        modifiers = e.modifiers()

        if key == Qt.Key_S and modifiers == Qt.NoModifier:
            self.toggle_mode()
            return True
        if key == Qt.Key_S and modifiers == Qt.ShiftModifier:
            self.open_settings_dialog()
            return True

        if not self.active:
            return False

        if key == Qt.Key_Space and modifiers == Qt.ShiftModifier:
            self._retreat()
            return True
        if key == Qt.Key_Space and modifiers == Qt.NoModifier:
            self._advance(mark=self._auto_mark_enabled())
            return True
        if key == Qt.Key_Backspace and modifiers == Qt.NoModifier:
            self._retreat()
            return True
        if key in (Qt.Key_Right, Qt.Key_Left, Qt.Key_Up, Qt.Key_Down) and modifiers == Qt.NoModifier:
            self._move_directional(key)
            return True
        if key == Qt.Key_X and modifiers == Qt.NoModifier:
            self._toggle_current_reviewed()
            return True
        if key == Qt.Key_Escape and modifiers == Qt.NoModifier:
            self.deactivate()
            return True

        return False

    # ------------------------------------------------------------------ #
    #  Mode lifecycle
    # ------------------------------------------------------------------ #
    def toggle_mode(self):
        """Toggle grid review mode on or off."""
        if self.active:
            self.deactivate()
        else:
            self.activate()

    def activate(self):
        """Enter grid review mode on the current image.

        Refused while the gallery is showing: the sweep is a single-image
        workflow and needs the main image canvas.
        """
        if self.active:
            return
        if getattr(self.parent, 'gallery_mode', False):
            status = getattr(self.parent, 'status_controller', None)
            if status is not None:
                status.show_toast(
                    self.tr("Grid review works in single-image mode — exit the gallery first."),
                    3000, "#B71C1C"
                )
            return
        image = self._current_image()
        if image is None:
            return

        self.active = True
        self._begin_image_sweep(image)
        self._sync_button_state()

    def deactivate(self):
        """Exit grid review mode, persist pending marks and restore the view."""
        if not self.active:
            self._sync_button_state()
            return

        self.active = False
        self.current_cell = None
        self._flush_save()
        if self._overlay_item is not None:
            self._overlay_item.hide()

        main_image = getattr(self.parent, 'main_image', None)
        if main_image is not None and not getattr(main_image, '_is_destroyed', True):
            main_image.resetZoom()

        self.parent.messages['Grid Review'] = None
        self._sync_button_state()

    def on_image_loaded(self):
        """React to the viewer finishing an image load.

        While the mode is active the freshly loaded image joins the sweep:
        the grid is reconfigured for its dimensions and the view zooms to
        its first unreviewed cell (overriding the zoom reset that just ran
        in ImageLoadController.load_image). When inactive the grid just
        stays hidden.
        """
        # An image change always flushes marks made on the previous image.
        self._flush_save()

        if not self.active:
            if self._overlay_item is not None:
                self._overlay_item.hide()
            return

        image = self._current_image()
        if image is None:
            self.deactivate()
            return
        self._begin_image_sweep(image)

    def cleanup(self):
        """Persist any pending marks; called from Viewer.closeEvent."""
        self._flush_save()

    # ------------------------------------------------------------------ #
    #  Settings dialog
    # ------------------------------------------------------------------ #
    def open_settings_dialog(self):
        """Open the grid settings dialog and apply accepted values."""
        # Imported here rather than at module top: the dialog pulls in the
        # generated UI module, which the headless controller tests don't need.
        from core.views.images.viewer.dialogs.GridReviewDialog import GridReviewDialog

        suggestion = self._suggest_dims()
        person_px = None
        if suggestion is not None:
            main_image = self.parent.main_image
            cell_w = main_image.sceneRect().width() / suggestion[1]
            try:
                gsd_cm = self.parent._get_current_image_gsd()
            except Exception:
                gsd_cm = None
            person_px = GridReviewService.person_screen_px(
                gsd_cm, cell_w, main_image.viewport().width()
            )

        dialog = GridReviewDialog(
            self.parent,
            settings_service=getattr(self.parent, 'settings_service', None),
            current_rows=self._rows,
            current_cols=self._cols,
            auto_mark=self._auto_mark_enabled(),
            sub_guide=self._sub_guide_enabled(),
            suggestion=suggestion,
            person_px=person_px,
        )
        if dialog.exec():
            rows, cols, _ = dialog.values()
            if dialog.apply_to_all():
                self._apply_grid_to_all(rows, cols)
            else:
                self._apply_grid_size(rows, cols)
            # Pick up a focus-guide toggle even when the grid size is
            # unchanged (the apply path may have returned without redraw).
            image = self._current_image()
            if self.active and image is not None and self._overlay_item is not None:
                self._refresh_overlay(image)

    def _apply_grid_size(self, rows, cols):
        """Resize the active sweep's grid when that is safe.

        An image whose sweep already has marked cells keeps its stored
        grid — resizing would silently remap the persisted cell indices.
        The accepted size still becomes the default for unstarted images
        (the dialog wrote it to settings).
        """
        if not self.active:
            return
        image = self._current_image()
        if image is None:
            return

        grid = image.get('grid_review')
        if grid and grid['reviewed']:
            if (int(rows), int(cols)) != (grid['rows'], grid['cols']):
                status = getattr(self.parent, 'status_controller', None)
                if status is not None:
                    status.show_toast(
                        self.tr("This image keeps its existing grid — the new size applies to unstarted images."),
                        3500
                    )
            return

        if grid:
            # A stored but unmarked grid is safe to discard.
            image['grid_review'] = None
            image_xml = image.get('xml')
            if image_xml is not None:
                self.parent.xml_service.clear_image_grid_review(image_xml)

        self._rows = max(1, int(rows))
        self._cols = max(1, int(cols))
        self.current_cell = GridReviewService.serpentine_order(self._rows, self._cols)[0]
        self._refresh_overlay(image)
        self._zoom_to_cell(self.current_cell)
        self._update_status()

    @staticmethod
    def _has_conflicting_progress(image, rows, cols):
        """True when an image has reviewed cells recorded at a different size."""
        grid = image.get('grid_review')
        return bool(grid and grid['reviewed'] and (grid['rows'], grid['cols']) != (rows, cols))

    def _apply_grid_to_all(self, rows, cols):
        """Apply the chosen grid size to every image in the dataset.

        Images with no review progress (and images already at this size)
        take the new grid directly. Images already reviewed at a different
        size would lose their cell mapping if resized, so the reviewer is
        asked whether to reset those too or leave them at their own size.
        The whole dataset is written once at the end.
        """
        images = getattr(self.parent, 'images', None)
        if not images:
            return
        rows = max(1, int(rows))
        cols = max(1, int(cols))

        conflicting = [img for img in images
                       if self._has_conflicting_progress(img, rows, cols)]
        reset_conflicting = False
        if conflicting:
            from PySide6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self.parent,
                self.tr("Apply Grid to All Images"),
                self.tr(
                    "{n} image(s) already have review progress recorded at a "
                    "different grid size.\n\nReset their progress and apply "
                    "{rows}×{cols} to them too?\n\n"
                    "Yes resets them; No keeps them at their current size."
                ).format(n=len(conflicting), rows=rows, cols=cols),
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.No,
            )
            if reply == QMessageBox.Cancel:
                return
            reset_conflicting = (reply == QMessageBox.Yes)

        for img in images:
            if not reset_conflicting and self._has_conflicting_progress(img, rows, cols):
                continue  # keep a started image at its own size
            grid = img.get('grid_review')
            if grid and (grid['rows'], grid['cols']) == (rows, cols):
                reviewed = grid['reviewed']  # same size -> progress still valid
            else:
                reviewed = set()
            img['grid_review'] = {'rows': rows, 'cols': cols, 'reviewed': reviewed}
            image_xml = img.get('xml')
            if image_xml is not None:
                self.parent.xml_service.set_image_grid_review(image_xml, rows, cols, reviewed)

        self._save_pending = True
        self._flush_save()

        # Re-grid the current view so the change is visible immediately.
        if self.active:
            image = self._current_image()
            if image is not None:
                self._begin_image_sweep(image)

    # ------------------------------------------------------------------ #
    #  Sweep logic
    # ------------------------------------------------------------------ #
    def _begin_image_sweep(self, image):
        """Configure the grid for *image* and move to its first open cell."""
        self._rows, self._cols = self._grid_dims_for_image(image)
        reviewed = self._reviewed_cells(image)

        order = GridReviewService.serpentine_order(self._rows, self._cols)
        self.current_cell = next((c for c in order if c not in reviewed), order[0])

        self._refresh_overlay(image)
        self._zoom_to_cell(self.current_cell)
        self._update_status()

    def _advance(self, mark=True):
        """Mark the current cell (optionally) and step forward in scan order.

        Stepping past the last cell saves the image's sweep and moves on to
        the next image; on_image_loaded then resumes at that image's first
        unreviewed cell.
        """
        if self.current_cell is None:
            return
        if mark:
            self._set_reviewed(self.current_cell, True)

        order = GridReviewService.serpentine_order(self._rows, self._cols)
        position = order.index(self.current_cell)
        if position + 1 < len(order):
            self.current_cell = order[position + 1]
            self._on_cell_changed()
        else:
            status = getattr(self.parent, 'status_controller', None)
            if status is not None:
                status.show_toast(self.tr("Image fully reviewed — advancing"), 1500)
            self._flush_save()
            self.parent._nextImageButton_clicked()

    def _retreat(self):
        """Step back one cell in scan order without changing marks."""
        if self.current_cell is None:
            return
        order = GridReviewService.serpentine_order(self._rows, self._cols)
        position = order.index(self.current_cell)
        if position > 0:
            self.current_cell = order[position - 1]
            self._on_cell_changed()

    def _move_directional(self, key):
        """Move one cell in the arrow direction, clamped at the grid edges."""
        if self.current_cell is None:
            return
        row, col = divmod(self.current_cell, self._cols)
        if key == Qt.Key_Right:
            col = min(col + 1, self._cols - 1)
        elif key == Qt.Key_Left:
            col = max(col - 1, 0)
        elif key == Qt.Key_Down:
            row = min(row + 1, self._rows - 1)
        elif key == Qt.Key_Up:
            row = max(row - 1, 0)
        target = row * self._cols + col
        if target != self.current_cell:
            self.current_cell = target
            self._on_cell_changed()

    def _toggle_current_reviewed(self):
        """Toggle the reviewed state of the current cell."""
        if self.current_cell is None:
            return
        image = self._current_image()
        if image is None:
            return
        currently = self.current_cell in self._reviewed_cells(image)
        self._set_reviewed(self.current_cell, not currently)

    def _on_cell_changed(self):
        """Update overlay highlight, zoom and status after a cell move."""
        if self._overlay_item is not None:
            self._overlay_item.set_current_index(self.current_cell)
        self._zoom_to_cell(self.current_cell)
        self._update_status()

    # ------------------------------------------------------------------ #
    #  Reviewed-state bookkeeping and persistence
    # ------------------------------------------------------------------ #
    def _set_reviewed(self, cell_index, reviewed):
        """Record a cell's reviewed state in memory, XML and the overlay."""
        image = self._current_image()
        if image is None:
            return

        grid = image.get('grid_review')
        if not grid:
            grid = {'rows': self._rows, 'cols': self._cols, 'reviewed': set()}
            image['grid_review'] = grid

        if reviewed:
            grid['reviewed'].add(cell_index)
        else:
            grid['reviewed'].discard(cell_index)

        image_xml = image.get('xml')
        if image_xml is not None:
            self.parent.xml_service.set_image_grid_review(
                image_xml, grid['rows'], grid['cols'], grid['reviewed']
            )
            self._save_pending = True
            self._save_timer.start()

        if self._overlay_item is not None:
            self._overlay_item.set_reviewed(grid['reviewed'])
        self._update_status()

    def _flush_save(self):
        """Write the result XML now if any marks are waiting."""
        self._save_timer.stop()
        if not self._save_pending:
            return
        self._save_pending = False
        try:
            self.parent.xml_service.save_xml_file(self.parent.xml_path)
        except Exception as e:
            self.logger.error(f"Grid review: could not save result file: {e}")

    # ------------------------------------------------------------------ #
    #  Grid geometry and view
    # ------------------------------------------------------------------ #
    def _grid_dims_for_image(self, image):
        """Determine the grid for an image: stored > GSD suggestion > settings."""
        grid = image.get('grid_review')
        if grid:
            return (grid['rows'], grid['cols'])

        suggestion = self._suggest_dims()
        if suggestion is not None:
            return suggestion

        return self._default_dims()

    def _suggest_dims(self):
        """Suggest grid dimensions from the current image's GSD, or None."""
        try:
            gsd_cm = self.parent._get_current_image_gsd()
        except Exception:
            gsd_cm = None
        main_image = getattr(self.parent, 'main_image', None)
        if gsd_cm is None or main_image is None or getattr(main_image, '_is_destroyed', True):
            return None

        scene_rect = main_image.sceneRect()
        viewport = main_image.viewport()
        return GridReviewService.suggest_grid(
            scene_rect.width(), scene_rect.height(), gsd_cm,
            viewport.width(), viewport.height(),
            min_person_px=self._min_person_px()
        )

    def _default_dims(self):
        """Read the default grid size from settings."""
        rows = self._int_setting('GridReviewRows', _DEFAULT_GRID_SIZE)
        cols = self._int_setting('GridReviewCols', _DEFAULT_GRID_SIZE)
        return (max(1, rows), max(1, cols))

    def _min_person_px(self):
        return self._int_setting('GridReviewMinPersonPx', _DEFAULT_MIN_PERSON_PX)

    def _auto_mark_enabled(self):
        service = getattr(self.parent, 'settings_service', None)
        if service is None:
            return True
        try:
            return service.get_bool_setting('GridReviewAutoMark', True)
        except Exception:
            return True

    def _sub_guide_enabled(self):
        """Whether the in-cell focus guide is shown (defaults on)."""
        service = getattr(self.parent, 'settings_service', None)
        if service is None:
            return True
        try:
            return service.get_bool_setting('GridReviewSubGuide', True)
        except Exception:
            return True

    def _subdivisions(self):
        """Focus-guide subdivisions per side (1 = guide off)."""
        return _DEFAULT_SUBDIVISIONS if self._sub_guide_enabled() else 1

    def _int_setting(self, name, default):
        service = getattr(self.parent, 'settings_service', None)
        if service is None:
            return default
        try:
            return int(service.get_setting(name, default))
        except (TypeError, ValueError):
            return default

    def _refresh_overlay(self, image):
        """(Re)configure the painted grid for the current image."""
        if not self._ensure_overlay():
            return
        scene_rect = self.parent.main_image.sceneRect()
        self._overlay_item.configure(
            scene_rect.width(), scene_rect.height(),
            self._rows, self._cols,
            self._reviewed_cells(image), self.current_cell,
            self._subdivisions()
        )
        self._overlay_item.show()

    def _ensure_overlay(self):
        """Create the grid graphics item in the image scene when needed.

        Returns:
            bool: True when the overlay item is available for use.
        """
        if self._overlay_item is not None:
            return True

        main_image = getattr(self.parent, 'main_image', None)
        if main_image is None or getattr(main_image, '_is_destroyed', False):
            return False
        scene = getattr(main_image, 'scene', None)
        if scene is None:
            return False

        self._overlay_item = GridOverlayItem()
        scene.addItem(self._overlay_item)
        return True

    def _zoom_to_cell(self, cell_index):
        """Frame a cell in the view, with a margin of neighboring context."""
        main_image = getattr(self.parent, 'main_image', None)
        if main_image is None or getattr(main_image, '_is_destroyed', True):
            return
        scene_rect = main_image.sceneRect()
        rects = GridReviewService.cell_rects(
            scene_rect.width(), scene_rect.height(), self._rows, self._cols
        )
        if cell_index is None or not (0 <= cell_index < len(rects)):
            return
        x, y, w, h = rects[cell_index]
        margin_x = w * _CELL_ZOOM_MARGIN
        margin_y = h * _CELL_ZOOM_MARGIN
        main_image.zoomToRect(QRectF(x - margin_x, y - margin_y,
                                     w + (2 * margin_x), h + (2 * margin_y)))

    # ------------------------------------------------------------------ #
    #  Progress display
    # ------------------------------------------------------------------ #
    def _update_status(self):
        """Publish cell/image/run progress to the status bar."""
        if not self.active:
            return
        image = self._current_image()
        if image is None:
            return

        default_rows, default_cols = self._default_dims()
        total_cells = self._rows * self._cols
        order = GridReviewService.serpentine_order(self._rows, self._cols)
        cell_number = order.index(self.current_cell) + 1 if self.current_cell in order else 0

        run_reviewed, run_total = GridReviewService.run_progress(
            self.parent.images, default_rows, default_cols
        )
        run_percent = int(round(100.0 * run_reviewed / run_total)) if run_total else 0

        self.parent.messages['Grid Review'] = self.tr(
            "cell {cell}/{cells} — image {image}/{images} — run {percent}% reviewed"
        ).format(
            cell=cell_number, cells=total_cells,
            image=self.parent.current_image + 1, images=len(self.parent.images),
            percent=run_percent
        )

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #
    def _current_image(self):
        """Return the current image dict, or None when unavailable."""
        images = getattr(self.parent, 'images', None)
        index = getattr(self.parent, 'current_image', None)
        if not images or index is None or not (0 <= index < len(images)):
            return None
        return images[index]

    @staticmethod
    def _reviewed_cells(image):
        """Return the reviewed-cell set for an image (empty when none)."""
        grid = image.get('grid_review') if image else None
        return grid['reviewed'] if grid else set()

    def _sync_button_state(self):
        """Mirror the mode state onto the toolbar button, when it exists."""
        button = getattr(self.parent, 'gridReviewButton', None)
        if button is not None:
            try:
                button.setChecked(self.active)
            except Exception:
                pass
        style = getattr(self.parent, 'ui_style_controller', None)
        if style is not None and hasattr(style, 'update_grid_review_button_style'):
            style.update_grid_review_button_style()
