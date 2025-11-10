"""
Custom Labeled Slider Widget

A horizontal slider with tick marks and value display above the slider.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QSlider, QStyle, QStyleOptionSlider
from PySide6.QtGui import QPainter, QPen, QPalette, QFont, QFontMetrics, QColor


class LabeledSlider(QWidget):
    """A slider widget with tick marks and value display above the slider.

    Custom QWidget that provides a horizontal slider with visual tick marks
    and a value label displayed above the slider handle.

    Attributes:
        valueChanged: Signal emitted when the slider value changes. Emits
            the new integer value.
    """

    # Signal emitted when the value changes
    valueChanged = Signal(int)

    def __init__(self, parent=None, minimum=1, maximum=20, value=4):
        """Initialize the labeled slider.

        Args:
            parent: Parent widget.
            minimum: Minimum slider value. Defaults to 1.
            maximum: Maximum slider value. Defaults to 20.
            value: Initial slider value. Defaults to 4.
        """
        super().__init__(parent)

        self._minimum = minimum
        self._maximum = maximum
        self._value = value

        # Create internal slider
        self._slider = QSlider(Qt.Horizontal, self)
        self._slider.setMinimum(minimum)
        self._slider.setMaximum(maximum)
        self._slider.setValue(value)
        self._slider.valueChanged.connect(self._on_slider_value_changed)

        # Widget dimensions
        self._tick_height = 8
        self._label_height = 25
        self._slider_height = 20

        # Set minimum size
        self.setMinimumHeight(self._label_height + self._slider_height + 10)
        self.setMinimumWidth(300)

    def _on_slider_value_changed(self, value):
        """Handle internal slider value change.

        Args:
            value: New slider value.
        """
        self._value = value
        self.update()  # Trigger repaint to update value display
        self.valueChanged.emit(value)

    def setMinimum(self, value):
        """Set minimum value.

        Args:
            value: New minimum value.
        """
        self._minimum = value
        self._slider.setMinimum(value)
        self.update()

    def setMaximum(self, value):
        """Set maximum value.

        Args:
            value: New maximum value.
        """
        self._maximum = value
        self._slider.setMaximum(value)
        self.update()

    def setValue(self, value):
        """Set current value.

        Args:
            value: New slider value.
        """
        self._value = value
        self._slider.setValue(value)
        self.update()

    def value(self):
        """Get current value.

        Returns:
            Current slider value.
        """
        return self._value

    def minimum(self):
        """Get minimum value.

        Returns:
            Minimum slider value.
        """
        return self._minimum

    def maximum(self):
        """Get maximum value.

        Returns:
            Maximum slider value.
        """
        return self._maximum

    def _value_to_position(self, value):
        """Convert value to horizontal position."""
        if self._maximum == self._minimum:
            return 0

        slider_width = self.width() - 40  # Margin on each side
        ratio = (value - self._minimum) / (self._maximum - self._minimum)
        return 20 + ratio * slider_width  # 20px left margin

    def resizeEvent(self, event):
        """Handle widget resize."""
        super().resizeEvent(event)
        # Position slider at bottom of widget
        # Use same margins as _value_to_position (20px on each side)
        slider_y = self._label_height + 5
        slider_x = 20  # Left margin to match _value_to_position
        slider_width = self.width() - 40  # Total width minus margins
        self._slider.setGeometry(slider_x, slider_y, slider_width, self._slider_height)
        self.update()  # Trigger repaint when resized

    def paintEvent(self, event):
        """Paint tick marks and value display."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get theme colors
        palette = self.palette()
        text_color = palette.color(QPalette.WindowText)
        tick_color = palette.color(QPalette.Mid)

        # Use the actual slider groove/handle rects from style for perfect alignment
        opt = QStyleOptionSlider()
        self._slider.initStyleOption(opt)
        groove_rect = self._slider.style().subControlRect(
            QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self._slider
        )
        # groove_width = max(1, _groove_right - _groove_left)  # Reserved for future use

        # Position ticks directly above the groove
        tick_bottom_y = groove_rect.top() + self._slider.y() - 2
        tick_top_y = tick_bottom_y - self._tick_height

        # Prepare common font metrics for 11pt labels
        base_font = QFont()
        base_font.setPointSize(11)
        base_fm = QFontMetrics(base_font)
        # Baseline for labels: just above tick marks, with small gap
        label_baseline_y = max(base_fm.ascent() + 2, tick_top_y - 2)

        # Draw tick marks for each value
        for val in range(self._minimum, self._maximum + 1):
            # Compute tick x based on the styled handle center for this value
            opt.sliderPosition = val
            handle_rect = self._slider.style().subControlRect(
                QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self._slider
            )
            tick_pos_i = handle_rect.center().x() + self._slider.x()

            # Draw tick mark
            painter.setPen(QPen(tick_color, 1))
            painter.drawLine(tick_pos_i, tick_top_y, tick_pos_i, tick_bottom_y)

            # Draw value label (only show every few values to avoid clutter)
            # Show all values if range is small (<= 20), otherwise show every 5th
            show_label = (self._maximum - self._minimum <= 20) or (val % 5 == 0) or (val == self._minimum) or (val == self._maximum)

            if show_label:
                # Use bold font and highlight color for the current value
                if val == self._value:
                    font = QFont(base_font)
                    font.setBold(True)
                    fm = QFontMetrics(font)
                    # Use highlight color for selected value
                    highlight_color = QColor(138, 180, 247)
                    label_color = highlight_color
                else:
                    font = base_font
                    fm = base_fm
                    label_color = text_color
                painter.setFont(font)

                label_text = str(val)
                label_width = fm.horizontalAdvance(label_text)
                label_x = tick_pos_i - label_width // 2

                painter.setPen(QPen(label_color))
                painter.drawText(int(label_x), int(label_baseline_y), label_text)


class TextLabeledSlider(QWidget):
    """
    A slider widget with custom text labels and associated numeric values.

    UI renders ONLY the text labels; numeric values are kept for logic,
    not displayed.

    The slider snaps to these predefined positions.
    """

    # Signal emitted when the value changes (emits the index of the selected preset)
    valueChanged = Signal(int)

    def __init__(self, parent=None, presets=None):
        """
        Initialize the TextLabeledSlider.

        Args:
            parent: Parent widget
            presets: Either a list of strings (text-only labels), or a list of
                     tuples (text_label, numeric_value). If None, a default list
                     is used.
        """
        super().__init__(parent)

        # Default presets matching the image
        if presets is None:
            presets = ["Very Conservative", "Conservative", "Moderate", "Aggressive", "Very Aggressive"]

        # Normalize presets to a list of (text, optional_numeric) tuples
        if presets and isinstance(presets[0], str):
            self._presets = [(label, None) for label in presets]  # type: ignore[index]
        else:
            self._presets = presets
        self._current_index = 2  # Default to "Moderate" (middle preset)

        # Check if any labels are multi-line (contain \n)
        has_multiline = any('\n' in (preset[0] if isinstance(preset, tuple) else preset)
                            for preset in self._presets)

        # Create internal slider
        self._slider = QSlider(Qt.Horizontal, self)
        self._slider.setMinimum(0)
        self._slider.setMaximum(len(self._presets) - 1)
        self._slider.setValue(self._current_index)
        self._slider.valueChanged.connect(self._on_slider_value_changed)

        # Widget dimensions
        self._tick_height = 8
        # Use smaller height for single-line labels, larger for multi-line
        self._label_height = 50 if has_multiline else 25  # Space for text labels
        self._slider_height = 20

        # Set minimum size
        self.setMinimumHeight(self._label_height + self._slider_height + 10)
        self.setMinimumWidth(400)

    def _on_slider_value_changed(self, value):
        """Handle internal slider value change."""
        self._current_index = value
        self.update()  # Trigger repaint to update display
        self.valueChanged.emit(value)

    def setValue(self, index):
        """
        Set current value by preset index.

        Args:
            index: Index of the preset (0-based)
        """
        if 0 <= index < len(self._presets):
            self._current_index = index
            self._slider.setValue(index)
            self.update()

    def value(self):
        """
        Get current preset index.

        Returns:
            int: Index of currently selected preset
        """
        return self._current_index

    def getCurrentPreset(self):
        """
        Get the current preset data.

        Returns:
            tuple: (text_label, numeric_value | None) of current preset
        """
        return self._presets[self._current_index]

    def getNumericValue(self):
        """
        Get the numeric value of the current preset.

        Returns:
            Optional[int]: Numeric value of current preset (if provided), else None
        """
        return self._presets[self._current_index][1]

    def setTextLabels(self, labels):
        """
        Replace labels with a list of strings. Numeric values will be cleared.
        """
        if not labels:
            return
        self._presets = [(label, None) for label in labels]
        self._slider.setMaximum(len(self._presets) - 1)
        if self._current_index >= len(self._presets):
            self._current_index = len(self._presets) - 1
        self._slider.setValue(self._current_index)
        self.update()

    def setPresets(self, presets):
        """
        Set custom presets.

        Args:
            presets: List of tuples (text_label, numeric_value)
        """
        self._presets = presets
        self._slider.setMaximum(len(self._presets) - 1)
        # Clamp current index to valid range
        if self._current_index >= len(self._presets):
            self._current_index = len(self._presets) - 1
        self._slider.setValue(self._current_index)
        self.update()

    def resizeEvent(self, event):
        """Handle widget resize."""
        super().resizeEvent(event)
        # Position slider at bottom of widget
        slider_y = self._label_height + 5
        slider_x = 20  # Left margin
        slider_width = self.width() - 40  # Total width minus margins
        self._slider.setGeometry(slider_x, slider_y, slider_width, self._slider_height)
        self.update()  # Trigger repaint when resized

    def paintEvent(self, event):
        """Paint tick marks, text labels, and numeric values."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get theme colors
        palette = self.palette()
        text_color = palette.color(QPalette.WindowText)
        tick_color = palette.color(QPalette.Mid)

        # Use the actual slider groove/handle rects from style for perfect alignment
        opt = QStyleOptionSlider()
        self._slider.initStyleOption(opt)
        groove_rect = self._slider.style().subControlRect(
            QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self._slider
        )

        # Position ticks directly above the groove
        tick_bottom_y = groove_rect.top() + self._slider.y() - 2
        tick_top_y = tick_bottom_y - self._tick_height

        # Prepare fonts
        text_font = QFont()
        text_font.setPointSize(12)
        text_fm = QFontMetrics(text_font)

        # Draw tick marks and labels for each preset
        for idx, (text_label, numeric_value) in enumerate(self._presets):
            # Compute tick x based on the styled handle center for this index
            opt.sliderPosition = idx
            handle_rect = self._slider.style().subControlRect(
                QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self._slider
            )
            tick_pos_x = handle_rect.center().x() + self._slider.x()

            # Draw tick mark
            painter.setPen(QPen(tick_color, 1))
            painter.drawLine(int(tick_pos_x), int(tick_top_y), int(tick_pos_x), int(tick_bottom_y))

            # Determine if this is the current selection
            is_current = (idx == self._current_index)

            # Draw text label
            if is_current:
                font = QFont(text_font)
                font.setBold(True)
                fm = QFontMetrics(font)
                label_color = QColor(138, 180, 247)
            else:
                font = text_font
                fm = text_fm
                label_color = text_color

            painter.setFont(font)
            painter.setPen(QPen(label_color))

            # Handle multi-line text labels (split by \n)
            lines = text_label.split('\n')
            line_height = fm.height()
            total_height = len(lines) * line_height

            # Calculate the starting Y position so the text block is centered above the tick
            # Position the text to end just above the tick marks with some padding
            text_bottom_y = tick_top_y - 6  # 6px padding above tick
            text_start_y = text_bottom_y - total_height

            # Find the widest line to center the entire block
            max_line_width = max(fm.horizontalAdvance(line) for line in lines)

            # Calculate the center X position for the text block
            block_center_x = tick_pos_x - max_line_width // 2
            # Clamp the block position so it doesn't go outside widget bounds
            if block_center_x < 0:
                block_center_x = 0
            elif block_center_x + max_line_width > self.width():
                block_center_x = self.width() - max_line_width

            # Draw each line centered within the block
            for line_idx, line in enumerate(lines):
                line_width = fm.horizontalAdvance(line)
                # Center this line within the text block
                line_x = block_center_x + (max_line_width - line_width) // 2

                # Calculate y position for this line (baseline position)
                line_y = int(text_start_y + (line_idx + 1) * line_height)
                painter.drawText(int(line_x), line_y, line)

            # Numeric values intentionally not rendered
