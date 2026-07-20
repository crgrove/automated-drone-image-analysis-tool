from algorithms.images.MRMap.controllers.MRMapController import MRMapController


def _config():
    return {
        'name': 'MRMap',
        'label': 'MRMap',
        'controller': 'MRMapController',
        'wizard_controller': 'MRMapWizardController',
        'service': 'MRMapService',
        'combine_overlapping_aois': True,
        'platforms': ['Windows', 'Linux', 'Darwin'],
        'type': 'RGB'
    }


def test_colorspace_combo_popup_width_fits_items(app, qtbot):
    controller = MRMapController(_config(), 'Dark')
    qtbot.addWidget(controller)

    combo_box = controller.colorspaceComboBox
    view = combo_box.view()
    model = combo_box.model()
    widest_item = max(
        view.sizeHintForIndex(model.index(row, combo_box.modelColumn())).width()
        for row in range(combo_box.count())
    )

    assert combo_box.minimumWidth() >= combo_box.minimumSizeHint().width()
    assert view.minimumWidth() >= widest_item + 24
