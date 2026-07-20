"""Tests for Viewer._backfill_image_dimensions_if_needed.

Regression coverage for the "stuck on Checking image dimensions" bug: the
always-on-top ResultsLoadingDialog hid the modal "Update Image Dimensions"
question box, so the app appeared frozen during a results-file open. The
method must hide the loading dialog before showing the modal prompt and
restore it afterwards.
"""

from unittest.mock import MagicMock, patch

import pytest

from core.controllers.images.viewer.Viewer import Viewer


@pytest.fixture
def stub_viewer():
    """Lightweight stand-in for a Viewer (the real __init__ is too heavy)."""
    viewer = MagicMock()
    viewer.tr = lambda s: s
    viewer.images = [
        {'path': 'a.jpg', 'width': None, 'height': None, 'xml': MagicMock()},
        {'path': 'b.jpg', 'width': 640, 'height': 480, 'xml': MagicMock()},
    ]
    viewer.xml_service = MagicMock()
    viewer.xml_path = 'results.xml'
    viewer._loading_dialog = MagicMock()
    return viewer


def test_no_missing_dimensions_returns_early(stub_viewer):
    """When every image already has dimensions, no prompt is shown."""
    for img in stub_viewer.images:
        img['width'], img['height'] = 100, 100

    with patch.object(Viewer, '__init__', return_value=None), \
            patch('core.controllers.images.viewer.Viewer.QMessageBox') as msg_box:
        Viewer._backfill_image_dimensions_if_needed(stub_viewer)

    msg_box.question.assert_not_called()
    stub_viewer._loading_dialog.hide.assert_not_called()
    stub_viewer.xml_service.save_xml_file.assert_not_called()


def test_loading_dialog_hidden_before_modal_prompt(stub_viewer):
    """The always-on-top loading dialog must be hidden while the modal is up."""
    call_order = []
    stub_viewer._loading_dialog.hide.side_effect = lambda: call_order.append('hide')
    stub_viewer._loading_dialog.show.side_effect = lambda: call_order.append('show')

    with patch('core.controllers.images.viewer.Viewer.QMessageBox') as msg_box:
        msg_box.Yes = 1
        msg_box.No = 0

        def question(*args, **kwargs):
            call_order.append('question')
            return msg_box.No  # decline so we skip the PIL loop
        msg_box.question.side_effect = question

        Viewer._backfill_image_dimensions_if_needed(stub_viewer)

    # hide must precede the modal, and show must restore it afterwards.
    assert call_order == ['hide', 'question', 'show']


def test_decline_does_not_modify_or_save(stub_viewer):
    """Answering No leaves dimensions untouched and writes nothing."""
    with patch('core.controllers.images.viewer.Viewer.QMessageBox') as msg_box:
        msg_box.Yes = 1
        msg_box.No = 0
        msg_box.question.return_value = msg_box.No

        Viewer._backfill_image_dimensions_if_needed(stub_viewer)

    assert stub_viewer.images[0]['width'] is None
    stub_viewer.xml_service.save_xml_file.assert_not_called()
    # Loading dialog restored even on decline.
    stub_viewer._loading_dialog.show.assert_called_once()


def test_accept_backfills_dimensions_and_saves(stub_viewer):
    """Answering Yes reads sizes, updates dict + XML, and saves once."""
    fake_image = MagicMock()
    fake_image.size = (800, 600)
    fake_image.__enter__ = MagicMock(return_value=fake_image)
    fake_image.__exit__ = MagicMock(return_value=False)

    with patch('core.controllers.images.viewer.Viewer.QMessageBox') as msg_box, \
            patch('os.path.isfile', return_value=True), \
            patch('PIL.Image.open', return_value=fake_image):
        msg_box.Yes = 1
        msg_box.No = 0
        msg_box.question.return_value = msg_box.Yes

        Viewer._backfill_image_dimensions_if_needed(stub_viewer)

    missing = stub_viewer.images[0]
    assert missing['width'] == 800
    assert missing['height'] == 600
    missing['xml'].set.assert_any_call('width', '800')
    missing['xml'].set.assert_any_call('height', '600')
    stub_viewer.xml_service.save_xml_file.assert_called_once_with('results.xml')
