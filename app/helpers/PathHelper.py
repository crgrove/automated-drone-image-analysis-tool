"""PathHelper - cross-platform path utilities for relocated result files.

``ADIAT_Data.xml`` travels between machines: a flight analyzed on a Windows
ground station is routinely reviewed on a Mac, results are shared between
searchers, and folders get moved onto external drives between the analysis and
the review. The stored image and mask paths are whatever the *analyzing*
machine wrote, so any code that re-derives a filename or re-locates a moved
file has to be agnostic about:

* **separators** - ``os.path`` is platform-bound. On POSIX a backslash is an
  ordinary filename character, so ``os.path.basename`` returns a
  Windows-authored path whole instead of its last component.
* **case** - ``DJI_0042.JPG`` vs ``DJI_0042.jpg``.
* **Unicode normalization** - macOS stores filenames decomposed (NFD) while
  Windows and most Linux tooling produce composed (NFC), so the same name can
  differ byte-for-byte across machines.
"""

import os
import unicodedata

_SEPARATORS = ('/', '\\')


def cross_platform_basename(path):
    """Return the last component of *path*, splitting on both / and \\.

    ``os.path.basename`` only recognizes the running platform's separator, so
    on macOS/Linux a Windows-authored path such as
    ``C:\\Flight1\\DJI_0042.JPG`` comes back unchanged. Result files move
    between machines, so filenames must be derived identically everywhere.

    Args:
        path (str): A path written by any platform, absolute or relative.

    Returns:
        str: The final path component, or '' when *path* is empty.
    """
    if not path:
        return ''
    normalized = path
    for sep in _SEPARATORS:
        normalized = normalized.replace(sep, os.sep)
    return os.path.basename(normalized.rstrip(os.sep))


def is_absolute_any_platform(path):
    """True when *path* is absolute on the platform that wrote it.

    ``os.path.isabs`` is platform-bound, so on POSIX it reports a Windows
    drive-letter path (``C:\\Flight1\\img.jpg``) or a UNC path
    (``\\\\nas\\flights\\img.jpg``) as *relative*. Joining such a path onto a
    local directory produces a nonsense path, which then fails to resolve for a
    reason that has nothing to do with where the file actually is.

    Args:
        path (str): A path written by any platform.

    Returns:
        bool: True if the path is absolute under POSIX or Windows rules.
    """
    if not path:
        return False
    if os.path.isabs(path):
        return True
    # UNC share, e.g. \\nas\flights\img.jpg
    if path.startswith('\\\\'):
        return True
    # Windows drive letter, e.g. C:\flights\img.jpg or C:/flights/img.jpg
    if len(path) >= 3 and path[1] == ':' and path[0].isalpha() and path[2] in _SEPARATORS:
        return True
    return False


def is_filesystem_root(path):
    """True for drive/filesystem roots, which are too big to index.

    Recovery code walks candidate folders recursively; pointing that walk at
    ``C:\\`` or ``/`` would index the whole machine, so roots are excluded
    everywhere a folder is remembered or tried.

    Args:
        path (str): A local folder path.

    Returns:
        bool: True when *path* names a filesystem root.
    """
    normalized = os.path.abspath(path)
    return os.path.dirname(normalized) == normalized


def canonical_path(path):
    """Return *path* with redundant separators and ``..`` segments collapsed.

    ``get_images`` rebuilds a stored relative path by joining it onto the
    result folder, and ``os.path.join`` does not normalize: a path stored as
    ``../../input/DJI_0065.JPG`` resolves to
    ``...\\output\\ADIAT_Results\\..\\..\\input\\DJI_0065.JPG``. That opens the
    right file, so nothing looks wrong, but it never compares equal to the
    ``...\\input\\DJI_0065.JPG`` that a directory scan produces for the same
    capture. Normalizing once at the point of resolution keeps every
    downstream ``==`` honest.

    Args:
        path (str): A resolved path.

    Returns:
        str: The normalized path, or '' when *path* is empty.
    """
    if not path:
        return ''
    return os.path.normpath(path)


def path_match_key(path):
    """Return a key that is equal for any two paths naming the same file.

    Collapses the three ways one file acquires two spellings on a single
    machine: unnormalized ``..`` segments, separator differences, and case
    (``DJI_0042.JPG`` vs ``DJI_0042.jpg``, which name one file on Windows and
    macOS). Unicode is composed for the same reason
    :func:`normalize_filename_key` composes it.

    For deciding identity only -- never store or open the value it returns,
    since ``os.path.normcase`` is lossy on Windows.

    Args:
        path (str): A path, absolute or relative to the current directory.

    Returns:
        str: Comparison key, or '' when *path* is empty.
    """
    if not path:
        return ''
    return os.path.normcase(unicodedata.normalize('NFC', os.path.abspath(path)))


def normalize_filename_key(filename):
    """Return a case- and Unicode-insensitive matching key for *filename*.

    Args:
        filename (str): A bare filename (not a path).

    Returns:
        str: Key suitable for dictionary lookup, or '' when *filename* is empty.
    """
    if not filename:
        return ''
    return unicodedata.normalize('NFC', filename).casefold()


def split_path_components(path):
    """Split *path* into its components, honouring both separators.

    Args:
        path (str): A path written by any platform.

    Returns:
        list[str]: Components, outermost first. Empty for an empty path.
    """
    if not path:
        return []
    normalized = path
    for sep in _SEPARATORS:
        normalized = normalized.replace(sep, os.sep)
    return [part for part in normalized.split(os.sep) if part]


def cross_platform_path_key(path):
    """Full separator/case/Unicode-normalized form of *path* for map lookups.

    The identity maps built by :func:`build_image_cache_identities` are keyed
    with this, so a consumer can look a path up however its platform spelled
    it. Comparison only - never store or open the value.

    Args:
        path (str): A path written by any platform.

    Returns:
        str: Normalized key, or '' when *path* is empty.
    """
    if not path:
        return ''
    joined = '/'.join(split_path_components(path))
    return unicodedata.normalize('NFC', joined).casefold()


def build_image_cache_identities(paths, input_root=None):
    """Map each image path to its dataset-relative cache identity.

    The AOI caches (thumbnails on disk, colors/temperatures in memory) need a
    per-image key that is unique WITHIN a dataset - a bare filename or fixed
    tail is not, because drone filenames repeat across nested flight folders
    (FlightA/DCIM/100MEDIA/DJI_0001.JPG vs FlightB/DCIM/100MEDIA/...) - while
    still surviving the dataset moving to another machine. The identity is the
    path below the dataset root:

    * A path under *input_root* (the analysis input directory, which the
      analysis writes into the results XML) keeps everything after it. This
      is exact, covers the writer and every un-moved dataset, and two images
      can never share it (relative paths within one tree are unique).
    * Remaining paths (a dataset relinked onto another machine) fall back to
      stripping the longest common leading components of that group, never
      consuming a basename - a structure-preserving copy then reproduces the
      original identities whenever the dataset has more than one top-level
      folder. A copy that rearranged the tree simply misses the cache and
      regenerates, which is the safe direction.

    The finished map is validated for uniqueness: a fallback identity that
    lands on a rooted image's identity is DROPPED, not registered. A partial
    relocation (one flight folder relinked while the rest stayed put) can
    otherwise over-strip the moved group down to identities the rooted images
    already own, and the colliding image would be served the rooted image's
    cached thumbnail. A dropped identity sends that image to the exact
    full-path key namespace - a cache miss and regeneration, never a wrong
    image.

    Args:
        paths (Iterable[str]): Every image path in the dataset. Pass the FULL
            set - a filtered subset shifts the common root and changes keys.
        input_root (str): The dataset's analysis input directory, when known.

    Returns:
        dict: :func:`cross_platform_path_key` of each path -> identity string
        (casefolded, '/'-joined). Empty paths, and paths whose identity could
        not be established uniquely, are absent.
    """
    root_parts = split_path_components(input_root) if input_root else []
    root_key = [unicodedata.normalize('NFC', p).casefold() for p in root_parts]

    rooted = {}
    unrooted = []
    for path in paths:
        parts = split_path_components(path)
        if not parts:
            continue
        folded = [unicodedata.normalize('NFC', p).casefold() for p in parts]
        if root_key and len(folded) > len(root_key) and folded[:len(root_key)] == root_key:
            rooted[cross_platform_path_key(path)] = '/'.join(folded[len(root_key):])
        else:
            unrooted.append((path, folded))

    # Relative paths below one root are unique per normalized path, so the
    # rooted entries can never collide with each other - only a fallback
    # identity can land on one of them.
    identities = dict(rooted)
    rooted_identities = set(rooted.values())

    if unrooted:
        prefix = 0
        while True:
            if any(len(folded) <= prefix + 1 for _path, folded in unrooted):
                break
            if len({folded[prefix] for _path, folded in unrooted}) != 1:
                break
            prefix += 1
        for path, folded in unrooted:
            identity = '/'.join(folded[prefix:])
            if identity in rooted_identities:
                continue  # cannot be established uniquely - full-path fallback
            identities[cross_platform_path_key(path)] = identity

    return identities


def cross_platform_path_tail(path, components=2):
    """Return the last *components* path components as one matching key.

    The cache services key persisted artifacts (AOI thumbnails) by image
    identity. A bare filename is not an identity: drone filenames repeat
    across flights and sorties (WALDO per-sortie counters restart, every DJI
    flight has a DJI_0001.JPG), so the enclosing folder must be part of the
    key - while the machine-specific root must NOT be, or the cache would die
    the moment a results folder moves to another machine. The tail (parent
    folder + filename by default) is the portable middle ground.

    Splits on both separator styles, joins with '/', and case/Unicode-folds,
    so Windows- and POSIX-authored paths to the same file produce one key.

    Args:
        path (str): A path written by any platform, absolute or relative.
        components (int): How many trailing components to keep. A path with
            fewer components yields what it has (a bare filename stays one).

    Returns:
        str: Matching key, e.g. ``'sortie2/0_000_00_022.jpg'``, or '' when
        *path* is empty.
    """
    parts = split_path_components(path)
    if not parts:
        return ''
    return unicodedata.normalize('NFC', '/'.join(parts[-components:])).casefold()


class FolderIndex(dict):
    """A filename index that remembers whether its walk was cut short.

    A plain dict cannot say "there may be more of these": a truncated walk
    yields an index where a duplicated name can appear unique, which is
    exactly the state :func:`find_in_index`'s ambiguity guard exists to
    catch. Subclassing keeps every existing dict use working unchanged.
    """

    truncated = False


def index_folder_by_filename(folder, recursive=True, max_entries=200000):
    """Map normalized filename -> every path under *folder* bearing that name.

    Built once per recovery rather than stat-ing each candidate individually: a
    flight folder holds thousands of captures and the caller has thousands of
    names to resolve against it, so one walk beats N syscalls per name. Nested
    layouts are the norm for drone media (``DCIM/100MEDIA/...``), so the walk
    recurses by default.

    EVERY match is kept, not just the first. Duplicate basenames are normal in
    this data, not an edge case: WALDO's per-sortie counters restart, so
    sortie2 has its own ``0_000_00_022.jpg`` colliding with sortie1's. Keeping
    one path per name silently relinked all of them to whichever file the walk
    reached first, and the repaired paths were persisted back into the result
    XML - AOIs then drew at their recorded (correct) coordinates on the wrong
    photo, which is bare ground. :func:`find_in_index` is what chooses among
    the candidates, and it needs to see all of them to do that.

    ``os.walk`` is top-down and directory names are sorted, so the traversal
    and hence each candidate list is deterministic (shallowest first).

    Args:
        folder (str): Directory to index.
        recursive (bool): Walk subdirectories. When False, only *folder* itself.
        max_entries (int): Safety bound on files examined, so pointing the
            recovery at a huge tree (a home directory, a whole volume) cannot
            hang the GUI thread indefinitely.

    Returns:
        dict: normalized filename -> list of absolute paths, shallowest first.
        Empty when *folder* is not a readable directory.
    """
    index = FolderIndex()
    if not folder or not os.path.isdir(folder):
        return index

    examined = 0
    for root, dirs, files in os.walk(folder):
        dirs.sort()
        for name in sorted(files):
            key = normalize_filename_key(name)
            if key:
                index.setdefault(key, []).append(os.path.join(root, name))
            examined += 1
            if examined >= max_entries:
                # Stopping mid-walk can hide a name's duplicate, which would
                # make an ambiguous name look unique and defeat the guard in
                # find_in_index. Flag it so callers can say so rather than
                # relink on a half-built picture.
                index.truncated = True
                return index
        if not recursive:
            break
    return index


def _trailing_match_score(stored_components, candidate_components):
    """Count path components shared by two paths, counting back from the file.

    The filename itself is excluded (all candidates share it by construction),
    so the score is how much *enclosing* structure the two paths agree on:
    ``.../Sortie2/0_000_00_022.jpg`` scores 1 against a candidate under
    ``Sortie2`` and 0 against one under ``Sortie1``.
    """
    score = 0
    for stored, candidate in zip(reversed(stored_components[:-1]),
                                 reversed(candidate_components[:-1])):
        if normalize_filename_key(stored) != normalize_filename_key(candidate):
            break
        score += 1
    return score


def find_in_index(stored_path, index, require_folder_agreement=False):
    """Resolve *stored_path* against a pre-built folder *index*.

    With one candidate this is a plain lookup. With several - same filename in
    several sortie folders - the enclosing folders decide: the candidate
    sharing the most trailing path components with *stored_path* wins.

    An ambiguous match resolves to None rather than to a guess. Callers persist
    what this returns into the result XML, so a wrong answer is not a transient
    mistake: it silently rewrites which photo an AOI belongs to, and the next
    reviewer has no way to tell. Reporting the file as still missing is
    recoverable; picking the wrong file is not.

    Args:
        stored_path (str): The path recorded in the result file, from any
            platform. Pass the FULL stored path, not just its basename -
            a bare filename carries no context to disambiguate with.
        index (dict): Mapping from :func:`index_folder_by_filename`.
        require_folder_agreement (bool): Reject even a SOLE candidate unless
            it shares an enclosing folder with *stored_path*. For unattended
            matching, where no one is watching the result: a folder indexed
            from memory can hold exactly one same-named file that belongs to
            a different flight line, and a lone candidate is otherwise taken
            on trust. Interactive recovery leaves this False - there the user
            has just pointed at the folder and said these are the files, so
            a plain move into an unrelated folder name must still resolve.

    Returns:
        str or None: The located path, None when the filename is absent from
        the index or when several candidates are equally plausible.
    """
    candidates = index.get(normalize_filename_key(cross_platform_basename(stored_path)))
    if not candidates:
        return None

    stored_components = split_path_components(stored_path)
    if len(candidates) == 1:
        if require_folder_agreement and _trailing_match_score(
                stored_components, split_path_components(candidates[0])) <= 0:
            return None
        return candidates[0]

    best_score = -1
    best = None
    tied = False
    for candidate in candidates:
        score = _trailing_match_score(stored_components, split_path_components(candidate))
        if score > best_score:
            best_score, best, tied = score, candidate, False
        elif score == best_score:
            tied = True

    # A zero-scoring winner shares no enclosing folder with the stored path,
    # so nothing distinguishes it from its rivals but walk order.
    if tied or best_score <= 0:
        return None
    return best
