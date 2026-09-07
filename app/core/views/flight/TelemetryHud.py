"""Compact telemetry overlay rendered at the bottom of every FlightTile.

Renders the publisher's live aircraft + gimbal state at ~4 Hz (publisher
throttle). Plan §19.3 specifies the layout and field formatting:

    LAT 30.2672  LON -97.7431  ALT AGL 21 / ATO 26 / MSL 312 m
    HDG 091° E   SPD 4.3 m/s   ↓0.5 m/s  BAT 82%   FLY · Normal

All three altitude references are shown because they are different
numbers: MSL is above sea level, ATO is above the takeoff point, AGL is
above the terrain beneath the aircraft. An AGL slot rendered as an
em-dash means no terrain-referenced value exists — never that the
aircraft is on the ground — and a trailing ``*`` marks an AGL nothing
referenced to terrain. The widget tooltip names where the AGL came from.

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
from helpers.FormatHelper import FormatHelper
from core.services.telemetry.TelemetryEnrichmentService import (
    AGL_SOURCE_FLIGHT,
    AGL_SOURCE_LASER,
    AGL_SOURCE_TAKEOFF_REFERENCE,
    AGL_SOURCE_TERRAIN,
    AGL_SOURCE_TERRAIN_DEM,
    AGL_SOURCE_ULTRASONIC,
    TERRAIN_AGL_KEY,
    TRUSTED_AGL_SOURCES,
    normalise_agl_source,
    publisher_agl_source,
)
from core.views.flight.telemetry_hud_ui import Ui_TelemetryHud
from helpers.TranslationMixin import TranslationMixin


# A telemetry envelope older than this is shown dimmed with a "stale Xs"
# badge per plan §19.3. The publisher sends at ~4 Hz so the gap is
# unambiguous in practice.
STALENESS_THRESHOLD_SECONDS = 5.0

# Appended to an AGL nothing referenced to terrain — the same marker
# ADIAT Flight's HUD uses for the case.
UNVERIFIED_AGL_MARKER = "*"

# Sources that genuinely measured height above terrain. Anything else
# beside an AGL value earns the marker above.
_TERRAIN_REFERENCED_SOURCES = TRUSTED_AGL_SOURCES | {AGL_SOURCE_TERRAIN}


def _abbrev(reference) -> str:
    """Short plane label, from the one helper that owns the vocabulary."""
    return FormatHelper.altitude_reference_abbreviation(reference)


def _is_terrain_referenced(agl_source) -> bool:
    """True when an AGL value actually measured height above terrain.

    ADIAT Flight publishes its AGL with no source name and omits the
    value entirely when no terrain source backed it, so a bare AGL is
    terrain-referenced by construction.
    """
    source = normalise_agl_source(agl_source)
    if source is None:
        return True
    return source in _TERRAIN_REFERENCED_SOURCES


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

        # Staleness only means something for a live feed. Video playback
        # legitimately stops producing telemetry while paused, and dimming
        # the HUD with "stale 12s" there tells the operator the feed has
        # dropped when nothing is wrong. Callers driving the HUD from a
        # file switch this off via :meth:`set_staleness_tracking`.
        self._staleness_enabled = True
        # The .ui's own sheet, carrying the translucent backing and the
        # monospace label rules. Stale/clear COMPOSE against this rather
        # than replacing it - blanking it stripped the background and left
        # unreadable text over the video.
        self._base_stylesheet = self.styleSheet()

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
        agl = env.get(TERRAIN_AGL_KEY)
        # Either provenance key: ADIAT Flight names its source on the wire,
        # enrichment records its own under the internal name.
        agl_source = publisher_agl_source(env)
        self.altLabel.setText(self._format_altitudes(
            env.get("aircraft_altitude_msl_m"),
            env.get("aircraft_altitude_agl_m"),
            agl,
            agl_source,
        ))
        self.altLabel.setToolTip(self._altitude_tooltip(agl_source, agl))
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

    #: Mode strings the publisher sends when it does not know the mode.
    #: Printing them verbatim put the word "Unknown" on the HUD next to the
    #: battery chip, where it read as a battery reading rather than as "the
    #: aircraft did not report a flight mode". An em dash says that, and
    #: says it the same way every other absent field does.
    _PLACEHOLDER_MODES = frozenset({"unknown", "none", "null", "n/a", "na", "-", "--"})

    def _render_flight_mode(self, is_flying, flight_mode) -> None:
        parts = []
        if is_flying is True:
            parts.append(self.tr("FLY"))
        mode = str(flight_mode).strip() if isinstance(flight_mode, str) else ""
        if mode and mode.lower() not in self._PLACEHOLDER_MODES:
            parts.append(mode)
        self.flightModeLabel.setText(" · ".join(parts) if parts else "—")

    # ------------------------------------------------------------------
    # staleness
    # ------------------------------------------------------------------

    def set_staleness_tracking(self, enabled: bool) -> None:
        """Enable/disable the "stale Ns" badge.

        Disabled for file playback, where a pause is not a dropped feed.
        """
        self._staleness_enabled = bool(enabled)
        if not self._staleness_enabled:
            self._clear_stale()

    def _check_staleness(self) -> None:
        if not self._staleness_enabled:
            return
        if self._last_received_at is None:
            return
        age = time.monotonic() - self._last_received_at
        if age < STALENESS_THRESHOLD_SECONDS:
            self._clear_stale()
            return
        # Dim the labels and append a "stale Ns" badge.
        self.setStyleSheet(
            self._base_stylesheet
            + "\nQWidget { background-color: rgba(0, 0, 0, 190); color: #9a9a9a; }"
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
        self.setStyleSheet(self._base_stylesheet)

    # ------------------------------------------------------------------
    # field formatting helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_coord(value, *, is_lat: bool) -> str:
        if not isinstance(value, (int, float)):
            return "—"
        return f"{float(value):.6f}"

    def _format_altitudes(self, msl, ato, agl, agl_source=None) -> str:
        """Render all three altitude references on one line.

        The three are different numbers: MSL is above sea level, ATO is
        above the *takeoff point* (the drone's own barometric figure) and
        AGL is above the terrain beneath the aircraft. ATO and AGL agree
        exactly on flat ground and diverge with relief, so showing either
        one labelled as the other is a mistake that passes every bench
        test and appears only in the field — which is why all three are
        shown, and why an unavailable AGL renders as an em-dash instead of
        borrowing the ATO reading.

        The unit is written once, at the end: three copies of "ft" do not
        fit beside LAT/LON/HDG/SPD on a 640 px strip.
        """
        # AGL leads: it is the number that describes clearance over the
        # ground being flown, so it reads first. ATO is the drone's own
        # reported figure, MSL the sea-level reference.
        values = (agl, ato, msl)
        if not any(isinstance(value, (int, float)) for value in values):
            return self.tr("ALT —")
        if self._distance_unit == "Feet":
            parts = [self._meters_to_feet(value) for value in values]
            unit = "ft"
        else:
            parts = [self._fmt_num(value, 0) for value in values]
            unit = "m"
        # The three plane names come from FormatHelper so a value's
        # reference travels with it (CLAUDE.md 2.11) and one place decides
        # how each plane is spelled. They are injected as .format()
        # parameters rather than returned as the whole sentence, because
        # FormatHelper returns untranslated English by design - the
        # sentence has to stay inside tr() to reach the catalog.
        text = self.tr("ALT {agl_label} {agl} / {ato_label} {ato} "
                       "/ {msl_label} {msl} {unit}").format(
            agl_label=_abbrev(FormatHelper.ALTITUDE_REFERENCE_TERRAIN),
            ato_label=_abbrev(FormatHelper.ALTITUDE_REFERENCE_TAKEOFF),
            msl_label=_abbrev(FormatHelper.ALTITUDE_REFERENCE_MSL),
            agl=parts[0], ato=parts[1], msl=parts[2], unit=unit,
        )
        # An "AGL" nothing referenced to terrain is really an ATO reading.
        # Mark it rather than letting it read as ground clearance — the
        # same convention ADIAT Flight's own HUD uses. Plain ASCII: the
        # HUD renders in Consolas/Courier New, which lack most symbol
        # glyphs.
        if isinstance(agl, (int, float)) and not _is_terrain_referenced(agl_source):
            text = f"{text}{UNVERIFIED_AGL_MARKER}"
        return text

    def _altitude_tooltip(self, agl_source, agl) -> str:
        """Spell out the three references, and name the AGL's source.

        The full source name lives here rather than inline: three values
        already fill the altitude slot, and the operator needs the name
        when interpreting a reading, not on every glance.
        """
        if not isinstance(agl, (int, float)):
            if normalise_agl_source(agl_source) == AGL_SOURCE_TAKEOFF_REFERENCE:
                # The publisher looked and found no terrain source. Worth
                # saying: it separates "nobody could measure this" from
                # "this feed cannot report it", and it is the reason
                # enrichment is still trying.
                origin = self.tr(
                    "no AGL yet - ADIAT Flight found no terrain source here"
                )
            else:
                origin = self.tr("no terrain-referenced AGL available")
        else:
            origin = self.tr("AGL source: {origin}").format(
                origin=self._agl_source_label(agl_source)
            )
        return "\n".join([
            self.tr("AGL — above the terrain beneath the aircraft; what "
                    "clearance and image scale depend on"),
            self.tr("ATO — above the takeoff point (the drone's own "
                    "reading); equal to AGL only over flat ground"),
            self.tr("MSL — above mean sea level"),
            origin,
        ])

    def _agl_source_label(self, agl_source) -> str:
        """Name an AGL provenance value for the operator.

        An unrecognised source is shown verbatim rather than hidden: a
        name a newer ADIAT Flight build invented is still better
        provenance than none.
        """
        source = normalise_agl_source(agl_source)
        if source is None or source == AGL_SOURCE_FLIGHT:
            # ADIAT Flight sends its fused AGL without naming the sensor.
            return self.tr("ADIAT Flight (fused)")
        if source == AGL_SOURCE_LASER:
            return self.tr("laser rangefinder (ADIAT Flight)")
        if source == AGL_SOURCE_ULTRASONIC:
            return self.tr("downward sensor (ADIAT Flight)")
        if source == AGL_SOURCE_TERRAIN_DEM:
            return self.tr("terrain DEM (ADIAT Flight)")
        if source == AGL_SOURCE_TERRAIN:
            return self.tr("desktop DEM")
        if source == AGL_SOURCE_TAKEOFF_REFERENCE:
            return self.tr("no terrain source — this is the takeoff-relative reading")
        return source

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
