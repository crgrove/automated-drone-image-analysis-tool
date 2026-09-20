"""Unit tests for AOIInteractionLogService."""

import json

from core.services.AOIInteractionLogService import (
    AOIInteractionLogService,
    DWELL_CAP_S,
    LOG_FILENAME,
    REASON_CLOSE,
    REASON_DESELECT,
    REASON_IMAGE_CHANGE,
    REASON_NEXT_SELECT,
    REASON_WINDOW_UNFOCUSED,
)


class _FakeClock:
    def __init__(self):
        self.now = 1000.0

    def advance(self, seconds):
        self.now += seconds

    def __call__(self):
        return self.now


def _service(tmp_path):
    clock = _FakeClock()
    service = AOIInteractionLogService(str(tmp_path / LOG_FILENAME), clock=clock)
    return service, clock


def _records(tmp_path):
    path = tmp_path / LOG_FILENAME
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line]


def test_session_records_identity(tmp_path):
    service, _ = _service(tmp_path)
    service.start_session(review_id='rev-1', reviewer_name='Casey')
    service.end_session()

    records = _records(tmp_path)
    assert records[0]['event'] == 'session_start'
    assert records[0]['review_id'] == 'rev-1'
    assert records[0]['reviewer'] == 'Casey'
    assert records[-1]['event'] == 'session_end'
    assert all('t' in r for r in records)


def test_view_records_dwell_and_reason(tmp_path):
    service, clock = _service(tmp_path)
    service.start_session()
    service.record_selection(7, 'gallery')
    clock.advance(12.5)
    service.record_selection(9, 'single')
    clock.advance(3.0)
    service.end_current_interval(REASON_IMAGE_CHANGE)
    service.end_session()

    views = [r for r in _records(tmp_path) if r['event'] == 'view']
    assert len(views) == 2
    assert views[0]['aoi'] == 7
    assert views[0]['mode'] == 'gallery'
    assert views[0]['dwell_s'] == 12.5
    assert views[0]['reason'] == REASON_NEXT_SELECT
    assert views[1]['aoi'] == 9
    assert views[1]['dwell_s'] == 3.0
    assert views[1]['reason'] == REASON_IMAGE_CHANGE


def test_dwell_is_capped(tmp_path):
    service, clock = _service(tmp_path)
    service.record_selection(1, 'single')
    clock.advance(DWELL_CAP_S + 900)
    service.end_current_interval(REASON_WINDOW_UNFOCUSED)

    views = [r for r in _records(tmp_path) if r['event'] == 'view']
    assert views[0]['dwell_s'] == DWELL_CAP_S


def test_consecutive_same_selection_is_deduped(tmp_path):
    """Style refreshes and gallery sync re-enter select_aoi; count once."""
    service, clock = _service(tmp_path)
    service.record_selection(5, 'single')
    clock.advance(2.0)
    service.record_selection(5, 'single')  # re-entry, not a new view
    clock.advance(2.0)
    service.end_current_interval(REASON_DESELECT)

    views = [r for r in _records(tmp_path) if r['event'] == 'view']
    assert len(views) == 1
    assert views[0]['dwell_s'] == 4.0


def test_same_aoi_in_other_mode_counts_again(tmp_path):
    service, clock = _service(tmp_path)
    service.record_selection(5, 'gallery')
    clock.advance(1.0)
    service.record_selection(5, 'single')
    clock.advance(1.0)
    service.end_session()

    views = [r for r in _records(tmp_path) if r['event'] == 'view']
    assert [v['mode'] for v in views] == ['gallery', 'single']
    assert views[-1]['reason'] == REASON_CLOSE


def test_none_aoi_number_is_ignored(tmp_path):
    service, _ = _service(tmp_path)
    service.record_selection(None, 'single')
    service.end_session()
    assert [r['event'] for r in _records(tmp_path)] == ['session_end']


def test_end_interval_without_selection_is_noop(tmp_path):
    service, _ = _service(tmp_path)
    service.end_current_interval(REASON_DESELECT)
    assert _records(tmp_path) == []


def test_summarize_aggregates_across_sessions(tmp_path):
    service, clock = _service(tmp_path)
    service.start_session()
    service.record_selection(7, 'gallery')
    clock.advance(10.0)
    service.record_selection(7, 'single')
    clock.advance(5.0)
    service.record_selection(9, 'single')
    clock.advance(2.0)
    service.end_session()

    # A later session appends to the same file
    second, clock2 = _service(tmp_path)
    second.start_session()
    second.record_selection(7, 'gallery')
    clock2.advance(1.0)
    second.end_session()

    summary = AOIInteractionLogService.summarize(str(tmp_path / LOG_FILENAME))
    assert summary[7] == {
        'clicks': 3, 'gallery_views': 2, 'single_views': 1, 'dwell_s': 16.0}
    assert summary[9]['clicks'] == 1
    assert summary[9]['dwell_s'] == 2.0


def test_summarize_skips_corrupt_lines(tmp_path):
    service, clock = _service(tmp_path)
    service.record_selection(3, 'single')
    clock.advance(1.0)
    service.end_session()
    with open(tmp_path / LOG_FILENAME, 'a', encoding='utf-8') as f:
        f.write('{"event": "view", "aoi": 4, "dwell_\n')  # crash mid-write

    summary = AOIInteractionLogService.summarize(str(tmp_path / LOG_FILENAME))
    assert list(summary) == [3]


def test_summarize_missing_file_is_empty(tmp_path):
    assert AOIInteractionLogService.summarize(str(tmp_path / "nope.jsonl")) == {}


def test_unwritable_path_degrades_silently(tmp_path):
    service = AOIInteractionLogService(str(tmp_path))  # a directory: open() fails
    service.start_session()
    service.record_selection(1, 'single')
    service.end_session()  # no exception raised
    assert service._disabled
