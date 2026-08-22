"""Tests for helpers.WidgetHelper."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QLabel, QPushButton, QVBoxLayout,
                               QWidget)

from helpers.WidgetHelper import hand_off_focus, retire_widget


@pytest.fixture(scope='session')
def app():
    return QApplication.instance() or QApplication([])


def test_retire_hides_immediately_and_leaves_layout(app, qtbot):
    """The point of the helper: hidden NOW, destroyed later.

    deleteLater alone leaves the widget visible until the event loop runs its
    deferred-delete pass, so a swap followed by long synchronous work paints
    the retired panel under its replacement.
    """
    host = QWidget()
    qtbot.addWidget(host)
    layout = QVBoxLayout(host)
    outgoing = QLabel("outgoing", host)
    layout.addWidget(outgoing)
    host.show()
    qtbot.waitExposed(host)
    assert not outgoing.isHidden()

    retire_widget(outgoing, layout)

    # No event-loop turn has happened yet - exactly the field condition.
    assert outgoing.isHidden()
    assert layout.indexOf(outgoing) == -1


def test_retire_without_layout_still_hides(app, qtbot):
    host = QWidget()
    qtbot.addWidget(host)
    widget = QLabel("floating", host)
    host.show()
    qtbot.waitExposed(host)

    retire_widget(widget)

    assert widget.isHidden()


def test_retire_none_is_a_noop(app):
    retire_widget(None)          # no guard needed at call sites
    retire_widget(None, None)


def _button_row(qtbot):
    """Host with three buttons: the one clicked, its successor, an unrelated one."""
    host = QWidget()
    qtbot.addWidget(host)
    layout = QVBoxLayout(host)
    clicked = QPushButton("Connect", host)
    successor = QPushButton("Disconnect", host)
    unrelated = QPushButton("Start Recording", host)
    for button in (clicked, successor, unrelated):
        layout.addWidget(button)
    host.show()
    qtbot.waitExposed(host)
    return host, clicked, successor, unrelated


def test_hand_off_focus_names_the_successor(app, qtbot):
    """Without this, Qt picks the successor: the next widget created."""
    host, clicked, successor, unrelated = _button_row(qtbot)
    clicked.setFocus(Qt.OtherFocusReason)

    hand_off_focus(successor, clicked)
    clicked.setEnabled(False)

    assert host.focusWidget() is successor
    assert host.focusWidget() is not unrelated


def test_hand_off_focus_leaves_focus_elsewhere_alone(app, qtbot):
    """Only a widget that actually holds focus triggers the handoff."""
    host, clicked, successor, unrelated = _button_row(qtbot)
    unrelated.setFocus(Qt.OtherFocusReason)

    hand_off_focus(successor, clicked)

    assert host.focusWidget() is unrelated


def test_hand_off_focus_clears_focus_when_the_target_refuses_it(app, qtbot):
    """A disabled target cannot take focus, so clear it rather than leave the chain walk armed."""
    host, clicked, successor, _unrelated = _button_row(qtbot)
    successor.setEnabled(False)
    clicked.setFocus(Qt.OtherFocusReason)

    hand_off_focus(successor, clicked)

    assert host.focusWidget() is None


def test_hand_off_focus_skips_none_entries(app, qtbot):
    """Call sites list optional controls without guarding each one."""
    host, clicked, successor, _unrelated = _button_row(qtbot)
    clicked.setFocus(Qt.OtherFocusReason)

    hand_off_focus(successor, None, clicked, None)

    assert host.focusWidget() is successor
