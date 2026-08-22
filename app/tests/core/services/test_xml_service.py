import pytest
import os
import xml.etree.ElementTree as ET
from core.services.XmlService import XmlService


@pytest.fixture
def sample_xml(tmp_path):
    xml_content = """
    <data>
        <settings output_dir="/output" input_dir="/input" num_processes="4" identifier_color="(255, 0, 0)" min_area="10" max_area="200" hist_ref_path="None"
        kmeans_clusters="None" algorithm="some_algorithm" thermal="True">
            <options>
                <option name="option1" value="value1"/>
                <option name="option2" value="value2"/>
            </options>
        </settings>
        <images>
            <image path="image1.jpg" hidden="False">
                <areas_of_interest center="(50,50)" radius="10" area="150"/>
            </image>
            <image path="image2.jpg">
                <areas_of_interest center="(100,100)" radius="20" area="300"/>
            </image>
        </images>
    </data>
    """.strip()
    xml_path = tmp_path / "test.xml"
    with open(xml_path, "w") as f:
        f.write(xml_content)
    return xml_path


def test_initialization(sample_xml):
    service = XmlService(sample_xml)
    assert service.xml_path == sample_xml
    assert isinstance(service.xml, ET.ElementTree)


def test_get_settings(sample_xml):
    service = XmlService(sample_xml)
    settings, image_count = service.get_settings()
    assert settings["output_dir"] == "/output"
    assert settings["input_dir"] == "/input"
    assert settings["num_processes"] == 4
    assert settings["identifier_color"] == (255, 0, 0)
    assert settings["min_area"] == 10
    assert settings["max_area"] == 200
    assert settings["algorithm"] == "some_algorithm"
    assert settings["thermal"] == "True"
    assert settings["options"]["option1"] == "value1"
    assert settings["options"]["option2"] == "value2"
    assert image_count == 2


def test_get_images(sample_xml):
    service = XmlService(sample_xml)
    images = service.get_images()
    assert len(images) == 2
    assert images[0]["path"].endswith("image1.jpg")
    assert images[0]["hidden"] is False
    assert images[0]["areas_of_interest"][0]["area"] == 150.0
    assert images[0]["areas_of_interest"][0]["center"] == (50, 50)
    assert images[0]["areas_of_interest"][0]["radius"] == 10


def test_add_settings_to_xml():
    service = XmlService()
    service.add_settings_to_xml(output_dir="/new_output", num_processes=8)

    settings, _ = service.get_settings()
    assert "output_dir" in settings
    assert settings["output_dir"] == "/new_output"
    assert settings["num_processes"] == 8
    assert settings["min_area"] == 10  # Ensure defaults are set correctly


def test_add_image_to_xml():
    service = XmlService()
    new_image = {
        "path": "new_image.jpg",
        "aois": [
            {"center": (25, 25), "radius": 5, "area": 50}
        ]
    }
    service.add_image_to_xml(new_image)

    images = service.get_images()
    assert len(images) == 1
    assert images[0]["path"] == "new_image.jpg"  # Should now work correctly
    assert images[0]["areas_of_interest"][0]["center"] == (25, 25)


def test_save_xml_file(tmp_path):
    service = XmlService()
    path = tmp_path / "output.xml"
    service.save_xml_file(path)
    assert os.path.exists(path)


@pytest.fixture
def fov_corners():
    return [
        (39.50100000, -105.50200000),
        (39.50110000, -105.49900000),
        (39.49980000, -105.49890000),
        (39.49970000, -105.50210000),
    ]


def test_set_and_get_fov_alignment(sample_xml, fov_corners):
    service = XmlService(sample_xml)
    image_path = service.get_images()[0]["path"]
    tie_points = [(1200.0, 800.0, 39.5005, -105.5005)]

    assert service.set_image_fov_alignment(image_path, fov_corners, tie_points, 12.5) is True

    reloaded = service.get_images()
    alignment = reloaded[0].get("fov_alignment")
    assert alignment is not None
    assert len(alignment["corners"]) == 4
    for got, expected in zip(alignment["corners"], fov_corners):
        assert got[0] == pytest.approx(expected[0], abs=1e-7)
        assert got[1] == pytest.approx(expected[1], abs=1e-7)
    assert alignment["tie_points"][0] == pytest.approx((1200.0, 800.0, 39.5005, -105.5005))
    assert alignment["rotation"] == pytest.approx(12.5)
    # The second (unrefined) image must not gain an alignment.
    assert "fov_alignment" not in reloaded[1]


def test_fov_alignment_survives_save_reload(tmp_path, sample_xml, fov_corners):
    service = XmlService(sample_xml)
    image_path = service.get_images()[0]["path"]
    service.set_image_fov_alignment(image_path, fov_corners, None, 0.0)

    out_path = tmp_path / "saved.xml"
    service.save_xml_file(out_path)

    reloaded = XmlService(out_path).get_images()
    # AOIs must be unaffected by the new attributes.
    assert len(reloaded[0]["areas_of_interest"]) == 1
    assert reloaded[0]["areas_of_interest"][0]["center"] == (50, 50)
    alignment = reloaded[0].get("fov_alignment")
    assert alignment is not None
    assert alignment["tie_points"] == []


def test_clear_fov_alignment(sample_xml, fov_corners):
    service = XmlService(sample_xml)
    image_path = service.get_images()[0]["path"]
    service.set_image_fov_alignment(image_path, fov_corners)
    assert service.get_images()[0].get("fov_alignment") is not None

    assert service.clear_image_fov_alignment(image_path) is True
    assert "fov_alignment" not in service.get_images()[0]


def test_set_fov_alignment_unknown_image(sample_xml, fov_corners):
    service = XmlService(sample_xml)
    assert service.set_image_fov_alignment("nonexistent.jpg", fov_corners) is False


def test_malformed_fov_corners_treated_as_unrefined(tmp_path):
    xml_content = """
    <data>
        <images>
            <image path="img.jpg" fov_corner_tl="garbage" fov_corner_tr="1,2" fov_corner_br="3,4" fov_corner_bl="5,6">
                <areas_of_interest center="(10,10)" radius="5" area="20"/>
            </image>
        </images>
    </data>
    """.strip()
    xml_path = tmp_path / "bad.xml"
    with open(xml_path, "w") as f:
        f.write(xml_content)

    images = XmlService(xml_path).get_images()
    assert "fov_alignment" not in images[0]
    assert len(images[0]["areas_of_interest"]) == 1


# ---------------------------------------------------------------------------
# Run-wide AOI numbers
# ---------------------------------------------------------------------------

def test_aoi_number_round_trips_through_xml(tmp_path):
    """A persisted AOI 'number' survives add_image_to_xml -> save -> reload."""
    service = XmlService()
    service.add_image_to_xml({
        "path": "img.jpg",
        "aois": [
            {"center": (10, 10), "radius": 5, "area": 20, "number": 1},
            {"center": (30, 30), "radius": 6, "area": 25, "number": 2},
        ],
    })
    out_path = tmp_path / "numbered.xml"
    service.save_xml_file(out_path)

    aois = XmlService(out_path).get_images()[0]["areas_of_interest"]
    assert aois[0]["number"] == 1
    assert aois[1]["number"] == 2


def test_add_image_to_xml_omits_number_when_absent(tmp_path):
    """AOIs without a number must not gain a 'number' attribute."""
    service = XmlService()
    service.add_image_to_xml({
        "path": "img.jpg",
        "aois": [{"center": (10, 10), "radius": 5, "area": 20}],
    })
    out_path = tmp_path / "unnumbered.xml"
    service.save_xml_file(out_path)

    assert "number" not in XmlService(out_path).get_images()[0]["areas_of_interest"][0]


def test_legacy_xml_loads_without_number(sample_xml):
    """Legacy result files (no 'number' attribute) load with no 'number' key."""
    images = XmlService(sample_xml).get_images()
    for image in images:
        for aoi in image["areas_of_interest"]:
            assert "number" not in aoi


def test_ensure_aoi_numbers_backfills_legacy_file(sample_xml):
    """ensure_aoi_numbers assigns sequential numbers to an unnumbered file."""
    service = XmlService(sample_xml)
    images = service.get_images()

    assert service.ensure_aoi_numbers(images) is True
    assert images[0]["areas_of_interest"][0]["number"] == 1
    assert images[1]["areas_of_interest"][0]["number"] == 2


def test_ensure_aoi_numbers_is_idempotent(sample_xml):
    """A second ensure_aoi_numbers pass changes nothing and returns False."""
    service = XmlService(sample_xml)
    images = service.get_images()
    service.ensure_aoi_numbers(images)

    assert service.ensure_aoi_numbers(images) is False
    assert images[0]["areas_of_interest"][0]["number"] == 1
    assert images[1]["areas_of_interest"][0]["number"] == 2


def test_ensure_aoi_numbers_persists_to_xml(tmp_path, sample_xml):
    """Backfilled numbers are written to the XML elements and survive reload."""
    service = XmlService(sample_xml)
    images = service.get_images()
    service.ensure_aoi_numbers(images)

    out_path = tmp_path / "backfilled.xml"
    service.save_xml_file(out_path)

    reloaded = XmlService(out_path).get_images()
    assert reloaded[0]["areas_of_interest"][0]["number"] == 1
    assert reloaded[1]["areas_of_interest"][0]["number"] == 2


# ---------------------------------------------------------------------------
# Grid review state
# ---------------------------------------------------------------------------

def test_grid_review_round_trips_through_save_reload(tmp_path, sample_xml):
    """Grid attributes survive save -> reload, and AOI parsing is unaffected."""
    service = XmlService(sample_xml)
    image = service.get_images()[0]
    assert service.set_image_grid_review(image['xml'], 4, 4, {0, 1, 5}) is True

    out_path = tmp_path / "grid.xml"
    service.save_xml_file(out_path)

    reloaded = XmlService(out_path).get_images()
    grid = reloaded[0]['grid_review']
    assert grid == {'rows': 4, 'cols': 4, 'reviewed': {0, 1, 5}}
    # Regression for the <image> child-iteration hazard: the new attributes
    # must not introduce elements that get mis-parsed as AOIs.
    assert len(reloaded[0]['areas_of_interest']) == 1
    assert reloaded[0]['areas_of_interest'][0]['center'] == (50, 50)
    # The untouched image stays unreviewed.
    assert reloaded[1]['grid_review'] is None


def test_legacy_xml_loads_without_grid_review(sample_xml):
    """Files written before grid review load with grid_review None."""
    for image in XmlService(sample_xml).get_images():
        assert image['grid_review'] is None


def test_malformed_grid_attributes_treated_as_unreviewed(tmp_path):
    xml_content = """
    <data>
        <images>
            <image path="a.jpg" grid_rows="x" grid_cols="4" grid_reviewed="0,1">
                <areas_of_interest center="(10,10)" radius="5" area="20"/>
            </image>
            <image path="b.jpg" grid_rows="0" grid_cols="4"/>
            <image path="c.jpg" grid_rows="2" grid_cols="2" grid_reviewed="junk,3"/>
        </images>
    </data>
    """.strip()
    xml_path = tmp_path / "bad_grid.xml"
    with open(xml_path, "w") as f:
        f.write(xml_content)

    images = XmlService(xml_path).get_images()
    # Non-integer rows -> unreviewed; AOIs untouched.
    assert images[0]['grid_review'] is None
    assert len(images[0]['areas_of_interest']) == 1
    # Zero rows -> unreviewed.
    assert images[1]['grid_review'] is None
    # Junk tokens in reviewed list are dropped, valid ones kept.
    assert images[2]['grid_review'] == {'rows': 2, 'cols': 2, 'reviewed': {3}}


def test_clear_image_grid_review(sample_xml):
    service = XmlService(sample_xml)
    image = service.get_images()[0]
    service.set_image_grid_review(image['xml'], 2, 2, {0})
    assert service.get_images()[0]['grid_review'] is not None

    assert service.clear_image_grid_review(image['xml']) is True
    assert service.get_images()[0]['grid_review'] is None
    # Clearing an element with no grid attributes is harmless.
    assert service.clear_image_grid_review(image['xml']) is True


def test_ensure_aoi_numbers_fills_gaps_above_existing_max(tmp_path):
    """Partially numbered files keep existing numbers; gaps get max+1 upward."""
    xml_content = """
    <data>
        <images>
            <image path="a.jpg">
                <areas_of_interest center="(10,10)" radius="5" area="20" number="7"/>
                <areas_of_interest center="(20,20)" radius="5" area="20"/>
            </image>
            <image path="b.jpg">
                <areas_of_interest center="(30,30)" radius="5" area="20"/>
            </image>
        </images>
    </data>
    """.strip()
    xml_path = tmp_path / "partial.xml"
    with open(xml_path, "w") as f:
        f.write(xml_content)

    service = XmlService(xml_path)
    images = service.get_images()
    assert service.ensure_aoi_numbers(images) is True

    # The already-numbered AOI keeps its number.
    assert images[0]["areas_of_interest"][0]["number"] == 7
    # Unnumbered AOIs get unique numbers above the existing maximum.
    assert images[0]["areas_of_interest"][1]["number"] == 8
    assert images[1]["areas_of_interest"][0]["number"] == 9


# --------------------------------------------------------------------------- #
#  Cross-platform stored paths. A flight analyzed on a Windows ground station  #
#  is routinely reviewed on a Mac, so get_images() must not mistake a Windows  #
#  absolute path for a relative one and join it onto the result folder.        #
# --------------------------------------------------------------------------- #

def _xml_with_image_path(tmp_path, stored_path):
    xml_content = (
        '<data><settings output_dir="/o" input_dir="/i"/><images>'
        f'<image path="{stored_path}" hidden="False">'
        '<areas_of_interest center="(1,1)" radius="1" area="1"/>'
        '</image></images></data>'
    )
    xml_path = tmp_path / "ADIAT_Data.xml"
    xml_path.write_text(xml_content)
    return xml_path


def test_windows_absolute_path_is_not_joined_onto_result_folder(tmp_path):
    """Regression: "C:\\Flight1\\a.jpg" read as relative on POSIX.

    It used to be joined onto the XML's directory, yielding a path like
    "/results/C:\\Flight1\\a.jpg" -- missing for a reason unrelated to where
    the file is, and whose real filename could no longer be recovered by the
    path-recovery prompt.
    """
    xml_path = _xml_with_image_path(tmp_path, r"C:\Flight1\DJI_0042.JPG")
    images = XmlService(str(xml_path)).get_images()
    assert images[0]["path"] == r"C:\Flight1\DJI_0042.JPG"
    assert str(tmp_path) not in images[0]["path"]


def test_unc_absolute_path_is_not_joined_onto_result_folder(tmp_path):
    xml_path = _xml_with_image_path(tmp_path, r"\\nas\flights\DJI_0042.JPG")
    images = XmlService(str(xml_path)).get_images()
    assert images[0]["path"] == r"\\nas\flights\DJI_0042.JPG"


def test_relative_stored_path_still_resolves_against_xml_dir(tmp_path):
    """Backward compatibility: relative paths keep resolving as before."""
    xml_path = _xml_with_image_path(tmp_path, "sub/DJI_0042.JPG")
    images = XmlService(str(xml_path)).get_images()
    assert images[0]["path"] == os.path.join(str(tmp_path), "sub", "DJI_0042.JPG")


def test_relative_stored_path_is_normalized_not_left_with_parent_segments(tmp_path):
    """Regression: the resolved path must be comparable, not merely openable.

    add_image_to_xml stores the source image relative to the result folder, so
    a real file reads back as "../../input/DJI_0065.JPG". Joining that onto the
    XML directory produced ".../ADIAT_Results/../../input/DJI_0065.JPG", which
    opens the correct file -- so the viewer looked healthy -- but never
    compared equal to the ".../input/DJI_0065.JPG" that a scan of
    settings['input_dir'] produces for the same capture. Viewer's source-image
    list compares those two strings, so every AOI image was reported as having
    no detections and was appended to the list a second time.
    """
    results_dir = tmp_path / "output" / "ADIAT_Results"
    results_dir.mkdir(parents=True)
    xml_path = _xml_with_image_path(results_dir, "../../input/DJI_0065.JPG")

    images = XmlService(str(xml_path)).get_images()

    expected = os.path.join(str(tmp_path), "input", "DJI_0065.JPG")
    assert images[0]["path"] == expected
    assert ".." not in images[0]["path"]
    # The original spelling stays available for legacy cache lookups.
    assert images[0]["xml_path"] == "../../input/DJI_0065.JPG"


def test_posix_absolute_stored_path_is_unchanged(tmp_path):
    """Regression: "/Volumes/SD/a.jpg" was separator-rewritten on Windows.

    get_images() normalized '/' to os.sep before deciding whether the path was
    absolute, so a Mac-authored result file reviewed on a Windows ground
    station reported "\\Volumes\\SD\\DJI_0042.JPG" -- the mirror image of the
    Windows-path-on-POSIX bug above. Only relative paths are stored with
    forward slashes (see add_image_to_xml), so only relative paths get the
    rewrite.
    """
    xml_path = _xml_with_image_path(tmp_path, "/Volumes/SD/DJI_0042.JPG")
    images = XmlService(str(xml_path)).get_images()
    assert images[0]["path"] == "/Volumes/SD/DJI_0042.JPG"


def test_forward_slash_windows_absolute_path_is_unchanged(tmp_path):
    """An absolute path keeps its stored separators whatever they are.

    Companion to the POSIX case: the rewrite is skipped for anything absolute,
    not just for paths that are foreign to the running platform.
    """
    xml_path = _xml_with_image_path(tmp_path, "C:/Flight1/DJI_0042.JPG")
    images = XmlService(str(xml_path)).get_images()
    assert images[0]["path"] == "C:/Flight1/DJI_0042.JPG"


def test_relative_forward_slash_path_is_separator_normalized(tmp_path):
    """The rewrite must still happen for relative paths, which is why it exists.

    add_image_to_xml stores result-relative paths with '/' for portability, so
    reading one back has to produce a native path.
    """
    xml_path = _xml_with_image_path(tmp_path, "sub/deeper/DJI_0042.JPG")
    images = XmlService(str(xml_path)).get_images()
    assert images[0]["path"] == os.path.join(
        str(tmp_path), "sub", "deeper", "DJI_0042.JPG"
    )
    assert "/" not in images[0]["path"].replace(str(tmp_path), "")


def test_xml_path_attribute_preserved_for_legacy_cache_lookups(tmp_path):
    """'xml_path' must keep the raw stored string regardless of resolution."""
    xml_path = _xml_with_image_path(tmp_path, r"C:\Flight1\DJI_0042.JPG")
    images = XmlService(str(xml_path)).get_images()
    assert images[0]["xml_path"] == r"C:\Flight1\DJI_0042.JPG"
