"""ReviewMergeService - Fold several reviewers' copies of one run into one.

The multi-reviewer workflow: a processed batch is copied to several
computers, each reviewer flags/comments/moves AOIs in their own copy of
ADIAT_Data.xml, and the coordinator collects just the XMLs. Collating those
naively repeats every run once per reviewer; this service detects copies of
the SAME run (identical detection payload - only the review fields differ),
merges their review data AOI-by-AOI, and reports each run once with combined
reviewer input:

- flagged  = any reviewer flagged it, with a "Flagged by X of N" note;
- comments = concatenated with reviewer attribution;
- a moved AOI uses the first mover's corrected position, and disagreeing
  corrections are called out with each reviewer's coordinates and their
  separation (in SAR, two people relocating a find differently is itself
  information);
- an image hidden by one reviewer stays visible if any reviewer kept it;
- reviewer-created AOIs appear once, attributed to their creator.

Everything merged lives only in the report's in-memory dicts - no results
XML is ever rewritten, so there is no format-compatibility exposure.
"""

import hashlib
import os

from core.services.LoggerService import LoggerService
from core.services.XmlService import XmlService
from helpers.LocationInfo import LocationInfo
from helpers.PathHelper import cross_platform_basename

# Two AOIs in copies of the same run are the same detection when their
# centers agree within this many pixels (the Search Coordinator's rule),
# used when a copy predates run-wide AOI numbers.
CENTER_MATCH_PX = 10


class RunRecord:
    """One parsed results XML: the raw data plus who reviewed it."""

    def __init__(self, xml_path, xml_service, settings, images,
                 folder_label, reviewer_label):
        self.xml_path = xml_path
        self.xml_service = xml_service
        self.settings = settings
        self.images = images
        self.folder_label = folder_label
        self.reviewer_label = reviewer_label


class MergedRun:
    """A run reported once, carrying every reviewer's combined input."""

    def __init__(self, run_name, xml_path, xml_service, settings, images,
                 reviewer_names):
        self.run_name = run_name
        self.xml_path = xml_path
        self.xml_service = xml_service
        self.settings = settings
        self.images = images
        self.reviewer_names = reviewer_names

    @property
    def review_count(self):
        return len(self.reviewer_names)


class ReviewMergeService:
    """Group and merge reviewer copies of the same processed run."""

    def __init__(self, logger=None):
        self.logger = logger or LoggerService()

    # ------------------------------------------------------------------
    # Loading and grouping
    # ------------------------------------------------------------------

    def load_run_records(self, xml_paths):
        """Parse each XML into a RunRecord; unreadable files are skipped."""
        records = []
        for xml_path in xml_paths:
            try:
                xml_service = XmlService(xml_path)
                settings, _ = xml_service.get_settings()
                images = xml_service.get_images()
            except Exception as e:
                self.logger.error(
                    f"Review merge: skipping unreadable results file {xml_path}: {e}")
                continue
            folder_label = self._folder_label(xml_path)
            review_meta = None
            try:
                review_meta = xml_service.get_review_metadata()
            except Exception:
                pass
            reviewer_label = ((review_meta or {}).get('reviewer_name')
                              or folder_label)
            records.append(RunRecord(
                xml_path=xml_path,
                xml_service=xml_service,
                settings=settings,
                images=images,
                folder_label=folder_label,
                reviewer_label=reviewer_label,
            ))
        return records

    def group_records(self, records):
        """Group records whose DETECTION payload is identical.

        Reviewer-created AOIs are excluded from the fingerprint (they differ
        between copies by design); everything the algorithm produced -
        image names and machine AOI centers - must match exactly.

        Returns:
            list[list[RunRecord]]: Groups in first-seen order.
        """
        groups = {}
        order = []
        for record in records:
            key = self._fingerprint(record)
            if key not in groups:
                groups[key] = []
                order.append(key)
            groups[key].append(record)
        return [groups[key] for key in order]

    def merge_group(self, group):
        """Merge one group of same-run records into a MergedRun."""
        first = group[0]
        reviewer_names = [record.reviewer_label for record in group]
        run_name = self._merged_run_name(group)

        if len(group) == 1:
            return MergedRun(
                run_name=run_name,
                xml_path=first.xml_path,
                xml_service=first.xml_service,
                settings=first.settings,
                images=[dict(img) for img in first.images],
                reviewer_names=reviewer_names,
            )

        merged_images = self._merge_images(group)
        return MergedRun(
            run_name=run_name,
            xml_path=first.xml_path,
            xml_service=first.xml_service,
            settings=first.settings,
            images=merged_images,
            reviewer_names=reviewer_names,
        )

    # ------------------------------------------------------------------
    # Merge internals
    # ------------------------------------------------------------------

    def _merge_images(self, group):
        """AOI-by-AOI merge across every record of one run."""
        review_count = len(group)

        # Union of image basenames, first-seen order
        image_keys = []
        per_record_images = []
        for record in group:
            by_name = {}
            for img in record.images:
                key = cross_platform_basename(img.get('path', '')).lower()
                by_name[key] = img
                if key not in image_keys:
                    image_keys.append(key)
            per_record_images.append(by_name)

        merged_images = []
        for image_key in image_keys:
            copies = [(group[i].reviewer_label, per_record_images[i][image_key])
                      for i in range(review_count)
                      if image_key in per_record_images[i]]
            base = dict(copies[0][1])
            # Visible if ANY reviewer kept it visible (flag-positive bias)
            base['hidden'] = all(img.get('hidden', False) for _, img in copies)
            base['areas_of_interest'] = self._merge_aois(copies, review_count)
            merged_images.append(base)
        return merged_images

    def _merge_aois(self, copies, review_count):
        """Merge one image's AOIs across its reviewer copies."""
        merged = []  # list of accumulator dicts

        def find_slot(aoi):
            number = aoi.get('number')
            for slot in merged:
                if number is not None and slot['aoi'].get('number') == number:
                    return slot
            center = aoi.get('center', (0, 0))
            for slot in merged:
                existing = slot['aoi'].get('center', (0, 0))
                if (abs(existing[0] - center[0]) <= CENTER_MATCH_PX
                        and abs(existing[1] - center[1]) <= CENTER_MATCH_PX):
                    return slot
            return None

        for reviewer, img in copies:
            for aoi in img.get('areas_of_interest', []):
                slot = find_slot(aoi)
                if slot is None:
                    slot = {'aoi': dict(aoi), 'flagged_by': [], 'comments': [],
                            'moved': [], 'created_by': None}
                    if aoi.get('user_created', False):
                        slot['created_by'] = reviewer
                    merged.append(slot)
                if aoi.get('flagged', False) and reviewer not in slot['flagged_by']:
                    slot['flagged_by'].append(reviewer)
                comment = (aoi.get('user_comment') or '').strip()
                if comment and (reviewer, comment) not in slot['comments']:
                    slot['comments'].append((reviewer, comment))
                if (aoi.get('user_latitude') is not None
                        and aoi.get('user_longitude') is not None):
                    slot['moved'].append(
                        (reviewer, aoi['user_latitude'], aoi['user_longitude']))

        return [self._finalize_aoi(slot, review_count) for slot in merged]

    def _finalize_aoi(self, slot, review_count):
        """Turn an accumulator into the report-ready merged AOI dict."""
        aoi = slot['aoi']
        aoi['flagged'] = bool(slot['flagged_by'])

        if slot['comments']:
            aoi['user_comment'] = " — ".join(
                f"{reviewer}: {text}" for reviewer, text in slot['comments'])
        else:
            aoi['user_comment'] = ''

        notes = []
        if slot['created_by']:
            notes.append(f"Added by {slot['created_by']}.")
        if slot['flagged_by'] and review_count > 1:
            names = ", ".join(slot['flagged_by'])
            notes.append(
                f"Flagged by {len(slot['flagged_by'])} of {review_count} "
                f"reviewers ({names}).")

        moved = slot['moved']
        if moved:
            # First mover's correction positions the marker and the GPS math
            aoi['user_latitude'] = moved[0][1]
            aoi['user_longitude'] = moved[0][2]
            distinct = self._distinct_positions(moved)
            if len(distinct) > 1:
                spread_m = max(
                    LocationInfo.haversine_m(distinct[0][1], distinct[0][2],
                                             lat, lon)
                    for _, lat, lon in distinct[1:])
                positions = "; ".join(
                    f"{reviewer} ({lat:.6f}, {lon:.6f})"
                    for reviewer, lat, lon in distinct)
                notes.append(
                    f"Position corrected differently by {len(distinct)} "
                    f"reviewers - {positions} - up to {spread_m:.0f} m apart. "
                    f"The first correction is used above.")
            else:
                notes.append(f"Position corrected by {moved[0][0]}.")
        else:
            aoi.pop('user_latitude', None)
            aoi.pop('user_longitude', None)

        if notes:
            # Rendered by the PDF's "Review:" line; never written to XML.
            aoi['review_note'] = " ".join(notes)
        return aoi

    @staticmethod
    def _distinct_positions(moved):
        """Collapse moves that landed on the same spot (< ~0.1 m)."""
        distinct = []
        for reviewer, lat, lon in moved:
            if not any(abs(lat - d[1]) < 1e-6 and abs(lon - d[2]) < 1e-6
                       for d in distinct):
                distinct.append((reviewer, lat, lon))
        return distinct

    def _fingerprint(self, record):
        """Hash of the run's detection payload (review fields excluded)."""
        parts = [str(record.settings.get('algorithm', ''))]
        images = sorted(
            record.images,
            key=lambda img: cross_platform_basename(img.get('path', '')).lower())
        for img in images:
            centers = sorted(
                str(aoi.get('center'))
                for aoi in img.get('areas_of_interest', [])
                if not aoi.get('user_created', False))
            parts.append(
                cross_platform_basename(img.get('path', '')).lower()
                + '|' + ';'.join(centers))
        return hashlib.sha1('\n'.join(parts).encode('utf-8')).hexdigest()

    @staticmethod
    def _folder_label(xml_path):
        """Folder-derived label (parent of an ADIAT_Results directory)."""
        xml_dir = os.path.dirname(os.path.abspath(xml_path))
        folder_name = os.path.basename(xml_dir)
        if folder_name.upper() == "ADIAT_RESULTS":
            parent = os.path.dirname(xml_dir)
            if parent:
                folder_name = os.path.basename(parent)
        return folder_name

    @staticmethod
    def _merged_run_name(group):
        """One name for the run.

        A single copy keeps its folder-derived label (what the scan dialog
        shows). Merged copies sit in per-reviewer folders, so any one folder
        names the reviewer, not the run - there the recorded input_dir names
        the batch every copy came from.
        """
        if len(group) == 1:
            return group[0].folder_label
        input_dir = (group[0].settings or {}).get('input_dir') or ''
        batch = os.path.basename(os.path.normpath(input_dir)) if input_dir else ''
        return batch or group[0].folder_label
