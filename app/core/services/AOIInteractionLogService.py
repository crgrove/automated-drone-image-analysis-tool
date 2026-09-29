"""AOIInteractionLogService - Per-run log of AOI review activity.

Records which AOIs a reviewer selected, in which view mode (gallery vs
single-image), and how long each stayed selected. Written as an append-only
JSONL sidecar (``ADIAT_ReviewLog.jsonl``) beside the run's ``ADIAT_Data.xml``:
appending keeps it crash-safe, later sessions simply add lines, and the
results XML format is untouched (no compatibility exposure).

Dwell definition: the time from an AOI's selection to the next terminating
event - the next selection, a deselection, an image change, a gallery/single
mode toggle, the viewer window deactivating, or the viewer closing - capped
at DWELL_CAP_S so a selection left overnight does not dominate totals. Time
is measured with a monotonic clock (injectable for tests); event records also
carry wall-clock timestamps for humans reading the file.

All writes are best-effort: a results folder on read-only media must never
break the review, so failures log one warning and the service goes quiet.
"""

import getpass
import json
import os
import time
import uuid
from datetime import datetime

from core.services.LoggerService import LoggerService

LOG_FILENAME = "ADIAT_ReviewLog.jsonl"

# A dwell longer than this is a walked-away-from screen, not review time.
DWELL_CAP_S = 300.0

# Interval-terminating reasons (the 'reason' field of every view record).
REASON_NEXT_SELECT = 'next_select'
REASON_DESELECT = 'deselect'
REASON_IMAGE_CHANGE = 'image_change'
REASON_MODE_TOGGLE = 'mode_toggle'
REASON_WINDOW_UNFOCUSED = 'window_unfocused'
REASON_CLOSE = 'close'


class AOIInteractionLogService:
    """Append-only JSONL recorder for AOI selection activity."""

    def __init__(self, log_path, clock=time.monotonic, logger=None):
        """
        Args:
            log_path (str): Path of the JSONL sidecar to append to.
            clock (callable): Monotonic time source, injectable for tests.
            logger: LoggerService override, mainly for tests.
        """
        self.log_path = log_path
        self._clock = clock
        self.logger = logger or LoggerService()
        self.session_id = uuid.uuid4().hex
        self._disabled = False
        # The open interval: (aoi_number, mode, start_monotonic) or None.
        self._open_interval = None

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def start_session(self, review_id=None, reviewer_name=None):
        """Open the session: one record identifying who is reviewing.

        Args:
            review_id: The run's persistent review id when the XML carries
                one; defaults to this session's id.
            reviewer_name: Defaults to the OS username.
        """
        self._append({
            'event': 'session_start',
            'session': self.session_id,
            'review_id': review_id or self.session_id,
            'reviewer': reviewer_name or self._default_reviewer(),
        })

    def record_selection(self, aoi_number, mode):
        """Record that an AOI became selected.

        Closes any open interval first (its dwell ends now). A repeat of the
        exact same selection while its interval is open is ignored - style
        refreshes and gallery/sidebar sync re-enter selection without the
        user doing anything.

        Args:
            aoi_number: The AOI's run-wide number.
            mode (str): 'gallery' or 'single'.
        """
        if aoi_number is None:
            return
        if self._open_interval is not None:
            open_number, open_mode, _ = self._open_interval
            if open_number == aoi_number and open_mode == mode:
                return
            self.end_current_interval(REASON_NEXT_SELECT)
        self._open_interval = (aoi_number, mode, self._clock())

    def end_current_interval(self, reason):
        """Close the open selection interval, writing its view record.

        No-op when nothing is selected.

        Args:
            reason (str): One of the REASON_* constants.
        """
        if self._open_interval is None:
            return
        aoi_number, mode, started = self._open_interval
        self._open_interval = None
        dwell = max(0.0, min(self._clock() - started, DWELL_CAP_S))
        self._append({
            'event': 'view',
            'session': self.session_id,
            'aoi': aoi_number,
            'mode': mode,
            'dwell_s': round(dwell, 3),
            'reason': reason,
        })

    def end_session(self):
        """Close the open interval (if any) and the session."""
        self.end_current_interval(REASON_CLOSE)
        self._append({'event': 'session_end', 'session': self.session_id})

    # ------------------------------------------------------------------
    # Reading
    # ------------------------------------------------------------------

    @classmethod
    def summarize(cls, log_path):
        """Aggregate a review log across all its sessions.

        Args:
            log_path (str): Path to an ADIAT_ReviewLog.jsonl file.

        Returns:
            dict: aoi_number -> {'clicks', 'gallery_views', 'single_views',
            'dwell_s'}. Empty when the file is missing or unreadable.
            Corrupt lines (a crash mid-write) are skipped.
        """
        summary = {}
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except OSError:
            return summary

        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if record.get('event') != 'view':
                continue
            aoi = record.get('aoi')
            if aoi is None:
                continue
            entry = summary.setdefault(aoi, {
                'clicks': 0, 'gallery_views': 0, 'single_views': 0, 'dwell_s': 0.0})
            entry['clicks'] += 1
            if record.get('mode') == 'gallery':
                entry['gallery_views'] += 1
            else:
                entry['single_views'] += 1
            try:
                entry['dwell_s'] += float(record.get('dwell_s', 0.0))
            except (TypeError, ValueError):
                pass
        return summary

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _default_reviewer():
        try:
            return getpass.getuser()
        except Exception:
            return 'unknown'

    def _append(self, record):
        """Append one JSON line, flushed immediately; degrade silently."""
        if self._disabled:
            return
        record.setdefault('t', datetime.now().isoformat(timespec='seconds'))
        try:
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(record) + '\n')
                f.flush()
                os.fsync(f.fileno())
        except OSError as e:
            # Read-only results folder: record once, then stay quiet.
            self.logger.warning(
                f"AOI interaction log disabled ({self.log_path}): {e}")
            self._disabled = True
