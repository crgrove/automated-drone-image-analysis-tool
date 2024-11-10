import numpy as np
from helpers.MetaDataHelper import MetaDataHelper

from core.services.thermalParserServices.DjiThermalParserService import DjiThermalParserService
from core.services.thermalParserServices.FlirThermalParserService import FlirThermalParserService
from core.services.thermalParserServices.AutelThermalParserService import AutelThermalImageParser


class ThermalParserService:
    """Service for parsing thermal images from various camera models."""

    FLIR_MODELS = [
        'Flir b60',
        'FLIR E40',
        'FLIR T640',
        'FLIR',
        'FLIR AX8',
        'XT2',
        'XTR'
    ]

    DJI_MODELS = [
        'ZH20T',
        'XT S',
        'MAVIC2-ENTERPRISE-ADVANCED',
        'ZH20N',
        'M3T',
        'M3TD',
        'M30T',
        'H30T'
    ]

    AUTEL_MODELS = [
        'XK729',
        'XL709',
        'XL801',
        'XL811',
        'MODELX'
    ]

    def __init__(self, dtype=np.float32):
        """
        Initialize the ThermalParserService.

        Args:
            dtype (type, optional): Data type for temperature arrays. Defaults to np.float32.
        """
        self.dtype = dtype

    def getModelandPlatform(self, meta_fields):
        """
        Determine the camera model and platform based on metadata.

        Args:
            meta_fields (dict): Dictionary of metadata key-value pairs.

        Returns:
            tuple[str, str]: Camera model name and platform ('FLIR', 'DJI', 'AUTEL', or 'None').
        """
        camera_model = meta_fields.get('CameraModel', meta_fields.get('Model'))
        if camera_model in self.FLIR_MODELS:
            return camera_model, 'FLIR'
        elif camera_model in self.DJI_MODELS:
            return camera_model, 'DJI'
        elif camera_model in self.AUTEL_MODELS:
            return camera_model, 'AUTEL'
        else:
            return 'Not Supported', 'None'

    def parseFile(self, full_path: str, palette: str = "White Hot"):
        """
        Process a thermal image file and return the temperature data and visual representation.

        Args:
            full_path (str): Path to the thermal image file.
            palette (str, optional): Color palette for visual representation. Defaults to "White Hot".

        Returns:
            tuple[numpy.ndarray, list]: Temperature data as a numpy array and the visual representation as a list.

        Raises:
            Exception: If the image file is invalid or the camera model is not supported.
        """
        data = MetaDataHelper.getMetaData(full_path)
        meta_fields = {k.split(':')[1].strip(): v for k, v in data.items() if ':' in k}
        camera_model, platform = self.getModelandPlatform(meta_fields)
        assert camera_model != "Not Supported", "Camera Model is not supported"

        if platform == 'FLIR':
            kwargs = {name: float(meta_fields[key]) for name, key in [
                ('emissivity', 'Emissivity'),
                ('ir_window_transmission', 'IRWindowTransmission'),
                ('planck_r1', 'PlanckR1'),
                ('planck_b', 'PlanckB'),
                ('planck_f', 'PlanckF'),
                ('planck_o', 'PlanckO'),
                ('planck_r2', 'PlanckR2'),
                ('ata1', 'AtmosphericTransAlpha1'),
                ('ata2', 'AtmosphericTransAlpha2'),
                ('atb1', 'AtmosphericTransBeta1'),
                ('atb2', 'AtmosphericTransBeta2'),
                ('atx', 'AtmosphericTransX'),
            ] if key in meta_fields}

            for name, key in [
                    ('object_distance', 'ObjectDistance'),
                    ('atmospheric_temperature', 'AtmosphericTemperature'),
                    ('reflected_apparent_temperature', 'ReflectedApparentTemperature'),
                    ('ir_window_temperature', 'IRWindowTemperature'),
                    ('relative_humidity', 'RelativeHumidity'),
            ]:
                if key in meta_fields:
                    kwargs[name] = float(meta_fields[key])

            try:
                parser = FlirThermalParserService(self.dtype)
                temps = parser.temperatures(filepath_image=full_path, **kwargs)
                img = parser.image(temps, palette)
                return temps, img
            except Exception as e:
                print(e)
                raise Exception("Invalid image file")

        elif platform == 'DJI':
            assert 'ThermalData' in meta_fields, "Image does not contain thermal data"
            kwargs = {name: float(meta_fields[key]) for name, key in [
                ('object_distance', 'ObjectDistance'),
                ('relative_humidity', 'RelativeHumidity'),
                ('emissivity', 'Emissivity'),
                ('reflected_apparent_temperature', 'Reflection'),
            ] if key in meta_fields}

            if camera_model not in ['M30T', 'M3T']:
                kwargs['image_height'] = int(meta_fields['ImageHeight'])
                kwargs['image_width'] = int(meta_fields['ImageWidth'])
            if 'emissivity' in kwargs:
                kwargs['emissivity'] /= 100
            if camera_model in ['MAVIC2-ENTERPRISE-ADVANCED', 'ZH20N', 'M3T', 'M30T', 'H30T', 'M3TD']:
                kwargs['m2ea_mode'] = True

            try:
                parser = DjiThermalParserService(self.dtype)
                temps = parser.temperatures(filepath_image=full_path, **kwargs)
                img = parser.image(full_path, palette)
                return temps, img
            except Exception:
                raise Exception("Invalid image file")

        elif platform == 'AUTEL':
            kwargs = {
                'image_height': int(meta_fields['ImageHeight']),
                'image_width': int(meta_fields['ImageWidth'])
            }

            try:
                parser = AutelThermalImageParser(self.dtype)
                temps = parser.temperatures(filepath_image=full_path, **kwargs)
                img = parser.image(temps, palette)
                return temps, img
            except Exception:
                raise Exception("Invalid image file")
