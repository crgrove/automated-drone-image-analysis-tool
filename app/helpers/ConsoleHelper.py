"""Windows console attachment for headless CLI runs.

The packaged Windows build is a GUI-subsystem exe (``console=False`` in
app.spec), so it has no console: ``print()`` output from the batch CLI is
swallowed when the exe is launched from a terminal. Attaching to the
parent process's console restores visible stdout/stderr for CLI use while
leaving double-click GUI launches untouched (there is no parent console to
attach to, so the call is a silent no-op).

No-op on macOS/Linux, where the binary already behaves like a normal
terminal program.
"""

import os
import sys

# kernel32.AttachConsole sentinel: attach to the parent process's console.
ATTACH_PARENT_PROCESS = -1


def _needs_rebind(stream):
    """True when a std stream is absent or not backed by a real handle.

    A parent-shell redirection (``> log.txt``) gives the process valid
    handles and Python real file streams — those must be left alone. The
    windowed-build placeholders (None or PyInstaller's NullWriter) have no
    usable fileno and should be rebound to the attached console.
    """
    if stream is None:
        return True
    try:
        return stream.fileno() < 0
    except Exception:
        return True


def attach_parent_console(kernel32=None, opener=open):
    """Attach to the parent terminal's console and rebind std streams.

    Args:
        kernel32: Injectable kernel32 module for tests; defaults to
            ``ctypes.windll.kernel32``.
        opener: Injectable ``open`` for tests.

    Returns:
        True when a parent console was attached, False otherwise (not
        Windows, a console already exists, or there is no parent console —
        e.g. the app was double-clicked).
    """
    if os.name != 'nt':
        return False

    if kernel32 is None:
        import ctypes
        kernel32 = ctypes.windll.kernel32

    if kernel32.GetConsoleWindow():
        # Already have a console (e.g. running from source with python.exe).
        return False

    if not kernel32.AttachConsole(ATTACH_PARENT_PROCESS):
        # No parent console — GUI launch. Stay silent.
        return False

    for name in ('stdout', 'stderr'):
        if _needs_rebind(getattr(sys, name, None)):
            try:
                setattr(sys, name, opener(
                    'CONOUT$', 'w', buffering=1, encoding='utf-8', errors='replace'
                ))
            except OSError:
                pass
    return True
