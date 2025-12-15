"""
Comprehensive tests for ColorListService.

Tests predefined color loading from pickle and CSV files.
"""

import pytest
import tempfile
import pickle
import csv
import os
from pathlib import Path
from unittest.mock import patch
from core.services.color.ColorListService import get_predefined_colors


def test_get_predefined_colors_from_pickle():
    """Test loading colors from pickle file."""
    test_colors = [
        {'name': 'Red', 'rgb': (255, 0, 0), 'uses': 'Fire'},
        {'name': 'Blue', 'rgb': (0, 0, 255), 'uses': 'Water'}
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create pickle file
        pkl_path = Path(tmpdir) / 'colors.pkl'
        with open(pkl_path, 'wb') as f:
            pickle.dump(test_colors, f)

        # Mock the path functions to return our test paths
        with patch('core.services.color.ColorListService._pkl_path', return_value=pkl_path):
            colors = get_predefined_colors()

            assert len(colors) == 2
            assert colors[0]['name'] == 'Red'
            assert colors[1]['name'] == 'Blue'


def test_get_predefined_colors_from_csv():
    """Test loading colors from CSV file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create CSV file
        csv_path = Path(tmpdir) / 'colors.csv'
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'r', 'g', 'b', 'uses'])
            writer.writeheader()
            writer.writerow({'name': 'Red', 'r': '255', 'g': '0', 'b': '0', 'uses': 'Fire'})
            writer.writerow({'name': 'Blue', 'r': '0', 'g': '0', 'b': '255', 'uses': 'Water'})

        nonexistent_pkl = Path(tmpdir) / 'nonexistent.pkl'
        with patch('core.services.color.ColorListService._pkl_path', return_value=nonexistent_pkl), \
                patch('core.services.color.ColorListService._csv_path', return_value=csv_path):
            colors = get_predefined_colors()

            assert len(colors) == 2
            assert colors[0]['name'] == 'Red'
            assert colors[0]['rgb'] == (255, 0, 0)
            assert colors[1]['name'] == 'Blue'
            assert colors[1]['rgb'] == (0, 0, 255)


def test_get_predefined_colors_empty():
    """Test when no color files exist."""
    nonexistent_pkl = Path('/nonexistent.pkl')
    nonexistent_csv = Path('/nonexistent.csv')
    with patch('core.services.color.ColorListService._pkl_path', return_value=nonexistent_pkl), \
            patch('core.services.color.ColorListService._csv_path', return_value=nonexistent_csv):
        colors = get_predefined_colors()

        assert colors == []


def test_get_predefined_colors_csv_invalid_row():
    """Test CSV loading with invalid rows (should skip them)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / 'colors.csv'
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'r', 'g', 'b', 'uses'])
            writer.writeheader()
            writer.writerow({'name': 'Red', 'r': '255', 'g': '0', 'b': '0', 'uses': 'Fire'})
            writer.writerow({'name': 'Invalid', 'r': 'not_a_number', 'g': '0', 'b': '0', 'uses': ''})  # Invalid
            writer.writerow({'name': 'Blue', 'r': '0', 'g': '0', 'b': '255', 'uses': 'Water'})

        nonexistent_pkl = Path(tmpdir) / 'nonexistent.pkl'
        with patch('core.services.color.ColorListService._pkl_path', return_value=nonexistent_pkl), \
                patch('core.services.color.ColorListService._csv_path', return_value=csv_path):
            colors = get_predefined_colors()

            # Should skip invalid row
            assert len(colors) == 2
            assert colors[0]['name'] == 'Red'
            assert colors[1]['name'] == 'Blue'
