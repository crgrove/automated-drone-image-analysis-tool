"""
Dialog for selecting from recently used colors/ranges.

Displays the last 10 colors with their parameters for quick reuse.
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QScrollArea, QWidget, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from typing import List, Dict, Any, Optional


class RecentColorWidget(QWidget):
    """Widget representing a single recent color entry."""

    clicked = Signal(dict)  # Emits the color_data when clicked

    def __init__(self, color_data: Dict[str, Any], mode: str, parent=None):
        super().__init__(parent)
        self.color_data = color_data
        self.mode = mode
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(10)

        # Color swatch
        selected_color = self.color_data.get('selected_color', (255, 0, 0))
        r, g, b = selected_color

        swatch = QLabel(self)
        swatch.setFixedSize(40, 30)
        swatch.setStyleSheet(f"""
            QLabel {{
                background-color: rgb({r}, {g}, {b});
                border: 1px solid #555;
                border-radius: 3px;
            }}
        """)
        layout.addWidget(swatch)

        # Color info label
        info_text = self._get_info_text()
        info_label = QLabel(info_text, self)
        info_label.setWordWrap(True)
        layout.addWidget(info_label, 1)

        # Make widget clickable
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
            QWidget:hover {
                background-color: rgba(255, 255, 255, 20);
            }
        """)
        self.setCursor(Qt.PointingHandCursor)

    def _get_info_text(self) -> str:
        """Generate description text based on mode and data."""
        selected_color = self.color_data.get('selected_color', (255, 0, 0))
        r, g, b = selected_color

        text = f"<b>RGB:</b> ({r}, {g}, {b})"

        if self.mode == 'HSV':
            hsv_ranges = self.color_data.get('hsv_ranges', {})
            if hsv_ranges:
                # Get center HSV values (all in 0-1 fractional format)
                h_center = hsv_ranges.get('h', 0)
                s_center = hsv_ranges.get('s', 0)
                v_center = hsv_ranges.get('v', 0)

                # Get range values (all in 0-1 fractional format)
                h_minus = hsv_ranges.get('h_minus', 0)
                h_plus = hsv_ranges.get('h_plus', 0)
                s_minus = hsv_ranges.get('s_minus', 0)
                s_plus = hsv_ranges.get('s_plus', 0)
                v_minus = hsv_ranges.get('v_minus', 0)
                v_plus = hsv_ranges.get('v_plus', 0)

                # Calculate min/max to match HSVColorRowWidget display format:
                # H (°): degrees 0-359
                # S (%): percentage 0-100
                # V (%): percentage 0-100
                h_min_deg = max(0, int((h_center - h_minus) * 360))
                h_max_deg = min(359, int((h_center + h_plus) * 360))
                s_min_pct = max(0, int((s_center - s_minus) * 100))
                s_max_pct = min(100, int((s_center + s_plus) * 100))
                v_min_pct = max(0, int((v_center - v_minus) * 100))
                v_max_pct = min(100, int((v_center + v_plus) * 100))

                text += f"<br><b>H (°):</b> {h_min_deg}-{h_max_deg}"
                text += f" <b>S (%):</b> {s_min_pct}-{s_max_pct}"
                text += f" <b>V (%):</b> {v_min_pct}-{v_max_pct}"

        elif self.mode == 'RGB':
            color_range = self.color_data.get('color_range')
            if color_range and len(color_range) == 2:
                min_rgb, max_rgb = color_range[0], color_range[1]
                if isinstance(min_rgb, (list, tuple)) and isinstance(max_rgb, (list, tuple)):
                    text += f"<br><b>R:</b> {min_rgb[0]}-{max_rgb[0]}"
                    text += f" <b>G:</b> {min_rgb[1]}-{max_rgb[1]}"
                    text += f" <b>B:</b> {min_rgb[2]}-{max_rgb[2]}"

        elif self.mode == 'MATCHED_FILTER':
            threshold = self.color_data.get('match_filter_threshold', 0.3)
            text += f"<br><b>Threshold:</b> {threshold:.2f}"

        return text

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.color_data)
        super().mousePressEvent(event)


class RecentColorsDialog(QDialog):
    """Dialog for selecting from recently used colors."""

    def __init__(self, recent_colors: List[Dict[str, Any]], mode: str, parent=None):
        """
        Initialize the recent colors dialog.

        Args:
            recent_colors: List of color data dicts
            mode: 'HSV', 'RGB', or 'MATCHED_FILTER'
            parent: Parent widget
        """
        super().__init__(parent)
        self.recent_colors = recent_colors
        self.mode = mode
        self.selected_color_data: Optional[Dict[str, Any]] = None

        self.setWindowTitle("Recent Colors")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Select a recently used color:", self)
        header.setStyleSheet("font-weight: bold; font-size: 12px; padding: 5px;")
        layout.addWidget(header)

        # Scroll area for color list
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(2)

        if not self.recent_colors:
            # Empty state
            empty_label = QLabel("No recent colors found", container)
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #888; font-style: italic; padding: 20px;")
            container_layout.addWidget(empty_label)
        else:
            # Add color widgets
            for color_data in self.recent_colors:
                color_widget = RecentColorWidget(color_data, self.mode, container)
                color_widget.clicked.connect(self._on_color_selected)
                container_layout.addWidget(color_widget)

                # Add separator
                separator = QFrame(container)
                separator.setFrameShape(QFrame.HLine)
                separator.setFrameShadow(QFrame.Sunken)
                separator.setStyleSheet("color: #444;")
                container_layout.addWidget(separator)

        container_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def _on_color_selected(self, color_data: Dict[str, Any]):
        """Handle color selection."""
        self.selected_color_data = color_data
        self.accept()

    def get_selected_color_data(self) -> Optional[Dict[str, Any]]:
        """Get the selected color data, or None if dialog was cancelled."""
        return self.selected_color_data
