from unittest.mock import MagicMock, patch

import pytest

from core.services.UpdateService import UpdateRelease, UpdateService


def test_parse_available_releases_supports_nested_installers():
    service = UpdateService(session=MagicMock(), logger=MagicMock())
    payload = {
        "versions": [
            {
                "version": "2.2.0",
                "notes": "Stability improvements",
                "installers": {
                    "windows": {
                        "url": "https://example.com/ADIAT-2.2.0.exe",
                        "arch": "x64",
                    },
                    "macos": {
                        "url": "https://example.com/ADIAT-2.2.0.dmg",
                        "arch": "arm64",
                        "filename": "ADIAT-2.2.0.dmg",
                    },
                },
            }
        ]
    }

    releases = service.parse_available_releases(payload)

    assert len(releases) == 2
    assert releases[0].version == "2.2.0"
    assert releases[0].matches_platform("windows") is True
    assert releases[0].arch == "x64"
    assert releases[1].filename == "ADIAT-2.2.0.dmg"
    assert releases[1].arch == "arm64"


def test_fetch_available_releases_rejects_non_json_response():
    response = MagicMock()
    response.headers = {"content-type": "text/html; charset=utf-8"}
    response.url = "https://desktop.adiat.app/"
    response.raise_for_status.return_value = None

    session = MagicMock()
    session.get.return_value = response
    service = UpdateService(session=session, logger=MagicMock())

    with pytest.raises(ValueError, match="did not return JSON"):
        service.fetch_available_releases()


def test_update_service_sets_distinct_user_agent():
    session = MagicMock()
    session.headers = {}

    UpdateService(session=session, logger=MagicMock(), app_version="2.1.0 Alpha")

    assert session.headers["User-Agent"] == "ADIAT-Updater/2.1.0 Alpha"


def test_parse_available_releases_infers_platform_and_arch_from_installer_key():
    service = UpdateService(session=MagicMock(), logger=MagicMock())
    payload = {
        "releases": [
            {
                "version": "2.2.0",
                "installers": {
                    "macos-apple": {
                        "url": "https://example.com/ADIAT-apple.dmg",
                    },
                    "macos-intel": {
                        "url": "https://example.com/ADIAT-intel.dmg",
                    },
                },
            }
        ]
    }

    releases = service.parse_available_releases(payload)

    assert len(releases) == 2
    assert all(release.platforms == ("macos",) for release in releases)
    assert {release.arch for release in releases} == {"arm64", "x64"}


def test_get_latest_available_release_prefers_newer_stable_release():
    service = UpdateService(session=MagicMock(), logger=MagicMock())
    releases = [
        UpdateRelease(version="2.1.0 Alpha", installer_url="https://example.com/a.exe", platforms=("windows",), arch="x64"),
        UpdateRelease(version="2.1.0", installer_url="https://example.com/release.exe", platforms=("windows",), arch="x64"),
    ]

    with patch.object(service, "current_platform", return_value="windows"), \
            patch.object(service, "current_arch", return_value="x64"), \
            patch.object(service, "fetch_available_releases", return_value=releases):
        release = service.get_latest_available_release("2.1.0 Alpha")

    assert release is not None
    assert release.version == "2.1.0"


def test_get_latest_available_release_prefers_exact_arch_match():
    service = UpdateService(session=MagicMock(), logger=MagicMock())
    releases = [
        UpdateRelease(version="2.2.0", installer_url="https://example.com/ADIAT-intel.dmg", platforms=("macos",), arch="x64"),
        UpdateRelease(version="2.2.0", installer_url="https://example.com/ADIAT-apple.dmg", platforms=("macos",), arch="arm64"),
    ]

    with patch.object(service, "current_platform", return_value="macos"), \
            patch.object(service, "current_arch", return_value="arm64"), \
            patch.object(service, "fetch_available_releases", return_value=releases):
        release = service.get_latest_available_release("2.1.0")

    assert release is not None
    assert release.installer_url == "https://example.com/ADIAT-apple.dmg"


def test_get_latest_available_release_falls_back_to_generic_arch():
    service = UpdateService(session=MagicMock(), logger=MagicMock())
    releases = [
        UpdateRelease(version="2.2.0", installer_url="https://example.com/ADIAT-generic.dmg", platforms=("macos",)),
        UpdateRelease(version="2.2.0", installer_url="https://example.com/ADIAT-intel.dmg", platforms=("macos",), arch="x64"),
    ]

    with patch.object(service, "current_platform", return_value="macos"), \
            patch.object(service, "current_arch", return_value="arm64"), \
            patch.object(service, "fetch_available_releases", return_value=releases):
        release = service.get_latest_available_release("2.1.0")

    assert release is not None
    assert release.installer_url == "https://example.com/ADIAT-generic.dmg"


def test_download_release_streams_file_and_reports_progress(tmp_path):
    response = MagicMock()
    response.headers = {"content-length": "6"}
    response.iter_content.return_value = [b"abc", b"def"]
    response.raise_for_status.return_value = None

    session = MagicMock()
    session.get.return_value = response
    service = UpdateService(session=session, logger=MagicMock())
    progress_calls = []

    release = UpdateRelease(
        version="2.2.0",
        installer_url="https://example.com/ADIAT-2.2.0.exe",
        platforms=("windows",),
    )

    path = service.download_release(
        release,
        destination_dir=str(tmp_path),
        progress_callback=lambda downloaded, total: progress_calls.append((downloaded, total)),
    )

    assert tmp_path.joinpath("ADIAT-2.2.0.exe").read_bytes() == b"abcdef"
    assert path.endswith("ADIAT-2.2.0.exe")
    assert progress_calls == [(3, 6), (6, 6)]


def test_is_newer_version_compares_beta_build_numbers():
    # A later beta build of the same numeric version is an update...
    assert UpdateService.is_newer_version("2.1.0 Beta 2", "2.1.0 Beta 1") is True
    # ...and an earlier or equal beta build is not.
    assert UpdateService.is_newer_version("2.1.0 Beta 1", "2.1.0 Beta 2") is False
    assert UpdateService.is_newer_version("2.1.0 Beta 1", "2.1.0 Beta 1") is False


def test_is_newer_version_release_supersedes_beta_build():
    # A same-numbered final release is newer than any beta build of it.
    assert UpdateService.is_newer_version("2.1.0", "2.1.0 Beta 9") is True
    assert UpdateService.is_newer_version("2.1.0 Beta 9", "2.1.0") is False


def test_is_newer_version_numeric_bump_ignores_build():
    # A higher numeric version wins regardless of build numbers.
    assert UpdateService.is_newer_version("2.1.1 Beta 1", "2.1.0 Beta 9") is True


def test_get_latest_available_release_picks_highest_beta_build():
    service = UpdateService(session=MagicMock(), logger=MagicMock())
    releases = [
        UpdateRelease(version="2.1.0 Beta 1", installer_url="https://example.com/b1.exe", platforms=("windows",), arch="x64"),
        UpdateRelease(version="2.1.0 Beta 3", installer_url="https://example.com/b3.exe", platforms=("windows",), arch="x64"),
        UpdateRelease(version="2.1.0 Beta 2", installer_url="https://example.com/b2.exe", platforms=("windows",), arch="x64"),
    ]

    with patch.object(service, "current_platform", return_value="windows"), \
            patch.object(service, "current_arch", return_value="x64"), \
            patch.object(service, "fetch_available_releases", return_value=releases):
        release = service.get_latest_available_release("2.1.0 Beta 1")

    assert release is not None
    assert release.version == "2.1.0 Beta 3"


@pytest.mark.skipif(not hasattr(__import__("os"), "startfile"), reason="Windows-specific launcher")
def test_launch_installer_uses_windows_shell():
    service = UpdateService(session=MagicMock(), logger=MagicMock())

    with patch.object(service, "current_platform", return_value="windows"), \
            patch("core.services.UpdateService.os.startfile") as mock_startfile:
        service.launch_installer("C:/Temp/ADIAT.exe")

    mock_startfile.assert_called_once_with("C:/Temp/ADIAT.exe")
