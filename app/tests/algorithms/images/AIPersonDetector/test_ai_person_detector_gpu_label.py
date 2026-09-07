"""Tests for the AI Person Detector's GPU status label.

The label used to be decided from the platform alone, which made it wrong in
both directions: macOS was told it had no GPU even once CoreML acceleration
was in the service, and every other platform was told it had one whether or
not DirectML was actually installed. It now reports what ONNX Runtime says it
can offer.
"""

from unittest.mock import MagicMock, patch

import pytest

from algorithms.images.AIPersonDetector.controllers.AIPersonDetectorController import (
    AIPersonDetectorController,
)

CONTROLLER = (
    'algorithms.images.AIPersonDetector.controllers'
    '.AIPersonDetectorController.AIPersonDetectorController'
)


@pytest.fixture
def controller(qtbot):
    # mirrors the AIPersonDetector entry in app/algorithms.conf
    widget = AIPersonDetectorController({'name': 'AIPersonDetector', 'type': 'RGB'}, 'dark')
    qtbot.addWidget(widget)
    return widget


def test_label_reports_available_when_the_provider_is_present(controller):
    with patch(f'{CONTROLLER}._acceleration_available', return_value=True):
        controller._update_gpu_label()

    text = controller.GPULabel.text()
    assert 'GPU Available' in text
    assert 'Not Available' not in text
    assert 'green' in text


def test_label_reports_unavailable_when_the_provider_is_missing(controller):
    with patch(f'{CONTROLLER}._acceleration_available', return_value=False):
        controller._update_gpu_label()

    text = controller.GPULabel.text()
    assert 'GPU Not Available' in text
    assert 'red' in text


def test_label_does_not_change_cpu_only(controller):
    """cpu_only picks the 640 model over the 1024 one - hardware must not.

    Deriving it from provider availability would silently change which
    network runs on every machine without an accelerator.
    """
    controller.cpu_only = False

    with patch(f'{CONTROLLER}._acceleration_available', return_value=False):
        controller._update_gpu_label()

    assert controller.cpu_only is False
    assert controller.get_options()['cpu_only'] is False


def test_macos_reports_available_when_coreml_is_present(controller):
    """The case the old hardcoded label got wrong."""
    with patch(
        'algorithms.images.AIPersonDetector.services.AIPersonDetectorService.sys.platform',
        'darwin',
    ), patch('onnxruntime.get_available_providers',
             return_value=['CoreMLExecutionProvider', 'CPUExecutionProvider']):
        controller._update_gpu_label()

    assert 'GPU Available' in controller.GPULabel.text()


def test_non_macos_reports_unavailable_without_directml(controller):
    """The other case it got wrong: Linux, or Windows with no DirectX12 GPU."""
    with patch(
        'algorithms.images.AIPersonDetector.services.AIPersonDetectorService.sys.platform',
        'linux',
    ), patch('onnxruntime.get_available_providers',
             return_value=['CPUExecutionProvider']):
        controller._update_gpu_label()

    assert 'GPU Not Available' in controller.GPULabel.text()


def test_acceleration_probe_survives_a_broken_onnxruntime(controller):
    """A build whose ONNX DLL failed to load must still render the widget."""
    controller.logger = MagicMock()

    with patch('onnxruntime.get_available_providers', side_effect=OSError('DLL load failed')):
        assert controller._acceleration_available() is False

    controller.logger.warning.assert_called_once()


def test_label_strings_are_translatable(controller):
    """Both strings must go through tr() so they reach the catalogs."""
    with patch(f'{CONTROLLER}.tr', side_effect=lambda s: f'<<{s}>>') as mock_tr:
        with patch(f'{CONTROLLER}._acceleration_available', return_value=True):
            controller._update_gpu_label()
        assert '<<GPU Available>>' in controller.GPULabel.text()

        with patch(f'{CONTROLLER}._acceleration_available', return_value=False):
            controller._update_gpu_label()
        assert '<<GPU Not Available>>' in controller.GPULabel.text()

    assert {call.args[0] for call in mock_tr.call_args_list} == {
        'GPU Available', 'GPU Not Available'
    }
