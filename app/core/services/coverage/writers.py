"""
writers - serialize a CoverageResult to the four mission products.

* coverage_pod.tif    - RGBA colormapped GeoTIFF (EPSG:3857), auto-places in
                        CalTopo Map Sheets.
* coverage_pod_values.tif - float32 POD probabilities 0-1 (NaN = no looks), the
                        GIS-queryable counterpart of the RGBA render.
* coverage_looks.tif  - uint16 look-count raster (binary coverage = count >= 1).
* coverage_gaps.geojson - WGS84 polygons where POD < gap_threshold inside the
                        flight-track hull (the re-tasking product).
* stats.json          - areas at POD thresholds, mean POD, skip reasons, canopy
                        source, terrain datum.

Also exposes ``compute_gap_polygons`` / ``build_stats`` used by
CoveragePodService so the CoverageResult is self-contained. Pure service layer
(rasterio / shapely / pyproj); no Qt.
"""

import json
import math
import os

import numpy as np

from core.services.LoggerService import LoggerService
from core.services.coverage.colormap import pod_to_rgba
from core.services.terrain.grid import mercator_to_lonlat

_logger = LoggerService()


def _to_wgs84_transformer():
    from pyproj import Transformer
    return Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True).transform


def _grid_center_lat(transform, shape) -> float:
    rows, cols = shape
    cx = transform.c + transform.a * cols / 2.0
    cy = transform.f + transform.e * rows / 2.0
    _, lat = mercator_to_lonlat(cx, cy)
    return lat


def _true_cell_area_m2(transform, center_lat: float) -> float:
    """Cell area corrected for Web Mercator inflation (cos^2 lat)."""
    return abs(transform.a * transform.e) * math.cos(math.radians(center_lat)) ** 2


def write_pod_geotiff(path, rgba: np.ndarray, transform, params=None,
                      crs: str = "EPSG:3857") -> None:
    import rasterio
    from rasterio.enums import ColorInterp

    rows, cols = rgba.shape[:2]
    profile = dict(
        driver="GTiff", height=rows, width=cols, count=4, dtype="uint8",
        crs=crs, transform=transform, photometric="RGB",
        compress="deflate", zlevel=6,
        tiled=True, blockxsize=256, blockysize=256,
    )
    with rasterio.open(path, "w", **profile) as dst:
        # Declare the 4th band as alpha before writing so GDAL records
        # ExtraSamples=alpha (viewers/CalTopo honor this for transparency).
        dst.colorinterp = [ColorInterp.red, ColorInterp.green,
                           ColorInterp.blue, ColorInterp.alpha]
        dst.write(np.moveaxis(rgba, 2, 0))
        tags = {"ADIAT_PRODUCT": "coverage_pod"}
        if params is not None:
            tags["ADIAT_PARAMS"] = json.dumps(params.to_dict())
        dst.update_tags(**tags)


def write_pod_values_geotiff(path, pod: np.ndarray, look_count: np.ndarray,
                             transform, params=None,
                             crs: str = "EPSG:3857") -> None:
    """Single-band float32 POD values (0-1), NaN where never looked at.

    The analyzable counterpart of the RGBA visualization: GIS tools can query,
    threshold, and restyle actual probabilities from this band.
    """
    import rasterio

    data = pod.astype("float32").copy()
    data[look_count == 0] = np.nan
    profile = dict(
        driver="GTiff", height=data.shape[0], width=data.shape[1],
        count=1, dtype="float32", crs=crs, transform=transform,
        nodata=float("nan"), compress="deflate",
        tiled=True, blockxsize=256, blockysize=256,
    )
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(data, 1)
        tags = {"ADIAT_PRODUCT": "coverage_pod_values"}
        if params is not None:
            tags["ADIAT_PARAMS"] = json.dumps(params.to_dict())
        dst.update_tags(**tags)


def write_pod_overlay_png(result, png_path: str) -> dict:
    """Write the POD render as a north-up WGS84 PNG for KML GroundOverlays.

    KML LatLonBox overlays are equirectangular, so the EPSG:3857 RGBA render
    is reprojected to EPSG:4326 first (nearest neighbour keeps the discrete
    colormap and the transparent no-look cells crisp). Returns the overlay's
    WGS84 bounding box as {'north', 'south', 'east', 'west'}.
    """
    from PIL import Image
    from rasterio.warp import calculate_default_transform, reproject, Resampling
    from rasterio.transform import array_bounds

    rgba = pod_to_rgba(result.pod, result.look_count, result.params)
    rows, cols = rgba.shape[:2]
    src_bounds = array_bounds(rows, cols, result.transform)
    dst_transform, dst_w, dst_h = calculate_default_transform(
        "EPSG:3857", "EPSG:4326", cols, rows, *src_bounds)
    dst = np.zeros((dst_h, dst_w, 4), dtype=np.uint8)
    for band in range(4):
        reproject(
            source=np.ascontiguousarray(rgba[:, :, band]),
            destination=dst[:, :, band],
            src_transform=result.transform, src_crs="EPSG:3857",
            dst_transform=dst_transform, dst_crs="EPSG:4326",
            resampling=Resampling.nearest)
    Image.fromarray(dst, "RGBA").save(png_path)
    west, south, east, north = array_bounds(dst_h, dst_w, dst_transform)
    return {"north": north, "south": south, "east": east, "west": west}


def write_looks_geotiff(path, look_count: np.ndarray, transform,
                        crs: str = "EPSG:3857") -> None:
    import rasterio

    profile = dict(
        driver="GTiff", height=look_count.shape[0], width=look_count.shape[1],
        count=1, dtype="uint16", crs=crs, transform=transform, nodata=0,
        compress="deflate", predictor=2, tiled=True, blockxsize=256, blockysize=256,
    )
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(look_count.astype("uint16"), 1)
        dst.update_tags(ADIAT_PRODUCT="coverage_looks")


def compute_gap_polygons(pod, look_count, transform, hull_3857, gap_threshold,
                         min_area_cells: int = 4):
    """Polygons (EPSG:3857) where POD < gap_threshold inside the flight hull."""
    import rasterio.features
    from shapely.geometry import shape

    gap_mask = pod < gap_threshold
    if hull_3857 is not None:
        inside = rasterio.features.geometry_mask(
            [hull_3857], out_shape=pod.shape, transform=transform, invert=True)
        gap_mask = gap_mask & inside
    if not gap_mask.any():
        return []

    cell_area = abs(transform.a * transform.e)
    polys = []
    for geom, val in rasterio.features.shapes(
            gap_mask.astype(np.uint8), mask=gap_mask, transform=transform):
        p = shape(geom)
        if p.area >= min_area_cells * cell_area:
            polys.append(p)
    return polys


def write_gaps_geojson(path, gap_polygons, gap_threshold) -> None:
    from shapely.geometry import mapping
    from shapely.ops import transform as shp_transform

    to_wgs84 = _to_wgs84_transformer()
    features = []
    for p in gap_polygons:
        g = shp_transform(to_wgs84, p)
        lat_c = g.centroid.y
        area = p.area * math.cos(math.radians(lat_c)) ** 2
        features.append({
            "type": "Feature",
            "properties": {"kind": "coverage_gap",
                           "area_sqm": round(area, 1),
                           "pod_threshold": gap_threshold},
            "geometry": mapping(g),
        })
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": features}, fh)


def build_stats(pod, look_count, transform, skipped, gap_polygons, params,
                canopy_source, terrain_info, generated_at=None) -> dict:
    center_lat = _grid_center_lat(transform, pod.shape)
    cell_area = _true_cell_area_m2(transform, center_lat)
    covered = look_count > 0

    reason_counts = {}
    for _, reason in skipped:
        reason_counts[reason] = reason_counts.get(reason, 0) + 1

    gap_area = sum(p.area for p in gap_polygons) * math.cos(math.radians(center_lat)) ** 2

    return {
        "generated_at": generated_at,
        "params": params.to_dict() if params is not None else {},
        "grid": {
            "crs": "EPSG:3857",
            "rows": int(pod.shape[0]),
            "cols": int(pod.shape[1]),
            "transform": list(transform)[:6],
            "grid_res_m": params.grid_res_m if params is not None else None,
        },
        "area_sqm": {
            "looks_ge_1": float(covered.sum() * cell_area),
            "pod_ge_0_25": float((pod >= 0.25).sum() * cell_area),
            "pod_ge_0_50": float((pod >= 0.50).sum() * cell_area),
            "pod_ge_0_75": float((pod >= 0.75).sum() * cell_area),
        },
        "mean_pod_covered": float(pod[covered].mean()) if covered.any() else 0.0,
        "skipped": [{"image": n, "reason": r} for n, r in skipped],
        "skipped_counts": reason_counts,
        "gaps": {"count": len(gap_polygons), "area_sqm": float(gap_area)},
        "canopy": {"source": canopy_source},
        "terrain": terrain_info,
    }


def write_all_outputs(result, out_dir: str) -> dict:
    """Write the mission products into ``out_dir``. Returns {name: path}."""
    os.makedirs(out_dir, exist_ok=True)
    paths = {}

    pod_path = os.path.join(out_dir, "coverage_pod.tif")
    rgba = pod_to_rgba(result.pod, result.look_count, result.params)
    write_pod_geotiff(pod_path, rgba, result.transform, result.params)
    paths["pod"] = pod_path

    values_path = os.path.join(out_dir, "coverage_pod_values.tif")
    write_pod_values_geotiff(values_path, result.pod, result.look_count,
                             result.transform, result.params)
    paths["pod_values"] = values_path

    looks_path = os.path.join(out_dir, "coverage_looks.tif")
    write_looks_geotiff(looks_path, result.look_count, result.transform)
    paths["looks"] = looks_path

    gaps_path = os.path.join(out_dir, "coverage_gaps.geojson")
    gap_threshold = result.params.gap_threshold if result.params is not None else 0.25
    write_gaps_geojson(gaps_path, result.gap_polygons, gap_threshold)
    paths["gaps"] = gaps_path

    stats_path = os.path.join(out_dir, "stats.json")
    with open(stats_path, "w", encoding="utf-8") as fh:
        json.dump(result.stats, fh, indent=2)
    paths["stats"] = stats_path

    _logger.info(f"CoveragePod: wrote {len(paths)} products to {out_dir}")
    return paths
