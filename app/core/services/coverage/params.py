"""
PodParams - tunable parameters for the Coverage/Probability-of-Detection pipeline.

Spec-defined knobs (section 6) plus a small number of engine-internal knobs that
the spec's prose implies but does not tabulate. Defaults are the calibrated
product; only a few are exposed to end users via settings (see from_settings).
"""

from dataclasses import dataclass, asdict, replace


@dataclass(frozen=True)
class PodParams:
    # --- spec section 6 ---
    grid_res_m: float = 3.0             # working cell size (true ground meters)
    ray_samples: int = 48              # samples per line-of-sight ray
    extinction_k: float = 0.06         # Beer-Lambert coefficient, 1/m
    gsd_full_cm: float = 2.0           # GSD at/below which adequacy = 1
    gsd_max_cm: float = 10.0           # GSD at/above which adequacy = 0
    max_range_m: float = 800.0         # clamp for very oblique frames
    min_pitch_deg: float = -10.0       # skip frames with pitch shallower than this (> min_pitch_deg)
    gap_threshold: float = 0.25        # POD below this -> gap polygon
    pod_frame_cap: float = 0.85        # max POD any single frame can claim
    common_mode_ceiling: float = 0.90  # mission ceiling C (correlated failure modes)
    angle_bins: int = 8                # 4 azimuth quadrants x {nadir, oblique}
    pod_display_floor: float = 0.05    # transparency floor in RGBA output

    # --- engine knobs beyond spec section 6 (documented deviations) ---
    los_epsilon_m: float = 0.5         # DEM-noise tolerance in the blocked test
    footprint_buffer_m: float = 50.0   # bbox margin around the flat-plane footprint
    nadir_split_deg: float = 30.0      # off-nadir angle separating nadir/oblique rings
    low_confidence_haircut: float = 0.7  # frame POD multiplier when bearing_confidence < 0.5
    kernel_chunk_cells: int = 16384    # ray-march memory bound (target cells per chunk)
    frame_index_block: int = 8         # cells per side of a coarse frame-index block
    frame_index_max_per_block: int = 64
    mem_budget_mb: int = 512           # accumulator lazy-growth clamp

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def thermal(cls) -> "PodParams":
        """Thermal preset (spec section 6 note): same two adequacy knobs, thermal values."""
        return cls(gsd_full_cm=6.0, gsd_max_cm=25.0)

    @classmethod
    def from_settings(cls, settings_service) -> "PodParams":
        """Build params from user settings, keeping non-exposed knobs at defaults.

        Only a small, safe subset is user-tunable; everything else stays the
        calibrated default. ``settings_service`` may be None (returns defaults).
        """
        if settings_service is None:
            return cls()

        preset = settings_service.get_setting('PodGsdPreset', 'rgb')
        base = cls.thermal() if preset == 'thermal' else cls()

        def _f(key, default):
            try:
                return float(settings_service.get_setting(key, default))
            except (TypeError, ValueError):
                return default

        return replace(
            base,
            grid_res_m=_f('PodGridResM', base.grid_res_m),
            gap_threshold=_f('PodGapThreshold', base.gap_threshold),
        )
