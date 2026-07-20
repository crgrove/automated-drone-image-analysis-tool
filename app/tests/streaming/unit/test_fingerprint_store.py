"""Unit tests for the TOFU :class:`FingerprintStore` (plan §19.4.3)."""

from __future__ import annotations

import os
import sys
import time

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.services.streaming.FingerprintStore import (  # noqa: E402
    FingerprintStore,
    PeerRecord,
)


@pytest.fixture
def store(tmp_path):
    db = tmp_path / "peers.sqlite"
    return FingerprintStore(db_path=db)


def test_record_pairing_inserts_new_device(store) -> None:
    record = store.record_pairing("M4E #3", "sha-256 AB:CD:EF")
    assert isinstance(record, PeerRecord)
    assert record.device_label == "M4E #3"
    assert record.sha256 == "sha-256 AB:CD:EF"
    assert record.first_seen_epoch_s <= record.last_seen_epoch_s


def test_record_pairing_is_idempotent_for_same_pair(store) -> None:
    record1 = store.record_pairing("M4E #3", "sha-256 AB:CD:EF")
    time.sleep(0.01)
    record2 = store.record_pairing("M4E #3", "sha-256 AB:CD:EF")
    assert record2.first_seen_epoch_s == record1.first_seen_epoch_s
    assert record2.last_seen_epoch_s >= record1.last_seen_epoch_s


def test_record_pairing_with_new_fingerprint_overwrites(store) -> None:
    """A new fingerprint for an existing label is a deliberate operator override."""
    store.record_pairing("M4E #3", "sha-256 OLD")
    store.record_pairing("M4E #3", "sha-256 NEW", notes="tablet swapped")
    record = store.get("M4E #3")
    assert record.sha256 == "sha-256 NEW"
    assert record.notes == "tablet swapped"


def test_matches_compares_canonical_form(store) -> None:
    """Whitespace and case differences in the fingerprint don't matter."""
    store.record_pairing("M4E #3", "sha-256 AB:CD:EF")
    assert store.matches("M4E #3", "sha-256 ab:cd:ef") is True
    assert store.matches("M4E #3", "sha-256AB:CD:EF") is True
    assert store.matches("M4E #3", "sha-256 99:88:77") is False


def test_find_by_fingerprint_reverse_lookup(store) -> None:
    store.record_pairing("Tablet A", "sha-256 11:22:33")
    store.record_pairing("Tablet B", "sha-256 44:55:66")
    match = store.find_by_fingerprint("sha-256 11:22:33")
    assert match is not None
    assert match.device_label == "Tablet A"
    assert store.find_by_fingerprint("sha-256 99:99:99") is None


def test_list_devices_orders_by_last_seen_desc(store) -> None:
    store.record_pairing("First",  "fp-1")
    time.sleep(0.01)
    store.record_pairing("Second", "fp-2")
    devices = store.list_devices()
    assert [d.device_label for d in devices] == ["Second", "First"]


def test_forget_removes_record(store) -> None:
    store.record_pairing("M4E #3", "sha-256 ABC")
    assert store.get("M4E #3") is not None
    store.forget("M4E #3")
    assert store.get("M4E #3") is None


def test_record_pairing_rejects_empty_args(store) -> None:
    with pytest.raises(ValueError):
        store.record_pairing("", "fp")
    with pytest.raises(ValueError):
        store.record_pairing("Tablet", "")
