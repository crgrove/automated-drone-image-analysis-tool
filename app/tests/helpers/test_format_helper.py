"""Tests for FormatHelper."""

import pytest

from helpers.FormatHelper import FormatHelper


def test_format_duration_seconds():
    """Durations under a minute show only seconds."""
    assert FormatHelper.format_duration(0) == '0s'
    assert FormatHelper.format_duration(45) == '45s'
    assert FormatHelper.format_duration(59.4) == '59s'


def test_format_duration_minutes():
    """Durations under an hour show minutes and seconds."""
    assert FormatHelper.format_duration(60) == '1m 0s'
    assert FormatHelper.format_duration(312) == '5m 12s'


def test_format_duration_hours():
    """Durations of an hour or more show hours, minutes and seconds."""
    assert FormatHelper.format_duration(3600) == '1h 0m 0s'
    assert FormatHelper.format_duration(5025) == '1h 23m 45s'


def test_format_duration_negative_is_zero():
    """Negative durations are clamped to zero."""
    assert FormatHelper.format_duration(-10) == '0s'


def test_format_megabytes_two_decimal_places():
    """Byte counts render as megabytes with exactly two decimals."""
    assert FormatHelper.format_megabytes(0) == '0.00'
    assert FormatHelper.format_megabytes(1024 * 1024) == '1.00'
    # 32,768,000 bytes / 1,048,576 == 31.25 MB
    assert FormatHelper.format_megabytes(32768000) == '31.25'
    # 403,572,640 bytes (the value from the download dialog) ~= 384.87 MB
    assert FormatHelper.format_megabytes(403572640) == '384.88'


def test_format_megabytes_negative_is_zero():
    """Negative byte counts are clamped to zero."""
    assert FormatHelper.format_megabytes(-500) == '0.00'


class TestAltitudeReferenceLabels:
    """ATO and AGL must never be labelled as each other.

    The two are equal over flat ground and differ by the whole terrain
    change everywhere else, so a wrong label reads as correct on the bench
    and misleads over the ridge a search team is actually working.
    """

    def test_takeoff_is_abbreviated_ato(self):
        assert FormatHelper.altitude_reference_abbreviation(
            FormatHelper.ALTITUDE_REFERENCE_TAKEOFF) == 'ATO'

    def test_terrain_is_abbreviated_agl(self):
        assert FormatHelper.altitude_reference_abbreviation(
            FormatHelper.ALTITUDE_REFERENCE_TERRAIN) == 'AGL'

    def test_an_operator_entered_height_is_agl(self):
        """The operator is asked for height above the ground being flown over."""
        assert FormatHelper.altitude_reference_abbreviation(
            FormatHelper.ALTITUDE_REFERENCE_MANUAL) == 'AGL'

    def test_takeoff_phrase_names_the_plane(self):
        assert FormatHelper.altitude_reference_phrase(
            FormatHelper.ALTITUDE_REFERENCE_TAKEOFF
        ) == 'ATO (above the takeoff point)'

    def test_terrain_phrase_names_the_plane(self):
        assert FormatHelper.altitude_reference_phrase(
            FormatHelper.ALTITUDE_REFERENCE_TERRAIN
        ) == 'AGL (above the terrain)'

    def test_manual_phrase_says_who_entered_it(self):
        assert FormatHelper.altitude_reference_phrase(
            FormatHelper.ALTITUDE_REFERENCE_MANUAL
        ) == 'AGL (operator-entered)'

    def test_sea_level_is_abbreviated_msl(self):
        """The third plane. Before it had a token of its own, a caller
        asking for a sea-level label fell through to the ATO default and
        got 'ATO' - the label collision this vocabulary exists to stop."""
        assert FormatHelper.altitude_reference_abbreviation(
            FormatHelper.ALTITUDE_REFERENCE_MSL) == 'MSL'

    def test_sea_level_phrase_names_the_plane(self):
        assert FormatHelper.altitude_reference_phrase(
            FormatHelper.ALTITUDE_REFERENCE_MSL
        ) == 'MSL (above mean sea level)'

    def test_the_three_planes_never_share_a_label(self):
        """CLAUDE.md 2.11: ATO, AGL and MSL must not share a label."""
        references = (FormatHelper.ALTITUDE_REFERENCE_TAKEOFF,
                      FormatHelper.ALTITUDE_REFERENCE_TERRAIN,
                      FormatHelper.ALTITUDE_REFERENCE_MSL)
        abbreviations = [FormatHelper.altitude_reference_abbreviation(r)
                         for r in references]
        phrases = [FormatHelper.altitude_reference_phrase(r)
                   for r in references]
        assert abbreviations == ['ATO', 'AGL', 'MSL']
        assert len(set(abbreviations)) == 3
        assert len(set(phrases)) == 3

    @pytest.mark.parametrize("junk", [None, '', 'AGL', 'nonsense', 0,
                                      'MSL', 'sea_level', 'asl'])
    def test_unknown_references_fall_back_to_takeoff(self, junk):
        """An unmarked RelativeAltitude is takeoff-relative; assume the least.

        Guessing AGL would present a takeoff-relative number as ground
        clearance, which is the one direction this label must never err in.
        """
        assert FormatHelper.altitude_reference_abbreviation(junk) == 'ATO'
        assert 'takeoff' in FormatHelper.altitude_reference_phrase(junk)


class TestAltitudeRendering:
    """One renderer per output shape; no site formats altitudes itself."""

    def _readings(self, **kwargs):
        from core.services.image.ImageService import AltitudeReadings
        return AltitudeReadings(**kwargs)

    def test_inline_shows_one_plane(self):
        readings = self._readings(
            value=171.0, unit='ft',
            reference=FormatHelper.ALTITUDE_REFERENCE_TAKEOFF)
        assert FormatHelper.altitude_inline(readings) == "171.0 ft ATO"

    def test_inline_leads_with_agl(self):
        """AGL is what clearance and image scale depend on; it reads first."""
        readings = self._readings(
            value=171.0, unit='ft', terrain_agl=141.2,
            reference=FormatHelper.ALTITUDE_REFERENCE_TAKEOFF)
        assert FormatHelper.altitude_inline(readings) == "141.2 ft AGL · 171.0 ft ATO"

    def test_inline_is_none_without_an_altitude(self):
        assert FormatHelper.altitude_inline(self._readings(value=None)) is None
        assert FormatHelper.altitude_inline(None) is None

    def test_lines_spell_the_plane_out(self):
        readings = self._readings(
            value=171.0, unit='ft',
            reference=FormatHelper.ALTITUDE_REFERENCE_TAKEOFF)
        assert FormatHelper.altitude_lines(readings) == [
            "Altitude: 171.0 ft ATO (above the takeoff point)"]

    def test_lines_carry_both_planes_agl_first(self):
        readings = self._readings(
            value=171.0, unit='ft', terrain_agl=141.2,
            reference=FormatHelper.ALTITUDE_REFERENCE_TAKEOFF)
        assert FormatHelper.altitude_lines(readings) == [
            "Altitude: 141.2 ft AGL (above the terrain, from DEM)",
            "Altitude: 171.0 ft ATO (above the takeoff point)",
        ]

    def test_the_shared_tooltip_explains_the_pair(self):
        """One string, so every surface teaches the same distinction."""
        tip = FormatHelper.ALTITUDE_TOOLTIP
        assert tip.index("AGL") < tip.index("ATO")
        assert "clearance" in tip
        assert "takeoff point" in tip
        assert "flat ground" in tip

    def test_lines_are_empty_without_an_altitude(self):
        assert FormatHelper.altitude_lines(self._readings(value=None)) == []
        assert FormatHelper.altitude_lines(None) == []

    def test_zero_is_a_value_not_an_absence(self):
        """A landed aircraft reads 0; that is not "no altitude"."""
        readings = self._readings(value=0.0, unit='ft')
        assert FormatHelper.altitude_inline(readings) == "0.0 ft ATO"


class TestElevationFormatting:
    """Elevations follow the same DistanceUnit preference as altitudes.

    Showing one in metres beside the other in feet is the mismatch that
    makes an operator distrust both readings - which is exactly what the
    coordinate popup did while the status bar read feet.
    """

    def test_feet_preference_converts(self):
        # 306.7 m is 1006 ft.
        assert FormatHelper.format_elevation(306.7, 'ft') == '1006 ft'

    def test_metres_preference_keeps_metres(self):
        assert FormatHelper.format_elevation(306.7, 'm') == '306.7 m'

    def test_both_spellings_of_the_preference_work(self):
        """The store says 'Feet'; the viewer says 'ft'. Both mean feet."""
        assert FormatHelper.format_elevation(306.7, 'Feet') == '1006 ft'
        assert FormatHelper.format_elevation(306.7, 'Meters') == '306.7 m'

    def test_feet_default_to_whole_units(self):
        """A tenth of a foot is far below DEM accuracy."""
        assert FormatHelper.format_elevation(100.0, 'ft') == '328 ft'

    def test_places_can_be_overridden(self):
        assert FormatHelper.format_elevation(306.7, 'ft', places=1) == '1006.2 ft'
        assert FormatHelper.format_elevation(38.0, 'm', places=0) == '38 m'

    @pytest.mark.parametrize("junk", [None, '', 'abc', object()])
    def test_junk_has_no_elevation_to_show(self, junk):
        assert FormatHelper.format_elevation(junk, 'ft') is None

    def test_zero_is_a_value_not_an_absence(self):
        """Sea level is a real elevation."""
        assert FormatHelper.format_elevation(0.0, 'm') == '0.0 m'

    def test_an_unknown_preference_falls_back_to_metres(self):
        """The DEM's own unit: never silently reinterpret the number."""
        assert FormatHelper.format_elevation(306.7, 'furlongs') == '306.7 m'

    @pytest.mark.parametrize("value,expected", [
        ('ft', True), ('Feet', True), ('FT', True), (' feet ', True),
        ('m', False), ('Meters', False), (None, False), ('', False),
    ])
    def test_prefers_feet_accepts_both_spellings(self, value, expected):
        assert FormatHelper.prefers_feet(value) is expected
