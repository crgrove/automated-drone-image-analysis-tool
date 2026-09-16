"""The EDSR model download, and the preference it used to ignore.

``UpscaleDialog`` fetches OpenCV super-resolution weights from GitHub the
first time an operator picks AI upscaling. That fetch ran regardless of
Offline Only — the one gap in this dialog, since everything else it does
is local pixel work.

Refusing costs quality, not the feature: both call sites already fall
back to Lanczos when no model is available, so the offline path lands on
a code path that was already exercised.
"""

import numpy as np
import pytest

from core.views.images.viewer.dialogs.UpscaleDialog import UpscaleDialog


class _StubSettings:
    def __init__(self, offline_only):
        self._offline_only = offline_only

    def get_bool_setting(self, name, default_value=False):
        if name == "OfflineOnly":
            return self._offline_only
        return default_value


@pytest.fixture
def dialog(qtbot):
    image = np.zeros((16, 16, 3), dtype=np.uint8)
    dlg = UpscaleDialog(image_array=image)
    qtbot.addWidget(dlg)
    yield dlg


def test_model_download_is_refused_in_offline_only_mode(dialog, monkeypatch):
    """No request is made, and the caller gets the None it already handles."""
    dialog.settings_service = _StubSettings(offline_only=True)
    monkeypatch.setattr(dialog, "_notify_offline_once", lambda: None)

    def fail(*args, **kwargs):
        raise AssertionError("urlretrieve called while Offline Only was enabled")

    import urllib.request

    monkeypatch.setattr(urllib.request, "urlretrieve", fail)

    assert dialog._download_model("EDSR_x2") is None


def test_an_already_downloaded_model_is_still_used_offline(dialog, monkeypatch, tmp_path):
    """A cached model is local data. Offline Only withholds the fetch, not
    the capability — an operator who downloaded it before going to the
    field keeps AI upscaling."""
    dialog.settings_service = _StubSettings(offline_only=True)
    cached = tmp_path / "EDSR_x2.pb"
    cached.write_bytes(b"not-a-real-model")
    monkeypatch.setattr(dialog, "_get_models_dir", lambda: tmp_path)

    notified = []
    monkeypatch.setattr(dialog, "_notify_offline_once", lambda: notified.append(1))

    assert dialog._download_model("EDSR_x2") == cached
    assert notified == [], "a cached hit must not warn about being offline"


def test_the_operator_is_told_once_not_once_per_upscale(dialog, monkeypatch):
    """The Lanczos fallback is silent and repeats on every upscale step, so
    without the latch the operator is either never told or nagged."""
    dialog.settings_service = _StubSettings(offline_only=True)
    shown = []
    monkeypatch.setattr(
        "PySide6.QtWidgets.QMessageBox.information",
        lambda *args, **kwargs: shown.append(args),
    )

    dialog._notify_offline_once()
    dialog._notify_offline_once()
    dialog._notify_offline_once()

    assert len(shown) == 1


def test_the_notice_names_the_setting_and_the_fallback(dialog, monkeypatch):
    shown = []
    monkeypatch.setattr(
        "PySide6.QtWidgets.QMessageBox.information",
        lambda *args, **kwargs: shown.append(args),
    )

    dialog._notify_offline_once()

    body = " ".join(str(a) for a in shown[0])
    assert "Offline Only" in body
    assert "Lanczos" in body


def test_download_proceeds_when_offline_only_is_off(dialog, monkeypatch, tmp_path):
    """The gate must not break the normal first-run download."""
    dialog.settings_service = _StubSettings(offline_only=False)
    monkeypatch.setattr(dialog, "_get_models_dir", lambda: tmp_path)

    calls = []

    def fake_urlretrieve(url, filename, reporthook=None):
        calls.append(url)
        with open(filename, "wb") as fp:
            fp.write(b"model")

    import urllib.request

    monkeypatch.setattr(urllib.request, "urlretrieve", fake_urlretrieve)

    result = dialog._download_model("EDSR_x2")

    assert result == tmp_path / "EDSR_x2.pb"
    assert len(calls) == 1
    assert calls[0].startswith("https://")


def test_offline_check_defaults_to_online_when_settings_fail(dialog):
    """A settings failure must not silently disable AI upscaling."""

    class Boom:
        def get_bool_setting(self, name, default_value=False):
            raise RuntimeError("settings unavailable")

    dialog.settings_service = Boom()

    assert dialog._is_offline_only() is False
