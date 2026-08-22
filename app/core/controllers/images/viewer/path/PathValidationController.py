"""
PathValidationController - Handles validation and recovery of missing image and mask paths.

This controller manages the UI orchestration for validating that image and mask files exist,
and prompts users to locate missing files when paths are invalid.
"""

import os
import json
from pathlib import Path
from PySide6.QtWidgets import QMessageBox, QFileDialog
from core.services.LoggerService import LoggerService
from core.services.SettingsService import SettingsService
from helpers.TranslationMixin import TranslationMixin
from helpers.PathHelper import (
    cross_platform_basename,
    index_folder_by_filename,
    find_in_index,
    normalize_filename_key,
)


class PathValidationController(TranslationMixin):
    """
    Controller for managing path validation and recovery.

    Handles checking for missing files and prompting users to locate them.
    """

    # Folders that fixed previous relinks, machine-wide, newest first. The
    # parent of a picked folder is remembered too: sibling batch folders under
    # one copied root then resolve without prompting at all.
    RECOVERY_FOLDERS_SETTING = 'ImageRecoveryFolders'
    RECOVERY_FOLDERS_LIMIT = 8

    def __init__(self, parent_viewer):
        """
        Initialize the path validation controller.

        Args:
            parent_viewer: The main Viewer instance
        """
        self.parent = parent_viewer
        self.logger = LoggerService()
        self.settings_service = SettingsService()
        # Set by _ask_retry_or_continue: whether the user chose to load with a
        # partial recovery rather than cancel.
        self._continued = False

    def validate_and_fix_paths(self, images):
        """
        Validate that all image and mask paths exist. Prompt user to select folders if missing.

        Args:
            images: List of image dictionaries to validate

        Returns:
            bool: True if all paths are valid or were fixed, False if user cancelled.
        """
        missing_images = []
        missing_masks = []

        # Check which images and masks are missing
        for image in images:
            image_path = image.get('path', '')
            mask_path = image.get('mask_path', '')

            # cross_platform_basename, not os.path.basename: a result file
            # authored on Windows stores "C:\Flight1\DJI_0042.JPG", and on
            # POSIX os.path.basename returns that whole string as the
            # "filename". Joining it onto the folder the user picks can never
            # match, so recovery reported every image as still missing no
            # matter how correct the chosen folder was.
            # 'stored_path' rides along with the display name: when several
            # files under the chosen folder share this basename (WALDO sortie
            # counters restart, so the name repeats per sortie), the enclosing
            # folders in the original path are the only thing that says WHICH
            # one this entry means. Matching on the bare filename relinked
            # every same-named entry to one file and persisted that into the
            # XML, so AOIs drew at their correct coordinates on the wrong
            # photo.
            if image_path and not os.path.exists(image_path):
                missing_images.append({
                    'image': image,
                    'filename': cross_platform_basename(image_path),
                    'stored_path': image_path,
                })

            if mask_path and not os.path.exists(mask_path):
                missing_masks.append({
                    'image': image,
                    'filename': cross_platform_basename(mask_path),
                    'stored_path': mask_path,
                })

        # Folders that fixed earlier batches usually fix this one too; try
        # them silently so batch 2..N never re-prompts on the same machine
        if missing_images:
            missing_images = self._resolve_from_remembered_folders(missing_images, 'path')
        if missing_masks:
            missing_masks = self._resolve_from_remembered_folders(missing_masks, 'mask_path')

        # Prompt for source images folder if any are missing
        if missing_images:
            if not self._prompt_for_source_folder(missing_images):
                return False  # User cancelled

        # Prompt for masks folder if any are missing
        if missing_masks:
            if not self._prompt_for_mask_folder(missing_masks):
                return False  # User cancelled

        return True

    def _prompt_for_source_folder(self, missing_images):
        """
        Prompt user to select folder containing source images.

        Args:
            missing_images (list): List of dicts with 'image' and 'filename' keys.

        Returns:
            bool: True if successful, False if user cancelled.
        """
        return self._recover_missing_files(
            missing_images,
            path_key='path',
            labels={
                'not_found_title': self.tr("Source Images Not Found"),
                'not_found_message': self.tr(
                    "{count} source image(s) not found at expected locations:\n\n"
                    "{files}\n\n"
                    "Please select the folder containing the source images."
                ),
                'picker_title': self.tr("Select Source Images Folder"),
                'partial_title': self.tr("Some Images Still Missing"),
                'partial_message': self.tr(
                    "Found {found} of {total} images.\n\n"
                    "Still missing:\n{missing}"
                ),
                'none_message': self.tr(
                    "None of the {total} missing images were found in that folder "
                    "(including its subfolders).\n\n"
                    "Expected to find files named:\n{missing}"
                ),
            },
        )

    def _prompt_for_mask_folder(self, missing_masks):
        """
        Prompt user to select folder containing detection masks.

        Args:
            missing_masks (list): List of dicts with 'image' and 'filename' keys.

        Returns:
            bool: True if successful, False if user cancelled.
        """
        return self._recover_missing_files(
            missing_masks,
            path_key='mask_path',
            labels={
                'not_found_title': self.tr("Detection Masks Not Found"),
                'not_found_message': self.tr(
                    "{count} detection mask(s) not found at expected locations:\n\n"
                    "{files}\n\n"
                    "Please select the folder containing the mask files."
                ),
                'picker_title': self.tr("Select Masks Folder"),
                'partial_title': self.tr("Some Masks Still Missing"),
                'partial_message': self.tr(
                    "Found {found} of {total} masks.\n\n"
                    "Still missing:\n{missing}"
                ),
                'none_message': self.tr(
                    "None of the {total} missing masks were found in that folder "
                    "(including its subfolders).\n\n"
                    "Expected to find files named:\n{missing}"
                ),
            },
        )

    @staticmethod
    def _is_filesystem_root(folder):
        """True for drive/filesystem roots, which are too big to index."""
        normalized = os.path.abspath(folder)
        return os.path.dirname(normalized) == normalized

    def _load_remembered_raw(self):
        """Read the stored recovery-folder list without existence filtering.

        Unplugged drives must stay remembered, not be forgotten forever the
        first time a validate runs while they are disconnected.
        """
        raw = self.settings_service.get_setting(self.RECOVERY_FOLDERS_SETTING, '[]')
        try:
            folders = json.loads(raw) if isinstance(raw, str) else list(raw or [])
        except (TypeError, ValueError):
            folders = []
        return [f for f in folders if isinstance(f, str) and f]

    def _remembered_folders(self):
        """Recovery folders worth trying right now (existing, non-root)."""
        return [
            f for f in self._load_remembered_raw()
            if os.path.isdir(f) and not self._is_filesystem_root(f)
        ]

    def _remember_folder(self, folder):
        """Store a folder that just fixed a relink, plus its parent."""
        try:
            candidates = []
            normalized = os.path.abspath(folder)
            parent = os.path.dirname(normalized)
            # Insert the parent first so the picked folder ends up on top
            if parent != normalized and not self._is_filesystem_root(parent):
                candidates.append(parent)
            if not self._is_filesystem_root(normalized):
                candidates.append(normalized)

            stored = self._load_remembered_raw()
            for cand in candidates:
                key = os.path.normcase(cand)
                stored = [f for f in stored if os.path.normcase(f) != key]
                stored.insert(0, cand)
            del stored[self.RECOVERY_FOLDERS_LIMIT:]
            self.settings_service.set_setting(self.RECOVERY_FOLDERS_SETTING, json.dumps(stored))
        except Exception as e:
            self.logger.warning(f"Could not remember recovery folder {folder}: {e}")

    def _resolve_from_remembered_folders(self, missing, path_key):
        """Try previously successful folders before prompting the user.

        Args:
            missing (list): Dicts with 'image' and 'filename' keys.
            path_key (str): Key on the image dict to repair ('path'/'mask_path').

        Returns:
            list: The subset of ``missing`` that is still unresolved.
        """
        remaining = list(missing)
        for folder in self._remembered_folders():
            if not remaining:
                break
            try:
                index = index_folder_by_filename(folder)
            except Exception as e:
                self.logger.warning(f"Could not index remembered folder {folder}: {e}")
                continue

            resolved = {}
            next_remaining = []
            for item in remaining:
                # require_folder_agreement: this branch relinks with no dialog
                # and no confirmation, so a lone same-named file in a
                # remembered folder must not be taken on trust - that is how a
                # whole result set silently moves to another flight line. When
                # it declines, the user is prompted instead of misled.
                located = find_in_index(
                    item.get('stored_path') or item['filename'], index,
                    require_folder_agreement=True)
                if located:
                    resolved[id(item)] = located
                else:
                    next_remaining.append(item)

            if resolved:
                # Point input_dir at the actual folder holding the files when
                # they share one, not at the (possibly much broader) index root
                parents = {os.path.dirname(p) for p in resolved.values()}
                input_dir = parents.pop() if len(parents) == 1 else folder
                self._apply_resolved(remaining, resolved, path_key, input_dir)
                self.logger.info(
                    f"Auto-relinked {len(resolved)} {path_key} entries via "
                    f"remembered folder {folder}"
                )
            remaining = next_remaining
        return remaining

    def _recover_missing_files(self, missing, path_key, labels):
        """Prompt for a replacement folder and relocate *missing* files in it.

        Shared by the image and mask recovery paths: the only differences are
        the dictionary key being repaired and the wording.

        Matching is done against a single recursive index of the chosen folder
        (see :func:`helpers.PathHelper.index_folder_by_filename`) rather than
        one ``os.path.exists`` per candidate. That fixes three separate reasons
        a correct folder used to be rejected:

        * filenames derived from Windows-authored paths (handled upstream by
          ``cross_platform_basename``),
        * drone media nested in subfolders (``DCIM/100MEDIA/...``) - the old
          flat join only ever looked directly inside the chosen folder,
        * case and Unicode-normalization drift between the machine that wrote
          the result file and the one reviewing it.

        A partial match no longer hard-fails the whole load either: the user can
        pick a different folder or continue with what was found.

        Args:
            missing (list): Dicts with 'image' and 'filename' keys.
            path_key (str): Key on the image dict to repair ('path'/'mask_path').
            labels (dict): Pre-translated user-facing strings.

        Returns:
            bool: True to continue loading, False if the user cancelled.
        """
        if not self._confirm_recovery(missing, labels):
            return False

        start_dir = ""
        while True:
            folder = QFileDialog.getExistingDirectory(
                self.parent,
                labels['picker_title'],
                start_dir,
                QFileDialog.ShowDirsOnly
            )
            if not folder:
                return False  # User cancelled

            # Re-open the picker where they last looked, not at the root.
            start_dir = folder

            index = index_folder_by_filename(folder)
            if getattr(index, 'truncated', False):
                # Too many files to index fully: a name's duplicate may never
                # have been reached, so "unique" is not trustworthy here.
                self.logger.warning(
                    f"Indexing of {folder} hit its file limit; duplicate "
                    f"filenames may not have been detected")
            resolved = {}
            still_missing = []
            ambiguous = []
            for item in missing:
                stored = item.get('stored_path') or item['filename']
                located = find_in_index(stored, index)
                if located:
                    resolved[id(item)] = located
                else:
                    still_missing.append(item['filename'])
                    # "Not found" and "found several and cannot tell which"
                    # need different advice: the second is fixed by pointing
                    # at one flight-line folder instead of a shared parent.
                    if len(index.get(
                            normalize_filename_key(
                                cross_platform_basename(stored)), [])) > 1:
                        ambiguous.append(item['filename'])

            if not still_missing:
                self._apply_resolved(missing, resolved, path_key, folder)
                self._remember_folder(folder)
                self.logger.info(
                    f"Relocated {len(resolved)} {path_key} entries to {folder}"
                )
                return True

            # Apply whatever was found before asking, so "Continue Anyway"
            # keeps the partial recovery instead of discarding it.
            self._apply_resolved(missing, resolved, path_key, folder)
            if resolved:
                self._remember_folder(folder)
            self.logger.warning(
                f"Relocated {len(resolved)} of {len(missing)} {path_key} entries "
                f"in {folder}; {len(still_missing)} unresolved"
            )

            if not self._ask_retry_or_continue(
                missing, still_missing, len(resolved), labels, ambiguous
            ):
                return self._continued

    def _confirm_recovery(self, missing, labels):
        """Tell the user what is missing and confirm they want to go looking."""
        file_list = self._format_file_list([item['filename'] for item in missing])
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(labels['not_found_title'])
        msg_box.setText(
            labels['not_found_message'].format(count=len(missing), files=file_list)
        )
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg_box.setDefaultButton(QMessageBox.Ok)
        return msg_box.exec() == QMessageBox.Ok

    def _ask_retry_or_continue(self, missing, still_missing, found_count, labels,
                               ambiguous=None):
        """Offer another folder, continuing partially, or cancelling.

        Args:
            ambiguous (list): Filenames that WERE present but matched several
                files. Without calling these out the dialog says the files
                were not found while they are sitting in the folder, and the
                user has no way to guess that the fix is to pick one
                flight-line folder rather than a shared parent.

        Returns:
            bool: True to loop and pick another folder. False to stop, with
            ``self._continued`` recording whether the user chose to continue
            with a partial recovery (True) or to cancel the load (False).
        """
        missing_list = self._format_file_list(still_missing)
        template = labels['partial_message'] if found_count else labels['none_message']
        text = template.format(
            found=found_count, total=len(missing), missing=missing_list
        )
        if ambiguous:
            text += self.tr(
                "\n\n{count} of these appear more than once in that folder, so "
                "which capture they belong to cannot be determined:\n{files}\n\n"
                "Choose the specific flight/sortie folder rather than a folder "
                "containing several of them."
            ).format(count=len(ambiguous), files=self._format_file_list(ambiguous, limit=5))

        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(labels['partial_title'])
        msg_box.setText(text)
        retry_button = msg_box.addButton(
            self.tr("Choose Another Folder"), QMessageBox.AcceptRole
        )
        continue_button = None
        if found_count:
            # Losing a whole review because one capture of several hundred was
            # deleted is worse than reviewing the ones that are present.
            continue_button = msg_box.addButton(
                self.tr("Continue Anyway"), QMessageBox.DestructiveRole
            )
        msg_box.addButton(QMessageBox.Cancel)
        msg_box.setDefaultButton(retry_button)
        msg_box.exec()

        clicked = msg_box.clickedButton()
        if clicked is retry_button:
            self._continued = False
            return True
        # Guard against clickedButton() being None (dialog dismissed with Esc):
        # `clicked is continue_button` would be True when both are None, which
        # would silently continue a load the user tried to cancel.
        self._continued = continue_button is not None and clicked is continue_button
        return False

    def _apply_resolved(self, missing, resolved, path_key, folder):
        """Write located paths onto the image dicts and persist them.

        Persisting matters as much as the in-memory fix: without it every
        subsequent open of the same result file re-prompts for the same folder.
        Both are best-effort - a result file on read-only media or a shared
        drive must not fail the load.

        Args:
            missing (list): The dicts passed to :meth:`_recover_missing_files`.
            resolved (dict): id(item) -> located path.
            path_key (str): Key to repair ('path' or 'mask_path').
            folder (str): The folder the user chose.
        """
        if not resolved:
            return

        for item in missing:
            located = resolved.get(id(item))
            if not located:
                continue
            item['image'][path_key] = located
            # get_images() resolves a stored absolute path as-is (and
            # os.path.join returns an absolute second argument unchanged, so an
            # absolute mask_path also survives the xml_dir join), which keeps
            # the written value readable by older builds.
            image_xml = item['image'].get('xml')
            if image_xml is not None:
                try:
                    image_xml.set(path_key, located)
                except Exception as e:
                    self.logger.warning(
                        f"Could not update {path_key} in result XML for "
                        f"{item['filename']}: {e}"
                    )

        if path_key == 'path':
            self._update_input_dir(folder)
        self._save_result_file()

    def _update_input_dir(self, folder):
        """Point settings['input_dir'] at the recovered folder.

        Viewer._build_source_images() enumerates the full flight from
        settings['input_dir']. Leaving it at the original capture folder means
        the map, coverage extents and WALDO heading derivation all silently
        fall back to the AOI subset even though the images were just located.
        """
        settings = getattr(self.parent, 'settings', None)
        if isinstance(settings, dict):
            settings['input_dir'] = folder

    def _save_result_file(self):
        """Persist repaired paths to the result XML (best effort)."""
        xml_service = getattr(self.parent, 'xml_service', None)
        xml_path = getattr(self.parent, 'xml_path', None)
        if xml_service is None or not xml_path:
            return
        try:
            xml_service.save_xml_file(xml_path)
        except Exception as e:
            # Read-only media or a locked file: the in-memory repair still
            # stands for this session, so the load continues.
            self.logger.warning(
                f"Could not persist relocated paths to {xml_path}: {e}"
            )

    def _format_file_list(self, filenames, limit=10):
        """Render a bulleted, truncated filename list for a message box."""
        listing = '\n'.join([f"  • {name}" for name in filenames[:limit]])
        if len(filenames) > limit:
            listing += self.tr("\n  ... and {count} more").format(
                count=len(filenames) - limit
            )
        return listing
