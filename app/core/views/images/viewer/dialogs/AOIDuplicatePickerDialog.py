"""
AOIDuplicatePickerDialog - Choose which AOI the selected AOI is a duplicate of.

Opened by the D key (or "Mark as Duplicate..." on an AOI's right-click menu).
Shows the AOI being marked beside its likely primaries - flagged AOIs and AOIs
that already have duplicates - ranked best match first. The best match is
selected, so a single Enter confirms it; double-clicking a tile picks that one.
"""

import numpy as np
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QImage, QPainter, QPixmap
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QListWidgetItem

from core.views.images.viewer.ui.AOIDuplicatePickerDialog_ui import Ui_AOIDuplicatePickerDialog
from helpers.TranslationMixin import TranslationMixin

FEET_PER_METER = 3.28084
THUMBNAIL_SIZE = 150


def _to_pixmap(thumbnail):
    """RGB (or grayscale) uint8 array -> QPixmap, or None."""
    if thumbnail is None:
        return None
    array = np.ascontiguousarray(thumbnail, dtype=np.uint8)
    if array.ndim == 2:
        height, width = array.shape
        image = QImage(array.tobytes(), width, height, width, QImage.Format_Grayscale8).copy()
    elif array.ndim == 3 and array.shape[2] == 3:
        height, width = array.shape[:2]
        image = QImage(array.tobytes(), width, height, 3 * width, QImage.Format_RGB888).copy()
    else:
        return None
    pixmap = QPixmap.fromImage(image)
    return None if pixmap.isNull() else pixmap


def _with_caption_strip(pixmap, text):
    """Copy of *pixmap* with *text* on a dark strip along its bottom edge."""
    if not text:
        return pixmap
    annotated = QPixmap(pixmap)
    painter = QPainter(annotated)
    try:
        font = QFont()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        strip_height = painter.fontMetrics().height() + 6
        strip = QRect(0, annotated.height() - strip_height, annotated.width(), strip_height)
        painter.fillRect(strip, QColor(0, 0, 0, 170))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(strip, Qt.AlignCenter, text)
    finally:
        painter.end()
    return annotated


class AOIDuplicatePickerDialog(TranslationMixin, QDialog, Ui_AOIDuplicatePickerDialog):
    """Pick the primary AOI that the selected AOI repeats."""

    def __init__(self, parent=None, source=None, candidates=None, distance_unit='m'):
        """
        Args:
            parent: Parent widget.
            source (dict): The AOI being marked: 'number', 'image_name' and
                'thumbnail' (RGB array or None).
            candidates (list): Dicts with 'candidate' (AOIDuplicateService.
                DuplicateCandidate) and 'thumbnail', best match first.
            distance_unit (str): 'm' or 'ft'.
        """
        super().__init__(parent)
        self.setupUi(self)
        self._apply_translations()
        self.distance_unit = 'ft' if distance_unit == 'ft' else 'm'
        self._candidates = list(candidates or [])

        self.ok_button = self.buttonBox.button(QDialogButtonBox.Ok)
        self.ok_button.setText(self.tr("Mark as Duplicate"))

        self._show_source(source or {})
        self._populate_candidates()

        self.candidateList.itemDoubleClicked.connect(lambda _item: self.accept())
        self.candidateList.currentRowChanged.connect(self._update_ok_button)
        if self._candidates:
            self.candidateList.setCurrentRow(0)
            self.candidateList.setFocus()
        self._update_ok_button()

    def selected_candidate(self):
        """The chosen DuplicateCandidate, or None."""
        row = self.candidateList.currentRow()
        if 0 <= row < len(self._candidates):
            return self._candidates[row]['candidate']
        return None

    def candidate_text(self, candidate):
        """Caption under a candidate tile: AOI number, then image name.

        Icon-mode list items show two caption lines, so the match details go
        on the thumbnail itself (see candidate_details).
        """
        number_line = (self.tr("AOI #{number}").format(number=candidate.number)
                       if candidate.number is not None else self.tr("AOI"))
        if candidate.duplicate_count:
            number_line += " " + self.tr("(+{count} dup.)").format(count=candidate.duplicate_count)
        return "\n".join([number_line, candidate.image_name])

    def candidate_details(self, candidate):
        """Why a candidate ranks where it does: '6 m away · 91% alike' ('' if unknown)."""
        details = []
        if candidate.distance_m is not None:
            if self.distance_unit == 'ft':
                details.append(self.tr("{distance:.0f} ft away").format(
                    distance=candidate.distance_m * FEET_PER_METER))
            else:
                details.append(self.tr("{distance:.0f} m away").format(distance=candidate.distance_m))
        if candidate.similarity is not None:
            details.append(self.tr("{similarity}% alike").format(similarity=candidate.similarity))
        return " \u00b7 ".join(details)

    def _show_source(self, source):
        pixmap = _to_pixmap(source.get('thumbnail'))
        if pixmap is not None:
            self.sourceThumbnailLabel.setPixmap(
                pixmap.scaled(THUMBNAIL_SIZE, THUMBNAIL_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        number = source.get('number')
        caption = self.tr("AOI #{number}").format(number=number) if number is not None else ""
        image_name = source.get('image_name') or ""
        self.sourceCaptionLabel.setText("\n".join(part for part in (caption, image_name) if part))

    def _populate_candidates(self):
        for entry in self._candidates:
            candidate = entry['candidate']
            item = QListWidgetItem(self.candidate_text(candidate))
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignTop)
            details = self.candidate_details(candidate)
            if details:
                item.setToolTip(details)
            pixmap = _to_pixmap(entry.get('thumbnail'))
            if pixmap is not None:
                pixmap = _with_caption_strip(
                    pixmap.scaled(THUMBNAIL_SIZE, THUMBNAIL_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                    details)
                icon = QIcon(pixmap)
                # Keep the selected tile untinted: it is the one being compared
                icon.addPixmap(pixmap, QIcon.Selected)
                item.setIcon(icon)
            self.candidateList.addItem(item)

    def _update_ok_button(self, *_):
        self.ok_button.setEnabled(self.selected_candidate() is not None)
