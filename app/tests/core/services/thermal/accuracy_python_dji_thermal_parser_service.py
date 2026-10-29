"""
Opt-in accuracy check: PythonDjiThermalParserService against DJI's Thermal SDK, through the app's own path.

Its name keeps a plain `pytest` run from collecting it. Run it explicitly, on Windows or Linux:

    pytest --no-cov app/tests/core/services/thermal/accuracy_python_dji_thermal_parser_service.py

Every image under app/tests/data/thermal/input that the app sends to the DJI parser goes through
ThermalParserService.parse_file twice, at the settings the app normally uses (stored in the file, or read from its
metadata): once with the SDK (expected) and once with the Python converter (actual). Every compared pixel must agree
within TOLERANCE_C, and a file the converter refuses but the SDK converts fails; a file the SDK refuses is only
reported. The statistics are printed either way; on failure the mismatching images are marked and their worst pixels
listed.
"""

import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional
from unittest.mock import patch

import numpy as np
import pytest

from core.services.thermal.ThermalParserService import ThermalParserService
from core.services.thermal.thermalParserServices.DjiThermalParserService import DjiThermalParserService
from core.services.thermal.thermalParserServices.PythonDjiThermalParserService import PythonDjiThermalParserService
from helpers.MetaDataHelper import MetaDataHelper

PARSER_SERVICE = 'core.services.thermal.ThermalParserService'
TOLERANCE_C = 0.75
WITHIN_C = 0.5          # the statistics' "<=0.5C" column
WORST_PIXELS = 5        # kept per image, and listed for each failing one

# ======================================================================================================================
# EXCLUDED PIXELS - REVISIT IF WE CHANGE OUR MINDS.
# Pixels the SDK reads below SDK_FLOOR_C are not compared. The converter follows DJI Thermal SDK v1.9, which floors
# iirp output at -20 C; the v1.7 SDK that ADIAT ships goes on down to -273.15 C, so every colder pixel (a cold sky, say)
# would otherwise count as a mismatch. They are counted in the statistics' "excluded" column.
# To compare them too, set SDK_FLOOR_C = -np.inf.
# ======================================================================================================================
SDK_FLOOR_C = -20.0


@dataclass
class _Result:
    """One image's comparison; the pixel statistics stay empty when either side refused it."""
    name: str
    camera: str
    status: str                     # ok, MISMATCH, SDK refused, converter refused or both refused
    reason: str = ''
    size: str = ''
    compared: int = 0               # pixels compared
    excluded: int = 0               # pixels the SDK reads below SDK_FLOOR_C
    within: int = 0                 # compared pixels within WITHIN_C
    beyond: int = 0                 # compared pixels beyond TOLERANCE_C, or NaN on either side
    diff_sum: float = 0.0
    max_diff: Optional[float] = None
    worst: list = field(default_factory=list)       # (row, col, SDK C, converter C), worst first

    @property
    def failed(self):
        return self.status in ('MISMATCH', 'converter refused')


@pytest.fixture
def images(testData):
    """Return the images the app sends to the DJI parser as (path, name, camera), and the other files as (name, reason)."""
    if sys.platform not in ('win32', 'linux'):
        pytest.fail('this is only to be run on Windows or Linux', pytrace=False)
    root = testData['Thermal_Input']
    service = ThermalParserService(dtype=np.float32)
    dji, skipped = [], []
    for folder, _, files in sorted(os.walk(root)):
        for file in sorted(files):
            path = os.path.join(folder, file)
            name = os.path.relpath(path, root).replace(os.sep, '/')
            try:
                data = MetaDataHelper.get_meta_data_exiftool(path)
            except Exception as e:
                skipped.append((name, f'unreadable: {e}'))
                continue
            meta_fields = {k.split(':')[1].strip(): v for k, v in data.items() if ':' in k}     # as parse_file reads them
            camera, platform = service._get_model_and_platform(meta_fields)
            if platform == 'DJI' and 'ThermalData' in meta_fields:
                dji.append((path, name, camera))
            elif platform == 'DJI':
                skipped.append((name, 'DJI image without thermal data'))
            else:
                skipped.append((name, f'{platform} thermal image, not DJI' if platform != 'None' else 'not a supported thermal image'))
    if not dji:
        pytest.fail('no thermal images found under app/tests/data/thermal/input', pytrace=False)
    return dji, skipped


def _temperatures(parser_class, path):
    """Return parse_file's temperatures for path, with both DJI parser names bound to parser_class."""
    with patch(f'{PARSER_SERVICE}.DjiThermalParserService', parser_class), \
            patch(f'{PARSER_SERVICE}.PythonDjiThermalParserService', parser_class):
        return np.asarray(ThermalParserService(dtype=np.float32).parse_file(path)[0], np.float64)


def _compare(path, name, camera):
    """Convert path both ways and compare them pixel by pixel."""
    outputs, errors = {}, {}
    for side, parser_class in (('SDK', DjiThermalParserService), ('converter', PythonDjiThermalParserService)):
        try:
            outputs[side] = _temperatures(parser_class, path)
        except Exception as e:
            cause = e.__context__ or e      # parse_file replaces every parser error with 'Invalid image file'
            errors[side] = f'{side}: {type(cause).__name__}: {cause}'
    if errors:
        return _Result(name, camera, 'both refused' if len(errors) == 2 else f'{next(iter(errors))} refused', '; '.join(errors.values()))
    expected, actual = outputs['SDK'], outputs['converter']
    if actual.shape != expected.shape:
        return _Result(name, camera, 'MISMATCH', f'converter shape {actual.shape}, SDK shape {expected.shape}')

    compared = expected >= SDK_FLOOR_C
    diff = np.abs(actual - expected)
    d = diff[compared]
    result = _Result(name, camera, 'ok', size=f'{expected.shape[1]}x{expected.shape[0]}', compared=d.size,
                     excluded=int(np.count_nonzero(~compared)), within=int(np.count_nonzero(d <= WITHIN_C)),
                     beyond=int(np.count_nonzero(~(d <= TOLERANCE_C))))
    if d.size:
        result.diff_sum, result.max_diff = float(d.sum()), float(d.max())
        score = np.where(compared, np.nan_to_num(diff, nan=np.inf), -np.inf).ravel()
        k = min(WORST_PIXELS, d.size)
        top = np.argpartition(score, -k)[-k:]
        rows, cols = np.unravel_index(top[np.argsort(score[top])[::-1]], diff.shape)
        result.worst = [(int(r), int(c), float(expected[r, c]), float(actual[r, c])) for r, c in zip(rows, cols)]
    if result.beyond:
        result.status = 'MISMATCH'
    return result


def _stats(compared, within, beyond, excluded, diff_sum, max_diff):
    """Return the statistics columns shared by the per-image and per-camera tables."""
    if not compared:
        return f'{"-":>8} {"-":>9} {"-":>8} {beyond:>7} {excluded:>9}'
    return f'{max_diff:>8.3f} {diff_sum / compared:>9.4f} {100 * within / compared:>7.2f}% {beyond:>7} {excluded:>9}'


def _report(results, skipped):
    """Return the statistics: one row per image, a per-camera summary, the skipped files and the worst pixel."""
    n, c = max(len(r.name) for r in results), max(len(r.camera) for r in results)
    columns = f'{"max|d|C":>8} {"mean|d|C":>9} {"<=" + str(WITHIN_C) + "C":>8} {">" + str(TOLERANCE_C) + "C":>7} {"excluded":>9}'
    lines = ['', f'Python converter vs DJI Thermal SDK on app/tests/data/thermal/input: tolerance {TOLERANCE_C} C, '
                 f'pixels the SDK reads below {SDK_FLOOR_C:g} C excluded', '',
             f'   {"image":<{n}}  {"camera":<{c}}  {"size":>9} {columns}  status']
    for r in results:
        stats = _stats(r.compared, r.within, r.beyond, r.excluded, r.diff_sum, r.max_diff)
        lines.append(f'{"!! " if r.failed else "   "}{r.name:<{n}}  {r.camera:<{c}}  {r.size or "-":>9} {stats}  {r.status}')

    cameras = defaultdict(list)
    for r in results:
        cameras[r.camera].append(r)
    lines += ['', f'   {"camera":<{c}}  {"images":>6} {"refused":>7} {columns}']
    for camera, rs in sorted(cameras.items()):
        done = [r for r in rs if r.compared]
        stats = _stats(sum(r.compared for r in done), sum(r.within for r in done), sum(r.beyond for r in rs),
                       sum(r.excluded for r in rs), sum(r.diff_sum for r in done), float(np.max([r.max_diff for r in done])) if done else None)
        lines.append(f'{"!! " if any(r.failed for r in rs) else "   "}{camera:<{c}}  {len(rs):>6} '
                     f'{sum("refused" in r.status for r in rs):>7} {stats}')

    if skipped:
        lines += ['', f'Skipped, not sent to the DJI parser: {len(skipped)}']
        lines += [f'   {name}: {reason}' for name, reason in skipped]
    for r in results:
        if 'refused' in r.status:
            lines.append(f'{"!! " if r.failed else "   "}{r.name}: {r.reason}')
    scored = [r for r in results if r.worst]
    if scored:
        r = max(scored, key=lambda r: np.nan_to_num(abs(r.worst[0][3] - r.worst[0][2]), nan=np.inf))
        row, col, sdk, converter = r.worst[0]
        lines += ['', f'Worst pixel: {r.name} row {row}, col {col}: SDK {sdk:.3f} C, converter {converter:.3f} C '
                      f'(|d| {abs(converter - sdk):.3f} C)']
    failed = sum(r.failed for r in results)
    lines.append(f'Result: {"FAIL, " + str(failed) + " of " + str(len(results)) + " images" if failed else "PASS"} '
                 f'({sum(r.compared > 0 for r in results)} compared, {sum("refused" in r.status for r in results)} refused, '
                 f'{len(skipped)} skipped)')
    return '\n'.join(lines)


def _failure_message(failures):
    """Return the failing images, each with its reason or its worst pixels."""
    lines = [f'{len(failures)} image(s) beyond {TOLERANCE_C} C, or refused by the converter where the SDK converts:']
    for r in failures:
        lines.append(f'  {r.name} ({r.camera}): {r.reason or f"{r.beyond} pixels beyond {TOLERANCE_C} C; worst:"}')
        lines += [f'    row {row}, col {col}: SDK {sdk:.3f} C, converter {converter:.3f} C (|d| {abs(converter - sdk):.3f} C)'
                  for row, col, sdk, converter in r.worst]
    return '\n'.join(lines)


def test_python_converter_matches_sdk(images, capsys):
    dji, skipped = images
    results = [_compare(*image) for image in dji]

    with capsys.disabled():
        print(_report(results, skipped))
    failures = [r for r in results if r.failed]
    if failures:
        pytest.fail(_failure_message(failures), pytrace=False)
