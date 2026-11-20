"""Teardown for a QThread that outlived its wait()."""

from PySide6.QtCore import Qt

# Threads whose wait() timed out, with the objects they are still using,
# held until they finish. Keyed by id(thread); see retire_running_thread.
_retired = {}


def retire_running_thread(thread, *companions) -> None:
    """Keep a QThread that is still running alive until it has finished.

    Call this instead of dropping the last reference when ``wait()`` timed
    out. PySide deletes an unparented QThread when its last Python reference
    goes, and if that happens before the thread has finished - the caller
    letting go, or a QThread subclass's own ``run()`` returning - Qt aborts
    the process with "QThread: Destroyed while thread is still running".
    That is a hard crash with nothing in adiat_logs.txt; it took down field
    sessions after an HDMI capture device hung in a native open.

    Args:
        thread: The QThread that did not stop in time.
        companions: Objects the thread is still using (e.g. a worker moved
            onto it) that must outlive it too.

    Everything is released on the main thread once ``finished`` has fired.
    """
    key = id(thread)
    _retired[key] = (thread, companions)

    def _release():
        if _retired.pop(key, None) is not None:
            thread.deleteLater()

    thread.finished.connect(_release, Qt.QueuedConnection)
    if thread.isFinished():  # it finished between the timed-out wait and the connect
        _release()
