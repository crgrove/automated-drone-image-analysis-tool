"""Tests for KMLGeneratorService POD GroundOverlay support and KMZ saving."""

import zipfile

import pytest

from core.services.export.KMLGeneratorService import KMLGeneratorService

BOX = {"north": 30.66, "south": 30.65, "east": -97.95, "west": -97.96}


@pytest.fixture
def overlay_png(tmp_path):
    """A tiny RGBA PNG standing in for the reprojected POD render."""
    from PIL import Image

    path = tmp_path / "pod_overlay.png"
    Image.new("RGBA", (4, 4), (255, 0, 0, 128)).save(path)
    return str(path)


def test_add_pod_overlay_sets_latlonbox_and_href(overlay_png):
    svc = KMLGeneratorService()
    overlay = svc.add_pod_overlay(overlay_png, BOX, name="POD Coverage",
                                  description="desc", href="pod/pod_overlay.png")
    assert float(overlay.latlonbox.north) == BOX["north"]
    assert float(overlay.latlonbox.south) == BOX["south"]
    assert float(overlay.latlonbox.east) == BOX["east"]
    assert float(overlay.latlonbox.west) == BOX["west"]
    assert overlay.icon.href == "pod/pod_overlay.png"


def test_save_kml_writes_groundoverlay_with_relative_href(tmp_path, overlay_png):
    svc = KMLGeneratorService()
    svc.add_pod_overlay(overlay_png, BOX, href="pod/pod_overlay.png")
    out = tmp_path / "export.kml"
    svc.save_kml(str(out))

    text = out.read_text(encoding="utf-8")
    assert "<GroundOverlay" in text
    assert "pod/pod_overlay.png" in text
    assert f"<north>{BOX['north']}</north>" in text


def test_save_kmz_packs_overlay_image(tmp_path, overlay_png):
    """A .kmz save must be self-contained: doc.kml + the packed PNG."""
    svc = KMLGeneratorService()
    svc.add_pod_overlay(overlay_png, BOX, packed=True)
    out = tmp_path / "export.kmz"
    svc.save_kml(str(out))

    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
        assert "doc.kml" in names
        packed = [n for n in names if n.endswith("pod_overlay.png")]
        assert packed, f"overlay PNG not packed; contents: {names}"
        doc = zf.read("doc.kml").decode("utf-8")
        assert "<GroundOverlay" in doc
        assert packed[0] in doc


def test_save_kml_extension_dispatch(tmp_path, overlay_png):
    """.kml stays plain XML (openable as text), .kmz is a zip archive."""
    svc = KMLGeneratorService()
    svc.add_pod_overlay(overlay_png, BOX, href="x.png")

    kml_out = tmp_path / "plain.kml"
    svc.save_kml(str(kml_out))
    assert kml_out.read_bytes().lstrip().startswith(b"<?xml")

    kmz_out = tmp_path / "packed.KMZ"   # case-insensitive dispatch
    svc.save_kml(str(kmz_out))
    assert zipfile.is_zipfile(kmz_out)
