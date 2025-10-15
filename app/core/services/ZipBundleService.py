import zipfile
import os


class ZipBundleService:
    """Service to generate a KML file with points representing locations where images with areas of interest were taken."""

    def __init__(self):
        """
        Initialize the KMLService, creating a new KML document.
        """

    def generate_zip_file(self, file_paths, output_path):
        with zipfile.ZipFile(output_path, 'w') as zipf:
            for img_path in file_paths:
                # Check if the file exists before adding
                if os.path.exists(img_path):
                    zipf.write(img_path, os.path.basename(img_path))
                else:
                    print(f"File not found: {img_path}")

    def generate_zip_from_directory(self, directory_path, output_path):
        """
        Create a zip archive from a directory, preserving subdirectory structure.

        Args:
            directory_path (str): Root directory to archive
            output_path (str): Destination .zip path
        """
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(directory_path):
                for name in files:
                    src = os.path.join(root, name)
                    # make arcname relative to directory_path
                    arcname = os.path.relpath(src, directory_path)
                    zipf.write(src, arcname)