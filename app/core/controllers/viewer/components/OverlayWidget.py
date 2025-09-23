"""
OverlayWidget - Handles the HUD overlay functionality for the image viewer.

This widget provides a semi-transparent overlay that displays compass/north arrow
and scale bar information over the main image.
"""

import math
from PySide6.QtGui import QImage, QPixmap, QPainter, QFont, QPen, QPalette, QColor
from PySide6.QtCore import Qt, QPointF, QPoint
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

from core.services.LoggerService import LoggerService


class OverlayWidget(QWidget):
    """
    Widget that provides a HUD overlay with compass and scale bar.
    
    The overlay is positioned over the main image and displays:
    - North arrow/compass showing drone orientation
    - Scale bar showing real-world measurements
    """
    
    def __init__(self, main_image_widget, scale_bar_widget, theme, logger=None):
        """
        Initialize the overlay widget.
        
        Args:
            main_image_widget: The QtImageViewer widget that displays the main image
            scale_bar_widget: The ScaleBarWidget to include in the overlay
            theme: Current theme name for loading compass assets
            logger: Optional logger instance for error reporting
        """
        super().__init__(main_image_widget.viewport())
        self.main_image = main_image_widget
        self.scale_bar = scale_bar_widget
        self.theme = theme
        self.logger = logger or LoggerService()
        
        # Track visibility state of individual components
        self._compass_visible = False
        self._scale_bar_visible = False
        self._user_wants_overlay = True
        
        # Setup widget properties
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setObjectName("hud")
        # Ensure stylesheet backgrounds are painted in Qt6
        self.setAttribute(Qt.WA_StyledBackground)
        # Use background-color to ensure style engine paints the background
        self.setStyleSheet("#hud{background-color: rgba(0,0,0,100); border-radius:6px;}")
        
        # Set minimum size to ensure the widget is visible
        self.setMinimumSize(200, 50)
        
        # Create layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(8, 4, 8, 4)
        self.layout.setSpacing(10)
        
        # Create compass label
        self.compass_label = QLabel(self)
        self.compass_label.setFixedSize(50, 50)
        self.layout.addWidget(self.compass_label)
        
        # Add scale bar to overlay
        self.scale_bar.setParent(self)
        self.layout.addWidget(self.scale_bar)
        # Initially hide scale bar until data is available
        self.scale_bar.setVisible(False)
        
        # Store reference to compass label for north icon updates
        self.north_icon = self.compass_label
        # Initially hide compass until direction data is available
        transparent_pixmap = QPixmap(1, 1)
        transparent_pixmap.fill(Qt.transparent)
        self.north_icon.setPixmap(transparent_pixmap)
        
        # Load compass asset
        self.original_north_pix = QPixmap(f":/icons/{self.theme.lower()}/north.png")
        # Ensure we have a valid pixmap
        if self.original_north_pix.isNull():
            # Create a fallback pixmap if the resource is not found
            self.original_north_pix = QPixmap(32, 32)
            self.original_north_pix.fill(Qt.transparent)
        
        # Connect to main image events for positioning
        self.main_image.viewChanged.connect(self._place_overlay)
        self.main_image.zoomChanged.connect(self._place_overlay)
        
        # Initialize visibility state - start hidden since no components are visible yet
        self._check_autohide()
    
    def paintEvent(self, event):
        """
        Paint a semi-transparent rounded rectangle as the overlay background.
        This is more reliable across styles/engines than stylesheet-only.
        """
        # Let the base class/style draw first (if any), then paint our overlay on top
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 100))
        radius = 6
        painter.drawRoundedRect(self.rect(), radius, radius)

    def _check_autohide(self):
        """
        Check if the overlay should be auto-hidden based on component visibility.
        
        Auto-hides the overlay if:
        - User wants to show overlay AND
        - Neither compass nor scale bar is visible
        """
        if self._user_wants_overlay:
            if not self._compass_visible and not self._scale_bar_visible:
                self.hide()
            else:
                # Only show and position if we have at least one visible component
                if not self.isVisible():
                    self.show()
                self._place_overlay()

    def update_visibility(self, show_overlay, direction=None, avg_gsd=None):
        """
        Update the overlay visibility based on available data and user preference.
        
        Args:
            show_overlay (bool): Whether the user wants to show the overlay
            direction (float|None): Drone orientation in degrees
            avg_gsd (float|None): Average ground sample distance
        """
        self._user_wants_overlay = show_overlay
        
        # Update component visibility expectations based on available data
        # (The actual visibility will be set by the individual update methods)
        
        if not show_overlay:
            self.hide()
        else:
            # Let the autohide check determine visibility based on component states
            self._check_autohide()
    
    def rotate_north_icon(self, direction):
        """
        Draws a north-facing arrow icon based on the given drone orientation.

        Args:
            direction (float | None): Yaw angle in degrees. If None, hides the arrow.
        """
        if direction is None:
            # Hide the icon by setting a fully transparent 1x1 pixmap
            transparent = QPixmap(1, 1)
            transparent.fill(Qt.transparent)
            self.north_icon.setPixmap(transparent)
            self._compass_visible = False
            self._check_autohide()
            return

        angle = 360 - direction
        pm = self.original_north_pix
        w, h = pm.width(), pm.height()
        
        # Safety check for empty pixmap
        if w == 0 or h == 0:
            # Create a simple fallback arrow
            transparent = QPixmap(1, 1)
            transparent.fill(Qt.transparent)
            self.north_icon.setPixmap(transparent)
            self._compass_visible = False
            self._check_autohide()
            return

        # Find the true tip: first non-transparent pixel from the top, center column
        img = pm.toImage().convertToFormat(QImage.Format_ARGB32)
        cx = w // 2
        for y in range(h):
            if QColor(img.pixel(cx, y)).alpha() > 0:
                tip_y = y
                break
        else:
            tip_y = 0  # fallback if arrow is fully transparent

        tip_offset_px = h / 2 - tip_y  # distance from center to true tip

        # final canvas size
        final_size = 50
        margin = 12
        spacing = 8  # spacing between arrow tip and label in final rendered px

        # scale so the arrow fits inside the canvas minus margin
        diag = math.hypot(w, h)
        scale = (final_size - 2 * margin) / diag

        canvas = QPixmap(final_size, final_size)
        canvas.fill(Qt.transparent)

        p = QPainter(canvas)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        # --- draw arrow ---
        p.save()
        p.translate(final_size / 2, final_size / 2)
        p.rotate(angle)
        p.scale(scale, scale)
        p.drawPixmap(round(-w / 2), round(-h / 2), pm)
        p.restore()

        # --- draw 'N' label a fixed number of px past the visual tip ---
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        p.setFont(font)
        fm = p.fontMetrics()
        text = "N"
        tw = fm.horizontalAdvance(text)

        # scaled distance from center to arrow tip, plus spacing beyond tip
        tip_offset = tip_offset_px * scale + spacing

        p.save()
        p.translate(final_size / 2, final_size / 2)
        p.rotate(angle)
        p.translate(0, -tip_offset)  # move up to just past tip
        p.rotate(-angle)             # make text upright again

        default_text_color = self.palette().color(QPalette.Text)
        p.setPen(QPen(default_text_color))

        text_y = (fm.ascent() - fm.height() / 2)
        p.drawText(QPointF(-tw / 2, text_y), text)
        p.restore()

        p.end()
        self.north_icon.setPixmap(canvas)
        self._compass_visible = True
        self._check_autohide()
    
    def _place_overlay(self):
        """Anchor HUD to bottom‑right corner *of the image*, not viewport."""
        # Check if main_image is still valid before accessing it
        if not hasattr(self.main_image, '_is_destroyed') or self.main_image._is_destroyed:
            return

        # Check if the image is properly loaded and scene is set up
        if not self.main_image.hasImage() or self.main_image.sceneRect().isEmpty():
            return

        self.adjustSize()  # Make sure widget/layout is up to date
        self.updateGeometry()
        vp = self.main_image.viewport()
        margin = 12

        # Get scene and viewport dimensions
        scene_rect = self.main_image.sceneRect()
        br_scene = scene_rect.bottomRight()
        br_view = self.main_image.mapFromScene(br_scene)

        hud_w, hud_h = self.width(), self.height()
        vp_w, vp_h = vp.width(), vp.height()

        # Calculate target position (anchored to image bottom-right)
        x = br_view.x() - hud_w - margin
        y = br_view.y() - hud_h - margin

        # Clamp into viewport
        x = max(margin, min(x, vp_w - hud_w - margin))
        y = max(margin, min(y, vp_h - hud_h - margin))

        # Fallback if overlay is bigger than viewport
        if hud_w + 2 * margin > vp_w or hud_h + 2 * margin > vp_h:
            x, y = margin, margin
            
        self.move(x, y)
        self.raise_()
        # Note: Visibility is controlled by autohide logic, not placed here
    
    def update_scale_bar(self, zoom: float, messages=None, distance_unit='m'):
        """
        Update the scale bar based on zoom level and GSD data.
        
        Args:
            zoom: Current zoom level
            messages: StatusDict containing GSD information
            distance_unit: Unit for distance display ('m' or 'ft')
        """
        if not self.scale_bar or not messages:
            self._scale_bar_visible = False
            self._check_autohide()
            return
            
        try:
            if not self.main_image or not self.main_image.hasImage():
                self.scale_bar.setVisible(False)
                self._scale_bar_visible = False
                self._check_autohide()
                return

            gsd_text = messages.get("Estimated Average GSD")  # e.g. '3.2cm/px'
            if not gsd_text:
                self.scale_bar.setVisible(False)
                self._scale_bar_visible = False
                self._check_autohide()
                return

            # -------- compute label --------
            gsd_cm = float(gsd_text.replace("cm/px", "").strip())   # cm / px
            zoomed_gsd = gsd_cm / zoom                                  # cm / px at current zoom
            bar_px = self.scale_bar._bar_px                          # fixed 120 px
            real_cm = bar_px * zoomed_gsd                            # cm represented by bar

            if distance_unit == 'ft':
                real_in = real_cm / 2.54
                if real_in >= 12:
                    label = f"{real_in / 12:.2f} ft"
                else:
                    label = f"{real_in:.1f} in"
            else:
                if real_cm >= 100:
                    label = f"{real_cm / 100:.1f} m"
                else:
                    label = f"{real_cm:.0f} cm"

            # -------- show --------
            self.scale_bar.setLabel(label)
            self.scale_bar.setVisible(True)
            self._scale_bar_visible = True
            self._check_autohide()

        except Exception as e:
            self.logger.error(f"scale‑bar update failed: {e}")
            self._scale_bar_visible = False
            self._check_autohide()
    
    def cleanup(self):
        """Clean up the overlay widget."""
        self.hide()
        if self.scale_bar:
            self.scale_bar.setParent(None)
