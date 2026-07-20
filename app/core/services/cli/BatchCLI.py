"""
BatchCLI.py -- command-line entry point for ADIAT batch image analysis.

Lets ADIAT run headless: point it at a parent folder and it analyzes every
subfolder containing images as a separate batch. Algorithm settings can be
supplied with command-line flags, taken from a previous run's ADIAT_Data.xml
(via --config), or both. It is invoked from __main__.py as:

    python app batch --input <parent> --output <root> [options]
"""

import argparse
import os
import pathlib
import sys
from ast import literal_eval

from core.services.ConfigService import ConfigService
from core.services.XmlService import XmlService
from core.services.BatchAnalyzeService import BatchAnalyzeService


# Processing-resolution percentage labels accepted by --resolution, mapped to
# the scaling factor AnalyzeService expects.
RESOLUTION_PRESETS = {
    '100%': 1.0,
    '75%': 0.75,
    '50%': 0.5,
    '33%': 0.33,
    '25%': 0.25,
    '10%': 0.1,
}


def _algorithms_conf_path():
    """Return the absolute path to the bundled algorithms.conf file."""
    if getattr(sys, 'frozen', False):
        app_root = sys._MEIPASS
    else:
        # app/core/services/cli/BatchCLI.py -> parents[3] is app/
        app_root = str(pathlib.Path(__file__).resolve().parents[3])
    return os.path.join(app_root, 'algorithms.conf')


def _resolve_algorithm(name):
    """Look up an algorithm configuration by name or label.

    Args:
        name: Algorithm name (e.g. 'ColorRange') or label (e.g. 'Color Range (RGB)').

    Returns:
        dict: The matching algorithm configuration.

    Raises:
        ValueError: If no algorithm matches the supplied name.
    """
    algorithms = ConfigService(_algorithms_conf_path()).get_algorithms()
    for algorithm in algorithms:
        if name.lower() in (algorithm.get('name', '').lower(),
                            algorithm.get('label', '').lower()):
            return algorithm
    available = ', '.join(a.get('name', '') for a in algorithms)
    raise ValueError(f"Unknown algorithm '{name}'. Available: {available}")


def _parse_value(text):
    """Convert a string to a Python literal when possible.

    Used for option values from the config XML and from --option flags so that
    numbers, tuples and lists are restored to real Python objects. Plain strings
    that are not literals are returned unchanged.

    Args:
        text: The raw string value.

    Returns:
        The parsed Python object, or the original string if it is not a literal.
    """
    try:
        return literal_eval(text)
    except (ValueError, SyntaxError):
        return text


def _parse_color(text):
    """Parse an 'R,G,B' string into a tuple of three integers.

    Args:
        text: Color string such as '0,255,0'.

    Returns:
        tuple: (red, green, blue) integers.

    Raises:
        ValueError: If the string is not three comma-separated integers.
    """
    parts = [p.strip() for p in text.split(',')]
    if len(parts) != 3:
        raise ValueError(f"Identifier color must be 'R,G,B', got '{text}'")
    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        raise ValueError(f"Identifier color must be three integers, got '{text}'")


def _build_parser():
    """Build the argparse parser for the batch subcommand.

    Returns:
        argparse.ArgumentParser: The configured parser.
    """
    parser = argparse.ArgumentParser(
        prog='app batch',
        description='Analyze every subfolder of a directory as a separate ADIAT batch.'
    )
    parser.add_argument('--input', required=True,
                        help='Parent folder; each subfolder containing images is one batch.')
    parser.add_argument('--output', required=True,
                        help='Output root for the per-batch results.')
    parser.add_argument('--config',
                        help='Previous ADIAT_Data.xml whose settings are used as a template.')
    parser.add_argument('--algorithm',
                        help='Algorithm name, e.g. ColorRange, RXAnomaly, ThermalRange.')
    parser.add_argument('--min-area', type=int,
                        help='Minimum area in pixels for an area of interest.')
    parser.add_argument('--max-area', type=int,
                        help='Maximum area in pixels (0 = no maximum).')
    parser.add_argument('--processes', type=int,
                        help='Number of parallel worker processes per batch.')
    parser.add_argument('--identifier-color',
                        help="AOI highlight color as 'R,G,B', e.g. 0,255,0.")
    parser.add_argument('--aoi-radius', type=int,
                        help='Radius in pixels added around each area of interest.')
    parser.add_argument('--max-aois', type=int,
                        help='Area-of-interest count that triggers a warning.')
    parser.add_argument('--resolution', choices=sorted(RESOLUTION_PRESETS.keys()),
                        help='Processing resolution as a percentage of original size.')
    parser.add_argument('--histogram-ref',
                        help='Histogram reference image path.')
    parser.add_argument('--option', action='append', default=[], metavar='NAME=VALUE',
                        help='Algorithm-specific option; repeatable.')
    parser.add_argument('--no-coordinator', action='store_true',
                        help='Do not create a Search Coordinator project for the batches.')
    parser.add_argument('--resume', action='store_true',
                        help='Skip batch folders that already have finished results.')
    parser.add_argument('--project-name',
                        help='Name for the generated Search Coordinator project.')
    parser.add_argument('--coordinator-name', default='',
                        help='Name recorded as the project creator.')
    return parser


def _build_analysis_config(args):
    """Resolve the analysis configuration from --config and command-line flags.

    Settings are resolved in order: built-in defaults, then the --config
    template, then command-line flags, then individual --option entries.

    Args:
        args: Parsed argparse namespace.

    Returns:
        dict: An analysis_config dictionary for BatchAnalyzeService.

    Raises:
        ValueError: If required settings cannot be resolved.
    """
    # 1. Built-in defaults.
    algorithm_name = None
    identifier_color = (0, 255, 0)
    min_area = 10
    max_area = 0
    num_processes = 4
    max_aois = 100
    aoi_radius = 15
    hist_ref_path = None
    processing_resolution = 1.0
    options = {}

    # 2. Seed from a previous run's ADIAT_Data.xml, if provided.
    if args.config:
        if not os.path.isfile(args.config):
            raise ValueError(f"Config file not found: {args.config}")
        settings, _ = XmlService(args.config).get_settings()
        algorithm_name = settings.get('algorithm') or algorithm_name
        if settings.get('identifier_color'):
            identifier_color = settings['identifier_color']
        min_area = settings.get('min_area', min_area)
        max_area = settings.get('max_area', max_area)
        num_processes = settings.get('num_processes') or num_processes
        aoi_radius = settings.get('aoi_radius', aoi_radius)
        if settings.get('hist_ref_path'):
            hist_ref_path = settings['hist_ref_path']
        # Restore option values from stored strings to real Python objects.
        for key, value in settings.get('options', {}).items():
            options[key] = _parse_value(value) if isinstance(value, str) else value

    # 3. Command-line flags override the config template.
    if args.algorithm:
        algorithm_name = args.algorithm
    if args.identifier_color:
        identifier_color = _parse_color(args.identifier_color)
    if args.min_area is not None:
        min_area = args.min_area
    if args.max_area is not None:
        max_area = args.max_area
    if args.processes is not None:
        num_processes = args.processes
    if args.aoi_radius is not None:
        aoi_radius = args.aoi_radius
    if args.max_aois is not None:
        max_aois = args.max_aois
    if args.resolution:
        processing_resolution = RESOLUTION_PRESETS[args.resolution]
    if args.histogram_ref:
        hist_ref_path = args.histogram_ref

    # 4. Individual --option NAME=VALUE entries override algorithm options.
    for entry in args.option:
        if '=' not in entry:
            raise ValueError(f"--option must be NAME=VALUE, got '{entry}'")
        name, value = entry.split('=', 1)
        options[name.strip()] = _parse_value(value.strip())

    if not algorithm_name:
        raise ValueError(
            "No algorithm specified. Use --algorithm NAME, or --config with a "
            "previous ADIAT_Data.xml."
        )

    return {
        'algorithm': _resolve_algorithm(algorithm_name),
        'identifier_color': identifier_color,
        'min_area': min_area,
        'max_area': max_area,
        'num_processes': num_processes,
        'max_aois': max_aois,
        'aoi_radius': aoi_radius,
        'hist_ref_path': hist_ref_path,
        'kmeans_clusters': None,
        'options': options,
        'processing_resolution': processing_resolution,
    }


def run_batch_cli(argv):
    """Run ADIAT batch processing from the command line.

    Args:
        argv: Argument list excluding the leading 'batch' subcommand token.

    Returns:
        int: Process exit code -- 0 on success, 1 if any batch failed or an
            error prevented the run.
    """
    args = _build_parser().parse_args(argv)

    try:
        analysis_config = _build_analysis_config(args)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    input_dir = os.path.abspath(args.input)
    output_dir = os.path.abspath(args.output)
    if not os.path.isdir(input_dir):
        print(f"Error: input folder does not exist: {input_dir}", file=sys.stderr)
        return 1

    # A QCoreApplication backs the QObject-based services for a headless run.
    from PySide6.QtCore import QCoreApplication
    QCoreApplication.instance() or QCoreApplication([])

    service = BatchAnalyzeService(
        input_dir,
        output_dir,
        analysis_config,
        create_search_project=not args.no_coordinator,
        project_name=args.project_name,
        coordinator_name=args.coordinator_name,
        resume=args.resume,
    )

    summary = {}
    service.sig_msg.connect(lambda text: print(text, flush=True))
    service.sig_done.connect(
        lambda succeeded, failed, project_path: summary.update(
            succeeded=succeeded, failed=failed, project_path=project_path
        )
    )

    print("ADIAT batch processing")
    print(f"  Input:     {input_dir}")
    print(f"  Output:    {output_dir}")
    print(f"  Algorithm: {analysis_config['algorithm'].get('name')}")
    print('')

    # Runs synchronously in this thread; BatchAnalyzeService manages the pools.
    service.process_batches()

    succeeded = summary.get('succeeded', 0)
    failed = summary.get('failed', 0)
    print('')
    print(f"Done: {succeeded} succeeded, {failed} failed.")
    if summary.get('project_path'):
        print(f"Search project: {summary['project_path']}")

    return 0 if failed == 0 else 1
