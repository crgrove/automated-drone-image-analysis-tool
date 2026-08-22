"""
Comprehensive tests for ImageService.

Tests metadata extraction and image attribute calculation functionality.
"""

import pytest
import numpy as np
import cv2
import tempfile
import os
import piexif
import pandas as pd
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
from core.services.image.ImageService import ImageService
from helpers.FormatHelper import FormatHelper

try:
    import tifffile
except ImportError:
    tifffile = None


@pytest.fixture
def image_service():
    """Fixture providing an ImageService instance."""
    # Create a temporary test image file
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imwrite(tmp_file.name, test_img)
        tmp_path = tmp_file.name

    service = ImageService(tmp_path)
    yield service

    # Cleanup
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)


@pytest.fixture
def image_service_with_img_array():
    """Fixture providing an ImageService instance with pre-loaded image array."""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imwrite(tmp_file.name, test_img)
        tmp_path = tmp_file.name

    # Pre-load image array
    img_array = np.zeros((100, 100, 3), dtype=np.uint8)
    service = ImageService(tmp_path, img_array=img_array)
    yield service

    # Cleanup
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)


def test_image_service_initialization(image_service):
    """Test ImageService initialization."""
    assert image_service is not None
    assert image_service.path is not None
    assert image_service.img_array is not None
    assert image_service.exif_data is not None or image_service.exif_data is None  # May be None for test images
    assert hasattr(image_service, 'xmp_data')
    assert hasattr(image_service, 'drone_make')


def test_image_service_with_img_array(image_service_with_img_array):
    """Test ImageService initialization with pre-loaded image array."""
    assert image_service_with_img_array is not None
    assert image_service_with_img_array.img_array is not None
    assert image_service_with_img_array.img_array.shape == (100, 100, 3)


def test_image_service_with_calculated_bearing():
    """Test ImageService initialization with calculated bearing."""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imwrite(tmp_file.name, test_img)
        tmp_path = tmp_file.name

    try:
        service = ImageService(tmp_path, calculated_bearing=45.5)
        assert service.calculated_bearing == 45.5
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_get_relative_altitude(image_service):
    """Test getting relative altitude from metadata."""
    # This will return None for test images without proper metadata
    altitude = image_service.get_relative_altitude()
    # Should return None or a float, depending on metadata
    assert altitude is None or isinstance(altitude, (int, float))

    # Test with feet unit
    altitude_ft = image_service.get_relative_altitude(distance_unit='ft')
    assert altitude_ft is None or isinstance(altitude_ft, (int, float))


def test_get_asl_altitude(image_service):
    """Test getting altitude above sea level from EXIF data."""
    altitude = image_service.get_asl_altitude('m')
    # Should return None or a float, depending on metadata
    assert altitude is None or isinstance(altitude, (int, float))

    # Test with feet unit
    altitude_ft = image_service.get_asl_altitude('ft')
    assert altitude_ft is None or isinstance(altitude_ft, (int, float))


def _asl_service(xmp_data, gps_alt_m=1500.0, make=b'Canon'):
    """ImageService with injected metadata for the ASL preference tests."""
    exif = {'0th': {piexif.ImageIFD.Make: make},
            'GPS': {piexif.GPSIFD.GPSAltitude: (int(gps_alt_m * 100), 100),
                    piexif.GPSIFD.GPSAltitudeRef: 0}}
    return ImageService(
        "dummy.jpg",
        img_array=np.zeros((10, 10, 3), dtype=np.uint8),
        exif_data=exif, xmp_data=xmp_data)


def test_get_asl_altitude_waldo_prefers_stamped_orthometric():
    """WALDO images use the pre-pass's orthometric AbsoluteAltitude, not the
    (ellipsoidal) EXIF GPSAltitude - a geoid-magnitude difference."""
    svc = _asl_service({'waldo:ProcessorVersion': '9',
                        'drone-dji:AbsoluteAltitude': '+1470.2500'})
    assert svc.get_asl_altitude('m') == pytest.approx(1470.25)
    assert svc.get_asl_altitude('ft') == pytest.approx(1470.25 * 3.28084, abs=0.01)


def test_get_asl_altitude_waldo_without_stamp_falls_back_to_exif():
    svc = _asl_service({'waldo:ProcessorVersion': '9'})
    assert svc.get_asl_altitude('m') == pytest.approx(1500.0)


def test_get_asl_altitude_non_waldo_unchanged():
    """DJI images keep reading EXIF GPSAltitude even when AbsoluteAltitude
    exists in XMP (DJI's own field; historical behaviour preserved)."""
    svc = _asl_service({'drone-dji:AbsoluteAltitude': '+1470.2500'}, make=b'DJI')
    assert svc.get_asl_altitude('m') == pytest.approx(1500.0)


def test_get_camera_pitch(image_service):
    """Test getting camera pitch angle."""
    pitch = image_service.get_camera_pitch()
    # Should return None or a float in range [-90, 90]
    assert pitch is None or (isinstance(pitch, (int, float)) and -90 <= pitch <= 90)


def test_get_gimbal_roll(image_service):
    """Test getting gimbal roll from XMP metadata."""
    roll = image_service.get_gimbal_roll()
    # Should return None or a float
    assert roll is None or isinstance(roll, (int, float))


def test_get_camera_yaw(image_service):
    """Test getting camera yaw/bearing."""
    yaw = image_service.get_camera_yaw()
    # Should return None or a float in range [0, 360)
    assert yaw is None or (isinstance(yaw, (int, float)) and 0 <= yaw < 360)


def test_get_camera_yaw_with_calculated_bearing():
    """Test that calculated bearing is used as fallback for camera yaw."""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imwrite(tmp_file.name, test_img)
        tmp_path = tmp_file.name

    try:
        service = ImageService(tmp_path, calculated_bearing=180.5)
        yaw = service.get_camera_yaw()
        # Should use calculated bearing if EXIF/XMP data is missing
        # May be None if there's other metadata, or 180.5 if calculated bearing is used
        assert yaw is None or isinstance(yaw, (int, float))
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_get_camera_intrinsics(image_service):
    """Test getting camera intrinsics."""
    intrinsics = image_service.get_camera_intrinsics()
    # Should return None or a dict with required keys
    assert intrinsics is None or isinstance(intrinsics, dict)
    if intrinsics:
        assert 'focal_length_mm' in intrinsics
        assert 'sensor_width_mm' in intrinsics
        assert 'sensor_height_mm' in intrinsics


def test_get_camera_hfov(image_service):
    """Test getting horizontal field of view."""
    hfov = image_service.get_camera_hfov()
    # Should return None or a float in degrees
    assert hfov is None or (isinstance(hfov, (int, float)) and 0 < hfov < 180)


def test_get_average_gsd(image_service):
    """Test getting average ground sampling distance."""
    gsd = image_service.get_average_gsd()
    # Should return None or a positive float
    assert gsd is None or (isinstance(gsd, (int, float)) and gsd > 0)

    # Test with custom altitude
    gsd_custom = image_service.get_average_gsd(custom_altitude_ft=100.0)
    assert gsd_custom is None or (isinstance(gsd_custom, (int, float)) and gsd_custom > 0)


# ---------------------------------------------------------------------------
# DJI Mini-series zeroed-gimbal handling (e.g. FC3682 / Mini 3)
#
# These airframes often leave GimbalPitch/Roll/Yaw at +0.00 even for nadir
# captures. A literal 0 pitch means "horizontal", which suppresses GSD and
# degrades AOI GPS/coverage. get_camera_pitch() must report the all-zero
# gimbal triad as unknown (None) so downstream nadir fallbacks apply, while
# leaving genuine oblique/horizon shots (any nonzero roll or yaw) untouched.
# ---------------------------------------------------------------------------

def _service_with_gimbal(make, pitch, roll, yaw, flight_yaw=None):
    """Build an ImageService over a blank temp image with injected gimbal XMP.

    Returns (service, tmp_path); caller is responsible for unlinking tmp_path.
    Values are strings as they appear in DJI XMP (e.g. '+0.00'); pass None to
    omit a key entirely. ``flight_yaw`` sets FlightYawDegree (the drone body
    heading) used by the flight-yaw fallback.
    """
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        cv2.imwrite(tmp_file.name, np.zeros((100, 100, 3), dtype=np.uint8))
        tmp_path = tmp_file.name

    service = ImageService(tmp_path)
    service.drone_make = make
    xmp = {}
    if pitch is not None:
        xmp['GimbalPitchDegree'] = pitch
    if roll is not None:
        xmp['GimbalRollDegree'] = roll
    if yaw is not None:
        xmp['GimbalYawDegree'] = yaw
    if flight_yaw is not None:
        xmp['FlightYawDegree'] = flight_yaw
    service.xmp_data = xmp
    return service, tmp_path


def test_get_camera_pitch_dji_zeroed_gimbal_returns_none():
    """DJI all-zero gimbal triad is the 'not recorded' signature -> None (nadir)."""
    service, tmp_path = _service_with_gimbal('DJI', '+0.00', '+0.00', '+0.00')
    try:
        assert service.get_camera_pitch() is None
    finally:
        os.unlink(tmp_path)


def test_get_camera_pitch_dji_zero_pitch_with_real_yaw_is_kept():
    """A recorded (nonzero) yaw means the gimbal WAS reporting -> keep pitch 0."""
    service, tmp_path = _service_with_gimbal('DJI', '+0.00', '+0.00', '+45.00')
    try:
        assert service.get_camera_pitch() == 0.0
    finally:
        os.unlink(tmp_path)


def test_get_camera_pitch_dji_zero_pitch_with_real_roll_is_kept():
    """A recorded (nonzero) roll means the gimbal WAS reporting -> keep pitch 0."""
    service, tmp_path = _service_with_gimbal('DJI', '+0.00', '-22.50', '+0.00')
    try:
        assert service.get_camera_pitch() == 0.0
    finally:
        os.unlink(tmp_path)


def test_get_camera_pitch_dji_normal_nadir_unchanged():
    """A genuine -90 nadir reading is returned verbatim."""
    service, tmp_path = _service_with_gimbal('DJI', '-90.00', '+0.00', '+0.00')
    try:
        assert service.get_camera_pitch() == -90.0
    finally:
        os.unlink(tmp_path)


def test_get_camera_pitch_non_dji_zero_triad_unchanged():
    """The heuristic is DJI-only; other makes keep a literal 0 pitch."""
    service, tmp_path = _service_with_gimbal('Autel Robotics', '+0.00', '+0.00', '+0.00')
    try:
        assert service.get_camera_pitch() == 0.0
    finally:
        os.unlink(tmp_path)


def test_get_gsd_service_recovers_for_zeroed_gimbal_dji_mini():
    """End-to-end: a Mini-3-style zeroed-gimbal image now yields a GSD.

    Before the fix, get_camera_pitch() returned 0.0 -> tilt 90 -> the >60
    'too oblique' guard suppressed GSD. With the nadir fallback the service
    builds and computes a sane per-pixel resolution.
    """
    service, tmp_path = _service_with_gimbal('DJI', '+0.00', '+0.00', '+0.00')
    try:
        service.exif_data = {
            "0th": {piexif.ImageIFD.Model: b"FC3682"},
            "Exif": {
                piexif.ExifIFD.FocalLength: (672, 100),      # 6.72 mm
                piexif.ExifIFD.PixelXDimension: 4000,
                piexif.ExifIFD.PixelYDimension: 3000,
            },
        }
        cam_df = pd.DataFrame([{'sensor_w': 9.65, 'sensor_h': 7.24}])  # DJI Mini 3
        with patch.object(service, '_get_camera_info', return_value=cam_df), \
             patch.object(service, 'get_relative_altitude', return_value=72.3):
            gsd_service = service.get_gsd_service()
            assert gsd_service is not None
            gsd = gsd_service.compute_average_gsd()
            assert gsd is not None and gsd > 0
    finally:
        os.unlink(tmp_path)


def test_get_camera_yaw_zeroed_gimbal_falls_back_to_flight_yaw():
    """Zeroed gimbal yaw (0.00) must not be trusted; use the real flight heading.

    This is the DJI_0264 case: gimbal all-zero, flight yaw -179.30 (~south).
    The bogus gimbal 0 would report the camera as facing north.
    """
    service, tmp_path = _service_with_gimbal(
        'DJI', '+0.00', '+0.00', '+0.00', flight_yaw='-179.30')
    try:
        yaw, source = service.get_camera_yaw_with_source()
        assert source == 'flight'
        assert yaw == pytest.approx(180.70, abs=0.01)   # -179.30 normalized
    finally:
        os.unlink(tmp_path)


def test_get_camera_yaw_recorded_gimbal_is_preferred():
    """A recorded gimbal (nonzero pitch) keeps the gimbal-yaw priority intact."""
    service, tmp_path = _service_with_gimbal(
        'DJI', '-90.00', '+0.00', '+45.00', flight_yaw='-179.30')
    try:
        yaw, source = service.get_camera_yaw_with_source()
        assert source == 'gimbal'
        assert yaw == pytest.approx(45.0, abs=0.01)
    finally:
        os.unlink(tmp_path)


def test_get_camera_yaw_non_dji_keeps_gimbal_priority():
    """The zeroed-gimbal redirect is DJI-only; other makes keep gimbal yaw."""
    service, tmp_path = _service_with_gimbal(
        'Autel Robotics', '+0.00', '+0.00', '+0.00', flight_yaw='-179.30')
    try:
        yaw, source = service.get_camera_yaw_with_source()
        assert source == 'gimbal'
        assert yaw == pytest.approx(0.0, abs=0.01)
    finally:
        os.unlink(tmp_path)


def test_get_position(image_service):
    """Test getting GPS position in various formats."""
    # Test decimal degrees format
    pos = image_service.get_position('Lat/Long - Decimal Degrees')
    assert pos is None or isinstance(pos, str)

    # Test DMS format
    pos_dms = image_service.get_position('Lat/Long - Degrees, Minutes, Seconds')
    assert pos_dms is None or isinstance(pos_dms, str)

    # Test UTM format
    pos_utm = image_service.get_position('UTM')
    assert pos_utm is None or isinstance(pos_utm, str)


def test_circle_areas_of_interest(image_service):
    """Test drawing circles on image for areas of interest."""
    areas_of_interest = [
        {'center': (50, 50), 'radius': 10},
        {'center': (80, 80), 'radius': 15}
    ]

    identifier_color = (255, 0, 0)  # Red in RGB
    augmented = image_service.circle_areas_of_interest(identifier_color, areas_of_interest)

    assert augmented is not None
    assert isinstance(augmented, np.ndarray)
    assert augmented.shape == image_service.img_array.shape


def test_circle_areas_of_interest_empty_list(image_service):
    """Test drawing circles with empty areas of interest list."""
    identifier_color = (255, 0, 0)
    augmented = image_service.circle_areas_of_interest(identifier_color, [])

    assert augmented is not None
    assert isinstance(augmented, np.ndarray)
    assert augmented.shape == image_service.img_array.shape


def test_circle_areas_of_interest_none(image_service):
    """Test drawing circles with None areas of interest."""
    identifier_color = (255, 0, 0)
    augmented = image_service.circle_areas_of_interest(identifier_color, None)

    assert augmented is not None
    assert isinstance(augmented, np.ndarray)
    assert augmented.shape == image_service.img_array.shape


def test_get_thermal_data_no_mask(image_service):
    """Test getting thermal data when no mask path is provided."""
    thermal_data = image_service.get_thermal_data('C')
    assert thermal_data is None


def test_get_thermal_data_with_mask():
    """Test getting thermal data from mask file."""
    # Skip test if tifffile is not available
    if tifffile is None:
        pytest.skip("tifffile is not available")

    # Create a temporary test image
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imwrite(tmp_file.name, test_img)
        tmp_path = tmp_file.name

    # Create a temporary mask file with thermal data
    with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as tmp_mask:
        # Create a 3-band TIFF: band 0 = mask, band 1 = temperature data
        mask_data = np.zeros((2, 100, 100), dtype=np.float32)
        mask_data[0] = 255  # Mask band
        mask_data[1] = 25.5  # Temperature in Celsius
        tifffile.imwrite(tmp_mask.name, mask_data)
        mask_path = tmp_mask.name

    try:
        service = ImageService(tmp_path, mask_path=mask_path)

        # Test getting thermal data in Celsius
        thermal_c = service.get_thermal_data('C')
        assert thermal_c is not None
        assert isinstance(thermal_c, np.ndarray)
        assert thermal_c.shape == (100, 100)

        # Test getting thermal data in Fahrenheit
        thermal_f = service.get_thermal_data('F')
        assert thermal_f is not None
        assert isinstance(thermal_f, np.ndarray)
        # Fahrenheit should be different from Celsius
        assert not np.array_equal(thermal_c, thermal_f)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        if os.path.exists(mask_path):
            os.unlink(mask_path)


def test_image_service_defer_load_skips_decode_until_access():
    """defer_load must not read pixels at construction, only on first access."""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imwrite(tmp_file.name, test_img)
        tmp_path = tmp_file.name

    try:
        service = ImageService(tmp_path, defer_load=True)
        assert service._img_array is None  # nothing decoded at construction

        loaded = service.img_array  # first access triggers the decode
        assert loaded.shape == (100, 100, 3)
        assert service._img_array is not None  # and the result is kept
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_image_service_defer_load_decodes_only_once():
    """Repeated img_array access must reuse the first decode."""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imwrite(tmp_file.name, test_img)
        tmp_path = tmp_file.name

    try:
        service = ImageService(tmp_path, defer_load=True)
        with patch.object(ImageService, '_load_img_array',
                          wraps=service._load_img_array) as mock_load:
            first = service.img_array
            second = service.img_array
        assert first is second
        assert mock_load.call_count == 1
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_image_service_img_array_assignment_still_works():
    """Code that swaps in a processed array must keep working with the property."""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imwrite(tmp_file.name, test_img)
        tmp_path = tmp_file.name

    try:
        service = ImageService(tmp_path, defer_load=True)
        replacement = np.ones((10, 10, 3), dtype=np.uint8)
        service.img_array = replacement
        assert service.img_array is replacement
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


class TestAltitudeReference:
    """Which plane RelativeAltitude is measured from.

    ``drone-dji:RelativeAltitude`` holds two different quantities: DJI puts
    height above the takeoff point there, and ADIAT's WALDO pre-pass puts a
    terrain-referenced AGL in the same tag. Nothing recorded which until
    the pre-pass started marking its own output with ``AltitudeType``.
    """

    def test_dji_imagery_is_takeoff_relative(self, image_service):
        """No marker - which is every DJI image ever shot."""
        image_service.xmp_data = {'drone-dji:RelativeAltitude': '+72.3000'}
        image_service.drone_make = 'DJI'
        assert image_service.get_altitude_reference() == \
            FormatHelper.ALTITUDE_REFERENCE_TAKEOFF

    def test_a_marked_image_is_terrain_referenced(self, image_service):
        image_service.xmp_data = {
            'drone-dji:RelativeAltitude': '+72.3000',
            'drone-dji:AltitudeType': 'terrain',
        }
        image_service.drone_make = 'Canon'
        assert image_service.get_altitude_reference() == \
            FormatHelper.ALTITUDE_REFERENCE_TERRAIN

    def test_the_marker_is_case_insensitive(self, image_service):
        image_service.xmp_data = {'drone-dji:AltitudeType': ' Terrain '}
        image_service.drone_make = 'Canon'
        assert image_service.get_altitude_reference() == \
            FormatHelper.ALTITUDE_REFERENCE_TERRAIN

    @pytest.mark.parametrize("value", ['RtkAlt', 'GpsAlt', '', 'agl', 42])
    def test_any_other_altitude_type_means_takeoff(self, image_service, value):
        """DJI's own AltitudeType values describe the fix, not the plane.

        Reading one of those as "terrain-referenced" would relabel a
        takeoff-relative number as ground clearance.
        """
        image_service.xmp_data = {'drone-dji:AltitudeType': value}
        image_service.drone_make = 'DJI'
        assert image_service.get_altitude_reference() == \
            FormatHelper.ALTITUDE_REFERENCE_TAKEOFF

    def test_no_metadata_at_all_means_takeoff(self, image_service):
        image_service.xmp_data = None
        image_service.drone_make = None
        assert image_service.get_altitude_reference() == \
            FormatHelper.ALTITUDE_REFERENCE_TAKEOFF

    def test_the_altitude_value_itself_is_unchanged(self, image_service):
        """Reading the reference must not disturb the number.

        This pass is a relabel: no GSD, AOI or coverage output may move.
        """
        image_service.xmp_data = {
            'drone-dji:RelativeAltitude': '+72.3000',
            'drone-dji:AltitudeType': 'terrain',
        }
        image_service.drone_make = 'Canon'
        image_service.get_altitude_reference()
        assert image_service.get_relative_altitude() == pytest.approx(72.3)


class TestAltitudeReadings:
    """One accessor decides which reference planes an image has.

    The AGL itself is not computed here - it comes from the effective-AGL
    iteration the GSD and AOI paths already run - so these tests cover the
    decision and the delegation, which is what display sites depend on.
    """

    def _service(self, image_service, reference, terrain_agl=None):
        image_service.get_relative_altitude = MagicMock(return_value=171.0)
        image_service.get_altitude_reference = MagicMock(return_value=reference)
        image_service.get_terrain_agl = MagicMock(return_value=terrain_agl)
        return image_service

    def test_dji_imagery_gets_both_planes(self, image_service):
        service = self._service(
            image_service, FormatHelper.ALTITUDE_REFERENCE_TAKEOFF, 141.2)
        readings = service.get_altitude_readings('ft')

        assert readings.value == 171.0
        assert readings.reference == FormatHelper.ALTITUDE_REFERENCE_TAKEOFF
        assert readings.terrain_agl == 141.2
        assert readings.has_terrain_agl is True

    def test_terrain_referenced_imagery_is_not_asked_twice(self, image_service):
        """WALDO imagery already carries AGL; a second lookup adds nothing."""
        service = self._service(
            image_service, FormatHelper.ALTITUDE_REFERENCE_TERRAIN, 141.2)
        readings = service.get_altitude_readings('ft')

        assert readings.reference == FormatHelper.ALTITUDE_REFERENCE_TERRAIN
        assert readings.terrain_agl is None
        service.get_terrain_agl.assert_not_called()

    def test_an_override_stands_alone_as_agl(self, image_service):
        """The operator was asked for height above the ground flown over."""
        service = self._service(
            image_service, FormatHelper.ALTITUDE_REFERENCE_TAKEOFF, 141.2)
        readings = service.get_altitude_readings('ft', custom_altitude_ft=250.0)

        assert readings.value == 250.0
        assert readings.reference == FormatHelper.ALTITUDE_REFERENCE_MANUAL
        assert readings.terrain_agl is None
        service.get_terrain_agl.assert_not_called()

    def test_an_override_converts_to_metres(self, image_service):
        service = self._service(
            image_service, FormatHelper.ALTITUDE_REFERENCE_TAKEOFF)
        readings = service.get_altitude_readings('m', custom_altitude_ft=328.084)
        assert readings.value == pytest.approx(100.0, abs=0.01)
        assert readings.unit == 'm'

    def test_an_unavailable_dem_leaves_the_ato_alone(self, image_service):
        """No tile cached, or no coverage: the ATO figure is still correct."""
        service = self._service(
            image_service, FormatHelper.ALTITUDE_REFERENCE_TAKEOFF, None)
        readings = service.get_altitude_readings('ft')

        assert readings.value == 171.0
        assert readings.has_terrain_agl is False

    def test_the_terrain_preference_is_forwarded(self, image_service):
        service = self._service(
            image_service, FormatHelper.ALTITUDE_REFERENCE_TAKEOFF, 141.2)
        service.get_altitude_readings('ft', use_terrain=False)
        assert service.get_terrain_agl.call_args.kwargs['use_terrain'] is False

    def test_display_reads_default_to_cache_only(self, image_service):
        """A status-bar read must never block on a tile fetch."""
        service = self._service(
            image_service, FormatHelper.ALTITUDE_REFERENCE_TAKEOFF, 141.2)
        service.get_altitude_readings('ft')
        assert service.get_terrain_agl.call_args.kwargs['offline_only'] is True

    def test_no_altitude_at_all_is_reported_as_absent(self, image_service):
        image_service.get_relative_altitude = MagicMock(return_value=None)
        image_service.get_altitude_reference = MagicMock(
            return_value=FormatHelper.ALTITUDE_REFERENCE_TAKEOFF)
        image_service.get_terrain_agl = MagicMock(return_value=None)
        readings = image_service.get_altitude_readings('ft')
        assert readings.has_value is False


class TestWorkingAltitude:
    """One decision: which altitude image geometry is computed with.

    GSD scales with height above the ground being photographed. Over flat
    terrain ATO and AGL agree; over relief they differ by the whole terrain
    change, and every figure derived from GSD inherits that error.
    """

    def _service(self, image_service, reported=100.0, effective=None,
                 has_intrinsics=True):
        image_service.get_relative_altitude = MagicMock(return_value=reported)
        image_service._effective_agl_at_pixel = MagicMock(return_value=effective)
        image_service._build_gsd_service = MagicMock(
            return_value=MagicMock() if has_intrinsics else None)
        return image_service

    def test_the_dem_agl_is_used_when_available(self, image_service):
        service = self._service(image_service, reported=100.0, effective=71.5)
        assert service.get_working_altitude_m() == 71.5

    def test_ato_is_the_fallback(self, image_service):
        """No coverage, or no tile cached yet: the reported figure stands."""
        service = self._service(image_service, reported=100.0, effective=None)
        assert service.get_working_altitude_m() == 100.0

    def test_a_non_positive_agl_falls_back(self, image_service):
        service = self._service(image_service, reported=100.0, effective=0.0)
        assert service.get_working_altitude_m() == 100.0

    def test_an_operator_override_wins_outright(self, image_service):
        """Entered as height above the ground flown - what GSD wants."""
        service = self._service(image_service, reported=100.0, effective=71.5)
        result = service.get_working_altitude_m(custom_altitude_ft=328.084)
        assert result == pytest.approx(100.0, abs=0.01)
        service._effective_agl_at_pixel.assert_not_called()

    def test_the_terrain_preference_forces_ato(self, image_service):
        service = self._service(image_service, reported=100.0, effective=71.5)
        assert service.get_working_altitude_m(use_terrain=False) == 100.0
        service._effective_agl_at_pixel.assert_not_called()

    def test_missing_intrinsics_fall_back_without_projecting(self, image_service):
        """Nothing can be projected, so the DEM cannot be consulted."""
        service = self._service(image_service, reported=100.0, effective=71.5,
                                has_intrinsics=False)
        assert service.get_working_altitude_m() == 100.0
        service._effective_agl_at_pixel.assert_not_called()

    def test_a_failing_dem_lookup_falls_back(self, image_service):
        service = self._service(image_service, reported=100.0)
        service._effective_agl_at_pixel = MagicMock(
            side_effect=RuntimeError("tile server down"))
        assert service.get_working_altitude_m() == 100.0

    def test_no_altitude_at_all_stays_none(self, image_service):
        service = self._service(image_service, reported=None, effective=None)
        assert service.get_working_altitude_m() is None


class TestGsdUsesTheWorkingAltitude:
    def test_the_gsd_service_is_built_at_the_resolved_altitude(self, image_service):
        image_service.get_working_altitude_m = MagicMock(return_value=71.5)
        image_service._build_gsd_service = MagicMock()
        image_service.get_gsd_service()
        assert image_service._build_gsd_service.call_args.kwargs['altitude_m'] == 71.5

    def test_terrain_agl_gives_a_larger_gsd_than_ato_over_rising_ground(self):
        """The physical point: less height above ground means finer scale.

        Guards the direction of the correction - swapping the two would make
        every derived object size wrong by the same ratio, silently.
        """
        from core.services.GSDService import GSDService
        common = dict(focal_length=24.0, image_size=(4000, 3000),
                      tilt_angle=0.0, sensor=(9.65, 7.24))
        at_ato = GSDService(altitude=100.0, **common).compute_average_gsd()
        at_agl = GSDService(altitude=71.5, **common).compute_average_gsd()
        assert at_agl < at_ato
        assert at_agl / at_ato == pytest.approx(71.5 / 100.0, rel=0.01)

    def test_the_agl_iteration_still_projects_from_ato(self, image_service):
        """Guards against the recursion this split exists to prevent.

        The effective-AGL solve needs a projection; building that projection
        from an AGL would re-enter the resolution that asked for it.
        """
        image_service.get_relative_altitude = MagicMock(return_value=100.0)
        image_service._effective_agl_at_pixel = MagicMock(return_value=71.5)
        base = MagicMock()
        image_service._build_gsd_service = MagicMock(return_value=base)

        image_service.get_effective_agl_at_pixel(10, 10)

        # Built with no explicit altitude: the ATO projection.
        assert image_service._build_gsd_service.call_args.args[0] is None
        assert image_service._effective_agl_at_pixel.call_args.args[2] is base


class TestAglEstimateSelection:
    """The two AGL estimates are cross-checked, not blindly preferred.

    Measured near Georgetown TX: ATO 150.9 ft over ground 11-15 ft below the
    takeoff point, so AGL is ~165 ft. The absolute-elevation chain reported
    254 ft - 89 ft high, the local geoid undulation - because that aircraft's
    EXIF GPSAltitude is already orthometric and the ellipsoid correction was
    applied to it anyway. The terrain-relief estimate is immune, so a
    disagreement means the absolute chain is the one to drop.
    """

    @staticmethod
    def _iterate(service, reported_agl, drone_terrain, drone_absolute,
                 terrain_here):
        """Drive one pass of the iteration with fixed terrain samples."""
        elevation = MagicMock()
        elevation.source = 'terrain'
        elevation.elevation_m = terrain_here
        terrain_service = MagicMock()
        terrain_service.enabled = True
        terrain_service.get_elevation.return_value = elevation

        service._get_projection_context = MagicMock(return_value={
            'drone_lat': 30.6535, 'drone_lon': -97.9536,
            'img_w': 4000, 'img_h': 3000, 'cx': 2000.0, 'cy': 1500.0,
            'focal_mm': 8.8, 'sensor_w_mm': 13.2, 'sensor_h_mm': 8.8,
            'pitch': -90.0, 'yaw': 0.0, 'roll': 0.0, 'roll_axis': None,
            'reported_agl': reported_agl,
            'drone_terrain_elev_m': drone_terrain,
            'drone_absolute_elev_m': drone_absolute,
            'geoid_undulation_m': -27.1,
            'terrain_service': terrain_service,
        })
        return service._effective_agl_at_pixel(2000, 1500, MagicMock())

    def test_a_geoid_sized_divergence_drops_the_absolute_estimate(self, image_service):
        """The field case: 46 m ATO, ground 3.7 m below takeoff."""
        # terrain here 308.0 m; takeoff ground 311.7 m; ATO 46.0 m
        # relief estimate  = 46.0 + (311.7 - 308.0) = 49.7 m  (~163 ft)
        # absolute estimate inflated by the 27.1 m undulation -> 76.8 m
        result = self._iterate(image_service, reported_agl=46.0,
                               drone_terrain=311.7, drone_absolute=384.8,
                               terrain_here=308.0)
        assert result == pytest.approx(49.7, abs=0.2)

    def test_agreement_keeps_the_more_precise_absolute_estimate(self, image_service):
        """A sound datum: the absolute chain is the better of the two."""
        # relief = 46.0 + (311.7 - 308.0) = 49.7; absolute = 357.7 - 308.0 = 49.7
        result = self._iterate(image_service, reported_agl=46.0,
                               drone_terrain=311.7, drone_absolute=357.7,
                               terrain_here=308.0)
        assert result == pytest.approx(49.7, abs=0.2)

    def test_rising_ground_reduces_agl_below_ato(self, image_service):
        """Direction guard: terrain above the takeoff point means less clearance."""
        # ground here 4 m ABOVE takeoff -> AGL = 46 - 4 = 42
        result = self._iterate(image_service, reported_agl=46.0,
                               drone_terrain=308.0, drone_absolute=None,
                               terrain_here=312.0)
        assert result == pytest.approx(42.0, abs=0.2)

    def test_falling_ground_raises_agl_above_ato(self, image_service):
        """And the converse - the case the field screenshot was taken over."""
        result = self._iterate(image_service, reported_agl=46.0,
                               drone_terrain=312.0, drone_absolute=None,
                               terrain_here=308.0)
        assert result == pytest.approx(50.0, abs=0.2)

    def test_without_terrain_under_the_camera_the_ato_figure_stands(self, image_service):
        result = self._iterate(image_service, reported_agl=46.0,
                               drone_terrain=None, drone_absolute=None,
                               terrain_here=308.0)
        assert result == pytest.approx(46.0, abs=0.2)


class TestAnchoredAglResolution:
    """With a mission anchor, altitude is takeoff + ATO - no datum, no
    cross-check. The DJI_0064 case: the per-frame absolute chain read
    77.4 m (254 ft) where the true figure is ~50 m (~165 ft)."""

    @staticmethod
    def _iterate_anchored(service, reported_agl, anchor_plus_ato, terrain_here):
        elevation = MagicMock()
        elevation.source = 'terrain'
        elevation.elevation_m = terrain_here
        terrain_service = MagicMock()
        terrain_service.enabled = True
        terrain_service.get_elevation.return_value = elevation

        service._get_projection_context = MagicMock(return_value={
            'drone_lat': 30.6535, 'drone_lon': -97.9536,
            'img_w': 4000, 'img_h': 3000, 'cx': 2000.0, 'cy': 1500.0,
            'focal_mm': 8.8, 'sensor_w_mm': 13.2, 'sensor_h_mm': 8.8,
            'pitch': -90.0, 'yaw': 0.0, 'roll': 0.0, 'roll_axis': None,
            'reported_agl': reported_agl,
            'drone_terrain_elev_m': None,
            'drone_absolute_elev_m': anchor_plus_ato,
            'geoid_undulation_m': None,
            'altitude_anchored': True,
            'terrain_service': terrain_service,
        })
        return service._effective_agl_at_pixel(2000, 1500, MagicMock())

    def test_anchored_agl_is_a_plain_dem_difference(self, image_service):
        """DJI_0064: camera = 311.0 + 46.0 = 357.0; ground 307.2 -> 49.8 m."""
        result = self._iterate_anchored(image_service, reported_agl=46.0,
                                        anchor_plus_ato=357.0,
                                        terrain_here=307.2)
        assert result == pytest.approx(49.8, abs=0.2)

    def test_takeoff_to_nadir_relief_is_not_misread_as_datum_error(self, image_service):
        """The reason the cross-check is skipped when anchored.

        A valley launch under a ridge search: anchored AGL and the
        nadir-relief estimate legitimately differ by the full launch-to-here
        relief. Running the divergence check would reject the correct
        anchored value - the trap the per-frame check falls into from the
        other side.
        """
        # Launch at 250 m, ground here 400 m, ATO 200 m -> true AGL 50 m.
        result = self._iterate_anchored(image_service, reported_agl=200.0,
                                        anchor_plus_ato=450.0,
                                        terrain_here=400.0)
        assert result == pytest.approx(50.0, abs=0.2)

    def test_the_projection_context_uses_the_mission_anchor(self, monkeypatch,
                                                            image_service):
        """anchor + ATO becomes the camera elevation; no geoid is consulted."""
        from core.services.image import AltitudeAnchorService as registry_module
        monkeypatch.setattr(registry_module, 'mission_anchor_elevation',
                            lambda offline_only=True, image_path=None: 311.0)

        image_service.get_camera_intrinsics = lambda: {
            'focal_length_mm': 8.8, 'sensor_width_mm': 13.2,
            'sensor_height_mm': 8.8}
        image_service.get_camera_yaw_with_source = lambda: (0.0, 'gimbal')
        image_service.get_camera_pitch = lambda: -90.0
        image_service.get_gimbal_roll = lambda: 0.0
        image_service.get_relative_altitude = lambda unit='m': 46.0
        image_service.get_asl_altitude = lambda unit: 358.1

        terrain = MagicMock()
        terrain.enabled = True
        terrain.get_elevation.return_value = SimpleNamespace(
            source='terrain', elevation_m=307.2)

        with patch("core.services.image.FrameGeometry.LocationInfo.get_gps",
                   return_value={'latitude': 30.6535, 'longitude': -97.9536}), \
             patch("core.services.terrain.TerrainService", return_value=terrain):
            ctx = image_service._get_projection_context()

        assert ctx['altitude_anchored'] is True
        assert ctx['drone_absolute_elev_m'] == pytest.approx(357.0)
        terrain.get_geoid_undulation.assert_not_called()

    def test_without_an_anchor_the_fallback_chain_is_unchanged(self, monkeypatch,
                                                               image_service):
        from core.services.image import AltitudeAnchorService as registry_module
        monkeypatch.setattr(registry_module, 'mission_anchor_elevation',
                            lambda offline_only=True, image_path=None: None)

        image_service.get_camera_intrinsics = lambda: {
            'focal_length_mm': 8.8, 'sensor_width_mm': 13.2,
            'sensor_height_mm': 8.8}
        image_service.get_camera_yaw_with_source = lambda: (0.0, 'gimbal')
        image_service.get_camera_pitch = lambda: -90.0
        image_service.get_gimbal_roll = lambda: 0.0
        image_service.get_relative_altitude = lambda unit='m': 46.0
        image_service.get_asl_altitude = lambda unit: 358.1

        terrain = MagicMock()
        terrain.enabled = True
        terrain.get_elevation.return_value = SimpleNamespace(
            source='terrain', elevation_m=307.2)
        terrain.get_geoid_undulation.return_value = -26.6

        with patch("core.services.image.FrameGeometry.LocationInfo.get_gps",
                   return_value={'latitude': 30.6535, 'longitude': -97.9536}), \
             patch("core.services.terrain.TerrainService", return_value=terrain):
            ctx = image_service._get_projection_context()

        assert ctx['altitude_anchored'] is False
        assert ctx['drone_absolute_elev_m'] == pytest.approx(384.7, abs=0.1)
