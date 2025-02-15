from PIL import Image
from os import path
import exiftool
import piexif
import json
import numpy as np
import platform


class MetaDataHelper:
    """Helper class for managing EXIF and metadata of image files."""

    @staticmethod
    def _get_exif_tool_path():
        """
        Return the path to the Exiftool based on the system platform.

        Returns:
            str: Absolute path to Exiftool executable.
        """
        if platform.system() == 'Windows':
            return path.abspath(path.join(path.dirname(path.dirname(__file__)), 'external/exiftool.exe'))
        elif platform.system() == 'Darwin':
            return path.abspath(path.join(path.dirname(path.dirname(__file__)), 'external/exiftool'))

    @staticmethod
    def transfer_exif_piexif(originFile, destinationFile):
        """
        Copy the EXIF information from one image file to another using piexif.

        Args:
            originFile (str): Path to the source file.
            destinationFile (str): Path to the destination file.
        """
        try:
            piexif.transplant(originFile, destinationFile)
        except piexif._exceptions.InvalidImageDataError:
            MetaDataHelper.transfer_exif_pil(originFile, destinationFile)
        except ValueError:
            return

    @staticmethod
    def transfer_exif_pil(originFile, destinationFile):
        """
        Copy the EXIF information from one image file to another using PIL.

        Args:
            originFile (str): Path to the source file.
            destinationFile (str): Path to the destination file.
        """
        image = Image.open(originFile)
        if 'exif' in image.info:
            exif = image.info['exif']
            image_new = Image.open(destinationFile)
            image_new.save(destinationFile, 'JPEG', exif=exif)

    @staticmethod
    def transfer_exif_exiftool(originFile, destinationFile):
        """
        Copy the EXIF information from one image file to another using Exiftool.

        Args:
            originFile (str): Path to the source file.
            destinationFile (str): Path to the destination file.
        """
        with exiftool.ExifTool(MetaDataHelper._get_exif_tool_path()) as et:
            et.execute("-tagsfromfile", originFile, "-exif", destinationFile, "-overwrite_original")
            et.terminate()

    @staticmethod
    def transfer_xmp_exiftool(originFile, destinationFile):
        """
        Copy the XMP information from one image file to another using Exiftool.

        Args:
            originFile (str): Path to the source file.
            destinationFile (str): Path to the destination file.
        """
        with exiftool.ExifTool(MetaDataHelper._get_exif_tool_path()) as et:
            et.execute("-tagsfromfile", originFile, "-xmp", destinationFile, "-overwrite_original")
            et.terminate()

    @staticmethod
    def transfer_all(originFile, destinationFile):
        """
        Copy the EXIF and XMP information from one image file to another using Exiftool.

        Args:
            originFile (str): Path to the source file.
            destinationFile (str): Path to the destination file.
        """
        with exiftool.ExifTool(MetaDataHelper._get_exif_tool_path()) as et:
            et.execute("-tagsfromfile", originFile, destinationFile, "-overwrite_original", "--thumbnailimage")
            et.terminate()

    @staticmethod
    def transfer_temperature_data(data, destinationFile):
        """
        Copy temperature data from an image to the Notes field on another image.

        Args:
            data (numpy.ndarray): Temperature data array.
            destinationFile (str): Path to the destination file.
        """
        json_data = json.dumps(data.tolist())
        with exiftool.ExifToolHelper(executable=MetaDataHelper._get_exif_tool_path()) as et:
            et.set_tags(
                [destinationFile],
                tags={"Notes": json_data},
                params=["-P", "-overwrite_original"]
            )
            et.terminate()

    @staticmethod
    def get_raw_temperature_data(file_path):
        """
        Retrieve raw temperature data as bytes from an image.

        Args:
            file_path (str): Path to the image.

        Returns:
            bytes: Bytes representing temperature data.
        """
        with exiftool.ExifTool(MetaDataHelper._get_exif_tool_path()) as et:
            thermal_img_bytes = et.execute("-b", "-RawThermalImage", file_path, raw_bytes=True)
            et.terminate()
        return thermal_img_bytes

    @staticmethod
    def get_temperature_data(file_path):
        """
        Retrieve temperature data as a numpy array from the Notes field of an image.

        Args:
            file_path (str): Path to the image.

        Returns:
            numpy.ndarray: Array of temperature data.
        """
        with exiftool.ExifToolHelper(executable=MetaDataHelper._get_exif_tool_path()) as et:
            json_data = et.get_tags([file_path], tags=['Notes'])[0]['XMP:Notes']
            data = json.loads(json_data)
            temperature_c = np.asarray(data)
            et.terminate()
        return temperature_c

    @staticmethod
    def get_meta_data(file_path):
        """
        Retrieve metadata from an image file.

        Args:
            file_path (str): Path to the image.

        Returns:
            dict: Key-value pairs of metadata.
        """
        with exiftool.ExifToolHelper(executable=MetaDataHelper._get_exif_tool_path()) as et:
            metadata = et.get_metadata([file_path])[0]
            et.terminate()
        return metadata

    @staticmethod
    def set_tags(file_path, tags):
        """
        Update metadata with provided tags.

        Args:
            file_path (str): Path to the image.
            tags (dict): Dictionary of tags and values to be set.
        """
        with exiftool.ExifToolHelper(executable=MetaDataHelper._get_exif_tool_path()) as et:
            et.set_tags([file_path], tags=tags, params=["-overwrite_original"])
            et.terminate()

    @staticmethod
    def add_gps_data(file_path, lat, lng, alt):
        """
        Add GPS data to an image file.

        Args:
            file_path (str): Path to the image.
            lat (float): Decimal latitude.
            lng (float): Decimal longitude.
            alt (float): Altitude in meters.
        """
        img = Image.open(file_path)
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}, "thumbnail": None}
        if "exif" in img.info:
            exif_dict = piexif.load(img.info["exif"])

        MetaDataHelper._set_gps_location(exif_dict, lat, lng, alt)
        exif_bytes = piexif.dump(exif_dict)
        img.save(file_path, "jpeg", exif=exif_bytes)

    @staticmethod
    def _set_gps_location(exif_dict, lat, lng, alt):
        """
        Convert lat/lng to degrees, minutes, and seconds format and store in EXIF GPS fields.

        Args:
            exif_dict (dict): EXIF data.
            lat (float): Decimal latitude.
            lng (float): Decimal longitude.
            alt (float): Altitude in meters.
        """
        def to_deg(value, ref):
            if value < 0:
                value = -value
                ref = ref[1]
            else:
                ref = ref[0]

            deg = int(value)
            min = int((value - deg) * 60)
            sec = int((value - deg - min / 60) * 3600 * 10000)

            return ((deg, 1), (min, 1), (sec, 10000)), ref

        lat_deg, lat_ref = to_deg(lat, ["N", "S"])
        lng_deg, lng_ref = to_deg(lng, ["E", "W"])

        exif_dict["GPS"] = {
            piexif.GPSIFD.GPSLatitudeRef: lat_ref,
            piexif.GPSIFD.GPSLatitude: lat_deg,
            piexif.GPSIFD.GPSLongitudeRef: lng_ref,
            piexif.GPSIFD.GPSLongitude: lng_deg,
            piexif.GPSIFD.GPSAltitudeRef: 0 if alt >= 0 else 1,
            piexif.GPSIFD.GPSAltitude: (abs(int(alt * 100)), 100),
        }

    @staticmethod
    def get_xmp_data(file_path):
        """
        Extract XMP data from an image file if present.
        
        Args:
            file_path (str): Path to the image file.
            
        Returns:
            str: XMP data if found, None otherwise.
        """
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                
            # Look for XMP header and footer
            start_tag = b'<?xpacket begin'
            end_tag = b'<?xpacket end'
            
            start_idx = data.find(start_tag)
            if start_idx == -1:
                return None
                
            end_idx = data.find(end_tag, start_idx)
            if end_idx == -1:
                return None
                
            # Include the end tag in the extracted data
            xmp_data = data[start_idx:end_idx + len(end_tag)]
            return xmp_data.decode('utf-8')
        except Exception:
            return None

    @staticmethod
    def set_xmp_data(file_path, xmp_data):
        """
        Add XMP data to an image file.
        
        Args:
            file_path (str): Path to the image file.
            xmp_data (str): XMP data to insert.
        """
        if not xmp_data:
            return
            
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                
            # Find the SOI and APP1 markers
            soi_marker = b'\xFF\xD8'
            app1_marker = b'\xFF\xE1'
            
            if not data.startswith(soi_marker):
                return
                
            # Insert XMP data after SOI marker
            xmp_length = len(xmp_data.encode('utf-8')) + 2  # +2 for length bytes
            app1_header = app1_marker + xmp_length.to_bytes(2, 'big')
            new_data = soi_marker + app1_header + xmp_data.encode('utf-8') + data[2:]
            
            with open(file_path, 'wb') as f:
                f.write(new_data)
        except Exception:
            return
