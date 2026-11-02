"""Unit tests for CombinedCalTopoExportController."""

from unittest.mock import MagicMock, patch

import pytest

from core.controllers.images.exports.CombinedCalTopoExportController import (
    CombinedCalTopoExportController,
)
from core.controllers.images.viewer.exports.CalTopoExportController import CalTopoExportController

_BASE_MODULE = "core.controllers.images.viewer.exports.CalTopoExportController"


def _run(name, images, identifier_color=None, duplicate_sightings=None):
    run = MagicMock()
    run.run_name = name
    run.images = images
    run.settings = {} if identifier_color is None else {'identifier_color': identifier_color}
    run.duplicate_sightings = duplicate_sightings or {}
    return run


def _image(name, aoi_count):
    return {'path': f'/missions/{name}', 'name': name,
            'areas_of_interest': [{'center': (i, i)} for i in range(aoi_count)]}


@pytest.fixture
def runs():
    return [
        _run("Flight1", [_image('a.jpg', 2)], identifier_color=(255, 0, 255),
             duplicate_sightings={1: ['first']}),
        _run("Flight2", [_image('a.jpg', 1), _image('b.jpg', 1)], identifier_color=(0, 255, 0),
             duplicate_sightings={1: ['second']}),
    ]


@pytest.fixture
def controller(runs):
    with patch(f"{_BASE_MODULE}.CalTopoService"), \
            patch(f"{_BASE_MODULE}.CalTopoAPIService"), \
            patch(f"{_BASE_MODULE}.CalTopoCredentialHelper"):
        return CombinedCalTopoExportController(
            MagicMock(spec=['settings_service']), runs, use_terrain_elevation=False,
            logger=MagicMock())


def test_images_are_flattened_with_report_names(controller):
    assert [img['name'] for img in controller.images] == ['[1] a.jpg', '[2] a.jpg', '[2] b.jpg']
    assert controller.flagged_aois == {0: [0, 1], 1: [0], 2: [0]}


@pytest.mark.parametrize('method, entry_point', [
    ('api', 'export_to_caltopo_via_api'),
    ('browser', 'export_to_caltopo'),
])
def test_export_detections_sends_flagged_aois_with_report_photos(controller, method, entry_point):
    with patch.object(CombinedCalTopoExportController, entry_point, return_value=True) as export:
        assert controller.export_detections(method, include_photos=True) is True

    args = export.call_args
    assert args.args == (controller.images, controller.flagged_aois)
    assert args.kwargs == {
        'include_flagged_aois': True,
        'include_locations': False,
        'include_images_without_flagged_aois': False,
        'include_coverage_area': False,
        'include_images': True,
        'aoi_photo_mode': 'full',
    }


def test_export_detections_can_skip_photos(controller):
    with patch.object(CombinedCalTopoExportController, 'export_to_caltopo', return_value=True) as export:
        controller.export_detections('browser', include_photos=False)
    assert export.call_args.kwargs['include_images'] is False


def test_prepare_markers_runs_each_run_with_its_own_settings(controller, runs):
    seen = []

    def base_prepare(self, images, flagged_aois, include_images=True, aoi_photo_mode='full'):
        seen.append({
            'names': [img['name'] for img in images],
            'flagged': flagged_aois,
            'color': self._identifier_color(),
            'sightings': self._duplicate_sightings(images),
            'terrain': self._use_terrain(),
        })
        return [f"marker-{len(seen)}"]

    with patch.object(CalTopoExportController, '_prepare_markers', base_prepare):
        markers = controller._prepare_markers(
            controller.images, controller.flagged_aois, include_images=True, aoi_photo_mode='full')

    assert markers == ['marker-1', 'marker-2']
    assert seen[0] == {'names': ['[1] a.jpg'], 'flagged': {0: [0, 1]}, 'color': (255, 0, 255),
                       'sightings': {1: ['first']}, 'terrain': False}
    assert seen[1]['names'] == ['[2] a.jpg', '[2] b.jpg']
    assert seen[1]['flagged'] == {0: [0], 1: [0]}  # re-based to the run's own slice
    assert seen[1]['color'] == (0, 255, 0)
    assert seen[1]['sightings'] == {1: ['second']}
    assert controller._active_run is None


def test_prepare_markers_clears_the_active_run_on_error(controller):
    def failing_prepare(self, *args, **kwargs):
        raise RuntimeError("boom")

    with patch.object(CalTopoExportController, '_prepare_markers', failing_prepare):
        with pytest.raises(RuntimeError):
            controller._prepare_markers(controller.images, controller.flagged_aois)
    assert controller._active_run is None


def test_hooks_fall_back_outside_a_run(controller):
    assert controller._identifier_color() == (255, 255, 0)
    with patch(f"{_BASE_MODULE}.AOIDuplicateService.sightings_by_primary", return_value={'x': 1}):
        assert controller._duplicate_sightings([]) == {'x': 1}


def test_run_without_identifier_color_uses_the_default(controller, runs):
    runs[0].settings = {}
    controller._active_run = runs[0]
    assert controller._identifier_color() == (255, 255, 0)
