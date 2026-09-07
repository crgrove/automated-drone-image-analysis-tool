"""Rules for the ``*_ui.py`` modules, generated and hand-maintained alike.

Two kinds of file share the suffix and almost nothing else:

* **generated** - compiled from a ``.ui`` by ``pyside6-uic``. Never edited by
  hand, and deliberately skipped by ``scripts/extract_translations.py``
  because lupdate already reads its strings from the ``.ui`` itself.
* **hand-maintained** - no ``.ui`` exists. CLAUDE.md 2.6 wants these
  converted; until they are, 2.8 requires them to implement
  ``retranslateUi`` and set their visible strings there.

The trap is that the two are indistinguishable by name, so the
generated-file exclusion silently swallowed the hand-maintained ones too.
Every string in the main streaming window - its own title, "Stream
Controls", "Algorithm Controls", "Video Stream" - had no catalog entry in
any of the four shipped languages, while the file looked entirely correct:
it called ``QCoreApplication.translate`` for each one, just through a local
alias that lupdate cannot follow.
"""

import ast
import os

import pytest

APP_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
REPO_ROOT = os.path.dirname(APP_ROOT)
RESOURCES = os.path.join(REPO_ROOT, 'resources', 'views')


def _ui_sources():
    names = set()
    for dirpath, _dirnames, filenames in os.walk(RESOURCES):
        for name in filenames:
            if name.endswith('.ui'):
                names.add(name[:-len('.ui')])
    return names


def _hand_maintained_ui_modules():
    """``*_ui.py`` modules with no ``.ui`` to regenerate them from."""
    ui_sources = _ui_sources()
    found = []
    for dirpath, dirnames, filenames in os.walk(APP_ROOT):
        dirnames[:] = [d for d in dirnames
                       if d not in ('tests', '__pycache__')]
        for name in filenames:
            if not name.endswith('_ui.py'):
                continue
            if name[:-len('_ui.py')] in ui_sources:
                continue          # generated
            found.append(os.path.join(dirpath, name))
    return sorted(found)


HAND_MAINTAINED = _hand_maintained_ui_modules()


def test_the_resources_tree_was_actually_read():
    """An empty .ui set would classify every generated module as hand-written."""
    assert len(_ui_sources()) >= 30


@pytest.mark.parametrize('path', HAND_MAINTAINED,
                         ids=lambda p: os.path.relpath(p, APP_ROOT))
def test_a_hand_maintained_ui_module_implements_retranslate_ui(path):
    """CLAUDE.md 2.8: visible strings must be set in retranslateUi, so the
    window can be re-rendered when the language changes."""
    with open(path, encoding='utf-8') as handle:
        tree = ast.parse(handle.read(), filename=path)

    methods = {node.name for node in ast.walk(tree)
               if isinstance(node, ast.FunctionDef)}
    assert 'retranslateUi' in methods


@pytest.mark.parametrize('path', HAND_MAINTAINED,
                         ids=lambda p: os.path.relpath(p, APP_ROOT))
def test_a_hand_maintained_ui_module_is_extractable(path):
    """No aliasing of the translate call.

    ``pyside6-lupdate`` matches ``QCoreApplication.translate(...)``
    syntactically. ``_translate = QCoreApplication.translate`` followed by
    ``_translate("Ctx", "Text")`` runs correctly and extracts nothing, which
    is the worst combination available: the file reads as internationalized
    and the catalog has no entry to look up.
    """
    with open(path, encoding='utf-8') as handle:
        source = handle.read()
    tree = ast.parse(source, filename=path)

    aliases = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        value = node.value
        if (isinstance(value, ast.Attribute) and value.attr == 'translate'
                and isinstance(node.targets[0], ast.Name)):
            aliases.append(f"line {node.lineno}: "
                           f"{node.targets[0].id} = ...translate")

    assert not aliases, (
        f"{os.path.relpath(path, APP_ROOT)} aliases the translate call, so "
        f"lupdate extracts none of its strings:\n  " + "\n  ".join(aliases))


@pytest.mark.parametrize('path', HAND_MAINTAINED,
                         ids=lambda p: os.path.relpath(p, APP_ROOT))
def test_extraction_actually_collects_this_module(path):
    """The filter in scripts/extract_translations.py must let it through."""
    import sys

    scripts = os.path.join(REPO_ROOT, 'scripts')
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    from pathlib import Path

    from extract_translations import _is_translatable_source

    ui_files = [Path(os.path.join(dirpath, name))
                for dirpath, _dirs, files in os.walk(RESOURCES)
                for name in files if name.endswith('.ui')]

    assert _is_translatable_source(Path(path), ui_files) is True


def test_generated_modules_stay_excluded():
    """Including them would put every .ui string in the catalog twice."""
    import sys

    scripts = os.path.join(REPO_ROOT, 'scripts')
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    from pathlib import Path

    from extract_translations import _is_translatable_source

    ui_files = [Path(os.path.join(dirpath, name))
                for dirpath, _dirs, files in os.walk(RESOURCES)
                for name in files if name.endswith('.ui')]
    generated = Path(os.path.join(
        APP_ROOT, 'core', 'views', 'streaming', 'ReplayWindow_ui.py'))
    assert generated.exists(), "fixture module moved; pick another generated one"

    assert _is_translatable_source(generated, ui_files) is False
    # And resource modules never carry text.
    assert _is_translatable_source(Path('anything_rc.py'), ui_files) is False
