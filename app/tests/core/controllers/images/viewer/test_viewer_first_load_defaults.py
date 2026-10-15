"""First-load view defaults: the results viewer opens in gallery mode with
AOIs sorted by pixel area, largest first (field request). The hook is
deferred one event-loop turn after the viewer is shown; these tests drive
the hook directly against a stub."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication, QComboBox

from core.controllers.images.viewer.Viewer import Viewer


@pytest.fixture(scope='session')
def app():
    return QApplication.instance() or QApplication([])


def _sort_combo():
    combo = QComboBox()
    combo.addItem("Default", None)
    combo.addItem("Pixel Area (Smallest First)", 'area_asc')
    combo.addItem("Pixel Area (Largest First)", 'area_desc')
    return combo


def _stub(images=({'name': 'a.jpg'},), gallery_mode=False):
    return SimpleNamespace(
        aoiSortComboBox=_sort_combo(),
        images=list(images),
        gallery_mode=gallery_mode,
        galleryModeButton=MagicMock(),
        logger=MagicMock(),
        _offer_wingtra_geotags=MagicMock(),
    )


def test_first_load_defaults_select_area_desc_and_enter_gallery(app):
    stub = _stub()

    Viewer._apply_first_load_view_defaults(stub)

    assert stub.aoiSortComboBox.currentData() == 'area_desc'
    stub.galleryModeButton.click.assert_called_once()


def test_first_load_defaults_skip_gallery_when_already_in_it(app):
    stub = _stub(gallery_mode=True)

    Viewer._apply_first_load_view_defaults(stub)

    assert stub.aoiSortComboBox.currentData() == 'area_desc'
    stub.galleryModeButton.click.assert_not_called()


def test_first_load_defaults_skip_gallery_without_images(app):
    stub = _stub(images=())

    Viewer._apply_first_load_view_defaults(stub)

    stub.galleryModeButton.click.assert_not_called()


def test_first_load_defaults_survive_a_missing_combo_entry(app):
    """A combo without the area_desc entry must not break startup."""
    stub = _stub()
    stub.aoiSortComboBox = QComboBox()  # empty combo, findData -> -1

    Viewer._apply_first_load_view_defaults(stub)

    stub.galleryModeButton.click.assert_called_once()  # gallery still entered


def test_first_load_offers_wingtra_geotags_after_the_view_defaults(app):
    """Once the viewer is on screen, so the question sits over its results."""
    stub = _stub()

    Viewer._apply_first_load_view_defaults(stub)

    stub._offer_wingtra_geotags.assert_called_once()


def test_a_failing_wingtra_offer_does_not_take_the_viewer_down(app):
    stub = SimpleNamespace(
        wingtra_controller=MagicMock(**{"auto_load_on_open.side_effect": OSError("disk")}),
        logger=MagicMock(),
        xml_path="ADIAT_Data.xml",
    )

    Viewer._offer_wingtra_geotags(stub)

    assert "ADIAT_Data.xml" in stub.logger.error.call_args[0][0]
