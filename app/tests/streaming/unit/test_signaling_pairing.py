"""Unit tests for the pairing helpers (plan §12 + §9 interop).

The SAS algorithm is locked to byte-for-byte compatibility with
ADIAT_Mobile/.../SasDerivation.kt. Any algorithm change here must move
in lockstep with the mobile side or live pairings break (both peers
display different 4-word phrases).
"""

from __future__ import annotations

import os
import sys

import pytest

# Ensure ``app`` is on the path when this test is run in isolation.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.services.streaming.signaling import pairing  # noqa: E402


# ----------------------------------------------------------------------
# Pairing code generator / normalizer
# ----------------------------------------------------------------------


def test_alphabet_excludes_confusable_characters() -> None:
    """The Worker excludes I/L/O/0/1; the desktop must match exactly."""
    for ch in "ILO01":
        assert ch not in pairing.PAIRING_CODE_ALPHABET, ch
    # All other A-Z plus 2-9 are present.
    expected_letters = set("ABCDEFGHJKMNPQRSTUVWXYZ")
    expected_digits = set("23456789")
    assert expected_letters | expected_digits == set(pairing.PAIRING_CODE_ALPHABET)
    assert len(pairing.PAIRING_CODE_ALPHABET) == 31


def test_generate_pairing_code_shape() -> None:
    code = pairing.generate_pairing_code()
    assert len(code) == pairing.PAIRING_CODE_LENGTH
    assert all(ch in pairing.PAIRING_CODE_ALPHABET for ch in code)


def test_generate_pairing_code_distribution_no_obvious_collisions() -> None:
    """Sanity test from plan §12: no obvious collisions over 10k codes."""
    codes = {pairing.generate_pairing_code() for _ in range(10_000)}
    # 31**6 ~= 887M possible codes; 10k draws should have <<1 collisions.
    assert len(codes) >= 9_990, f"unexpected collision rate: {10_000 - len(codes)}"


def test_normalize_pairing_code_strips_separators_and_upcases() -> None:
    assert pairing.normalize_pairing_code("k 3-f7pm") == "K3F7PM"
    assert pairing.normalize_pairing_code("KM-NV-23") == "KMNV23"


def test_normalize_pairing_code_rejects_confusable_characters() -> None:
    """I, L, O are deliberately absent from the alphabet — no silent remap."""
    for code in ("IBCDEF", "ABLDEF", "ABCDOF"):
        with pytest.raises(ValueError) as exc_info:
            pairing.normalize_pairing_code(code)
        assert "outside" in str(exc_info.value).lower()


def test_normalize_pairing_code_rejects_zero_and_one() -> None:
    with pytest.raises(ValueError):
        pairing.normalize_pairing_code("ABC012")
    with pytest.raises(ValueError):
        pairing.normalize_pairing_code("ABC123")


def test_normalize_pairing_code_accepts_digits_two_through_nine() -> None:
    """The Worker's alphabet keeps 2-9 (excludes 0/1); make sure 8/9 are valid."""
    assert pairing.normalize_pairing_code("ABC289") == "ABC289"


def test_normalize_pairing_code_rejects_wrong_length() -> None:
    with pytest.raises(ValueError):
        pairing.normalize_pairing_code("ABCDE")  # too short
    with pytest.raises(ValueError):
        pairing.normalize_pairing_code("ABCDEFG")  # too long


# ----------------------------------------------------------------------
# SAS wordlist + algorithm structure
# ----------------------------------------------------------------------


def test_sas_wordlist_is_exactly_128_unique_lowercase_entries() -> None:
    """Locked structural invariants — must match mobile's SasDerivation.kt."""
    assert len(pairing.SAS_WORDLIST) == 128
    assert len(set(pairing.SAS_WORDLIST)) == 128
    assert all(word.isalpha() and word.islower() for word in pairing.SAS_WORDLIST)


def test_sas_wordlist_first_entries_match_mobile() -> None:
    """Spot-check the first few entries to flag accidental reordering."""
    assert pairing.SAS_WORDLIST[0] == "amber"
    assert pairing.SAS_WORDLIST[1] == "anchor"
    assert pairing.SAS_WORDLIST[-1] == "willow"


def test_sas_bits_per_word_is_seven() -> None:
    assert pairing.SAS_BITS_PER_WORD == 7


# ----------------------------------------------------------------------
# SAS derivation behaviour
# ----------------------------------------------------------------------


# The mobile test fixture uses these exact two fingerprints (see
# ADIAT_Mobile/.../SasDerivationTest.kt). We use them here to lock the
# algorithm with a golden output — both sides MUST produce the same
# phrase for this canonical pair, otherwise SAS interop is broken.
_FP_A = ("AB:CD:EF:01:23:45:67:89:AB:CD:EF:01:23:45:67:89:"
         "AB:CD:EF:01:23:45:67:89:AB:CD:EF:01:23:45:67:89")
_FP_B = ("12:34:56:78:9A:BC:DE:F0:12:34:56:78:9A:BC:DE:F0:"
         "12:34:56:78:9A:BC:DE:F0:12:34:56:78:9A:BC:DE:F0")


def test_sas_golden_value_for_mobile_test_fingerprints() -> None:
    """Cross-platform regression guard.

    These four words are the exact output of ADIAT_Mobile's
    ``SasDerivation.derive(fpA, fpB)`` for the test fingerprint pair. If
    this assertion fires the desktop and mobile have diverged and live
    pairings will fail with mismatched phrases. Rerun mobile's test
    suite + this one before merging any algorithm change.
    """
    assert pairing.derive_sas_words(_FP_A, _FP_B) == ["oak", "coal", "mouse", "river"]


def test_sas_derivation_is_argument_swap_invariant() -> None:
    """Both peers compute the SAS with local-first or remote-first; same result."""
    assert pairing.derive_sas_words(_FP_A, _FP_B) == pairing.derive_sas_words(_FP_B, _FP_A)


def test_sas_derivation_tolerates_colons_and_case() -> None:
    """Mirrors mobile's `derive tolerates colon-separated and bare hex inputs`."""
    with_colons = pairing.derive_sas_words(_FP_A, _FP_B)
    without_colons = pairing.derive_sas_words(
        _FP_A.replace(":", ""),
        _FP_B.replace(":", ""),
    )
    assert with_colons == without_colons

    upper = pairing.derive_sas_words(_FP_A.upper(), _FP_B.upper())
    lower = pairing.derive_sas_words(_FP_A.lower(), _FP_B.lower())
    assert upper == lower


def test_sas_one_bit_flip_yields_different_words() -> None:
    """SHA-256 avalanche — even a 4-bit nibble change perturbs the SAS phrase."""
    tweaked = "AC" + _FP_A[2:]  # flip 'AB' → 'AC'
    original = pairing.derive_sas_words(_FP_A, _FP_B)
    mutated = pairing.derive_sas_words(tweaked, _FP_B)
    assert original != mutated


def test_sas_word_count_is_configurable() -> None:
    sas = pairing.derive_sas_words(_FP_A, _FP_B, count=2)
    assert len(sas) == 2
    assert all(w in pairing.SAS_WORDLIST for w in sas)


def test_sas_rejects_empty_fingerprint() -> None:
    with pytest.raises(ValueError):
        pairing.derive_sas_words("", "ABCDEF")
    with pytest.raises(ValueError):
        pairing.derive_sas_words("ABCDEF", "")


def test_sas_rejects_non_128_wordlist() -> None:
    """Mismatched wordlist would silently produce wrong phrases — fail fast."""
    with pytest.raises(ValueError):
        pairing.derive_sas_words(_FP_A, _FP_B, wordlist=["only", "two"])


def test_canonical_hash_uses_colon_separator() -> None:
    """Regression guard — mobile uses ``min + ":" + max`` (not ``|``)."""
    import hashlib

    a = "abcdef"
    b = "012345"
    low, high = sorted((a, b))
    expected = hashlib.sha256(f"{low}:{high}".encode("ascii")).digest()
    assert pairing.canonical_fingerprint_hash(a, b) == expected
