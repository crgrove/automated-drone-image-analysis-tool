from unittest.mock import MagicMock

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

    assert page.selected_algorithm == "Temperature Residual Anomaly"
    assert wizard_data.get('algorithm') == "Temperature Residual Anomaly"


def test_thermal_anomaly_branch_can_select_standard_detector():
    page, wizard_data, _ = _create_page()

    page._on_algorithm_answer(True)   # Thermal imagery
    page._on_algorithm_answer(False)  # Not temperature range
    page._on_algorithm_answer(False)  # Use standard detector

    assert page.selected_algorithm == "Temperature Anomaly"
    assert wizard_data.get('algorithm') == "Temperature Anomaly"
