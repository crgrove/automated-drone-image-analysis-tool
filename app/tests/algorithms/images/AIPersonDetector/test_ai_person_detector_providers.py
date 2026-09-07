"""Tests for ONNX execution-provider selection in the AI Person Detector.

Provider selection arrived untested, and it is the kind of code that cannot
be tested by running it: the machine running the suite has whichever
accelerator it has. So the platform check and the onnxruntime call are both
patched, and these tests assert what gets *requested* and what gets *logged* -
which is all that platform branching can promise.

Why the logging matters enough to test: ONNX Runtime does not raise when a
requested provider is unavailable. It emits a Python warning and quietly
returns a CPU session. Nothing else in the app would reveal that, and on
macOS the difference is not only speed - CoreML runs on the Neural Engine at
fp16, so scores near the confidence threshold can move.
"""

from unittest.mock import MagicMock, patch

import pytest

from algorithms.images.AIPersonDetector.services.AIPersonDetectorService import (
    AIPersonDetectorService,
)


@pytest.fixture
def service():
    """A service with the ONNX-dependent constructor bypassed."""
    svc = AIPersonDetectorService.__new__(AIPersonDetectorService)
    svc.logger = MagicMock()
    svc.model_path = 'model.onnx'
    svc.cpu_only = False
    return svc


def fake_session(active_providers):
    session = MagicMock()
    session.get_providers.return_value = list(active_providers)
    return session


# ---------------------------------------------------------------------------
# accelerated_provider_name
# ---------------------------------------------------------------------------

def test_macos_uses_coreml():
    with patch(
        'algorithms.images.AIPersonDetector.services.AIPersonDetectorService.sys.platform',
        'darwin',
    ):
        assert AIPersonDetectorService.accelerated_provider_name() == 'CoreMLExecutionProvider'


@pytest.mark.parametrize("platform_name", ['win32', 'linux', 'cygwin'])
def test_non_macos_uses_directml(platform_name):
    with patch(
        'algorithms.images.AIPersonDetector.services.AIPersonDetectorService.sys.platform',
        platform_name,
    ):
        assert AIPersonDetectorService.accelerated_provider_name() == 'DmlExecutionProvider'


# ---------------------------------------------------------------------------
# which providers get requested
# ---------------------------------------------------------------------------

def test_macos_requests_coreml_then_cpu(service):
    with patch(
        'algorithms.images.AIPersonDetector.services.AIPersonDetectorService.sys.platform',
        'darwin',
    ), patch(
        'algorithms.images.AIPersonDetector.services.AIPersonDetectorService.ort'
    ) as mock_ort:
        mock_ort.InferenceSession.return_value = fake_session(['CoreMLExecutionProvider'])

        service._create_onnx_session()

        assert mock_ort.InferenceSession.call_args.kwargs['providers'] == [
            'CoreMLExecutionProvider', 'CPUExecutionProvider'
        ]


def test_windows_requests_directml_then_cpu(service):
    with patch(
        'algorithms.images.AIPersonDetector.services.AIPersonDetectorService.sys.platform',
        'win32',
    ), patch(
        'algorithms.images.AIPersonDetector.services.AIPersonDetectorService.ort'
    ) as mock_ort:
        mock_ort.InferenceSession.return_value = fake_session(['DmlExecutionProvider'])

        service._create_onnx_session()

        assert mock_ort.InferenceSession.call_args.kwargs['providers'] == [
            'DmlExecutionProvider', 'CPUExecutionProvider'
        ]


def test_cpu_only_never_requests_an_accelerator(service):
    """cpu_only must not be second-guessed by the platform branch."""
    service.cpu_only = True

    with patch(
        'algorithms.images.AIPersonDetector.services.AIPersonDetectorService.sys.platform',
        'darwin',
    ), patch(
        'algorithms.images.AIPersonDetector.services.AIPersonDetectorService.ort'
    ) as mock_ort:
        mock_ort.InferenceSession.return_value = fake_session(['CPUExecutionProvider'])

        service._create_onnx_session()

        assert mock_ort.InferenceSession.call_count == 1
        assert mock_ort.InferenceSession.call_args.kwargs['providers'] == ['CPUExecutionProvider']


# ---------------------------------------------------------------------------
# fallback
# ---------------------------------------------------------------------------

def test_falls_back_to_cpu_when_the_accelerated_session_raises(service):
    with patch(
        'algorithms.images.AIPersonDetector.services.AIPersonDetectorService.sys.platform',
        'darwin',
    ), patch(
        'algorithms.images.AIPersonDetector.services.AIPersonDetectorService.ort'
    ) as mock_ort:
        cpu_session = fake_session(['CPUExecutionProvider'])
        mock_ort.InferenceSession.side_effect = [RuntimeError('no CoreML here'), cpu_session]

        result = service._create_onnx_session()

        assert result is cpu_session
        assert mock_ort.InferenceSession.call_count == 2
        assert mock_ort.InferenceSession.call_args.kwargs['providers'] == ['CPUExecutionProvider']
        service.logger.warning.assert_called()
        assert 'CoreMLExecutionProvider' in service.logger.warning.call_args[0][0]


def test_raises_a_clear_error_when_even_cpu_fails(service):
    with patch(
        'algorithms.images.AIPersonDetector.services.AIPersonDetectorService.ort'
    ) as mock_ort:
        mock_ort.InferenceSession.side_effect = RuntimeError('model is corrupt')

        with pytest.raises(RuntimeError, match='could not be loaded with any provider'):
            service._create_onnx_session()

        service.logger.error.assert_called()


# ---------------------------------------------------------------------------
# the silent-downgrade log (the reason this file exists)
# ---------------------------------------------------------------------------

def test_warns_when_onnx_silently_downgrades_to_cpu(service):
    """ORT returns a CPU session without raising if the provider is missing."""
    with patch(
        'algorithms.images.AIPersonDetector.services.AIPersonDetectorService.sys.platform',
        'darwin',
    ), patch(
        'algorithms.images.AIPersonDetector.services.AIPersonDetectorService.ort'
    ) as mock_ort:
        # no exception - just a session that did not get what was asked for
        mock_ort.InferenceSession.return_value = fake_session(['CPUExecutionProvider'])
        mock_ort.get_available_providers.return_value = ['CPUExecutionProvider']

        service._create_onnx_session()

        service.logger.warning.assert_called_once()
        message = service.logger.warning.call_args[0][0]
        assert 'CoreMLExecutionProvider' in message
        assert 'not available' in message


def test_logs_the_active_providers_when_acceleration_is_used(service):
    with patch(
        'algorithms.images.AIPersonDetector.services.AIPersonDetectorService.sys.platform',
        'win32',
    ), patch(
        'algorithms.images.AIPersonDetector.services.AIPersonDetectorService.ort'
    ) as mock_ort:
        mock_ort.InferenceSession.return_value = fake_session(
            ['DmlExecutionProvider', 'CPUExecutionProvider']
        )

        service._create_onnx_session()

        service.logger.warning.assert_not_called()
        service.logger.info.assert_called_once()
        assert 'DmlExecutionProvider' in service.logger.info.call_args[0][0]


def test_cpu_only_run_is_logged_without_a_downgrade_warning(service):
    """Asking for CPU and getting CPU is not a downgrade."""
    service.cpu_only = True

    with patch(
        'algorithms.images.AIPersonDetector.services.AIPersonDetectorService.ort'
    ) as mock_ort:
        mock_ort.InferenceSession.return_value = fake_session(['CPUExecutionProvider'])

        service._create_onnx_session()

        service.logger.warning.assert_not_called()
        service.logger.info.assert_called_once()


def test_a_session_without_a_provider_list_is_still_returned(service):
    """Diagnostics must never be the reason analysis cannot start."""
    with patch(
        'algorithms.images.AIPersonDetector.services.AIPersonDetectorService.ort'
    ) as mock_ort:
        session = MagicMock()
        session.get_providers.side_effect = AttributeError('no such method')
        mock_ort.InferenceSession.return_value = session

        assert service._create_onnx_session() is session
