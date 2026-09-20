"""Unit tests for ReviewMergeService - multi-reviewer copy merging."""

import pytest

from core.services.export.CombinedPdfReportService import (
    CombinedPdfReportService,
    RunReportContext,
)
from core.services.export.ReviewMergeService import ReviewMergeService


def _aoi_xml(center, number=None, flagged=False, comment=None,
             user_created=False, user_pos=None):
    attrs = [f'center="{center}"', 'radius="5"', 'area="20.0"',
             f'flagged="{flagged}"']
    if number is not None:
        attrs.append(f'number="{number}"')
    if comment:
        attrs.append(f'user_comment="{comment}"')
    if user_created:
        attrs.append('user_created="True"')
    if user_pos:
        attrs.append(f'user_latitude="{user_pos[0]}" user_longitude="{user_pos[1]}"')
    return f'<areas_of_interest {" ".join(attrs)}/>'


def _write_copy(tmp_path, reviewer, images, input_dir="D:/missions/Batch1",
                reviewer_name=None):
    """One reviewer's XML copy in its own folder (as the workflow produces).

    Args:
        images: list of (path, hidden, [aoi_xml_strings]).
    """
    folder = tmp_path / reviewer
    folder.mkdir(parents=True, exist_ok=True)
    review_meta = (f'<review_metadata review_id="rid-{reviewer}" '
                   f'reviewer_name="{reviewer_name}" review_date="2026-08-22"/>'
                   if reviewer_name else '')
    image_blocks = "".join(
        f'<image path="{path}" hidden="{hidden}" width="100" height="100">'
        f'{"".join(aois)}</image>'
        for path, hidden, aois in images
    )
    xml = (
        f'<data>{review_meta}'
        f'<settings input_dir="{input_dir}" output_dir="out" '
        'identifier_color="(255, 0, 255)" aoi_radius="15" algorithm="HSVColorRange" '
        'thermal="False" num_processes="1" min_area="10" max_area="" '
        'hist_ref_path="" kmeans_clusters=""><options/></settings>'
        f'<images>{image_blocks}</images>'
        '</data>'
    )
    xml_path = folder / "ADIAT_Data.xml"
    xml_path.write_text(xml)
    return str(xml_path)


def _load_group(tmp_path, paths):
    service = ReviewMergeService()
    records = service.load_run_records(paths)
    groups = service.group_records(records)
    return service, groups


# ---------------------------------------------------------------------------
# Fingerprinting and grouping
# ---------------------------------------------------------------------------

def test_copies_of_the_same_run_group_together(tmp_path):
    base = [("C:/orig/a.jpg", "False", [_aoi_xml("(10, 10)", number=1)])]
    with_review = [("C:/orig/a.jpg", "False",
                    [_aoi_xml("(10, 10)", number=1, flagged=True,
                              comment="clothing?", user_pos=(34.1, -117.2))])]
    other_run = [("C:/orig/b.jpg", "False", [_aoi_xml("(50, 50)", number=1)])]

    p1 = _write_copy(tmp_path, "Reviewer1", base)
    p2 = _write_copy(tmp_path, "Reviewer2", with_review)
    p3 = _write_copy(tmp_path, "OtherRun", other_run)

    _, groups = _load_group(tmp_path, [p1, p2, p3])

    assert [len(g) for g in groups] == [2, 1]


def test_reviewer_created_aois_do_not_split_the_group(tmp_path):
    base = [("C:/orig/a.jpg", "False", [_aoi_xml("(10, 10)", number=1)])]
    with_added = [("C:/orig/a.jpg", "False", [
        _aoi_xml("(10, 10)", number=1),
        _aoi_xml("(80, 80)", number=2, flagged=True, user_created=True),
    ])]
    p1 = _write_copy(tmp_path, "Reviewer1", base)
    p2 = _write_copy(tmp_path, "Reviewer2", with_added)

    _, groups = _load_group(tmp_path, [p1, p2])
    assert [len(g) for g in groups] == [2]


# ---------------------------------------------------------------------------
# Merge semantics
# ---------------------------------------------------------------------------

def _merged_single_image(tmp_path, copies):
    """Write copies of a one-image run, merge, return the image's AOIs."""
    paths = [_write_copy(tmp_path, reviewer, images, reviewer_name=name)
             for reviewer, name, images in copies]
    service, groups = _load_group(tmp_path, paths)
    assert len(groups) == 1
    merged = service.merge_group(groups[0])
    return merged, merged.images[0]['areas_of_interest']


def test_flags_or_together_with_count_note(tmp_path):
    merged, aois = _merged_single_image(tmp_path, [
        ("R1", "Sarah", [("C:/o/a.jpg", "False",
                          [_aoi_xml("(10, 10)", number=1, flagged=True)])]),
        ("R2", "John", [("C:/o/a.jpg", "False",
                         [_aoi_xml("(10, 10)", number=1, flagged=True)])]),
        ("R3", "Ana", [("C:/o/a.jpg", "False",
                        [_aoi_xml("(10, 10)", number=1)])]),
    ])
    assert merged.review_count == 3
    assert len(aois) == 1, "one AOI, not one per reviewer"
    assert aois[0]['flagged'] is True
    assert "Flagged by 2 of 3 reviewers" in aois[0]['review_note']
    assert "Sarah" in aois[0]['review_note'] and "John" in aois[0]['review_note']


def test_comments_combine_with_attribution(tmp_path):
    _, aois = _merged_single_image(tmp_path, [
        ("R1", "Sarah", [("C:/o/a.jpg", "False",
                          [_aoi_xml("(10, 10)", number=1, flagged=True,
                                    comment="possible clothing")])]),
        ("R2", "John", [("C:/o/a.jpg", "False",
                         [_aoi_xml("(10, 10)", number=1, comment="shadow")])]),
    ])
    assert aois[0]['user_comment'] == "Sarah: possible clothing — John: shadow"


def test_single_mover_position_is_adopted_and_noted(tmp_path):
    _, aois = _merged_single_image(tmp_path, [
        ("R1", "Sarah", [("C:/o/a.jpg", "False",
                          [_aoi_xml("(10, 10)", number=1, flagged=True,
                                    user_pos=(34.1, -117.2))])]),
        ("R2", "John", [("C:/o/a.jpg", "False",
                         [_aoi_xml("(10, 10)", number=1)])]),
    ])
    assert aois[0]['user_latitude'] == pytest.approx(34.1)
    assert aois[0]['user_longitude'] == pytest.approx(-117.2)
    assert "Position corrected by Sarah." in aois[0]['review_note']


def test_disagreeing_movers_are_called_out_with_distance(tmp_path):
    _, aois = _merged_single_image(tmp_path, [
        ("R1", "Sarah", [("C:/o/a.jpg", "False",
                          [_aoi_xml("(10, 10)", number=1, flagged=True,
                                    user_pos=(34.1000, -117.2000))])]),
        ("R2", "John", [("C:/o/a.jpg", "False",
                         [_aoi_xml("(10, 10)", number=1, flagged=True,
                                   user_pos=(34.1009, -117.2000))])]),
    ])
    # First mover's correction positions the marker
    assert aois[0]['user_latitude'] == pytest.approx(34.1000)
    note = aois[0]['review_note']
    assert "corrected differently by 2 reviewers" in note
    assert "Sarah (34.100000, -117.200000)" in note
    assert "John (34.100900, -117.200000)" in note
    assert "100 m apart" in note  # ~0.0009 deg lat = ~100 m


def test_identical_moves_do_not_read_as_disagreement(tmp_path):
    _, aois = _merged_single_image(tmp_path, [
        ("R1", "Sarah", [("C:/o/a.jpg", "False",
                          [_aoi_xml("(10, 10)", number=1,
                                    user_pos=(34.1, -117.2))])]),
        ("R2", "John", [("C:/o/a.jpg", "False",
                         [_aoi_xml("(10, 10)", number=1,
                                   user_pos=(34.1, -117.2))])]),
    ])
    assert "differently" not in aois[0]['review_note']


def test_reviewer_created_aoi_appears_once_attributed(tmp_path):
    _, aois = _merged_single_image(tmp_path, [
        ("R1", "Sarah", [("C:/o/a.jpg", "False",
                          [_aoi_xml("(10, 10)", number=1)])]),
        ("R2", "John", [("C:/o/a.jpg", "False", [
            _aoi_xml("(10, 10)", number=1),
            _aoi_xml("(80, 80)", number=2, flagged=True, user_created=True),
        ])]),
    ])
    assert len(aois) == 2
    added = [a for a in aois if a.get('user_created')][0]
    assert "Added by John." in added['review_note']


def test_center_matching_when_numbers_are_absent(tmp_path):
    # Copies that were never opened in a viewer carry no backfilled AOI
    # numbers; identity falls back to the center rule.
    _, aois = _merged_single_image(tmp_path, [
        ("R1", "Sarah", [("C:/o/a.jpg", "False",
                          [_aoi_xml("(100, 100)", flagged=True)])]),
        ("R2", "John", [("C:/o/a.jpg", "False",
                         [_aoi_xml("(100, 100)", flagged=True)])]),
    ])
    assert len(aois) == 1
    assert "Flagged by 2 of 2" in aois[0]['review_note']


def test_image_hidden_by_one_reviewer_stays_visible(tmp_path):
    merged, _ = _merged_single_image(tmp_path, [
        ("R1", "Sarah", [("C:/o/a.jpg", "True",
                          [_aoi_xml("(10, 10)", number=1)])]),
        ("R2", "John", [("C:/o/a.jpg", "False",
                         [_aoi_xml("(10, 10)", number=1, flagged=True)])]),
    ])
    assert merged.images[0]['hidden'] is False


def test_merged_run_named_after_the_batch_not_a_reviewer(tmp_path):
    merged, _ = _merged_single_image(tmp_path, [
        ("R1", "Sarah", [("C:/o/a.jpg", "False",
                          [_aoi_xml("(10, 10)", number=1)])]),
        ("R2", "John", [("C:/o/a.jpg", "False",
                         [_aoi_xml("(10, 10)", number=1)])]),
    ])
    assert merged.run_name == "Batch1"
    assert merged.reviewer_names == ["Sarah", "John"]


# ---------------------------------------------------------------------------
# Context integration: policy filters + scan-root image resolution
# ---------------------------------------------------------------------------

def test_commented_unflagged_aoi_is_kept(tmp_path):
    img = tmp_path / "real.jpg"
    img.write_text("jpg")
    path = str(img).replace("\\", "/")
    xml = _write_copy(tmp_path, "R1", [(path, "False", [
        _aoi_xml("(10, 10)", number=1, comment="worth a look"),
        _aoi_xml("(50, 50)", number=2),
    ])])

    ctx = RunReportContext.from_xml(xml, 'Lat/Long - Decimal Degrees', 'ft')

    assert len(ctx.images) == 1
    kept = ctx.images[0]['areas_of_interest']
    assert len(kept) == 1
    assert kept[0]['user_comment'] == "worth a look"


def test_path_resolver_rescues_a_travelling_xml(tmp_path):
    # The reviewer's XML references the ORIGINAL machine's path; the scan
    # root on this machine holds the images under a matching folder.
    scan_root = tmp_path / "scan"
    batch = scan_root / "Batch1"
    batch.mkdir(parents=True)
    (batch / "a.jpg").write_text("jpg")

    xml = _write_copy(tmp_path, "R1", [
        ("D:/missions/Batch1/a.jpg", "False",
         [_aoi_xml("(10, 10)", number=1, flagged=True)])])

    from core.services.RecoverySessionService import RecoverySession
    session = RecoverySession(str(scan_root))

    without = RunReportContext.from_xml(xml, 'Lat/Long - Decimal Degrees', 'ft')
    assert without.images == [] and without.unavailable_count == 1

    with_resolver = RunReportContext.from_xml(
        xml, 'Lat/Long - Decimal Degrees', 'ft',
        path_resolver=session.resolve_file)
    assert len(with_resolver.images) == 1
    assert with_resolver.images[0]['path'] == str(batch / "a.jpg")
    assert with_resolver.unavailable_count == 0


def test_load_contexts_end_to_end_merges_copies(tmp_path):
    img = tmp_path / "shared.jpg"
    img.write_text("jpg")
    path = str(img).replace("\\", "/")

    copy1 = _write_copy(tmp_path, "Reviewer1", [
        (path, "False", [_aoi_xml("(10, 10)", number=1, flagged=True)])],
        reviewer_name="Sarah")
    copy2 = _write_copy(tmp_path, "Reviewer2", [
        (path, "False", [_aoi_xml("(10, 10)", number=1, flagged=True)])],
        reviewer_name="John")
    other = _write_copy(tmp_path, "OtherRun", [
        (path, "False", [_aoi_xml("(90, 90)", number=1, flagged=True)])],
        input_dir="D:/missions/Batch2")

    service = CombinedPdfReportService()
    contexts = service.load_contexts([copy1, copy2, other])

    assert len(contexts) == 2
    merged_ctx = contexts[0]
    assert merged_ctx.review_count == 2
    assert merged_ctx.run_name == "Batch1"
    assert merged_ctx.total_aoi_count == 1, "the shared AOI appears once"
    assert contexts[1].review_count == 1
