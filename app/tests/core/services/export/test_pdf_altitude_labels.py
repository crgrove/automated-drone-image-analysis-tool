"""The PDF report must name each altitude's reference plane in full.

A printed report is the one export read entirely outside ADIAT: no tooltip,
no status bar, no way to ask what plane a number is measured from. CLAUDE.md
2.11 therefore groups it with KML and CalTopo as a surface that spells the
plane out - and it was the odd one out, emitting the tight-UI abbreviation
("ATO: 171.0 ft") and a bare hardcoded "AGL:" for the DEM-derived value.

The metadata line is exercised through ``_altitude_metadata`` rather than by
generating a PDF: everything else on that line needs a real image on disk,
and the label contract is what this file is about.
"""

from unittest.mock import MagicMock

import pytest

from core.services.export.PdfGeneratorService import PdfGeneratorService
from core.services.image.ImageService import AltitudeReadings
from helpers.FormatHelper import FormatHelper


@pytest.fixture
def service():
    viewer = MagicMock()
    viewer.distance_unit = 'ft'
    viewer.use_terrain_elevation = True
    return PdfGeneratorService(viewer)


def test_a_dji_altitude_names_the_takeoff_point(service):
    text = service._altitude_metadata(AltitudeReadings(
        value=171.0, unit='ft',
        reference=FormatHelper.ALTITUDE_REFERENCE_TAKEOFF))

    # The value/unit spacing is _report_value's existing shape and not
    # what this file is about; the plane name is.
    assert 'ATO (above the takeoff point): 171.0ft' in text
    # The bare abbreviation is what a reader outside ADIAT cannot decode.
    assert 'ATO: ' not in text


def test_a_terrain_referenced_altitude_names_the_terrain(service):
    """WALDO-prepassed imagery really is height above the terrain."""
    text = service._altitude_metadata(AltitudeReadings(
        value=95.0, unit='ft',
        reference=FormatHelper.ALTITUDE_REFERENCE_TERRAIN))

    assert 'AGL (above the terrain): 95.0ft' in text


def test_an_operator_override_says_who_entered_it(service):
    text = service._altitude_metadata(AltitudeReadings(
        value=250.0, unit='ft',
        reference=FormatHelper.ALTITUDE_REFERENCE_MANUAL))

    assert 'AGL (operator-entered): 250.0ft' in text


def test_the_dem_agl_is_spelled_out_and_leads(service):
    """Worded as KML and CalTopo word it, and first - the reader of a report
    cannot see the launch point, so ground clearance is the useful number."""
    text = service._altitude_metadata(AltitudeReadings(
        value=171.0, unit='ft', terrain_agl=71.4,
        reference=FormatHelper.ALTITUDE_REFERENCE_TAKEOFF))

    assert 'AGL (above the terrain, from DEM): 71.4ft' in text
    assert 'ATO (above the takeoff point): 171.0ft' in text
    assert (text.index('AGL (above the terrain')
            < text.index('ATO (above the takeoff'))


def test_no_dem_agl_means_no_agl_claim(service):
    """The DEM could not answer for this position. Saying nothing is right;
    reporting the ATO figure under an AGL label is the error the three-plane
    split exists to prevent."""
    text = service._altitude_metadata(AltitudeReadings(
        value=171.0, unit='ft',
        reference=FormatHelper.ALTITUDE_REFERENCE_TAKEOFF))

    assert 'AGL' not in text


def test_a_missing_altitude_reads_as_not_available(service):
    """Formatting None with its unit printed "AGL: Noneft" in the report."""
    text = service._altitude_metadata(AltitudeReadings(
        value=None, unit='ft',
        reference=FormatHelper.ALTITUDE_REFERENCE_TAKEOFF))

    assert 'None' not in text
    assert 'N/A' in text
