"""Tests for KMLGeneratorService.add_flight_path (recording bundles)."""

import os

from core.services.export.KMLGeneratorService import KMLGeneratorService

PATH = [(30.0, -97.0), (30.01, -97.01), (30.02, -97.02)]


def _kml_text(service, tmp_path, name="flight.kml"):
    target = os.path.join(str(tmp_path), name)
    service.save_kml(target)
    with open(target, encoding="utf-8") as handle:
        return handle.read()


class TestAddFlightPath:
    """The aircraft's track as a LineString."""

    def test_writes_a_linestring_in_lon_lat_order(self, tmp_path):
        service = KMLGeneratorService(use_terrain=False)

        assert service.add_flight_path(PATH) is not None
        kml = _kml_text(service, tmp_path)

        assert "<LineString" in kml
        # KML coordinates are lon,lat - the reverse of how ADIAT carries them.
        assert "-97.0,30.0" in kml
        assert "-97.02,30.02" in kml

    def test_names_and_describes_the_path(self, tmp_path):
        service = KMLGeneratorService(use_terrain=False)
        service.add_flight_path(PATH, name="Search Leg 2", description="ADIAT recording")

        kml = _kml_text(service, tmp_path)

        assert "Search Leg 2" in kml
        assert "ADIAT recording" in kml

    def test_endpoints_are_marked_by_default(self, tmp_path):
        service = KMLGeneratorService(use_terrain=False)
        service.add_flight_path(PATH, name="Flight Path")

        kml = _kml_text(service, tmp_path)

        assert "Flight Path - Start" in kml
        assert "Flight Path - End" in kml

    def test_endpoint_markers_can_be_suppressed(self, tmp_path):
        service = KMLGeneratorService(use_terrain=False)
        service.add_flight_path(PATH, mark_endpoints=False)

        kml = _kml_text(service, tmp_path)

        assert "- Start" not in kml
        assert "- End" not in kml

    def test_color_is_written_as_abgr(self, tmp_path):
        service = KMLGeneratorService(use_terrain=False)
        service.add_flight_path(PATH, color_rgb=(0, 229, 255), width=5)

        kml = _kml_text(service, tmp_path)

        # RGB (0, 229, 255) -> ABGR ffffe500
        assert "ffffe500" in kml
        assert "<width>5</width>" in kml

    def test_fewer_than_two_points_draws_nothing(self, tmp_path):
        service = KMLGeneratorService(use_terrain=False)

        assert service.add_flight_path([]) is None
        assert service.add_flight_path([(30.0, -97.0)]) is None
        assert service.add_flight_path(None) is None
        assert "<LineString" not in _kml_text(service, tmp_path)

    def test_unusable_fixes_are_skipped(self, tmp_path):
        """Telemetry can report a partial fix; it must not break the export."""
        service = KMLGeneratorService(use_terrain=False)
        mixed = [(30.0, -97.0), (None, -97.01), ("x", "y"), (30.02, -97.02)]

        assert service.add_flight_path(mixed) is not None
        kml = _kml_text(service, tmp_path)

        assert "-97.0,30.0" in kml
        assert "-97.02,30.02" in kml
        assert "None" not in kml

    def test_path_and_detection_placemarks_coexist(self, tmp_path):
        """A recording bundle's KML carries both in one document."""
        service = KMLGeneratorService(use_terrain=False)
        service.add_flight_path(PATH)
        service.add_aoi_placemark(
            "person #1", 30.005, -97.005, "Confidence: 0.82", color_rgb=(30, 20, 10)
        )

        kml = _kml_text(service, tmp_path)

        assert "<LineString" in kml
        assert "person #1" in kml
        assert "Confidence: 0.82" in kml
