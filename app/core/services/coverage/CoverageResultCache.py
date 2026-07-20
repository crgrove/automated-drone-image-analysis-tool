"""
CoverageResultCache - in-session cache for the last CoveragePodService run.

Mirrors the HeatmapService lifecycle idiom (is-valid / get / invalidate) so the
viewer overlay can re-render the cached POD product without recomputing.

The cache also records the terrain/canopy configuration fingerprint the result
was computed with, so consumers can detect (and drop) a POD product that no
longer matches the active elevation or canopy source.
"""

# Settings keys that change what a POD result would compute to. A cached
# result made under a different value of any of these is stale.
_CONFIG_KEYS = (
    'TerrainProviderId',
    'Terrain3DEPManifestPath',
    'Terrain3DEPTilesDir',
    'CanopyKind',
    'CanopyManifestPath',
    'CanopyTilesDir',
)


def config_fingerprint(settings_service) -> str:
    """Stable fingerprint of the terrain/canopy configuration.

    Returns '' when no settings service is available (fingerprinting then
    degrades to "never stale", matching the pre-fingerprint behavior).
    """
    if settings_service is None:
        return ''
    values = []
    for key in _CONFIG_KEYS:
        try:
            values.append(str(settings_service.get_setting(key, '') or ''))
        except Exception:
            values.append('')
    return '|'.join(values)


class CoverageResultCache:
    def __init__(self):
        self._result = None
        self._fingerprint = None

    def set_result(self, result, fingerprint: str = None) -> None:
        self._result = result
        self._fingerprint = fingerprint

    def get_result(self):
        return self._result

    def has_result(self) -> bool:
        return self._result is not None

    def is_stale(self, current_fingerprint: str) -> bool:
        """True when a cached result was computed under a different
        terrain/canopy configuration than ``current_fingerprint``.

        An empty cache is never stale; a result cached without a fingerprint
        (or checked against an empty fingerprint) is trusted, preserving the
        pre-fingerprint behavior for callers that don't participate.
        """
        if self._result is None:
            return False
        if not self._fingerprint or not current_fingerprint:
            return False
        return self._fingerprint != current_fingerprint

    def invalidate(self) -> None:
        self._result = None
        self._fingerprint = None
