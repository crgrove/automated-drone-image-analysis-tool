"""Unit tests for CombinedPdfReportService and RunReportContext."""

import os
from unittest.mock import patch

import pytest

from core.services.export.CombinedPdfReportService import (
    CombinedPdfReportService,
    RunReportContext,
)


def _write_run(tmp_path, name, images):
    """Create <name>/ADIAT_Results/ADIAT_Data.xml plus the image files.

    Args:
        images: list of (filename, exists, hidden, aoi_flags) where aoi_flags
            is a list of bools (one AOI per flag).
    """
    run_dir = tmp_path / name
    results_dir = run_dir / "ADIAT_Results"
    results_dir.mkdir(parents=True)

    image_blocks = []
    for filename, exists, hidden, aoi_flags in images:
        if exists:
            (run_dir / filename).write_text("jpg")
        aois = "".join(
            f'<areas_of_interest center="(10, 10)" radius="5" area="20.0" '
            f'flagged="{flag}" number="{i + 1}"/>'
            for i, flag in enumerate(aoi_flags)
        )
        image_blocks.append(
            f'<image path="../{filename}" hidden="{hidden}" '
            f'width="100" height="100">{aois}</image>'
        )

    xml = (
        '<data>'
        '<settings input_dir="in" output_dir="out" identifier_color="(255, 0, 255)" '
        'aoi_radius="15" algorithm="HSVColorRange" thermal="False" num_processes="1" '
        'min_area="10" max_area="" hist_ref_path="" kmeans_clusters="">'
        '<options><option name="sensitivity" value="5"/></options>'
        '</settings>'
        f'<images>{"".join(image_blocks)}</images>'
        '</data>'
    )
    xml_path = results_dir / "ADIAT_Data.xml"
    xml_path.write_text(xml)
    return str(xml_path)


# ---------------------------------------------------------------------------
# RunReportContext.from_xml
# ---------------------------------------------------------------------------

def test_context_filters_mirror_the_single_run_report(tmp_path):
    xml_path = _write_run(tmp_path, "Flight1", [
        ("keep.jpg", True, "False", ["True", "False"]),   # flagged: keep only flagged AOI
        ("plain.jpg", True, "False", ["False"]),          # unflagged: dropped by default
        ("hidden.jpg", True, "True", ["True"]),           # hidden: dropped
        ("gone.jpg", False, "False", ["True"]),           # missing file: counted
    ])

    ctx = RunReportContext.from_xml(
        xml_path, 'Lat/Long - Decimal Degrees', 'ft',
        include_images_without_flagged_aois=False)

    assert [img['name'] for img in ctx.images] == ['keep.jpg']
    assert len(ctx.images[0]['areas_of_interest']) == 1
    assert ctx.images[0]['areas_of_interest'][0]['flagged'] is True
    assert ctx.unavailable_count == 1
    assert ctx.total_aoi_count == 1
    assert ctx.run_name == "Flight1"
    assert not hasattr(ctx, 'custom_agl_altitude_ft')


def test_context_include_flag_keeps_unflagged_images(tmp_path):
    xml_path = _write_run(tmp_path, "Flight2", [
        ("plain.jpg", True, "False", ["False", "False"]),
    ])

    ctx = RunReportContext.from_xml(
        xml_path, 'Lat/Long - Decimal Degrees', 'ft',
        include_images_without_flagged_aois=True)

    assert [img['name'] for img in ctx.images] == ['plain.jpg']
    assert len(ctx.images[0]['areas_of_interest']) == 2
    assert ctx.total_aoi_count == 2


def test_context_run_name_uses_parent_of_adiat_results(tmp_path):
    xml_path = _write_run(tmp_path, "Ridge Sortie", [
        ("a.jpg", True, "False", ["True"]),
    ])
    ctx = RunReportContext.from_xml(xml_path, 'Lat/Long - Decimal Degrees', 'ft')
    assert ctx.run_name == "Ridge Sortie"


# ---------------------------------------------------------------------------
# generate_combined_report
# ---------------------------------------------------------------------------

def _service(**kwargs):
    return CombinedPdfReportService(
        organization="TEXSAR", search_name="Test Search", **kwargs)


def test_combined_report_builds_one_pdf_across_runs(tmp_path):
    run1 = _write_run(tmp_path, "Flight1", [("a.jpg", True, "False", ["True"])])
    run2 = _write_run(tmp_path, "Flight2", [("b.jpg", True, "False", ["True"])])
    empty = _write_run(tmp_path, "Flight3", [("c.jpg", True, "False", ["False"])])
    output = tmp_path / "combined.pdf"

    service = _service()
    seen_runs = []

    def fake_details(progress_callback=None, cancel_check=None):
        seen_runs.append((service.viewer.run_name,
                          [img['name'] for img in service.images]))

    with patch.object(service, '_generate_overview_map', return_value=None), \
            patch.object(service, '_add_image_details', side_effect=fake_details):
        service.generate_combined_report(str(output), [run1, run2, empty])

    assert output.exists() and output.stat().st_size > 0
    # Per-run sections used each run's own context/images, in order, and the
    # image names carry the collision-proof run prefix.
    assert seen_runs == [
        ("Flight1", ["[1] a.jpg"]),
        ("Flight2", ["[2] b.jpg"]),
    ]


def test_combined_report_without_usable_runs_raises(tmp_path):
    empty = _write_run(tmp_path, "Flight1", [("a.jpg", True, "False", ["False"])])
    output = tmp_path / "combined.pdf"
    service = _service()

    with pytest.raises(ValueError):
        service.generate_combined_report(str(output), [empty])
    assert not output.exists()


def test_combined_report_skips_unreadable_files(tmp_path):
    run1 = _write_run(tmp_path, "Flight1", [("a.jpg", True, "False", ["True"])])
    junk = tmp_path / "junk.xml"
    junk.write_text("not xml <<<")
    output = tmp_path / "combined.pdf"
    service = _service()

    with patch.object(service, '_generate_overview_map', return_value=None), \
            patch.object(service, '_add_image_details'):
        service.generate_combined_report(str(output), [str(junk), run1])

    assert output.exists()


def test_cancel_between_runs_stops_the_build(tmp_path):
    run1 = _write_run(tmp_path, "Flight1", [("a.jpg", True, "False", ["True"])])
    run2 = _write_run(tmp_path, "Flight2", [("b.jpg", True, "False", ["True"])])
    output = tmp_path / "combined.pdf"
    service = _service()

    calls = []

    def cancel_after_first():
        return len(calls) >= 1

    with patch.object(service, '_generate_overview_map', return_value=None), \
            patch.object(service, '_add_image_details',
                         side_effect=lambda **k: calls.append(1)):
        service.generate_combined_report(
            str(output), [run1, run2], cancel_check=cancel_after_first)

    assert calls == [1]
    assert not output.exists()


def test_progress_offsets_accumulate_across_runs(tmp_path):
    run1 = _write_run(tmp_path, "Flight1", [("a.jpg", True, "False", ["True", "True"])])
    run2 = _write_run(tmp_path, "Flight2", [("b.jpg", True, "False", ["True"])])
    output = tmp_path / "combined.pdf"
    service = _service()
    updates = []

    def fake_details(progress_callback=None, cancel_check=None):
        # The base class reports run-local counts; the wrapper globalizes them
        if progress_callback:
            progress_callback(1, 99, "processing")

    with patch.object(service, '_generate_overview_map', return_value=None), \
            patch.object(service, '_add_image_details', side_effect=fake_details):
        service.generate_combined_report(
            str(output), [run1, run2],
            progress_callback=lambda c, t, m: updates.append((c, t, m)))

    run_updates = [u for u in updates if "processing" in u[2]]
    assert run_updates[0][:2] == (1, 3)   # run 1: offset 0 + 1 of grand total 3
    assert run_updates[1][:2] == (3, 3)   # run 2: offset 2 + 1
    assert "Flight1" in run_updates[0][2]
    assert "Flight2" in run_updates[1][2]


def test_context_collects_duplicate_sightings_before_filtering(tmp_path):
    """The duplicate's image has no flagged AOI, so the report drops it -
    its sighting must still be listed under the primary."""
    run_dir = tmp_path / "Flight9"
    results_dir = run_dir / "ADIAT_Results"
    results_dir.mkdir(parents=True)
    for name in ("primary.jpg", "dup.jpg"):
        (run_dir / name).write_text("jpg")
    xml = (
        '<data><settings input_dir="in" output_dir="out" identifier_color="(255, 0, 255)" '
        'aoi_radius="15" algorithm="HSVColorRange" thermal="False" num_processes="1" '
        'min_area="10" max_area="" hist_ref_path="" kmeans_clusters=""><options/></settings>'
        '<images>'
        '<image path="../primary.jpg" hidden="False" width="100" height="100">'
        '<areas_of_interest center="(10, 10)" radius="5" area="20.0" flagged="True" number="1"/></image>'
        '<image path="../dup.jpg" hidden="False" width="100" height="100">'
        '<areas_of_interest center="(60, 60)" radius="5" area="20.0" flagged="False" number="2" '
        'duplicate_of="1"/></image>'
        '</images></data>'
    )
    xml_path = results_dir / "ADIAT_Data.xml"
    xml_path.write_text(xml)

    ctx = RunReportContext.from_xml(str(xml_path), 'Lat/Long - Decimal Degrees', 'ft')

    assert [img['name'] for img in ctx.images] == ['primary.jpg']
    sightings = ctx.duplicate_sightings[1]
    assert [(s.image_name, s.number) for s in sightings] == [('dup.jpg', 2)]


# ---------------------------------------------------------------------------
# Wingtra geotags (load_run_contexts)
# ---------------------------------------------------------------------------

_GEOTAGS_HEADER = (
    "# image name,latitude [decimal degrees],longitude [decimal degrees],"
    "altitude [meter],omega [degrees],phi [degrees],kappa [degrees],"
    "accuracy horizontal [meter],accuracy vertical [meter]"
)


class _FlatTerrain:
    """Terrain stub: 100 m ground everywhere, no network (CLAUDE.md 3.3)."""

    def __init__(self, **kwargs):
        pass

    def get_elevation(self, lat, lon):
        from types import SimpleNamespace
        return SimpleNamespace(elevation_m=100.0, geoid_undulation_m=None, source='terrain')


def _wingtra_run(tmp_path, link_status=None):
    """A one-image run with a geotags CSV beside its image.

    Args:
        link_status: None writes no <wingtra_geotags> block (every XML from
            before the link existed); otherwise the block's status.
    """
    xml_path = _write_run(tmp_path, "Wingtra", [("W1.JPG", True, "False", ["True"])])
    csv_path = tmp_path / "Wingtra" / "geotags.csv"
    csv_path.write_text(
        _GEOTAGS_HEADER + "\nW1.JPG,43.78,-110.72,350.0,0.5,1.2,90.0,0.02,0.03\n",
        encoding="utf-8")
    if link_status is not None:
        with open(xml_path, encoding="utf-8") as handle:
            xml = handle.read()
        block = f'<wingtra_geotags csv_path="{csv_path}" status="{link_status}" />'
        with open(xml_path, "w", encoding="utf-8") as handle:
            handle.write(xml.replace("</data>", block + "</data>"))
    return xml_path


@pytest.mark.parametrize('link_status', [None, 'loaded'])
def test_load_run_contexts_applies_wingtra_geotags(tmp_path, link_status):
    """Without the geotags a Wingtra AOI has no position but the camera's."""
    from core.services.export.CombinedPdfReportService import load_run_contexts
    xml_path = _wingtra_run(tmp_path, link_status)

    with patch("core.services.image.WingtraDataService.TerrainService", _FlatTerrain):
        contexts = load_run_contexts([xml_path], 'Lat/Long - Decimal Degrees', 'ft')

    image = contexts[0].images[0]
    assert image['bearing'] == pytest.approx(270.0)
    assert image['wingtra_agl_ft'] == pytest.approx(250.0 * 3.28084)


def test_load_run_contexts_respects_a_declined_link(tmp_path):
    from core.services.export.CombinedPdfReportService import load_run_contexts
    xml_path = _wingtra_run(tmp_path, 'declined')

    with patch("core.services.image.WingtraDataService.TerrainService", _FlatTerrain):
        contexts = load_run_contexts([xml_path], 'Lat/Long - Decimal Degrees', 'ft')

    assert 'wingtra_agl_ft' not in contexts[0].images[0]


def test_a_geotags_failure_keeps_the_run(tmp_path):
    from unittest.mock import MagicMock
    from core.services.export.CombinedPdfReportService import load_run_contexts
    xml_path = _wingtra_run(tmp_path)
    logger = MagicMock()

    with patch("core.services.export.CombinedPdfReportService.attach_geotags",
               side_effect=RuntimeError("no DEM")):
        contexts = load_run_contexts([xml_path], 'Lat/Long - Decimal Degrees', 'ft', logger=logger)

    assert [ctx.run_name for ctx in contexts] == ["Wingtra"]
    assert "no DEM" in logger.warning.call_args.args[0]
