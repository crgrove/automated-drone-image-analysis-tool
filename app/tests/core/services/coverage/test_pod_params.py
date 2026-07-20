"""Tests for PodParams defaults, thermal preset, and settings loading."""

from unittest.mock import MagicMock

from core.services.coverage.params import PodParams


def test_spec_defaults():
    p = PodParams()
    assert p.grid_res_m == 3.0
    assert p.ray_samples == 48
    assert p.extinction_k == 0.06
    assert p.gsd_full_cm == 2.0
    assert p.gsd_max_cm == 10.0
    assert p.max_range_m == 800.0
    assert p.min_pitch_deg == -10.0
    assert p.gap_threshold == 0.25
    assert p.pod_frame_cap == 0.85
    assert p.common_mode_ceiling == 0.90
    assert p.angle_bins == 8
    assert p.pod_display_floor == 0.05


def test_to_dict_roundtrips_keys():
    d = PodParams().to_dict()
    assert d['grid_res_m'] == 3.0
    assert 'extinction_k' in d and 'pod_frame_cap' in d


def test_thermal_preset_changes_only_gsd_knobs():
    base = PodParams()
    t = PodParams.thermal()
    assert t.gsd_full_cm == 6.0
    assert t.gsd_max_cm == 25.0
    # Everything else stays default.
    assert t.grid_res_m == base.grid_res_m
    assert t.extinction_k == base.extinction_k


def test_from_settings_none_returns_defaults():
    assert PodParams.from_settings(None) == PodParams()


def test_from_settings_reads_exposed_subset():
    settings = MagicMock()
    values = {'PodGsdPreset': 'rgb', 'PodGridResM': '1.5', 'PodGapThreshold': '0.4'}
    settings.get_setting.side_effect = lambda k, d=None: values.get(k, d)
    p = PodParams.from_settings(settings)
    assert p.grid_res_m == 1.5
    assert p.gap_threshold == 0.4
    # Unexposed knobs stay default.
    assert p.pod_frame_cap == 0.85


def test_from_settings_thermal_preset():
    settings = MagicMock()
    settings.get_setting.side_effect = lambda k, d=None: 'thermal' if k == 'PodGsdPreset' else d
    p = PodParams.from_settings(settings)
    assert p.gsd_full_cm == 6.0
    assert p.gsd_max_cm == 25.0


def test_from_settings_bad_value_falls_back():
    settings = MagicMock()
    values = {'PodGridResM': 'not-a-number'}
    settings.get_setting.side_effect = lambda k, d=None: values.get(k, d)
    p = PodParams.from_settings(settings)
    assert p.grid_res_m == 3.0
