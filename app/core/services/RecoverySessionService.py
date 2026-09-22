"""RecoverySessionService - Session-scoped folder candidates for image relinking.

A "Load Results Folder" scan often surfaces several runs whose source images
moved along with the scanned tree. This session object remembers the scanned
root (plus any folder the user picks at a relink prompt during the session) so
each subsequently opened run tries those folders silently before prompting,
and it shares the expensive recursive folder index between runs instead of
rebuilding it per viewer.

Deliberately NOT persisted: scan roots are often huge trees whose indexes
would slow every future unrelated open, and the "same scan" scope the feature
needs is exactly one session. Machine-wide persistence stays with
PathValidationController's ImageRecoveryFolders setting.
"""

import os

from core.services.LoggerService import LoggerService
from helpers.PathHelper import find_in_index, index_folder_by_filename, is_filesystem_root


class RecoverySession:
    """Folder candidates and cached folder indexes for one results-folder scan."""

    def __init__(self, scan_root):
        """
        Args:
            scan_root (str): The folder the user scanned for results.
        """
        self.scan_root = os.path.abspath(scan_root)
        self.logger = LoggerService()
        # Folders the user picked at relink prompts this session, newest first.
        self._picked = []
        # normcase(abspath(folder)) -> FolderIndex, built lazily on first use.
        self._indexes = {}

    def matches_root(self, folder):
        """True when *folder* is the root this session was built for.

        Args:
            folder (str): A folder path to compare against the scan root.

        Returns:
            bool: True when both name the same directory.
        """
        if not folder:
            return False
        return os.path.normcase(os.path.abspath(folder)) == os.path.normcase(self.scan_root)

    def remember(self, folder):
        """Record a folder the user picked at a relink prompt.

        Picked folders are tried before the scan root: the user just told us
        where this batch's files live, so siblings from the same scan should
        look there first.

        Args:
            folder (str): The folder the user chose.
        """
        if not folder:
            return
        normalized = os.path.abspath(folder)
        if is_filesystem_root(normalized):
            return
        key = os.path.normcase(normalized)
        self._picked = [f for f in self._picked if os.path.normcase(f) != key]
        self._picked.insert(0, normalized)

    def candidate_folders(self):
        """Folders worth trying silently, best first.

        Returns:
            list: Session picks (newest first) then the scan root, filtered to
            directories that exist and are not filesystem roots.
        """
        candidates = list(self._picked) + [self.scan_root]
        folders = []
        seen = set()
        for folder in candidates:
            key = os.path.normcase(folder)
            if key in seen:
                continue
            seen.add(key)
            if os.path.isdir(folder) and not is_filesystem_root(folder):
                folders.append(folder)
        return folders

    def resolve_file(self, stored_path):
        """Locate one recorded file under the session's folders, or None.

        The same silent-relink safety contract as the interactive recovery:
        with several same-named candidates the enclosing folders must agree
        (``require_folder_agreement``), and a resolved path is re-verified on
        disk because cached indexes can go stale mid-session.

        Args:
            stored_path (str): The path recorded in a result file, from any
                platform.

        Returns:
            str | None: The located path, or None when not found/ambiguous.
        """
        if not stored_path:
            return None
        for folder in self.candidate_folders():
            try:
                index = self.get_index(folder)
            except Exception as e:
                self.logger.warning(f"Could not index session folder {folder}: {e}")
                continue
            located = find_in_index(stored_path, index, require_folder_agreement=True)
            if located and os.path.exists(located):
                return located
        return None

    def find_files_by_extension(self, extensions):
        """All files under the session's folders bearing one of *extensions*.

        Reuses the cached folder indexes, so after the first call for a folder
        this is a dictionary sweep, not a disk walk. Used to discover flight
        support files (WALDO trigger KMLs, track logs) inside the scanned tree
        without asking the user where they are.

        Args:
            extensions (tuple): Lowercase extensions including the dot,
                e.g. ('.kml', '.gpx', '.csv').

        Returns:
            list: Absolute paths, deduped, session picks' files first.
        """
        exts = tuple(e.lower() for e in extensions)
        found = []
        seen = set()
        for folder in self.candidate_folders():
            try:
                index = self.get_index(folder)
            except Exception as e:
                self.logger.warning(f"Could not index session folder {folder}: {e}")
                continue
            for paths in index.values():
                for path in paths:
                    if not path.lower().endswith(exts):
                        continue
                    key = os.path.normcase(path)
                    if key in seen:
                        continue
                    seen.add(key)
                    found.append(path)
        return found

    def get_index(self, folder):
        """Return the recursive filename index for *folder*, cached per session.

        The cache is what makes opening run 2..N from one scan cheap: the scan
        root is indexed once, not once per viewer. Cached entries can go stale
        if files move mid-session, so callers must re-verify a resolved path
        with ``os.path.exists`` before trusting it.

        Args:
            folder (str): Folder to index.

        Returns:
            FolderIndex: Mapping of normalized filename -> matching paths.
        """
        key = os.path.normcase(os.path.abspath(folder))
        index = self._indexes.get(key)
        if index is None:
            index = index_folder_by_filename(folder)
            if getattr(index, 'truncated', False):
                self.logger.warning(
                    f"Indexing of {folder} hit its file limit; duplicate "
                    f"filenames may not have been detected"
                )
            self._indexes[key] = index
        return index
