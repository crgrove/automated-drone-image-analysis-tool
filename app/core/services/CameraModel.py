"""CameraModel - forward projection of 3D world points to image pixels.

Builds a pinhole camera model from a drone image's metadata pose (AGL
altitude, gimbal pitch/yaw, lens intrinsics) and projects 3D points given in
a local North/East/Down (NED) frame centred on the camera.

Used by the Person Size Reference tool to draw perspective-correct
silhouettes and shadows - foreshortened at oblique gimbal angles and toward
the frame edges - instead of a flat top-down silhouette scaled by GSD.

The rotation conventions match AOIService._calculate_ground_position and
AOINeighborService.gps_to_pixel, so projected geometry lines up with the
imagery and with computed AOI ground positions. Lens distortion and gimbal
roll are not modelled (roll is omitted to stay consistent with
gps_to_pixel); both are minor for the reference-overlay use case.
"""

import math
from typing import Optional, Tuple


class CameraModel:
    """Pinhole camera built from a drone image's metadata pose.

    Coordinates use a local North/East/Down (NED) metric frame with the
    camera at the origin. The optical axis points down-and-forward per the
    gimbal pitch and yaw. project() maps a 3D NED point to its pixel;
    pixel_to_ground() casts a pixel ray onto a horizontal ground plane.
    """

    def __init__(self, agl_m, pitch_deg, yaw_deg,
                 focal_mm, sensor_w_mm, sensor_h_mm, width, height):
        """
        Args:
            agl_m: camera height above ground level, metres (> 0).
            pitch_deg: gimbal pitch; -90 = nadir (straight down), 0 = horizontal.
            yaw_deg: gimbal yaw; 0 = north, increasing clockwise.
            focal_mm: lens focal length, mm.
            sensor_w_mm: sensor width, mm.
            sensor_h_mm: sensor height, mm.
            width: image width, pixels.
            height: image height, pixels.

        Raises:
            ValueError: if the inputs are degenerate.
        """
        if not agl_m or agl_m <= 0:
            raise ValueError("CameraModel requires a positive AGL altitude")
        if not width or not height or width <= 0 or height <= 0:
            raise ValueError("CameraModel requires positive image dimensions")
        if not focal_mm or not sensor_w_mm or not sensor_h_mm:
            raise ValueError("CameraModel requires valid lens intrinsics")

        self.agl_m = float(agl_m)
        self.width = float(width)
        self.height = float(height)
        self.pitch_deg = float(pitch_deg)  # -90 = nadir (straight down)

        # Intrinsics: focal length in pixels, principal point at image centre.
        # Sensors have square pixels, so fx == fy. The datasheet sensor size
        # describes the *full* sensor, but many images are a cropped-aspect
        # readout (e.g. a 16:9 frame crops the sensor height, a 4:3 frame crops
        # a 3:2 sensor's width). On the cropped axis, datasheet_mm / image_px
        # overstates the pixel pitch and would shrink that axis' focal length,
        # skewing the projection. The uncropped axis yields the true pitch, so
        # take the smaller of the two (the cropped axis is always the inflated
        # one) and apply it to both axes.
        pixel_pitch_mm = min(sensor_w_mm / width, sensor_h_mm / height)
        self.fx = focal_mm / pixel_pitch_mm
        self.fy = self.fx
        self.cx = width / 2.0
        self.cy = height / 2.0

        # Camera axes expressed in the NED frame - same construction as
        # AOINeighborService.gps_to_pixel (elevation = pitch, azimuth = yaw).
        elev = math.radians(pitch_deg)
        az = math.radians(yaw_deg)
        cos_e, sin_e = math.cos(elev), math.sin(elev)
        cos_a, sin_a = math.cos(az), math.sin(az)

        # Camera Z (optical axis) and Y (image-down) in NED.
        self._r3 = (cos_e * cos_a, cos_e * sin_a, -sin_e)
        self._r2 = (sin_e * cos_a, sin_e * sin_a, cos_e)
        # Camera X (image-right) = cross(optical axis, up), normalised.
        up = (-sin_e * cos_a, -sin_e * sin_a, -cos_e)  # = -r2
        r1 = (
            self._r3[1] * up[2] - self._r3[2] * up[1],
            self._r3[2] * up[0] - self._r3[0] * up[2],
            self._r3[0] * up[1] - self._r3[1] * up[0],
        )
        norm = math.sqrt(r1[0] ** 2 + r1[1] ** 2 + r1[2] ** 2)
        if norm < 1e-10:
            raise ValueError("CameraModel: degenerate camera orientation")
        self._r1 = (r1[0] / norm, r1[1] / norm, r1[2] / norm)

    @classmethod
    def from_image_service(cls, image_service, agl_override_m=None):
        """Build a CameraModel from an ImageService.

        Args:
            image_service: an ImageService for the loaded image.
            agl_override_m: optional AGL altitude (metres) overriding metadata.

        Returns:
            CameraModel, or None when the metadata needed to build one
            (intrinsics, altitude, image array) is unavailable.
        """
        try:
            intrinsics = image_service.get_camera_intrinsics()
            if intrinsics is None:
                return None

            if agl_override_m and agl_override_m > 0:
                agl = agl_override_m
            else:
                agl = image_service.get_relative_altitude('m')
            if not agl or agl <= 0:
                return None

            pitch = image_service.get_camera_pitch()
            if pitch is None:
                pitch = -90.0  # assume nadir when the gimbal angle is missing
            yaw = image_service.get_camera_yaw() or 0.0

            img = image_service.img_array
            if img is None:
                return None
            height, width = img.shape[:2]

            return cls(
                agl, pitch, yaw,
                intrinsics['focal_length_mm'],
                intrinsics['sensor_width_mm'],
                intrinsics['sensor_height_mm'],
                width, height,
            )
        except Exception:
            return None

    def project(self, north, east, down) -> Optional[Tuple[float, float]]:
        """Project a 3D NED point (relative to the camera) to a pixel.

        Args:
            north, east, down: point coordinates in metres, relative to the
                camera (down is positive below the camera).

        Returns:
            (u, v) pixel coordinates, or None if the point is at or behind
            the image plane.
        """
        point = (north, east, down)
        cam_x = self._dot(self._r1, point)
        cam_y = self._dot(self._r2, point)
        cam_z = self._dot(self._r3, point)
        if cam_z <= 1e-6:
            return None
        u = (cam_x / cam_z) * self.fx + self.cx
        v = (cam_y / cam_z) * self.fy + self.cy
        return u, v

    def pixel_ray(self, u, v) -> Tuple[float, float, float]:
        """Return the NED direction of the ray through pixel (u, v).

        The ray is not normalised; its components are convenient for
        intersecting horizontal planes (the down component is the per-unit
        descent rate).
        """
        a = (u - self.cx) / self.fx
        b = (v - self.cy) / self.fy
        return (
            a * self._r1[0] + b * self._r2[0] + self._r3[0],
            a * self._r1[1] + b * self._r2[1] + self._r3[1],
            a * self._r1[2] + b * self._r2[2] + self._r3[2],
        )

    def pixel_to_ground(self, u, v, ground_down=None) -> Optional[Tuple[float, float, float]]:
        """Cast the ray through pixel (u, v) onto a horizontal ground plane.

        Args:
            u, v: pixel coordinates.
            ground_down: depth (metres below the camera) of the ground plane.
                Defaults to the camera AGL - i.e. flat ground at nadir level.

        Returns:
            (north, east, down) of the intersection, or None if the ray does
            not descend to the plane.
        """
        if ground_down is None:
            ground_down = self.agl_m
        ray = self.pixel_ray(u, v)
        if ray[2] <= 1e-9:
            return None  # ray is level or points upward
        t = ground_down / ray[2]
        if t <= 0:
            return None
        return (t * ray[0], t * ray[1], t * ray[2])

    @staticmethod
    def _dot(a, b):
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
