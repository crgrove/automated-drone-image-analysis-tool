"""Sidebar AOI thumbnails show a duplicate's link: violet flag and "#2 -> #1"."""

from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication, QLabel

from core.controllers.images.viewer.aoi.AOIUIComponent import AOIUIComponent


@pytest.fixture(scope='session')
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def component(app):
    aoi_controller = MagicMock()
    aoi_controller.parent.images = [{'areas_of_interest': [
        {'center': (10, 10), 'radius': 5, 'area': 20, 'number': 1, 'flagged': True},
        {'center': (50, 50), 'radius': 5, 'area': 20, 'number': 2, 'duplicate_of': 1},
        {'center': (90, 90), 'radius': 5, 'area': 20, 'number': 3, 'duplicate_of': 99},
    ]}]
    return AOIUIComponent(aoi_controller)


def _aoi(component, index):
    return component.aoi_controller.parent.images[0]['areas_of_interest'][index]


def _labels(widget):
    return widget.findChildren(QLabel)


def test_live_duplicate_of_ignores_orphaned_links(component):
    assert component._live_duplicate_of(_aoi(component, 1)) == 1
    assert component._live_duplicate_of(_aoi(component, 2)) is None
    assert component._live_duplicate_of(_aoi(component, 0)) is None


def test_duplicate_number_label_names_the_primary(component):
    widget = component._create_top_info_widget("(50, 50)", 1, _aoi(component, 1))
    texts = [label.text() for label in _labels(widget)]
    assert "#2 → #1" in texts


def test_duplicate_flag_tooltip_explains_the_click(component):
    widget = component._create_bottom_info_widget(None, None, 1, set(), _aoi(component, 1))
    tooltips = [label.toolTip() for label in _labels(widget)]
    assert any(tip.startswith("Duplicate of AOI #1") for tip in tooltips)


def test_flagged_and_plain_flags_unchanged(component):
    flagged = component._create_bottom_info_widget(None, None, 0, {0}, _aoi(component, 0))
    plain = component._create_bottom_info_widget(None, None, 2, set(), _aoi(component, 2))
    assert "Unflag AOI" in [label.toolTip() for label in _labels(flagged)]
    assert "Flag AOI" in [label.toolTip() for label in _labels(plain)]
