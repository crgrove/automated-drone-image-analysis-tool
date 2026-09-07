"""No fixed delay may stand in for an event (CLAUDE.md 2.9).

A delay encodes an assumption about machine speed. It passes on the
development machine and fails in the field - on network volumes, on slower
hardware, under macOS timing - and each failure invites a longer delay. The
rule is absolute for coordination: consume a completion signal, or use an
explicit request/consume handoff.

Timers stay legitimate where the delay itself is the requirement: a toast
that hides after six seconds, a debounce, a bounded give-up guard, a poll of
a source that emits nothing. Those cases are indistinguishable from a settle
wait by shape alone, so this test asks for them to be *declared*: a
``# 2.9:`` comment on or just above the call, saying which.

Scope: ``QTimer.singleShot`` with a non-zero delay - the settle-wait shape,
and the one every violation in the audited set took. A zero delay is a
deliberate yield to the event loop, not a wait. Named ``QTimer`` objects
driven by ``.start(ms)`` are overwhelmingly debounces and polls and are not
covered here; if a settle wait is ever written that way, it will need its own
rule.
"""

import os
import re

import pytest

APP_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

# QTimer.singleShot(<delay>, ...) where the delay is not a literal 0.
_SINGLE_SHOT = re.compile(r"QTimer\.singleShot\(\s*(?P<delay>[^,\n]*)")
_MARKER = "# 2.9:"
_CONTEXT_LINES = 4


def _production_sources():
    for dirpath, dirnames, filenames in os.walk(APP_ROOT):
        dirnames[:] = [d for d in dirnames
                       if d not in ('tests', '__pycache__')]
        for name in sorted(filenames):
            if name.endswith('.py') and not name.endswith('_rc.py'):
                yield os.path.join(dirpath, name)


def _delayed_single_shots(path):
    """(line number, delay text) for each non-zero-delay singleShot."""
    with open(path, encoding='utf-8') as handle:
        lines = handle.read().splitlines()

    found = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('#'):
            continue                      # a comment about the call, not one
        match = _SINGLE_SHOT.search(line)
        if not match:
            continue
        delay = match.group('delay').strip()
        if delay in ('0', '0.0', ''):
            continue                      # event-loop yield, not a wait
        found.append((index + 1, delay, lines))
    return found


CALL_SITES = [(path, lineno, delay, lines)
              for path in _production_sources()
              for lineno, delay, lines in _delayed_single_shots(path)]


def test_the_source_tree_was_actually_walked():
    """An empty file list would make the case below vacuous."""
    assert len(list(_production_sources())) >= 200


@pytest.mark.parametrize(
    'path, lineno, delay, lines', CALL_SITES,
    ids=[f"{os.path.relpath(p, APP_ROOT)}:{n}" for p, n, _d, _l in CALL_SITES])
def test_a_delayed_timer_declares_why(path, lineno, delay, lines):
    start = max(0, lineno - 1 - _CONTEXT_LINES)
    context = "\n".join(lines[start:lineno])

    assert _MARKER in context, (
        f"{os.path.relpath(path, APP_ROOT)}:{lineno} waits {delay} ms with no "
        f"'{_MARKER}' justification.\n"
        f"If it is waiting for something to happen, consume that thing's "
        f"completion signal instead (CLAUDE.md 2.9). If the delay itself is "
        f"the requirement - a toast, a debounce, a give-up guard, a poll of a "
        f"source that emits nothing - say so in a '{_MARKER}' comment."
    )
