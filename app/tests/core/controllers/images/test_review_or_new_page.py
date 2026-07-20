"""
Tests for the Image Analysis Guide's Review-or-New first page.

Focus: the file picker must accept a batch's Search Coordinator project
(ADIAT_Search_*.xml) as readily as a single-run ADIAT_Data.xml result.
"""

import os
import pytest
from unittest.mock import patch

try:
    from core.controllers.images.ImageAnalysisGuide import ImageAnalysisGuide
    _GUIDE_AVAILABLE = True
except ImportError as e:
    _GUIDE_AVAILABLE = False
    _IMPORT_ERROR = str(e)


@pytest.fixture
def review_page(qtbot):
    if not _GUIDE_AVAILABLE:
        pytest.skip(f"ImageAnalysisGuide not available: {_IMPORT_ERROR}")
    guide = ImageAnalysisGuide()
    qtbot.addWidget(guide)
    # Page 0 is the ReviewOrNewPage, fully set up by the guide's __init__.
    return guide.pages[0]


def _browse_returning(page, file_path):
    """Invoke the page's browse handler as if the user picked file_path."""
    mod = 'core.controllers.images.guidePages.ReviewOrNewPage'
    with patch(f'{mod}.QFileDialog.getOpenFileName', return_value=(file_path, '')), \
            patch(f'{mod}.QMessageBox') as mock_box:
        page._on_browse_file()
    return mock_box


def test_browse_accepts_search_project_without_warning(review_page):
    """An ADIAT_Search_*.xml project is accepted silently (no name warning)."""
    path = 'C:/results/output/ADIAT_Search_input_20260715_003004.xml'
    mock_box = _browse_returning(review_page, path)

    mock_box.warning.assert_not_called()
    stored = review_page.wizard_data['review_file_path']
    assert stored and os.path.basename(stored) == os.path.basename(path)


def test_browse_accepts_data_result_without_warning(review_page):
    """A single-run ADIAT_Data.xml result is still accepted silently."""
    path = 'C:/results/output/ADIAT_Data.xml'
    mock_box = _browse_returning(review_page, path)

    mock_box.warning.assert_not_called()
    stored = review_page.wizard_data['review_file_path']
    assert stored and os.path.basename(stored) == os.path.basename(path)


def test_browse_warns_on_unrelated_file(review_page):
    """A file that is neither result nor project still triggers the warning."""
    path = 'C:/results/output/something_else.xml'
    mod = 'core.controllers.images.guidePages.ReviewOrNewPage'
    with patch(f'{mod}.QFileDialog.getOpenFileName', return_value=(path, '')), \
            patch(f'{mod}.QMessageBox') as mock_box:
        # Simulate the user declining to continue with the odd file.
        mock_box.warning.return_value = mock_box.No
        review_page._on_browse_file()

    mock_box.warning.assert_called_once()
