"""Tests for AOISimilaritySortDialog: defaults, unit conversion, and remembered values."""

import pytest

from core.views.images.viewer.dialogs import AOISimilaritySortDialog as dialog_module
from core.views.images.viewer.dialogs.AOISimilaritySortDialog import (
    AOISimilaritySortDialog,
    FEET_PER_METER,
    MAX_DISTANCE_SETTING,
    MIN_SIMILARITY_SETTING,
)
from core.services.image.AOISimilarityGroupingService import (
    DEFAULT_MAX_DISTANCE_M, DEFAULT_MIN_SIMILARITY
)


class FakeSettings:
    store = {}

    def get_setting(self, name, default_value=None):
        return self.store.get(name, default_value)

    def set_setting(self, name, value):
        self.store[name] = value


@pytest.fixture(autouse=True)
def settings(monkeypatch):
    FakeSettings.store = {}
    monkeypatch.setattr(dialog_module, 'SettingsService', FakeSettings)
    return FakeSettings.store


def test_defaults_in_metres(qtbot):
    dialog = AOISimilaritySortDialog(None, 'm')
    qtbot.addWidget(dialog)
    assert dialog.get_max_distance_m() == pytest.approx(DEFAULT_MAX_DISTANCE_M)
    assert dialog.get_min_similarity() == DEFAULT_MIN_SIMILARITY
    assert dialog.distanceSpinBox.suffix() == " m"


def test_feet_are_shown_and_converted_back(qtbot):
    dialog = AOISimilaritySortDialog(None, 'ft')
    qtbot.addWidget(dialog)
    assert dialog.distanceSpinBox.suffix() == " ft"
    assert dialog.distanceSpinBox.value() == pytest.approx(DEFAULT_MAX_DISTANCE_M * FEET_PER_METER, abs=0.05)
    dialog.distanceSpinBox.setValue(100.0)
    assert dialog.get_max_distance_m() == pytest.approx(100.0 / FEET_PER_METER)


def test_accept_remembers_values(qtbot, settings):
    dialog = AOISimilaritySortDialog(None, 'm')
    qtbot.addWidget(dialog)
    dialog.distanceSpinBox.setValue(30.0)
    dialog.similaritySpinBox.setValue(85)
    dialog.accept()

    assert settings[MAX_DISTANCE_SETTING] == pytest.approx(30.0)
    assert settings[MIN_SIMILARITY_SETTING] == 85

    reopened = AOISimilaritySortDialog(None, 'm')
    qtbot.addWidget(reopened)
    assert reopened.get_max_distance_m() == pytest.approx(30.0)
    assert reopened.get_min_similarity() == 85


def test_corrupt_stored_values_fall_back_to_defaults(qtbot, settings):
    settings[MAX_DISTANCE_SETTING] = 'not a number'
    settings[MIN_SIMILARITY_SETTING] = 500
    dialog = AOISimilaritySortDialog(None, 'm')
    qtbot.addWidget(dialog)
    assert dialog.get_max_distance_m() == pytest.approx(DEFAULT_MAX_DISTANCE_M)
    assert dialog.get_min_similarity() == DEFAULT_MIN_SIMILARITY
