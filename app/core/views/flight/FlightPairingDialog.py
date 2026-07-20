"""Pairing dialog for adding a Flight Viewer feed.

Per plan §4 *Adding a feed*, this dialog walks a single feed through:

* ``awaiting-code`` — user types the 6-character pairing code.
* ``negotiating``   — ICE/DTLS in progress; controller is responsible.
* ``failed``        — terminal; user can dismiss and retry.

The dialog is a pure UI surface. Lifecycle (signaling, peer connection,
DTLS handshake) lives in :class:`~core.controllers.flight.\
FlightTileController.FlightTileController`, which constructs and drives
this dialog. Decoupling lets us spawn multiple dialogs in parallel for
multi-feed IC workflow.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog

from core.services.streaming.signaling import pairing
from core.views.flight.flight_pairing_ui import Ui_FlightPairingDialog
from helpers.TranslationMixin import TranslationMixin


# QStackedWidget page indexes (matches ``flight_pairing.ui`` order).
PAGE_CODE_ENTRY = 0
PAGE_NEGOTIATING = 1
PAGE_FAILED = 2


class FlightPairingDialog(TranslationMixin, QDialog, Ui_FlightPairingDialog):
    """UI for the per-feed pairing handshake.

    Signals are designed for one-shot use: a controller spawns this dialog,
    binds the signals, then disposes of the dialog when it closes.
    """

    codeSubmitted = Signal(str)
    cancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.codeEdit.setFocus()
        self._set_page(PAGE_CODE_ENTRY)

        self.codeEdit.textChanged.connect(self._on_code_changed)
        self.codeEdit.returnPressed.connect(self._on_connect_clicked)
        self.connectButton.clicked.connect(self._on_connect_clicked)
        self.cancelButton.clicked.connect(self._on_cancel_clicked)

        self._update_connect_enabled()

    # ------------------------------------------------------------------
    # page transitions
    # ------------------------------------------------------------------

    def _set_page(self, idx: int) -> None:
        self.stateStack.setCurrentIndex(idx)
        # Connect button is only meaningful on the code-entry page.
        self.connectButton.setVisible(idx == PAGE_CODE_ENTRY)
        if idx == PAGE_FAILED:
            self.cancelButton.setText(self.tr("Close"))
        else:
            self.cancelButton.setText(self.tr("Cancel"))

    def show_negotiating(self, detail: Optional[str] = None) -> None:
        """Move to the negotiating page; called by controller."""
        if detail:
            self.negotiatingDetail.setText(detail)
        self._set_page(PAGE_NEGOTIATING)

    def show_failed(self, message: str) -> None:
        """Move to the failed page with ``message``; dialog stays open."""
        self.failedDetail.setText(message)
        self._set_page(PAGE_FAILED)

    def show_cap_hint(self, current: int, limit: int) -> None:
        """M2 helper: render the "drone has 2/3 viewers" hint per plan §4."""
        self.capHintLabel.setText(
            self.tr("drone has {current}/{limit} viewers").format(
                current=current, limit=limit
            )
        )

    def show_trust_hint(self, trusted: bool) -> None:
        """M3 TOFU hint: tell the operator whether this publisher is recognised.

        Routed through ``capHintLabel`` so the message stays visible at the
        bottom of the dialog without growing the .ui file.
        """
        if trusted:
            self.capHintLabel.setText(
                self.tr("known device — same fingerprint as last pair")
            )
        else:
            self.capHintLabel.setText(self.tr("new device"))

    def clear_error(self) -> None:
        """Reset the inline code-entry error label."""
        self.codeErrorLabel.setText("")

    def show_code_error(self, message: str) -> None:
        """Inline error under the code field; stays on the code-entry page."""
        self.codeErrorLabel.setText(message)
        self._set_page(PAGE_CODE_ENTRY)

    # ------------------------------------------------------------------
    # signal plumbing
    # ------------------------------------------------------------------

    def _on_code_changed(self, text: str) -> None:
        upper = text.upper()
        if upper != text:
            self.codeEdit.blockSignals(True)
            cursor_pos = self.codeEdit.cursorPosition()
            self.codeEdit.setText(upper)
            self.codeEdit.setCursorPosition(cursor_pos)
            self.codeEdit.blockSignals(False)
        self.codeErrorLabel.setText("")
        self._update_connect_enabled()

    def _update_connect_enabled(self) -> None:
        text = self.codeEdit.text().strip()
        # Accept anything plausible up to the max length; final validation
        # happens in ``pairing.normalize_pairing_code`` below.
        self.connectButton.setEnabled(bool(text))

    def _on_connect_clicked(self) -> None:
        try:
            code = pairing.normalize_pairing_code(self.codeEdit.text())
        except ValueError as exc:
            self.show_code_error(str(exc))
            return
        self.codeSubmitted.emit(code)

    def _on_cancel_clicked(self) -> None:
        self.cancelled.emit()
        self.reject()

    # ------------------------------------------------------------------
    # accessors
    # ------------------------------------------------------------------

    @property
    def submitted_code(self) -> str:
        try:
            return pairing.normalize_pairing_code(self.codeEdit.text())
        except ValueError:
            return self.codeEdit.text().strip().upper()
