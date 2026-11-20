"""retire_running_thread: a QThread that outlives its wait() must not crash the process.

Dropping the last reference to a running QThread makes PySide delete it,
and Qt aborts with "QThread: Destroyed while thread is still running". The
abort kills the interpreter, so the scenario runs in a subprocess: a
regression fails this test instead of taking the whole pytest run down.
"""

import os
import subprocess
import sys
import textwrap

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

_SCENARIO = textwrap.dedent("""
    import sys, time
    sys.path.insert(0, {app_dir!r})
    from PySide6.QtCore import QCoreApplication, QObject, QThread, QTimer
    from helpers import ThreadHelper

    app = QCoreApplication(sys.argv)

    class Stuck(QThread):
        def run(self):
            time.sleep(0.4)  # outlives the caller's wait, like a hung capture open

    thread = Stuck()
    companion = QObject()
    thread.start()
    assert not thread.wait(50)
    ThreadHelper.retire_running_thread(thread, companion)
    del thread, companion  # the caller lets go, as disconnect_stream does

    def check():
        assert not ThreadHelper._retired, "retired thread was never released"
        app.quit()
    QTimer.singleShot(1500, check)
    app.exec()
""")


def test_retired_thread_finishes_without_aborting_and_is_released():
    result = subprocess.run(
        [sys.executable, "-c", _SCENARIO.format(app_dir=APP_DIR)],
        capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stderr
