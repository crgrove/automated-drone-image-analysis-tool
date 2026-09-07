"""Tests for the DJI SRT telemetry parser.

The parser has to handle two structurally different layouts that both
appear in the field, plus DJI's multi-pair brackets. Both shapes are
pinned here because the previous implementation silently produced zero
samples for the embedded variant and dropped altitude for the
``rel_alt``/``abs_alt`` pair.
"""

from datetime import datetime

import pytest

from core.services.telemetry.DjiSrtParser import (
    extract_fields,
    parse_dji_srt,
    parse_timecode,
    parse_wall_clock,
)

# Newer firmware / embedded subtitle track: 4 lines, FrameCnt and the wall
# clock share a line, telemetry sits at line index 3.
EMBEDDED_SRT = """\
1
00:00:00,000 --> 00:00:00,033
FrameCnt: 0 2026-07-25 14:38:26.477
[iso: 120] [shutter: 1/1250.0] [fnum: 2.8] [ev: 0] [focal_len: 24.00] \
[latitude: 30.648730] [longitude: -97.675867] [rel_alt: 14.885 abs_alt: 207.027] \
[gb_yaw: -161.5 gb_pitch: -53.0 gb_roll: 0.0]

2
00:00:00,033 --> 00:00:00,066
FrameCnt: 1 2026-07-25 14:38:26.511
[iso: 120] [latitude: 30.648740] [longitude: -97.675877] \
[rel_alt: 15.885 abs_alt: 208.027] [gb_yaw: -160.0 gb_pitch: -53.0 gb_roll: 0.0]
"""

# Classic sidecar: 5 lines, HTML-wrapped, single ``altitude`` key.
CLASSIC_SRT = """\
1
00:00:00,000 --> 00:00:00,033
<font size="28">FrameCnt: 1, DiffTime: 33ms
2023-05-01 10:00:00,000
[iso: 100] [latitude: 30.100000] [longtitude: -97.200000] [altitude: 210.5] </font>

2
00:00:00,033 --> 00:00:00,066
<font size="28">FrameCnt: 2, DiffTime: 33ms
2023-05-01 10:00:00,033
[iso: 100] [latitude: 30.100100] [longtitude: -97.200100] [altitude: 211.0] </font>
"""


class TestTimecode:
    @pytest.mark.parametrize("text,expected", [
        ("00:00:00,000", 0.0),
        ("00:00:01,500", 1.5),
        ("00:01:00,000", 60.0),
        ("01:00:00,000", 3600.0),
        ("00:00:29,663", 29.663),
        ("00:00:00.250", 0.25),   # dot separator
    ])
    def test_parses_known_timecodes(self, text, expected):
        assert parse_timecode(text) == pytest.approx(expected)

    def test_pads_short_milliseconds(self):
        """``,5`` is 500 ms, not 5 ms."""
        assert parse_timecode("00:00:00,5") == pytest.approx(0.5)

    @pytest.mark.parametrize("text", ["", None, "garbage", "1:2:3"])
    def test_rejects_malformed(self, text):
        assert parse_timecode(text) is None


class TestFieldExtraction:
    def test_splits_multi_pair_brackets(self):
        """``[rel_alt: X abs_alt: Y]`` must yield two keys, not one.

        The previous single-split approach produced
        ``rel_alt = "14.885 abs_alt"`` and lost the altitude entirely.
        """
        fields = extract_fields("[rel_alt: 14.885 abs_alt: 207.027]")
        assert fields["rel_alt"] == "14.885"
        assert fields["abs_alt"] == "207.027"

    def test_handles_three_pairs_in_one_bracket(self):
        fields = extract_fields("[gb_yaw: -161.5 gb_pitch: -53.0 gb_roll: 0.0]")
        assert fields["gb_yaw"] == "-161.5"
        assert fields["gb_pitch"] == "-53.0"
        assert fields["gb_roll"] == "0.0"

    def test_handles_values_with_slashes(self):
        assert extract_fields("[shutter: 1/1250.0]")["shutter"] == "1/1250.0"

    def test_keys_are_lowercased(self):
        assert "latitude" in extract_fields("[Latitude: 30.5]")

    def test_empty_input(self):
        assert extract_fields("") == {}
        assert extract_fields(None) == {}


class TestEmbeddedVariant:
    """The 4-line layout the previous parser rejected outright."""

    def test_parses_all_entries(self):
        samples = parse_dji_srt(EMBEDDED_SRT)
        assert len(samples) == 2

    def test_extracts_position(self):
        first = parse_dji_srt(EMBEDDED_SRT)[0]
        assert first.latitude == pytest.approx(30.648730)
        assert first.longitude == pytest.approx(-97.675867)
        assert first.has_position

    def test_separates_msl_from_agl(self):
        """``abs_alt`` is MSL, ``rel_alt`` is above the takeoff point."""
        first = parse_dji_srt(EMBEDDED_SRT)[0]
        assert first.altitude_msl_m == pytest.approx(207.027)
        assert first.altitude_ato_m == pytest.approx(14.885)

    def test_extracts_times_and_frame_index(self):
        samples = parse_dji_srt(EMBEDDED_SRT)
        assert samples[0].start_seconds == pytest.approx(0.0)
        assert samples[0].end_seconds == pytest.approx(0.033)
        assert samples[0].frame_index == 0
        assert samples[1].start_seconds == pytest.approx(0.033)
        assert samples[1].frame_index == 1

    def test_extracts_gimbal_yaw(self):
        assert parse_dji_srt(EMBEDDED_SRT)[0].yaw_deg == pytest.approx(-161.5)


class TestClassicVariant:
    """The 5-line HTML-wrapped sidecar must keep working."""

    def test_parses_all_entries(self):
        assert len(parse_dji_srt(CLASSIC_SRT)) == 2

    def test_handles_longitude_misspelling(self):
        """Some firmware writes ``longtitude``."""
        first = parse_dji_srt(CLASSIC_SRT)[0]
        assert first.longitude == pytest.approx(-97.200000)

    def test_legacy_relative_altitude_lands_in_the_agl_slot(self):
        """Older firmware writes one ``altitude`` key with no datum, and the
        datum differs between aircraft — verified on four real tracks, three
        relative (one starting at -9.7 m) and a Mavic 2 Pro genuinely MSL at
        1622 m. Filing a relative value as MSL made the HUD label it "MSL",
        left AGL blank, and starved both the wizard's altitude detection and
        the DEM correction, which anchor on reported AGL.
        """
        relative = (
            '1\n'
            '00:00:00,000 --> 00:00:00,033\n'
            '<font size="36">SrtCnt : 1, DiffTime : 33ms\n'
            '2024-03-22 16:51:55,597,864\n'
            '[latitude: 30.652916] [longitude: -97.954593] [altitude: -4.600000] </font>\n'
            '\n'
            '2\n'
            '00:00:00,033 --> 00:00:00,066\n'
            '<font size="36">SrtCnt : 2, DiffTime : 33ms\n'
            '2024-03-22 16:51:55,631,227\n'
            '[latitude: 30.652920] [longitude: -97.954600] [altitude: 77.100000] </font>\n'
        )
        samples = parse_dji_srt(relative)
        assert len(samples) == 2
        assert samples[0].altitude_ato_m == pytest.approx(-4.6)
        assert samples[1].altitude_ato_m == pytest.approx(77.1)
        # No absolute datum is knowable, so MSL must stay unset rather than
        # be filled with a number that is 320 m wrong.
        assert all(s.altitude_msl_m is None for s in samples)

    def test_an_explicit_pair_is_never_reinterpreted(self):
        """Modern firmware states both datums; the heuristic must not touch
        it even when rel_alt is small or negative."""
        modern = (
            '1\n'
            '00:00:00,000 --> 00:00:00,033\n'
            'FrameCnt: 0 2026-07-25 15:04:50.177\n'
            '[latitude: 30.648621] [longitude: -97.675879] '
            '[rel_alt: -0.100 abs_alt: 194.900]\n'
        )
        first = parse_dji_srt(modern)[0]
        assert first.altitude_ato_m == pytest.approx(-0.1)
        assert first.altitude_msl_m == pytest.approx(194.9)
        assert first.altitude_datum_unknown is False

    def test_a_high_legacy_track_is_still_read_as_msl(self):
        """The Mavic 2 Pro case: 1622 m cannot be height above takeoff."""
        high = (
            '1\n'
            '00:00:00,000 --> 00:00:00,033\n'
            '<font size="36">SrtCnt : 1, DiffTime : 33ms\n'
            '2019-08-01 10:00:00,000,000\n'
            '[latitude: 41.357636] [longitude: -111.867787] [altitude: 1622.800000] </font>\n'
        )
        first = parse_dji_srt(high)[0]
        assert first.altitude_msl_m == pytest.approx(1622.8)
        assert first.altitude_ato_m is None

    def test_the_whole_track_decides_not_one_cue(self):
        """A track that climbs from near zero is relative throughout, even
        though its later cues are individually above the threshold."""
        climbing = "".join(
            f'{i + 1}\n'
            f'00:00:0{i},000 --> 00:00:0{i},033\n'
            f'<font size="36">SrtCnt : {i + 1}, DiffTime : 33ms\n'
            f'2024-03-22 16:51:5{i},000,000\n'
            f'[latitude: 30.65] [longitude: -97.95] [altitude: {i * 40}.0] </font>\n\n'
            for i in range(4)
        )
        samples = parse_dji_srt(climbing)
        assert [s.altitude_ato_m for s in samples] == [0.0, 40.0, 80.0, 120.0]
        assert all(s.altitude_msl_m is None for s in samples)

    def test_legacy_altitude_key_maps_to_msl(self):
        first = parse_dji_srt(CLASSIC_SRT)[0]
        assert first.altitude_msl_m == pytest.approx(210.5)
        assert first.altitude_ato_m is None

    def test_frame_index_from_comma_form(self):
        assert parse_dji_srt(CLASSIC_SRT)[0].frame_index == 1


class TestRobustness:
    def test_empty_input(self):
        assert parse_dji_srt("") == []
        assert parse_dji_srt(None) == []

    def test_entry_without_timecode_is_skipped(self):
        assert parse_dji_srt("1\nnot a timecode\n[latitude: 1.0]\n") == []

    def test_one_bad_entry_does_not_lose_the_rest(self):
        """A truncated cue must not cost the operator the other fixes."""
        text = EMBEDDED_SRT + "\n\n3\nthis entry is broken\n"
        assert len(parse_dji_srt(text)) == 2

    def test_missing_position_still_yields_a_sample(self):
        text = "1\n00:00:00,000 --> 00:00:00,033\n[iso: 100]\n"
        samples = parse_dji_srt(text)
        assert len(samples) == 1
        assert not samples[0].has_position

    def test_samples_are_time_ordered(self):
        out_of_order = (
            "2\n00:00:05,000 --> 00:00:05,033\n[latitude: 2.0] [longitude: 2.0]\n"
            "\n"
            "1\n00:00:01,000 --> 00:00:01,033\n[latitude: 1.0] [longitude: 1.0]\n"
        )
        samples = parse_dji_srt(out_of_order)
        assert [s.start_seconds for s in samples] == [1.0, 5.0]

    def test_tolerates_crlf_line_endings(self):
        assert len(parse_dji_srt(EMBEDDED_SRT.replace("\n", "\r\n"))) == 2


class TestWallClock:
    """The aircraft's own clock, which dates an extracted frame.

    ``start_seconds`` is only an offset into the video, so without this a
    frame has no capture time and nothing downstream can order the images
    (the GPS map traces its path by timestamp; auto-bearing sorts by it).
    Both SRT layouts must yield one: the classic sidecar puts the stamp on
    its own line, the embedded variant folds it onto the FrameCnt line.
    """

    def test_embedded_layout_yields_the_wall_clock(self):
        samples = parse_dji_srt(EMBEDDED_SRT)
        assert samples[0].captured_at == datetime(2026, 7, 25, 14, 38, 26, 477000)
        assert samples[1].captured_at == datetime(2026, 7, 25, 14, 38, 26, 511000)

    def test_classic_layout_yields_the_wall_clock(self):
        assert parse_dji_srt(CLASSIC_SRT)[0].captured_at == datetime(2023, 5, 1, 10, 0, 0)

    def test_a_cue_without_a_stamp_has_none(self):
        text = "1\n00:00:00,000 --> 00:00:00,033\n[latitude: 1.0] [longitude: 1.0]\n"
        assert parse_dji_srt(text)[0].captured_at is None

    @pytest.mark.parametrize('text, expected', [
        ('2026-08-15 12:09:26.002', datetime(2026, 8, 15, 12, 9, 26, 2000)),
        ('2026-08-15 12:09:26,002', datetime(2026, 8, 15, 12, 9, 26, 2000)),
        ('2026-08-15 12:09:26', datetime(2026, 8, 15, 12, 9, 26)),
        # DJI has written comma-grouped sub-seconds; the whole second still reads.
        ('2023-05-01 12:00:00,000,000', datetime(2023, 5, 1, 12, 0, 0)),
        ('  2026-08-15 12:09:26  ', datetime(2026, 8, 15, 12, 9, 26)),
        # ISO-style separator, seen in some embedded tracks.
        ('2026-08-15T12:09:26', datetime(2026, 8, 15, 12, 9, 26)),
        # Found anywhere in the line, not at a fixed offset.
        ('FrameCnt: 1, DiffTime: 33ms 2026-08-15 12:09:26', datetime(2026, 8, 15, 12, 9, 26)),
    ])
    def test_formats(self, text, expected):
        assert parse_wall_clock(text) == expected

    @pytest.mark.parametrize('text', ['FrameCnt: 1, DiffTime: 33ms', 'not a date', '', None])
    def test_rejects_non_dates(self, text):
        assert parse_wall_clock(text) is None
