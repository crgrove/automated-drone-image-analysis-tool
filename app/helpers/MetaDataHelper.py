from PIL import Image
from os import path
import exiftool
import piexif
import json
import numpy as np
import platform


class MetaDataHelper:

    @staticmethod
    def getEXIFToolPath():
        if platform.system() == 'Windows':
            return path.abspath(path.join(path.dirname(path.dirname(__file__)), 'external/exiftool.exe'))
        elif platform.system() == 'Darwin':
            return path.abspath(path.join(path.dirname(path.dirname(__file__)), 'external/exiftool'))

    @staticmethod
    def transferExifPiexif(originFile, destinationFile):
        """
        transferExifPiexif copies the exif information of an image file to another image file using piexif

        :String originFile: the path to the source file
        :String destinationFile: the path to the destination file
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
        transferExifPil copies the exif information of an image file to another image file using PIL

        :String originFile: the path to the source file
        :String destinationFile: the path to the destination file
        """

        # load old image and extract EXIF
        image = Image.open(originFile)
        if 'exif' in image.info:
            exif = image.info['exif']
            # load new image
            image_new = Image.open(destinationFile)
            image_new.save(destinationFile, 'JPEG', exif=exif)

    @staticmethod
    def transferExifExiftool(originFile, destinationFile):
        """
        transferExifExiftool copies the exif information of an image file to another image file using Exiftool

        :String originFile: the path to the source file
        :String destinationFile: the path to the destination file
        """
        with exiftool.ExifTool(MetaDataHelper.getEXIFToolPath()) as et:
            et.execute("-tagsfromfile", originFile, "-exif", destinationFile, "-overwrite_original")
            et.terminate()

    @staticmethod
    def transferXmpExiftool(originFile, destinationFile):
        """
        transferXmpExiftool copies the xmp information of an image file to another image file using Exiftool

        :String originFile: the path to the source file
        :String destinationFile: the path to the destination file
        """
        with exiftool.ExifTool(MetaDataHelper.getEXIFToolPath()) as et:
            et.execute("-tagsfromfile", originFile, "-xmp", destinationFile, "-overwrite_original")
            et.terminate()

    def transferAll(originFile, destinationFile):
        """
        transferAll copies the exif and xmp information of an image file to another image file using Exiftool

        :String originFile: the path to the source file
        :String destinationFile: the path to the destination file
        """
        with exiftool.ExifTool(MetaDataHelper.getEXIFToolPath()) as et:
            et.execute("-tagsfromfile", originFile, destinationFile, "-overwrite_original", "--thumbnailimage")
            et.terminate()

    @staticmethod
    def transferTemperatureData(data, destinationFile):
        """
        transferTemperatureData copies the temperature data from the original image to the Note field on the augmented image.

        :numpy.ndarray data: the path to the source file
        :String destinationFile: the path to the destination file
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
        getRawTemperatureData returns a byte string representing the temperature data
        :String full_path: the path to the image
        :return str: the bytes representing the temperature values
        """
        with exiftool.ExifTool(MetaDataHelper.getEXIFToolPath()) as et:
            thermal_img_bytes = et.execute("-b", "-RawThermalImage", file_path, raw_bytes=True)
            et.terminate()
        return thermal_img_bytes

    @staticmethod
    def getTemperatureData(file_path):
        """
        getTemperatureData returns a numpy array of temeprature data from the notes field an image.
        :String full_path: the path to the image
        :return numpy.ndarray: array of temperature data
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
        getMetaData returns a dictionary representation of the metadata from a file
        :String full_path: the path to the image
        :return Dict: Key value pairs of metadata.
        """
        with exiftool.ExifToolHelper(executable=MetaDataHelper.getEXIFToolPath()) as et:
            metadata = et.get_metadata([file_path])[0]
            et.terminate()
        return metadata

    @staticmethod
    def setTags(file_path, tags):
        """
        setTags updates file metadata with tags provided
        :String full_path: the path to the image
        :Dict tags: dictionary of tags and values to be set
        """
        with exiftool.ExifToolHelper(executable=MetaDataHelper.getEXIFToolPath()) as et:
            et.set_tags([file_path], tags=tags, params=["-overwrite_original"])
            et.terminate()

    @staticmethod
    def addGPSData(file_path, lat, lng, alt):
        # Load the image and its EXIF data
        img = Image.open(file_path)
        # Try to load the existing EXIF data, or create an empty EXIF dictionary
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}, "thumbnail": None}
        if "exif" in img.info:
            exif_dict = piexif.load(img.info["exif"])

        # Set the GPS data
        MetaDataHelper.setGPSLocation(exif_dict, lat, lng, alt)

        # Save the modified EXIF data back to the image
        exif_bytes = piexif.dump(exif_dict)
        img.save(file_path, "jpeg", exif=exif_bytes)

    @staticmethod
    def setGPSLocation(exif_dict, lat, lng, alt):
        # Convert decimal coordinates into degrees, minutes, seconds
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
