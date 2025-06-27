from PIL import Image
from os import path
import exiftool
import piexif
import json
import numpy as np
import platform
import re
import struct
import xml.etree.ElementTree as ET

from helpers.PickleHelper import PickleHelper

class MetaDataHelper:
    """Helper class for managing EXIF, XMP, and thermal metadata of image files."""

    @staticmethod
    def _get_exif_tool_path():
        """
        Returns the absolute path to the ExifTool binary for the current platform.

        Returns:
            str: Path to ExifTool executable.
        """
        if platform.system() == 'Windows':
            return path.abspath(path.join(path.dirname(path.dirname(__file__)), 'external/exiftool.exe'))
        elif platform.system() == 'Darwin':
            return path.abspath(path.join(path.dirname(path.dirname(__file__)), 'external/exiftool'))

    @staticmethod
    def _transfer_exif_piexif(origin_file, destination_file):
        """
        Transfers EXIF metadata using piexif.

        Args:
            origin_file (str): Source image path.
            destination_file (str): Destination image path.
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
        Transfers EXIF metadata using PIL as a fallback.

        Args:
            origin_file (str): Source image path.
            destination_file (str): Destination image path.
        """
        image = Image.open(origin_file)
        if 'exif' in image.info:
            exif = image.info['exif']
            image_new = Image.open(destination_file)
            image_new.save(destination_file, 'JPEG', exif=exif)

    @staticmethod
    def transfer_exif_exiftool(origin_file, destination_file):
        """
        Transfers EXIF metadata using ExifTool.

        Args:
            origin_file (str): Source image path.
            destination_file (str): Destination image path.
        """
        with exiftool.ExifTool(MetaDataHelper._get_exif_tool_path()) as et:
            et.execute("-tagsfromfile", origin_file, "-exif", destination_file, "-overwrite_original")
            et.terminate()

    @staticmethod
    def transfer_xmp_exiftool(origin_file, destination_file):
        """
        Transfers XMP metadata using ExifTool.

        Args:
            origin_file (str): Source image path.
            destination_file (str): Destination image path.
        """
        with exiftool.ExifTool(MetaDataHelper._get_exif_tool_path()) as et:
            et.execute("-tagsfromfile", origin_file, "-xmp", destination_file, "-overwrite_original")
            et.terminate()

    @staticmethod
    def transfer_exif(origin_file, destination_file):
        """
        Attempts to transfer EXIF metadata using piexif and falls back to PIL.

        Args:
            origin_file (str): Source image path.
            destination_file (str): Destination image path.
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
        Transfers both EXIF and XMP metadata using ExifTool.

        Args:
            origin_file (str): Source image path.
            destination_file (str): Destination image path.
        """
        with exiftool.ExifTool(MetaDataHelper._get_exif_tool_path()) as et:
            et.execute("-tagsfromfile", origin_file, destination_file, "-overwrite_original", "--thumbnailimage")
            et.terminate()

    @staticmethod
    def transfer_temperature_data(data, destination_file):
        """
        Stores temperature data in the XMP Notes field as JSON.

        Args:
            data (numpy.ndarray): Temperature matrix.
            destination_file (str): Destination image path.
        """
        json_data = json.dumps(data.tolist())
        with exiftool.ExifToolHelper(executable=MetaDataHelper._get_exif_tool_path()) as et:
            et.set_tags([destination_file], tags={"Notes": json_data}, params=["-P", "-overwrite_original"])
            et.terminate()

    @staticmethod
    def get_raw_temperature_data(file_path):
        """
        Retrieves raw byte content of embedded thermal image.

        Args:
            file_path (str): Image path.

        Returns:
            bytes: Byte data of raw thermal image.
        """
        with exiftool.ExifTool(MetaDataHelper._get_exif_tool_path()) as et:
            thermal_img_bytes = et.execute("-b", "-RawThermalImage", file_path, raw_bytes=True)
            et.terminate()
        return thermal_img_bytes

    @staticmethod
    def get_temperature_data(file_path):
        """
        Extracts temperature data from the XMP Notes field.

        Args:
            file_path (str): Path to the image.

        Returns:
            numpy.ndarray: Temperature matrix.
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
        Reads all metadata from an image using ExifTool.

        Args:
            file_path (str): Image path.

        Returns:
            dict: Metadata dictionary.
        """
        with exiftool.ExifToolHelper(executable=MetaDataHelper._get_exif_tool_path()) as et:
            metadata = et.get_metadata([file_path])[0]
            et.terminate()
        return metadata

    @staticmethod
    def get_exif_data_piexif(file_path):
        """
        Extracts EXIF metadata using piexif.

        Args:
            file_path (str): Image path.

        Returns:
            dict: EXIF tag data.
        """
        return piexif.load(file_path)

    @staticmethod
    def set_tags_exiftool(file_path, tags):
        """
        Sets EXIF/XMP tags using ExifTool.

        Args:
            file_path (str): Path to image.
            tags (dict): Dictionary of tag:value to apply.
        """
        with exiftool.ExifToolHelper(executable=MetaDataHelper._get_exif_tool_path()) as et:
            et.set_tags([file_path], tags=tags, params=["-overwrite_original"])
            et.terminate()

    @staticmethod
    def add_gps_data(file_path, lat, lng, alt, rel_alt=0):
        """
        Adds GPS metadata to an image.

        Args:
            file_path (str): Image path.
            lat (float): Latitude in decimal degrees.
            lng (float): Longitude in decimal degrees.
            alt (float): Altitude in meters.
            rel_alt (float, optional): Relative altitude. Defaults to 0.
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
        Converts and embeds GPS coordinates into EXIF GPS tags.

        Args:
            exif_dict (dict): Mutable EXIF dictionary.
            lat (float): Latitude.
            lng (float): Longitude.
            alt (float): Altitude.
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
        Retrieves XMP metadata as raw XML or parsed dict.

        Args:
            file_path (str): Path to image file.
            parse (bool): Whether to parse XML into dict.

        Returns:
            str or dict or None: Raw XML string or parsed dictionary, or None if XMP not found.
        """
        try:
            with open(file_path, 'rb') as f:
                data = f.read()

            start_tag = b'<?xpacket begin'
            end_tag = b'<?xpacket end'

            start_idx = data.find(start_tag)
            if start_idx == -1:
                return None

            end_idx = data.find(end_tag, start_idx)
            if end_idx == -1:
                return None

            end_close_idx = data.find(b'>', end_idx) + 1
            if end_close_idx == 0:
                return None

            xmp_data = data[start_idx:end_close_idx]
            xmp_decode = xmp_data.decode('utf-8')

            return MetaDataHelper._parse_xmp_xml(xmp_decode) if parse else xmp_decode
        except Exception:
            return None

    @staticmethod
    def extract_xmp(image_path):
        """
        Extracts raw XMP block from a JPEG.

        Args:
            image_path (str): Path to image.

        Returns:
            bytes or None: XMP segment if found, otherwise None.
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
                continue

            xmp_marker = b"http://ns.adobe.com/xap/1.0/"
            if xmp_marker in img_data[app1_start:app1_end]:
                return img_data[app1_start:app1_end]

        return None

    @staticmethod
    def get_drone_make(exif_data):
        """
        Extracts the drone make from EXIF.

        Args:
            exif_data (dict): Parsed EXIF data.

        Returns:
            str or None: Drone make string.
        """
        make = exif_data["0th"].get(piexif.ImageIFD.Make)
        return make.decode('utf-8').strip().rstrip("\x00") if make else None

    @staticmethod
    def get_xmp_attribute(attribute, make, xmp_data):
        """
        Looks up and retrieves a specific XMP field based on attribute mapping.

        Args:
            attribute (str): Logical attribute name (e.g., "Flight Yaw").
            make (str): Drone manufacturer (e.g., "DJI").
            xmp_data (dict): Parsed XMP dictionary.

        Returns:
            str or None: Attribute value, if available.
        """
        xmp_df = PickleHelper.get_xmp_mapping()
        try:
            key = xmp_df.loc[xmp_df['Attribute'] == attribute, make].iloc[0]
            return xmp_data[key]
        except (KeyError, IndexError):
            return None

    @staticmethod
    def embed_xmp(xmp_segment, destination_file):
        """
        Embeds a raw XMP segment into a JPEG file.

        Args:
            xmp_segment (bytes): Full XMP APP1 segment.
            destination_file (str): Path to target JPEG.

        Returns:
            bool: True if successful, False otherwise.
        """
        if xmp_segment is None:
            return False

        with open(destination_file, "rb") as img_file:
            img_data = img_file.read()

        exif_marker = img_data.find(b"\xFF\xE1")
        insert_pos = 2  # default
        if exif_marker != -1:
            segment_length = struct.unpack(">H", img_data[exif_marker + 2:exif_marker + 4])[0]
            insert_pos = exif_marker + 2 + segment_length

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

        return True

    @staticmethod
    def _parse_xmp_xml(xmp_xml):
        """
        Parses XMP XML into a flat dictionary.

        Args:
            xmp_xml (str): Raw XMP XML string.

        Returns:
            dict: Flattened key-value pairs from XMP.
        """
        root = ET.fromstring(xmp_xml)
        xmp_dict = {}

        def clean_key(key):
            key = re.sub(r'^RDF:Description:?', '', key)
            key = re.sub(r'\{.*?\}', '', key)
            return key.lstrip(':')

        def parse_element(element, parent_key=""):
            for child in element:
                tag = child.tag.split("}", 1)[1] if "}" in child.tag else child.tag
                key = f"{parent_key}:{tag}" if parent_key else tag
                key = clean_key(key)

                if child.attrib:
                    for attr, value in child.attrib.items():
                        attr_key = clean_key(f"{key}:{attr}")
                        xmp_dict[attr_key] = value

                if child.text and child.text.strip():
                    xmp_dict[key] = child.text.strip()

                if list(child):
                    parse_element(child, key)

        parse_element(root)
        return xmp_dict
