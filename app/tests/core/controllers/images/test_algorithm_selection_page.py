from unittest.mock import MagicMock, patch

from core.controllers.images.guidePages.AlgorithmSelectionPage import AlgorithmSelectionPage


class _DummyWidget:
    def __init__(self):
        self.visible = True
        self.style = ""

    def setVisible(self, visible):
        self.visible = visible

    def setStyleSheet(self, style):
        self.style = style


class _DummyLabel(_DummyWidget):
    def __init__(self):
        super().__init__()
        self._text = ""

    def setText(self, text):
        self._text = text

    def text(self):
        return self._text


class _DummyDialog:
    def __init__(self):
        self.labelCurrentQuestion = _DummyLabel()
        self.labelAlgorithmResult = _DummyLabel()
        self.buttonYes = _DummyWidget()
        self.buttonNo = _DummyWidget()
        self.resetAlgorithmButton = _DummyWidget()


def _create_page():
    wizard_data = {}
    settings_service = MagicMock()
    dialog = _DummyDialog()
    page = AlgorithmSelectionPage(wizard_data, settings_service, dialog)
    # The thermal branch is Windows-only: on Darwin _reset_algorithm_selection
    # pre-answers "not thermal", so these tests would walk the RGB tree.
    with patch("core.controllers.images.guidePages.AlgorithmSelectionPage.platform.system", return_value="Windows"):
        page.setup_ui()
    return page, wizard_data, dialog


def test_thermal_anomaly_branch_prompts_for_detector_choice():
    page, _, dialog = _create_page()

    page._on_algorithm_answer(True)   # Thermal imagery
    page._on_algorithm_answer(False)  # Not temperature range

    assert page.selected_algorithm is None
    assert "local surroundings" in dialog.labelCurrentQuestion.text().lower()


def test_thermal_anomaly_branch_can_select_residual_detector():
    page, wizard_data, _ = _create_page()

    page._on_algorithm_answer(True)   # Thermal imagery
    page._on_algorithm_answer(False)  # Not temperature range
    page._on_algorithm_answer(True)   # Use local residual detector

    # The stable algorithms.conf name, not the display label: the wizard
    # hands this to MainWindow, which looks it up in the config.
    assert page.selected_algorithm == "ThermalResidualAnomaly"
    assert wizard_data.get('algorithm') == "ThermalResidualAnomaly"


def test_thermal_anomaly_branch_can_select_standard_detector():
    page, wizard_data, _ = _create_page()

    page._on_algorithm_answer(True)   # Thermal imagery
    page._on_algorithm_answer(False)  # Not temperature range
    page._on_algorithm_answer(False)  # Use standard detector

    assert page.selected_algorithm == "ThermalAnomaly"
    assert wizard_data.get('algorithm') == "ThermalAnomaly"


def test_the_selection_is_shown_by_its_display_name():
    """The operator reads a label; the wizard carries a key. Interpolating
    the key into the sentence rendered "Algoritmo seleccionado:
    ThermalResidualAnomaly" - and interpolating the English label rendered
    the English label in every locale."""
    page, wizard_data, dialog = _create_page()

    page._on_algorithm_answer(True)
    page._on_algorithm_answer(False)
    page._on_algorithm_answer(True)

    shown = dialog.labelAlgorithmResult.text()
    assert "Temperature Residual Anomaly" in shown
    assert "ThermalResidualAnomaly" not in shown
    # ...and the key is still what travels onward.
    assert wizard_data['algorithm'] == "ThermalResidualAnomaly"


def test_every_decision_tree_outcome_names_a_real_algorithm():
    """A key the config does not know is a dead end: MainWindow looks the
    wizard's value up in algorithms.conf and would keep its current
    algorithm instead. The outcomes are read out of the page's own source so
    a branch added later is covered without editing this list."""
    import ast
    import inspect
    import json
    import os

    import core.controllers.images.guidePages.AlgorithmSelectionPage as module

    source = inspect.getsource(module)
    tree = ast.parse(source)
    outcomes = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if (isinstance(target, ast.Attribute)
                and target.attr == 'selected_algorithm'
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)):
            outcomes.add(node.value.value)

    assert len(outcomes) == 9, outcomes

    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))))),
        'algorithms.conf')
    with open(config_path, encoding='utf-8') as handle:
        known = {a['name'] for a in json.load(handle)['algorithms']}

    assert outcomes <= known, outcomes - known

    # And each has a display name, so no key is ever shown to the operator.
    # MRMap's happens to read the same either way; the point is that the
    # mapping covers it deliberately rather than falling through.
    page, _wizard_data, _dialog = _create_page()
    for name in outcomes:
        assert name in page._display_name_map()
