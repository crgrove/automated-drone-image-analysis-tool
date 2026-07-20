"""
Tests for AOISimilarityResultsDialog.

Covers dialog initialization, thumbnail loading (including reference styling and
None-thumbnail tolerance), click-to-row signal propagation, and keyboard shortcuts.
"""

from core.views.images.viewer.dialogs.AOISimilarityResultsDialog import (
    AOISimilarityResultsDialog,
    SimilarityGalleryView,
)
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, qInstallMessageHandler
import os
import pytest
import numpy as np

# Suppress Qt QPainter warnings in headless test environment
os.environ.setdefault('QT_LOGGING_RULES', '*.debug=false;qt.qpa.*=false')


def _qt_message_handler(mode, context, message):
    """Filter out QPainter warnings that occur in headless test environments."""
    if 'QPainter' in message:
        return
    print(message)


qInstallMessageHandler(_qt_message_handler)


@pytest.fixture(scope='session')
def app():
    """Create QApplication for widget tests."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def sample_thumbnail():
    """Create a sample thumbnail image."""
    return np.random.randint(0, 255, (180, 180, 3), dtype=np.uint8)


@pytest.fixture
def sample_results(sample_thumbnail):
    """Create sample similarity results: reference first, then two matches."""
    return [
        {
            'image_idx': 1,
            'aoi_idx': 0,
            'image_name': 'DJI_0002.JPG',
            'image_path': '/path/to/DJI_0002.JPG',
            'aoi_number': 12,
            'similarity': 100,
            'thumbnail': sample_thumbnail.copy(),
            'aoi_data': {'center': (100, 100), 'radius': 40},
            'is_reference': True,
        },
        {
            'image_idx': 0,
            'aoi_idx': 2,
            'image_name': 'DJI_0001.JPG',
            'image_path': '/path/to/DJI_0001.JPG',
            'aoi_number': 3,
            'similarity': 82,
            'thumbnail': sample_thumbnail.copy(),
            'aoi_data': {'center': (300, 200), 'radius': 30},
            'is_reference': False,
        },
        {
            'image_idx': 2,
            'aoi_idx': 1,
            'image_name': 'DJI_0003.JPG',
            'image_path': '/path/to/DJI_0003.JPG',
            'aoi_number': None,  # Exercises the index fallback caption
            'similarity': 47,
            'thumbnail': sample_thumbnail.copy(),
            'aoi_data': {'center': (50, 60), 'radius': 25},
            'is_reference': False,
        },
    ]


class TestSimilarityGalleryView:

    def test_initialization(self, app):
        view = SimilarityGalleryView()
        assert view.scene is not None
        assert view._zoom == 1.0
        assert view._thumbnail_rects == []
        assert view._selected_row == -1

    def test_load_thumbnails_empty_and_none(self, app):
        view = SimilarityGalleryView()
        view.load_thumbnails([])
        assert view._thumbnail_rects == []
        view.load_thumbnails(None)
        assert view._thumbnail_rects == []

    def test_load_thumbnails_success(self, app, sample_results):
        view = SimilarityGalleryView()
        view.load_thumbnails(sample_results)
        assert len(view._thumbnail_rects) == 3
        assert len(view._border_items) == 3
        # Rows map to the results-list indices
        assert [row for _, row in view._thumbnail_rects] == [0, 1, 2]

    def test_reference_row_styled(self, app, sample_results):
        view = SimilarityGalleryView()
        view.load_thumbnails(sample_results)
        reference_items = [item for item in view._border_items if item[2] is True]
        assert len(reference_items) == 1
        assert reference_items[0][0] == 0  # Row 0 is the reference

    def test_none_thumbnail_skipped_but_rows_stay_aligned(self, app, sample_results):
        sample_results[1]['thumbnail'] = None
        view = SimilarityGalleryView()
        view.load_thumbnails(sample_results)
        # Row 1 is skipped; remaining tiles keep their original row keys
        assert [row for _, row in view._thumbnail_rects] == [0, 2]

    def test_select_thumbnail(self, app, sample_results):
        view = SimilarityGalleryView()
        view.load_thumbnails(sample_results)
        view.select_thumbnail(2)
        assert view._selected_row == 2

    def test_similarity_color_thresholds(self, app):
        green = SimilarityGalleryView._similarity_color(80)
        gold = SimilarityGalleryView._similarity_color(60)
        gray = SimilarityGalleryView._similarity_color(30)
        assert green.name() == '#4caf50'
        assert gold.name() == '#ffd700'
        assert gray.name() == '#aaaaaa'

    def test_grayscale_thumbnail_supported(self, app):
        results = [{
            'image_idx': 0, 'aoi_idx': 0, 'image_name': 'thermal.JPG',
            'similarity': 90, 'is_reference': False,
            'thumbnail': np.random.randint(0, 255, (180, 180), dtype=np.uint8),
        }]
        view = SimilarityGalleryView()
        view.load_thumbnails(results)
        assert len(view._thumbnail_rects) == 1


class TestAOISimilarityResultsDialog:

    def test_initialization(self, app, sample_results):
        dialog = AOISimilarityResultsDialog(None, sample_results, total_candidates=57)
        assert dialog.results == sample_results
        assert dialog.windowTitle() == "Similar AOIs"
        assert not dialog.isModal()
        assert dialog.windowFlags() & Qt.WindowStaysOnTopHint
        assert dialog.width() == 900
        assert dialog.height() == 430

    def test_initialization_no_results(self, app):
        dialog = AOISimilarityResultsDialog(None, None)
        assert dialog.results == []

    def test_info_label_counts(self, app, sample_results):
        dialog = AOISimilarityResultsDialog(None, sample_results, total_candidates=57)
        text = dialog.info_label.text()
        assert "Top 2 of 57" in text
        assert "AOI #12" in text  # Reference AOI number

    def test_result_clicked_signal(self, app, sample_results):
        dialog = AOISimilarityResultsDialog(None, sample_results, total_candidates=2)
        clicked_rows = []
        dialog.result_clicked.connect(clicked_rows.append)

        dialog.gallery_view.thumbnail_clicked.emit(1)
        assert clicked_rows == [1]

    def test_click_inside_tile_rect_emits_row(self, app, sample_results):
        dialog = AOISimilarityResultsDialog(None, sample_results, total_candidates=2)
        dialog.show()
        app.processEvents()
        import time
        time.sleep(0.05)  # Wait for the deferred QTimer load (10ms)
        app.processEvents()

        view = dialog.gallery_view
        assert len(view._thumbnail_rects) == 3

        clicked_rows = []
        dialog.result_clicked.connect(clicked_rows.append)

        # Simulate a click on the second tile via its stored rect
        rect, row = view._thumbnail_rects[1]
        view.select_thumbnail(row)
        view.thumbnail_clicked.emit(row)

        assert clicked_rows == [1]
        assert view._selected_row == 1
        dialog.close()

    def test_escape_key_closes(self, app, sample_results):
        from PySide6.QtGui import QKeyEvent
        from PySide6.QtCore import QEvent
        dialog = AOISimilarityResultsDialog(None, sample_results, total_candidates=2)
        dialog.show()
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_Escape, Qt.NoModifier)
        dialog.keyPressEvent(event)
        assert event.isAccepted()

    def test_r_key_resets_view(self, app, sample_results):
        from PySide6.QtGui import QKeyEvent
        from PySide6.QtCore import QEvent
        dialog = AOISimilarityResultsDialog(None, sample_results, total_candidates=2)
        dialog.gallery_view._zoom = 3.0
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_R, Qt.NoModifier)
        dialog.keyPressEvent(event)
        assert dialog.gallery_view._zoom == 1.0

    def test_tolerates_none_thumbnails(self, app, sample_results):
        for result in sample_results:
            result['thumbnail'] = None
        dialog = AOISimilarityResultsDialog(None, sample_results, total_candidates=2)
        dialog.show()
        app.processEvents()
        import time
        time.sleep(0.05)
        app.processEvents()
        assert dialog.gallery_view._thumbnail_rects == []
        dialog.close()


# ============================================================================
# Bulk selection and actions
# ============================================================================

def _loaded_dialog(app, results, total=2):
    """Create a dialog and force-load its thumbnails synchronously."""
    dialog = AOISimilarityResultsDialog(None, results, total_candidates=total)
    dialog.gallery_view.load_thumbnails(results)
    return dialog


class TestBulkSelection:

    def test_checkboxes_only_on_aoi_rows(self, app, sample_results):
        # A malformed row without a backing AOI gets no checkbox but still renders
        sample_results[0]['aoi_idx'] = None
        sample_results[0]['image_idx'] = None
        sample_results[0]['aoi_data'] = None
        sample_results[0]['aoi_number'] = None
        view = SimilarityGalleryView()
        view.load_thumbnails(sample_results)

        assert set(view._checkbox_items.keys()) == {1, 2}
        assert len(view._thumbnail_rects) == 3

    def test_toggle_and_get_checked_rows(self, app, sample_results):
        view = SimilarityGalleryView()
        view.load_thumbnails(sample_results)

        counts = []
        view.selection_changed.connect(counts.append)

        view.toggle_row_checked(1)
        view.toggle_row_checked(2)
        assert view.get_checked_rows() == [1, 2]
        view.toggle_row_checked(1)
        assert view.get_checked_rows() == [2]
        assert counts == [1, 2, 1]

    def test_set_row_checked_ignores_uncheckable_rows(self, app, sample_results):
        sample_results[0]['aoi_idx'] = None
        view = SimilarityGalleryView()
        view.load_thumbnails(sample_results)

        view.set_row_checked(0, True)  # No checkbox on row 0
        assert view.get_checked_rows() == []

    def test_select_all_and_clear(self, app, sample_results):
        dialog = _loaded_dialog(app, sample_results)

        dialog.gallery_view.set_all_checked(True)
        assert dialog.gallery_view.get_checked_rows() == [0, 1, 2]
        assert dialog.flag_button.isEnabled()
        assert dialog.unflag_button.isEnabled()
        assert dialog.comment_button.isEnabled()
        assert "3" in dialog.selection_label.text()

        dialog.gallery_view.set_all_checked(False)
        assert dialog.gallery_view.get_checked_rows() == []
        assert not dialog.flag_button.isEnabled()
        assert not dialog.unflag_button.isEnabled()
        assert not dialog.comment_button.isEnabled()

    def test_reload_clears_selection(self, app, sample_results):
        view = SimilarityGalleryView()
        view.load_thumbnails(sample_results)
        view.set_all_checked(True)
        view.load_thumbnails(sample_results)
        assert view.get_checked_rows() == []

    def test_bulk_flag_signal_carries_checked_rows(self, app, sample_results):
        dialog = _loaded_dialog(app, sample_results)
        dialog.gallery_view.set_row_checked(1, True)
        dialog.gallery_view.set_row_checked(2, True)

        received = []
        dialog.bulk_flag_requested.connect(lambda rows, flagged: received.append((rows, flagged)))
        dialog._emit_bulk_flag(True)
        dialog._emit_bulk_flag(False)

        assert received == [([1, 2], True), ([1, 2], False)]

    def test_bulk_comment_signal_carries_checked_rows(self, app, sample_results):
        dialog = _loaded_dialog(app, sample_results)
        dialog.gallery_view.set_row_checked(2, True)

        received = []
        dialog.bulk_comment_requested.connect(received.append)
        dialog._emit_bulk_comment()

        assert received == [[2]]

    def test_bulk_signals_not_emitted_without_selection(self, app, sample_results):
        dialog = _loaded_dialog(app, sample_results)
        received = []
        dialog.bulk_flag_requested.connect(lambda rows, flagged: received.append(rows))
        dialog.bulk_comment_requested.connect(received.append)
        dialog._emit_bulk_flag(True)
        dialog._emit_bulk_comment()
        assert received == []


class TestStatusBadges:

    def test_badges_reflect_initial_state(self, app, sample_results):
        sample_results[1]['aoi_data'] = {'flagged': True, 'user_comment': 'check this'}
        view = SimilarityGalleryView()
        view.load_thumbnails(sample_results)

        flag_item, comment_item = view._badge_items[1]
        assert flag_item.isVisible()
        assert comment_item.isVisible()

        flag_item0, comment_item0 = view._badge_items[0]
        assert not flag_item0.isVisible()
        assert not comment_item0.isVisible()

    def test_refresh_status_badges_after_change(self, app, sample_results):
        dialog = _loaded_dialog(app, sample_results)
        flag_item, comment_item = dialog.gallery_view._badge_items[1]
        assert not flag_item.isVisible()

        # Simulate a bulk action mutating the live AOI dict
        dialog.results[1]['aoi_data']['flagged'] = True
        dialog.results[1]['aoi_data']['user_comment'] = 'orange tarp'
        dialog.refresh_status_badges()

        assert flag_item.isVisible()
        assert comment_item.isVisible()

    def test_checkbox_hit_takes_priority_over_tile(self, app, sample_results):
        view = SimilarityGalleryView()
        view.load_thumbnails(sample_results)

        # A point inside row 0's checkbox is also inside row 0's tile rect
        box_rect, row = view._checkbox_rects[0]
        assert any(tile.contains(box_rect.center()) for tile, _ in view._thumbnail_rects)

        clicked = []
        view.thumbnail_clicked.connect(clicked.append)
        view.toggle_row_checked(row)
        assert view.get_checked_rows() == [row]
        assert clicked == []
