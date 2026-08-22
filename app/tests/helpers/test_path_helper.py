"""Unit tests for helpers.PathHelper.

These cover the cross-platform path handling that result-file relocation
depends on: a flight analyzed on one platform is routinely reviewed on another,
so filenames must be derived and matched identically everywhere.
"""

import os
import unicodedata

import pytest

from helpers.PathHelper import (
    canonical_path,
    cross_platform_basename,
    find_in_index,
    index_folder_by_filename,
    is_absolute_any_platform,
    normalize_filename_key,
    path_match_key,
)


# ------------------------------ canonical_path ----------------------------- #


def test_canonical_path_collapses_parent_segments():
    """The ".." churn os.path.join leaves behind is removed.

    This is the exact shape get_images produces for a path stored relative to
    the result folder, and the reason a viewer path never compared equal to a
    directory scan's path for the same capture.
    """
    joined = os.path.join("root", "output", "ADIAT_Results", "..", "..", "input", "a.JPG")
    assert canonical_path(joined) == os.path.join("root", "input", "a.JPG")


def test_canonical_path_empty_is_empty():
    assert canonical_path("") == ""
    assert canonical_path(None) == ""


# ------------------------------ path_match_key ----------------------------- #


def test_path_match_key_equates_unnormalized_and_scanned_forms(tmp_path):
    """The two spellings one capture acquires must key identically."""
    scanned = str(tmp_path / "input" / "DJI_0065.JPG")
    resolved = str(tmp_path / "output" / "ADIAT_Results" / ".." / ".." / "input" / "DJI_0065.JPG")
    assert path_match_key(scanned) == path_match_key(resolved)


@pytest.mark.skipif(os.name != "nt", reason="case-insensitive match is a Windows/macOS rule")
def test_path_match_key_is_case_insensitive_on_windows(tmp_path):
    upper = str(tmp_path / "DJI_0042.JPG")
    lower = str(tmp_path / "dji_0042.jpg")
    assert path_match_key(upper) == path_match_key(lower)


def test_path_match_key_separates_distinct_files(tmp_path):
    a = str(tmp_path / "DJI_0042.JPG")
    b = str(tmp_path / "DJI_0043.JPG")
    assert path_match_key(a) != path_match_key(b)


def test_path_match_key_empty_is_empty():
    assert path_match_key("") == ""
    assert path_match_key(None) == ""


# --------------------------- cross_platform_basename ----------------------- #

def test_basename_of_windows_path_on_any_platform():
    """The regression: os.path.basename does not split backslashes on POSIX."""
    stored = r"C:\Users\pilot\Flight1\DJI_0042.JPG"
    assert cross_platform_basename(stored) == "DJI_0042.JPG"


def test_basename_of_unc_path():
    assert cross_platform_basename(r"\\nas\flights\day2\DJI_0007.JPG") == "DJI_0007.JPG"


def test_basename_of_posix_path():
    assert cross_platform_basename("/Volumes/SD/Flight1/DJI_0042.JPG") == "DJI_0042.JPG"


def test_basename_of_mixed_separators():
    assert cross_platform_basename("C:/Flight1\\sub/DJI_0042.JPG") == "DJI_0042.JPG"


def test_basename_of_bare_filename():
    assert cross_platform_basename("DJI_0042.JPG") == "DJI_0042.JPG"


def test_basename_of_empty_is_empty():
    assert cross_platform_basename("") == ""
    assert cross_platform_basename(None) == ""


def test_basename_ignores_trailing_separator():
    assert cross_platform_basename("/Volumes/SD/Flight1/") == "Flight1"
    assert cross_platform_basename("C:\\Flight1\\") == "Flight1"


# --------------------------- is_absolute_any_platform ---------------------- #

def test_windows_drive_path_is_absolute():
    assert is_absolute_any_platform(r"C:\Flight1\img.jpg")
    assert is_absolute_any_platform("C:/Flight1/img.jpg")
    assert is_absolute_any_platform(r"z:\img.jpg")


def test_unc_path_is_absolute():
    assert is_absolute_any_platform(r"\\nas\flights\img.jpg")


def test_posix_path_is_absolute():
    assert is_absolute_any_platform("/Volumes/SD/img.jpg")


def test_relative_paths_are_not_absolute():
    assert not is_absolute_any_platform("Flight1/img.jpg")
    assert not is_absolute_any_platform(r"Flight1\img.jpg")
    assert not is_absolute_any_platform("../Flight1/img.jpg")
    assert not is_absolute_any_platform("")
    assert not is_absolute_any_platform(None)


def test_drive_letter_without_separator_is_not_absolute():
    """"C:img.jpg" is a drive-relative path, not an absolute one."""
    assert not is_absolute_any_platform("C:img.jpg")


# --------------------------- normalize_filename_key ----------------------- #

def test_normalization_key_is_case_insensitive():
    assert normalize_filename_key("DJI_0042.JPG") == normalize_filename_key("dji_0042.jpg")


def test_normalization_key_unifies_nfd_and_nfc():
    """macOS stores filenames decomposed; Windows/Linux compose them."""
    composed = unicodedata.normalize("NFC", "Sétx_01.JPG")
    decomposed = unicodedata.normalize("NFD", "Sétx_01.JPG")
    assert composed != decomposed, "test needs a name that differs between forms"
    assert normalize_filename_key(composed) == normalize_filename_key(decomposed)


def test_normalization_key_of_empty():
    assert normalize_filename_key("") == ""
    assert normalize_filename_key(None) == ""


# --------------------------- index_folder_by_filename --------------------- #

def test_index_finds_nested_files(tmp_path):
    """Drone media is normally nested (DCIM/100MEDIA/...)."""
    nested = tmp_path / "DCIM" / "100MEDIA"
    nested.mkdir(parents=True)
    (nested / "DJI_0042.JPG").write_text("x")
    index = index_folder_by_filename(str(tmp_path))
    assert find_in_index(r"C:\elsewhere\DJI_0042.JPG", index) == str(nested / "DJI_0042.JPG")


def test_index_non_recursive_skips_subfolders(tmp_path):
    nested = tmp_path / "sub"
    nested.mkdir()
    (nested / "a.jpg").write_text("x")
    index = index_folder_by_filename(str(tmp_path), recursive=False)
    assert find_in_index("a.jpg", index) is None


def test_index_matches_case_insensitively(tmp_path):
    (tmp_path / "DJI_0042.jpg").write_text("x")
    index = index_folder_by_filename(str(tmp_path))
    assert find_in_index("DJI_0042.JPG", index) == str(tmp_path / "DJI_0042.jpg")


# --------------------------- duplicate basenames -------------------------- #
#
# Field report lineage: a WALDO dataset whose per-sortie counters restart has
# the same filename in every sortie folder. Recovery kept one path per name
# and matched on the bare filename, so all same-named entries relinked to one
# file - and _apply_resolved persisted that into the result XML. AOIs then
# drew at their recorded (correct) coordinates on the wrong photo: a circle
# on bare ground next to a gallery thumbnail showing the real detection,
# which had been cropped at analysis time from the right file.


def _two_sorties(tmp_path, name="0_000_00_022.jpg"):
    """Same filename under Sortie1 and Sortie2, as WALDO produces."""
    paths = {}
    for sortie in ("Sortie1", "Sortie2"):
        folder = tmp_path / sortie
        folder.mkdir()
        (folder / name).write_text(sortie)
        paths[sortie] = str(folder / name)
    return paths


def test_index_keeps_every_duplicate_candidate(tmp_path):
    _two_sorties(tmp_path)
    index = index_folder_by_filename(str(tmp_path))
    assert len(index[normalize_filename_key("0_000_00_022.jpg")]) == 2


def test_duplicate_basenames_resolve_by_enclosing_folder(tmp_path):
    paths = _two_sorties(tmp_path)
    index = index_folder_by_filename(str(tmp_path))

    # Each stored path finds its OWN sortie, not whichever the walk hit first.
    assert find_in_index(r"D:\Flights\Sortie2\0_000_00_022.jpg", index) == paths["Sortie2"]
    assert find_in_index(r"D:\Flights\Sortie1\0_000_00_022.jpg", index) == paths["Sortie1"]


def test_ambiguous_duplicate_refuses_to_guess(tmp_path):
    """No distinguishing context: report missing rather than poison the XML.

    A wrong answer here is persisted into the result file and silently
    reassigns an AOI to another photo; "still missing" is recoverable.
    """
    _two_sorties(tmp_path)
    index = index_folder_by_filename(str(tmp_path))

    # Bare filename, and a stored path whose folders match neither candidate.
    assert find_in_index("0_000_00_022.jpg", index) is None
    assert find_in_index(r"D:\Elsewhere\Batch9\0_000_00_022.jpg", index) is None


def test_unique_basename_still_resolves_without_folder_context(tmp_path):
    """The ordinary moved-folder case must keep working unchanged."""
    nested = tmp_path / "DCIM" / "100MEDIA"
    nested.mkdir(parents=True)
    (nested / "DJI_0042.JPG").write_text("x")
    index = index_folder_by_filename(str(tmp_path))

    assert find_in_index("DJI_0042.JPG", index) == str(nested / "DJI_0042.JPG")


def test_sibling_flight_lines_do_not_cross_contaminate(tmp_path):
    """The shipped failure, reproduced from the customer's actual tree.

    One capture folder holds two flight lines whose files are named
    identically (0_000_00_NNN.jpg), plus loose copies one level up. The
    analysis ran on Road2; recovery relinked 364 of 370 entries to Road1's
    same-named files and 16 to the loose copies. Every path stayed unique,
    so this is invisible to a duplicate/collapse check - the only tell is
    that the folder no longer matches the one the analysis ran on.
    """
    for rel in ("Source",
                "Source/Images/Road1 North-South",
                "Source/Images/Road2 South-North"):
        folder = tmp_path.joinpath(*rel.split('/'))
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "0_000_00_022.jpg").write_text(rel)

    index = index_folder_by_filename(str(tmp_path))
    located = find_in_index(
        r"E:\SAR\Inyo\Source\Images\Road2 South-North\0_000_00_022.jpg", index)

    assert located == str(
        tmp_path / "Source" / "Images" / "Road2 South-North" / "0_000_00_022.jpg")


def test_sole_candidate_is_trusted_by_default(tmp_path):
    """Interactive recovery: the user just pointed at this folder."""
    (tmp_path / "moved").mkdir()
    (tmp_path / "moved" / "DJI_9.JPG").write_text("x")
    index = index_folder_by_filename(str(tmp_path))

    assert find_in_index(r"D:\Old\Sortie2\DJI_9.JPG", index) is not None


def test_sole_candidate_refused_when_folder_agreement_required(tmp_path):
    """Unattended relink: a lone same-named file is not evidence.

    _resolve_from_remembered_folders relinks with no dialog, so one stray
    same-named file in a remembered folder could move a whole result set to
    another flight line with nobody watching.
    """
    (tmp_path / "Sortie1").mkdir()
    (tmp_path / "Sortie1" / "DJI_9.JPG").write_text("x")
    index = index_folder_by_filename(str(tmp_path))

    assert find_in_index(r"D:\Old\Sortie2\DJI_9.JPG", index,
                         require_folder_agreement=True) is None
    # ... but the matching sortie still resolves unattended.
    assert find_in_index(r"D:\Old\Sortie1\DJI_9.JPG", index,
                         require_folder_agreement=True) is not None


def test_truncated_index_is_flagged(tmp_path):
    """A cut-short walk can hide a duplicate, making it look unique."""
    for i in range(10):
        (tmp_path / f"f{i}.jpg").write_text("x")

    full = index_folder_by_filename(str(tmp_path))
    partial = index_folder_by_filename(str(tmp_path), max_entries=3)

    assert full.truncated is False
    assert partial.truncated is True


def test_deeper_folder_agreement_wins(tmp_path):
    """More matching enclosing folders beats fewer."""
    shallow = tmp_path / "Sortie2"
    shallow.mkdir()
    (shallow / "img.jpg").write_text("x")
    deep = tmp_path / "Day2" / "Sortie2"
    deep.mkdir(parents=True)
    (deep / "img.jpg").write_text("x")
    index = index_folder_by_filename(str(tmp_path))

    located = find_in_index(r"E:\Capture\Day2\Sortie2\img.jpg", index)
    assert located == str(deep / "img.jpg")


def test_index_of_missing_folder_is_empty():
    assert index_folder_by_filename("/definitely/not/a/folder") == {}
    assert index_folder_by_filename("") == {}


def test_index_respects_max_entries(tmp_path):
    for i in range(10):
        (tmp_path / f"f{i}.jpg").write_text("x")
    index = index_folder_by_filename(str(tmp_path), max_entries=3)
    assert len(index) == 3


def test_index_is_deterministic(tmp_path):
    for name in ("b.jpg", "a.jpg", "c.jpg"):
        (tmp_path / name).write_text("x")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "d.jpg").write_text("x")
    first = index_folder_by_filename(str(tmp_path))
    second = index_folder_by_filename(str(tmp_path))
    assert first == second


def test_find_in_index_miss_returns_none(tmp_path):
    (tmp_path / "a.jpg").write_text("x")
    index = index_folder_by_filename(str(tmp_path))
    assert find_in_index("nope.jpg", index) is None
    assert find_in_index("", index) is None


def test_index_uses_os_sep_paths(tmp_path):
    (tmp_path / "a.jpg").write_text("x")
    index = index_folder_by_filename(str(tmp_path))
    assert all(os.path.isabs(p) for p in index[normalize_filename_key("a.jpg")])
