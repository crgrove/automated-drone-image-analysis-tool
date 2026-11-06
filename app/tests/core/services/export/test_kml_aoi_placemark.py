"""Tests for KMLGeneratorService.add_aoi_placemark."""

import os
import xml.etree.ElementTree as ET

from core.services.export.KMLGeneratorService import KMLGeneratorService

_KML = '{http://www.opengis.net/kml/2.2}'


def _saved_root(service, tmp_path):
    target = os.path.join(str(tmp_path), "aois.kml")
    service.save_kml(target)
    return ET.parse(target).getroot()


class TestAddAoiPlacemark:
    """AOI points, at the document root or inside a folder."""

    def test_defaults_to_the_document_root(self, tmp_path):
        service = KMLGeneratorService(use_terrain=False)
        service.add_aoi_placemark("IMG_1 - AOI 1", 30.0, -97.0, "found", (255, 0, 0))

        document = _saved_root(service, tmp_path).find(f'{_KML}Document')

        placemark = document.find(f'{_KML}Placemark')
        assert placemark.find(f'{_KML}name').text == "IMG_1 - AOI 1"
        assert document.find(f'{_KML}Folder') is None

    def test_goes_into_the_given_folder(self, tmp_path):
        service = KMLGeneratorService(use_terrain=False)
        folder = service.kml.newfolder(name="1. Flight1")
        service.add_aoi_placemark("[1] IMG_1 - AOI 1", 30.0, -97.0, "found", folder=folder)

        document = _saved_root(service, tmp_path).find(f'{_KML}Document')

        assert document.find(f'{_KML}Placemark') is None
        saved_folder = document.find(f'{_KML}Folder')
        assert saved_folder.find(f'{_KML}name').text == "1. Flight1"
        assert saved_folder.find(f'{_KML}Placemark/{_KML}name').text == "[1] IMG_1 - AOI 1"
