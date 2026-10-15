"""Tests for AOIDuplicatePickerDialog - choosing the primary an AOI duplicates."""

import numpy as np
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox

from core.services.AOIDuplicateService import DuplicateCandidate
from core.views.images.viewer.dialogs.AOIDuplicatePickerDialog import AOIDuplicatePickerDialog, _to_pixmap


@pytest.fixture(scope='session')
def app():
    return QApplication.instance() or QApplication([])


def _candidate(number, distance_m=12.0, similarity=84, duplicate_count=0):
    return DuplicateCandidate(image_idx=number, aoi_idx=0, number=number, image_name=f"IMG_{number:04d}.JPG",
                              similarity=similarity, distance_m=distance_m,
                              duplicate_count=duplicate_count, score=0.5)


def _entries(*candidates):
    thumbnail = np.full((180, 180, 3), 120, dtype=np.uint8)
    return [{'candidate': candidate, 'thumbnail': thumbnail} for candidate in candidates]


@pytest.fixture
def dialog(app, qtbot):
    source = {'number': 46, 'image_name': 'IMG_0046.JPG', 'thumbnail': np.zeros((180, 180, 3), dtype=np.uint8)}
    dlg = AOIDuplicatePickerDialog(None, source, _entries(_candidate(12, duplicate_count=2), _candidate(30)))
    qtbot.addWidget(dlg)
    return dlg


def test_best_match_is_preselected(dialog):
    assert dialog.candidateList.count() == 2
    assert dialog.candidateList.currentRow() == 0
    assert dialog.selected_candidate().number == 12
    ok = dialog.buttonBox.button(QDialogButtonBox.Ok)
    assert ok.isEnabled()
    assert ok.text() == "Mark as Duplicate"


def test_source_aoi_is_shown(dialog):
    assert dialog.sourceCaptionLabel.text() == "AOI #46\nIMG_0046.JPG"
    assert not dialog.sourceThumbnailLabel.pixmap().isNull()


def test_candidate_captions_and_details(dialog):
    item = dialog.candidateList.item(0)
    assert item.text() == "AOI #12 (+2 dup.)\nIMG_0012.JPG"
    assert item.toolTip() == "12 m away · 84% alike"
    assert not item.icon().isNull()


def test_feet_and_missing_values(app, qtbot):
    dlg = AOIDuplicatePickerDialog(None, {}, [], distance_unit='ft')
    qtbot.addWidget(dlg)
    assert dlg.candidate_details(_candidate(5, distance_m=10.0, similarity=None)) == "33 ft away"
    assert dlg.candidate_details(_candidate(5, distance_m=None, similarity=None)) == ""
    assert dlg.candidate_text(_candidate(5)) == "AOI #5\nIMG_0005.JPG"


def test_caption_strip_leaves_the_original_untouched(app):
    from core.views.images.viewer.dialogs.AOIDuplicatePickerDialog import _with_caption_strip
    original = _to_pixmap(np.full((150, 150, 3), 200, dtype=np.uint8))
    annotated = _with_caption_strip(original, "6 m away")
    assert annotated is not original
    assert annotated.toImage().pixelColor(75, 148) != original.toImage().pixelColor(75, 148)
    assert _with_caption_strip(original, "") is original


def test_choosing_another_tile(dialog):
    dialog.candidateList.setCurrentRow(1)
    assert dialog.selected_candidate().number == 30


def test_double_click_accepts(dialog):
    item = dialog.candidateList.item(1)
    dialog.candidateList.setCurrentItem(item)
    dialog.candidateList.itemDoubleClicked.emit(item)
    assert dialog.result() == QDialog.Accepted
    assert dialog.selected_candidate().number == 30


def test_enter_accepts_the_preselected_match(dialog, qtbot):
    dialog.show()
    qtbot.keyClick(dialog.candidateList, Qt.Key_Return)
    assert dialog.result() == QDialog.Accepted
    assert dialog.selected_candidate().number == 12


def test_no_candidates_disables_ok(app, qtbot):
    dlg = AOIDuplicatePickerDialog(None, {}, [])
    qtbot.addWidget(dlg)
    assert dlg.selected_candidate() is None
    assert not dlg.buttonBox.button(QDialogButtonBox.Ok).isEnabled()


def test_to_pixmap_handles_grayscale_and_rejects_bad_shapes(app):
    assert _to_pixmap(None) is None
    assert _to_pixmap(np.zeros((10, 10), dtype=np.uint8)).width() == 10
    assert _to_pixmap(np.zeros((10, 10, 4), dtype=np.uint8)) is None
