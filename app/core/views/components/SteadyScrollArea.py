"""
Steady Scroll Area

A QScrollArea for tall control panels: it keeps its position when a control
hands off focus because it was disabled, instead of jumping to the successor.
"""

from PySide6.QtWidgets import QScrollArea


class SteadyScrollArea(QScrollArea):
    """Scroll area that does not chase focus handed off by a disabled widget.

    ``QScrollArea::focusNextPrevChild`` scrolls the newly focused widget into
    view, which is what makes Tab navigation work inside a scrolled panel. Qt
    routes one other thing through that same override: disabling the focus
    widget makes it walk the focus chain, so a button that disables itself
    hands focus to whatever control comes next in creation order. In a tall
    panel that control can be far below, and the panel jumps to it (field
    report: Connect/Disconnect on the streaming detector snapped the control
    panel down to the Recording group every time).

    The two cases are told apart by where the focus came from: Qt marks the
    widget disabled *before* walking the chain, so a walk that starts from a
    widget which is no longer enabled is a handoff, not navigation. Tab still
    scrolls to follow focus.
    """

    def focusNextPrevChild(self, next):
        previous = self.window().focusWidget() if self.window() else None
        vertical = self.verticalScrollBar().value()
        horizontal = self.horizontalScrollBar().value()

        moved = super().focusNextPrevChild(next)

        if moved and previous is not None and not previous.isEnabled():
            self.verticalScrollBar().setValue(vertical)
            self.horizontalScrollBar().setValue(horizontal)
        return moved
