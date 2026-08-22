"""Tests for the PyInstaller spec's algorithm hidden-import collection.

Algorithm packages are imported by dotted path at runtime (importlib driven by
algorithms.conf), so PyInstaller cannot see them statically and a missing hidden
import only surfaces in the frozen build. The streaming AI Person Detector
shipped that way: the wizard's parameters page died with "No module named
'algorithms.streaming.AIPersonDetector'" while running fine from source. These
tests exercise app.spec's collector against algorithms.conf so the gap fails
here instead of in the field.
"""

import ast
import json
import os

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SPEC_PATH = os.path.join(REPO_ROOT, 'app.spec')
CONF_PATH = os.path.join(REPO_ROOT, 'app', 'algorithms.conf')


@pytest.fixture(scope='module')
def collected_modules():
    """Run app.spec's real collect_algorithm_modules().

    The spec cannot be imported outright - it calls PyInstaller-injected globals
    (Analysis, EXE, ...) at module scope - so lift just the collector out of its
    AST and execute that. This keeps the test bound to the shipped code rather
    than to a copy of the walk.
    """
    with open(SPEC_PATH, encoding='utf-8') as handle:
        tree = ast.parse(handle.read(), filename=SPEC_PATH)

    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == 'collect_algorithm_modules':
            namespace = {'os': os, 'spec_dir': REPO_ROOT}
            exec(compile(ast.Module(body=[node], type_ignores=[]), SPEC_PATH, 'exec'), namespace)
            return namespace['collect_algorithm_modules']()

    pytest.fail("app.spec no longer defines collect_algorithm_modules()")


@pytest.fixture(scope='module')
def algorithm_config():
    with open(CONF_PATH, encoding='utf-8') as handle:
        return json.load(handle)


def test_streaming_controller_modules_are_bundled(collected_modules, algorithm_config):
    """Every streaming_algorithms 'module' path must be a hidden import."""
    for entry in algorithm_config['streaming_algorithms']:
        assert entry['module'] in collected_modules, (
            f"{entry['name']} streaming controller module is missing from the frozen build"
        )


def test_streaming_wizard_controllers_are_bundled(collected_modules, algorithm_config):
    """The setup guide imports <Name>WizardController alongside the controller."""
    for entry in algorithm_config['streaming_algorithms']:
        package = entry['module'].rsplit('.controllers.', 1)[0]
        wizard = f"{package}.controllers.{entry['name']}WizardController"
        assert wizard in collected_modules, (
            f"{entry['name']} streaming wizard controller is missing from the frozen build"
        )


def test_image_algorithm_modules_are_bundled(collected_modules, algorithm_config):
    """Image controllers/wizards/services are importlib-loaded by name too."""
    for entry in algorithm_config['algorithms']:
        package = f"algorithms.images.{entry['name']}"
        expected = [
            f"{package}.controllers.{entry['controller']}",
            f"{package}.controllers.{entry['wizard_controller']}",
            f"{package}.services.{entry['service']}",
        ]
        for module in expected:
            assert module in collected_modules, (
                f"{module} is missing from the frozen build"
            )


def test_collected_modules_all_exist_on_disk(collected_modules):
    """Guards the other direction: stale entries for deleted packages.

    The hand-maintained list this collector replaced still named a
    MotionDetection streaming package long after it was removed.
    """
    app_root = os.path.join(REPO_ROOT, 'app')
    for module in collected_modules:
        path = os.path.join(app_root, *module.split('.'))
        assert os.path.isdir(path) or os.path.isfile(path + '.py'), (
            f"{module} is collected as a hidden import but does not exist"
        )


def test_no_duplicate_hidden_imports(collected_modules):
    assert len(collected_modules) == len(set(collected_modules))
