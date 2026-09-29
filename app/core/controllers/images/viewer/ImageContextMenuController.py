"""
ImageContextMenuController - Right-click context menu for the main image viewer.

Fired by QtImageViewer.contextMenuRequested (a right click without a drag, in
both control schemes). Hosts the cursor GPS actions and quick zoom controls.
"""

from PySide6.QtWidgets import QMenu

from core.services.LoggerService import LoggerService
from helpers.TranslationMixin import TranslationMixin


class ImageContextMenuController(TranslationMixin):
    """Builds and shows the image viewer's right-click menu."""

    def __init__(self, parent_viewer):
        """
        Args:
            parent_viewer: The main Viewer instance.
        """
        self.parent = parent_viewer
        self.logger = LoggerService()

    def show_menu(self, scene_pos, global_pos):
        """Show the context menu for a right click on the main image.

        Args:
            scene_pos (QPointF): Click position in image (scene) coordinates.
            global_pos (QPoint): Screen position to open the menu at.
        """
        try:
            x, y = scene_pos.x(), scene_pos.y()
            in_image = self._position_in_image(scene_pos)

            menu = QMenu(self.parent)
            copy_action = menu.addAction(self.tr("Copy GPS coordinates"))
            show_action = menu.addAction(self.tr("Show GPS coordinates..."))
            maps_action = menu.addAction(self.tr("Open location in Google Maps"))
            copy_action.setEnabled(in_image)
            show_action.setEnabled(in_image)
            maps_action.setEnabled(in_image)
            menu.addSeparator()
            fit_action = menu.addAction(self.tr("Zoom to fit"))
            zoom_in_action = menu.addAction(self.tr("Zoom in"))
            zoom_out_action = menu.addAction(self.tr("Zoom out"))

            chosen = menu.exec(global_pos)
            if chosen is None:
                return

            coordinate_controller = self.parent.coordinate_controller
            main_image = self.parent.main_image
            if chosen is copy_action:
                coordinate_controller.copy_cursor_coordinates(x, y)
            elif chosen is show_action:
                coordinate_controller.show_cursor_coordinates(x, y, anchor_point=global_pos)
            elif chosen is maps_action:
                resolved = coordinate_controller.resolve_cursor_coords(x, y)
                if resolved is None:
                    self.parent.status_controller.show_toast(
                        self.tr("Coordinates unavailable"), 3000, color="#F44336")
                else:
                    coordinate_controller.open_in_maps((resolved[0], resolved[1]))
            elif chosen is fit_action:
                main_image.resetZoom()
            elif chosen is zoom_in_action:
                main_image._zoomInAtPos(scene_pos)
            elif chosen is zoom_out_action:
                main_image._zoomOutAtPos(scene_pos)
        except Exception as e:
            self.logger.error(f"Error showing image context menu: {e}")

    def _position_in_image(self, scene_pos):
        """True when the click landed on the image itself."""
        main_image = getattr(self.parent, 'main_image', None)
        if main_image is None:
            return False
        scene_rect = main_image.sceneRect()
        return (not scene_rect.isEmpty()) and scene_rect.contains(scene_pos)
