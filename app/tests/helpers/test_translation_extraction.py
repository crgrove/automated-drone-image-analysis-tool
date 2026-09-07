"""Visible strings in algorithm UI must be extractable, not just wrapped.

``TranslationMixin._apply_translations`` re-``tr()``s every child label at
construction, so a widget full of bare literals *looks* internationalized -
it calls into Qt's translation machinery on every string it shows. What it
cannot do is put those strings in the catalog: ``pyside6-lupdate`` reads the
source, and it extracts only literal arguments to ``tr()``. A bare
``QLabel("R:")`` and a ``self.tr(variable)`` are both invisible to it, so
the lookup at runtime finds nothing and returns English in every locale.

That failure is silent in both directions - the code reads as translated and
the catalog simply has no entry - which is why this is a test and not a
convention. It walks the source with ``ast``: no Qt, no display, no
extraction run.
"""

import ast
import os
import re

import pytest

APP_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
ALGORITHMS_ROOT = os.path.join(APP_ROOT, 'algorithms')

# Widget constructors whose first string argument is displayed.
DISPLAY_CONSTRUCTORS = {
    'QLabel', 'QPushButton', 'QCheckBox', 'QRadioButton', 'QGroupBox',
    'QToolButton', 'QAction',
}

# Methods whose string argument is displayed.
DISPLAY_METHODS = {
    'setText', 'setToolTip', 'setWindowTitle', 'setPlaceholderText',
    'setTitle', 'addItem', 'setItemText', 'setTabText', 'setStatusTip',
}

# A literal has to contain a real word to be worth translating. "-", "%",
# "1", "12.5 m" and object names do not.
_WORD = re.compile(r'[A-Za-z]{3,}')

# Marker comment that licenses a tr() over a runtime value. Required at the
# call site so the exception is a decision someone made, not an omission.
_DYNAMIC_MARKER = 'i18n-dynamic'


def _line_text(lines, lineno):
    index = lineno - 1
    return lines[index] if 0 <= index < len(lines) else ''


# Deliberate exclusions, each with its reason. Keyed by the literal text so
# the entry survives the line moving.
ALLOWED_LITERALS = {
    # Stable internal identifiers surfaced in a combo whose readers all use
    # currentData(); translating them would be wrong, not merely pointless.
    'FRAME_DIFF', 'MOG2', 'KNN', 'BOTH',
    'AND', 'OR', 'WEIGHTED',
    # Colour-space and channel names that are the same token in every
    # locale and are compared as keys.
    'LAB', 'RGB', 'HSV', 'BGR',
}


def _iter_source_files():
    for dirpath, _dirnames, filenames in os.walk(ALGORITHMS_ROOT):
        parent = os.path.basename(dirpath)
        if parent not in ('controllers', 'views'):
            continue
        for name in sorted(filenames):
            if not name.endswith('.py'):
                continue
            if name.endswith('_ui.py') or name.endswith('_rc.py'):
                continue  # generated; strings come from the .ui
            yield os.path.join(dirpath, name)


SOURCE_FILES = sorted(_iter_source_files())


def _is_translation_call(node):
    """True for ``x.tr(...)`` and ``QCoreApplication.translate(...)``.

    ``translate`` is qualified deliberately: ``QTransform.translate`` and
    ``QPainter.translate`` are geometry, and matching the bare attribute
    name reports every zoom handler as an i18n defect.
    """
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
        return False
    if node.func.attr == 'tr':
        return True
    return (node.func.attr == 'translate'
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == 'QCoreApplication')


def _display_string_args(node):
    """String constants this call will show to the operator."""
    if not isinstance(node, ast.Call):
        return []

    func = node.func
    if isinstance(func, ast.Name) and func.id in DISPLAY_CONSTRUCTORS:
        candidates = node.args[:1]
    elif isinstance(func, ast.Attribute) and func.attr in DISPLAY_METHODS:
        candidates = node.args[:1]
    else:
        return []

    return [arg for arg in candidates
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str)]


def test_the_walk_found_the_algorithm_sources():
    """A silently empty file list would make every case below vacuous."""
    assert len(SOURCE_FILES) >= 20


@pytest.mark.parametrize('path', SOURCE_FILES,
                         ids=lambda p: os.path.relpath(p, ALGORITHMS_ROOT))
def test_visible_literals_are_extractable(path):
    with open(path, encoding='utf-8') as handle:
        tree = ast.parse(handle.read(), filename=path)

    offenders = []
    for node in ast.walk(tree):
        for arg in _display_string_args(node):
            text = arg.value
            if not _WORD.search(text):
                continue          # punctuation, digits, units
            if text.strip() in ALLOWED_LITERALS:
                continue
            offenders.append(f"line {arg.lineno}: {text!r}")

    assert not offenders, (
        f"{os.path.relpath(path, APP_ROOT)} shows string literals that "
        f"pyside6-lupdate will not extract; wrap each in self.tr(\"...\") "
        f"with the literal inside the call:\n  " + "\n  ".join(offenders)
    )


@pytest.mark.parametrize('path', SOURCE_FILES,
                         ids=lambda p: os.path.relpath(p, ALGORITHMS_ROOT))
def test_no_translation_call_wraps_a_variable(path):
    """``self.tr(label)`` extracts nothing and returns English everywhere.

    It is worse than a bare literal because it reads as compliant. Use a
    literal lookup table - see ``_preset_label`` in the row wizard widgets.
    """
    with open(path, encoding='utf-8') as handle:
        source = handle.read()
    tree = ast.parse(source, filename=path)
    source_lines = source.splitlines()

    offenders = []
    for node in ast.walk(tree):
        if not _is_translation_call(node) or not node.args:
            continue
        first = node.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            continue
        if isinstance(first, ast.JoinedStr):
            # An f-string is a literal template; lupdate cannot use it
            # either, but flagging those belongs to its own change.
            continue
        if _DYNAMIC_MARKER in _line_text(source_lines, node.lineno):
            # An explicit, documented exception: the string genuinely
            # arrives at runtime (operator config, a plugin) and the
            # lookup is best-effort. The marker is required so the
            # decision is visible at the call site rather than inferred.
            continue
        offenders.append(f"line {node.lineno}: tr() over a non-literal")

    assert not offenders, (
        f"{os.path.relpath(path, APP_ROOT)}:\n  " + "\n  ".join(offenders)
    )
