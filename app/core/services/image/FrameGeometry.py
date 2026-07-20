"""
FrameGeometry - a public camera pose + intrinsics snapshot for one image frame.

Promoted out of ``ImageService._get_projection_context`` so the Coverage/POD
pipeline (and, eventually, CoverageExtentService) can collect a frame's geometry
once, in one place. It carries pose (lat/lon/AGL/yaw/pitch/roll) and intrinsics
(focal, sensor, image size, principal point) but deliberately performs **no**
terrain access: ``cam_elev_m`` is left for the caller to resolve against the
frame's own DEM so the datum rule ``cam_elev = DEM(nadir) + AGL`` holds by
construction (a constant vertical datum offset cancels).

Lives in the image package (pose/intrinsics is image metadata), keeping the
dependency flow one-way: coverage -> image, never the reverse.
"""

from dataclasses import dataclass
from typing import Optional, Tuple, TYPE_CHECKING

from helpers.LocationInfo import LocationInfo

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids importing ImageService
    from core.services.image.ImageService import ImageService

# BearingResult.confidence is never set != 1.0 by BearingCalculationService and is
# not persisted in ADIAT_Data.xml (only bearing / bearing_source / bearing_quality
# are). So the persisted quality string is the actual confidence signal available
# for track-interpolated ("calculated") yaw.
BEARING_QUALITY_CONFIDENCE = {
    'good': 0.9,
    'turn_inferred': 0.6,
    'gap': 0.4,
    'hover_estimate': 0.3,
}
DEFAULT_CALCULATED_CONFIDENCE = 0.5   # 'calculated' yaw with unknown/absent quality
NO_YAW_CONFIDENCE = 0.25              # no yaw metadata at all -> assumed 0 deg


@dataclass
class FrameGeometry:
    """Camera pose + intrinsics for a single frame (see module docstring)."""

    lat: float                                   # camera nadir point (EXIF GPS)
    lon: float
    agl_m: float                                 # reported AGL (or custom override)
    yaw_deg: float                               # camera yaw, 0=N, 90=E
    pitch_deg: float                             # 0 = horizon, -90 = nadir
    roll_deg: float                              # gimbal roll; 0 when |roll|>90 (inverted-gimbal flag)
    focal_mm: float
    sensor_mm: Tuple[float, float]               # (width_mm, height_mm)
    image_size: Tuple[int, int]                  # (width_px, height_px)
    principal_point_mm: Optional[Tuple[float, float]]  # None -> image center
    yaw_source: str                              # 'gimbal' | 'flight' | 'calculated' | 'default'
    bearing_confidence: float                    # 1.0 for gimbal/flight; mapped for 'calculated'; 0.25 for 'default'
    asl_alt_m: Optional[float] = None            # raw EXIF ASL altitude (datum fallback only)
    cam_elev_m: Optional[float] = None           # filled by the caller: DEM(nadir) + agl_m

    @classmethod
    def from_image_service(cls, image_service: "ImageService",
                           custom_altitude_ft: Optional[float] = None,
                           bearing_quality: Optional[str] = None,
                           agl_override_ft: Optional[float] = None
                           ) -> Optional["FrameGeometry"]:
        """Collect pose + intrinsics from an ``ImageService``.

        Returns ``None`` when GPS, intrinsics, image size, or a positive AGL is
        unavailable. Performs no terrain access (``cam_elev_m`` stays ``None``).

        Args:
            image_service: the source ImageService.
            custom_altitude_ft: overrides XMP AGL when > 0 (feet).
            bearing_quality: persisted ``bearing_quality`` string for the frame,
                used to set confidence when yaw falls back to track interpolation.
            agl_override_ft: highest-priority AGL override in feet (e.g. a
                Wingtra per-image AGL); takes precedence over ``custom_altitude_ft``.
        """
        try:
            gps = LocationInfo.get_gps(exif_data=image_service.exif_data)
            if not gps:
                return None
            lat = gps['latitude']
            lon = gps['longitude']

            intrinsics = image_service.get_camera_intrinsics()
            if intrinsics is None:
                return None

            image_size = cls._resolve_image_size(image_service)
            if image_size is None:
                return None

            agl_m = cls._resolve_agl_m(image_service, custom_altitude_ft, agl_override_ft)
            if agl_m is None or agl_m <= 0:
                return None

            yaw_deg, yaw_source = image_service.get_camera_yaw_with_source()
            if yaw_deg is None:
                yaw_deg = 0.0
                yaw_source = 'default'

            pitch_deg = image_service.get_camera_pitch()
            if pitch_deg is None:
                pitch_deg = -90.0

            roll_deg = image_service.get_gimbal_roll() or 0.0
            if abs(roll_deg) > 90.0:
                roll_deg = 0.0

            return cls(
                lat=lat,
                lon=lon,
                agl_m=agl_m,
                yaw_deg=yaw_deg,
                pitch_deg=pitch_deg,
                roll_deg=roll_deg,
                focal_mm=intrinsics['focal_length_mm'],
                sensor_mm=(intrinsics['sensor_width_mm'], intrinsics['sensor_height_mm']),
                image_size=image_size,
                principal_point_mm=None,
                yaw_source=yaw_source,
                bearing_confidence=cls._confidence_for(yaw_source, bearing_quality),
                asl_alt_m=image_service.get_asl_altitude('m'),
                cam_elev_m=None,
            )
        except Exception:
            return None

    @staticmethod
    def _resolve_image_size(image_service) -> Optional[Tuple[int, int]]:
        """(width_px, height_px) from the loaded array, else EXIF dimensions."""
        arr = getattr(image_service, 'img_array', None)
        if arr is not None:
            h, w = arr.shape[:2]
            return int(w), int(h)
        try:
            import piexif
            exif = image_service.exif_data.get("Exif", {})
            w = exif.get(piexif.ExifIFD.PixelXDimension)
            h = exif.get(piexif.ExifIFD.PixelYDimension)
            if w and h:
                return int(w), int(h)
        except Exception:
            pass
        return None

    @staticmethod
    def _resolve_agl_m(image_service, custom_altitude_ft, agl_override_ft) -> Optional[float]:
        """Reported AGL in meters by priority: override -> custom -> XMP AGL."""
        if agl_override_ft is not None and agl_override_ft > 0:
            return agl_override_ft / 3.28084
        if custom_altitude_ft is not None and custom_altitude_ft > 0:
            return custom_altitude_ft / 3.28084
        return image_service.get_relative_altitude('m')

    @staticmethod
    def _confidence_for(yaw_source: str, bearing_quality: Optional[str]) -> float:
        if yaw_source in ('gimbal', 'flight'):
            return 1.0
        if yaw_source == 'calculated':
            return BEARING_QUALITY_CONFIDENCE.get(bearing_quality, DEFAULT_CALCULATED_CONFIDENCE)
        return NO_YAW_CONFIDENCE
