"""Tests for ONNX execution-provider selection in the streaming AI Person Detector.

Mirrors app/tests/algorithms/images/AIPersonDetector/test_ai_person_detector_providers.py:
this is the streaming counterpart to that service, and previously requested
DmlExecutionProvider unconditionally on every platform (never checking
sys.platform at all), which is why a Mac would see ONNX Runtime warn that
DirectML was unavailable even though CoreMLExecutionProvider was never tried.

Provider selection cannot be tested by running it: the machine running the
suite has whichever accelerator it has. So the platform check and the
onnxruntime call are both patched, and these tests assert what gets
*requested* and what gets *logged* - which is all that platform branching
can promise.

Why the logging matters enough to test: ONNX Runtime does not raise when a
requested provider is unavailable. It emits a Python warning and quietly
returns a CPU session. Nothing else in the app would reveal that, and on
macOS the difference is not only speed - CoreML runs on the Neural Engine at
fp16, so scores near the confidence threshold can move.
"""

from unittest.mock import MagicMock, patch

import pytest

from algorithms.streaming.AIPersonDetector.services.AIPersonStreamingService import (
    AIPersonStreamingConfig,
    AIPersonStreamingService,
)

MODULE = 'algorithms.streaming.AIPersonDetector.services.AIPersonStreamingService'


@pytest.fixture
def service():
    """A service with the ONNX-dependent constructor bypassed."""
    svc = AIPersonStreamingService.__new__(AIPersonStreamingService)
    svc.logger = MagicMock()
    svc._session_cache = {}
    return svc


def fake_session(active_providers):
    session = MagicMock()
    session.get_providers.return_value = list(active_providers)
    return session


def _get_session(service, cpu_only=False):
    cfg = AIPersonStreamingConfig(cpu_only=cpu_only)
    with patch.object(service, '_resolve_model_path', return_value='model.onnx'):
        return service._get_session(cfg)


# ---------------------------------------------------------------------------
# accelerated_provider_name
# ---------------------------------------------------------------------------

def test_macos_uses_coreml():
    with patch(f'{MODULE}.sys.platform', 'darwin'):
        assert AIPersonStreamingService.accelerated_provider_name() == 'CoreMLExecutionProvider'


@pytest.mark.parametrize("platform_name", ['win32', 'linux', 'cygwin'])
def test_non_macos_uses_directml(platform_name):
    with patch(f'{MODULE}.sys.platform', platform_name):
        assert AIPersonStreamingService.accelerated_provider_name() == 'DmlExecutionProvider'


# ---------------------------------------------------------------------------
# which providers get requested
# ---------------------------------------------------------------------------

def test_macos_requests_coreml_then_cpu(service):
    with patch(f'{MODULE}.sys.platform', 'darwin'), \
            patch(f'{MODULE}.ONNXRUNTIME_AVAILABLE', True), \
            patch(f'{MODULE}.ort') as mock_ort:
        mock_ort.InferenceSession.return_value = fake_session(['CoreMLExecutionProvider'])

        _get_session(service)

        assert mock_ort.InferenceSession.call_args.kwargs['providers'] == [
            'CoreMLExecutionProvider', 'CPUExecutionProvider'
        ]


def test_windows_requests_directml_then_cpu(service):
    with patch(f'{MODULE}.sys.platform', 'win32'), \
            patch(f'{MODULE}.ONNXRUNTIME_AVAILABLE', True), \
            patch(f'{MODULE}.ort') as mock_ort:
        mock_ort.InferenceSession.return_value = fake_session(['DmlExecutionProvider'])

        _get_session(service)

        assert mock_ort.InferenceSession.call_args.kwargs['providers'] == [
            'DmlExecutionProvider', 'CPUExecutionProvider'
        ]


def test_cpu_only_never_requests_an_accelerator(service):
    """cpu_only must not be second-guessed by the platform branch."""
    with patch(f'{MODULE}.sys.platform', 'darwin'), \
            patch(f'{MODULE}.ONNXRUNTIME_AVAILABLE', True), \
            patch(f'{MODULE}.ort') as mock_ort:
        mock_ort.InferenceSession.return_value = fake_session(['CPUExecutionProvider'])

        _get_session(service, cpu_only=True)

        assert mock_ort.InferenceSession.call_count == 1
        assert mock_ort.InferenceSession.call_args.kwargs['providers'] == ['CPUExecutionProvider']


# ---------------------------------------------------------------------------
# fallback
# ---------------------------------------------------------------------------

def test_falls_back_to_cpu_when_the_accelerated_session_raises(service):
    with patch(f'{MODULE}.sys.platform', 'darwin'), \
            patch(f'{MODULE}.ONNXRUNTIME_AVAILABLE', True), \
            patch(f'{MODULE}.ort') as mock_ort:
        cpu_session = fake_session(['CPUExecutionProvider'])
        mock_ort.InferenceSession.side_effect = [RuntimeError('no CoreML here'), cpu_session]

        result = _get_session(service)

        assert result is cpu_session
        assert mock_ort.InferenceSession.call_count == 2
        assert mock_ort.InferenceSession.call_args.kwargs['providers'] == ['CPUExecutionProvider']
        service.logger.warning.assert_called()
        assert 'CoreMLExecutionProvider' in service.logger.warning.call_args[0][0]


def test_raises_a_clear_error_when_even_cpu_fails(service):
    with patch(f'{MODULE}.ONNXRUNTIME_AVAILABLE', True), \
            patch(f'{MODULE}.ort') as mock_ort:
        mock_ort.InferenceSession.side_effect = RuntimeError('model is corrupt')

        with pytest.raises(RuntimeError, match='could not be loaded with any provider'):
            _get_session(service)

        service.logger.error.assert_called()


# ---------------------------------------------------------------------------
# the silent-downgrade log (the reason this file exists)
# ---------------------------------------------------------------------------

def test_warns_when_onnx_silently_downgrades_to_cpu(service):
    """ORT returns a CPU session without raising if the provider is missing."""
    with patch(f'{MODULE}.sys.platform', 'darwin'), \
            patch(f'{MODULE}.ONNXRUNTIME_AVAILABLE', True), \
            patch(f'{MODULE}.ort') as mock_ort:
        # no exception - just a session that did not get what was asked for
        mock_ort.InferenceSession.return_value = fake_session(['CPUExecutionProvider'])
        mock_ort.get_available_providers.return_value = ['CPUExecutionProvider']

        _get_session(service)

        service.logger.warning.assert_called_once()
        message = service.logger.warning.call_args[0][0]
        assert 'CoreMLExecutionProvider' in message
        assert 'not available' in message


def test_logs_the_active_providers_when_acceleration_is_used(service):
    with patch(f'{MODULE}.sys.platform', 'win32'), \
            patch(f'{MODULE}.ONNXRUNTIME_AVAILABLE', True), \
            patch(f'{MODULE}.ort') as mock_ort:
        mock_ort.InferenceSession.return_value = fake_session(
            ['DmlExecutionProvider', 'CPUExecutionProvider']
        )

        _get_session(service)

        service.logger.warning.assert_not_called()
        service.logger.info.assert_called_once()
        assert 'DmlExecutionProvider' in service.logger.info.call_args[0][0]


def test_cpu_only_run_is_logged_without_a_downgrade_warning(service):
    """Asking for CPU and getting CPU is not a downgrade."""
    with patch(f'{MODULE}.ONNXRUNTIME_AVAILABLE', True), \
            patch(f'{MODULE}.ort') as mock_ort:
        mock_ort.InferenceSession.return_value = fake_session(['CPUExecutionProvider'])

        _get_session(service, cpu_only=True)

        service.logger.warning.assert_not_called()
        service.logger.info.assert_called_once()


def test_a_session_without_a_provider_list_is_still_returned(service):
    """Diagnostics must never be the reason analysis cannot start."""
    with patch(f'{MODULE}.ONNXRUNTIME_AVAILABLE', True), \
            patch(f'{MODULE}.ort') as mock_ort:
        session = MagicMock()
        session.get_providers.side_effect = AttributeError('no such method')
        mock_ort.InferenceSession.return_value = session

        assert _get_session(service, cpu_only=True) is session


def test_session_is_cached_per_model_and_cpu_only(service):
    """_get_session should not re-create a session already built for this key."""
    with patch(f'{MODULE}.ONNXRUNTIME_AVAILABLE', True), \
            patch(f'{MODULE}.ort') as mock_ort:
        mock_ort.InferenceSession.return_value = fake_session(['CPUExecutionProvider'])

        first = _get_session(service, cpu_only=True)
        second = _get_session(service, cpu_only=True)

        assert first is second
        assert mock_ort.InferenceSession.call_count == 1
