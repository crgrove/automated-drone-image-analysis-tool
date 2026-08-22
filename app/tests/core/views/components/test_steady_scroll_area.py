"""Tests for core.views.components.SteadyScrollArea."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (QApplication, QPushButton, QScrollArea, QVBoxLayout,
                               QWidget)

from core.views.components.SteadyScrollArea import SteadyScrollArea


@pytest.fixture(scope='session')
def app():
    return QApplication.instance() or QApplication([])


def _tall_panel(scroll, qtbot):
    """Fill *scroll* with a panel taller than its viewport.

    Shape of the real control panel: a button the user operates near the top,
    a lot of controls in between, and another focusable button at the bottom.

    Returns:
        (top_button, bottom_button)
    """
    panel = QWidget()
    layout = QVBoxLayout(panel)
    top = QPushButton("Connect", panel)
    filler = QWidget(panel)
    filler.setMinimumHeight(1500)
    bottom = QPushButton("Start Recording", panel)
    layout.addWidget(top)
    layout.addWidget(filler)
    layout.addWidget(bottom)

    scroll.setWidgetResizable(True)
    scroll.setWidget(panel)
    qtbot.addWidget(scroll)
    scroll.resize(300, 250)
    scroll.show()
    qtbot.waitExposed(scroll)
    assert scroll.verticalScrollBar().maximum() > 0, "panel must overflow for the test to mean anything"
    return top, bottom


def test_disabling_the_focused_widget_does_not_move_the_panel(app, qtbot):
    """The reported bug: clicking Connect scrolled the control panel to the bottom.

    The click disables Connect, Qt hands focus to the next widget in creation
    order, and a plain QScrollArea scrolls that widget into view.
    """
    scroll = SteadyScrollArea()
    top, bottom = _tall_panel(scroll, qtbot)
    top.setFocus(Qt.OtherFocusReason)

    top.setEnabled(False)

    assert scroll.verticalScrollBar().value() == 0
    # Focus still moved - only the scrolling is suppressed.
    assert scroll.window().focusWidget() is bottom


def test_panel_holds_a_mid_scroll_position_through_a_handoff(app, qtbot):
    """The position is restored, not just clamped to the top."""
    scroll = SteadyScrollArea()
    top, _bottom = _tall_panel(scroll, qtbot)
    middle = scroll.verticalScrollBar().maximum() // 2
    scroll.verticalScrollBar().setValue(middle)
    top.setFocus(Qt.OtherFocusReason)

    top.setEnabled(False)

    assert scroll.verticalScrollBar().value() == middle


def test_tab_navigation_still_scrolls_to_follow_focus(app, qtbot):
    """Suppression is limited to handoffs; Tab must still reveal its target."""
    scroll = SteadyScrollArea()
    top, bottom = _tall_panel(scroll, qtbot)
    top.setFocus(Qt.OtherFocusReason)

    QTest.keyClick(top, Qt.Key_Tab)

    assert scroll.window().focusWidget() is bottom
    assert scroll.verticalScrollBar().value() > 0


def test_plain_scroll_area_chases_the_handoff(app, qtbot):
    """The Qt behaviour this class exists to correct.

    Kept as a test so that swapping SteadyScrollArea back for a QScrollArea, or
    a change in Qt's own behaviour, is visible rather than silent.
    """
    scroll = QScrollArea()
    top, _bottom = _tall_panel(scroll, qtbot)
    top.setFocus(Qt.OtherFocusReason)

    top.setEnabled(False)

    assert scroll.verticalScrollBar().value() > 0
