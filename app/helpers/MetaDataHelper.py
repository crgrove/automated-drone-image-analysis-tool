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
    def getEXIFToolPath():
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
    def transferExifPiexif(originFile, destinationFile):
        """
        Copy the EXIF information from one image file to another using piexif.

        Args:
            originFile (str): Path to the source file.
            destinationFile (str): Path to the destination file.
        """
        try:
            piexif.transplant(originFile, destinationFile)
        except piexif._exceptions.InvalidImageDataError:
            MetaDataHelper.transferExifPil(originFile, destinationFile)
        except ValueError:
            return

    @staticmethod
    def transferExifPil(originFile, destinationFile):
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
    def transferExifExiftool(originFile, destinationFile):
        """
        Copy the EXIF information from one image file to another using Exiftool.

        Args:
            originFile (str): Path to the source file.
            destinationFile (str): Path to the destination file.
        """
        with exiftool.ExifTool(MetaDataHelper.getEXIFToolPath()) as et:
            et.execute("-tagsfromfile", originFile, "-exif", destinationFile, "-overwrite_original")
            et.terminate()

    @staticmethod
    def transferXmpExiftool(originFile, destinationFile):
        """
        Copy the XMP information from one image file to another using Exiftool.

        Args:
            originFile (str): Path to the source file.
            destinationFile (str): Path to the destination file.
        """
        with exiftool.ExifTool(MetaDataHelper.getEXIFToolPath()) as et:
            et.execute("-tagsfromfile", originFile, "-xmp", destinationFile, "-overwrite_original")
            et.terminate()

    @staticmethod
    def transferAll(originFile, destinationFile):
        """
        Copy the EXIF and XMP information from one image file to another using Exiftool.

        Args:
            originFile (str): Path to the source file.
            destinationFile (str): Path to the destination file.
        """
        with exiftool.ExifTool(MetaDataHelper.getEXIFToolPath()) as et:
            et.execute("-tagsfromfile", originFile, destinationFile, "-overwrite_original", "--thumbnailimage")
            et.terminate()

    @staticmethod
    def transferTemperatureData(data, destinationFile):
        """
        Copy temperature data from an image to the Notes field on another image.

        Args:
            data (numpy.ndarray): Temperature data array.
            destinationFile (str): Path to the destination file.
        """
        json_data = json.dumps(data.tolist())
        with exiftool.ExifToolHelper(executable=MetaDataHelper.getEXIFToolPath()) as et:
            et.set_tags(
                [destinationFile],
                tags={"Notes": json_data},
                params=["-P", "-overwrite_original"]
            )
            et.terminate()

    @staticmethod
    def getRawTemperatureData(file_path):
        """
        Retrieve raw temperature data as bytes from an image.

        Args:
            file_path (str): Path to the image.

        Returns:
            bytes: Bytes representing temperature data.
        """
        with exiftool.ExifTool(MetaDataHelper.getEXIFToolPath()) as et:
            thermal_img_bytes = et.execute("-b", "-RawThermalImage", file_path, raw_bytes=True)
            et.terminate()
        return thermal_img_bytes

    @staticmethod
    def getTemperatureData(file_path):
        """
        Retrieve temperature data as a numpy array from the Notes field of an image.

        Args:
            file_path (str): Path to the image.

        Returns:
            numpy.ndarray: Array of temperature data.
        """
        with exiftool.ExifToolHelper(executable=MetaDataHelper.getEXIFToolPath()) as et:
            json_data = et.get_tags([file_path], tags=['Notes'])[0]['XMP:Notes']
            data = json.loads(json_data)
            temperature_c = np.asarray(data)
            et.terminate()
        return temperature_c

    @staticmethod
    def getMetaData(file_path):
        """
        Retrieve metadata from an image file.

        Args:
            file_path (str): Path to the image.

        Returns:
            dict: Key-value pairs of metadata.
        """
        with exiftool.ExifToolHelper(executable=MetaDataHelper.getEXIFToolPath()) as et:
            metadata = et.get_metadata([file_path])[0]
            et.terminate()
        return metadata

    @staticmethod
    def setTags(file_path, tags):
        """
        Update metadata with provided tags.

        Args:
            file_path (str): Path to the image.
            tags (dict): Dictionary of tags and values to be set.
        """
        with exiftool.ExifToolHelper(executable=MetaDataHelper.getEXIFToolPath()) as et:
            et.set_tags([file_path], tags=tags, params=["-overwrite_original"])
            et.terminate()

    @staticmethod
    def addGPSData(file_path, lat, lng, alt):
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

        MetaDataHelper.setGPSLocation(exif_dict, lat, lng, alt)
        exif_bytes = piexif.dump(exif_dict)
        img.save(file_path, "jpeg", exif=exif_bytes)

    @staticmethod
    def setGPSLocation(exif_dict, lat, lng, alt):
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
