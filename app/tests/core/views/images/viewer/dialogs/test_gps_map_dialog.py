"""Tests for GPSMapDialog overlay-control gating."""

import pytest
from PySide6.QtWidgets import QApplication

from core.views.images.viewer.dialogs.GPSMapDialog import GPSMapDialog


@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def dialog(app):
    dlg = GPSMapDialog(None, [], None, offline_only=True)
    yield dlg
    dlg.close()
    dlg.deleteLater()


def _mode_keys(dlg):
    return [dlg.pod_mode_combo.itemData(i) for i in range(dlg.pod_mode_combo.count())]


def test_mode_combo_offers_canopy(dialog):
    assert _mode_keys(dialog) == ["pod", "looks", "canopy"]


def test_canopy_only_enables_toggle_and_hops_selection(dialog):
    model = dialog.pod_mode_combo.model()
    keys = _mode_keys(dialog)

    dialog.set_overlay_availability(False, True)
    assert dialog.pod_toggle_btn.isEnabled()
    assert model.item(keys.index("canopy")).isEnabled()
    assert not model.item(keys.index("pod")).isEnabled()
    assert not model.item(keys.index("looks")).isEnabled()
    # The unavailable default ('pod') hops to the only enabled mode.
    assert dialog.pod_mode_combo.currentData() == "canopy"


def test_pod_only_disables_canopy_and_hops_back(dialog):
    model = dialog.pod_mode_combo.model()
    keys = _mode_keys(dialog)

    dialog.set_overlay_availability(False, True)   # selection lands on canopy
    dialog.set_overlay_availability(True, False)
    assert model.item(keys.index("pod")).isEnabled()
    assert not model.item(keys.index("canopy")).isEnabled()
    assert dialog.pod_mode_combo.currentData() == "pod"


def test_nothing_available_disables_and_unchecks(dialog):
    dialog.set_overlay_availability(True, True)
    dialog.pod_toggle_btn.setChecked(True)
    dialog.set_overlay_availability(False, False)
    assert not dialog.pod_toggle_btn.isEnabled()
    assert not dialog.pod_toggle_btn.isChecked()


def test_set_pod_available_keeps_canopy_state(dialog):
    dialog.set_overlay_availability(False, True)
    dialog.set_pod_available(True)  # legacy entry point must not drop canopy
    model = dialog.pod_mode_combo.model()
    keys = _mode_keys(dialog)
    assert model.item(keys.index("pod")).isEnabled()
    assert model.item(keys.index("canopy")).isEnabled()


# ---------------------------------------------------------------------------
# activate_pod_overlay: post-Calculate-POD control state (regression)
# ---------------------------------------------------------------------------


def test_activate_pod_overlay_checks_button_and_enables_dropdown(dialog, qtbot):
    """After Calculate POD, activating the overlay must leave the button
    checked and the dropdown/slider enabled — not just paint the map.

    Regression: the overlay appeared while the POD Overlay button stayed
    unchecked and the mode dropdown stayed disabled (grayed)."""
    with qtbot.waitSignal(dialog.pod_display_changed, timeout=1000) as blocker:
        dialog.activate_pod_overlay('pod')

    assert dialog.pod_toggle_btn.isChecked() is True
    assert dialog.pod_toggle_btn.isEnabled() is True
    assert dialog.pod_mode_combo.isEnabled() is True
    assert dialog.pod_opacity_slider.isEnabled() is True
    assert dialog.pod_mode_combo.currentData() == "pod"
    # The single emission carries the active mode so the controller paints it.
    enabled, mode_key, _opacity = blocker.args
    assert enabled is True and mode_key == "pod"


def test_activate_pod_overlay_selects_requested_mode(dialog, qtbot):
    with qtbot.waitSignal(dialog.pod_display_changed, timeout=1000) as blocker:
        dialog.activate_pod_overlay('looks')
    assert dialog.pod_mode_combo.currentData() == "looks"
    assert blocker.args[1] == "looks"


def test_activate_pod_overlay_emits_once(dialog, qtbot):
    """Selecting the mode then checking the toggle must paint exactly once
    (no mid-way emit from the combo change)."""
    emissions = []
    dialog.pod_display_changed.connect(lambda *a: emissions.append(a))
    dialog.activate_pod_overlay('looks')
    assert len(emissions) == 1


def test_activate_pod_overlay_when_already_on_repaints(dialog, qtbot):
    """Re-activating an already-on overlay (e.g. a second Calculate POD) still
    emits so the map repaints, even though the toggle doesn't change state."""
    dialog.activate_pod_overlay('pod')
    emissions = []
    dialog.pod_display_changed.connect(lambda *a: emissions.append(a))
    dialog.activate_pod_overlay('looks')
    assert emissions and emissions[-1][1] == "looks"
    assert dialog.pod_toggle_btn.isChecked() is True


# ---------------------------------------------------------------------------
# pod_display_changed(enabled, mode_key, opacity) signal emission (P2)
# ---------------------------------------------------------------------------


def test_pod_toggle_emits_pod_display_changed(dialog, qtbot):
    """Checking the POD button emits pod_display_changed with the current
    combo mode key and slider opacity value."""
    dialog.set_overlay_availability(True, True)  # all modes available, toggle enabled
    # Pick a known, non-default mode + opacity so we can assert they drive the payload.
    dialog.pod_mode_combo.setCurrentIndex(_mode_keys(dialog).index("looks"))
    dialog.pod_opacity_slider.setValue(42)

    with qtbot.waitSignal(dialog.pod_display_changed, timeout=1000) as blocker:
        dialog.pod_toggle_btn.setChecked(True)

    enabled, mode_key, opacity = blocker.args
    assert enabled is True
    assert mode_key == "looks"
    assert opacity == 42


def test_pod_untoggle_emits_disabled(dialog, qtbot):
    """Unchecking the POD button emits with enabled=False."""
    dialog.set_overlay_availability(True, True)
    dialog.pod_toggle_btn.setChecked(True)  # turn on first

    with qtbot.waitSignal(dialog.pod_display_changed, timeout=1000) as blocker:
        dialog.pod_toggle_btn.setChecked(False)

    enabled, _mode_key, _opacity = blocker.args
    assert enabled is False


def test_mode_combo_change_drives_emitted_mode(dialog, qtbot):
    """Changing the combo selection re-emits pod_display_changed with the new
    stable mode key (itemData), not the localized label."""
    dialog.set_overlay_availability(True, True)
    dialog.pod_toggle_btn.setChecked(True)
    keys = _mode_keys(dialog)

    with qtbot.waitSignal(dialog.pod_display_changed, timeout=1000) as blocker:
        dialog.pod_mode_combo.setCurrentIndex(keys.index("canopy"))

    enabled, mode_key, _opacity = blocker.args
    assert enabled is True
    assert mode_key == "canopy"


def test_slider_value_drives_emitted_opacity(dialog, qtbot):
    """The opacity slider value is folded into the payload of the next
    enable/mode emission."""
    dialog.set_overlay_availability(True, True)
    dialog.pod_opacity_slider.setValue(15)

    with qtbot.waitSignal(dialog.pod_display_changed, timeout=1000) as blocker:
        dialog.pod_toggle_btn.setChecked(True)

    _enabled, _mode_key, opacity = blocker.args
    assert opacity == 15


def test_slider_move_does_not_emit_pod_display_changed(dialog):
    """Opacity is pure view state: moving the slider updates the map view
    directly and MUST NOT emit pod_display_changed (avoids recompute churn)."""
    dialog.set_overlay_availability(True, True)
    dialog.pod_toggle_btn.setChecked(True)

    received = []
    dialog.pod_display_changed.connect(lambda *args: received.append(args))
    dialog.pod_opacity_slider.setValue(dialog.pod_opacity_slider.value() + 5)

    assert received == []


def test_toggle_gates_combo_and_slider_enabled_state(dialog):
    """The POD toggle gates the mode combo and opacity slider: they are only
    interactive while the overlay is enabled."""
    dialog.set_overlay_availability(True, True)
    assert not dialog.pod_mode_combo.isEnabled()
    assert not dialog.pod_opacity_slider.isEnabled()

    dialog.pod_toggle_btn.setChecked(True)
    assert dialog.pod_mode_combo.isEnabled()
    assert dialog.pod_opacity_slider.isEnabled()

    dialog.pod_toggle_btn.setChecked(False)
    assert not dialog.pod_mode_combo.isEnabled()
    assert not dialog.pod_opacity_slider.isEnabled()


# ---------------------------------------------------------------------------
# Canopy tile-download button (Offline Only gating + request signal)
# ---------------------------------------------------------------------------


def test_canopy_fetch_button_disabled_in_offline_mode(dialog):
    """The `dialog` fixture is offline_only=True, so downloading is disabled."""
    assert not dialog.canopy_fetch_btn.isEnabled()


def test_canopy_fetch_button_enabled_when_online(app):
    dlg = GPSMapDialog(None, [], None, offline_only=False)
    try:
        assert dlg.canopy_fetch_btn.isEnabled()
    finally:
        dlg.close()
        dlg.deleteLater()


def test_set_offline_mode_toggles_canopy_fetch_button(app):
    """Flipping Offline Only must enable/disable the download button live."""
    dlg = GPSMapDialog(None, [], None, offline_only=False)
    try:
        assert dlg.canopy_fetch_btn.isEnabled()
        dlg.set_offline_mode(True)
        assert not dlg.canopy_fetch_btn.isEnabled()
        dlg.set_offline_mode(False)
        assert dlg.canopy_fetch_btn.isEnabled()
    finally:
        dlg.close()
        dlg.deleteLater()


def test_canopy_fetch_button_emits_request_signal(app, qtbot):
    """Clicking the button emits canopy_download_requested (controller wires it)."""
    dlg = GPSMapDialog(None, [], None, offline_only=False)
    try:
        with qtbot.waitSignal(dlg.canopy_download_requested, timeout=1000):
            dlg.canopy_fetch_btn.click()
    finally:
        dlg.close()
        dlg.deleteLater()


def test_pod_calculate_button_emits_request_signal(app, qtbot):
    """The Calculate POD button lets the user compute coverage without leaving
    the map; clicking emits pod_calculate_requested (controller wires it)."""
    dlg = GPSMapDialog(None, [], None, offline_only=False)
    try:
        assert dlg.pod_calc_btn.isEnabled()
        with qtbot.waitSignal(dlg.pod_calculate_requested, timeout=1000):
            dlg.pod_calc_btn.click()
    finally:
        dlg.close()
        dlg.deleteLater()


def test_pod_calculate_button_enabled_even_offline(dialog):
    """POD computes from local data (images + registered tiles), so the button
    stays enabled in Offline Only mode (the `dialog` fixture is offline)."""
    assert dialog.pod_calc_btn.isEnabled()
