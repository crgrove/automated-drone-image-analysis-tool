from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Sequence, Tuple
from urllib.parse import unquote, urlparse
import os
import platform
import subprocess
import tempfile

import requests
from requests.exceptions import JSONDecodeError as RequestsJSONDecodeError

from core.services.LoggerService import LoggerService
from helpers.PickleHelper import PickleHelper


@dataclass(frozen=True)
class UpdateRelease:
    """Represents a single installer release from the update feed."""

    version: str
    installer_url: str
    platforms: Tuple[str, ...] = ()
    arch: str = ""
    notes: str = ""
    title: str = ""
    filename: str = ""

    def matches_platform(self, current_platform: str) -> bool:
        """Return True when this release applies to the current platform."""
        normalized = {UpdateService.normalize_platform_name(item) for item in self.platforms if item}
        if not normalized or "all" in normalized:
            return True
        return UpdateService.normalize_platform_name(current_platform) in normalized

    def arch_match_rank(self, current_arch: str) -> int:
        """Return how well this release matches the current architecture."""
        normalized_release_arch = UpdateService.normalize_arch_name(self.arch)
        normalized_current_arch = UpdateService.normalize_arch_name(current_arch)

        if not normalized_release_arch or normalized_release_arch == "all":
            return 1
        if normalized_release_arch == normalized_current_arch:
            return 2
        return 0

    def matches_environment(self, current_platform: str, current_arch: str) -> bool:
        """Return True when the release matches the current platform and arch."""
        return self.matches_platform(current_platform) and self.arch_match_rank(current_arch) > 0


class UpdateService:
    """Handle update-feed retrieval, installer download, and installer launch."""

    DEFAULT_FEED_URL = os.environ.get(
        "ADIAT_UPDATE_FEED_URL",
        "https://desktop.adiat.app/version.json"
    )

    def __init__(
        self,
        feed_url: Optional[str] = None,
        session: Optional[requests.Session] = None,
        logger: Optional[LoggerService] = None,
        app_version: str = ""
    ):
        self.feed_url = feed_url or self.DEFAULT_FEED_URL
        self.session = session or requests.Session()
        self.logger = logger or LoggerService()
        self.app_version = app_version.strip()
        self.session.headers.setdefault("User-Agent", self._build_user_agent())

    @staticmethod
    def normalize_platform_name(value: Optional[str]) -> str:
        """Normalize platform names coming from Python and the update feed."""
        if not value:
            return ""

        lowered = str(value).strip().lower()
        aliases = {
            "windows": "windows",
            "win": "windows",
            "win32": "windows",
            "windows-x64": "windows",
            "windows-arm64": "windows",
            "darwin": "macos",
            "mac": "macos",
            "macos": "macos",
            "osx": "macos",
            "macos-apple": "macos",
            "macos-intel": "macos",
            "linux": "linux",
            "all": "all",
            "*": "all",
        }
        return aliases.get(lowered, lowered)

    def current_platform(self) -> str:
        """Return the normalized current platform name."""
        return self.normalize_platform_name(platform.system())

    def current_arch(self) -> str:
        """Return the normalized current CPU architecture."""
        return self.normalize_arch_name(platform.machine())

    @staticmethod
    def normalize_arch_name(value: Optional[str]) -> str:
        """Normalize architecture values from the host and update feed."""
        if not value:
            return ""

        lowered = str(value).strip().lower()
        aliases = {
            "x86_64": "x64",
            "amd64": "x64",
            "x64": "x64",
            "intel": "x64",
            "macos-intel": "x64",
            "windows-x64": "x64",
            "arm64": "arm64",
            "aarch64": "arm64",
            "arm64e": "arm64",
            "apple": "arm64",
            "macos-apple": "arm64",
            "windows-arm64": "arm64",
            "universal": "all",
            "all": "all",
            "*": "all",
        }
        return aliases.get(lowered, lowered)

    def fetch_available_releases(self, timeout: int = 10) -> List[UpdateRelease]:
        """Fetch and parse the update feed."""
        response = self.session.get(self.feed_url, timeout=timeout)
        response.raise_for_status()

        content_type = (response.headers.get("content-type") or "").lower()
        if "json" not in content_type:
            final_url = response.url or self.feed_url
            raise ValueError(
                f"Update feed did not return JSON. Content-Type: {content_type or 'unknown'} | URL: {final_url}"
            )

        try:
            payload = response.json()
        except RequestsJSONDecodeError as exc:
            final_url = response.url or self.feed_url
            raise ValueError(
                f"Update feed returned invalid JSON from {final_url}: {exc}"
            ) from exc

        return self.parse_available_releases(payload)

    def parse_available_releases(self, payload) -> List[UpdateRelease]:
        """Parse a JSON payload into normalized release entries."""
        raw_items = self._coerce_release_items(payload)
        releases: List[UpdateRelease] = []

        for item in raw_items:
            if not isinstance(item, dict):
                continue
            releases.extend(self._parse_release_item(item))

        releases.sort(key=lambda entry: self._version_sort_key(entry.version), reverse=True)
        return releases

    def get_latest_available_release(
        self,
        current_version: str,
        timeout: int = 10
    ) -> Optional[UpdateRelease]:
        """Return the newest compatible release newer than the current version."""
        current_platform = self.current_platform()
        current_arch = self.current_arch()
        releases = self.fetch_available_releases(timeout=timeout)
        compatible_releases = [
            release for release in releases
            if release.matches_environment(current_platform, current_arch)
            and self.is_newer_version(release.version, current_version)
        ]
        if not compatible_releases:
            return None

        compatible_releases.sort(
            key=lambda release: (
                self._version_sort_key(release.version),
                release.arch_match_rank(current_arch),
            ),
            reverse=True,
        )
        return compatible_releases[0]

    def download_release(
        self,
        release: UpdateRelease,
        destination_dir: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        timeout: Tuple[int, int] = (10, 300)
    ) -> str:
        """Download the selected installer and return the local file path."""
        download_dir = Path(destination_dir or Path(tempfile.gettempdir()) / "ADIAT" / "updates")
        download_dir.mkdir(parents=True, exist_ok=True)

        file_name = self._resolve_filename(release)
        target_path = download_dir / file_name

        response = self.session.get(release.installer_url, timeout=timeout, stream=True)
        response.raise_for_status()

        total_bytes = int(response.headers.get("content-length", "0") or "0")
        downloaded = 0

        try:
            with open(target_path, "wb") as handle:
                for chunk in response.iter_content(chunk_size=1024 * 128):
                    if not chunk:
                        continue
                    handle.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total_bytes)
        except Exception:
            if target_path.exists():
                target_path.unlink()
            raise

        return str(target_path)

    def launch_installer(self, installer_path: str) -> None:
        """Open the downloaded installer using the platform default handler."""
        normalized_platform = self.current_platform()

        if normalized_platform == "windows" and hasattr(os, "startfile"):
            os.startfile(installer_path)
            return
        if normalized_platform == "macos":
            subprocess.Popen(["open", installer_path])
            return

        subprocess.Popen(["xdg-open", installer_path])

    @staticmethod
    def is_newer_version(candidate_version: str, current_version: str) -> bool:
        """Compare two ADIAT version strings."""
        try:
            candidate_tuple = PickleHelper._version_to_tuple(candidate_version)
            current_tuple = PickleHelper._version_to_tuple(current_version)
        except ValueError:
            return False

        candidate_numeric = candidate_tuple[:3]
        current_numeric = current_tuple[:3]
        if candidate_numeric != current_numeric:
            return candidate_numeric > current_numeric

        # Lower label values are more stable: release < rc < beta < alpha.
        if candidate_tuple[3] != current_tuple[3]:
            return candidate_tuple[3] < current_tuple[3]

        # Same numeric version and label: a higher build number is newer. This
        # lets successive beta builds (e.g. 2.1.0 Beta 1 -> 2.1.0 Beta 2) be
        # offered without bumping the numeric version.
        return candidate_tuple[4] > current_tuple[4]

    @staticmethod
    def _version_sort_key(version: str) -> Tuple[int, int, int, int, int]:
        """Return a sortable key for ADIAT versions."""
        try:
            major, minor, patch, label_value, build = PickleHelper._version_to_tuple(version)
        except ValueError:
            return (0, 0, 0, -1, -1)
        return (major, minor, patch, -label_value, build)

    @staticmethod
    def _coerce_release_items(payload) -> Sequence[dict]:
        """Extract the release list from a few common feed shapes."""
        if isinstance(payload, list):
            return payload

        if not isinstance(payload, dict):
            return []

        for key in ("versions", "releases", "items", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return value

        if any(key in payload for key in ("version", "tag", "name", "installer_url", "download_url", "url", "installers")):
            return [payload]

        return []

    def _parse_release_item(self, item: dict) -> List[UpdateRelease]:
        """Parse one feed item, including nested platform installer maps."""
        version = self._first_text(item, "version", "tag", "name")
        if not version:
            return []

        notes = self._first_text(item, "notes", "release_notes", "description")
        title = self._first_text(item, "title", "label", "name") or version
        default_filename = self._first_text(item, "filename", "file_name")

        installers = item.get("installers")
        if isinstance(installers, dict):
            releases: List[UpdateRelease] = []
            for platform_name, installer_data in installers.items():
                installer_url, filename = self._extract_installer_fields(installer_data)
                if not installer_url:
                    continue
                platforms = self._normalize_platforms(
                    installer_data.get("platforms") if isinstance(installer_data, dict) else platform_name
                )
                if not platforms:
                    platforms = self._normalize_platforms(platform_name)
                arch = ""
                if isinstance(installer_data, dict):
                    arch = installer_data.get("arch") or ""
                arch = self.normalize_arch_name(arch or platform_name)
                releases.append(
                    UpdateRelease(
                        version=version,
                        installer_url=installer_url,
                        platforms=platforms,
                        arch=arch,
                        notes=notes,
                        title=title,
                        filename=filename or default_filename,
                    )
                )
            return releases

        installer_url = self._first_text(
            item,
            "installer_url",
            "download_url",
            "url",
            "installerUrl",
            "downloadUrl",
        )
        if not installer_url:
            return []

        return [
            UpdateRelease(
                version=version,
                installer_url=installer_url,
                platforms=self._normalize_platforms(item.get("platforms") or item.get("platform") or item.get("os")),
                arch=self.normalize_arch_name(item.get("arch")),
                notes=notes,
                title=title,
                filename=default_filename,
            )
        ]

    def _extract_installer_fields(self, installer_data) -> Tuple[str, str]:
        """Extract installer URL and filename from a nested installer payload."""
        if isinstance(installer_data, str):
            return installer_data.strip(), ""

        if not isinstance(installer_data, dict):
            return "", ""

        installer_url = self._first_text(
            installer_data,
            "installer_url",
            "download_url",
            "url",
            "installerUrl",
            "downloadUrl",
        )
        filename = self._first_text(installer_data, "filename", "file_name")
        return installer_url, filename

    @staticmethod
    def _normalize_platforms(value) -> Tuple[str, ...]:
        """Normalize a string or list of platforms into a tuple."""
        if value is None:
            return ()

        if isinstance(value, (list, tuple, set)):
            items: Iterable = value
        else:
            items = [value]

        normalized = []
        for item in items:
            normalized_item = UpdateService.normalize_platform_name(item)
            if normalized_item and normalized_item not in normalized:
                normalized.append(normalized_item)
        return tuple(normalized)

    @staticmethod
    def _first_text(source: dict, *keys: str) -> str:
        """Return the first non-empty string value for the provided keys."""
        for key in keys:
            value = source.get(key)
            if value is None:
                continue
            text = str(value).strip()
            if text:
                return text
        return ""

    @staticmethod
    def _resolve_filename(release: UpdateRelease) -> str:
        """Resolve the output filename for a downloaded installer."""
        if release.filename:
            return release.filename

        parsed = urlparse(release.installer_url)
        base_name = os.path.basename(parsed.path)
        if base_name:
            return unquote(base_name)

        safe_version = release.version.replace(" ", "_")
        return f"ADIAT_{safe_version}_installer"

    def _build_user_agent(self) -> str:
        """Build a stable User-Agent for update-feed and installer requests."""
        if self.app_version:
            return f"ADIAT-Updater/{self.app_version}"
        return "ADIAT-Updater"
