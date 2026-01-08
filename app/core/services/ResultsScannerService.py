"""ResultsScannerService - Service for scanning folders for ADIAT results."""

import os
from dataclasses import dataclass
from typing import List, Optional, Tuple, Callable

from core.services.XmlService import XmlService
from core.services.LoggerService import LoggerService
from helpers.LocationInfo import LocationInfo
from helpers.MetaDataHelper import MetaDataHelper


@dataclass
class ResultsScanResult:
    """Data class representing a found results folder."""
    xml_path: str                    # Full path to ADIAT_DATA.XML
    folder_name: str                 # Name of containing folder
    algorithm: str                   # Algorithm name from settings
    image_count: int                 # Number of images with AOIs
    aoi_count: int                   # Total number of AOIs
    missing_images: int              # Count of images that cannot be found
    first_image_path: Optional[str]  # Path to first available image (for GPS)
    gps_coordinates: Optional[Tuple[float, float]]  # (lat, lon) or None


class ResultsScannerService:
    """Service for scanning folders recursively for ADIAT result files."""

    XML_FILENAME = "ADIAT_DATA.XML"  # Case-insensitive search pattern

    def __init__(self):
        self.logger = LoggerService()

    def count_directories(self, root_folder: str) -> int:
        """
        Count the total number of directories to scan.

        Args:
            root_folder: Path to the root folder

        Returns:
            Total number of directories
        """
        count = 0
        for _, dirnames, _ in os.walk(root_folder):
            count += 1 + len(dirnames)
        return max(count, 1)

    def scan_folder(self, root_folder: str,
                    progress_callback: Optional[Callable[[int, int, str], None]] = None) -> List[ResultsScanResult]:
        """
        Recursively scan a folder for ADIAT_DATA.XML files.

        Args:
            root_folder: Path to the root folder to scan
            progress_callback: Optional callback(current, total, current_dir) for progress updates

        Returns:
            List of ResultsScanResult objects
        """
        results = []

        # Count directories first for progress tracking
        total_dirs = self.count_directories(root_folder)
        current_dir_num = 0

        for dirpath, dirnames, filenames in os.walk(root_folder):
            current_dir_num += 1

            # Report progress
            if progress_callback:
                progress_callback(current_dir_num, total_dirs, dirpath)

            for filename in filenames:
                if filename.upper() == self.XML_FILENAME.upper():
                    xml_path = os.path.join(dirpath, filename)
                    try:
                        result = self._parse_result_file(xml_path)
                        if result:
                            results.append(result)
                    except Exception as e:
                        self.logger.error(f"Error parsing {xml_path}: {e}")

        return results

    def _parse_result_file(self, xml_path: str) -> Optional[ResultsScanResult]:
        """
        Parse a single ADIAT_DATA.XML file and extract metadata.

        Args:
            xml_path: Full path to the XML file

        Returns:
            ResultsScanResult or None if parsing fails
        """
        try:
            xml_service = XmlService(xml_path)
            settings, image_count = xml_service.get_settings()
            images = xml_service.get_images()

            # Extract algorithm name
            algorithm = settings.get('algorithm', 'Unknown')

            # Count AOIs and track missing images
            aoi_count = 0
            missing_images = 0
            first_available_image = None
            available_images = []  # Track all available images for GPS fallback

            for image in images:
                aoi_count += len(image.get('areas_of_interest', []))

                # Check if image file exists
                image_path = image.get('path', '')
                if image_path and os.path.exists(image_path):
                    available_images.append(image_path)
                    if first_available_image is None:
                        first_available_image = image_path
                else:
                    missing_images += 1

            # Get GPS coordinates - try multiple images if first one fails
            gps_coords = None
            for img_path in available_images:
                gps_coords = self._get_image_gps(img_path)
                if gps_coords:
                    break  # Found GPS, stop searching

            # Get folder name - use parent of ADIAT_Results if applicable
            xml_dir = os.path.dirname(xml_path)
            folder_name = os.path.basename(xml_dir)

            # If the XML is in an ADIAT_Results folder, use the parent folder name instead
            if folder_name.upper() == "ADIAT_RESULTS":
                parent_dir = os.path.dirname(xml_dir)
                if parent_dir:
                    folder_name = os.path.basename(parent_dir)

            return ResultsScanResult(
                xml_path=xml_path,
                folder_name=folder_name,
                algorithm=algorithm,
                image_count=image_count,
                aoi_count=aoi_count,
                missing_images=missing_images,
                first_image_path=first_available_image,
                gps_coordinates=gps_coords
            )

        except Exception as e:
            self.logger.error(f"Failed to parse result file {xml_path}: {e}")
            return None

    def _get_image_gps(self, image_path: str) -> Optional[Tuple[float, float]]:
        """
        Extract GPS coordinates from an image.

        Args:
            image_path: Path to the image file

        Returns:
            Tuple of (latitude, longitude) or None
        """
        try:
            # First try using MetaDataHelper to get EXIF data (works with more formats)
            exif_data = MetaDataHelper.get_exif_data_piexif(image_path)
            if exif_data:
                gps_info = LocationInfo.get_gps(exif_data=exif_data)
                if gps_info and 'latitude' in gps_info and 'longitude' in gps_info:
                    return (gps_info['latitude'], gps_info['longitude'])

            # Fallback to direct path method (works with JPEG)
            gps_info = LocationInfo.get_gps(full_path=image_path)
            if gps_info and 'latitude' in gps_info and 'longitude' in gps_info:
                return (gps_info['latitude'], gps_info['longitude'])
        except Exception as e:
            self.logger.error(f"Failed to get GPS from {image_path}: {e}")
        return None
