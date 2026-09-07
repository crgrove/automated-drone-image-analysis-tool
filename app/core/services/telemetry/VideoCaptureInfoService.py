"""Derive capture settings from a video, so the operator doesn't guess.

The streaming setup guide asks two questions that decide GSD — which
drone/camera shot the video, and how high it was flying — and both are
usually recorded *in* the file:

* **Aircraft** — DJI writes it into the MP4's ``encoder`` container tag
  (``"DJI DJI Matrice 4E"``). This is the video counterpart to the EXIF
  Make/Model that image analysis already matches against ``drones.csv``.
* **Altitude** — the embedded telemetry track carries per-frame
  ``rel_alt`` (height above the takeoff point), the same field the HUD
  and map use.

Getting either wrong is not cosmetic. GSD scales linearly with altitude
and detection area with GSD², so a video shot at 49 ft but configured as
150 ft produces min/max detection areas roughly 9× off — enough to
filter out the very targets the operator is looking for. Picking the
wrong airframe is worse still, because sibling models carry different
sensors (a Matrice 4E has Wide/Medium/Zoom; a 4T has Wide/Zoom/Thermal).

Detection is advisory: the wizard pre-selects what is found and the
operator can override it.
"""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass
from typing import Optional

from core.services.LoggerService import LoggerService
from core.services.telemetry.TelemetrySourceResolver import load_telemetry_for_video
from helpers.FormatHelper import FormatHelper
from helpers.VideoFileHelper import get_video_device_tags

# Container tags that may name the capturing device, best first.
_DEVICE_TAG_KEYS = ("encoder", "model", "com.apple.quicktime.model", "make")

# Fixes below this are treated as ground time rather than flight. Clips that
# start on the pad or end on landing are common, and a legacy relative
# altitude can even read slightly negative, so ground fixes have to be
# excluded before asking "what altitude was this shot at".
_AIRBORNE_FLOOR_M = 2.0


@dataclass
class VideoCaptureInfo:
    """What we could work out about how a video was captured."""

    make: Optional[str] = None
    model: Optional[str] = None
    device_text: Optional[str] = None      # raw tag the model came from
    # Above the takeoff point - DJI's ``rel_alt`` and a flight log's
    # relative-altitude column. Kept apart from the terrain AGL below
    # because the two are equal only over flat ground.
    altitude_ato_m: Optional[float] = None
    # Above the terrain beneath the aircraft, where the log resolved one
    # itself. Rare: DJI never does.
    altitude_agl_terrain_m: Optional[float] = None
    altitude_samples: int = 0

    @property
    def has_device(self) -> bool:
        return bool(self.make and self.model)

    @property
    def has_altitude(self) -> bool:
        return (self.altitude_agl_terrain_m is not None
                or self.altitude_ato_m is not None)

    @property
    def altitude_m(self) -> Optional[float]:
        """The altitude to prefill the wizard with, best reference first.

        The wizard asks for height above the ground being flown over, so a
        terrain AGL answers it exactly and ATO only approximates it. Read
        :attr:`altitude_reference` to find out which came back — the
        difference is what the operator needs to know before accepting the
        number.
        """
        if self.altitude_agl_terrain_m is not None:
            return self.altitude_agl_terrain_m
        return self.altitude_ato_m

    @property
    def altitude_reference(self) -> str:
        """Which plane :attr:`altitude_m` is measured from."""
        if self.altitude_agl_terrain_m is not None:
            return FormatHelper.ALTITUDE_REFERENCE_TERRAIN
        return FormatHelper.ALTITUDE_REFERENCE_TAKEOFF


def read_device_text(video_path, logger=None) -> Optional[str]:
    """Return the container tag most likely to name the capture device."""
    tags = get_video_device_tags(video_path, logger=logger)
    for key in _DEVICE_TAG_KEYS:
        value = tags.get(key)
        if value and value.strip():
            return value.strip()
    return None


def match_drone_model(device_text: str, drones_df) -> Optional[tuple]:
    """Match a container device string against the drone table.

    DJI writes the tag two different ways, and both appear in the wild:

    * the human-readable name, with the make repeated —
      ``"DJI DJI Matrice 4E"``; and
    * the short EXIF-style code — ``"DJI M4TD"``, which lives in the
      table's ``Model (Exif)`` column as ``"M4T, M4TD"``.

    Exact equality is therefore useless. Codes are matched as whole words
    (so ``M4T`` does not match inside ``M4TD``) and names by containment,
    with codes preferred because they are unambiguous.

    Returns:
        ``(manufacturer, model)`` on a confident match, else None.
    """
    if not device_text or drones_df is None or drones_df.empty:
        return None

    haystack = _normalize(device_text)
    # Padded so a code can be tested as a bounded phrase. A set of single
    # words would not do: normalization turns a hyphenated code such as
    # ``L1D-20c`` into two tokens, which could then never match.
    padded_haystack = f" {haystack} "

    code_match = None
    name_match = None
    name_length = 0

    for _, row in drones_df.iterrows():
        make = _clean(row.get("Manufacturer"))
        model = _clean(row.get("Model"))
        if not make or not model:
            continue
        # The make must appear too, so a bare "Mini 3" in some unrelated
        # vendor's tag cannot match a DJI row.
        if _normalize(make) not in haystack:
            continue

        # 1. EXIF-style codes, as bounded phrases. Bounding keeps the
        #    whole-word property (``M4T`` still does not match inside
        #    ``M4TD``) while letting multi-token codes match.
        for code in _split_codes(row.get("Model (Exif)")):
            if code and f" {code} " in padded_haystack:
                code_match = (make, model)
                break
        if code_match:
            break

        # 2. Human-readable name, by containment. Longest wins so
        #    "Matrice 4E" beats a "Matrice 4" row that prefixes it.
        needle = _normalize(model)
        if needle and needle in haystack and len(needle) > name_length:
            name_length = len(needle)
            name_match = (make, model)

    return code_match or name_match


def detect_capture_info(
    video_path, drones_df=None, logger=None, metadata_path=None
) -> VideoCaptureInfo:
    """Work out the aircraft and flight altitude for ``video_path``.

    Args:
        video_path: Path to the video.
        drones_df: Drone/sensor table. Loaded from ``drones.csv`` when None.
        logger: Optional logger.
        metadata_path: Optional operator-selected ``.SRT`` / ``.csv``
            metadata file, used instead of the video's own telemetry.
            Altitude detection needs a **height above the ground**, which
            is what GSD is computed from, so a log carrying only MSL
            yields no altitude. That is deliberate: neither ATO nor AGL is
            derivable from MSL without terrain data, and a wrong altitude
            squares into the detection-area filter. A log's own terrain
            AGL is preferred where it has one; otherwise ATO stands in,
            and :attr:`VideoCaptureInfo.altitude_reference` says which.

    Returns:
        A :class:`VideoCaptureInfo`; every field is optional, so callers
        must check ``has_device`` / ``has_altitude`` before using it.
    """
    logger = logger or LoggerService()
    info = VideoCaptureInfo()

    # --- aircraft -----------------------------------------------------
    try:
        device_text = read_device_text(video_path, logger=logger)
        info.device_text = device_text
        if device_text:
            if drones_df is None:
                from helpers.PickleHelper import PickleHelper
                drones_df = PickleHelper.get_drone_sensor_info()
            match = match_drone_model(device_text, drones_df)
            if match:
                info.make, info.model = match
    except Exception as e:  # noqa: BLE001 - detection is advisory
        logger.debug(f"Drone detection failed for {video_path}: {e}")

    # --- altitude -----------------------------------------------------
    try:
        resolution = load_telemetry_for_video(
            video_path, metadata_path, logger=logger
        )
        if resolution.found:
            # One reference for the whole clip. Mixing a terrain AGL from
            # some fixes with ATO from others would produce a median that
            # describes neither plane.
            attribute = (
                "altitude_agl_terrain_m"
                if any(point.altitude_agl_terrain_m is not None
                       for point in resolution.track.points)
                else "altitude_ato_m"
            )
            airborne = [
                getattr(point, attribute)
                for point in resolution.track.points
                if getattr(point, attribute) is not None
                and getattr(point, attribute) >= _AIRBORNE_FLOOR_M
            ]
            if airborne:
                # Median of the *airborne* fixes. Median alone is not enough:
                # a real 80-second clip in the test data spends 58% of its
                # fixes on the ground and 42% at 77 m, so the plain median is
                # -4.4 m — which clamps to 0 and makes GSD uncomputable,
                # worse than not detecting at all. Excluding ground time
                # gives 76.9 m, the altitude the footage was actually shot
                # at. Median rather than mean still guards against the odd
                # bad fix and the climb/descent legs.
                setattr(info, attribute, float(statistics.median(airborne)))
                info.altitude_samples = len(airborne)
    except Exception as e:  # noqa: BLE001 - detection is advisory
        logger.debug(f"Altitude detection failed for {video_path}: {e}")

    return info


def _clean(value) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return "" if text.lower() in ("nan", "none") else text


def _split_codes(value) -> list:
    """Split a ``Model (Exif)`` cell (``"M4T, M4TD"``) into normalized codes."""
    text = _clean(value)
    if not text:
        return []
    return [_normalize(part) for part in text.split(",") if _normalize(part)]


def _normalize(text: str) -> str:
    """Lower-case and collapse punctuation/whitespace for containment tests."""
    return re.sub(r"[^a-z0-9]+", " ", str(text).lower()).strip()
