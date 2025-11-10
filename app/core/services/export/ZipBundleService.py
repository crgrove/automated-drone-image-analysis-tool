import zipfile
import os


class ZipBundleService:
    """Service to generate ZIP archive files from file paths or directories.

    Provides functionality to create ZIP archives from lists of files or
    entire directory structures, preserving file organization.
    """

    def __init__(self):
        """Initialize the ZipBundleService."""
        pass

    def generate_zip_file(self, file_paths, output_path):
        """Generate a ZIP file from a list of file paths.

        Creates a ZIP archive containing the specified files. Files are
        added with their basename (filename only) in the archive.

        Args:
            file_paths: List of file paths to include in the ZIP.
            output_path: Path where the ZIP file will be created.
        """
        with zipfile.ZipFile(output_path, 'w') as zipf:
            for img_path in file_paths:
                # Check if the file exists before adding
                if os.path.exists(img_path):
                    zipf.write(img_path, os.path.basename(img_path))
                else:
                    print(f"File not found: {img_path}")

    def generate_zip_from_directory(self, directory_path, output_path):
        """Create a ZIP archive from a directory, preserving subdirectory structure.

        Recursively archives all files in the specified directory, maintaining
        the relative directory structure within the ZIP file.

        Args:
            directory_path: Root directory to archive.
            output_path: Destination ZIP file path.
        """
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(directory_path):
                for name in files:
                    src = os.path.join(root, name)
                    # make arcname relative to directory_path
                    arcname = os.path.relpath(src, directory_path)
                    zipf.write(src, arcname)
