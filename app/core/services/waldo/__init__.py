"""WALDO airframe support.

WALDO is a fixed-wing rig with two Canon EOS 5DS R DSLRs mounted with 22.5°
outward roll. Their JPEGs carry GPS but no gimbal/AGL XMP, so ADIAT cannot
estimate AOI GPS for them out of the box. This package handles a one-time
pre-processing pass that synthesises the missing metadata from the existing
GPS sequence + a local DEM, allowing the standard pipeline to work unchanged.
"""

from .WaldoMetadataService import (
    WaldoMetadataService,
    WaldoProcessResult,
    WaldoImageRecord,
    WaldoHeadingUnavailable,
    WaldoCoverageError,
    WaldoMissingGPSError,
    WALDO_NAMESPACE_URI,
    WALDO_PROCESSOR_VERSION,
)

__all__ = [
    'WaldoMetadataService',
    'WaldoProcessResult',
    'WaldoImageRecord',
    'WaldoHeadingUnavailable',
    'WaldoCoverageError',
    'WaldoMissingGPSError',
    'WALDO_NAMESPACE_URI',
    'WALDO_PROCESSOR_VERSION',
]
