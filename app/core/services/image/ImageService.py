
import os
import piexif
import pandas as pd
import cv2
import numpy as np
import json
import math
import zlib
import base64
import tifffile
from PIL import Image

from core.services.GSDService import GSDService

from core.services.LoggerService import LoggerService
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Optional

from helpers.FormatHelper import FormatHelper
from helpers.MetaDataHelper import MetaDataHelper, XMP_ALTITUDE_TYPE_TERRAIN
from helpers.PickleHelper import PickleHelper
from helpers.LocationInfo import LocationInfo


@dataclass
class AltitudeReadings:
    """An image's altitude, the plane it is measured from, and its AGL.

    ``value`` is what the image's own metadata carries - ATO for DJI
    imagery, a terrain-referenced AGL for WALDO-prepassed imagery, an
    operator override where one is set. ``terrain_agl`` is the DEM-derived
    height above the ground beneath the camera, present only when it is a
    *different* number from ``value`` and the DEM could supply it.
    """

    value: Optional[float] = None
    reference: str = FormatHelper.ALTITUDE_REFERENCE_TAKEOFF
    unit: str = 'm'
    terrain_agl: Optional[float] = None

    @property
    def has_value(self) -> bool:
        return isinstance(self.value, (int, float))

    @property
    def has_terrain_agl(self) -> bool:
        return isinstance(self.terrain_agl, (int, float))


class ImageService:
    """Service to calculate various drone and image attributes based on metadata."""

    def __init__(self, path, mask_path=None, img_array=None, calculated_bearing=None,
                 exif_data=None, xmp_data=None, defer_load=False):
        """
        Initializes the ImageService by extracting Exif and XMP metadata.

        Args:
            path (str): The file path to the image.
            mask_path (str, optional): Path to the mask file containing thermal metadata.
            img_array (np.ndarray, optional): Pre-loaded image array (RGB format).
                                              If provided, skips loading from disk.
            calculated_bearing (float, optional): Calculated bearing in degrees [0, 360).
                                                 Used as fallback if EXIF bearing is missing.
            exif_data (dict, optional): Pre-read EXIF data. Skips the piexif read when given.
            xmp_data (dict, optional): Pre-read XMP data. Skips the (ExifTool) XMP read when
                                       given — used by bulk callers (e.g. the POD pass) to
                                       avoid launching one ExifTool process per image.
            defer_load (bool, optional): When True (and no img_array is given), pixel data
                                         is not read from disk until img_array is first
                                         accessed. Metadata-only callers use this to avoid
                                         decoding images whose pixels they may never need.
        """
        self.exif_data = exif_data if exif_data is not None else MetaDataHelper.get_exif_data_piexif(path)
        self.xmp_data = xmp_data if xmp_data is not None else MetaDataHelper.get_xmp_data_merged(path)
        self.drone_make = MetaDataHelper.get_drone_make(self.exif_data)
        self.path = path
        self.mask_path = mask_path
        self.calculated_bearing = calculated_bearing

        # Use pre-loaded array if provided, otherwise load from disk (now,
        # or lazily on first img_array access when defer_load is set)
        self._img_array = None
        if img_array is not None:
            self._img_array = img_array
        elif not defer_load:
            self._img_array = self._load_img_array()

    def _load_img_array(self):
        """Read and decode the image from disk as an RGB array."""
        img = cv2.imdecode(np.fromfile(self.path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        if img is None:
            raise ValueError(f"Could not load image: {self.path}")
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    @property
    def img_array(self):
        """Pixel data (RGB). Loaded lazily when defer_load was requested."""
        if self._img_array is None:
            self._img_array = self._load_img_array()
        return self._img_array

    @img_array.setter
    def img_array(self, value):
        self._img_array = value

    def get_relative_altitude(self, distance_unit='m'):
        """
        Retrieves the drone's relative altitude from metadata.

        Args:
            distance_unit (str): Unit to return altitude in ('ft' or 'm').

        Returns:
            float or None: Relative altitude in the specified unit, or None if unavailable.
        """
        METERS_TO_FEET = 3.28084
        if self.xmp_data is None or self.drone_make is None:
            return None

        altitude_meters = MetaDataHelper.get_drone_xmp_attribute('AGL', self.drone_make, self.xmp_data)

        if altitude_meters:
            try:
                altitude_meters = float(altitude_meters)
                return round(altitude_meters * METERS_TO_FEET, 2) if distance_unit == 'ft' else altitude_meters
            except ValueError:
                return None
        return None

    def get_altitude_reference(self):
        """Return the plane :meth:`get_relative_altitude` is measured from.

        ``drone-dji:RelativeAltitude`` carries two different quantities.
        DJI writes height above the **takeoff point** (ATO) - the value
        does not change when the terrain beneath the aircraft rises. ADIAT's
        WALDO pre-pass computes a genuine terrain-referenced **AGL** and
        writes it into the same tag, marking it with
        ``drone-dji:AltitudeType``.

        Only the exact marker counts. An absent tag - every DJI image ever
        shot - means takeoff-relative, which is also the safe assumption
        for any value ADIAT did not write.

        This is for labelling and diagnostics only: no GSD, AOI
        geolocation or coverage calculation branches on it. Making one do
        so would move numeric output and belongs in its own change.

        Returns:
            str: ``FormatHelper.ALTITUDE_REFERENCE_TERRAIN`` or
            ``FormatHelper.ALTITUDE_REFERENCE_TAKEOFF``.
        """
        if self.xmp_data is None or self.drone_make is None:
            return FormatHelper.ALTITUDE_REFERENCE_TAKEOFF

        altitude_type = MetaDataHelper.get_drone_xmp_attribute(
            'Altitude Type', self.drone_make, self.xmp_data
        )
        if (isinstance(altitude_type, str)
                and altitude_type.strip().lower() == XMP_ALTITUDE_TYPE_TERRAIN):
            return FormatHelper.ALTITUDE_REFERENCE_TERRAIN
        return FormatHelper.ALTITUDE_REFERENCE_TAKEOFF

    def get_altitude_readings(self, distance_unit='m', use_terrain=True,
                              custom_altitude_ft=None, offline_only=True):
        """Every altitude reference that applies to this image, resolved once.

        The single place that decides *which* planes an image has, so no
        display or export surface repeats the reasoning:

        * an operator override is height above the ground being flown over,
          so it stands alone as AGL;
        * WALDO-prepassed imagery already carries a terrain-referenced AGL
          in ``RelativeAltitude``, so it stands alone too;
        * DJI imagery carries ATO, and the DEM is asked for the matching
          AGL - the number that describes clearance and image scale - which
          is None when the DEM cannot answer for this position.

        Args:
            distance_unit (str): ``'ft'`` or ``'m'``; applies to both values.
            use_terrain (bool): Honor the DEM.
            custom_altitude_ft (float, optional): Operator override, in feet.
            offline_only (bool): Passed to :meth:`get_terrain_agl`; default
                True keeps a display read off the network.

        Returns:
            AltitudeReadings: ``value``/``reference`` from the image's own
            metadata, plus ``terrain_agl`` when a second plane exists.
        """
        if custom_altitude_ft is not None and custom_altitude_ft > 0:
            value = (custom_altitude_ft if distance_unit == 'ft'
                     else custom_altitude_ft / 3.28084)
            return AltitudeReadings(
                value=round(value, 2),
                reference=FormatHelper.ALTITUDE_REFERENCE_MANUAL,
                unit=distance_unit,
            )

        reference = self.get_altitude_reference()
        readings = AltitudeReadings(
            value=self.get_relative_altitude(distance_unit),
            reference=reference,
            unit=distance_unit,
        )
        if reference == FormatHelper.ALTITUDE_REFERENCE_TAKEOFF:
            readings.terrain_agl = self.get_terrain_agl(
                distance_unit, use_terrain=use_terrain,
                custom_altitude_ft=custom_altitude_ft,
                offline_only=offline_only,
            )
        return readings

    def get_terrain_agl(self, distance_unit='m', use_terrain=True,
                        custom_altitude_ft=None, offline_only=True):
        """Height above the terrain beneath the camera, from the DEM.

        The companion to :meth:`get_relative_altitude`: that one reports
        the reference plane the image's own metadata carries (ATO for DJI
        imagery), this one reports height above the ground actually being
        flown over. Over flat terrain they agree; over relief they diverge
        by the whole terrain change, and the AGL is the figure that
        describes clearance and image scale.

        No new arithmetic: this is the same effective-AGL iteration the GSD
        and AOI-geolocation paths run, evaluated at the image centre - the
        ground directly below the camera.

        Args:
            distance_unit (str): ``'ft'`` or ``'m'``.
            use_terrain (bool): Honor the DEM. False returns None.
            custom_altitude_ft (float, optional): Operator override.
            offline_only (bool): Default True - a *display* read must never
                block on a tile fetch, so it uses cached elevation only and
                returns None until the tile is local. Acquisition stocks the
                area in the background; callers doing real work (GSD, AOI
                positioning) pass False and accept the wait.

        Returns:
            float or None: AGL in the requested unit, or None when the DEM
            cannot answer for this position.
        """
        METERS_TO_FEET = 3.28084
        if not use_terrain:
            return None
        try:
            if self.img_array is None:
                return None
            height, width = self.img_array.shape[:2]
            agl_m = self.get_effective_agl_at_pixel(
                width / 2.0, height / 2.0, use_terrain=True,
                custom_altitude_ft=custom_altitude_ft,
                offline_only=offline_only,
            )
        except Exception as e:
            # Display-only: an unavailable DEM is not an error worth
            # interrupting anything for.
            LoggerService().debug(f"Terrain AGL unavailable for {self.path}: {e}")
            return None
        if agl_m is None:
            return None
        return round(agl_m * METERS_TO_FEET, 2) if distance_unit == 'ft' else agl_m

    def get_asl_altitude(self, distance_unit):
        """Retrieve the drone's altitude above sea level from EXIF data.

        WALDO imagery (waldo:ProcessorVersion stamped) prefers the
        pre-pass's drone-dji:AbsoluteAltitude: the synthesis computed a
        true orthometric ASL there (GPS ellipsoidal minus geoid
        undulation), while the raw EXIF GPSAltitude on these cameras is
        WGS84-ellipsoidal - tens of meters off as "sea level". Non-WALDO
        behaviour is unchanged.

        Args:
            distance_unit (str): Unit to return altitude in ("ft" or "m").

        Returns:
            float or None: Altitude in the requested unit, or None if unavailable.
        """
        METERS_TO_FEET = 3.28084

        if self.get_waldo_processor_version() is not None and self.xmp_data is not None:
            for key in ('drone-dji:AbsoluteAltitude', 'AbsoluteAltitude',
                        'XMP-drone-dji:AbsoluteAltitude'):
                value = self.xmp_data.get(key)
                if value is not None:
                    try:
                        asl_m = float(value)
                        return round(asl_m * METERS_TO_FEET, 2) if distance_unit == 'ft' else asl_m
                    except (TypeError, ValueError):
                        break

        if self.exif_data is None:
            return None

        gps_ifd = self.exif_data.get("GPS")
        if not gps_ifd:
            return None

        altitude = gps_ifd.get(piexif.GPSIFD.GPSAltitude)
        if altitude is None:
            return None

        try:
            if isinstance(altitude, tuple):
                altitude = altitude[0] / altitude[1]
            else:
                altitude = float(altitude)
        except (TypeError, ValueError, ZeroDivisionError):
            return None

        ref = gps_ifd.get(piexif.GPSIFD.GPSAltitudeRef, 0)
        if ref == 1:
            altitude = -altitude

        return round(altitude * METERS_TO_FEET, 2) if distance_unit == 'ft' else altitude

    def _dji_gimbal_unrecorded(self):
        """Whether a DJI image carries the "gimbal telemetry not recorded" signature.

        DJI Mini-series airframes (e.g. FC3682 / Mini 3) omit gimbal
        orientation and leave GimbalPitch/Roll/Yaw all at +0.00 even for
        straight-down captures, while flight telemetry (FlightYaw etc.) is
        populated normally. Trusting those zeros makes a nadir frame look
        horizontal (pitch 0) and north-facing (yaw 0), which suppresses GSD
        and rotates AOI ground positions. This detects that case so callers
        can fall back to nadir pitch and the flight-yaw heading.

        A genuinely recorded gimbal reads nonzero on at least one axis, so
        requiring the whole triad to be zero (or absent) keeps real
        oblique/panned captures out of the heuristic. DJI-only.

        Returns:
            bool: True when the gimbal triad is the unrecorded all-zero signature.
        """
        if self.drone_make != 'DJI' or self.xmp_data is None:
            return False

        def _angle(attr):
            raw = MetaDataHelper.get_drone_xmp_attribute(attr, self.drone_make, self.xmp_data)
            try:
                return float(raw) if raw is not None else None
            except (TypeError, ValueError):
                return None

        pitch = _angle('Gimbal Pitch')
        roll = _angle('Gimbal Roll')
        yaw = _angle('Gimbal Yaw')
        return pitch in (None, 0.0) and roll in (None, 0.0) and yaw in (None, 0.0)

    def get_camera_pitch(self):
        """
        Get camera pitch angle (standard photogrammetry convention).

        Convention: -90° = nadir (straight down), 0° = horizontal, +90° = straight up.

        Returns:
            float or None: Camera pitch in degrees (-90 to +90), or None if unavailable.
        """
        if self.xmp_data is None or self.drone_make is None:
            return None

        pitch = MetaDataHelper.get_drone_xmp_attribute('Gimbal Pitch', self.drone_make, self.xmp_data)
        if pitch is None:
            return None

        try:
            pitch = float(pitch)
        except (TypeError, ValueError):
            return None

        # Normalize to [-180, 180] range
        while pitch > 180:
            pitch -= 360
        while pitch < -180:
            pitch += 360

        # For DJI drones, gimbal pitch is already in the correct convention
        # (-90 = nadir, 0 = horizontal, +90 = up)
        # For Autel, may need different handling (add if needed)

        # DJI Mini-series images leave the gimbal angles unrecorded (all
        # +0.00). A literal 0 pitch reads as a horizontal view, suppressing
        # GSD and degrading AOI GPS/coverage, so report the pitch as unknown;
        # downstream callers treat a missing pitch as nadir, which is the
        # correct assumption for these straight-down SAR mapping captures.
        if self._dji_gimbal_unrecorded():
            return None

        return pitch

    def get_gimbal_roll(self):
        """Retrieve gimbal roll from XMP metadata.

        Returns:
            float or None: Roll in degrees, or None if unavailable.
        """
        if self.xmp_data is None or self.drone_make is None:
            return None

        roll = MetaDataHelper.get_drone_xmp_attribute('Gimbal Roll', self.drone_make, self.xmp_data)
        try:
            return float(roll)
        except (TypeError, ValueError):
            return None

    def get_flight_yaw(self):
        """Retrieve the aircraft/drone flight heading from XMP metadata.

        Distinct from the gimbal yaw: for WALDO imagery the stored image
        orientation (GimbalYawDegree) and the plane's travel direction
        (FlightYawDegree) can differ arbitrarily, and the pod-tilt roll is
        physically anchored to the flight direction.

        Returns:
            float or None: Heading in degrees [0, 360), or None if unavailable.
        """
        if self.xmp_data is None:
            return None
        for key in ('FlightYawDegree', 'drone-dji:FlightYawDegree'):
            value = self.xmp_data.get(key)
            if value is not None:
                try:
                    return float(value) % 360.0
                except (TypeError, ValueError):
                    return None
        return None

    def get_waldo_processor_version(self):
        """Return the WALDO pre-pass processor version stamped on this image.

        Returns:
            int or None: Version number, or None for non-WALDO imagery.
        """
        if self.xmp_data is None:
            return None
        for key in ('waldo:ProcessorVersion', 'ProcessorVersion',
                    'XMP-waldo:ProcessorVersion'):
            value = self.xmp_data.get(key)
            if value is not None:
                try:
                    return int(str(value))
                except (TypeError, ValueError):
                    return None
        return None

    def get_roll_axis_azimuth(self):
        """Compass azimuth of the axis the stamped gimbal roll rotates about.

        WALDO processor version >= 6 stamps the pod-tilt roll about the FLIGHT
        axis, decoupled from the stored image orientation. Returns None for
        everything else, which keeps the historical behaviour (roll about the
        gimbal-yaw axis).

        Returns:
            float or None: Axis azimuth in degrees, or None for legacy handling.
        """
        version = self.get_waldo_processor_version()
        if version is None or version < 6:
            return None
        return self.get_flight_yaw()

    def get_camera_yaw(self):
        """
        Get the camera yaw/bearing (direction the camera is pointing).

        Priority order:
        1. Gimbal Yaw (actual camera direction) - most accurate
        2. Flight Yaw (drone body direction) - fallback from EXIF
        3. Calculated Bearing (from track/GPS) - fallback from bearing recovery

        Note: Compensates for gimbal roll when roll is ~180°, which indicates
        the camera orientation is effectively inverted. This commonly occurs
        in DJI mapping missions where the gimbal maintains a fixed heading
        regardless of flight direction.

        Returns:
            float or None: Camera yaw in degrees (0-360), or None if unavailable.
        """
        return self.get_camera_yaw_with_source()[0]

    def get_camera_yaw_with_source(self):
        """
        Get the camera yaw together with the source that provided it.

        Same priority chain and roll-flip normalization as :meth:`get_camera_yaw`,
        but also reports which rung of the chain fired so callers (e.g.
        FrameGeometry) can attach a confidence to track-interpolated yaw.

        Returns:
            tuple[float | None, str | None]: (yaw_deg in [0, 360), source) where
            source is 'gimbal', 'flight', 'calculated', or None when no yaw is
            available.
        """
        yaw = None
        source = None

        # Prefer gimbal yaw if available (actual camera direction).
        #
        # DJI Mini-series images leave gimbal yaw at 0.00 when it was never
        # recorded (see _dji_gimbal_unrecorded). Trusting that 0 reports the
        # camera as facing north regardless of the aircraft's true heading,
        # which mis-orients the compass and rotates AOI ground positions. Skip
        # the gimbal rung in that case so the flight-yaw fallback supplies the
        # heading — a nadir body-fixed camera shares the aircraft heading.
        if (self.xmp_data is not None and self.drone_make is not None
                and not self._dji_gimbal_unrecorded()):
            gimbal_yaw = MetaDataHelper.get_drone_xmp_attribute('Gimbal Yaw', self.drone_make, self.xmp_data)
            if gimbal_yaw is not None:
                try:
                    yaw = float(gimbal_yaw)
                    source = 'gimbal'
                except (TypeError, ValueError):
                    pass

        # Fall back to flight yaw (drone body direction)
        if yaw is None:
            flight_yaw = self._get_drone_orientation()
            if flight_yaw is not None:
                yaw = flight_yaw
                source = 'flight'

        # Final fallback: use calculated bearing if available
        if yaw is None and self.calculated_bearing is not None:
            yaw = self.calculated_bearing
            source = 'calculated'

        if yaw is None:
            return None, None

        # Normalize to 0-360 range
        if yaw < 0:
            yaw += 360

        # Account for gimbal roll - if roll is ~180°, the camera is effectively
        # pointing in the opposite direction. This occurs in DJI mapping missions
        # when the gimbal maintains a fixed heading regardless of flight direction.
        # The gimbal physically can't roll 180° (limited to ~±52°), but DJI uses
        # roll=180° in metadata to represent this inverted orientation.
        gimbal_roll = self.get_gimbal_roll()
        if gimbal_roll is not None and abs(gimbal_roll) > 90:
            yaw = (yaw + 180) % 360

        return yaw, source

    def get_camera_intrinsics(self):
        """
        Get camera intrinsics for photogrammetric calculations.

        Returns:
            dict or None: Dictionary with 'focal_length_mm', 'sensor_width_mm', 'sensor_height_mm',
                         or None if camera info is unavailable.
        """
        # Get focal length from EXIF
        focal_length = self.exif_data["Exif"].get(piexif.ExifIFD.FocalLength)
        if focal_length is None:
            return None
        focal_length_mm = focal_length[0] / focal_length[1]

        # Get sensor size from camera database
        camera_info = self._get_camera_info()
        if camera_info is None or camera_info.empty:
            return None

        sensor_width_mm = float(camera_info['sensor_w'].iloc[0])
        sensor_height_mm = float(camera_info['sensor_h'].iloc[0])

        return {
            'focal_length_mm': focal_length_mm,
            'sensor_width_mm': sensor_width_mm,
            'sensor_height_mm': sensor_height_mm
        }

    def get_camera_hfov(self):
        """Compute the camera's horizontal field of view in degrees.

        Returns:
            float or None: Horizontal FOV in degrees, or None if data missing.
        """
        camera_info = self._get_camera_info()
        if camera_info is None or camera_info.empty:
            return None

        focal_length = self.exif_data["Exif"].get(piexif.ExifIFD.FocalLength)
        if focal_length is None:
            return None
        focal_length = focal_length[0] / focal_length[1]

        sensor_w = float(camera_info['sensor_w'].iloc[0])
        hfov = 2 * math.atan(sensor_w / (2 * focal_length))
        return math.degrees(hfov)

    def get_working_altitude_m(self, use_terrain=True, custom_altitude_ft=None,
                               offline_only=False):
        """The altitude image geometry should be computed with, in metres.

        The single place this decision is made, so GSD, ground distances and
        anything else scaling with height agree on the plane:

        * an operator override wins outright - it is entered as height above
          the ground being flown over, which is what the geometry wants, and
          it is set precisely when the metadata cannot be trusted;
        * otherwise the DEM-derived AGL, height above the ground actually
          being photographed;
        * otherwise the image's own takeoff-relative figure, which is what
          every ADIAT release before this one used everywhere.

        Args:
            use_terrain (bool): Honor the DEM. False forces the ATO path,
                which is what ``UseTerrainElevation`` and the effective-AGL
                iteration itself both need.
            custom_altitude_ft (float, optional): Operator override, feet.
            offline_only (bool): Use cached elevation only. A caller that
                must not block passes True and accepts ATO until terrain
                acquisition has stocked the area.

        Returns:
            float or None: Altitude in metres, or None when the image has
            none at all.
        """
        if custom_altitude_ft is not None and custom_altitude_ft > 0:
            return custom_altitude_ft / 3.28084

        reported = self.get_relative_altitude()
        if not use_terrain:
            return reported

        base = self._build_gsd_service()
        if base is None:
            # No intrinsics, so nothing can be projected: the DEM cannot be
            # consulted and the reported figure is all there is.
            return reported
        try:
            if self.img_array is None:
                return reported
            height, width = self.img_array.shape[:2]
            # The iteration projects with `base`, an ATO-altitude service, so
            # it cannot re-enter this method. Sampled where the camera is
            # pointed - the same value the altitude readout shows.
            effective_agl_m = self._effective_agl_at_pixel(
                int(width // 2), int(height // 2), base,
                offline_only=offline_only,
            )
        except Exception as e:
            LoggerService().debug(
                f"Working altitude: terrain AGL unavailable for {self.path}: {e}")
            return reported
        if effective_agl_m is None or effective_agl_m <= 0:
            return reported
        return effective_agl_m

    def get_gsd_service(self, custom_altitude_ft=None, use_terrain=True,
                        offline_only=False):
        """Return a GSDService for this image, at the best altitude available.

        Ground sample distance scales with height above the ground being
        photographed, so the altitude comes from
        :meth:`get_working_altitude_m` - the DEM-derived AGL where terrain
        data can answer, the takeoff-relative figure where it cannot.

        Args:
            custom_altitude_ft (float, optional): Operator override, feet.
            use_terrain (bool): Honor the DEM.
            offline_only (bool): Use cached elevation only.

        Returns:
            GSDService or None: None when intrinsics or altitude are missing.
        """
        altitude_m = self.get_working_altitude_m(
            use_terrain=use_terrain, custom_altitude_ft=custom_altitude_ft,
            offline_only=offline_only)
        return self._build_gsd_service(altitude_m=altitude_m)

    def _build_gsd_service(self, custom_altitude_ft=None, altitude_m=None):
        """
        Build a GSDService configured for this image.

        Returns the service so callers can query GSD at specific pixels (for
        oblique imagery where GSD varies across the frame). Returns None if
        any required EXIF/XMP/sensor data is missing or if the view is too
        oblique for a reliable estimate.

        Args:
            custom_altitude_ft (float, optional): Custom altitude in feet to use
                instead of XMP data. Useful when XMP altitude is negative or
                incorrect.

        Returns:
            GSDService or None
        """
        image_width = self.exif_data["Exif"].get(piexif.ExifIFD.PixelXDimension)
        image_height = self.exif_data["Exif"].get(piexif.ExifIFD.PixelYDimension)

        model = self.exif_data["0th"].get(piexif.ImageIFD.Model)
        if model:
            model = model.decode('utf-8').strip().rstrip("\x00")
        if not model or not self.drone_make:
            return None

        focal_length = self.exif_data["Exif"].get(piexif.ExifIFD.FocalLength)
        if focal_length is None:
            return None
        focal_length = focal_length[0] / focal_length[1]

        # An explicit altitude - the plane resolved by
        # get_working_altitude_m - wins, then the operator override, then the
        # image's own takeoff-relative figure. Callers that need the
        # uncorrected projection (the effective-AGL iteration) pass neither.
        if altitude_m is not None and altitude_m > 0:
            altitude_meters = altitude_m
        elif custom_altitude_ft is not None and custom_altitude_ft > 0:
            altitude_meters = custom_altitude_ft / 3.28084
        else:
            altitude_meters = self.get_relative_altitude()

        if altitude_meters is None:
            return None

        # Camera pitch -> tilt-from-nadir
        pitch = self.get_camera_pitch()
        if pitch is None:
            tilt_angle = 0
        else:
            tilt_angle = 90 + pitch
            tilt_angle = max(0, min(90, tilt_angle))

        if tilt_angle > 60:
            return None  # Too oblique for accurate GSD calculation

        camera_info = self._get_camera_info()
        if camera_info is None or camera_info.empty:
            return None

        sensor_w = float(camera_info['sensor_w'].iloc[0])
        sensor_h = float(camera_info['sensor_h'].iloc[0])
        sensor = (sensor_w, sensor_h)

        return GSDService(
            focal_length=focal_length,
            image_size=(image_width, image_height),
            altitude=altitude_meters,
            tilt_angle=tilt_angle,
            sensor=sensor
        )

    def get_average_gsd(self, custom_altitude_ft=None):
        """
        Computes the estimated average Ground Sampling Distance (GSD).

        Args:
            custom_altitude_ft (float, optional): Custom altitude in feet to use instead of XMP data.
                                                  Useful when XMP altitude is negative or incorrect.

        Returns:
            float or None: Average GSD in cm/pixel, or None if required data is missing.
        """
        gsd_service = self.get_gsd_service(custom_altitude_ft=custom_altitude_ft)
        if gsd_service is None:
            return None
        avg = gsd_service.compute_average_gsd()
        if avg is None:
            return None
        return round(avg, 2)

    def compute_gsd_at_pixel(self, col, row, use_terrain=True, custom_altitude_ft=None):
        """Compute GSD at a specific image pixel, with optional DEM-corrected AGL.

        For oblique imagery the effective AGL at a pixel can differ
        substantially from the drone's reported AGL because the ground point
        sampled by that pixel sits at a different terrain elevation than the
        ground directly under the drone. When the terrain service is enabled
        this method projects the pixel ray to the ground, queries the DEM for
        the terrain elevation at that ground point, derives an effective AGL,
        and uses it to compute GSD. Falls back to flat-ground GSD when
        terrain data is unavailable.

        Args:
            col: Image column (x pixel coordinate).
            row: Image row (y pixel coordinate).
            use_terrain (bool): Honor DEM data when available. Default True.
            custom_altitude_ft (float, optional): User-supplied AGL override
                in feet (e.g. from the altitude controller).

        Returns:
            GSD in cm/px, or None if not computable.
        """
        gsd_service = self.get_gsd_service(custom_altitude_ft=custom_altitude_ft)
        if gsd_service is None:
            return None

        irow = int(round(row))
        icol = int(round(col))

        if not use_terrain:
            return gsd_service.compute_gsd(irow, icol)

        effective_agl_m = self._effective_agl_at_pixel(
            icol, irow, gsd_service, custom_altitude_ft=custom_altitude_ft
        )
        if effective_agl_m is None or effective_agl_m <= 0:
            return gsd_service.compute_gsd(irow, icol)

        return gsd_service.compute_gsd(irow, icol, altitude_override=effective_agl_m)

    def get_effective_agl_at_pixel(self, col, row, use_terrain=True, custom_altitude_ft=None,
                                   offline_only=False):
        """Public accessor for the DEM-corrected effective AGL at a pixel.

        Args:
            col: Image column (x pixel coordinate).
            row: Image row (y pixel coordinate).
            use_terrain (bool): Honor DEM data when available. Default True.
            custom_altitude_ft (float, optional): User-supplied AGL override
                in feet.

        Returns:
            Effective AGL in meters when terrain data is available (and
            use_terrain is True), otherwise None — callers should fall back
            to the reported/flat AGL.
        """
        if not use_terrain:
            return None
        # The ATO-altitude projection: this is what the AGL is being solved
        # for, so it must not itself be built from an AGL.
        gsd_service = self._build_gsd_service(custom_altitude_ft)
        if gsd_service is None:
            return None
        return self._effective_agl_at_pixel(
            int(round(col)), int(round(row)), gsd_service,
            custom_altitude_ft=custom_altitude_ft, offline_only=offline_only
        )

    # ---------------- terrain helpers ----------------

    def get_frame_geometry(self, custom_altitude_ft=None, bearing_quality=None,
                           agl_override_ft=None):
        """Collect this image's camera pose + intrinsics as a FrameGeometry.

        A public, terrain-free snapshot (see
        :class:`core.services.image.FrameGeometry.FrameGeometry`) consumed by the
        Coverage/POD pipeline and, internally, by :meth:`_get_projection_context`.
        Cached per ``(custom_altitude_ft, agl_override_ft)``. Returns None when
        GPS, intrinsics, image size, or a positive AGL is unavailable.
        """
        cache_key = (custom_altitude_ft, agl_override_ft)
        cache = getattr(self, '_frame_geometry_cache', None)
        if cache is None:
            cache = {}
            self._frame_geometry_cache = cache
        if cache_key in cache:
            return cache[cache_key]

        from core.services.image.FrameGeometry import FrameGeometry
        fg = FrameGeometry.from_image_service(
            self,
            custom_altitude_ft=custom_altitude_ft,
            bearing_quality=bearing_quality,
            agl_override_ft=agl_override_ft,
        )
        cache[cache_key] = fg
        return fg

    def _get_projection_context(self, custom_altitude_ft=None, offline_only=False):
        """Collect drone pose, intrinsics and per-image terrain data needed for
        per-pixel projection. Caches the result on the instance so repeated
        per-pixel queries (e.g. dragging the person-reference overlay) don't
        re-read EXIF or re-query the DEM for the drone position.

        Built on top of :meth:`get_frame_geometry` (pose + intrinsics), then
        augmented with the terrain reconciliation fields.

        Returns:
            dict or None: projection context, or None if any required data is
            missing.
        """
        cache_key = ('proj_ctx', custom_altitude_ft, bool(offline_only))
        cached = getattr(self, '_projection_context_cache', {}).get(cache_key)
        if cached is not None:
            return cached

        try:
            # Preserve the historical guard: this path requires the pixel array
            # (per-pixel projection callers always have it loaded).
            if self.img_array is None:
                return None

            fg = self.get_frame_geometry(custom_altitude_ft=custom_altitude_ft)
            if fg is None:
                return None

            drone_lat = fg.lat
            drone_lon = fg.lon
            img_h, img_w = self.img_array.shape[:2]
            reported_agl = fg.agl_m
            absolute_alt = fg.asl_alt_m

            # Lazy import to avoid pulling the terrain stack when unused.
            try:
                from core.services.terrain import TerrainService
                terrain_service = TerrainService()
            except Exception:
                terrain_service = None

            drone_terrain_elev_m = None
            geoid_undulation_m = None
            drone_absolute_elev_m = None
            altitude_anchored = False

            if terrain_service is not None and getattr(terrain_service, 'enabled', False):
                # The mission anchor first: takeoff elevation resolved once
                # for the whole flight, carried per-frame by the barometer.
                # Datum-free, so neither the geoid nor EXIF GPSAltitude's
                # unknown reference enters the arithmetic.
                from core.services.image.AltitudeAnchorService import (
                    mission_anchor_elevation)
                anchor_elev = mission_anchor_elevation(
                    offline_only=offline_only, image_path=self.path)
                drone_terrain = terrain_service.get_elevation(
                    drone_lat, drone_lon, offline_only=offline_only)
                if drone_terrain.source == 'terrain' and drone_terrain.elevation_m is not None:
                    drone_terrain_elev_m = drone_terrain.elevation_m
                if anchor_elev is not None:
                    drone_absolute_elev_m = anchor_elev + reported_agl
                    altitude_anchored = True
                else:
                    # Fallback: the per-frame chains. GPSAltitude's datum is
                    # per-airframe unknown, which is why this is only ever a
                    # cross-checked fallback, never the primary.
                    geoid_undulation_m = terrain_service.get_geoid_undulation(
                        drone_lat, drone_lon, offline_only=offline_only)
                    if absolute_alt is not None and geoid_undulation_m is not None:
                        drone_absolute_elev_m = absolute_alt - geoid_undulation_m
                    elif drone_terrain_elev_m is not None:
                        drone_absolute_elev_m = drone_terrain_elev_m + reported_agl

            ctx = {
                'drone_lat': drone_lat,
                'drone_lon': drone_lon,
                'img_w': img_w,
                'img_h': img_h,
                'cx': img_w / 2.0,
                'cy': img_h / 2.0,
                'focal_mm': fg.focal_mm,
                'sensor_w_mm': fg.sensor_mm[0],
                'sensor_h_mm': fg.sensor_mm[1],
                'pitch': fg.pitch_deg,
                'yaw': fg.yaw_deg,
                'roll': fg.roll_deg,
                'roll_axis': self.get_roll_axis_azimuth() if fg.roll_deg else None,
                'reported_agl': reported_agl,
                'drone_terrain_elev_m': drone_terrain_elev_m,
                'drone_absolute_elev_m': drone_absolute_elev_m,
                'geoid_undulation_m': geoid_undulation_m,
                'altitude_anchored': altitude_anchored,
                'terrain_service': terrain_service,
            }
            if not hasattr(self, '_projection_context_cache'):
                self._projection_context_cache = {}
            self._projection_context_cache[cache_key] = ctx
            return ctx
        except Exception:
            return None

    @staticmethod
    def _agl_selection_context():
        """A stand-in ``self`` for ``AOIService._select_effective_agl``.

        That method reads nothing off the instance but ``.logger``, and
        sharing the real selection matters more than the awkward call - a
        second implementation here is exactly how the AOI path and everything
        else drifted onto different altitudes.
        """
        return SimpleNamespace(logger=LoggerService())

    def _effective_agl_at_pixel(self, col, row, gsd_service, custom_altitude_ft=None,
                                offline_only=False):
        """Iteratively refine the effective AGL at a pixel using DEM data.

        Mirrors the algorithm used by AOIService for AOI positioning. Returns
        the effective AGL in meters when terrain data is available, otherwise
        None (caller should fall back to the flat-ground GSD).
        """
        ctx = self._get_projection_context(custom_altitude_ft=custom_altitude_ft,
                                           offline_only=offline_only)
        if ctx is None:
            return None
        terrain_service = ctx['terrain_service']
        if terrain_service is None or not getattr(terrain_service, 'enabled', False):
            return None

        # Lazy import to dodge circular reference between AOIService/ImageService.
        from core.services.image.AOIService import AOIService

        reported_agl = ctx['reported_agl']
        drone_terrain_elev = ctx['drone_terrain_elev_m']
        drone_absolute_elev = ctx['drone_absolute_elev_m']

        # Cache iteration result per (pixel, altitude) so repeated queries from
        # a dragging overlay don't re-iterate the projection unnecessarily.
        cache = getattr(self, '_effective_agl_cache', None)
        if cache is None:
            cache = {}
            self._effective_agl_cache = cache
        # Quantize the pixel to a small grid (every 8 pixels) so we hit the
        # cache even when the user is dragging continuously without committing
        # to a stale value for big jumps.
        ck = (col >> 3, row >> 3, custom_altitude_ft, bool(offline_only))
        if ck in cache:
            return cache[ck]

        # Initial ground projection using the reported AGL.
        initial = AOIService._calculate_ground_position(
            ctx['drone_lat'], ctx['drone_lon'], col, row,
            ctx['cx'], ctx['cy'], ctx['img_w'], ctx['img_h'],
            ctx['focal_mm'], ctx['sensor_w_mm'], ctx['sensor_h_mm'],
            reported_agl, ctx['pitch'], ctx['yaw'], ctx['roll'],
            roll_axis_azimuth_deg=ctx['roll_axis'],
        )
        if initial is None:
            cache[ck] = None
            return None

        current_lat, current_lon = initial
        effective_agl = reported_agl
        for _ in range(AOIService.MAX_TERRAIN_ITERATIONS):
            terrain_result = terrain_service.get_elevation(current_lat, current_lon)
            if terrain_result.source != 'terrain' or terrain_result.elevation_m is None:
                cache[ck] = None
                return None

            terrain_elev = terrain_result.elevation_m

            # Absolute-elevation estimate: precise when the altitude datum
            # matches the DEM's. Terrain-relief estimate: immune to the datum
            # entirely, because a constant offset cancels in the difference of
            # two DEM samples.
            #
            # Trusting the first without checking it against the second is how
            # a measured frame near Georgetown TX read 254 ft AGL where the
            # true figure was ~165 ft (ATO 150.9 ft over ground 11-15 ft below
            # the takeoff point). The 89 ft gap is the local geoid undulation:
            # this aircraft's EXIF GPSAltitude is already orthometric, so
            # applying the ellipsoid correction to it adds ~27 m to every
            # image in the dataset.
            if ctx.get('altitude_anchored') and drone_absolute_elev is not None:
                # Anchored: camera elevation is takeoff + ATO, datum-free by
                # construction. No cross-check - the nadir-relief estimate
                # differs from this by the real takeoff-to-nadir relief, and
                # rejecting the anchor over real relief is the trap the
                # per-frame check falls into from the other side.
                effective_agl = max(1.0, drone_absolute_elev - terrain_elev)
            else:
                agl_abs = (drone_absolute_elev - terrain_elev
                           if drone_absolute_elev is not None else None)
                agl_rel = (reported_agl + (drone_terrain_elev - terrain_elev)
                           if drone_terrain_elev is not None else None)
                effective_agl = max(1.0, AOIService._select_effective_agl(
                    self._agl_selection_context(), agl_abs, agl_rel, reported_agl,
                    ctx.get('geoid_undulation_m'),
                    SimpleNamespace(elevation_m=drone_terrain_elev),
                    terrain_elev,
                ))

            new_pos = AOIService._calculate_ground_position(
                ctx['drone_lat'], ctx['drone_lon'], col, row,
                ctx['cx'], ctx['cy'], ctx['img_w'], ctx['img_h'],
                ctx['focal_mm'], ctx['sensor_w_mm'], ctx['sensor_h_mm'],
                effective_agl, ctx['pitch'], ctx['yaw'], ctx['roll'],
                roll_axis_azimuth_deg=ctx['roll_axis'],
            )
            if new_pos is None:
                break

            new_lat, new_lon = new_pos
            dlat_m = (new_lat - current_lat) * 111320
            dlon_m = (new_lon - current_lon) * 111320 * math.cos(math.radians(current_lat))
            displacement = math.sqrt(dlat_m * dlat_m + dlon_m * dlon_m)
            current_lat, current_lon = new_lat, new_lon
            if displacement < AOIService.CONVERGENCE_THRESHOLD_M:
                break

        cache[ck] = effective_agl
        return effective_agl

    def get_position(self, position_format='Lat/Long - Decimal Degrees'):
        """
        Formats the GPS position based on the specified output format.

        Args:
            position_format (str): One of 'Lat/Long - Decimal Degrees',
                                   'Lat/Long - Degrees, Minutes, Seconds', or 'UTM'.

        Returns:
            str or None: Formatted position string or None if GPS data unavailable.
        """
        gps_coords = LocationInfo.get_gps(exif_data=self.exif_data)
        if gps_coords is None or gps_coords == {}:
            return None

        if position_format == 'Lat/Long - Decimal Degrees':
            return f"{gps_coords['latitude']}, {gps_coords['longitude']}"
        elif position_format == 'Lat/Long - Degrees, Minutes, Seconds':
            dms = LocationInfo.convert_decimal_to_dms(gps_coords['latitude'], gps_coords['longitude'])
            return (
                f"{dms['latitude']['degrees']}°{dms['latitude']['minutes']}'{dms['latitude']['seconds']}\"{dms['latitude']['reference']} "
                f"{dms['longitude']['degrees']}°{dms['longitude']['minutes']}'{dms['longitude']['seconds']}\"{dms['longitude']['reference']}"
            )
        elif position_format == 'UTM':
            utm = LocationInfo.convert_degrees_to_utm(gps_coords['latitude'], gps_coords['longitude'])
            return f"{utm['zone_number']}{utm['zone_letter']} {utm['easting']} {utm['northing']}"

    def get_thermal_data(self, unit):
        """
        Loads thermal data from a multi-band mask GeoTIFF.
        Band 0 = mask, Bands 1..N = temperature data.

        Args:
            unit (str): Temperature unit ('C' or 'F').

        Returns:
            np.ndarray or None: Temperature data array in the specified unit.
        """
        if not self.mask_path or not os.path.exists(self.mask_path):
            return None

        try:
            # Read all bands from the TIFF
            data = tifffile.imread(self.mask_path)

            # Ensure 3D shape (bands, height, width)
            if data.ndim == 2:
                # Only one band, no thermal data
                return None
            elif data.ndim == 3:
                # (bands, height, width)
                if data.shape[0] < 2:
                    return None  # no thermal bands present
                # Take only the first thermal band (band 1) for backward compatibility
                # Most thermal algorithms only store one temperature band anyway
                thermal_data = data[1].astype(np.float32)  # Shape: (height, width)
            else:
                return None

            # Convert units if needed
            if unit.upper() == 'F':
                thermal_data = thermal_data * 1.8 + 32.0

            return thermal_data

        except Exception as e:
            LoggerService().warning(f"Failed to read thermal data from {self.mask_path}: {e}")
            return None

    def _is_autel(self):
        """
        Checks if the drone is made by Autel

        Returns:
            boolean: True if the drone is an Autel
        """
        return self.drone_make in ('Autel', 'Autel Robotics')

    def _get_camera_info(self):
        """
        Retrieves camera specification information from a drone metadata lookup table.

        This method uses EXIF and XMP metadata to determine the drone's camera model,
        image source, and ISO sensitivity, then filters the drone metadata DataFrame
        to return the matching camera configuration.

        Returns:
            pandas.DataFrame or None: A filtered DataFrame containing camera specifications
            that match the current image's metadata, or None if the model or drone make is not found.
        """
        drones_df = PickleHelper.get_drone_sensor_info()

        # Check if drones_df was loaded successfully
        if drones_df is None or drones_df.empty:
            return None

        model = self.exif_data["0th"].get(piexif.ImageIFD.Model)
        if model:
            model = model.decode('utf-8').strip().rstrip("\x00")
        if not model or not self.drone_make:
            return None

        # Try multiple ways to get ImageSource
        image_source = MetaDataHelper.get_drone_xmp_attribute('ImageSource', self.drone_make, self.xmp_data)
        if not image_source:
            # Try direct lookup in xmp_data with various keys
            for key in ['ImageSource', 'XMP:ImageSource', 'drone-dji:ImageSource']:
                if key in self.xmp_data:
                    image_source = self.xmp_data[key]
                    break

        image_width = self.exif_data["Exif"].get(piexif.ExifIFD.PixelXDimension)

        iso = self.exif_data["Exif"].get(piexif.ExifIFD.ISOSpeedRatings)
        if image_source is not None and self.drone_make == 'DJI':
            def image_width_matches(row):
                # Skip width check if no width is specified in the row
                if pd.isna(row['Image Width']) or not str(row['Image Width']).strip():
                    return True
                # Handle multiple widths in the cell
                widths = [int(w.strip()) for w in str(row['Image Width']).replace(',', ' ').split()]
                return image_width in widths

            matching_rows = drones_df[
                (drones_df['Manufacturer'] == 'DJI') &
                (drones_df['Model (Exif)'].str.contains(model, na=False)) &
                (drones_df['Image Source (XMP)'] == image_source)
            ]

            matching_rows = matching_rows[matching_rows.apply(image_width_matches, axis=1)]

            return matching_rows
        elif self._is_autel():
            if iso == 0:
                return drones_df[
                    (drones_df['Model (Exif)'] == model) &
                    (drones_df['Camera'] == 'Thermal')
                ]
            else:
                return drones_df[
                    (drones_df['Model (Exif)'] == model) &
                    (drones_df['Camera'] != 'Thermal')
                ]
        else:
            return drones_df[
                (drones_df['Model (Exif)'] == model)
            ]

    def _get_drone_orientation(self):
        """
        Retrieves the yaw orientation of the drone body (0–360 degrees).

        Private method - use get_camera_yaw() instead for the camera direction.

        Returns:
            float or None: Yaw in degrees, or None if unavailable.
        """
        if self.xmp_data is None or self.drone_make is None:
            return None

        yaw = MetaDataHelper.get_drone_xmp_attribute('Flight Yaw', self.drone_make, self.xmp_data)
        if yaw is None:
            return None

        yaw = float(yaw)
        return 360 + yaw if yaw < 0 else yaw

    def circle_areas_of_interest(self, identifier_color, areas_of_interest):
        """
        Augments the image with contour outlines or circles for areas of interest.

        Returns:
            (augmented_image: np.ndarray, areas_of_interest: list[dict])
        """
        image_copy = self.img_array.copy()

        # Expect identifier_color as RGB; OpenCV uses BGR
        bgr = (int(identifier_color[2]), int(identifier_color[1]), int(identifier_color[0]))

        for aoi in areas_of_interest or []:
            # Get center and radius for circle drawing
            cx, cy = aoi.get("center", (0, 0))
            r = int(aoi.get("radius", 0))
            center = (int(cx), int(cy))

            cv2.circle(image_copy, center, r, bgr, thickness=2)

            # Add confidence label if available
            # Turning off for now
            if "confidence" in aoi and False:
                confidence = aoi["confidence"]
                # Position label above the AOI circle
                label_pos = (int(cx - r), int(cy - r - 10))
                # Ensure label stays within image bounds
                label_pos = (max(5, label_pos[0]), max(20, label_pos[1]))

                # Create confidence text
                conf_text = f"{confidence:.1f}%"

                # Choose text color based on confidence level
                if confidence >= 75:
                    text_color = (0, 255, 0)  # Green (BGR) for high confidence
                elif confidence >= 50:
                    text_color = (0, 215, 255)  # Gold (BGR) for medium-high confidence
                elif confidence >= 25:
                    text_color = (0, 165, 255)  # Orange (BGR) for medium-low confidence
                else:
                    text_color = (107, 107, 255)  # Red (BGR) for low confidence

                # Draw text background for better visibility
                (text_width, text_height), baseline = cv2.getTextSize(conf_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                cv2.rectangle(image_copy,
                              (label_pos[0] - 2, label_pos[1] - text_height - 2),
                              (label_pos[0] + text_width + 2, label_pos[1] + baseline + 2),
                              (0, 0, 0), -1)  # Black background

                # Draw confidence text
                cv2.putText(image_copy, conf_text, label_pos,
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)

        return image_copy

    @staticmethod
    def save_rgb_as_jpeg(img_array, path, quality=95):
        """Save an RGB numpy array as a JPEG file.

        Args:
            img_array: numpy array in RGB format (HxWx3).
            path: Destination file path.
            quality: JPEG quality (0-100).
        """
        bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(path), bgr, [int(cv2.IMWRITE_JPEG_QUALITY), quality])

    @staticmethod
    def rotate_image(img_array, angle_degrees, border_color=(128, 128, 128)):
        """Rotate an image by a given angle without cropping.

        Args:
            img_array: numpy array of the image (HxWxC).
            angle_degrees: Rotation angle in degrees (counter-clockwise positive).
            border_color: RGB tuple for the fill color of new border areas.

        Returns:
            numpy array of the rotated image.
        """
        h, w = img_array.shape[:2]
        center = (w // 2, h // 2)

        M = cv2.getRotationMatrix2D(center, angle_degrees, 1.0)

        cos = abs(M[0, 0])
        sin = abs(M[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))

        M[0, 2] += (new_w / 2) - center[0]
        M[1, 2] += (new_h / 2) - center[1]

        return cv2.warpAffine(img_array, M, (new_w, new_h),
                              borderMode=cv2.BORDER_CONSTANT,
                              borderValue=border_color)
