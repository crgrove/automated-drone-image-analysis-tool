"""Tests for run_in_workers, using real worker processes.

eval is the target so one callable can return, crash (os._exit) or wedge (sleep).
"""
import multiprocessing
import time
from multiprocessing import Pipe

from helpers.WorkerProcessHelper import run_in_workers

QUICK = "6 * 7"
CRASH = "__import__('os')._exit(3)"
WEDGE = "__import__('time').sleep(60)"


def _tasks(**exprs):
    return [(key, (expr,)) for key, expr in exprs.items()]


def test_crash_and_timeout_cost_only_their_own_task():
    cancel_reader, _ = Pipe(duplex=False)
    tasks = _tasks(first=QUICK, crash=CRASH, wedged=WEDGE, after=QUICK)

    results = dict(run_in_workers(tasks, 2, cancel_reader, eval, timeout=3))

    assert results["first"] == 42 and results["after"] == 42
    assert isinstance(results["crash"], RuntimeError)
    assert isinstance(results["wedged"], TimeoutError)
    assert multiprocessing.active_children() == []


def test_cancel_kills_tasks_in_progress_at_once():
    cancel_reader, cancel_writer = Pipe(duplex=False)
    results = run_in_workers(_tasks(quick=QUICK, slow=WEDGE), 2, cancel_reader, eval, timeout=300)

    assert next(results) == ("quick", 42)
    started = time.monotonic()
    cancel_writer.send(None)
    assert list(results) == []
    assert time.monotonic() - started < 10  # not the slow task's 60 s
    assert multiprocessing.active_children() == []


def test_closing_mid_run_kills_every_worker():
    """process_files closes the generator when it sees the cancel flag, possibly
    while a worker's result is being handed over - that worker must die too."""
    cancel_reader, _ = Pipe(duplex=False)
    results = run_in_workers(_tasks(quick=QUICK, slow=WEDGE), 2, cancel_reader, eval, timeout=300)

    next(results)
    results.close()
    assert multiprocessing.active_children() == []


def test_already_cancelled_run_starts_no_workers():
    cancel_reader, cancel_writer = Pipe(duplex=False)
    cancel_writer.send(None)

    assert list(run_in_workers(_tasks(a=QUICK), 2, cancel_reader, eval, timeout=300)) == []
    assert multiprocessing.active_children() == []
