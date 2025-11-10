from PIL import Image
from os import path
import exiftool
import piexif
import hashlib
import platform
import re
import struct
import xml.etree.ElementTree as ET
import sys

from helpers.PickleHelper import PickleHelper

# Constant headers
_XMP_STD_HDR = b"http://ns.adobe.com/xap/1.0/\x00"
_XMP_EXT_HDR = b"http://ns.adobe.com/xmp/extension/\x00"


class MetaDataHelper:
    """Helper class for managing EXIF, XMP, and thermal metadata of image files."""

    @staticmethod
    def _get_exif_tool_path():
        """
        Returns the absolute path to the ExifTool binary for the current platform.

        Returns:
            str: Path to ExifTool executable.
        """
        # Determine the base path based on whether we're running from a PyInstaller bundle
        if getattr(sys, 'frozen', False):
            # Running from a PyInstaller bundle
            app_root = sys._MEIPASS
        else:
            # Running from source code
            app_root = path.dirname(path.dirname(__file__))

        if platform.system() == 'Windows':
            return path.abspath(path.join(app_root, 'external/exiftool.exe'))
        elif platform.system() == 'Darwin':
            return path.abspath(path.join(app_root, 'external/exiftool'))

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
    def get_xmp_data_merged(file_path: str) -> dict:
        """
        Get XMP data using ExifTool first (for bundled exe compatibility),
        falling back to direct file parsing if ExifTool fails.
        """
        # Try using ExifTool first (works better in bundled exe)
        try:
            metadata = MetaDataHelper.get_meta_data_exiftool(file_path)
            if metadata:
                # Extract XMP fields from ExifTool output
                xmp_data = {}

                # Process all metadata fields
                for key, value in metadata.items():
                    # Store original key-value for reference
                    xmp_data[key] = value

                    # Convert ExifTool format to expected XMP format
                    if key.startswith('XMP:'):
                        xmp_key = key[4:]  # Remove "XMP:" prefix
                        xmp_data[xmp_key] = value
                        # Also store with drone-dji namespace if it's a DJI field
                        if any(field in xmp_key for field in ['FlightYaw', 'FlightPitch', 'FlightRoll',
                                                              'GimbalYaw', 'GimbalPitch', 'GimbalRoll',
                                                              'RelativeAltitude', 'AbsoluteAltitude']):
                            xmp_data[f'drone-dji:{xmp_key}'] = value
                    elif key.startswith('XMP-'):
                        # Handle namespaced XMP tags like "XMP-drone-dji:FlightYawDegree"
                        xmp_key = key[4:]  # Remove "XMP-" prefix
                        xmp_data[xmp_key] = value
                        # Also store without namespace for compatibility
                        if ':' in xmp_key:
                            simple_key = xmp_key.split(':')[-1]
                            xmp_data[simple_key] = value
                            # Store with proper drone-dji namespace
                            if 'drone' in xmp_key.lower():
                                namespace_key = xmp_key.replace('drone-dji:', 'drone-dji:')
                                xmp_data[namespace_key] = value

                # Ensure critical drone fields are properly mapped
                # ExifTool might return these with different key formats
                critical_mappings = [
                    ('RelativeAltitude', 'drone-dji:RelativeAltitude'),
                    ('AbsoluteAltitude', 'drone-dji:AbsoluteAltitude'),
                    ('FlightYawDegree', 'drone-dji:FlightYawDegree'),
                    ('GimbalYawDegree', 'drone-dji:GimbalYawDegree'),
                    ('GimbalPitchDegree', 'drone-dji:GimbalPitchDegree'),
                ]

                for base_key, full_key in critical_mappings:
                    # Check various possible key formats from ExifTool
                    possible_keys = [
                        base_key,
                        f'XMP:{base_key}',
                        f'XMP-drone-dji:{base_key}',
                        f'drone-dji:{base_key}',
                        full_key
                    ]
                    for possible_key in possible_keys:
                        if possible_key in metadata:
                            xmp_data[full_key] = metadata[possible_key]
                            xmp_data[base_key] = metadata[possible_key]
                            break

                if xmp_data:
                    return xmp_data
        except Exception:
            # If ExifTool fails, fall back to direct parsing
            pass

        # Fallback to original direct parsing method
        _XMP_EXT_HDR = b"http://ns.adobe.com/xmp/extension/\x00"

        def parse_base(data: bytes):
            s = data.find(b'<?xpacket begin')
            if s == -1:
                return None, {}
            e = data.find(b'<?xpacket end', s)
            if e == -1:
                return None, {}
            e = data.find(b'>', e) + 1
            if e <= 0:
                return None, {}
            xml = data[s:e].decode('utf-8', 'ignore')
            d = MetaDataHelper._parse_xmp_xml(xml)
            return d.get('HasExtendedXMP'), d  # our parser strips ns → key becomes 'HasExtendedXMP'

        def collect_ext(data: bytes, guid: str):
            if not guid:
                return None
            chunks, total = [], None
            i = 2
            while i + 4 <= len(data) and data[i] == 0xFF and data[i+1] != 0xDA:
                marker = data[i:i+2]
                L = struct.unpack(">H", data[i+2:i+4])[0]
                seg_end = i + 2 + L
                if marker == b"\xFF\xE1":
                    payload = data[i+4:seg_end]
                    if payload.startswith(_XMP_EXT_HDR):
                        g = payload[len(_XMP_EXT_HDR):len(_XMP_EXT_HDR)+32].decode('ascii', 'ignore')
                        if g == guid:
                            tlen = struct.unpack(">I", payload[len(_XMP_EXT_HDR)+32:len(_XMP_EXT_HDR)+36])[0]
                            off = struct.unpack(">I", payload[len(_XMP_EXT_HDR)+36:len(_XMP_EXT_HDR)+40])[0]
                            chunk = payload[len(_XMP_EXT_HDR)+40:]
                            total = tlen if total is None else total
                            chunks.append((off, bytes(chunk)))
                i = seg_end
            if not chunks or total is None:
                return None
            buf = bytearray(total)
            for off, ch in sorted(chunks, key=lambda x: x[0]):
                buf[off:off+len(ch)] = ch
            return bytes(buf)

        with open(file_path, 'rb') as f:
            data = f.read()

        guid, base = parse_base(data)
        if not guid:
            return base
        ext_xml = collect_ext(data, guid)
        if not ext_xml:
            return base
        try:
            ext_dict = MetaDataHelper._parse_xmp_xml(ext_xml.decode('utf-8', 'ignore'))
        except Exception:
            ext_dict = {}
        merged = dict(base)
        merged.update(ext_dict)
        return merged

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
    def get_drone_xmp_attribute(attribute, make, xmp_data):
        """
        Looks up and retrieves a specific XMP field based on attribute mapping.

        Args:
            attribute (str): Logical attribute name (e.g., "Flight Yaw").
            make (str): Drone manufacturer (e.g., "DJI").
            xmp_data (dict): Parsed XMP dictionary.

        Returns:
            str or None: Attribute value, if available.
        """
        # Handle special cases for attribute names
        attribute_map = {
            'AGL': 'Relative Altitude',  # AGL (Above Ground Level) maps to Relative Altitude
        }
        mapped_attribute = attribute_map.get(attribute, attribute)

        xmp_df = PickleHelper.get_xmp_mapping()

        # If xmp_df is None or empty, use hardcoded mappings
        if xmp_df is None or xmp_df.empty:
            # Fallback hardcoded mappings for DJI drones
            fallback_mappings = {
                'Flight Yaw': 'drone-dji:FlightYawDegree',
                'Flight Pitch': 'drone-dji:FlightPitchDegree',
                'Flight Roll': 'drone-dji:FlightRollDegree',
                'Gimbal Yaw': 'drone-dji:GimbalYawDegree',
                'Gimbal Pitch': 'drone-dji:GimbalPitchDegree',
                'Gimbal Roll': 'drone-dji:GimbalRollDegree',
                'Relative Altitude': 'drone-dji:RelativeAltitude',
                'AGL': 'drone-dji:RelativeAltitude'
            }
            if make and 'DJI' in make.upper():
                key = fallback_mappings.get(mapped_attribute)
                if key and key in xmp_data:
                    return xmp_data[key]
                # Also try without namespace
                simple_key = key.split(':')[-1] if key and ':' in key else key
                if simple_key and simple_key in xmp_data:
                    return xmp_data[simple_key]

        # Try to use the pickle mapping
        try:
            key = xmp_df.loc[xmp_df['Attribute'] == mapped_attribute, make].iloc[0]
            if key in xmp_data:
                return xmp_data[key]
            # Also try without namespace
            simple_key = key.split(':')[-1] if ':' in key else key
            if simple_key in xmp_data:
                return xmp_data[simple_key]
        except (KeyError, IndexError):
            pass

        # Additional fallback: check common variations in xmp_data directly
        if make and 'DJI' in make.upper():
            # Define possible keys for different attributes
            if attribute == 'AGL' or mapped_attribute == 'Relative Altitude':
                possible_keys = [
                    'drone-dji:RelativeAltitude',
                    'RelativeAltitude',
                    'XMP:RelativeAltitude',
                    'XMP-drone-dji:RelativeAltitude',
                ]
            elif attribute == 'ImageSource':
                possible_keys = [
                    'drone-dji:ImageSource',
                    'ImageSource',
                    'XMP:ImageSource',
                    'XMP-drone-dji:ImageSource',
                    'drone-dji:CameraType',
                    'CameraType',
                ]
            elif 'Gimbal' in attribute:
                gimbal_type = attribute.replace('Gimbal ', '')
                possible_keys = [
                    f'drone-dji:Gimbal{gimbal_type}Degree',
                    f'Gimbal{gimbal_type}Degree',
                    f'XMP:Gimbal{gimbal_type}Degree',
                    f'XMP-drone-dji:Gimbal{gimbal_type}Degree',
                ]
            else:
                # Generic fallback
                possible_keys = [
                    f'drone-dji:{attribute}',
                    attribute,
                    f'XMP:{attribute}',
                    f'XMP-drone-dji:{attribute}',
                ]

            for key in possible_keys:
                if key in xmp_data:
                    return xmp_data[key]

        return None

    @staticmethod
    def add_xmp_field(destination_file: str, namespace_uri: str, tag_name: str, value_str: str, threshold: int = 48000):
        """
        Store a tag either in the base XMP or the Extended XMP if it exceeds threshold.
        - threshold default (~48KB) leaves headroom for headers.
        """
        # 1) Build/parse the current base XMP
        xmp_segment = MetaDataHelper.extract_xmp(destination_file)

        def minimal_packet():
            return (
                '<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>'
                '<x:xmpmeta xmlns:x="adobe:ns:meta/">'
                '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
                '<rdf:Description/>'
                '</rdf:RDF>'
                '</x:xmpmeta>'
                '<?xpacket end="w"?>'
            ).encode("utf-8")

        if xmp_segment is None:
            base_xml = minimal_packet()
        else:
            # Strip APP1 and std header to get XML
            if xmp_segment.startswith(b"\xFF\xE1"):
                seg_len = struct.unpack(">H", xmp_segment[2:4])[0]
                payload = xmp_segment[4:4 + seg_len - 2]
            else:
                payload = xmp_segment
            if payload.startswith(_XMP_STD_HDR):
                xml_bytes = payload[len(_XMP_STD_HDR):]
            else:
                # try to find <?xpacket
                idx = payload.find(b"<?xpacket")
                xml_bytes = payload[idx:] if idx != -1 else payload
            try:
                ET.fromstring(xml_bytes.decode("utf-8"))
                base_xml = xml_bytes
            except Exception:
                base_xml = minimal_packet()

        root = ET.fromstring(base_xml)
        rdf_ns = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
        desc = root.find(f".//{rdf_ns}Description")
        if desc is None:
            rdf = root.find(f".//{rdf_ns}RDF")
            if rdf is None:
                rdf = ET.SubElement(root, f"{rdf_ns}RDF")
            desc = ET.SubElement(rdf, f"{rdf_ns}Description")

        # Register namespaces
        ET.register_namespace("custom", namespace_uri)
        ET.register_namespace("xmpNote", "http://ns.adobe.com/xmp/note/")

        value_bytes = value_str.encode("utf-8")

        if len(value_bytes) <= threshold:
            # Small: store directly in base packet
            desc.set(f"{{{namespace_uri}}}{tag_name}", value_str)
            base_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=False)
            # Ensure xpacket wrapper (so your get_xmp_data finder works)
            if b"<?xpacket" not in base_bytes:
                xpacket_start = (
                    b'<?xpacket begin="\xef\xbb\xbf" '
                    b'id="W5M0MpCehiHzreSzNTczkc9d"?>'
                )
                xpacket_end = b'<?xpacket end="w"?>'
                base_bytes = xpacket_start + base_bytes + xpacket_end
            MetaDataHelper.embed_xmp_xml(base_bytes, destination_file)
            return

        # Large: move the actual property into extended packet
        # 1) Ensure base packet declares GUID pointer
        #    (Do NOT store the large property in base)
        # Build a minimal extended <rdf:Description> carrying our tag.
        ext_root = ET.Element("x:xmpmeta")
        ext_root.set("xmlns:x", "adobe:ns:meta/")
        rdf = ET.SubElement(ext_root, "rdf:RDF")
        rdf.set("xmlns:rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        ext_desc = ET.SubElement(rdf, "rdf:Description")
        ext_desc.set(f"{{{namespace_uri}}}{tag_name}", value_str)
        ET.register_namespace("custom", namespace_uri)
        ext_xml = ET.tostring(ext_root, encoding="utf-8", xml_declaration=False)

        guid = MetaDataHelper._make_guid(ext_xml)

        # Add GUID pointer to base packet
        desc.set("{http://ns.adobe.com/xmp/note/}HasExtendedXMP", guid)
        base_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=False)
        if b"<?xpacket" not in base_bytes:
            xpacket_start = (
                b'<?xpacket begin="\xef\xbb\xbf" '
                b'id="W5M0MpCehiHzreSzNTczkc9d"?>'
            )
            xpacket_end = b'<?xpacket end="w"?>'
            base_bytes = xpacket_start + base_bytes + xpacket_end
        MetaDataHelper.embed_xmp_xml(base_bytes, destination_file)

        # 2) Write the extended packet (chunked APP1)
        MetaDataHelper.embed_extended_xmp(ext_xml, destination_file, guid)

    @staticmethod
    def embed_extended_xmp(extended_xml_bytes: bytes, destination_file: str, guid: str):
        """
        Write the Extended XMP packet split across multiple APP1 segments.
        Each APP1 payload layout:
        EXT_HDR + GUID(32 ASCII) + total_len(4 BE) + chunk_offset(4 BE) + chunk
        """
        with open(destination_file, "rb") as f:
            data = f.read()

        total = len(extended_xml_bytes)
        # Compute max chunk per segment
        overhead = len(_XMP_EXT_HDR) + 32 + 4 + 4  # header + GUID + total_len + offset
        max_payload = 65535 - 2 - overhead  # 2 bytes for segment length field
        if max_payload <= 0:
            raise ValueError("Computed negative chunk capacity; header too large?")

        out = bytearray(data)
        offset = 0
        while offset < total:
            chunk = extended_xml_bytes[offset: offset + max_payload]
            payload = bytearray()
            payload += _XMP_EXT_HDR
            payload += guid.encode("ascii")              # 32 ASCII hex
            payload += struct.pack(">I", total)          # total length
            payload += struct.pack(">I", offset)         # this chunk offset
            payload += chunk

            # Insert each extended segment before SOS (append multiple)
            # We don't "replace" by header because there can be many; appending is fine.
            out = MetaDataHelper._insert_or_replace_app1_segment(bytes(out), bytes(payload), match_header=None)
            offset += len(chunk)

        with open(destination_file, "wb") as f:
            f.write(out)

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

    def _make_guid(data_bytes: bytes) -> str:
        # Spec uses a 128-bit GUID. MD5 of the extended packet is common practice.
        return hashlib.md5(data_bytes).hexdigest().upper()  # 32 ASCII hex chars

    @staticmethod
    def _insert_or_replace_app1_segment(data: bytes, payload: bytes, match_header: bytes = None) -> bytes:
        """
        Insert (or replace if match_header is found) an APP1 segment in a JPEG.
        payload is the bytes AFTER the 2-byte length (i.e., the APP1 data excluding marker+len).
        """
        out = bytearray()
        out += data[:2]  # SOI
        i = 2
        replaced = False

        while i + 4 <= len(data) and data[i] == 0xFF and data[i+1] != 0xDA:
            marker = data[i:i+2]
            seg_len = struct.unpack(">H", data[i+2:i+4])[0]
            seg_start = i
            seg_end = i + 2 + seg_len
            seg_payload = data[i+4:seg_end]

            if marker == b"\xFF\xE1" and match_header and seg_payload.startswith(match_header):
                # replace matching APP1
                out += b"\xFF\xE1" + struct.pack(">H", len(payload) + 2) + payload
                i = seg_end
                replaced = True
                continue

            out += data[seg_start:seg_end]
            i = seg_end

        if not replaced:
            # insert before SOS (i)
            out += b"\xFF\xE1" + struct.pack(">H", len(payload) + 2) + payload

        out += data[i:]
        return bytes(out)

    @staticmethod
    def embed_xmp_xml(base_xmp_xml_bytes: bytes, destination_file: str):
        """
        Replace/insert the standard XMP APP1 segment (single packet).
        """
        std_payload = _XMP_STD_HDR + base_xmp_xml_bytes
        with open(destination_file, "rb") as f:
            data = f.read()
        new_data = MetaDataHelper._insert_or_replace_app1_segment(data, std_payload, match_header=_XMP_STD_HDR)
        with open(destination_file, "wb") as f:
            f.write(new_data)
