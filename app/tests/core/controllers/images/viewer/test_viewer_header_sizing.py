"""Tests for the viewer header layout (Viewer._tighten_header).

The header is a simple two-part row: a left group (file name, index label,
Show Overlay) and the right-justified toolbar buttons, separated by a single
expanding spacer. The only element that yields under width pressure is the
file-name label, so when the two groups would overlap the file name is what
gets cut off — every other item keeps its natural width.

The tests drive the *real* generated UI so the assertions track the actual
header the user sees.
"""

from PySide6.QtWidgets import QMainWindow, QSizePolicy

from core.controllers.images.viewer.Viewer import Viewer
from core.views.images.viewer.ui.Viewer_ui import Ui_Viewer

# Mirrors the header_height set in Viewer._setup_splitter_layout.
HEADER_HEIGHT = 46


def _build_header(qtbot):
    """Build the real viewer UI and constrain the header like the live app."""
    win = QMainWindow()
    qtbot.addWidget(win)
    ui = Ui_Viewer()
    ui.setupUi(win)
    ui.mainHeaderWidget.setMinimumHeight(HEADER_HEIGHT)
    ui.mainHeaderWidget.setMaximumHeight(HEADER_HEIGHT)
    return win, ui


def test_tighten_header_reduces_minimum_width(qtbot):
    """The header's minimum width must drop after tightening the spacing."""
    win, ui = _build_header(qtbot)
    before = ui.mainHeaderWidget.layout().minimumSize().width()

    Viewer._tighten_header(ui.horizontalLayout_5)

    after = ui.mainHeaderWidget.layout().minimumSize().width()
    assert after < before


def test_tighten_header_frees_vertical_space(qtbot):
    """Top/bottom margins are removed so the file-name text isn't clipped."""
    win, ui = _build_header(qtbot)

    Viewer._tighten_header(ui.horizontalLayout_5)

    margins = ui.horizontalLayout_5.contentsMargins()
    assert margins.top() == 0
    assert margins.bottom() == 0

    # With margins removed, the full header height is available, which must
    # exceed the label's required height at its 16pt font.
    ui.fileNameLabel.setText("DJI 20250509162825 0046 V map-plan-681e72dc08bf0d0a")
    assert ui.fileNameLabel.sizeHint().height() <= HEADER_HEIGHT


def test_tighten_header_sets_spacing(qtbot):
    """The inter-widget spacing is tightened."""
    win, ui = _build_header(qtbot)

    Viewer._tighten_header(ui.horizontalLayout_5)

    assert ui.horizontalLayout_5.spacing() == 2


def test_only_file_name_is_shrinkable(qtbot):
    """The file name is the sole flexible element; the index stays rigid.

    The file-name label pins a tiny (10px) minimum width in the .ui, so it can
    be squeezed and clipped. The index label is left untouched — no artificial
    minimum, no shrinkable policy — so it always renders its full text.
    """
    win, ui = _build_header(qtbot)

    Viewer._tighten_header(ui.horizontalLayout_5)

    # File name yields (small minimum -> clips).
    assert ui.fileNameLabel.minimumWidth() == 10
    # Index label is not made artificially shrinkable.
    assert ui.indexLabel.minimumWidth() == 0
    assert ui.indexLabel.sizePolicy().horizontalPolicy() != QSizePolicy.Policy.Maximum


def test_tighten_header_leaves_fonts_untouched(qtbot):
    """The readable .ui fonts are preserved (the header is tall enough now)."""
    win, ui = _build_header(qtbot)
    name_pt = ui.fileNameLabel.font().pointSize()
    index_pt = ui.indexLabel.font().pointSize()
    skip_pt = ui.skipHidden.font().pointSize()

    Viewer._tighten_header(ui.horizontalLayout_5)

    assert ui.fileNameLabel.font().pointSize() == name_pt
    assert ui.indexLabel.font().pointSize() == index_pt
    assert ui.skipHidden.font().pointSize() == skip_pt


def test_file_name_does_not_pin_window_minimum(qtbot):
    """A long file name must not force the header minimum width up.

    The file-name label is capped at a 10px minimum, so even a very long name
    cannot push the window's minimum width past the screen edge.
    """
    win, ui = _build_header(qtbot)
    Viewer._tighten_header(ui.horizontalLayout_5)

    ui.fileNameLabel.setText("(short)")
    ui.mainHeaderWidget.layout().invalidate()
    baseline = ui.mainHeaderWidget.layout().minimumSize().width()

    ui.fileNameLabel.setText("DJI_20250509162825_0046_V_map-plan-681e72dc08bf0d0a.JPG")
    ui.mainHeaderWidget.layout().invalidate()
    grown = ui.mainHeaderWidget.layout().minimumSize().width()

    # The long name must not widen the header minimum (label is capped at 10px).
    assert grown <= baseline


def test_file_name_label_is_not_horizontally_expanding(qtbot):
    """The file-name label must hug its content, keeping the left group left-justified.

    Regression: making ``fileNameLabel`` horizontally ``Expanding`` made it
    absorb the row's slack, so the file name pinned to the far left while the
    index label, Show Overlay toggle and toolbar buttons were shoved toward the
    center. The label should not expand; the dedicated spacer absorbs the slack.
    """
    win, ui = _build_header(qtbot)
    assert (ui.fileNameLabel.sizePolicy().horizontalPolicy()
            != QSizePolicy.Policy.Expanding)


def test_single_expanding_spacer_right_justifies_buttons(qtbot):
    """Exactly one expanding spacer sits between the Show Overlay control and buttons.

    That single expanding item absorbs the header's horizontal slack, so the
    file name / index / Show Overlay group stays left-justified and the toolbar
    buttons are pushed to the right — the "float left / float right" layout.
    """
    win, ui = _build_header(qtbot)
    layout = ui.horizontalLayout_5

    overlay_idx = layout.indexOf(ui.showOverlayCheckBox)
    first_button_idx = layout.indexOf(ui.galleryModeButton)

    expanding_spacer_positions = [
        i for i in range(layout.count())
        if (spacer := layout.itemAt(i).spacerItem()) is not None
        and spacer.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Expanding
    ]

    # Precisely one expanding spacer...
    assert len(expanding_spacer_positions) == 1
    # ...positioned after the Show Overlay control and before the first button,
    # so the buttons are right-justified.
    assert overlay_idx < expanding_spacer_positions[0] < first_button_idx


def test_narrow_header_truncates_only_the_file_name(qtbot):
    """At the tightest fit, only the file name is clipped; the index stays whole."""
    win, ui = _build_header(qtbot)
    ui.fileNameLabel.setText("DJI_20250509162825_0046_a_long_enough_name.JPG")
    ui.indexLabel.setText("(Image 1 of 49)")
    Viewer._tighten_header(ui.horizontalLayout_5)

    ui.mainHeaderWidget.show()
    layout = ui.mainHeaderWidget.layout()
    layout.activate()
    name_natural = ui.fileNameLabel.sizeHint().width()
    index_natural = ui.indexLabel.sizeHint().width()

    # Squeeze the header to its tightest legal width.
    layout.invalidate()
    ui.mainHeaderWidget.setFixedWidth(layout.minimumSize().width())
    layout.activate()

    # The file name is clipped well below its natural width...
    assert ui.fileNameLabel.width() < name_natural
    # ...while the index label keeps its full text.
    assert ui.indexLabel.width() >= index_natural
