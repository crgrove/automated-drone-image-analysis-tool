"""Compact telemetry overlay rendered at the bottom of every FlightTile.

Renders the publisher's live aircraft + gimbal state at ~4 Hz (publisher
throttle). Plan §19.3 specifies the layout and field formatting:

    LAT 30.2672  LON -97.7431  ALT 312 m MSL / 26 m AGL
    HDG 091° E   SPD 4.3 m/s   ↓0.5 m/s  BAT 82%   FLY · Normal

The widget is fed by :class:`~core.services.streaming.\
TelemetryFeedService.TelemetryFeedService` via Qt signal/slot wiring.
Null fields render as em-dashes; stale envelopes (>5 s without an
update) dim the strip and append a stale-time badge.
"""

from __future__ import annotations

import time
from typing import Optional

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget

from core.services.SettingsService import SettingsService
from core.views.flight.telemetry_hud_ui import Ui_TelemetryHud
from helpers.TranslationMixin import TranslationMixin


# A telemetry envelope older than this is shown dimmed with a "stale Xs"
# badge per plan §19.3. The publisher sends at ~4 Hz so the gap is
# unambiguous in practice.
STALENESS_THRESHOLD_SECONDS = 5.0

# Cardinal letters for the compass — pad heading text to 3 digits + letter.
_CARDINALS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW", "N")


class TelemetryHud(TranslationMixin, QWidget, Ui_TelemetryHud):
    """One HUD per :class:`FlightTile`; mirrors the publisher state."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setupUi(self)
        self._settings = SettingsService()
        self._last_envelope: Optional[dict] = None
        self._last_received_at: Optional[float] = None
        self._distance_unit = self._read_distance_unit()

        # 1 Hz staleness check — cheap; pure label updates.
        self._stale_timer = QTimer(self)
        self._stale_timer.setInterval(1000)
        self._stale_timer.timeout.connect(self._check_staleness)
        self._stale_timer.start()

        # Render a "no data yet" baseline.
        self._render(None)

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def apply_envelope(self, envelope: dict) -> None:
        """Update the HUD from a parsed telemetry envelope."""
        if not isinstance(envelope, dict):
            return
        self._last_envelope = envelope
        self._last_received_at = time.monotonic()
        # Re-read distance unit each tick in case the operator flipped
        # it in Preferences mid-session.
        self._distance_unit = self._read_distance_unit()
        self._render(envelope)
        self._clear_stale()

    @property
    def last_envelope(self) -> Optional[dict]:
        return self._last_envelope

    # ------------------------------------------------------------------
    # rendering
    # ------------------------------------------------------------------

    def _render(self, envelope: Optional[dict]) -> None:
        env = envelope or {}
        self.latLabel.setText(self.tr("LAT {value}").format(
            value=self._format_coord(env.get("aircraft_latitude"), is_lat=True)
        ))
        self.lonLabel.setText(self.tr("LON {value}").format(
            value=self._format_coord(env.get("aircraft_longitude"), is_lat=False)
        ))
        self.altLabel.setText(self._format_altitudes(
            env.get("aircraft_altitude_msl_m"),
            env.get("aircraft_altitude_agl_m"),
        ))
        self.headingLabel.setText(self._format_heading(env.get("aircraft_yaw_deg")))
        self.speedLabel.setText(self._format_speed(env.get("horizontal_speed_ms")))
        self.verticalSpeedLabel.setText(
            self._format_vertical_speed(env.get("vertical_speed_ms"))
        )
        self._render_battery(env.get("battery_percent"))
        self._render_flight_mode(env.get("is_flying"), env.get("flight_mode"))

    def _render_battery(self, percent) -> None:
        if not isinstance(percent, (int, float)):
            self.batteryChip.setText("—")
            self.batteryChip.setStyleSheet("")
            return
        value = int(percent)
        if value >= 50:
            colour = "#2ecc71"   # green
        elif value >= 20:
            colour = "#f39c12"   # amber
        else:
            colour = "#e74c3c"   # red
        self.batteryChip.setText(f"{value}%")
        self.batteryChip.setStyleSheet(
            f"QLabel#batteryChip {{ background-color: {colour}; color: black; "
            f"padding-left: 4px; padding-right: 4px; border-radius: 2px; }}"
        )

    def _render_flight_mode(self, is_flying, flight_mode) -> None:
        parts = []
        if is_flying is True:
            parts.append(self.tr("FLY"))
        mode = str(flight_mode).strip() if isinstance(flight_mode, str) else ""
        if mode:
            parts.append(mode)
        self.flightModeLabel.setText(" · ".join(parts) if parts else "—")

    # ------------------------------------------------------------------
    # staleness
    # ------------------------------------------------------------------

    def _check_staleness(self) -> None:
        if self._last_received_at is None:
            return
        age = time.monotonic() - self._last_received_at
        if age < STALENESS_THRESHOLD_SECONDS:
            self._clear_stale()
            return
        # Dim the labels and append a "stale Ns" badge.
        self.setStyleSheet(
            "QWidget { background-color: rgba(0, 0, 0, 160); color: #888; }"
            "QLabel { font-family: \"Consolas\", \"Courier New\", monospace; "
            "font-size: 11px; }"
            "QLabel#staleBadge { color: #ff8080; font-weight: bold; }"
        )
        self.staleBadge.setText(
            self.tr("stale {age}s").format(age=int(age))
        )

    def _clear_stale(self) -> None:
        self.staleBadge.setText("")
        # Restore the .ui-defined stylesheet by resetting our override.
        self.setStyleSheet("")

    # ------------------------------------------------------------------
    # field formatting helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_coord(value, *, is_lat: bool) -> str:
        if not isinstance(value, (int, float)):
            return "—"
        return f"{float(value):.6f}"

    def _format_altitudes(self, msl, agl) -> str:
        if not isinstance(msl, (int, float)) and not isinstance(agl, (int, float)):
            return self.tr("ALT —")
        if self._distance_unit == "Feet":
            msl_part = self._meters_to_feet(msl)
            agl_part = self._meters_to_feet(agl)
            suffix_msl = "ft MSL"
            suffix_agl = "ft AGL"
        else:
            msl_part = self._fmt_num(msl, 0)
            agl_part = self._fmt_num(agl, 0)
            suffix_msl = "m MSL"
            suffix_agl = "m AGL"
        return self.tr("ALT {msl} {msl_unit} / {agl} {agl_unit}").format(
            msl=msl_part, msl_unit=suffix_msl, agl=agl_part, agl_unit=suffix_agl,
        )

    def _format_heading(self, yaw_deg) -> str:
        if not isinstance(yaw_deg, (int, float)):
            return self.tr("HDG —")
        # Normalize to [0, 360).
        bearing = float(yaw_deg) % 360.0
        cardinal = _CARDINALS[int(round(bearing / 45.0)) % 8]
        return self.tr("HDG {bearing:03d}° {cardinal}").format(
            bearing=int(round(bearing)), cardinal=cardinal,
        )

    def _format_speed(self, horizontal_ms) -> str:
        if not isinstance(horizontal_ms, (int, float)):
            return self.tr("SPD —")
        # Match the altitude unit's family: ``Feet`` operators get mph
        # (the way ground-side SAR teams typically read drone speed in
        # the US); ``Meters`` keeps m/s. Without this, the HUD mixes
        # "ALT 878 ft" with "SPD 4.3 m/s" on the same strip.
        if self._distance_unit == "Feet":
            return self.tr("SPD {value} mph").format(
                value=self._fmt_num(float(horizontal_ms) * 2.23694, 1)
            )
        return self.tr("SPD {value} m/s").format(
            value=self._fmt_num(horizontal_ms, 1)
        )

    def _format_vertical_speed(self, vertical_ms) -> str:
        if not isinstance(vertical_ms, (int, float)):
            return "↕ —"
        arrow = "↑" if vertical_ms > 0 else ("↓" if vertical_ms < 0 else "•")
        # ``Feet`` → fpm (aviation-standard vertical speed in the US);
        # ``Meters`` → m/s. Matches the horizontal-speed unit family.
        if self._distance_unit == "Feet":
            fpm = abs(float(vertical_ms)) * 196.850393701
            return f"{arrow}{self._fmt_num(fpm, 0)} fpm"
        return f"{arrow}{self._fmt_num(abs(vertical_ms), 1)} m/s"

    @staticmethod
    def _fmt_num(value, places: int) -> str:
        if not isinstance(value, (int, float)):
            return "—"
        if places <= 0:
            return f"{int(round(float(value)))}"
        return f"{float(value):.{places}f}"

    @staticmethod
    def _meters_to_feet(meters) -> str:
        if not isinstance(meters, (int, float)):
            return "—"
        return f"{float(meters) * 3.28084:.0f}"

    def _read_distance_unit(self) -> str:
        unit = self._settings.get_setting("DistanceUnit", "Feet") or "Feet"
        return str(unit)
