"""Audit an ADIAT results XML for wrong-thumbnail causes.

Run this on the machine showing the symptom, against that machine's copy of
the results XML. It checks, in order of likelihood:

1. RELINK COLLAPSE - path recovery matches missing files by FILENAME against
   a recursive index that keeps one path per name (first match wins). On a
   dataset with duplicate basenames (WALDO sortie counters restart, so
   sortie2's 0_00123.jpg collides with sortie1's), every same-named image
   relinks to the same single file, and the repaired paths are persisted
   back into this XML. Fingerprint: multiple <image> entries sharing one
   identical path. Symptom: the gallery thumb (cached at analysis time, so
   correct) doesn't match the image the click zooms into (the wrong
   same-named file).

2. THUMBNAIL CACHE-KEY COLLISIONS - the disk cache (loose .jpg and
   thumbnails.db alike) is keyed by md5("v3:" + identity + center + radius),
   where the identity is the image's dataset-relative path (below the
   analysis input root, else below the image set's common root). Two AOIs
   collide only when their images share that WHOLE relative path with
   identical center+radius. (Older builds keyed on the bare basename (v1)
   or a two-component tail (v2); those entries are orphaned by the version
   prefix and regenerate rather than ever being served.)

Usage:
    python scripts/audit_thumbnail_keys.py <path\\to\\ADIAT_Data.xml>

Exit code 1 if either problem was found, 0 otherwise.
"""

import hashlib
import os
import sys
import unicodedata
from ast import literal_eval
from collections import defaultdict
from xml.etree import ElementTree


def _folded_components(path):
    """Split *path* on both separators; casefold and NFC-normalize each part."""
    normalized = (path or '').replace('\\', '/')
    return [unicodedata.normalize('NFC', part).casefold()
            for part in normalized.split('/') if part]


def image_identities(paths, input_root=None):
    """Reproduce helpers.PathHelper.build_image_cache_identities exactly.

    Returns {path: identity} keyed by the ORIGINAL path strings given.
    """
    root_key = _folded_components(input_root) if input_root else []
    identities = {}
    unrooted = []
    for path in paths:
        folded = _folded_components(path)
        if not folded:
            continue
        if root_key and len(folded) > len(root_key) and folded[:len(root_key)] == root_key:
            identities[path] = '/'.join(folded[len(root_key):])
        else:
            unrooted.append((path, folded))
    if unrooted:
        prefix = 0
        while True:
            if any(len(folded) <= prefix + 1 for _path, folded in unrooted):
                break
            if len({folded[prefix] for _path, folded in unrooted}) != 1:
                break
            prefix += 1
        for path, folded in unrooted:
            identities[path] = '/'.join(folded[prefix:])
    return identities


def cache_key(identity, center, radius):
    """Reproduce ThumbnailCacheService.get_cache_key exactly.

    *identity* is the image's dataset-relative identity from
    image_identities() - the same one the production writer registers, so the
    'v3' namespace applies.
    """
    identifier = f"v3:{identity}:{center[0]}:{center[1]}:{radius}"
    return hashlib.md5(identifier.encode()).hexdigest()


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2

    xml_path = sys.argv[1]
    root = ElementTree.parse(xml_path).getroot()

    settings_xml = root.find('settings')
    input_root = settings_xml.get('input_dir', '') if settings_xml is not None else ''

    images_node = root.find('images')
    image_nodes = list(images_node) if images_node is not None else list(root.iter('image'))

    # Identities need the FULL image set (the fallback root is their common
    # prefix), so collect the paths before keying any AOI.
    all_paths = [image_xml.get('path') for image_xml in image_nodes if image_xml.get('path')]
    identities = image_identities(all_paths, input_root=input_root or None)

    by_basename = defaultdict(list)   # basename -> [path, ...]
    by_path = defaultdict(int)        # exact path -> how many <image> entries use it
    by_key = defaultdict(list)        # cache key -> [(path, aoi number, center, radius)]
    total_aois = 0

    for image_xml in image_nodes:
        path = image_xml.get('path')
        if not path:
            continue
        basename = os.path.basename(path)
        by_basename[basename].append(path)
        by_path[os.path.normcase(path)] += 1

        # Mirror XmlService.get_images: every DIRECT child of <image> is an
        # AOI regardless of tag name (the writer emits one <areas_of_interest>
        # element per AOI; there is no wrapper element).
        for aoi_xml in image_xml:
            if aoi_xml.get('center') is None:
                continue  # defensive: not AOI-shaped
            total_aois += 1
            try:
                center = literal_eval(aoi_xml.get('center'))
                radius = int(aoi_xml.get('radius', '0'))
            except (ValueError, SyntaxError):
                continue
            key = cache_key(identities.get(path, ''), center, radius)
            by_key[key].append((path, aoi_xml.get('number'), center, radius))

    dup_names = {name: paths for name, paths in by_basename.items() if len(paths) > 1}
    collapsed = {p: n for p, n in by_path.items() if n > 1}
    collisions = {k: hits for k, hits in by_key.items()
                  if len({p for p, *_ in hits}) > 1}

    print(f"Images: {sum(len(p) for p in by_basename.values())}   AOIs: {total_aois}")

    print(f"\nRELINK COLLAPSE (multiple <image> entries pointing at ONE file): "
          f"{len(collapsed)}")
    for path, n in sorted(collapsed.items())[:20]:
        print(f"  x{n}  {path}")
    if len(collapsed) > 20:
        print(f"  ... and {len(collapsed) - 20} more")
    if collapsed:
        total_affected = sum(collapsed.values()) - len(collapsed)
        print(f"  => {total_affected} image entries are displaying the WRONG file.")
        print("  Fix: on this machine, clear the ImageRecoveryFolders setting,")
        print("  restore the original XML (or re-copy it), and when re-linking")
        print("  pick each sortie folder individually, not a shared parent.")

    print(f"\nDuplicate basenames: {len(dup_names)}")
    for name, paths in sorted(dup_names.items())[:20]:
        print(f"  {name}  x{len(paths)}")
        for p in paths[:4]:
            print(f"      {p}")
    if len(dup_names) > 20:
        print(f"  ... and {len(dup_names) - 20} more")

    print(f"\nThumbnail cache-key COLLISIONS (cross-image, same key): {len(collisions)}")
    for key, hits in sorted(collisions.items())[:20]:
        print(f"  key {key[:12]}...")
        for path, number, center, radius in hits:
            print(f"      AOI #{number} center={center} r={radius}  {path}")
    if len(collisions) > 20:
        print(f"  ... and {len(collisions) - 20} more")

    if collapsed:
        print("\nRESULT: relink collapse found - clicked thumbnails will zoom "
              "into the wrong (same-named) image on this machine.")
        return 1
    if collisions:
        print("\nRESULT: cache-key collisions found - these AOIs display each "
              "other's thumbnails in the gallery (loose files did this too).")
        return 1
    print("\nRESULT: clean - neither relink collapse nor key collisions. "
          "Wrong-thumbnail reports on this dataset point back at the build.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
