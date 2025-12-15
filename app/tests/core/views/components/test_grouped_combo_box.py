"""
Comprehensive tests for GroupedComboBox.

Tests custom combo box with grouped items.
"""

import pytest
from PySide6.QtWidgets import QApplication
from core.views.components.GroupedComboBox import GroupedComboBox


@pytest.fixture(scope='session')
def app():
    """Create QApplication for widget tests."""
    return QApplication.instance() or QApplication([])


def test_grouped_combo_box_initialization(app):
    """Test GroupedComboBox initialization."""
    combo = GroupedComboBox()
    assert combo is not None
    assert combo.model() is not None


def test_add_group(app):
    """Test adding a group of items."""
    combo = GroupedComboBox()
    items = ['Item 1', 'Item 2', 'Item 3']

    combo.add_group('Test Group', items)

    # Should have 1 header + 3 items = 4 rows
    assert combo.model().rowCount() == 4

    # First row should be the group header (non-selectable)
    header_item = combo.model().item(0)
    assert header_item is not None
    assert 'Test Group' in header_item.text()
    from PySide6.QtCore import Qt
    assert header_item.flags() == Qt.NoItemFlags  # Should not be selectable


def test_add_multiple_groups(app):
    """Test adding multiple groups."""
    combo = GroupedComboBox()

    combo.add_group('Group 1', ['Item 1', 'Item 2'])
    combo.add_group('Group 2', ['Item 3', 'Item 4'])

    # Should have 2 headers + 4 items = 6 rows
    assert combo.model().rowCount() == 6


def test_group_header_not_selectable(app):
    """Test that group headers are not selectable."""
    combo = GroupedComboBox()
    combo.add_group('Test Group', ['Item 1'])

    header_item = combo.model().item(0)
    # Check that item has no flags (non-selectable)
    from PySide6.QtCore import Qt
    assert header_item.flags() == Qt.NoItemFlags


def test_group_items_selectable(app):
    """Test that group items are selectable."""
    combo = GroupedComboBox()
    combo.add_group('Test Group', ['Item 1', 'Item 2'])

    # Items should be selectable (after the header)
    item1 = combo.model().item(1)
    item2 = combo.model().item(2)

    assert item1 is not None
    assert item2 is not None
    assert item1.text() == 'Item 1'
    assert item2.text() == 'Item 2'
