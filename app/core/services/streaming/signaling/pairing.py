"""Pairing primitives for the Flight Viewer.

Implements the two pieces of pairing logic that are independent of any
signaling backend:

* a 31-character no-confusables 6-character pairing code generator. The
  alphabet is ``A-Z`` minus ``I``, ``L``, ``O`` plus ``2-9`` — matching
  the alphabet the ``adiat-flight-signaling`` Cloudflare Worker uses to
  allocate codes via CAS on its Durable Object name lookup (plan §8).
  The desktop never allocates codes in production (mobile does, via POST
  to the Worker), but the generator is useful for tests, the in-memory
  signaling backend, and any future desktop-initiated pairings.

* the Short Authentication String (SAS) derivation. **This implementation
  is the byte-for-byte equivalent of ADIAT_Mobile's
  ``SasDerivation.kt``** — same wordlist, same canonical-hash composition
  (``SHA-256(min || ":" || max)``), same 7-bit extraction windows at
  offsets 0/7/14/21. Any change to the algorithm here MUST be mirrored
  in mobile or pairing breaks: both sides display different phrases.

Both helpers are deliberately pure (no Qt, no asyncio, no I/O) so they can
be unit tested in isolation.
"""

from __future__ import annotations

import hashlib
import secrets
from typing import Iterable, List

# No-confusables alphabet matching the `adiat-flight-signaling` Worker
# (plan §8 *Code allocation*). 23 letters (A-Z minus I, L, O) + digits 2-9
# = 31 characters; 31**6 ≈ 887M distinct codes.
PAIRING_CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
PAIRING_CODE_LENGTH = 6


# 128-word SAS wordlist. **MUST match ADIAT_Mobile/.../SasDerivation.kt
# WORDLIST exactly, in the same order.** Short concrete nouns chosen for
# readability over voice radio. 128 entries → 7 bits per word × 4 words
# = 28 bits of SAS entropy.
SAS_WORDLIST: tuple = (
    "amber", "anchor", "apple", "arrow", "ash", "bay", "bear", "bell",
    "birch", "bird", "blade", "blue", "book", "boot", "bowl", "brass",
    "bread", "brick", "bridge", "bronze", "brush", "cake", "candle", "canyon",
    "cave", "cedar", "chain", "chalk", "cliff", "cloud", "clover", "coal",
    "coast", "coin", "copper", "coral", "crane", "crow", "crown", "cube",
    "dawn", "deer", "desk", "dock", "drum", "dusk", "eagle", "earth",
    "ember", "fern", "field", "flame", "forest", "fork", "fox", "frost",
    "garden", "ghost", "glass", "gold", "grain", "grape", "harbor", "hawk",
    "heart", "hill", "honey", "iron", "ivy", "jade", "kite", "lake",
    "lamp", "leaf", "lily", "lion", "lock", "maple", "marble", "marsh",
    "meadow", "mint", "mist", "moon", "moss", "mountain", "mouse", "music",
    "nest", "oak", "ocean", "olive", "opal", "owl", "palm", "peach",
    "pearl", "pebble", "pine", "plum", "pond", "quartz", "rain", "raven",
    "ridge", "river", "rock", "rose", "salmon", "sand", "seal", "shore",
    "silver", "snow", "star", "stone", "storm", "stream", "sun", "swan",
    "thorn", "tide", "tiger", "tower", "trout", "valley", "wave", "willow",
)

# Bits per wordlist index — locked to mobile's value.
SAS_BITS_PER_WORD = 7

assert len(SAS_WORDLIST) == (1 << SAS_BITS_PER_WORD), (
    f"SAS_WORDLIST must have 2^{SAS_BITS_PER_WORD} entries to match "
    f"ADIAT_Mobile/SasDerivation.kt — got {len(SAS_WORDLIST)}"
)
assert len(set(SAS_WORDLIST)) == len(SAS_WORDLIST), (
    "SAS_WORDLIST must contain unique entries"
)


def generate_pairing_code(rng: "secrets.SystemRandom | None" = None) -> str:
    """Generate a fresh 6-character no-confusables pairing code.

    Production codes are normally allocated by the Worker (see the plan
    §8 *Code allocation*). This helper exists so unit tests and the
    in-memory signaling backend can mint codes that match the production
    alphabet without going through a mailbox.

    Args:
        rng: Optional ``secrets.SystemRandom``-shaped object; defaults to a
            fresh instance. Tests inject deterministic shims here.

    Returns:
        A 6-character code drawn from :data:`PAIRING_CODE_ALPHABET`.
    """
    rng = rng or secrets.SystemRandom()
    return "".join(rng.choice(PAIRING_CODE_ALPHABET) for _ in range(PAIRING_CODE_LENGTH))


def normalize_pairing_code(code: str) -> str:
    """Normalize user input into the canonical pairing code shape.

    Accepts user-typed codes with whitespace, hyphens, or lower-case
    letters. Rejects anything containing characters outside the
    no-confusables alphabet (``I``/``L``/``O``/``0``/``1``/``8`` are
    deliberately absent from the alphabet; ``0`` and ``1`` are common
    typos but there's no unambiguous remap, so reject and let the
    dialog surface a clear error).
    """
    if code is None:
        raise ValueError("pairing code is required")

    # Strip whitespace, hyphens, and other separators users tend to add.
    cleaned = "".join(ch for ch in str(code).upper() if ch.isalnum())

    if len(cleaned) != PAIRING_CODE_LENGTH:
        raise ValueError(
            f"pairing code must be {PAIRING_CODE_LENGTH} characters; got {len(cleaned)}"
        )

    invalid = [ch for ch in cleaned if ch not in PAIRING_CODE_ALPHABET]
    if invalid:
        raise ValueError(
            "pairing code contains characters outside the alphabet "
            "(A-Z minus I/L/O, 2-9): " + "".join(sorted(set(invalid)))
        )
    return cleaned


def _normalize_fingerprint(fp: str) -> str:
    """Canonicalize a fingerprint for hash composition.

    Mirrors ``SasDerivation.normalize`` on mobile: strip ``:`` separators,
    trim outer whitespace, lowercase. **Does NOT strip internal spaces** —
    both sides must agree, and mobile's implementation only does
    ``replace(":", "").trim().lowercase()``.
    """
    return (fp or "").replace(":", "").strip().lower()


def canonical_fingerprint_hash(fp_a: str, fp_b: str) -> bytes:
    """Return a hash that is independent of the argument order.

    Mirrors ADIAT_Mobile/SasDerivation.kt:

    .. code-block:: kotlin

        val (smaller, larger) = if (canonicalA <= canonicalB) ...
        val composed = "$smaller:$larger".encodeToByteArray()
        MessageDigest.getInstance("SHA-256").digest(composed)

    Note the ``:`` separator — earlier desktop builds used ``|`` and
    produced incompatible SAS words; the colon was the long-standing
    mobile choice and is the source of truth.
    """
    a = _normalize_fingerprint(fp_a)
    b = _normalize_fingerprint(fp_b)
    if not a or not b:
        raise ValueError("both fingerprints are required to derive SAS")
    low, high = sorted((a, b))
    return hashlib.sha256(f"{low}:{high}".encode("ascii")).digest()


def _extract_n_bits(digest: bytes, bit_start: int, bits_per_word: int) -> int:
    """Extract ``bits_per_word`` bits from ``digest`` starting at ``bit_start``.

    Direct port of ``SasDerivation.extract7Bits``. Reads two bytes so the
    window can safely span a byte boundary; SHA-256's 32-byte output is
    far larger than the bit positions we ever consume (0..21 for 4 words).
    """
    byte_start = bit_start // 8
    bit_offset_in_byte = bit_start % 8
    two_bytes = (digest[byte_start] << 8) | digest[byte_start + 1]
    shift = (16 - bits_per_word) - bit_offset_in_byte
    mask = (1 << bits_per_word) - 1
    return (two_bytes >> shift) & mask


def derive_sas_words(
    fp_a: str,
    fp_b: str,
    *,
    count: int = 4,
    wordlist: Iterable[str] = SAS_WORDLIST,
) -> List[str]:
    """Derive a Short Authentication String from two DTLS fingerprints.

    Byte-for-byte compatible with ADIAT_Mobile/SasDerivation.kt — both
    peers must compute the same 4 words for the same fingerprint pair so
    the operator/viewer voice readback succeeds.

    Args:
        fp_a: Hex fingerprint of one peer (colon-separated or bare;
            normalization handles both).
        fp_b: Hex fingerprint of the other peer.
        count: Number of words to emit. Default 4 (the mobile spec).
        wordlist: Iterable of exactly 128 short nouns. Default is
            :data:`SAS_WORDLIST` which mirrors mobile's wordlist. Tests
            may pass a stub but it must remain length-128 because the
            7-bit extraction window depends on that size.

    Returns:
        A list of ``count`` lower-case words.
    """
    if count <= 0:
        return []
    words = tuple(wordlist)
    if len(words) != (1 << SAS_BITS_PER_WORD):
        raise ValueError(
            f"SAS wordlist must have exactly {1 << SAS_BITS_PER_WORD} entries "
            f"to match mobile's algorithm; got {len(words)}"
        )

    digest = canonical_fingerprint_hash(fp_a, fp_b)
    return [
        words[_extract_n_bits(digest, i * SAS_BITS_PER_WORD, SAS_BITS_PER_WORD)]
        for i in range(count)
    ]
