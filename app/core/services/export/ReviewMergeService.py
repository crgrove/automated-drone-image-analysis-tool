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
            images = [dict(img) for img in first.images]
            # Same labeling rule as the merged path: a run holding same-named
            # images in different flight folders shows the distinguishing tail.
            for key, img in zip(self._relative_image_keys(first.images), images):
                img['merge_key'] = key
            return MergedRun(
                run_name=run_name,
                xml_path=first.xml_path,
                xml_service=first.xml_service,
                settings=first.settings,
                images=images,
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

        # Union of image identities, first-seen order. The identity is the
        # path tail below each record's own common root, NOT the basename:
        # a recursive analysis legitimately holds FlightA/a.jpg beside
        # FlightB/a.jpg, and keying on the name alone silently dropped one.
        # The tail travels between reviewer machines (their roots differ,
        # their flight subfolders do not).
        image_keys = []
        per_record_images = []
        for record in group:
            by_key = {}
            for key, img in zip(self._relative_image_keys(record.images),
                                record.images):
                by_key[key] = img
                if key not in image_keys:
                    image_keys.append(key)
            per_record_images.append(by_key)

        merged_images = []
        for image_key in image_keys:
            copies = [(group[i].reviewer_label, per_record_images[i][image_key])
                      for i in range(review_count)
                      if image_key in per_record_images[i]]
            base = dict(copies[0][1])
            # Visible if ANY reviewer kept it visible (flag-positive bias)
            base['hidden'] = all(img.get('hidden', False) for _, img in copies)
            base['areas_of_interest'] = self._merge_aois(copies, review_count)
            # Carry the distinguishing subfolder into report labels; a plain
            # basename stays a basename.
            base['merge_key'] = image_key
            merged_images.append(base)
        return merged_images

    @staticmethod
    def _relative_image_keys(images):
        """Per-image identity: the path tail below the images' common root.

        Distinguishes same-named files in different flight subfolders and
        survives relocation to another machine (only the shared root differs
        between reviewer copies, and it is stripped per record). Separators
        and case are normalized so Windows- and POSIX-authored copies agree.
        """
        parts_per_image = []
        for img in images:
            path = (img.get('path') or '').replace('\\', '/').lower()
            parts_per_image.append([p for p in path.split('/') if p])
        if not parts_per_image:
            return []
        prefix = 0
        while True:
            # Never consume a basename, and stop at the first divergence.
            if any(len(parts) <= prefix + 1 for parts in parts_per_image):
                break
            if len({parts[prefix] for parts in parts_per_image}) != 1:
                break
            prefix += 1
        return ['/'.join(parts[prefix:]) for parts in parts_per_image]

    def _merge_aois(self, copies, review_count):
        """Merge one image's AOIs across its reviewer copies.

        Identity rules (each guards a way findings were being lost):

        * Matching is one-to-one per reviewer copy: two AOIs from the same
          copy can never share a slot, so nearby detections in one review
          cannot collapse into each other.
        * Reviewer-created AOIs never match by number - each copy numbers its
          own additions locally, so two reviewers' independent finds routinely
          share a number. They match only an identical copied payload (a
          shared manual AOI added before the copies were made has the same
          center in every copy).
        * Machine detections with run-wide numbers match by number alone;
          two DIFFERENT valid numbers are two different detections, however
          close their centers. The center-proximity rule survives only for
          pairings where at least one side predates AOI numbers, and picks
          the nearest eligible slot.
        """
        merged = []  # list of accumulator dicts

        def find_slot(aoi, copy_idx):
            def eligible(slot):
                return copy_idx not in slot['copies']

            user_created = aoi.get('user_created', False)
            center = tuple(aoi.get('center', (0, 0)))
            if user_created:
                for slot in merged:
                    if (slot['aoi'].get('user_created', False) and eligible(slot)
                            and tuple(slot['aoi'].get('center', (0, 0))) == center):
                        return slot
                return None

            number = aoi.get('number')
            if number is not None:
                for slot in merged:
                    if (not slot['aoi'].get('user_created', False)
                            and slot['aoi'].get('number') == number
                            and eligible(slot)):
                        return slot

            best = None
            best_dist = None
            for slot in merged:
                slot_aoi = slot['aoi']
                if slot_aoi.get('user_created', False) or not eligible(slot):
                    continue
                if number is not None and slot_aoi.get('number') is not None:
                    continue   # both numbered: number equality already decided
                existing = slot_aoi.get('center', (0, 0))
                dx = abs(existing[0] - center[0])
                dy = abs(existing[1] - center[1])
                if dx <= CENTER_MATCH_PX and dy <= CENTER_MATCH_PX:
                    dist = dx * dx + dy * dy
                    if best is None or dist < best_dist:
                        best, best_dist = slot, dist
            return best

        for copy_idx, (reviewer, img) in enumerate(copies):
            for aoi in img.get('areas_of_interest', []):
                slot = find_slot(aoi, copy_idx)
                if slot is None:
                    slot = {'aoi': dict(aoi), 'flagged_by': [], 'comments': [],
                            'moved': [], 'created_by': None, 'copies': set()}
                    if aoi.get('user_created', False):
                        slot['created_by'] = reviewer
                    merged.append(slot)
                slot['copies'].add(copy_idx)
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

    # Settings fields that are machine/path-bound and legitimately differ
    # between true copies (path recovery may localize them); everything else
    # in the settings IS the analysis identity.
    _FINGERPRINT_EXCLUDED_SETTINGS = {'input_dir', 'output_dir', 'hist_ref_path'}

    def _fingerprint(self, record):
        """Hash of the run's immutable analysis identity (review fields excluded).

        Covers the full analysis settings (minus machine-specific paths), the
        relative image identities, and each machine detection's payload
        (center, radius, area) - not just centers. Two runs over the same
        images with different options or detection geometry are different
        runs, never "reviewer copies"; genuinely ambiguous runs stay separate.
        AOI numbers are excluded: they are backfilled by viewers, so one
        opened and one never-opened copy of the same run must still group.
        """
        settings = record.settings or {}
        setting_parts = []
        for key in sorted(settings):
            if key in self._FINGERPRINT_EXCLUDED_SETTINGS:
                continue
            value = settings[key]
            if isinstance(value, dict):
                value = sorted(value.items())
            setting_parts.append(f"{key}={value!r}")
        parts = ["settings:" + ";".join(setting_parts)]

        keyed = sorted(zip(self._relative_image_keys(record.images), record.images),
                       key=lambda pair: pair[0])
        for image_key, img in keyed:
            detections = sorted(
                f"{aoi.get('center')}|{aoi.get('radius')}|{aoi.get('area')}"
                for aoi in img.get('areas_of_interest', [])
                if not aoi.get('user_created', False))
            parts.append(image_key + '|' + ';'.join(detections))
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
