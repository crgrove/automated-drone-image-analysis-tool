"""
Tests for the BatchCLI command-line interface.

Covers value parsing, algorithm lookup, settings resolution from flags and
from a --config template, and the missing-input exit path.
"""

import pytest
from unittest.mock import patch

from core.services.cli.BatchCLI import (
    _build_parser, _build_analysis_config, _resolve_algorithm,
    _parse_value, _parse_color, run_batch_cli, RESOLUTION_PRESETS
)


# --- value parsing ----------------------------------------------------------

def test_parse_value_literals():
    """_parse_value restores numbers, tuples and lists from strings."""
    assert _parse_value('20.5') == 20.5
    assert _parse_value('30') == 30
    assert _parse_value('(1, 2, 3)') == (1, 2, 3)
    assert _parse_value('[1, 2]') == [1, 2]


def test_parse_value_plain_string():
    """_parse_value leaves non-literal strings unchanged."""
    assert _parse_value('C:\\images\\ref.jpg') == 'C:\\images\\ref.jpg'
    assert _parse_value('') == ''


def test_parse_color_valid():
    """_parse_color converts 'R,G,B' to an integer tuple."""
    assert _parse_color('0,255,0') == (0, 255, 0)
    assert _parse_color(' 10, 20 ,30 ') == (10, 20, 30)


def test_parse_color_invalid():
    """_parse_color rejects malformed color strings."""
    with pytest.raises(ValueError):
        _parse_color('255,0')
    with pytest.raises(ValueError):
        _parse_color('red,green,blue')


# --- algorithm lookup -------------------------------------------------------

def test_resolve_algorithm_by_name():
    """_resolve_algorithm finds an algorithm from algorithms.conf by name."""
    algorithm = _resolve_algorithm('ColorRange')
    assert algorithm['name'] == 'ColorRange'
    assert algorithm['service'] == 'ColorRangeService'


def test_resolve_algorithm_case_insensitive():
    """Algorithm lookup is case-insensitive."""
    assert _resolve_algorithm('colorrange')['name'] == 'ColorRange'


def test_resolve_algorithm_unknown():
    """An unknown algorithm name raises ValueError."""
    with pytest.raises(ValueError):
        _resolve_algorithm('NotAnAlgorithm')


# --- configuration building -------------------------------------------------

def test_build_config_from_flags():
    """Command-line flags populate the analysis configuration."""
    args = _build_parser().parse_args([
        '--input', 'in', '--output', 'out', '--algorithm', 'ColorRange',
        '--min-area', '50', '--max-area', '2000', '--processes', '8',
        '--identifier-color', '0,255,0', '--resolution', '50%'
    ])
    config = _build_analysis_config(args)
    assert config['algorithm']['name'] == 'ColorRange'
    assert config['min_area'] == 50
    assert config['max_area'] == 2000
    assert config['num_processes'] == 8
    assert config['identifier_color'] == (0, 255, 0)
    assert config['processing_resolution'] == RESOLUTION_PRESETS['50%']


def test_build_config_options_parsed():
    """--option entries are parsed into typed algorithm options."""
    args = _build_parser().parse_args([
        '--input', 'in', '--output', 'out', '--algorithm', 'ThermalRange',
        '--option', 'minTemp=20.5', '--option', 'maxTemp=30'
    ])
    config = _build_analysis_config(args)
    assert config['options']['minTemp'] == 20.5
    assert config['options']['maxTemp'] == 30


def test_build_config_requires_algorithm():
    """Building the config fails when no algorithm can be resolved."""
    args = _build_parser().parse_args(['--input', 'in', '--output', 'out'])
    with pytest.raises(ValueError):
        _build_analysis_config(args)


def test_build_config_bad_option():
    """An --option without '=' raises a clear error."""
    args = _build_parser().parse_args([
        '--input', 'in', '--output', 'out', '--algorithm', 'ColorRange',
        '--option', 'noequalshere'
    ])
    with pytest.raises(ValueError):
        _build_analysis_config(args)


def test_build_config_from_xml_template(tmp_path):
    """--config seeds settings from a previous run's XML."""
    cfg = tmp_path / 'prev.xml'
    cfg.write_text('<data/>')
    args = _build_parser().parse_args([
        '--input', 'in', '--output', 'out', '--config', str(cfg)
    ])
    with patch('core.services.cli.BatchCLI.XmlService') as MockXml:
        MockXml.return_value.get_settings.return_value = (
            {
                'algorithm': 'RXAnomaly', 'min_area': 99, 'max_area': 0,
                'num_processes': 6, 'identifier_color': (1, 2, 3),
                'aoi_radius': 7, 'hist_ref_path': '',
                'options': {'sensitivity': '5'}
            },
            12
        )
        config = _build_analysis_config(args)
    assert config['algorithm']['name'] == 'RXAnomaly'
    assert config['min_area'] == 99
    assert config['num_processes'] == 6
    assert config['identifier_color'] == (1, 2, 3)
    # Stored option strings are restored to real Python values.
    assert config['options']['sensitivity'] == 5


def test_flags_override_config_template(tmp_path):
    """Command-line flags take precedence over the --config template."""
    cfg = tmp_path / 'prev.xml'
    cfg.write_text('<data/>')
    args = _build_parser().parse_args([
        '--input', 'in', '--output', 'out', '--config', str(cfg),
        '--min-area', '5'
    ])
    with patch('core.services.cli.BatchCLI.XmlService') as MockXml:
        MockXml.return_value.get_settings.return_value = (
            {'algorithm': 'ColorRange', 'min_area': 99, 'max_area': 0,
             'num_processes': 4, 'identifier_color': (0, 0, 0),
             'aoi_radius': 15, 'hist_ref_path': '', 'options': {}},
            0
        )
        config = _build_analysis_config(args)
    assert config['min_area'] == 5


def test_missing_config_file_raises():
    """A --config path that does not exist raises a clear error."""
    args = _build_parser().parse_args([
        '--input', 'in', '--output', 'out', '--config', 'no_such_file.xml'
    ])
    with pytest.raises(ValueError):
        _build_analysis_config(args)


# --- run_batch_cli ----------------------------------------------------------

def test_run_batch_cli_missing_input(tmp_path):
    """run_batch_cli returns exit code 1 when the input folder is missing."""
    code = run_batch_cli([
        '--input', str(tmp_path / 'does_not_exist'),
        '--output', str(tmp_path / 'out'),
        '--algorithm', 'ColorRange'
    ])
    assert code == 1
