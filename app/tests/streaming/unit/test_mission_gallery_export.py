"""Unit tests for the Mission Gallery export path (plan §15 M3)."""

from __future__ import annotations

import os
import sys
import tempfile
import xml.etree.ElementTree as ET

import pytest
from PySide6.QtWidgets import QApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.controllers.flight import MissionGalleryController  # noqa: E402
from core.views.flight.MissionGalleryDock import MissionGalleryDock  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _detection(track_key: str, *, lat: float, lon: float, thumb=b"\xff\xd8\xff\xe0fakejpeg"):
    return {
        "track_key": track_key,
        "feed_id": "ABC234",
        "feed_label": "Tile-ABC234",
        "class_name": "person",
        "confidence": 0.87,
        "captured_at_ms": 1737310912345,
        "location": {"lat": lat, "lon": lon},
        "bbox_norm": [0.4, 0.5, 0.1, 0.2],
        "thumb_bytes": thumb,
    }


def test_export_writes_xml_and_thumbnails(qapp, tmp_path) -> None:
    dock = MissionGalleryDock()
    controller = MissionGalleryController(dock)
    dock.register_feed("ABC234", "Tile-ABC234")
    controller.add_detection("ABC234", _detection("t1", lat=30.1, lon=-97.5))
    controller.add_detection("ABC234", _detection("t2", lat=30.2, lon=-97.6))

    xml_path = controller._write_export(str(tmp_path), controller.detections)

    # XML file exists at the expected location.
    assert os.path.exists(xml_path)
    assert os.path.basename(xml_path) == "ADIAT_Data.xml"

    # Two thumbnails written.
    files = sorted(os.listdir(tmp_path))
    assert "detection_0000.jpg" in files
    assert "detection_0001.jpg" in files

    # XML schema matches the image-mode loader's expectations.
    tree = ET.parse(xml_path)
    root = tree.getroot()
    assert root.tag == "data"
    images = root.find("images")
    assert images is not None
    image_elems = images.findall("image")
    assert len(image_elems) == 2
    for image in image_elems:
        aois = image.findall("areas_of_interest")
        assert len(aois) == 1
        aoi = aois[0]
        # Required attributes for the image-mode viewer.
        assert aoi.get("center")
        assert aoi.get("radius")
        assert aoi.get("area")
        # GPS coordinates surface in the user_comment field.
        comment = aoi.get("user_comment", "")
        assert "GPS:" in comment


def test_export_handles_thumb_less_detections(qapp, tmp_path) -> None:
    """A detection without thumb_bytes still gets a placeholder image."""
    dock = MissionGalleryDock()
    controller = MissionGalleryController(dock)
    dock.register_feed("ABC234", "Tile-ABC234")
    detection = _detection("t1", lat=30.1, lon=-97.5, thumb=None)
    controller.add_detection("ABC234", detection)

    controller._write_export(str(tmp_path), controller.detections)

    # Placeholder JPEG written and non-empty (1x1 baseline JPEG, ~125 bytes).
    placeholder = os.path.join(tmp_path, "detection_0000.jpg")
    assert os.path.exists(placeholder)
    assert os.path.getsize(placeholder) > 0
    # Standard JPEG SOI marker.
    with open(placeholder, "rb") as fp:
        head = fp.read(2)
    assert head == b"\xff\xd8"


def test_build_aoi_falls_back_when_bbox_missing(qapp) -> None:
    aoi = MissionGalleryController._build_aoi({"class_name": "person", "confidence": 0.7})
    assert aoi["center"] == (128, 128)
    assert aoi["radius"] >= 8
    assert aoi["confidence"] == 0.7


def test_build_aoi_includes_user_comment_with_gps(qapp) -> None:
    detection = {
        "class_name": "person",
        "confidence": 0.8,
        "location": {"lat": 30.1234, "lon": -97.5678},
    }
    aoi = MissionGalleryController._build_aoi(detection)
    assert "30.1234" in aoi["user_comment"]
    assert "-97.5678" in aoi["user_comment"]
    assert "person" in aoi["user_comment"]
