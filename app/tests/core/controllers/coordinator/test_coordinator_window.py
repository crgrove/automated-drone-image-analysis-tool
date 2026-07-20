"""
Tests for CoordinatorWindow.load_project_file.

Covers opening a Search Coordinator project directly from a known path (the
path a batch run produces), without going through the file-picker dialog.
"""

import pytest
from unittest.mock import patch

from core.controllers.coordinator.CoordinatorWindow import CoordinatorWindow


_SEARCH_PROJECT_XML = (
    '<?xml version="1.0"?><search_project>'
    '<metadata><name>Batch Run</name><created_by>Tester</created_by></metadata>'
    '<batches/><consolidated_aois/></search_project>'
)

_SEARCH_PROJECT_WITH_BATCH_XML = (
    '<?xml version="1.0"?><search_project>'
    '<metadata><name>Batch Run</name><created_by>Tester</created_by></metadata>'
    '<batches><batch>'
    '<batch_id>batch_001</batch_id>'
    '<original_xml_path>C:/results/batch_001/ADIAT_Data.xml</original_xml_path>'
    '<algorithm>ColorRange</algorithm>'
    '<image_count>15</image_count>'
    '<reviews/>'
    '</batch></batches><consolidated_aois/></search_project>'
)


@pytest.fixture
def coordinator_window(qtbot):
    window = CoordinatorWindow('Light')
    qtbot.addWidget(window)
    return window


def test_load_project_file_success(coordinator_window, tmp_path):
    """A valid project path loads and enables project controls without dialogs."""
    project = tmp_path / 'ADIAT_Search_Batch.xml'
    project.write_text(_SEARCH_PROJECT_XML, encoding='utf-8')

    with patch('core.controllers.coordinator.CoordinatorWindow.QMessageBox') as mock_box:
        result = coordinator_window.load_project_file(str(project))

    assert result is True
    assert coordinator_window.project_path == str(project)
    assert coordinator_window.save_project_btn.isEnabled()
    assert coordinator_window.add_batch_btn.isEnabled()
    # Success is silent; no critical/information dialog should be raised here.
    mock_box.critical.assert_not_called()


def test_load_project_file_missing_path(coordinator_window, tmp_path):
    """A missing project path reports an error and does not enable controls."""
    missing = str(tmp_path / 'does_not_exist.xml')

    with patch('core.controllers.coordinator.CoordinatorWindow.QMessageBox') as mock_box:
        result = coordinator_window.load_project_file(missing)

    assert result is False
    assert coordinator_window.project_path is None
    assert not coordinator_window.save_project_btn.isEnabled()
    mock_box.critical.assert_called_once()


def test_review_button_disabled_until_project_loaded(coordinator_window, tmp_path):
    """The Review Selected Batch button is enabled only once a project loads."""
    assert not coordinator_window.review_batch_btn.isEnabled()

    project = tmp_path / 'ADIAT_Search_Batch.xml'
    project.write_text(_SEARCH_PROJECT_WITH_BATCH_XML, encoding='utf-8')
    with patch('core.controllers.coordinator.CoordinatorWindow.QMessageBox'):
        coordinator_window.load_project_file(str(project))

    assert coordinator_window.review_batch_btn.isEnabled()


def test_review_selected_batch_opens_viewer(coordinator_window, tmp_path):
    """Clicking Review with a row selected opens that batch in the Viewer."""
    project = tmp_path / 'ADIAT_Search_Batch.xml'
    project.write_text(_SEARCH_PROJECT_WITH_BATCH_XML, encoding='utf-8')
    with patch('core.controllers.coordinator.CoordinatorWindow.QMessageBox'):
        coordinator_window.load_project_file(str(project))

    assert coordinator_window.batch_table.rowCount() == 1
    coordinator_window.batch_table.selectRow(0)

    with patch.object(coordinator_window, '_open_batch_in_viewer') as open_viewer:
        coordinator_window._review_selected_batch()

    open_viewer.assert_called_once_with(0, 0)


def test_review_selected_batch_no_selection_warns(coordinator_window):
    """Clicking Review with no row selected warns and opens nothing."""
    with patch('core.controllers.coordinator.CoordinatorWindow.QMessageBox') as mock_box, \
            patch.object(coordinator_window, '_open_batch_in_viewer') as open_viewer:
        coordinator_window._review_selected_batch()

    mock_box.information.assert_called_once()
    open_viewer.assert_not_called()
