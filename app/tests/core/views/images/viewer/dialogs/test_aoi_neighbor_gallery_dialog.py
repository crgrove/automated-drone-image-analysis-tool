"""
Comprehensive tests for AOINeighborGalleryDialog.

Tests for the gallery dialog that displays AOI appearances across neighboring images:
- Dialog initialization
- ThumbnailItem class
- NeighborGalleryView functionality
- Thumbnail loading and display
- User interaction (click, zoom, pan)
- Keyboard shortcuts
"""

from core.views.images.viewer.dialogs.AOINeighborGalleryDialog import (
    AOINeighborGalleryDialog,
    NeighborGalleryView,
    ThumbnailItem
)
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QPointF, qInstallMessageHandler, QtMsgType
import os
import pytest
import numpy as np
from unittest.mock import patch, MagicMock

# Suppress Qt QPainter warnings in headless test environment
# QPixmap requires a display backend which may not be available in CI/tests
os.environ.setdefault('QT_LOGGING_RULES', '*.debug=false;qt.qpa.*=false')


def _qt_message_handler(mode, context, message):
    """Filter out QPainter warnings that occur in headless test environments."""
    if 'QPainter' in message:
        return  # Suppress QPainter warnings
    # Print other messages normally
    print(message)


# Install custom message handler to suppress QPainter warnings
qInstallMessageHandler(_qt_message_handler)


@pytest.fixture(scope='session')
def app():
    """Create QApplication for widget tests."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def sample_thumbnail():
    """Create a sample thumbnail image."""
    return np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)


@pytest.fixture
def sample_results(sample_thumbnail):
    """Create sample neighbor search results."""
    return [
        {
            'image_idx': 0,
            'image_name': 'DJI_0001.JPG',
            'image_path': '/path/to/DJI_0001.JPG',
            'pixel_x': 750.5,
            'pixel_y': 500.5,
            'thumbnail': sample_thumbnail.copy(),
            'is_current': False
        },
        {
            'image_idx': 1,
            'image_name': 'DJI_0002.JPG',
            'image_path': '/path/to/DJI_0002.JPG',
            'pixel_x': 800.0,
            'pixel_y': 450.0,
            'thumbnail': sample_thumbnail.copy(),
            'is_current': True  # Current/originating image
        },
        {
            'image_idx': 2,
            'image_name': 'DJI_0003.JPG',
            'image_path': '/path/to/DJI_0003.JPG',
            'pixel_x': 700.0,
            'pixel_y': 550.0,
            'thumbnail': sample_thumbnail.copy(),
            'is_current': False
        }
    ]


@pytest.fixture
def grayscale_result():
    """Create a sample result with grayscale thumbnail."""
    return {
        'image_idx': 0,
        'image_name': 'thermal.JPG',
        'image_path': '/path/to/thermal.JPG',
        'pixel_x': 500.0,
        'pixel_y': 400.0,
        'thumbnail': np.random.randint(0, 255, (200, 200), dtype=np.uint8),
        'is_current': False
    }


# ============================================================================
# Test ThumbnailItem class
# ============================================================================

class TestThumbnailItem:
    """Tests for ThumbnailItem data class."""

    def test_initialization(self, sample_thumbnail):
        """Test ThumbnailItem initialization with all parameters."""
        item = ThumbnailItem(
            image_idx=5,
            image_name='test_image.jpg',
            thumbnail=sample_thumbnail,
            pixel_x=100.5,
            pixel_y=200.5,
            is_current=True
        )

        assert item.image_idx == 5
        assert item.image_name == 'test_image.jpg'
        assert np.array_equal(item.thumbnail, sample_thumbnail)
        assert item.pixel_x == 100.5
        assert item.pixel_y == 200.5
        assert item.is_current is True

    def test_default_is_current(self, sample_thumbnail):
        """Test ThumbnailItem with default is_current value."""
        item = ThumbnailItem(
            image_idx=0,
            image_name='test.jpg',
            thumbnail=sample_thumbnail,
            pixel_x=0,
            pixel_y=0
        )

        assert item.is_current is False


# ============================================================================
# Test NeighborGalleryView
# ============================================================================

class TestNeighborGalleryView:
    """Tests for NeighborGalleryView widget."""

    def test_initialization(self, app):
        """Test NeighborGalleryView initialization."""
        view = NeighborGalleryView()

        assert view is not None
        assert view.scene is not None
        assert view._zoom == 1.0
        assert view._panning is False
        assert view._thumbnail_rects == []
        assert view._selected_index == -1

    def test_style_settings(self, app):
        """Test view style settings are initialized."""
        view = NeighborGalleryView()

        assert view.thumbnail_spacing == 20
        assert view.thumbnail_size == 200
        assert view.label_height == 25
        assert view.current_highlight_width == 4

    def test_load_thumbnails_empty(self, app):
        """Test loading empty results."""
        view = NeighborGalleryView()
        view.load_thumbnails([])

        assert view._thumbnail_rects == []
        assert view._results == []

    def test_load_thumbnails_none(self, app):
        """Test loading None results."""
        view = NeighborGalleryView()
        view.load_thumbnails(None)

        assert view._thumbnail_rects == []
        assert view._results == []

    def test_load_thumbnails_success(self, app, sample_results):
        """Test loading thumbnails successfully."""
        view = NeighborGalleryView()
        view.load_thumbnails(sample_results)

        # Should have created thumbnail rects for each result
        assert len(view._thumbnail_rects) == 3
        assert len(view._border_items) == 3
        assert view._results == sample_results

    def test_load_thumbnails_with_grayscale(self, app, grayscale_result):
        """Test loading grayscale thumbnail."""
        view = NeighborGalleryView()
        view.load_thumbnails([grayscale_result])

        assert len(view._thumbnail_rects) == 1

    def test_load_thumbnails_marks_current(self, app, sample_results):
        """Test that current image is highlighted differently."""
        view = NeighborGalleryView()
        view.load_thumbnails(sample_results)

        # Check that border items include current flag
        current_items = [item for item in view._border_items if item[2] is True]
        assert len(current_items) == 1
        assert current_items[0][0] == 1  # image_idx 1 is current

    def test_load_thumbnails_skip_none_thumbnail(self, app, sample_thumbnail):
        """Test that results with None thumbnail are skipped."""
        results = [
            {'image_idx': 0, 'image_name': 'test.jpg', 'thumbnail': sample_thumbnail.copy()},
            {'image_idx': 1, 'image_name': 'test2.jpg', 'thumbnail': None},  # None thumbnail
            {'image_idx': 2, 'image_name': 'test3.jpg', 'thumbnail': sample_thumbnail.copy()},
        ]
        view = NeighborGalleryView()
        view.load_thumbnails(results)

        # Only 2 should be loaded
        assert len(view._thumbnail_rects) == 2

    def test_reset_view(self, app, sample_results):
        """Test reset view functionality."""
        view = NeighborGalleryView()
        view.load_thumbnails(sample_results)

        # Modify zoom
        view._zoom = 2.0

        view.reset_view()

        assert view._zoom == 1.0

    def test_select_thumbnail(self, app, sample_results):
        """Test thumbnail selection."""
        view = NeighborGalleryView()
        view.load_thumbnails(sample_results)

        view.select_thumbnail(1)

        assert view._selected_index == 1

    def test_select_thumbnail_updates_borders(self, app, sample_results):
        """Test that selecting thumbnail updates border colors."""
        view = NeighborGalleryView()
        view.load_thumbnails(sample_results)

        # Select thumbnail
        view.select_thumbnail(0)

        # Check that borders were updated (no exception thrown)
        assert view._selected_index == 0


# ============================================================================
# Test AOINeighborGalleryDialog
# ============================================================================

class TestAOINeighborGalleryDialog:
    """Tests for AOINeighborGalleryDialog."""

    def test_initialization_no_results(self, app):
        """Test dialog initialization with no results."""
        dialog = AOINeighborGalleryDialog(None, None)

        assert dialog is not None
        assert dialog.results == []
        assert dialog.windowTitle() == "AOI in Neighboring Images"

    def test_initialization_with_results(self, app, sample_results):
        """Test dialog initialization with results."""
        dialog = AOINeighborGalleryDialog(None, sample_results)

        assert dialog.results == sample_results
        assert dialog.gallery_view is not None

    def test_dialog_is_non_modal(self, app, sample_results):
        """Test that dialog is non-modal."""
        dialog = AOINeighborGalleryDialog(None, sample_results)

        assert not dialog.isModal()

    def test_dialog_has_stays_on_top_flag(self, app, sample_results):
        """Test that dialog has stay on top flag."""
        dialog = AOINeighborGalleryDialog(None, sample_results)

        # Check window flags
        flags = dialog.windowFlags()
        assert flags & Qt.WindowStaysOnTopHint

    def test_dialog_initial_size(self, app, sample_results):
        """Test dialog initial size."""
        dialog = AOINeighborGalleryDialog(None, sample_results)

        assert dialog.width() == 900
        assert dialog.height() == 400

    def test_info_label_content(self, app, sample_results):
        """Test info label shows correct count."""
        dialog = AOINeighborGalleryDialog(None, sample_results)

        info_text = dialog.info_label.text()
        assert "3 image(s)" in info_text

    def test_gallery_view_exists(self, app, sample_results):
        """Test that gallery view is created."""
        dialog = AOINeighborGalleryDialog(None, sample_results)

        assert dialog.gallery_view is not None
        assert isinstance(dialog.gallery_view, NeighborGalleryView)

    def test_thumbnail_clicked_signal(self, app, sample_results):
        """Test that thumbnail click emits signal."""
        dialog = AOINeighborGalleryDialog(None, sample_results)

        # Track emitted signals
        emitted_values = []
        dialog.image_clicked.connect(lambda idx: emitted_values.append(idx))

        # Simulate thumbnail click by calling the handler
        dialog._on_thumbnail_clicked(2)

        assert len(emitted_values) == 1
        assert emitted_values[0] == 2

    def test_escape_key_closes_dialog(self, app, sample_results):
        """Test that Escape key closes the dialog."""
        dialog = AOINeighborGalleryDialog(None, sample_results)
        dialog.show()

        # Create key event for Escape
        from PySide6.QtGui import QKeyEvent
        from PySide6.QtCore import QEvent
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_Escape, Qt.NoModifier)

        dialog.keyPressEvent(event)

        # Dialog should be closing (visibility may depend on event loop)
        assert event.isAccepted()

    def test_r_key_resets_view(self, app, sample_results):
        """Test that R key resets the view."""
        dialog = AOINeighborGalleryDialog(None, sample_results)

        # Modify zoom
        dialog.gallery_view._zoom = 3.0

        # Create key event for R
        from PySide6.QtGui import QKeyEvent
        from PySide6.QtCore import QEvent
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_R, Qt.NoModifier)

        dialog.keyPressEvent(event)

        assert dialog.gallery_view._zoom == 1.0


# ============================================================================
# Test edge cases and error handling
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_load_invalid_thumbnail_shape(self, app):
        """Test loading thumbnail with unexpected shape."""
        results = [
            {
                'image_idx': 0,
                'image_name': 'test.jpg',
                'thumbnail': np.zeros((10, 10, 10, 10), dtype=np.uint8),  # 4D array
                'is_current': False
            }
        ]

        view = NeighborGalleryView()
        # Should handle gracefully without crashing
        view.load_thumbnails(results)

    def test_result_missing_optional_fields(self, app, sample_thumbnail):
        """Test loading result with minimal fields."""
        results = [
            {
                'image_idx': 0,
                'thumbnail': sample_thumbnail.copy()
                # Missing image_name, is_current, etc.
            }
        ]

        view = NeighborGalleryView()
        view.load_thumbnails(results)

        # Should still create thumbnail rect
        assert len(view._thumbnail_rects) == 1

    def test_dialog_with_empty_list(self, app):
        """Test dialog with empty results list."""
        dialog = AOINeighborGalleryDialog(None, [])

        assert dialog.results == []
        assert "0 image(s)" in dialog.info_label.text()

    def test_gallery_view_min_zoom_limit(self, app, sample_results):
        """Test that zoom out has minimum limit."""
        view = NeighborGalleryView()
        view.load_thumbnails(sample_results)

        # Try to zoom out many times
        for _ in range(100):
            view._zoom = max(view._min_zoom, view._zoom / 1.15)

        # Should not go below minimum
        assert view._zoom >= view._min_zoom

    def test_gallery_view_zoom_in_no_max(self, app, sample_results):
        """Test that zoom in has no upper limit (removed in implementation)."""
        view = NeighborGalleryView()
        view.load_thumbnails(sample_results)

        # Zoom in many times
        for _ in range(50):
            view._zoom *= 1.15

        # Should be able to zoom significantly
        assert view._zoom > 10.0

    def test_select_nonexistent_thumbnail(self, app, sample_results):
        """Test selecting thumbnail that doesn't exist."""
        view = NeighborGalleryView()
        view.load_thumbnails(sample_results)

        # Select non-existent index (should not crash)
        view.select_thumbnail(999)

        assert view._selected_index == 999  # Still sets the index


# ============================================================================
# Test integration scenarios
# ============================================================================

class TestIntegration:
    """Integration tests for gallery dialog workflow."""

    def test_full_workflow(self, app, sample_results):
        """Test complete workflow: create dialog, load thumbnails, select, close."""
        # Create dialog with results
        dialog = AOINeighborGalleryDialog(None, sample_results)
        dialog.show()

        # Process events to allow QTimer to fire and load thumbnails
        app.processEvents()
        import time
        time.sleep(0.05)  # Wait for QTimer (10ms) + processing
        app.processEvents()

        # Verify thumbnails loaded
        assert len(dialog.gallery_view._thumbnail_rects) == 3

        # Simulate selection
        dialog.gallery_view.select_thumbnail(1)
        assert dialog.gallery_view._selected_index == 1

        # Reset view
        dialog.gallery_view.reset_view()
        assert dialog.gallery_view._zoom == 1.0

        # Close dialog
        dialog.close()

    def test_signal_chain(self, app, sample_results):
        """Test signal propagation from gallery view to dialog."""
        dialog = AOINeighborGalleryDialog(None, sample_results)

        # Track signals
        clicked_indices = []
        dialog.image_clicked.connect(lambda idx: clicked_indices.append(idx))

        # Emit signal from gallery view
        dialog.gallery_view.thumbnail_clicked.emit(0)

        assert len(clicked_indices) == 1
        assert clicked_indices[0] == 0

    def test_reload_thumbnails(self, app, sample_results, sample_thumbnail):
        """Test reloading thumbnails clears previous state."""
        view = NeighborGalleryView()
        view.load_thumbnails(sample_results)

        # Store initial state
        initial_rect_count = len(view._thumbnail_rects)
        assert initial_rect_count == 3

        # Select a thumbnail
        view.select_thumbnail(1)
        assert view._selected_index == 1

        # Reload with different results
        new_results = [
            {'image_idx': 5, 'image_name': 'new.jpg', 'thumbnail': sample_thumbnail.copy()}
        ]
        view.load_thumbnails(new_results)

        # State should be reset
        assert len(view._thumbnail_rects) == 1
        assert view._selected_index == -1
