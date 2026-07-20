"""Tests for ConsoleHelper.attach_parent_console.

The Windows packaged build is a GUI-subsystem exe; the batch CLI attaches
to the parent terminal's console so its output is visible. kernel32 and
open() are injected so the decision logic is testable on any platform
without touching a real console.
"""

import io
import os
import sys

import pytest

from helpers.ConsoleHelper import attach_parent_console, _needs_rebind


class _FakeKernel32:
    def __init__(self, has_console=False, attach_ok=True):
        self._has_console = 1 if has_console else 0
        self._attach_ok = 1 if attach_ok else 0
        self.attach_calls = []

    def GetConsoleWindow(self):
        return self._has_console

    def AttachConsole(self, pid):
        self.attach_calls.append(pid)
        return self._attach_ok


class _FakeOpener:
    def __init__(self):
        self.opened = []

    def __call__(self, path, mode, **kwargs):
        self.opened.append(path)
        return io.StringIO()


windows_only = pytest.mark.skipif(os.name != 'nt', reason="Windows console semantics")


@windows_only
def test_noop_when_console_already_exists():
    """Running from source (python.exe) already has a console — no attach."""
    k32 = _FakeKernel32(has_console=True)
    assert attach_parent_console(kernel32=k32, opener=_FakeOpener()) is False
    assert k32.attach_calls == []


@windows_only
def test_silent_when_no_parent_console():
    """Double-click GUI launch: AttachConsole fails and nothing changes."""
    k32 = _FakeKernel32(has_console=False, attach_ok=False)
    opener = _FakeOpener()
    assert attach_parent_console(kernel32=k32, opener=opener) is False
    assert k32.attach_calls == [-1]
    assert opener.opened == []


@windows_only
def test_attaches_and_rebinds_null_streams(monkeypatch):
    """Windowed build launched from a terminal: attach + rebind stdout/stderr."""
    k32 = _FakeKernel32(has_console=False, attach_ok=True)
    opener = _FakeOpener()
    # Simulate the windowed build's unusable std streams.
    monkeypatch.setattr(sys, 'stdout', None)
    monkeypatch.setattr(sys, 'stderr', None)

    assert attach_parent_console(kernel32=k32, opener=opener) is True

    assert opener.opened == ['CONOUT$', 'CONOUT$']
    assert isinstance(sys.stdout, io.StringIO)
    assert isinstance(sys.stderr, io.StringIO)


@windows_only
def test_attach_preserves_parent_redirection(monkeypatch):
    """`ADIAT.exe batch ... > log.txt` gives real file streams — keep them."""

    class _RealFileLike:
        def fileno(self):
            return 3

    redirected = _RealFileLike()
    k32 = _FakeKernel32(has_console=False, attach_ok=True)
    opener = _FakeOpener()
    monkeypatch.setattr(sys, 'stdout', redirected)
    monkeypatch.setattr(sys, 'stderr', redirected)

    assert attach_parent_console(kernel32=k32, opener=opener) is True

    assert opener.opened == []  # nothing rebound
    assert sys.stdout is redirected
    assert sys.stderr is redirected


@pytest.mark.skipif(os.name == 'nt', reason="non-Windows no-op branch")
def test_noop_on_posix():
    k32 = _FakeKernel32(has_console=False, attach_ok=True)
    assert attach_parent_console(kernel32=k32, opener=_FakeOpener()) is False
    assert k32.attach_calls == []


def test_needs_rebind_decisions():
    """None and fileno-less placeholders rebind; real handles don't."""
    assert _needs_rebind(None) is True
    assert _needs_rebind(io.StringIO()) is True  # fileno raises -> rebind

    class _NullWriter:  # PyInstaller windowed-mode placeholder shape
        def write(self, *_):
            pass

    assert _needs_rebind(_NullWriter()) is True

    class _RealFileLike:
        def fileno(self):
            return 1

    assert _needs_rebind(_RealFileLike()) is False
