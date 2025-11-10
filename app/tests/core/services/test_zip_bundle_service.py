import pytest
import zipfile
import os
from unittest.mock import patch, MagicMock
from core.services.ZipBundleService import ZipBundleService


@pytest.fixture
def zip_service():
    return ZipBundleService()


@pytest.fixture
def example_file_paths():
    return ["app/tests/data/rgb/input/DJI_0082.JPG", "app/tests/data/rgb/input/DJI_0083.JPG"]


@pytest.fixture
def example_output_path():
    return "app/tests/data/output.zip"


def test_generate_zip_file(zip_service, example_file_paths, example_output_path):
    with patch("zipfile.ZipFile") as mock_zipfile, patch("os.path.exists", side_effect=lambda x: x in example_file_paths):
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance

        zip_service.generate_zip_file(example_file_paths, example_output_path)

        mock_zipfile.assert_called_once_with(example_output_path, 'w')
        assert mock_zip_instance.write.call_count == len(example_file_paths)
        for file_path in example_file_paths:
            mock_zip_instance.write.assert_any_call(file_path, os.path.basename(file_path))


def test_generate_zip_file_with_missing_files(zip_service, example_file_paths, example_output_path):
    with patch("zipfile.ZipFile") as mock_zipfile, patch("os.path.exists", side_effect=lambda x: x == example_file_paths[0]):
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance

        zip_service.generate_zip_file(example_file_paths, example_output_path)

        mock_zipfile.assert_called_once_with(example_output_path, 'w')
        mock_zip_instance.write.assert_called_once_with(example_file_paths[0], os.path.basename(example_file_paths[0]))
