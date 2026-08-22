"""
AOINeighborService - Service for tracking AOIs across neighboring images.

Provides methods to:
- Calculate if a GPS coordinate falls within an image's coverage
- Convert GPS coordinates back to pixel coordinates
- Extract thumbnails from images at specific GPS locations
"""

import math
import numpy as np
import cv2
from pathlib import Path
from PIL import Image
from helpers.MetaDataHelper import MetaDataHelper
from helpers.LocationInfo import LocationInfo
from helpers.GeodesicHelper import GeodesicHelper
from helpers.PhotogrammetryHelper import (
    FovHomography, validate_alignment, build_camera_to_ned
)
from core.services.image.ImageService import ImageService
from core.services.GSDService import GSDService
from core.services.LoggerService import LoggerService
# Reuse AOIService's lazy terrain accessor rather than building a second one:
# it refreshes the singleton's offline floor from the app preference on every
# fetch, and two accessors would mean two places to keep that behaviour.
from core.services.image.AOIService import AOIService, _get_terrain_service


class AOINeighborService:
    """Service for tracking AOI GPS coordinates across neighboring images."""

    # How far inside the frame the projected point must fall for the image to
    # count as showing the AOI. Small and fixed: it answers "is this really in
    # frame", which has nothing to do with how much context the crop shows.
    EDGE_MARGIN_PX = 50

    # Radius of the "the AOI is somewhere in here" ring, in METRES on the
    # ground, converted to pixels per image via that image's GSD so it stays
    # honest at any altitude.
    #
    # Measured on a real DJI flight by comparing where ADIAT's own detector
    # found the same tarp in each capture: adjacent frames disagree by ~1.5 m,
    # rising to ~3.9 m five frames out, mean 2.2 m. Most of that is a gimbal
    # yaw stamped ~4.5 degrees off the aircraft's actual heading (it is held
    # constant across a flight line while the heading wanders); the remainder
    # is the aircraft's own GPS noise. 3 m covers the bulk of it without
    # drawing a ring so large it stops meaning anything.
    POSITION_UNCERTAINTY_M = 3.0

    def __init__(self):
        """Initialize the AOINeighborService."""
        self.logger = LoggerService()
        # Image metadata does not change on disk during a session, so repeated
        # searches (and the radius estimate) reuse it instead of re-reading
        # EXIF/XMP for every image on every Z press. Keyed per method below.
        self._center_gps_cache = {}
        self._coverage_meta_cache = {}

    @staticmethod
    def _get_image_dimensions(path):
        """Read image dimensions from the file header without decoding pixels.

        PIL reads only the header on open. The result matches
        cv2.imdecode(IMREAD_UNCHANGED) — the loader ImageService uses —
        because neither applies EXIF orientation.

        Args:
            path (str): Image file path

        Returns:
            tuple or None: (width, height), or None if the header can't be read
        """
        try:
            with Image.open(path) as img:
                return img.size
        except Exception:
            return None

    def _make_deferred_service(self, image, exif_data=None):
        """Create an ImageService that reads metadata now but pixels lazily."""
        return ImageService(
            image['path'],
            image.get('mask_path', ''),
            calculated_bearing=image.get('bearing'),
            exif_data=exif_data,
            defer_load=True
        )

    def get_image_coverage_info(self, image, agl_override_m=None, include_service=True):
        """
        Get the coverage information for an image including its corner GPS coordinates.

        Metadata-only and cached: no pixel decode happens here. The returned
        dict is a copy, so callers may mutate it (e.g. terrain-adjusted
        altitude) without corrupting the cache.

        Args:
            image (dict): Image metadata dict with 'path' key
            agl_override_m (float, optional): Manual AGL altitude override in meters
            include_service (bool): Attach a lazily-loading ImageService under
                'image_service'. Callers that only test coverage can pass False
                and skip the metadata reads its construction performs.

        Returns:
            dict or None: Coverage info with center GPS, dimensions, orientation
        """
        try:
            cache_key = (image['path'], agl_override_m, image.get('bearing'))
            cached = self._coverage_meta_cache.get(cache_key)
            # The FOV alignment can change mid-session (Align Image tool), so a
            # cache entry is only valid while the refinement it saw is current
            if cached is not None and cached['refinement_source'] == image.get('fov_alignment'):
                if cached['meta'] is None:
                    return None
                info = dict(cached['meta'])
                if include_service:
                    info['image_service'] = self._make_deferred_service(image)
                return info

            def remember(meta):
                self._coverage_meta_cache[cache_key] = {
                    'refinement_source': image.get('fov_alignment'),
                    'meta': meta
                }
                return meta

            # Get EXIF data and GPS
            exif_data = MetaDataHelper.get_exif_data_piexif(image['path'])
            gps_coords = LocationInfo.get_gps(exif_data=exif_data)
            if not gps_coords:
                return remember(None)
            lat0, lon0 = gps_coords['latitude'], gps_coords['longitude']

            # Metadata reads only — pixels are not loaded unless the PIL
            # header fallback below needs them
            image_service = self._make_deferred_service(image, exif_data=exif_data)

            # Get camera orientation. Read exactly what AOIService.estimate_aoi_gps
            # reads, including roll: the AOI's GPS was produced by that method,
            # and this method's job is to invert it. Any input one side honours
            # and the other ignores lands the AOI somewhere it is not -- a
            # WALDO +-22.5 degree pod tilt alone is worth ~1500 px.
            yaw = image_service.get_camera_yaw() or 0.0
            pitch = image_service.get_camera_pitch()
            if pitch is None:
                pitch = -90  # assume nadir
            roll = image_service.get_gimbal_roll() or 0.0
            if abs(roll) > 90.0:
                # DJI's "inverted gimbal" pattern; get_camera_yaw already
                # compensates by flipping yaw 180, so honouring roll too would
                # double-rotate. Same rule as AOIService.
                roll = 0.0
            roll_axis = image_service.get_roll_axis_azimuth() if roll else None

            # A manually aligned image can produce coverage info even when its
            # metadata (altitude, intrinsics) is missing or unreliable.
            refinement = image.get('fov_alignment')
            has_refinement = bool(
                refinement and refinement.get('corners')
                and validate_alignment(refinement['corners'])
            )

            # Get altitude
            if agl_override_m and agl_override_m > 0:
                altitude = agl_override_m
            else:
                altitude = image_service.get_relative_altitude('m') or 0

            if altitude <= 0 and not has_refinement:
                return remember(None)

            # Get image dimensions from the header; fall back to a decode for
            # formats PIL cannot header-read
            dims = self._get_image_dimensions(image['path'])
            if dims is not None:
                width, height = dims
            else:
                height, width = image_service.img_array.shape[:2]

            # Get camera intrinsics
            intrinsics = image_service.get_camera_intrinsics()
            if intrinsics is None:
                if not has_refinement:
                    return remember(None)
                focal_mm = sensor_w_mm = sensor_h_mm = None
            else:
                focal_mm = intrinsics['focal_length_mm']
                sensor_w_mm = intrinsics['sensor_width_mm']
                sensor_h_mm = intrinsics['sensor_height_mm']

            # Convert pitch to tilt angle
            tilt_angle = 90 + pitch
            tilt_angle = max(0, min(90, tilt_angle))

            meta = remember({
                'center_lat': lat0,
                'center_lon': lon0,
                'yaw': yaw,
                'pitch': pitch,
                'roll': roll,
                'roll_axis_azimuth': roll_axis,
                'tilt_angle': tilt_angle,
                'altitude': altitude,
                'asl_altitude': image_service.get_asl_altitude('m'),
                'width': width,
                'height': height,
                'focal_mm': focal_mm,
                'sensor_w_mm': sensor_w_mm,
                'sensor_h_mm': sensor_h_mm,
                'fov_alignment': refinement if has_refinement else None,
            })

            info = dict(meta)
            if include_service:
                info['image_service'] = image_service
            return info

        except Exception as e:
            self.logger.error(f"AOINeighborService: Failed to get image coverage info - {e}")
            return None

    def gps_to_pixel(self, target_lat, target_lon, coverage_info):
        """
        Convert GPS coordinates to pixel coordinates in an image.

        Uses the analytical inverse of the 3D ray-cast in
        AOIService._calculate_ground_position for accurate results with
        both nadir and oblique imagery.

        Args:
            target_lat (float): Target latitude
            target_lon (float): Target longitude
            coverage_info (dict): Coverage info from get_image_coverage_info

        Returns:
            tuple or None: (x, y) pixel coordinates or None if not in image
        """
        try:
            # Manually aligned image: invert the homography directly.
            refinement = coverage_info.get('fov_alignment')
            if refinement and refinement.get('corners'):
                homography = FovHomography(
                    refinement['corners'],
                    coverage_info['width'], coverage_info['height'],
                    refinement.get('tie_points')
                )
                return homography.gps_to_pixel(target_lat, target_lon)

            lat0 = coverage_info['center_lat']
            lon0 = coverage_info['center_lon']
            yaw = coverage_info['yaw']
            pitch = coverage_info.get('pitch', -90)
            altitude = coverage_info['altitude']
            width = coverage_info['width']
            height = coverage_info['height']
            focal_mm = coverage_info['focal_mm']
            sensor_w_mm = coverage_info['sensor_w_mm']
            sensor_h_mm = coverage_info['sensor_h_mm']

            # Convert GPS difference to NED offset in meters
            R_earth = 6378137.0
            dlat_rad = math.radians(target_lat - lat0)
            dlon_rad = math.radians(target_lon - lon0)
            north = dlat_rad * R_earth
            east = dlon_rad * R_earth * math.cos(math.radians(lat0))

            # The exact rotation AOIService._calculate_ground_position used, by
            # construction rather than by duplication -- including gimbal roll.
            R = build_camera_to_ned(
                pitch, yaw,
                coverage_info.get('roll', 0.0) or 0.0,
                coverage_info.get('roll_axis_azimuth')
            )
            if R is None:
                return None
            # Columns are the camera axes in NED, so R @ [a, b, 1] is
            # a*r1 + b*r2 + r3.
            r1, r2, r3 = R[:, 0], R[:, 1], R[:, 2]

            # Solve the inverse of the forward projection analytically.
            # Forward: ground = H * (R @ [a, b, 1]) / (R @ [a, b, 1])_z
            #   where a = (u-cx)/fx, b = (v-cy)/fy
            # Rearranging into a 2x2 linear system:
            #   a*(N*r1z - H*r1x) + b*(N*r2z - H*r2x) = H*r3x - N*r3z
            #   a*(E*r1z - H*r1y) + b*(E*r2z - H*r2y) = H*r3y - E*r3z
            H = altitude
            N = north
            E = east

            A11 = N * r1[2] - H * r1[0]
            A12 = N * r2[2] - H * r2[0]
            A21 = E * r1[2] - H * r1[1]
            A22 = E * r2[2] - H * r2[1]
            c1 = H * r3[0] - N * r3[2]
            c2 = H * r3[1] - E * r3[2]

            det = A11 * A22 - A12 * A21
            if abs(det) < 1e-12:
                return None

            a = (c1 * A22 - c2 * A12) / det
            b = (A11 * c2 - A21 * c1) / det

            # Convert normalized camera coordinates back to pixels
            fx = focal_mm / (sensor_w_mm / width)
            fy = focal_mm / (sensor_h_mm / height)
            cx = width / 2.0
            cy = height / 2.0

            u = a * fx + cx
            v = b * fy + cy

            # Verify the ray points downward (valid ground intersection)
            ray_z = r1[2] * a + r2[2] * b + r3[2]
            if ray_z <= 0:
                return None

            return (u, v)

        except Exception as e:
            self.logger.error(f"AOINeighborService: Failed to convert GPS to pixel - {e}")
            return None

    def _terrain_adjusted_altitude(self, coverage_info, aoi_terrain_elevation_m):
        """Height of this camera above the AOI's ground, not above its own.

        The forward projection positions the AOI with a terrain-corrected
        effective AGL (AOIService._calculate_with_terrain). Inverting it with
        the neighbour's raw EXIF RelativeAltitude assumes flat ground between
        the two, so on real relief the AOI lands short or long -- 30 m of
        relief at 100 m AGL moves it ~625 px, several thumbnails' worth.

        Builds BOTH estimates the forward pass builds -- the absolute-elevation
        chain and the terrain-relief chain -- and picks between them with
        AOIService._select_effective_agl, the same function. Rebuilding only
        the relief estimate here was wrong: the forward pass PREFERS the
        absolute chain whenever the two agree within tolerance, so on a dataset
        with a trustworthy geoid/ASL (RTK) the two sides silently chose
        different altitudes. They can differ by the whole tolerance -- 15% or
        8 m -- which at the frame corner is ~300 px, far outside the crop.

        Args:
            coverage_info (dict): This image's coverage metadata.
            aoi_terrain_elevation_m (float or None): Ground elevation at the
                AOI, from the forward calculation. None disables the
                adjustment.

        Returns:
            float: Altitude to project with. The unadjusted value whenever the
            DEM cannot answer for this camera's position, so a terrain gap
            degrades to today's flat-earth behaviour rather than to nothing.
        """
        altitude = coverage_info['altitude']
        if aoi_terrain_elevation_m is None:
            return altitude

        terrain_service = _get_terrain_service()
        if terrain_service is None or not terrain_service.enabled:
            return altitude

        lat, lon = coverage_info['center_lat'], coverage_info['center_lon']
        try:
            camera_ground = terrain_service.get_elevation(lat, lon)
            geoid = terrain_service.get_geoid_undulation(lat, lon)
        except Exception:
            return altitude
        if camera_ground.source != 'terrain' or camera_ground.elevation_m is None:
            return altitude

        # Terrain-relief estimate: robust to a bad geoid or a non-ellipsoidal
        # ASL, because any datum offset cancels in the DEM difference.
        agl_rel = altitude + (camera_ground.elevation_m - aoi_terrain_elevation_m)

        # Absolute-elevation estimate: more precise when the datum is sound.
        agl_abs = None
        asl = coverage_info.get('asl_altitude')
        if asl is not None and geoid is not None:
            agl_abs = (asl - geoid) - aoi_terrain_elevation_m

        # Called unbound with this service as `self`: the method reads nothing
        # off the instance but `.logger`, which both services carry. Sharing
        # the real selection matters more than the awkward call -- a
        # reimplementation here is exactly how the two sides drifted apart.
        effective = AOIService._select_effective_agl(
            self, agl_abs, agl_rel, altitude, geoid, camera_ground,
            aoi_terrain_elevation_m
        )
        # Same floor as the forward path: a non-positive AGL has no ground
        # intersection at all, and would drop the image from the results.
        return max(1.0, effective)

    def _uncertainty_radius_px(self, coverage_info):
        """POSITION_UNCERTAINTY_M expressed in this image's pixels.

        Uses the same GSDService the rest of the app uses, so the ring means
        the same ground distance whatever the altitude. Returns None when the
        intrinsics are missing (a manually aligned image can reach here with
        focal/sensor unset), which makes extract_thumbnail fall back to the
        plain marker rather than draw a ring of invented radius.
        """
        try:
            if not coverage_info.get('focal_mm') or not coverage_info.get('sensor_w_mm'):
                return None
            gsd_cm = GSDService(
                focal_length=coverage_info['focal_mm'],
                image_size=(coverage_info['width'], coverage_info['height']),
                altitude=coverage_info['altitude'],
                tilt_angle=coverage_info['tilt_angle'],
                sensor=(coverage_info['sensor_w_mm'], coverage_info['sensor_h_mm'])
            ).compute_average_gsd()
            if not gsd_cm or gsd_cm <= 0:
                return None
            return self.POSITION_UNCERTAINTY_M / (gsd_cm / 100.0)
        except Exception:
            return None

    def is_point_in_image(self, pixel_x, pixel_y, width, height, margin=0):
        """
        Check if pixel coordinates are within the image bounds.

        Args:
            pixel_x (float): X coordinate in pixels
            pixel_y (float): Y coordinate in pixels
            width (int): Image width
            height (int): Image height
            margin (int): Optional margin to consider point out of bounds

        Returns:
            bool: True if point is within image bounds
        """
        return (margin <= pixel_x < width - margin and
                margin <= pixel_y < height - margin)

    def _get_image_center_gps(self, image):
        """
        Get the center GPS coordinates for an image (lightweight, no full coverage calc).

        Args:
            image (dict): Image metadata dict with 'path' key

        Returns:
            tuple or None: (latitude, longitude) or None if not available
        """
        path = image.get('path')
        if path in self._center_gps_cache:
            return self._center_gps_cache[path]
        center = None
        try:
            exif_data = MetaDataHelper.get_exif_data_piexif(path)
            gps_coords = LocationInfo.get_gps(exif_data=exif_data)
            if gps_coords:
                center = (gps_coords['latitude'], gps_coords['longitude'])
        except Exception:
            pass
        self._center_gps_cache[path] = center
        return center

    def _estimate_max_coverage_radius(self, images, agl_override_m=None):
        """
        Estimate the maximum ground coverage radius for images in the dataset.

        Samples a few images to determine the maximum distance from image center
        to corner, which represents the maximum radius where an AOI could be visible.

        Args:
            images (list): List of all images
            agl_override_m (float, optional): Manual AGL altitude override

        Returns:
            float: Maximum coverage radius in meters (default 500m if estimation fails)
        """
        max_radius = 0
        sample_count = min(10, len(images))  # Sample first few images

        for i in range(sample_count):
            try:
                coverage_info = self.get_image_coverage_info(images[i], agl_override_m, include_service=False)
                if coverage_info:
                    # Calculate diagonal coverage distance using GSD
                    gsd_service = GSDService(
                        focal_length=coverage_info['focal_mm'],
                        image_size=(coverage_info['width'], coverage_info['height']),
                        altitude=coverage_info['altitude'],
                        tilt_angle=coverage_info['tilt_angle'],
                        sensor=(coverage_info['sensor_w_mm'], coverage_info['sensor_h_mm'])
                    )
                    avg_gsd_cm = gsd_service.compute_average_gsd()
                    if avg_gsd_cm is None:
                        continue
                    avg_gsd_m = avg_gsd_cm / 100.0

                    # Diagonal distance from center to corner
                    half_width = (coverage_info['width'] / 2) * avg_gsd_m
                    half_height = (coverage_info['height'] / 2) * avg_gsd_m
                    radius = math.sqrt(half_width**2 + half_height**2)
                    max_radius = max(max_radius, radius)
            except Exception:
                continue

        # Add 20% buffer for safety, default to 500m if estimation fails
        return max_radius * 1.2 if max_radius > 0 else 500

    def extract_thumbnail(self, image_service, pixel_x, pixel_y, radius=100,
                          uncertainty_px=None):
        """
        Extract a thumbnail centered at the given pixel coordinates.

        Args:
            image_service (ImageService): Image service with loaded image
            pixel_x (float): X coordinate in pixels
            pixel_y (float): Y coordinate in pixels
            radius (int): Radius of the thumbnail in pixels
            uncertainty_px (float, optional): Radius, in this image's pixels,
                of the ring marking where the AOI may actually be. None or a
                degenerate value falls back to the plain centre marker.

        Returns:
            np.ndarray or None: Thumbnail image array (RGB)
        """
        try:
            img_array = image_service.img_array
            height, width = img_array.shape[:2]

            # Calculate bounding box
            x1 = max(0, int(pixel_x - radius))
            y1 = max(0, int(pixel_y - radius))
            x2 = min(width, int(pixel_x + radius))
            y2 = min(height, int(pixel_y + radius))

            # Extract the region
            if x2 <= x1 or y2 <= y1:
                return None

            thumbnail = img_array[y1:y2, x1:x2].copy()

            center_x = int(pixel_x - x1)
            center_y = int(pixel_y - y1)

            # A ring at the real positional uncertainty, not a tight circle on
            # the nominal point. The projection is only as good as each
            # image's gimbal/GPS metadata, and neighbouring captures disagree
            # about where the same ground object is by metres -- measured 1.5 m
            # between adjacent frames of a real DJI flight, ~4 m five frames
            # out, driven mostly by a gimbal-yaw bias against the actual
            # heading. A 10 px circle asserted 13 cm precision it never had and
            # pointed the reviewer confidently at bare ground. The ring says
            # "the AOI is somewhere in here", which is the true claim and the
            # one that makes the reviewer search rather than dismiss.
            if uncertainty_px and uncertainty_px > 12:
                cv2.circle(thumbnail, (center_x, center_y),
                           int(uncertainty_px), (255, 0, 0), 2)
                # Small tick at the nominal point so the ring's centre is
                # readable without implying that is where the AOI is.
                cv2.drawMarker(thumbnail, (center_x, center_y), (255, 0, 0),
                               markerType=cv2.MARKER_CROSS, markerSize=14,
                               thickness=1)
            else:
                # No usable scale (missing intrinsics): fall back to the plain
                # marker rather than drawing a ring of meaningless radius.
                cv2.circle(thumbnail, (center_x, center_y), 10, (255, 0, 0), 2)

            return thumbnail

        except Exception as e:
            self.logger.error(f"AOINeighborService: Failed to extract thumbnail - {e}")
            return None

    def find_aoi_in_neighbors(self, images, current_image_idx, aoi_gps, agl_override_m=None,
                              thumbnail_radius=100, progress_callback=None, max_results=50,
                              aoi_terrain_elevation_m=None, should_cancel=None):
        """
        Find all images that contain the AOI GPS coordinate.

        Uses GPS-based filtering to efficiently search all images, not just
        sequential neighbors. This handles drone lawn-mower flight patterns
        where parallel flight paths may also contain the AOI.

        Args:
            images (list): List of all images
            current_image_idx (int): Index of the current image
            aoi_gps (tuple): (latitude, longitude) of the AOI
            agl_override_m (float, optional): Manual AGL altitude override
            thumbnail_radius (int): Radius of thumbnails to extract
            progress_callback (callable, optional): Callback for progress updates
            max_results (int): Maximum number of results to return (default 50)
            aoi_terrain_elevation_m (float, optional): Ground elevation at the
                AOI, from the forward calculation. Lets each candidate be
                projected from its height above the AOI's ground rather than
                above its own, which is what the forward pass assumed.
            should_cancel (callable, optional): Polled between images; return
                True to abandon the search. Without it Cancel was cosmetic --
                the flag it set was never read here, so the worker kept reading
                EXIF and decoding full-resolution images for the rest of the
                flight while the user waited on a dialog that had already
                closed.

        Returns:
            tuple: (results, truncated). Results are dicts with thumbnail info,
            sorted by image index -- whatever was found so far when cancelled.
            ``truncated`` is True when the max_results cap stopped the search
            with candidates still unchecked, so the caller can say so rather
            than presenting a capped count as the answer.
        """
        results = []
        truncated = False
        target_lat, target_lon = aoi_gps

        if progress_callback:
            progress_callback("Calculating search area...")

        # Estimate maximum coverage radius for GPS-based pre-filtering
        max_coverage_radius = self._estimate_max_coverage_radius(images, agl_override_m)

        # Build list of candidate images based on GPS proximity. Cancellable:
        # this reads EXIF for every capture in the flight, which on a large
        # sortie is itself a long operation.
        candidates = []
        for i, image in enumerate(images):
            if should_cancel and should_cancel():
                return [], False
            center_gps = self._get_image_center_gps(image)
            if center_gps:
                center_lat, center_lon = center_gps
                distance = GeodesicHelper.haversine_distance(
                    target_lat, target_lon, center_lat, center_lon
                )
                # Only consider images within maximum coverage radius
                if distance <= max_coverage_radius:
                    candidates.append((i, distance))

        # Sort candidates by distance (closest first for better UX)
        candidates.sort(key=lambda x: x[1])

        if progress_callback:
            progress_callback(f"Checking {len(candidates)} candidate images...")

        # Check each candidate image. The per-image cost here is a full-
        # resolution decode on a hit, so the cancel check goes before the work.
        for idx, (i, _) in enumerate(candidates):
            if should_cancel and should_cancel():
                break
            if progress_callback:
                progress_callback(f"Checking image {idx + 1} of {len(candidates)}...")

            result = self._check_image_for_aoi(
                images[i], i, target_lat, target_lon, agl_override_m, thumbnail_radius,
                aoi_terrain_elevation_m
            )
            if result:
                # Mark if this is the current/originating image
                if i == current_image_idx:
                    result['is_current'] = True
                results.append(result)

                # Stop if we've hit the maximum
                if len(results) >= max_results:
                    truncated = idx + 1 < len(candidates)
                    break

        # Sort results by image index for consistent display order
        results.sort(key=lambda r: r['image_idx'])

        return results, truncated

    def _check_image_for_aoi(self, image, image_idx, target_lat, target_lon,
                             agl_override_m=None, thumbnail_radius=100,
                             aoi_terrain_elevation_m=None):
        """
        Check if an AOI GPS coordinate is visible in an image and extract thumbnail.

        Args:
            image (dict): Image metadata dict
            image_idx (int): Image index
            target_lat (float): Target latitude
            target_lon (float): Target longitude
            agl_override_m (float, optional): Manual AGL altitude override
            thumbnail_radius (int): Radius of thumbnail to extract

        Returns:
            dict or None: Thumbnail info if AOI is visible, None otherwise
        """
        try:
            # Coverage is metadata-only here; most candidates are rejected by
            # the bounds check below without their pixels ever being decoded
            coverage_info = self.get_image_coverage_info(image, agl_override_m, include_service=False)
            if not coverage_info:
                return None

            # Safe to mutate: get_image_coverage_info returns a copy, so the
            # cached metadata keeps its unadjusted altitude.
            coverage_info['altitude'] = self._terrain_adjusted_altitude(
                coverage_info, aoi_terrain_elevation_m
            )

            # Convert GPS to pixel coordinates
            pixel_coords = self.gps_to_pixel(target_lat, target_lon, coverage_info)
            if not pixel_coords:
                return None

            pixel_x, pixel_y = pixel_coords

            # Is the AOI actually inside this frame? A small fixed margin, NOT
            # one derived from the crop size: the crop is deliberately much
            # wider than the AOI (it has to cover the metadata's positional
            # error), and scaling the rejection margin with it would throw away
            # images that genuinely show the AOI simply because it sits nearer
            # the edge than half a crop. extract_thumbnail already clips the
            # crop to the image bounds, so a near-edge hit is fine to keep.
            margin = self.EDGE_MARGIN_PX
            if not self.is_point_in_image(
                pixel_x, pixel_y,
                coverage_info['width'], coverage_info['height'],
                margin
            ):
                return None

            # Confirmed hit: decode the image now, only for the thumbnail
            image_service = ImageService(
                image['path'],
                image.get('mask_path', ''),
                calculated_bearing=image.get('bearing')
            )
            thumbnail = self.extract_thumbnail(
                image_service, pixel_x, pixel_y, thumbnail_radius,
                uncertainty_px=self._uncertainty_radius_px(coverage_info)
            )
            if thumbnail is None:
                return None

            # Get image name
            image_name = Path(image['path']).name

            return {
                'image_idx': image_idx,
                'image_name': image_name,
                'image_path': image['path'],
                'pixel_x': pixel_x,
                'pixel_y': pixel_y,
                'thumbnail': thumbnail,
                'is_current': False
            }

        except Exception as e:
            self.logger.error(f"AOINeighborService: Error checking image {image_idx} - {e}")
            return None
