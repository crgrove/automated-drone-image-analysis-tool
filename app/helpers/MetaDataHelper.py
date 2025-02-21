from PIL import Image
from os import path
import exiftool
import piexif
import json
import numpy as np
import platform
import traceback
import re
import struct
import xml.etree.ElementTree as ET


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
    def _transfer_exif_piexif(origin_file, destination_file):
        """
        Copy the EXIF information from one image file to another using piexif.

        Args:
            origin_file (str): Path to the source file.
            destination_file (str): Path to the destination file.
        """
        try:
            piexif.transplant(origin_file, destination_file)
        except piexif._exceptions.InvalidImageDataError:
            MetaDataHelper._transfer_exif_pil(origin_file, destination_file)
        except ValueError:
            return

    @staticmethod
    def _transfer_exif_pil(origin_file, destination_file):
        """
        Copy the EXIF information from one image file to another using PIL.

        Args:
            origin_file (str): Path to the source file.
            destination_file (str): Path to the destination file.
        """
        image = Image.open(origin_file)
        if 'exif' in image.info:
            exif = image.info['exif']
            image_new = Image.open(destination_file)
            image_new.save(destination_file, 'JPEG', exif=exif)

    @staticmethod
    def transfer_exif_exiftool(origin_file, destination_file):
        """
        Copy the EXIF information from one image file to another using Exiftool.

        Args:
            origin_file (str): Path to the source file.
            destination_file (str): Path to the destination file.
        """
        with exiftool.ExifTool(MetaDataHelper._get_exif_tool_path()) as et:
            et.execute("-tagsfromfile", origin_file, "-exif", destination_file, "-overwrite_original")
            et.terminate()

    @staticmethod
    def transfer_xmp_exiftool(origin_file, destination_file):
        """
        Copy the XMP information from one image file to another using Exiftool.

        Args:
            origin_file (str): Path to the source file.
            destination_file (str): Path to the destination file.
        """
        with exiftool.ExifTool(MetaDataHelper._get_exif_tool_path()) as et:
            et.execute("-tagsfromfile", origin_file, "-xmp", destination_file, "-overwrite_original")
            et.terminate()

    @staticmethod
    def transfer_exif(origin_file, destination_file):
        """
        Copy the EXIF information from one image file to another.

        Args:
            origin_file (str): Path to the source file.
            destination_file (str): Path to the destination file.
        """
        try:
            MetaDataHelper._transfer_exif_piexif(origin_file, destination_file)
        except piexif._exceptions.InvalidImageDataError:
            MetaDataHelper._transfer_exif_pil(origin_file, destination_file)

        except ValueError:
            return

    @staticmethod
    def transfer_all_exiftool(origin_file, destination_file):
        """
        Copy the EXIF and XMP information from one image file to another using Exiftool.

        Args:
            origin_file (str): Path to the source file.
            destination_file (str): Path to the destination file.
        """
        with exiftool.ExifTool(MetaDataHelper._get_exif_tool_path()) as et:
            et.execute("-tagsfromfile", origin_file, destination_file, "-overwrite_original", "--thumbnailimage")
            et.terminate()

    @staticmethod
    def transfer_temperature_data(data, destination_file):
        """
        Copy temperature data from an image to the Notes field on another image.

        Args:
            data (numpy.ndarray): Temperature data array.
            destination_file (str): Path to the destination file.
        """
        json_data = json.dumps(data.tolist())
        with exiftool.ExifToolHelper(executable=MetaDataHelper._get_exif_tool_path()) as et:
            et.set_tags(
                [destination_file],
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
    def get_meta_data_exiftool(file_path):
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
    def get_exif_data_piexif(file_path):
        """
        Retrieve EXIF metadata from an image file.

        Args:
            file_path (str): Path to the image.

        Returns:
            dict: Key-value pairs of EXIF data.
        """
        return piexif.load(file_path)

    @staticmethod
    def set_tags_exiftool(file_path, tags):
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
    def add_gps_data(file_path, lat, lng, alt, rel_alt=0):
        """
        Add GPS data to an image file.

        Args:
            file_path (str): Path to the image.
            lat (float): Decimal latitude.
            lng (float): Decimal longitude.
            alt (float): Absolute Altitude in meters.
            rel_alt (float): Relative altitude in meters.
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
    def get_xmp_data(file_path, parse=False):
        """
        Extract XMP data from an image file if present.

        Args:
            file_path (str): Path to the image file.
            parse (boolean): Should the xmp data be parsed and returned as a dictionary

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

            # Find the closing '>' for the end tag
            end_close_idx = data.find(b'>', end_idx) + 1
            if end_close_idx == 0:  # if '>' not found
                return None

            # Include complete end tag in the extracted data
            xmp_data = data[start_idx:end_close_idx]
            xmp_decode = xmp_data.decode('utf-8')

            if parse:
                return MetaDataHelper._parse_xmp_xml(xmp_decode)
            else:
                return xmp_decode
        except Exception:
            return None

    @staticmethod
    def extract_xmp(image_path):
        """Extracts only the XMP metadata from a JPEG file without modifying EXIF data.

        This function scans the `APP1` segments of a JPEG file to locate and 
        extract XMP metadata.

        Args:
            image_path (str): Path to the image file.

        Returns:
            bytes: The raw XMP metadata in binary format, or None if no XMP is found.
        """
        with open(image_path, "rb") as img_file:
            img_data = img_file.read()

        app1_positions = [m.start() for m in re.finditer(b"\xFF\xE1", img_data)]
        if not app1_positions:
            return None

        for app1_start in app1_positions:
            segment_length = struct.unpack(">H", img_data[app1_start + 2:app1_start + 4])[0]
            app1_end = app1_start + 2 + segment_length

            if app1_end > len(img_data) or app1_end < app1_start:
                continue  # Skip corrupt segments

            xmp_marker = b"http://ns.adobe.com/xap/1.0/"
            if xmp_marker in img_data[app1_start:app1_end]:
                return img_data[app1_start:app1_end]

        return None

    @staticmethod
    def embed_xmp(xmp_segment, destination_file):
        """Embeds XMP metadata into a JPEG file while ensuring format integrity.

        This function inserts the XMP metadata at the correct location in the 
        JPEG file, preserving EXIF and ensuring `imghdr.what()` still recognizes it.

        Args:
            xmp_segment (bytes): The XMP metadata segment to embed.
            destination_file (str): Path to the image file where XMP will be inserted.

        Returns:
            bool: True if successful, False if the operation failed.
        """
        if xmp_segment is None:
            return False

        with open(destination_file, "rb") as img_file:
            img_data = img_file.read()

        exif_marker = img_data.find(b"\xFF\xE1")
        if exif_marker != -1:
            segment_length = struct.unpack(">H", img_data[exif_marker + 2:exif_marker + 4])[0]
            insert_pos = exif_marker + 2 + segment_length
        else:
            insert_pos = 2  # Default: insert after SOI marker (FFD8)

        xmp_header = b"http://ns.adobe.com/xap/1.0/\x00"
        xmp_bytes = xmp_segment[len(b"\xFF\xE1") + 2:]

        new_xmp_block = (
            b"\xFF\xE1"
            + struct.pack(">H", len(xmp_header) + len(xmp_bytes) + 2)
            + xmp_header
            + xmp_bytes
        )

        new_data = img_data[:insert_pos] + new_xmp_block + img_data[insert_pos:]

        with open(destination_file, "wb") as f:
            f.write(new_data)

    @staticmethod
    def _parse_xmp_xml(xmp_xml):
        """Parses XMP metadata from XML format into a dictionary.

        This function recursively extracts all nested XMP metadata entries,
        including namespace-prefixed attributes.

        Args:
            xmp_xml (str): The raw XML string containing XMP metadata.

        Returns:
            dict: A dictionary with nested XMP metadata entries as key-value pairs.
        """
        root = ET.fromstring(xmp_xml)
        xmp_dict = {}

        def parse_element(element, parent_key=""):
            """Recursively processes XML elements into a dictionary.

            Args:
                element (xml.etree.ElementTree.Element): The XML element to parse.
                parent_key (str, optional): Prefix for nested keys to maintain hierarchy.

            Returns:
                None
            """
            for child in element:
                tag = child.tag.split("}", 1)[1] if "}" in child.tag else child.tag
                key = f"{parent_key}:{tag}" if parent_key else tag

                if child.attrib:
                    for attr, value in child.attrib.items():
                        attr_key = f"{key}:{attr}"
                        xmp_dict[attr_key] = value

                if child.text and child.text.strip():
                    xmp_dict[key] = child.text.strip()

                if list(child):
                    parse_element(child, key)

        parse_element(root)
        return xmp_dict
