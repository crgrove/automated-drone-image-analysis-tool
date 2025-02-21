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
    assert settings["min_area"] == 0  # Ensure defaults are set correctly


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
