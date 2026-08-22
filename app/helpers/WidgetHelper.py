"""WidgetHelper - shared widget lifecycle utilities.

Collects the small Qt lifecycle details that are easy to get wrong the same
way in several places.
"""

from PySide6.QtCore import Qt


def retire_widget(widget, layout=None):
    """Remove *widget* from view and queue its destruction.

    ``deleteLater`` only *queues* destruction: until the event loop next runs
    its deferred-delete pass, the widget is still a visible child painted at
    its old geometry. Code that swaps a panel and then does long synchronous
    work - constructing the replacement, loading a model, opening a result set
    - keeps the event loop busy, and ``QApplication.processEvents()`` does not
    flush deferred deletes. The retired panel therefore stays on screen,
    stacked under its replacement (field report: an outgoing algorithm
    parameter panel visible beneath the incoming one).

    Hiding first makes the removal immediate and leaves the destruction
    deferred, which is what callers actually want.

    Args:
        widget: The widget to retire. ``None`` is accepted and ignored so
            callers need no separate guard.
        layout: Optional layout to remove *widget* from first.
    """
    if widget is None:
        return
    if layout is not None:
        layout.removeWidget(widget)
    widget.hide()
    widget.deleteLater()


def hand_off_focus(target, *widgets):
    """Give *target* the keyboard focus if any of *widgets* currently holds it.

    Call this before disabling a control the user just operated. Qt reacts to
    ``setEnabled(False)`` on the focus widget by walking the focus chain
    (``QWidget::focusNextChild``), and the successor it picks is whatever comes
    next in creation order - frequently a control on the far side of the panel.
    Naming the successor keeps focus next to the button the user clicked (field
    report: clicking Connect parked focus on Start Recording at the bottom of
    the streaming control panel).

    ``target`` normally is the counterpart control being enabled in the same
    update - Disconnect for Connect, Stop for Start. If it refuses focus
    (disabled, or ``Qt.NoFocus``), focus is cleared instead so the chain walk
    still does not happen.

    Args:
        target: Widget that should receive focus.
        *widgets: Widgets about to be disabled. ``None`` entries are ignored.
    """
    for widget in widgets:
        if widget is None:
            continue
        window = widget.window()
        # Match Qt's own condition rather than hasFocus(), which is False while
        # the window is inactive even though Qt would still walk the chain.
        if window is None or window.focusWidget() is not widget:
            continue
        if target is not None:
            target.setFocus(Qt.OtherFocusReason)
        if window.focusWidget() is widget:
            widget.clearFocus()
        return
