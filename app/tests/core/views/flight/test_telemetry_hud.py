"""Tests for the telemetry HUD's altitude strip.

The HUD is the **only** altitude display in either live window — the
Flight Viewer tiles and the streaming window share this widget — so it is
the single place where confusing the three references would reach an
operator. Every test here is about keeping them apart:

* MSL is above mean sea level,
* ATO is above the takeoff point (the drone's own barometric reading),
* AGL is above the terrain beneath the aircraft.

The strip must never show ATO in the AGL slot, must render an em-dash
when no AGL exists, and must mark an AGL nothing referenced to terrain.
"""

import pytest

from core.services.telemetry.TelemetryEnrichmentService import (
    AGL_SOURCE_FLIGHT,
    AGL_SOURCE_REPORTED,
    AGL_SOURCE_TERRAIN,
    TERRAIN_AGL_KEY,
)
from core.views.flight.TelemetryHud import TelemetryHud, UNVERIFIED_AGL_MARKER


@pytest.fixture
def hud(qtbot, monkeypatch):
    """A HUD in metric, independent of the developer's own preference."""
    monkeypatch.setattr(
        "core.views.flight.TelemetryHud.TelemetryHud._read_distance_unit",
        lambda self: "Meters",
    )
    widget = TelemetryHud()
    qtbot.addWidget(widget)
    return widget


@pytest.fixture
def imperial_hud(qtbot, monkeypatch):
    monkeypatch.setattr(
        "core.views.flight.TelemetryHud.TelemetryHud._read_distance_unit",
        lambda self: "Feet",
    )
    widget = TelemetryHud()
    qtbot.addWidget(widget)
    return widget


def envelope(msl=312.0, ato=52.0, agl=None, source=None):
    env = {
        "aircraft_latitude": 30.2672,
        "aircraft_longitude": -97.7431,
        "aircraft_altitude_msl_m": msl,
        "aircraft_altitude_agl_m": ato,
    }
    if agl is not None:
        env[TERRAIN_AGL_KEY] = agl
    if source is not None:
        env["agl_source"] = source
    return env


class TestThreeReferences:
    def test_all_three_are_rendered(self, hud):
        hud.apply_envelope(envelope(agl=47.0, source=AGL_SOURCE_TERRAIN))
        assert hud.altLabel.text() == "ALT AGL 47 / ATO 52 / MSL 312 m"

    def test_the_plane_labels_come_from_formathelper(self, hud, monkeypatch):
        """The rendered text is identical either way, so this is the only
        assertion that can tell a helper-sourced label from a literal - and
        without it the next edit can quietly hardcode them back."""
        monkeypatch.setattr(
            "helpers.FormatHelper.FormatHelper.altitude_reference_abbreviation",
            staticmethod(lambda reference: f"X-{reference}"),
        )
        hud.apply_envelope(envelope(agl=47.0, source=AGL_SOURCE_TERRAIN))

        text = hud.altLabel.text()
        assert "X-terrain 47" in text
        assert "X-takeoff 52" in text
        assert "X-msl 312" in text

    def test_feet_converts_every_slot(self, imperial_hud):
        imperial_hud.apply_envelope(envelope(agl=47.0, source=AGL_SOURCE_TERRAIN))
        # 47 m = 154 ft, 52 m = 171 ft, 312 m = 1024 ft.
        assert imperial_hud.altLabel.text() == "ALT AGL 154 / ATO 171 / MSL 1024 ft"

    def test_unavailable_agl_is_an_em_dash(self, hud):
        """ATO must never be substituted into the AGL slot.

        Substituting would show a takeoff-relative number as ground
        clearance — the mistake the whole three-reference split exists to
        prevent — and there is nothing to gain from it, since ATO is
        already displayed beside it.
        """
        hud.apply_envelope(envelope(source=AGL_SOURCE_REPORTED))
        assert hud.altLabel.text() == "ALT AGL — / ATO 52 / MSL 312 m"

    def test_a_null_agl_key_is_also_an_em_dash(self, hud):
        env = envelope()
        env[TERRAIN_AGL_KEY] = None
        hud.apply_envelope(env)
        assert "AGL —" in hud.altLabel.text()

    def test_missing_msl_leaves_the_other_slots(self, hud):
        hud.apply_envelope(envelope(msl=None, agl=47.0))
        assert hud.altLabel.text() == "ALT AGL 47 / ATO 52 / MSL — m"

    def test_no_altitudes_at_all(self, hud):
        hud.apply_envelope(envelope(msl=None, ato=None))
        assert hud.altLabel.text() == "ALT —"

    def test_empty_state_before_any_envelope(self, hud):
        assert hud.altLabel.text() == "ALT —"

    def test_zero_agl_is_a_value_not_an_absence(self, hud):
        """A landed aircraft reads 0, which is not the same as unknown."""
        hud.apply_envelope(envelope(agl=0.0, source=AGL_SOURCE_TERRAIN))
        assert "AGL 0 " in hud.altLabel.text()


class TestUnverifiedAgl:
    def test_takeoff_reference_is_marked(self, hud):
        """The publisher had no terrain source, so its AGL *is* ATO."""
        hud.apply_envelope(envelope(agl=52.0, source="TAKEOFF_REFERENCE"))
        assert hud.altLabel.text().endswith(UNVERIFIED_AGL_MARKER)

    def test_an_unknown_source_is_marked(self, hud):
        hud.apply_envelope(envelope(agl=52.0, source="RADAR_ALTIMETER"))
        assert hud.altLabel.text().endswith(UNVERIFIED_AGL_MARKER)

    @pytest.mark.parametrize("source", [
        None, AGL_SOURCE_FLIGHT, "LASER", "ULTRASONIC", "TERRAIN_DEM",
        AGL_SOURCE_TERRAIN,
    ])
    def test_terrain_referenced_sources_are_not_marked(self, hud, source):
        hud.apply_envelope(envelope(agl=47.0, source=source))
        assert not hud.altLabel.text().endswith(UNVERIFIED_AGL_MARKER)

    def test_an_absent_agl_is_not_marked(self, hud):
        """The em-dash already says everything; a marker would add noise."""
        hud.apply_envelope(envelope(source="TAKEOFF_REFERENCE"))
        assert not hud.altLabel.text().endswith(UNVERIFIED_AGL_MARKER)


class TestProvenanceTooltip:
    """The full source name lives in the tooltip, not on the strip."""

    def test_names_the_desktop_dem(self, hud):
        hud.apply_envelope(envelope(agl=47.0, source=AGL_SOURCE_TERRAIN))
        assert "desktop DEM" in hud.altLabel.toolTip()

    def test_names_a_flight_measurement(self, hud):
        hud.apply_envelope(envelope(agl=47.0, source="LASER"))
        assert "laser rangefinder" in hud.altLabel.toolTip()

    def test_bare_flight_agl_is_attributed_to_flight(self, hud):
        """ADIAT Flight sends a fused AGL without naming the sensor."""
        hud.apply_envelope(envelope(agl=47.0))
        assert "ADIAT Flight" in hud.altLabel.toolTip()

    def test_unknown_source_is_shown_verbatim(self, hud):
        hud.apply_envelope(envelope(agl=47.0, source="RADAR_ALTIMETER"))
        assert "radar_altimeter" in hud.altLabel.toolTip()

    def test_no_agl_says_so(self, hud):
        hud.apply_envelope(envelope(source=AGL_SOURCE_REPORTED))
        assert "no terrain-referenced AGL" in hud.altLabel.toolTip()

    def test_every_reference_is_explained_agl_first(self, hud):
        """The tooltip reads in the same order as the strip."""
        hud.apply_envelope(envelope(agl=47.0, source=AGL_SOURCE_TERRAIN))
        tooltip = hud.altLabel.toolTip()
        for label in ("AGL", "ATO", "MSL"):
            assert label in tooltip
        assert tooltip.index("AGL") < tooltip.index("ATO") < tooltip.index("MSL")

    def test_the_tooltip_says_what_each_plane_is_for(self, hud):
        """An operator must be able to tell the pair apart from the tip."""
        hud.apply_envelope(envelope(agl=47.0, source=AGL_SOURCE_TERRAIN))
        tooltip = hud.altLabel.toolTip()
        assert "clearance" in tooltip
        assert "takeoff point" in tooltip
        assert "flat ground" in tooltip


class TestStripFits:
    def test_the_altitude_slot_fits_the_hud(self, imperial_hud):
        """Three values share the strip with five other fields.

        The HUD is 640 px wide and the altitude slot is one item in a
        horizontal layout, so a long imperial reading is the case that
        would elide. Measured against the widget's own font rather than a
        guess about character widths.
        """
        imperial_hud.apply_envelope(
            envelope(msl=3048.0, ato=1524.0, agl=1524.0, source="TAKEOFF_REFERENCE")
        )
        metrics = imperial_hud.altLabel.fontMetrics()
        width = metrics.horizontalAdvance(imperial_hud.altLabel.text())
        # Half the strip leaves room for LAT/LON on the same row.
        assert width < 320


class TestPublisherSourceKeyOnTheHud:
    """The HUD reads provenance from either key.

    ADIAT Flight names its source on ``aircraft_altitude_agl_source``;
    enrichment records its own inference under ``agl_source``. A HUD that
    only read one of them would attribute half the fixes to nobody.
    """

    def test_the_wire_key_names_the_source(self, hud):
        env = envelope(agl=47.0)
        env["aircraft_altitude_agl_source"] = "LASER"
        hud.apply_envelope(env)
        assert "laser rangefinder" in hud.altLabel.toolTip()
        assert not hud.altLabel.text().endswith(UNVERIFIED_AGL_MARKER)

    def test_takeoff_reference_from_the_wire_is_marked(self, hud):
        env = envelope(agl=52.0)
        env["aircraft_altitude_agl_source"] = "TAKEOFF_REFERENCE"
        hud.apply_envelope(env)
        assert hud.altLabel.text().endswith(UNVERIFIED_AGL_MARKER)

    def test_a_null_agl_says_flight_found_no_terrain_source(self, hud):
        """Distinct from a feed that cannot report AGL at all.

        Flight sends TAKEOFF_REFERENCE unconditionally, so this state is
        "the aircraft looked and found nothing" - worth telling the
        operator, since desktop enrichment is still trying.
        """
        env = envelope()
        env["aircraft_altitude_agl_terrain_m"] = None
        env["aircraft_altitude_agl_source"] = "TAKEOFF_REFERENCE"
        hud.apply_envelope(env)

        assert "AGL —" in hud.altLabel.text()
        assert "found no terrain source" in hud.altLabel.toolTip()

    def test_an_older_publisher_gets_the_generic_wording(self, hud):
        env = envelope()
        env["aircraft_altitude_agl_terrain_m"] = None
        hud.apply_envelope(env)
        assert "no terrain-referenced AGL" in hud.altLabel.toolTip()
