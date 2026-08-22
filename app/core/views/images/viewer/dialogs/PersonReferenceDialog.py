"""PersonReferenceDialog - perspective-projected person-size overlay.

Draws standing and recumbent (and optional sitting) person silhouettes on
the image at true perspective scale, plus the standing person's shadow.

Unlike a flat top-down silhouette scaled by GSD, the overlay is built by
projecting a 3D person model through a CameraModel derived from the image's
metadata pose. The silhouette is therefore foreshortened correctly - a
compact top-down shape near the nadir point, an upright side-on figure
toward oblique frame edges - and the shadow is cast from the real sun
position at the image's capture time.

Engine pieces:
- CameraModel       - 3D world point -> image pixel projection.
- PersonModel       - 3D point cloud for standing/sitting poses.
- PersonShadow      - casts the standing person's outline onto the ground.
- SolarPosition     - capture-time EXIF -> sun elevation/azimuth.
"""

import math

import cv2
import numpy as np

from PySide6.QtCore import Qt, QRectF, QPointF, QTimer
from PySide6.QtGui import QPen, QColor, QBrush, QPainterPath, QPolygonF
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget,
    QGroupBox, QComboBox, QSpinBox, QFormLayout, QCheckBox, QGraphicsPathItem,
    QGraphicsEllipseItem, QGraphicsItem, QGraphicsLineItem, QColorDialog,
    QApplication,
)

from helpers.TranslationMixin import TranslationMixin
from helpers.MetaDataHelper import MetaDataHelper
from helpers.LocationInfo import LocationInfo
from core.services.SettingsService import SettingsService
from core.services.LoggerService import LoggerService
from core.services.CameraModel import CameraModel
from core.services import PersonModel
from core.services.shadow.PersonShadow import compute_shadow_ground_points
from core.services.shadow.SolarPosition import (
    resolve_capture_utc, get_solar_position, SolarTimeUnresolvable,
    timezone_name_for_position,
)
from core.services.shadow.ShadowTimeSolver import solve_time_for_shadow_azimuth

# Persisted setting keys. The overlay is a recurring reference tool, so the
# user's last choices (colour, size class, which poses/shadow/terrain are on)
# are restored on the next open.
SETTING_OVERLAY_COLOR = 'PersonReferenceOverlayColor'
SETTING_SIZE_KEY = 'PersonReferenceSizeKey'
SETTING_SHOW_STANDING = 'PersonReferenceShowStanding'
SETTING_SHOW_RECUMBENT = 'PersonReferenceShowRecumbent'
SETTING_SHOW_SITTING = 'PersonReferenceShowSitting'
SETTING_SHOW_SHADOWS = 'PersonReferenceShowShadows'
SETTING_USE_TERRAIN = 'PersonReferenceUseTerrain'
DEFAULT_OVERLAY_COLOR = '#00ff00'  # bright green

# On-screen span below which the reference person is effectively invisible
# and the viewer auto-zooms to it. High-altitude fixed-wing imagery (e.g.
# WALDO tiles at ~1500m AGL / ~13cm/px) renders a person only ~15 image px
# tall, which fit zoom reduces to 2-3 screen px.
MIN_LEGIBLE_SCREEN_PX = 28
# After auto-zoom the viewport spans about this many person-heights.
AUTO_ZOOM_VIEW_SPAN = 10

# Reference size classes: key, label, standing height (inches), weight (lb).
SIZE_CLASSES = [
    ("large_adult", "Large adult",           6 * 12 + 2,  220),
    ("average_adult", "Average adult",       5 * 12 + 7,  185),
    ("small_adult", "Small adult",           5 * 12 + 2,  120),
    ("child", "Child",                       4 * 12 + 0,  50),
    ("small_child", "Small child / toddler", 3 * 12 + 0,  30),
    ("infant", "Infant",                     2 * 12 + 4,  20),
]

CM_PER_INCH = 2.54

# WGS-84 equatorial radius, for the local NED <-> lat/lon conversion used by
# the DEM terrain lookups.
EARTH_RADIUS_M = 6378137.0

# A person lying down is a low slab; this fraction of their standing height
# is the body thickness used to cast the recumbent shadow.
RECUMBENT_THICKNESS_FRACTION = 0.12

# On near-nadir imagery a standing person is drawn as a flat overhead
# footprint (no vertical layover). Beyond this many degrees off straight-down
# the camera is oblique enough that the full 3D upright figure reads correctly
# and is projected instead.
NADIR_PITCH_TOLERANCE_DEG = 15.0

# Gap (image px) between the reference person's anchor and the edge of the
# selected AOI: an anchor landing on the AOI is shifted aside by the AOI's
# radius plus this clearance, so the overlay never covers the detection it
# is being compared against.
AOI_CLEARANCE_PX = 40.0


def _build_recumbent_path(height_cm):
    """Top-down silhouette of a person lying flat.

    Built by drawing the head, body, arms, and legs as separate closed paths
    and merging them with QPainterPath.united() into a single outer outline.
    Coordinates are centimetres, centred on the origin.
    """
    h = height_cm
    cx = 0.0

    head_diam = 0.135 * h
    head_r = head_diam / 2.0

    body_half_w = 0.118 * h
    body_top_y = 0.115 * h
    body_bot_y = 0.555 * h
    neck_half_w = 0.045 * h
    neck_top_y = head_diam * 0.85

    arm_cx_offset = 0.108 * h
    arm_half_w = 0.038 * h
    arm_top_y = body_top_y + 0.010 * h
    arm_bot_y = body_bot_y + 0.005 * h

    leg_cx_offset = 0.058 * h
    thigh_half_w = 0.052 * h
    knee_half_w = 0.044 * h
    ankle_half_w = 0.034 * h
    foot_outer = 0.066 * h
    foot_inner = 0.005 * h
    hip_y = body_bot_y - 0.025 * h
    knee_y = 0.730 * h
    ankle_y = 0.955 * h
    foot_tip_y = 1.000 * h

    total_len = foot_tip_y
    y0 = -total_len / 2.0

    head = QPainterPath()
    head.addEllipse(QRectF(cx - head_r, y0, head_diam, head_diam))

    body = QPainterPath()
    body.moveTo(cx + neck_half_w, y0 + neck_top_y)
    body.cubicTo(
        cx + neck_half_w + 0.020 * h, y0 + body_top_y - 0.005 * h,
        cx + body_half_w - 0.020 * h, y0 + body_top_y,
        cx + body_half_w, y0 + body_top_y + 0.015 * h,
    )
    body.lineTo(cx + body_half_w, y0 + body_bot_y - 0.020 * h)
    body.cubicTo(
        cx + body_half_w, y0 + body_bot_y,
        cx - body_half_w, y0 + body_bot_y,
        cx - body_half_w, y0 + body_bot_y - 0.020 * h,
    )
    body.lineTo(cx - body_half_w, y0 + body_top_y + 0.015 * h)
    body.cubicTo(
        cx - body_half_w + 0.020 * h, y0 + body_top_y,
        cx - neck_half_w - 0.020 * h, y0 + body_top_y - 0.005 * h,
        cx - neck_half_w, y0 + neck_top_y,
    )
    body.closeSubpath()

    arms = []
    for sign in (1, -1):
        ax = sign * arm_cx_offset
        arm = QPainterPath()
        arm.addRoundedRect(
            QRectF(ax - arm_half_w, y0 + arm_top_y,
                   arm_half_w * 2.0, arm_bot_y - arm_top_y),
            arm_half_w, arm_half_w,
        )
        arms.append(arm)

    legs = []
    for sign in (1, -1):
        lx = sign * leg_cx_offset
        leg = QPainterPath()
        leg.moveTo(lx + sign * thigh_half_w, y0 + hip_y)
        leg.cubicTo(
            lx + sign * thigh_half_w, y0 + hip_y + 0.080 * h,
            lx + sign * knee_half_w * 1.06, y0 + knee_y - 0.040 * h,
            lx + sign * knee_half_w, y0 + knee_y,
        )
        leg.cubicTo(
            lx + sign * knee_half_w, y0 + knee_y + 0.060 * h,
            lx + sign * ankle_half_w, y0 + ankle_y - 0.060 * h,
            lx + sign * ankle_half_w, y0 + ankle_y,
        )
        leg.lineTo(lx + sign * foot_outer, y0 + foot_tip_y)
        leg.lineTo(lx + sign * foot_inner, y0 + foot_tip_y)
        leg.lineTo(lx - sign * ankle_half_w * 0.85, y0 + ankle_y)
        leg.cubicTo(
            lx - sign * ankle_half_w * 0.85, y0 + ankle_y - 0.060 * h,
            lx - sign * knee_half_w * 0.85, y0 + knee_y + 0.060 * h,
            lx - sign * knee_half_w * 0.85, y0 + knee_y,
        )
        leg.cubicTo(
            lx - sign * knee_half_w * 0.95, y0 + knee_y - 0.040 * h,
            lx - sign * thigh_half_w * 0.70, y0 + hip_y + 0.080 * h,
            lx - sign * thigh_half_w * 0.70, y0 + hip_y,
        )
        leg.closeSubpath()
        legs.append(leg)

    result = head.united(body)
    for arm in arms:
        result = result.united(arm)
    for leg in legs:
        result = result.united(leg)
    return result, total_len


class _AnchorHandle(QGraphicsEllipseItem):
    """Draggable marker for the person's ground position.

    Ignores the view transform so it stays a constant screen size; its scene
    position is the pixel the silhouettes and shadow are projected from.
    """

    def __init__(self, dialog, radius=9):
        super().__init__(-radius, -radius, 2 * radius, 2 * radius)
        self._dialog = dialog
        self.setZValue(1003)
        self.setBrush(QBrush(QColor(255, 255, 255, 200)))
        self.setPen(QPen(QColor(40, 40, 40), 2))
        self.setCursor(Qt.OpenHandCursor)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)

    def itemChange(self, change, value):
        if (change == QGraphicsItem.ItemPositionHasChanged
                and self._dialog is not None):
            self._dialog._on_anchor_moved()
        return super().itemChange(change, value)


class PersonReferenceDialog(TranslationMixin, QDialog):
    """Dialog for placing perspective-projected person silhouettes on the image."""

    def __init__(self, parent, image_viewer, image_service, image_path,
                 distance_unit, agl_override_m=None):
        """
        Args:
            parent: Parent widget (Viewer).
            image_viewer: QtImageViewer showing the current image.
            image_service: ImageService for the current image (camera pose).
            image_path: Path to the current image (EXIF capture time / GPS).
            distance_unit: 'ft' for imperial display, else metric.
            agl_override_m: Optional AGL altitude override in metres.
        """
        super().__init__(parent)
        self.logger = LoggerService()
        self._parent_viewer = parent
        self.image_viewer = image_viewer
        self.distance_unit = distance_unit

        self.size_key = SIZE_CLASSES[1][0]  # default: Average adult
        self.rotation_deg = 0  # ground heading of the reference person

        # Camera + sun state for the current image.
        self.camera = None
        self.image_path = None
        self.drone_lat = None
        self.drone_lon = None
        self.sun_elev = None
        self.sun_az = None
        self.sun_error = None
        self.sun_time_source = None

        # Shadow-trace state: the user can trace a real shadow on the image
        # (base of the caster, then shadow tip) and the solved time of day
        # overrides the - possibly wrong - camera clock for sun rendering.
        self._capture_utc = None          # resolved capture moment (UTC)
        self._trace_override_utc = None   # solved time from a traced shadow
        self._trace_active = False
        self._trace_connected = False     # click signal currently connected
        self._trace_points = []           # image-pixel clicks, base first
        self._trace_items = []            # scene items visualising the trace

        # DEM terrain state for the current image.
        self.terrain_service = None
        self.terrain_nadir_elev = None

        # Overlay color (persisted so the user only sets it once).
        self._settings_service = SettingsService()
        saved = self._settings_service.get_setting(SETTING_OVERLAY_COLOR)
        color = QColor(saved) if saved else QColor(DEFAULT_OVERLAY_COLOR)
        self.overlay_color = color if color.isValid() else QColor(DEFAULT_OVERLAY_COLOR)

        # Scene items: persistent, re-pathed on every move.
        self.anchor_item = None
        self.pose_items = {}   # 'standing'|'recumbent'|'sitting' -> QGraphicsPathItem
        self.shadow_item = None

        # Image-change rebuilds are deferred so in-flight navigation (e.g.
        # a gallery AOI click that loads the image and then zooms to the
        # AOI) lands before the person is placed - see update_for_image.
        self._pending_image = None
        self._image_change_timer = QTimer(self)
        self._image_change_timer.setSingleShot(True)
        self._image_change_timer.timeout.connect(self._apply_pending_image)

        self._setup_ui()
        self._connect_signals()
        self._apply_translations()

        self._load_image(image_service, image_path, agl_override_m)

    # ---------------- UI ----------------
    def _setup_ui(self):
        self.setWindowTitle(self.tr("Person Size Reference"))
        self.setModal(False)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(340)

        layout = QVBoxLayout(self)

        params_group = QGroupBox(self.tr("Reference Person"))
        form = QFormLayout()

        self.size_combo = QComboBox()
        for key, label, height_in, weight_lb in SIZE_CLASSES:
            ft, inch = height_in // 12, height_in % 12
            if self.distance_unit == 'ft':
                text = f"{self.tr(label)}  ({ft}'{inch}\", {weight_lb} lb)"
            else:
                h_cm = round(height_in * CM_PER_INCH)
                w_kg = round(weight_lb * 0.4536, 1)
                text = f"{self.tr(label)}  ({h_cm} cm, {w_kg} kg)"
            self.size_combo.addItem(text, key)
        saved_size = self._settings_service.get_setting(SETTING_SIZE_KEY)
        saved_idx = self.size_combo.findData(saved_size) if saved_size else -1
        self.size_combo.setCurrentIndex(saved_idx if saved_idx >= 0 else 1)
        self.size_key = self.size_combo.currentData()

        get_bool = self._settings_service.get_bool_setting
        self.standing_check = QCheckBox(self.tr("Standing"))
        self.standing_check.setChecked(get_bool(SETTING_SHOW_STANDING, True))
        self.recumbent_check = QCheckBox(self.tr("Lying down"))
        self.recumbent_check.setChecked(get_bool(SETTING_SHOW_RECUMBENT, True))
        self.sitting_check = QCheckBox(self.tr("Sitting"))
        self.sitting_check.setChecked(get_bool(SETTING_SHOW_SITTING, False))
        poses_row = QHBoxLayout()
        poses_row.addWidget(self.standing_check)
        poses_row.addWidget(self.recumbent_check)
        poses_row.addWidget(self.sitting_check)
        poses_widget = QWidget()
        poses_widget.setLayout(poses_row)

        self.shadow_check = QCheckBox(self.tr("Show shadows (from capture time)"))
        self.shadow_check.setChecked(get_bool(SETTING_SHOW_SHADOWS, True))

        self.terrain_check = QCheckBox(self.tr("Use terrain elevation (DEM)"))
        self.terrain_check.setChecked(get_bool(SETTING_USE_TERRAIN, True))

        # Ground rotation of the person, for lining a pose up with an object.
        self.rotation_spin = QSpinBox()
        self.rotation_spin.setRange(0, 359)
        self.rotation_spin.setWrapping(True)
        self.rotation_spin.setSuffix("°")
        self.rotation_spin.setToolTip(
            self.tr("Rotate the person on the ground to line it up with an object")
        )

        self.color_button = QPushButton()
        self.color_button.setFixedWidth(60)
        self.color_button.setToolTip(self.tr("Click to choose overlay color"))
        self._apply_color_button_style()
        color_row = QHBoxLayout()
        color_row.addWidget(self.color_button)
        color_row.addStretch()
        color_widget = QWidget()
        color_widget.setLayout(color_row)

        form.addRow(self.tr("Size:"), self.size_combo)
        form.addRow(self.tr("Show:"), poses_widget)
        form.addRow(self.tr("Rotation:"), self.rotation_spin)
        form.addRow("", self.shadow_check)
        form.addRow("", self.terrain_check)
        form.addRow(self.tr("Color:"), color_widget)
        params_group.setLayout(form)

        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("QLabel { color: #d9822b; }")
        self.status_label.setVisible(False)

        self.sun_label = QLabel()
        self.sun_label.setWordWrap(True)
        self.sun_label.setStyleSheet("QLabel { color: gray; }")

        # WALDO imagery: the camera clock is corrected via stamped metadata;
        # when the rendered shadow reveals a wrong correction, this is the
        # place the operator notices - offer the amendment right here.
        # (Visibility is decided in _update_sun_label, after the image loads.)
        self.adjust_clock_button = QPushButton(self.tr("Adjust camera clock..."))
        self.adjust_clock_button.setVisible(False)

        # WALDO imagery: attach the pilot's ForeFlight track log to stamp
        # true per-image bank/pitch and GPS-accurate capture times.
        self.flight_log_button = QPushButton(self.tr("Flight track log..."))
        self.flight_log_button.setToolTip(self.tr(
            "Attach a ForeFlight track log CSV to stamp true aircraft "
            "attitude (bank/pitch) and GPS-accurate capture times onto "
            "these images."))
        self.flight_log_button.setVisible(False)

        # Trace a real shadow in the image to recover the true time of day
        # (works even when the camera clock is wrong).
        self.trace_shadow_button = QPushButton(self.tr("Trace shadow..."))
        self.trace_shadow_button.setToolTip(self.tr(
            "Derive the time of day from a real shadow: click the base of "
            "an object casting a shadow (rock, tree, post), then the tip of "
            "its shadow. The solved time drives the rendered shadows."))
        self.trace_shadow_button.setEnabled(False)

        instructions = QLabel(self.tr(
            "Drag the white handle to position the reference person. "
            "Silhouettes are drawn at true ground scale for this image's "
            "altitude and camera angle."
        ))
        instructions.setWordWrap(True)
        instructions.setStyleSheet("QLabel { color: gray; }")

        button_row = QHBoxLayout()
        self.recenter_button = QPushButton(self.tr("Recenter"))
        self.recenter_button.setToolTip(self.tr(
            "Bring the reference person to the center of the current view"))
        self.close_button = QPushButton(self.tr("Close"))
        button_row.addWidget(self.recenter_button)
        button_row.addWidget(self.trace_shadow_button)
        button_row.addWidget(self.adjust_clock_button)
        button_row.addWidget(self.flight_log_button)
        button_row.addStretch()
        button_row.addWidget(self.close_button)

        layout.addWidget(params_group)
        layout.addWidget(self.status_label)
        layout.addWidget(self.sun_label)
        layout.addWidget(instructions)
        layout.addLayout(button_row)
        layout.addStretch()

    def _apply_translations(self):
        # Static strings are set inline; this hook is kept for consistency
        # with the other translatable dialogs.
        pass

    def _connect_signals(self):
        self.size_combo.currentIndexChanged.connect(self._on_params_changed)
        self.standing_check.toggled.connect(self._on_params_changed)
        self.recumbent_check.toggled.connect(self._on_params_changed)
        self.sitting_check.toggled.connect(self._on_params_changed)
        self.shadow_check.toggled.connect(self._on_params_changed)
        self.terrain_check.toggled.connect(self._on_params_changed)
        self.rotation_spin.valueChanged.connect(self._on_rotation_changed)
        self.color_button.clicked.connect(self._on_color_button_clicked)
        self.recenter_button.clicked.connect(self._recenter)
        self.adjust_clock_button.clicked.connect(self._on_adjust_clock)
        self.flight_log_button.clicked.connect(self._on_flight_log)
        self.trace_shadow_button.clicked.connect(self._on_trace_shadow_clicked)
        self.close_button.clicked.connect(self.close)

    def _is_waldo_image(self) -> bool:
        try:
            from core.services.waldo import WaldoMetadataService
            return (self.image_path is not None
                    and WaldoMetadataService.is_waldo_image(self.image_path) is not None)
        except Exception:
            return False

    def _on_adjust_clock(self):
        """Open the clock-correction dialog for this image's folder.

        Prefilled from the currently stamped correction when one exists,
        else from fresh fault detection. After an apply, the sun position
        and shadows re-render with the corrected time.
        """
        import glob as _glob
        import os as _os
        from core.services.waldo import WaldoMetadataService, WaldoClockDecisions
        from core.views.images.viewer.dialogs.WaldoClockCorrectionDialog import (
            WaldoClockCorrectionDialog,
        )
        try:
            folder = _os.path.dirname(self.image_path)
            paths = [p for p in sorted(_glob.glob(_os.path.join(folder, '*.jpg')))
                     if WaldoMetadataService.is_waldo_image(p) is not None]
            if not paths:
                return
            service = WaldoMetadataService(terrain_service=None)
            proposal = (service.propose_amendment(paths)
                        or service.propose_clock_correction(paths))
            if proposal is None:
                self.sun_label.setText(self.tr(
                    "No camera clock fault or applied correction was found "
                    "for this folder."))
                return
            dialog = WaldoClockCorrectionDialog(self, service, paths, proposal)
            dialog.exec()
            if dialog.applied:
                if dialog.remember_choice:
                    WaldoClockDecisions.store_decision(
                        WaldoClockDecisions.folder_key_for(paths[0]),
                        {'decision': 'accepted',
                         'face_shift_h': dialog.accepted_face_shift_h,
                         'tz_text': dialog.accepted_tz_text})
                # A changed clock invalidates any applied flight-log stamps
                # (their signature records the correction the fit used) -
                # silently re-apply a remembered log against the new clock.
                self._reapply_flight_log_if_remembered(paths)
                self._invalidate_viewer_caches()
                self._resolve_sun()
                self._update_sun_label()
                self._on_params_changed()
        except Exception as e:
            LoggerService().error(f"PersonReferenceDialog: clock adjustment failed - {e}")

    def _waldo_folder_paths(self):
        """All WALDO image paths in this image's folder (sorted)."""
        import glob as _glob
        import os as _os
        from core.services.waldo import WaldoMetadataService
        folder = _os.path.dirname(self.image_path)
        return [p for p in sorted(_glob.glob(_os.path.join(folder, '*.jpg')))
                if WaldoMetadataService.is_waldo_image(p) is not None]

    def _invalidate_viewer_caches(self):
        """Drop viewer caches built from the (just restamped) attitude XMP."""
        try:
            from core.controllers.images.viewer.WaldoPrePassController import (
                invalidate_attitude_caches,
            )
            invalidate_attitude_caches(self.parent())
        except Exception as e:
            LoggerService().error(f"PersonReferenceDialog: cache invalidation failed - {e}")

    def _reapply_flight_log_if_remembered(self, paths):
        """Silently re-run the flight-log stage when this folder has one attached."""
        import os as _os
        from core.services.waldo import (
            WaldoMetadataService, WaldoClockDecisions, WaldoFlightLogDecisions,
        )
        from core.services.waldo.WaldoFlightLog import WaldoFlightLogService
        from core.views.images.viewer.dialogs.WaldoFlightLogDialog import (
            WaldoFlightLogDialog,
        )
        try:
            decision = WaldoFlightLogDecisions.get_decision(
                WaldoClockDecisions.folder_key_for(paths[0]))
            log_path = (decision or {}).get('log_path')
            if (decision or {}).get('decision') != 'accepted' or not log_path:
                return
            if not _os.path.isfile(log_path):
                return
            service = WaldoMetadataService(terrain_service=None)
            dialog = WaldoFlightLogDialog(
                self, service, WaldoFlightLogService(), paths, [log_path],
                auto_apply=True)
            dialog.exec()
        except Exception as e:
            LoggerService().error(f"PersonReferenceDialog: flight-log re-apply failed - {e}")

    def _on_flight_log(self):
        """Attach (or re-run) a ForeFlight track log for this image's folder.

        Discovers candidate CSVs near the folder; falls back to a file picker
        when none are found. After an apply, viewer caches rebuild so the
        FOV boxes / AOI positions reflect the new attitude immediately.
        """
        from PySide6.QtWidgets import QFileDialog
        from core.services.waldo import WaldoClockDecisions, WaldoFlightLogDecisions
        from core.services.waldo import WaldoMetadataService
        from core.services.waldo.WaldoFlightLog import WaldoFlightLogService
        from core.views.images.viewer.dialogs.WaldoFlightLogDialog import (
            WaldoFlightLogDialog,
        )
        import os as _os
        try:
            paths = self._waldo_folder_paths()
            if not paths:
                return
            folder_key = WaldoClockDecisions.folder_key_for(paths[0])
            flight_service = WaldoFlightLogService()

            candidates = []
            remembered = WaldoFlightLogDecisions.get_decision(folder_key)
            remembered_path = (remembered or {}).get('log_path')
            if remembered_path and _os.path.isfile(remembered_path):
                candidates.append(remembered_path)
            candidates.extend(p for p in flight_service.candidate_files(
                _os.path.dirname(paths[0])) if p not in candidates)
            if not candidates:
                picked, _filter = QFileDialog.getOpenFileName(
                    self, self.tr("Select ForeFlight track log"),
                    _os.path.dirname(paths[0]),
                    self.tr("Track logs (*.csv);;All files (*.*)"))
                if not picked:
                    return
                candidates = [picked]

            service = WaldoMetadataService(terrain_service=None)
            dialog = WaldoFlightLogDialog(
                self, service, flight_service, paths, candidates, auto_apply=False)
            dialog.exec()
            if dialog.applied and dialog.fit is not None:
                if dialog.remember_choice:
                    WaldoFlightLogDecisions.store_decision(folder_key, {
                        'decision': 'accepted',
                        'log_path': dialog.fit.log_path,
                    })
                self._invalidate_viewer_caches()
                self._resolve_sun()
                self._update_sun_label()
                self._on_params_changed()
        except Exception as e:
            LoggerService().error(f"PersonReferenceDialog: flight-log attach failed - {e}")

    def showEvent(self, event):
        super().showEvent(event)
        self.activateWindow()
        self.raise_()
        if not getattr(self, '_position_adjusted', False):
            try:
                pos = self.pos()
                self.move(pos.x() + 100, pos.y())
            except Exception:
                pass
            self._position_adjusted = True

    # ---------------- image / camera / sun ----------------
    def _load_image(self, image_service, image_path, agl_override_m,
                    allow_auto_zoom=True):
        """Build the camera model and sun position for an image, then render.

        Args:
            allow_auto_zoom: whether the legibility auto-zoom may run. It is
                suppressed on image changes that land in an already-zoomed
                view (the navigation's zoom must not be hijacked).
        """
        self.image_path = image_path
        self.camera = CameraModel.from_image_service(image_service, agl_override_m)
        self._resolve_sun()
        self._resolve_terrain()
        self._build_overlay()
        self._update_sun_label()
        self._update_terrain_check()
        self._render_all()

        if self.camera is None:
            self._show_status(self.tr(
                "Perspective overlay unavailable: this image is missing the "
                "altitude or lens metadata needed to project a person."
            ))
        else:
            self._show_status(None)
            if allow_auto_zoom:
                self._ensure_reference_visible()

    def _reference_bounds_scene(self):
        """United scene-space bounding rect of the visible silhouettes, or None.

        The shadow is deliberately excluded: a low sun casts a shadow many
        person-lengths long, and framing it would zoom the person itself back
        out to illegibility.
        """
        bounds = None
        for item in self.pose_items.values():
            if item is None or not item.isVisible():
                continue
            rect = item.path().boundingRect()
            if rect.isNull() or rect.isEmpty():
                continue
            bounds = rect if bounds is None else bounds.united(rect)
        return bounds

    def _ensure_reference_visible(self):
        """Zoom the viewer to the reference person when it is sub-visible.

        Drone imagery renders a person tens to hundreds of screen pixels
        tall, but high-altitude fixed-wing imagery renders one a couple of
        screen pixels tall at fit zoom, which reads as the tool doing nothing
        at all. When the projected silhouette would be illegible on screen,
        frame it in the viewer instead. Runs only on image load, so it never
        fights manual zooming afterwards.
        """
        viewer = self.image_viewer
        if self.camera is None or viewer is None:
            return
        bounds = self._reference_bounds_scene()
        if bounds is None:
            return
        try:
            on_screen = viewer.mapFromScene(bounds).boundingRect()
            screen_span = max(on_screen.width(), on_screen.height())
            if screen_span >= MIN_LEGIBLE_SCREEN_PX:
                return
            span = max(bounds.width(), bounds.height()) * AUTO_ZOOM_VIEW_SPAN
            # Floor keeps a degenerate sub-pixel person from zooming absurdly
            span = max(span, 80.0)
            target = QRectF(0.0, 0.0, span, span)
            target.moveCenter(bounds.center())
            viewer.zoomToRect(target)
        except Exception:
            # Zooming is a convenience; never let it break the overlay
            return
        self._show_status(self.tr(
            "Zoomed to the reference person: at this altitude a person spans "
            "only a few pixels."
        ))

    def update_for_image(self, image_service, image_path, agl_override_m=None):
        """Rebuild the camera/sun for a newly selected image (called by Viewer).

        The rebuild is deferred one beat: an image change is often part of a
        larger navigation - a gallery AOI click loads the image and then
        zooms to the AOI through a transient viewChanged handler. Rebuilding
        immediately would anchor the person at the pre-zoom view centre and
        the legibility auto-zoom would stomp the AOI zoom (field report).
        Waiting lets the navigation land; the person is then placed at the
        final view centre (the AOI, for gallery clicks).
        """
        self._reset_trace_state()
        self._clear_items()
        self._pending_image = (image_service, image_path, agl_override_m)
        self._image_change_timer.start(300)

    def _apply_pending_image(self):
        """Deferred tail of update_for_image.

        The legibility auto-zoom is never run here: it exists so the tool
        does not look inert on FIRST open, but once the dialog is up an
        image change is part of the operator's own navigation (arrow keys,
        gallery zoom-to-AOI) and the view must stay exactly where that
        navigation put it. Recenter brings the person in on demand.
        """
        if self._pending_image is None:
            return
        image_service, image_path, agl_override_m = self._pending_image
        self._pending_image = None
        self._load_image(image_service, image_path, agl_override_m,
                         allow_auto_zoom=False)

    def _resolve_sun(self):
        """Resolve the sun elevation/azimuth from the image capture metadata."""
        self.sun_elev = None
        self.sun_az = None
        self.sun_error = None
        self.sun_time_source = None
        self._capture_utc = None
        if not self.image_path:
            self.sun_error = self.tr("no image loaded")
            return
        try:
            exif = MetaDataHelper.get_exif_data_piexif(self.image_path)
        except Exception:
            self.sun_error = self.tr("image metadata could not be read")
            return
        gps = LocationInfo.get_gps(exif_data=exif)
        if not gps:
            self.sun_error = self.tr("image has no GPS coordinates")
            return
        self.drone_lat = gps['latitude']
        self.drone_lon = gps['longitude']
        try:
            xmp = MetaDataHelper.get_xmp_data(self.image_path, parse=True)
        except Exception:
            xmp = None
        try:
            utc, source = resolve_capture_utc(
                exif, xmp, lat=self.drone_lat, lon=self.drone_lon)
        except SolarTimeUnresolvable:
            self.sun_error = self.tr("capture time / timezone not in metadata")
            return
        self._capture_utc = utc
        # A time solved from a traced shadow beats the camera clock.
        if self._trace_override_utc is not None:
            utc = self._trace_override_utc
            source = 'shadow_trace'
        self.sun_time_source = source
        try:
            elev, az = get_solar_position(self.drone_lat, self.drone_lon, utc)
        except Exception:
            self.sun_error = self.tr("sun position could not be computed")
            return
        self.sun_elev = elev
        self.sun_az = az

    def _update_sun_label(self):
        """Refresh the sun-info line and enable/disable the shadow toggle."""
        self.adjust_clock_button.setVisible(self._is_waldo_image())
        self.flight_log_button.setVisible(self._is_waldo_image())
        self.trace_shadow_button.setEnabled(
            self.camera is not None and self.drone_lat is not None
            and self._capture_utc is not None)
        if self.sun_elev is not None and self.sun_elev > 0:
            text = self.tr(
                "Sun at capture: {elev:.0f}° above horizon, "
                "azimuth {az:.0f}°."
            ).format(elev=self.sun_elev, az=self.sun_az)
            if self.sun_time_source == 'exif_local_tz_from_gps':
                text += " " + self.tr(
                    "Capture time zone estimated from GPS location.")
            elif self.sun_time_source == 'waldo_corrected':
                text += " " + self.tr(
                    "Using repaired capture time (camera clock fault).")
            elif self.sun_time_source == 'shadow_trace':
                text += " " + self.tr(
                    "Time of day derived from the traced shadow.")
            self.sun_label.setText(text)
            self.shadow_check.setEnabled(True)
        else:
            if self.sun_elev is not None and self.sun_elev <= 0:
                reason = self.tr("the sun was below the horizon at capture")
            else:
                reason = self.sun_error or self.tr("sun position unavailable")
            self.sun_label.setText(self.tr("Shadow unavailable: {reason}.")
                                   .format(reason=reason))
            self.shadow_check.setEnabled(False)

    # ---------------- overlay items ----------------
    def _build_overlay(self):
        """Create the anchor handle and one path item per pose + shadow."""
        if self.camera is None:
            return
        scene = self.image_viewer.scene

        self.anchor_item = _AnchorHandle(self)
        self.anchor_item.setPos(self._default_anchor_scene())
        scene.addItem(self.anchor_item)

        # Shadow sits below the silhouettes; silhouettes below the handle.
        self.shadow_item = QGraphicsPathItem()
        self.shadow_item.setZValue(1000)
        self.shadow_item.setPen(QPen(QColor(0, 0, 0, 110), 1, Qt.DashLine))
        self.shadow_item.setBrush(QBrush(QColor(0, 0, 0, 70)))
        scene.addItem(self.shadow_item)

        for pose in ("recumbent", "sitting", "standing"):
            item = QGraphicsPathItem()
            item.setZValue(1001)
            scene.addItem(item)
            self.pose_items[pose] = item
        self._apply_color_to_items()

    def _clear_items(self):
        """Remove every overlay item from the scene."""
        scene = getattr(self.image_viewer, 'scene', None)
        for item in list(self.pose_items.values()):
            if scene is not None and item is not None:
                try:
                    scene.removeItem(item)
                except Exception:
                    pass
        self.pose_items.clear()
        for attr in ('shadow_item', 'anchor_item'):
            item = getattr(self, attr, None)
            if item is not None and scene is not None:
                try:
                    scene.removeItem(item)
                except Exception:
                    pass
            setattr(self, attr, None)

    # ---------------- rendering ----------------
    def _selected_height_cm(self):
        idx = max(0, self.size_combo.currentIndex())
        return SIZE_CLASSES[idx][2] * CM_PER_INCH

    def _is_near_nadir(self):
        """True when the camera looks close enough to straight down that a
        standing figure should be drawn as a flat overhead footprint rather
        than a laid-over 3D column."""
        if self.camera is None:
            return True
        return abs(self.camera.pitch_deg + 90.0) < NADIR_PITCH_TOLERANCE_DEG

    def _foot_ned(self):
        """Ground point (NED, metres from the camera) under the anchor handle.

        Casts the anchor pixel onto the DEM terrain surface when terrain use
        is enabled and available, otherwise onto a flat plane at the AGL.
        """
        if self.camera is None or self.anchor_item is None:
            return None
        pos = self.anchor_item.pos()
        if self._terrain_active():
            terrain_foot = self._terrain_foot_ned(pos.x(), pos.y())
            if terrain_foot is not None:
                return terrain_foot
        return self.camera.pixel_to_ground(pos.x(), pos.y())

    # ---------------- DEM terrain ----------------
    def _resolve_terrain(self):
        """Look up the terrain service and the nadir reference elevation."""
        self.terrain_service = None
        self.terrain_nadir_elev = None
        try:
            from core.services.image.AOIService import _get_terrain_service
            service = _get_terrain_service()
        except Exception:
            return
        if service is None or not getattr(service, 'enabled', False):
            return
        self.terrain_service = service
        # Reference elevation: the terrain directly under the drone (nadir).
        self.terrain_nadir_elev = self._terrain_elevation(0.0, 0.0)

    def _update_terrain_check(self):
        """Enable the terrain checkbox only when DEM data covers this image."""
        available = (self.terrain_service is not None
                     and self.terrain_nadir_elev is not None)
        self.terrain_check.setEnabled(available)
        if available:
            self.terrain_check.setToolTip(self.tr(
                "Place the person and shadow on the DEM terrain surface"
            ))
        else:
            self.terrain_check.setToolTip(self.tr(
                "Terrain (DEM) data is not available for this image"
            ))

    def _terrain_active(self):
        """Whether terrain-aware placement is currently enabled and usable."""
        return (self.terrain_check.isChecked() and self.terrain_check.isEnabled()
                and self.terrain_service is not None
                and self.terrain_nadir_elev is not None)

    def _ned_to_latlon(self, north, east):
        """Convert a camera-NED horizontal offset to a (lat, lon)."""
        lat = self.drone_lat + math.degrees(north / EARTH_RADIUS_M)
        lon = self.drone_lon + math.degrees(
            east / (EARTH_RADIUS_M * math.cos(math.radians(self.drone_lat)))
        )
        return lat, lon

    def _terrain_elevation(self, north, east):
        """Terrain elevation (metres) at a camera-NED ground point, or None."""
        if self.terrain_service is None or self.drone_lat is None:
            return None
        lat, lon = self._ned_to_latlon(north, east)
        try:
            result = self.terrain_service.get_elevation(lat, lon)
        except Exception:
            return None
        if (result is None or getattr(result, 'source', None) != 'terrain'
                or result.elevation_m is None):
            return None
        return result.elevation_m

    def _terrain_foot_ned(self, u, v):
        """Iteratively cast the pixel ray onto the DEM surface.

        The camera AGL is taken as the height above the terrain at the nadir
        point, so a point whose terrain is higher than the nadir is
        correspondingly closer to the camera.
        """
        ray = self.camera.pixel_ray(u, v)
        if ray[2] <= 1e-9:
            return None
        down = self.camera.agl_m
        for _ in range(5):
            t = down / ray[2]
            elev = self._terrain_elevation(t * ray[0], t * ray[1])
            if elev is None:
                break
            new_down = self.camera.agl_m - (elev - self.terrain_nadir_elev)
            if new_down <= 1.0:
                break  # implausible - keep the previous estimate
            if abs(new_down - down) < 0.05:
                down = new_down
                break
            down = new_down
        t = down / ray[2]
        if t <= 0:
            return None
        return (t * ray[0], t * ray[1], t * ray[2])

    def _shadow_slope(self, foot):
        """Terrain grade along the shadow direction (rise/run), or 0.0 if flat.

        Positive means the ground rises away from the sun, which shortens
        shadows; negative lengthens them.
        """
        if not self._terrain_active() or foot is None or self.sun_az is None:
            return 0.0
        foot_elev = self._terrain_elevation(foot[0], foot[1])
        if foot_elev is None:
            return 0.0
        baseline_m = 10.0
        anti_sun = math.radians(self.sun_az + 180.0)
        tip_n = foot[0] + baseline_m * math.cos(anti_sun)
        tip_e = foot[1] + baseline_m * math.sin(anti_sun)
        tip_elev = self._terrain_elevation(tip_n, tip_e)
        if tip_elev is None:
            return 0.0
        return (tip_elev - foot_elev) / baseline_m

    def _project_person_local(self, person_points, foot_ned):
        """Project person-local (x=right, y=forward, z=up) points to pixels."""
        fn, fe, fd = foot_ned
        pixels = []
        for px, py, pz in person_points:
            uv = self.camera.project(fn + py, fe + px, fd - pz)
            if uv is not None:
                pixels.append(uv)
        return pixels

    @staticmethod
    def _hull_path(pixels):
        """Closed QPainterPath around the convex hull of projected pixels."""
        if len(pixels) < 3:
            return None
        hull = cv2.convexHull(np.array(pixels, dtype=np.float32))
        poly = QPolygonF([QPointF(float(p[0][0]), float(p[0][1])) for p in hull])
        path = QPainterPath()
        path.addPolygon(poly)
        path.closeSubpath()
        return path

    @staticmethod
    def _polyline_path(pixels):
        """Closed QPainterPath through projected pixels in order."""
        if len(pixels) < 3:
            return None
        path = QPainterPath()
        path.moveTo(pixels[0][0], pixels[0][1])
        for u, v in pixels[1:]:
            path.lineTo(u, v)
        path.closeSubpath()
        return path

    def _recumbent_local_points(self, height_cm):
        """Sample the recumbent silhouette outline as flat ground points (metres)."""
        path, _ = _build_recumbent_path(height_cm)
        polygons = path.toSubpathPolygons()
        if not polygons:
            return []
        outline = max(polygons, key=lambda p: p.count())
        points = []
        for i in range(outline.count()):
            qp = outline.at(i)
            # Centimetres -> metres; lie flat on the ground (z = 0).
            points.append((qp.x() / 100.0, -qp.y() / 100.0, 0.0))
        return points

    def _orient(self, points):
        """Rotate person-local (x, y) points by the current rotation setting."""
        if not self.rotation_deg:
            return list(points)
        theta = math.radians(self.rotation_deg)
        cos_t, sin_t = math.cos(theta), math.sin(theta)
        return [(x * cos_t + y * sin_t, -x * sin_t + y * cos_t, z)
                for x, y, z in points]

    def _on_rotation_changed(self, value):
        """Re-render when the user changes the person's ground rotation."""
        self.rotation_deg = int(value)
        self._render_all()

    def _render_all(self):
        """Re-project every enabled pose and the shadow at the anchor."""
        if self.camera is None:
            return
        foot = self._foot_ned()
        height_cm = self._selected_height_cm()
        height_m = height_cm / 100.0

        upright = {
            'standing': self.standing_check.isChecked(),
            'sitting': self.sitting_check.isChecked(),
        }
        near_nadir = self._is_near_nadir()
        for pose, enabled in upright.items():
            item = self.pose_items.get(pose)
            if item is None:
                continue
            path = None
            if enabled and foot is not None:
                if near_nadir:
                    # Flat overhead footprint: compact and person-sized
                    # everywhere, instead of a radial layover smear.
                    model = PersonModel.build_footprint_points(height_m, pose)
                else:
                    model = PersonModel.build_points(height_m, pose)
                points = self._orient(model)
                path = self._hull_path(self._project_person_local(points, foot))
            item.setPath(path or QPainterPath())
            item.setVisible(path is not None)

        rec_item = self.pose_items.get('recumbent')
        if rec_item is not None:
            path = None
            if self.recumbent_check.isChecked() and foot is not None:
                points = self._orient(self._recumbent_local_points(height_cm))
                path = self._polyline_path(self._project_person_local(points, foot))
            rec_item.setPath(path or QPainterPath())
            rec_item.setVisible(path is not None)

        self._render_shadows(height_cm, height_m, foot)

    def _render_shadows(self, height_cm, height_m, foot):
        """Re-project the shadow of every enabled pose into one shadow shape."""
        if self.shadow_item is None:
            return
        shadow_on = (self.shadow_check.isChecked() and self.shadow_check.isEnabled()
                     and foot is not None
                     and self.sun_elev is not None and self.sun_elev > 0)
        combined = None
        if shadow_on:
            slope = self._shadow_slope(foot)
            enabled = {
                'standing': self.standing_check.isChecked(),
                'sitting': self.sitting_check.isChecked(),
                'recumbent': self.recumbent_check.isChecked(),
            }
            for pose, is_on in enabled.items():
                if not is_on:
                    continue
                path = self._shadow_path_for_pose(
                    pose, height_cm, height_m, foot, slope)
                if path is None or path.isEmpty():
                    continue
                combined = path if combined is None else combined.united(path)
        self.shadow_item.setPath(combined or QPainterPath())
        self.shadow_item.setVisible(combined is not None)

    def _shadow_path_for_pose(self, pose, height_cm, height_m, foot, slope=0.0):
        """Build the ground-shadow QPainterPath cast by one pose, or None.

        Every pose is cast the same way: a cloud of 3D body points is dropped
        along the sun ray to the ground and the convex hull of the result is
        the shadow - one coherent dark patch. Standing and sitting use their
        upright volumes; the recumbent body is the lying outline given a small
        lying thickness so it casts a low shadow that hugs the body.
        """
        if pose == 'recumbent':
            outline = self._recumbent_local_points(height_cm)
            thickness = RECUMBENT_THICKNESS_FRACTION * height_m
            points = ([(x, y, 0.0) for x, y, _z in outline]
                      + [(x, y, thickness) for x, y, _z in outline])
        else:
            points = PersonModel.build_points(height_m, pose)
        ground = compute_shadow_ground_points(
            self._orient(points), foot, self.sun_elev, self.sun_az, slope
        )
        return self._hull_path(self._project_ground(ground))

    def _project_ground(self, ground_points):
        """Project NED ground points to pixels, dropping any behind the camera."""
        pixels = []
        for north, east, down in ground_points:
            uv = self.camera.project(north, east, down)
            if uv is not None:
                pixels.append(uv)
        return pixels

    # ---------------- colour ----------------
    def _apply_color_button_style(self):
        c = self.overlay_color
        border = '#ffffff' if c.lightness() < 128 else '#222222'
        self.color_button.setStyleSheet(
            f"QPushButton {{ background-color: {c.name()}; "
            f"border: 1px solid {border}; min-height: 22px; }}"
        )

    def _apply_color_to_items(self):
        pen = QPen(QColor(self.overlay_color))
        pen.setCosmetic(True)
        pen.setWidth(2)
        fill = QColor(self.overlay_color)
        fill.setAlpha(60)
        for item in self.pose_items.values():
            if item is not None:
                item.setPen(pen)
                item.setBrush(QBrush(fill))

    def _on_color_button_clicked(self):
        chosen = QColorDialog.getColor(
            self.overlay_color, self, self.tr("Choose Overlay Color")
        )
        if not chosen.isValid():
            return
        self.overlay_color = chosen
        self._settings_service.set_setting(SETTING_OVERLAY_COLOR, chosen.name())
        self._apply_color_button_style()
        self._apply_color_to_items()

    # ---------------- helpers ----------------
    def _viewport_center_scene(self):
        try:
            return self.image_viewer.mapToScene(
                self.image_viewer.viewport().rect().center()
            )
        except Exception:
            return self.image_viewer.sceneRect().center()

    def _default_anchor_scene(self):
        """Person placement for open and Recenter: the current view centre.

        Opening the tool must not yank the operator away from the area
        they are inspecting (field report: opening while zoomed to an AOI
        panned the view to the image centre) - the person appears where
        they are already looking, clamped to the image bounds. Falls back
        to the nadir placement when the view centre cannot be determined.
        """
        try:
            point = self._viewport_center_scene()
            x = float(point.x())
            y = float(point.y())
            if self.camera is not None:
                x = min(max(x, 0.0), float(self.camera.width))
                y = min(max(y, 0.0), float(self.camera.height))
            return self._avoid_selected_aoi(QPointF(x, y))
        except Exception:
            return self._avoid_selected_aoi(self._nadir_anchor_scene())

    def _avoid_selected_aoi(self, point):
        """Nudge an anchor point off the currently selected AOI.

        Clicking an AOI centres the view on it, so a view-centre placement
        would sit the person exactly on top of the find. When the anchor
        falls within the AOI's radius + AOI_CLEARANCE_PX, shift it level
        with the AOI to its left; when that leaves the image, to its right.
        """
        try:
            viewer = self._parent_viewer
            aoi_index = viewer.aoi_controller.selected_aoi_index
            if aoi_index is None or aoi_index < 0:
                return point
            image = viewer.images[viewer.current_image]
            aoi = image['areas_of_interest'][aoi_index]
            aoi_x = float(aoi['center'][0])
            aoi_y = float(aoi['center'][1])
            radius = float(aoi.get('radius', 0) or 0)
        except Exception:
            return point
        clearance = radius + AOI_CLEARANCE_PX
        dx = point.x() - aoi_x
        dy = point.y() - aoi_y
        if (dx * dx + dy * dy) > clearance * clearance:
            return point  # anchor is not on the AOI - leave it alone
        left_x = aoi_x - clearance
        if left_x >= 0.0:
            return QPointF(left_x, aoi_y)
        right_x = aoi_x + clearance
        if self.camera is not None:
            right_x = min(right_x, float(self.camera.width))
        return QPointF(right_x, aoi_y)

    def _nadir_anchor_scene(self):
        """Fallback placement: the ground point directly under the drone.

        The nadir projects to a compact, upright silhouette, so the
        overlay still opens sensibly when the view centre is unusable.
        Falls back further to the image centre.
        """
        if self.camera is not None:
            nadir = self.camera.project(0.0, 0.0, self.camera.agl_m)
            if nadir is not None:
                u, v = nadir
                if (0.0 <= u <= self.camera.width
                        and 0.0 <= v <= self.camera.height):
                    return QPointF(u, v)
            return QPointF(self.camera.width / 2.0, self.camera.height / 2.0)
        return QPointF(0.0, 0.0)

    def _show_status(self, message):
        if message:
            self.status_label.setText(message)
            self.status_label.setVisible(True)
        else:
            self.status_label.setVisible(False)

    # ---------------- event handlers ----------------
    def _on_params_changed(self, *_):
        self.size_key = self.size_combo.currentData()
        self._persist_settings()
        self._render_all()

    def _persist_settings(self):
        """Persist the reference-person choices for the next time the tool opens."""
        s = self._settings_service
        s.set_setting(SETTING_SIZE_KEY, self.size_combo.currentData())
        s.set_setting(SETTING_SHOW_STANDING, self.standing_check.isChecked())
        s.set_setting(SETTING_SHOW_RECUMBENT, self.recumbent_check.isChecked())
        s.set_setting(SETTING_SHOW_SITTING, self.sitting_check.isChecked())
        s.set_setting(SETTING_SHOW_SHADOWS, self.shadow_check.isChecked())
        s.set_setting(SETTING_USE_TERRAIN, self.terrain_check.isChecked())

    def _on_anchor_moved(self):
        self._render_all()

    def _recenter(self):
        """Bring the reference person into the user's current view.

        The user pans/zooms to the spot they are inspecting and hits
        Recenter to pull the overlay there - the same placement rule the
        tool uses when it opens.
        """
        if self.anchor_item is not None:
            self.anchor_item.setPos(self._default_anchor_scene())
            self._render_all()

    # ---------------- shadow trace ----------------
    def _on_trace_shadow_clicked(self):
        """Start/cancel a shadow trace, or clear an applied traced time."""
        if self._trace_active:
            self._end_trace(cancelled=True)
            return
        if self._trace_override_utc is not None:
            self._reset_trace_state()
            self._resolve_sun()
            self._update_sun_label()
            self._on_params_changed()
            return
        self._begin_trace()

    def _begin_trace(self):
        """Arm the two-click trace on the main image viewer."""
        self._trace_points = []
        self._clear_trace_items()
        try:
            self.image_viewer.leftMouseButtonPressed.connect(self._on_trace_click)
        except Exception:
            return
        self._trace_connected = True
        # The main image's left button normally starts a region zoom, which
        # consumes the press before leftMouseButtonPressed is emitted -
        # point-capture mode routes plain left clicks to the signal instead.
        begin_capture = getattr(self.image_viewer, 'begin_point_capture', None)
        if callable(begin_capture):
            try:
                begin_capture()
            except Exception:
                pass
        self._trace_active = True
        self.trace_shadow_button.setText(self.tr("Cancel trace"))
        self._show_status(self.tr(
            "Shadow trace: on the image, click the BASE of an object casting "
            "a shadow (rock, tree, post), then click the TIP of its shadow."))

    def _end_trace(self, cancelled=False):
        """Disarm the trace clicks; optionally discard what was traced."""
        self._trace_active = False
        # Only disconnect when actually connected: a blind disconnect makes
        # Qt print a RuntimeWarning on every image change.
        if self._trace_connected:
            self._trace_connected = False
            try:
                self.image_viewer.leftMouseButtonPressed.disconnect(self._on_trace_click)
            except Exception:
                pass
        end_capture = getattr(self.image_viewer, 'end_point_capture', None)
        if callable(end_capture):
            try:
                end_capture()
            except Exception:
                pass
        if cancelled:
            self._trace_points = []
            self._clear_trace_items()
            self.trace_shadow_button.setText(self.tr("Trace shadow..."))
            self._show_status(None)

    def _reset_trace_state(self):
        """Drop the trace override and visuals (image change / clear / close)."""
        self._end_trace(cancelled=True)
        self._trace_override_utc = None
        self.trace_shadow_button.setText(self.tr("Trace shadow..."))

    def _on_trace_click(self, x, y, _viewer=None):
        """Collect the two trace clicks: shadow base, then shadow tip."""
        if not self._trace_active:
            return
        self._trace_points.append((float(x), float(y)))
        self._add_trace_marker(float(x), float(y),
                               first=len(self._trace_points) == 1)
        if len(self._trace_points) < 2:
            self._show_status(self.tr(
                "Shadow trace: now click the TIP of the shadow."))
            return
        self._end_trace()
        self._draw_trace_line()
        self._solve_traced_shadow()

    def _add_trace_marker(self, x, y, first):
        """Drop a fixed-screen-size dot where the user clicked."""
        scene = getattr(self.image_viewer, 'scene', None)
        if scene is None:
            return
        radius = 5.0
        item = QGraphicsEllipseItem(-radius, -radius, 2 * radius, 2 * radius)
        item.setPos(QPointF(x, y))
        color = QColor('#ff9800') if first else QColor('#ffc107')
        item.setBrush(QBrush(color))
        item.setPen(QPen(QColor(0, 0, 0), 1))
        item.setZValue(1101)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
        scene.addItem(item)
        self._trace_items.append(item)

    def _draw_trace_line(self):
        """Draw the traced base->tip line (kept visible for comparison with
        the rendered shadow)."""
        scene = getattr(self.image_viewer, 'scene', None)
        if scene is None or len(self._trace_points) != 2:
            return
        (x1, y1), (x2, y2) = self._trace_points
        line = QGraphicsLineItem(x1, y1, x2, y2)
        pen = QPen(QColor('#ff9800'), 2, Qt.DashLine)
        pen.setCosmetic(True)
        line.setPen(pen)
        line.setZValue(1100)
        scene.addItem(line)
        self._trace_items.append(line)

    def _clear_trace_items(self):
        """Remove the trace visuals from the scene."""
        scene = getattr(self.image_viewer, 'scene', None)
        for item in self._trace_items:
            if scene is not None:
                try:
                    scene.removeItem(item)
                except Exception:
                    pass
        self._trace_items = []

    def _traced_shadow_azimuth(self):
        """World azimuth of the traced shadow (base -> tip), or None.

        Both clicks are cast onto the ground through the same CameraModel
        used to render the person and its shadow, so the traced azimuth and
        the rendered shadow live in the same frame - after applying the
        solved time the rendered shadow lines up with the traced line.
        """
        if self.camera is None or len(self._trace_points) != 2:
            return None
        base = self.camera.pixel_to_ground(*self._trace_points[0])
        tip = self.camera.pixel_to_ground(*self._trace_points[1])
        if base is None or tip is None:
            return None
        d_north = tip[0] - base[0]
        d_east = tip[1] - base[1]
        if abs(d_north) < 1e-9 and abs(d_east) < 1e-9:
            return None
        return math.degrees(math.atan2(d_east, d_north)) % 360.0

    def _format_local_time(self, utc_dt):
        """Format a UTC moment as local wall time at the drone's position."""
        try:
            from zoneinfo import ZoneInfo
            tz_name = timezone_name_for_position(self.drone_lat, self.drone_lon)
            if tz_name:
                return utc_dt.astimezone(ZoneInfo(tz_name)).strftime('%H:%M %Z')
        except Exception:
            pass
        return utc_dt.strftime('%H:%M UTC')

    def _solve_traced_shadow(self):
        """Invert the traced shadow to a time of day and apply it."""
        shadow_az = self._traced_shadow_azimuth()
        if shadow_az is None:
            self._reset_trace_state()
            self._show_status(self.tr(
                "Shadow trace: the traced points could not be projected to "
                "the ground - try two points further apart."))
            return
        if self._capture_utc is None or self.drone_lat is None:
            self._reset_trace_state()
            self._show_status(self.tr(
                "Shadow trace: the image is missing the capture date or GPS "
                "position needed to solve the time."))
            return
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            solution = solve_time_for_shadow_azimuth(
                self.drone_lat, self.drone_lon, self._capture_utc, shadow_az)
        except Exception as e:
            solution = None
            self.logger.error(f"Shadow trace: solver failed - {e}")
        finally:
            QApplication.restoreOverrideCursor()
        if solution is None:
            self._reset_trace_state()
            self._show_status(self.tr(
                "Shadow trace: no daylight sun position matches that "
                "direction on the capture date. Check the traced direction "
                "(base first, then shadow tip)."))
            return
        self._trace_override_utc = solution.utc
        self.trace_shadow_button.setText(self.tr("Clear traced time"))
        message = self.tr(
            "Time solved from the traced shadow: {time} "
            "(sun azimuth {az:.0f}°, {elev:.0f}° above horizon)."
        ).format(time=self._format_local_time(solution.utc),
                 az=solution.sun_azimuth_deg,
                 elev=solution.sun_elevation_deg)
        if solution.direction_flipped:
            message += " " + self.tr(
                "The traced direction looked reversed and was interpreted "
                "tip-to-base.")
        if solution.ambiguous:
            message += " " + self.tr(
                "Note: another time of day matches this direction almost "
                "as well.")
        self._show_status(message)
        self._resolve_sun()
        self._update_sun_label()
        self._on_params_changed()

    # ---------------- close ----------------
    def closeEvent(self, event):
        # A pending image-change rebuild must not fire into a closed dialog
        # (it would re-add overlay items that nothing would ever remove).
        self._image_change_timer.stop()
        self._pending_image = None
        self._reset_trace_state()
        self._clear_items()
        super().closeEvent(event)
