"""
Tests for BatchAnalyzeService.

Verifies batch folder discovery, output path mirroring, per-folder failure
isolation, Search Coordinator project generation, and the summary report.
AnalyzeService is replaced with a lightweight fake so the tests do not depend
on real imagery or the multiprocessing pool.
"""

import os
import time
import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtCore import QObject, Signal

from core.services.BatchAnalyzeService import BatchAnalyzeService


# --- Test helpers -----------------------------------------------------------

class FakeAnalyzeService(QObject):
    """Stand-in for AnalyzeService that simulates a per-folder analysis pass."""

    sig_msg = Signal(str)
    sig_done = Signal(int, int, str)
    sig_progress = Signal(int, int, float)

    def __init__(self, output_dir, behavior, images_with_aois):
        """Create a fake analysis service.

        Args:
            output_dir: The batch output directory passed by BatchAnalyzeService.
            behavior: 'success', 'raise' or 'incomplete'.
            images_with_aois: Count reported on the sig_done signal.
        """
        super().__init__()
        self.output_dir = output_dir
        self.behavior = behavior
        self.images_with_aois = images_with_aois
        self.pool = MagicMock()

    def process_files(self):
        """Simulate a pass: write a minimal XML and emit sig_done, fail, or stall."""
        if self.behavior == 'raise':
            raise RuntimeError("simulated analysis crash")
        if self.behavior == 'incomplete':
            return  # returns without ever emitting sig_done
        results_dir = os.path.join(self.output_dir, 'ADIAT_Results')
        os.makedirs(results_dir, exist_ok=True)
        xml_path = os.path.join(results_dir, 'ADIAT_Data.xml')
        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write('<data><settings algorithm="ColorRange"/><images/></data>')
        self.sig_done.emit(1, self.images_with_aois, xml_path)

    def process_cancel(self):
        """No-op cancel for the fake."""
        pass


def _make_analyze_factory(behaviors):
    """Build a patch side_effect that returns a FakeAnalyzeService per folder.

    Args:
        behaviors: Dict mapping a folder's basename to 'success', 'raise' or
            'incomplete'. Folders not listed default to 'success'.

    Returns:
        A callable matching the AnalyzeService constructor signature.
    """
    def factory(_id, _algorithm, input_dir, output, *args, **kwargs):
        name = os.path.basename(os.path.normpath(input_dir))
        return FakeAnalyzeService(output, behaviors.get(name, 'success'), 2)
    return factory


def _make_config():
    """Return a minimal analysis_config dictionary for BatchAnalyzeService."""
    return {
        'algorithm': {
            'name': 'ColorRange', 'type': 'RGB',
            'service': 'ColorRangeService', 'combine_overlapping_aois': True
        },
        'identifier_color': (0, 255, 0),
        'min_area': 10,
        'max_area': 0,
        'num_processes': 1,
        'max_aois': 100,
        'aoi_radius': 15,
        'hist_ref_path': None,
        'kmeans_clusters': None,
        'options': {},
        'processing_resolution': 1.0,
    }


def _touch_image(folder, name='image.jpg'):
    """Create an empty image-extension file inside folder."""
    os.makedirs(folder, exist_ok=True)
    open(os.path.join(folder, name), 'w').close()


# --- discover_batch_folders -------------------------------------------------

def test_discover_finds_folders_with_images(tmp_path):
    """Only folders that directly contain images are returned as batches."""
    parent = tmp_path / 'input'
    _touch_image(str(parent / 'gridA'))
    _touch_image(str(parent / 'gridB'))
    # gridC has no direct images, only a subfolder that does.
    _touch_image(str(parent / 'gridC' / 'sub'))
    # A folder with no images at all is not a batch.
    os.makedirs(str(parent / 'empty'), exist_ok=True)

    service = BatchAnalyzeService(str(parent), str(tmp_path / 'output'), _make_config())
    folders = service.discover_batch_folders()
    names = {os.path.relpath(f, str(parent)) for f in folders}

    assert names == {'gridA', 'gridB', os.path.join('gridC', 'sub')}


def test_discover_includes_loose_images_in_root(tmp_path):
    """Images directly in the input root make the root itself a batch."""
    parent = tmp_path / 'input'
    _touch_image(str(parent))

    service = BatchAnalyzeService(str(parent), str(tmp_path / 'output'), _make_config())
    folders = service.discover_batch_folders()

    assert os.path.abspath(str(parent)) in folders


def test_discover_skips_output_tree(tmp_path):
    """Folders inside the output directory are never discovered as input."""
    parent = tmp_path / 'input'
    output = parent / 'results'  # output nested inside input
    _touch_image(str(parent / 'gridA'))
    _touch_image(str(output / 'old_batch'))  # pre-existing results

    service = BatchAnalyzeService(str(parent), str(output), _make_config())
    folders = service.discover_batch_folders()
    names = {os.path.relpath(f, str(parent)) for f in folders}

    assert 'gridA' in names
    assert os.path.join('results', 'old_batch') not in names


# --- _batch_output_dir ------------------------------------------------------

def test_batch_output_dir_mirrors_structure(tmp_path):
    """Batch output mirrors the folder's path relative to the input root."""
    service = BatchAnalyzeService(str(tmp_path / 'in'), str(tmp_path / 'out'), _make_config())

    flat = service._batch_output_dir(str(tmp_path / 'in' / 'gridA'))
    assert flat == str(tmp_path / 'out' / 'gridA')

    nested = service._batch_output_dir(str(tmp_path / 'in' / 'region' / 'gridA'))
    assert nested == str(tmp_path / 'out' / 'region' / 'gridA')


def test_batch_output_dir_for_root_images(tmp_path):
    """Loose images in the input root are written under a folder named for it."""
    service = BatchAnalyzeService(str(tmp_path / 'searcharea'), str(tmp_path / 'out'),
                                  _make_config())
    result = service._batch_output_dir(str(tmp_path / 'searcharea'))
    assert result == str(tmp_path / 'out' / 'searcharea')


# --- _safe_filename ---------------------------------------------------------

def test_safe_filename():
    """Unsafe characters are stripped and spaces become underscores."""
    assert BatchAnalyzeService._safe_filename('My Search 2024') == 'My_Search_2024'
    assert BatchAnalyzeService._safe_filename('a/b\\c:d*e') == 'abcde'
    assert BatchAnalyzeService._safe_filename('') == 'Batch'


# --- process_batches --------------------------------------------------------

def test_process_batches_runs_every_folder(tmp_path):
    """Each discovered folder is analyzed and recorded as a completed batch."""
    parent = tmp_path / 'input'
    for name in ('gridA', 'gridB', 'gridC'):
        _touch_image(str(parent / name))

    service = BatchAnalyzeService(str(parent), str(tmp_path / 'output'), _make_config())
    with patch('core.services.BatchAnalyzeService.AnalyzeService',
               side_effect=_make_analyze_factory({})):
        service.process_batches()

    assert len(service.results) == 3
    assert all(r['status'] == 'Completed' for r in service.results)


def test_process_batches_isolates_failures(tmp_path):
    """A failure in one folder does not stop the remaining folders."""
    parent = tmp_path / 'input'
    for name in ('gridA', 'gridB', 'gridC'):
        _touch_image(str(parent / name))

    done = []
    service = BatchAnalyzeService(str(parent), str(tmp_path / 'output'), _make_config())
    service.sig_done.connect(lambda s, f, p: done.append((s, f, p)))

    with patch('core.services.BatchAnalyzeService.AnalyzeService',
               side_effect=_make_analyze_factory({'gridB': 'raise'})):
        service.process_batches()

    statuses = {os.path.basename(r['folder']): r['status'] for r in service.results}
    assert statuses == {'gridA': 'Completed', 'gridB': 'Failed', 'gridC': 'Completed'}
    # sig_done reports 2 succeeded, 1 failed.
    assert done and done[0][0] == 2 and done[0][1] == 1


def test_process_batches_incomplete_pass_is_failed(tmp_path):
    """A pass that returns without emitting sig_done is recorded as failed."""
    parent = tmp_path / 'input'
    _touch_image(str(parent / 'gridA'))

    service = BatchAnalyzeService(str(parent), str(tmp_path / 'output'), _make_config())
    with patch('core.services.BatchAnalyzeService.AnalyzeService',
               side_effect=_make_analyze_factory({'gridA': 'incomplete'})):
        service.process_batches()

    assert service.results[0]['status'] == 'Failed'


def test_process_batches_creates_search_project(tmp_path):
    """A Search Coordinator project linking successful batches is written."""
    parent = tmp_path / 'input'
    for name in ('gridA', 'gridB'):
        _touch_image(str(parent / name))
    output = tmp_path / 'output'

    service = BatchAnalyzeService(str(parent), str(output), _make_config())
    with patch('core.services.BatchAnalyzeService.AnalyzeService',
               side_effect=_make_analyze_factory({})):
        service.process_batches()

    assert service.search_project_path
    assert os.path.isfile(service.search_project_path)
    project_files = [f for f in os.listdir(str(output))
                     if f.startswith('ADIAT_Search_') and f.endswith('.xml')]
    assert len(project_files) == 1


def test_process_batches_writes_summary(tmp_path):
    """A batch_summary.txt report is written to the output root."""
    parent = tmp_path / 'input'
    _touch_image(str(parent / 'gridA'))
    output = tmp_path / 'output'

    service = BatchAnalyzeService(str(parent), str(output), _make_config())
    with patch('core.services.BatchAnalyzeService.AnalyzeService',
               side_effect=_make_analyze_factory({})):
        service.process_batches()

    summary = os.path.join(str(output), 'batch_summary.txt')
    assert os.path.isfile(summary)
    with open(summary, encoding='utf-8') as f:
        content = f.read()
    assert 'ADIAT Batch Processing Summary' in content
    assert 'gridA' in content


def test_process_batches_no_folders(tmp_path):
    """With no image folders, the run completes reporting zero batches."""
    parent = tmp_path / 'input'
    os.makedirs(str(parent), exist_ok=True)

    done = []
    service = BatchAnalyzeService(str(parent), str(tmp_path / 'output'), _make_config())
    service.sig_done.connect(lambda s, f, p: done.append((s, f, p)))
    service.process_batches()

    assert done == [(0, 0, '')]
    assert service.results == []


def test_no_search_project_when_disabled(tmp_path):
    """create_search_project=False suppresses the Coordinator project."""
    parent = tmp_path / 'input'
    _touch_image(str(parent / 'gridA'))

    service = BatchAnalyzeService(str(parent), str(tmp_path / 'output'), _make_config(),
                                  create_search_project=False)
    with patch('core.services.BatchAnalyzeService.AnalyzeService',
               side_effect=_make_analyze_factory({})):
        service.process_batches()

    assert service.search_project_path == ''


def test_cancel_stops_remaining_folders(tmp_path):
    """Cancelling before the run starts leaves all folders unprocessed."""
    parent = tmp_path / 'input'
    for name in ('gridA', 'gridB'):
        _touch_image(str(parent / name))

    service = BatchAnalyzeService(str(parent), str(tmp_path / 'output'), _make_config())
    service.cancelled = True  # request cancellation up front
    with patch('core.services.BatchAnalyzeService.AnalyzeService',
               side_effect=_make_analyze_factory({})):
        service.process_batches()

    assert service.results == []


# --- per-batch timing, resume, and ETA --------------------------------------

def test_process_batches_records_elapsed(tmp_path):
    """Each batch result records an elapsed time."""
    parent = tmp_path / 'input'
    _touch_image(str(parent / 'gridA'))

    service = BatchAnalyzeService(str(parent), str(tmp_path / 'output'), _make_config())
    with patch('core.services.BatchAnalyzeService.AnalyzeService',
               side_effect=_make_analyze_factory({})):
        service.process_batches()

    assert 'elapsed' in service.results[0]
    assert service.results[0]['elapsed'] >= 0


def test_count_completed_batches(tmp_path):
    """count_completed_batches counts folders that already have results."""
    parent = tmp_path / 'input'
    for name in ('gridA', 'gridB', 'gridC'):
        _touch_image(str(parent / name))
    output = tmp_path / 'output'

    # Simulate gridB already finished by a previous run.
    grid_b_results = output / 'gridB' / 'ADIAT_Results'
    os.makedirs(str(grid_b_results), exist_ok=True)
    open(str(grid_b_results / 'ADIAT_Data.xml'), 'w').close()

    service = BatchAnalyzeService(str(parent), str(output), _make_config())
    completed, total = service.count_completed_batches()

    assert completed == 1
    assert total == 3


def test_resume_skips_completed_batches(tmp_path):
    """resume=True skips folders that already have results and runs the rest."""
    parent = tmp_path / 'input'
    for name in ('gridA', 'gridB', 'gridC'):
        _touch_image(str(parent / name))
    output = tmp_path / 'output'

    # Simulate gridA already finished by a previous run.
    grid_a_results = output / 'gridA' / 'ADIAT_Results'
    os.makedirs(str(grid_a_results), exist_ok=True)
    open(str(grid_a_results / 'ADIAT_Data.xml'), 'w').close()

    service = BatchAnalyzeService(str(parent), str(output), _make_config(), resume=True)
    with patch('core.services.BatchAnalyzeService.AnalyzeService',
               side_effect=_make_analyze_factory({})):
        service.process_batches()

    by_name = {os.path.basename(r['folder']): r for r in service.results}
    assert by_name['gridA'].get('skipped') is True
    assert by_name['gridB'].get('skipped') is not True
    assert by_name['gridC'].get('skipped') is not True
    assert all(r['status'] == 'Completed' for r in service.results)


def test_on_inner_progress_emits_batch_eta(tmp_path):
    """_on_inner_progress emits a status line with the batch position and ETAs."""
    service = BatchAnalyzeService(str(tmp_path / 'in'), str(tmp_path / 'out'), _make_config())
    service._current_index = 2
    service._current_total = 5
    service._current_folder_name = 'gridB'
    service._current_batch_start = time.time()

    received = []
    service.sig_progress.connect(received.append)
    service._on_inner_progress(10, 20, 30.0)

    assert received
    assert 'Batch 2/5' in received[0]
    assert 'gridB' in received[0]
