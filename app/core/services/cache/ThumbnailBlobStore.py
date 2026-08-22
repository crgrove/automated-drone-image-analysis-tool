"""
ThumbnailBlobStore - Single-file SQLite container for cached AOI thumbnails.

A large search produces thousands of loose thumbnail JPEGs, and copying
thousands of small files between drives or machines is dominated by per-file
filesystem overhead rather than data size. This store packs them into one
``thumbnails.db`` per cache directory - keyed by the same md5 cache keys the
loose files used and holding the same JPEG bytes - so a results folder moves
as a handful of large files instead of a swarm of small ones.

Thread safety: a fresh connection is opened per operation, so the GUI thread
and the thumbnail worker pool can call any method concurrently without a
shared-connection registry. Connection setup is microseconds next to the JPEG
decode each thumbnail already pays. The default rollback journal (not WAL) is
used deliberately: it leaves exactly one file on disk when the app is closed,
which is the whole point of the container.
"""

import os
import sqlite3
import time
from contextlib import closing
from typing import Optional


class ThumbnailBlobStore:
    """One-file SQLite blob store for thumbnail JPEG bytes."""

    DB_FILENAME = 'thumbnails.db'

    def __init__(self, directory, logger=None):
        """
        Initialize the store for a cache directory.

        Args:
            directory: Cache directory the container lives in (created by the
                cache service before the store is constructed).
            logger: Optional LoggerService for diagnostics.
        """
        self.db_path = os.path.join(str(directory), self.DB_FILENAME)
        self.logger = logger
        self._ensure_schema()

    def _connect(self):
        """Open a connection for a single operation."""
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        # NORMAL keeps writes fast; a lost thumbnail on power failure is
        # regenerated from the source image, so full durability buys nothing
        conn.execute('PRAGMA synchronous=NORMAL')
        return conn

    def _ensure_schema(self):
        try:
            with closing(self._connect()) as conn, conn:
                conn.execute(
                    'CREATE TABLE IF NOT EXISTS thumbnails ('
                    '    key TEXT PRIMARY KEY,'
                    '    data BLOB NOT NULL,'
                    '    created REAL NOT NULL'
                    ')'
                )
        except sqlite3.Error as e:
            if self.logger:
                self.logger.error(f"Thumbnail store schema error at {self.db_path}: {e}")

    def put(self, key: str, jpeg_bytes: bytes) -> bool:
        """Store (or replace) the JPEG bytes for a cache key."""
        try:
            with closing(self._connect()) as conn, conn:
                conn.execute(
                    'INSERT OR REPLACE INTO thumbnails (key, data, created) VALUES (?, ?, ?)',
                    (key, sqlite3.Binary(jpeg_bytes), time.time())
                )
            return True
        except sqlite3.Error as e:
            if self.logger:
                self.logger.error(f"Thumbnail store write error for {key}: {e}")
            return False

    def get(self, key: str) -> Optional[bytes]:
        """Return the JPEG bytes for a cache key, or None."""
        try:
            with closing(self._connect()) as conn, conn:
                row = conn.execute(
                    'SELECT data FROM thumbnails WHERE key = ?', (key,)
                ).fetchone()
            return bytes(row[0]) if row else None
        except sqlite3.Error as e:
            if self.logger:
                self.logger.error(f"Thumbnail store read error for {key}: {e}")
            return None

    def has(self, key: str) -> bool:
        """Return whether a cache key is stored, without loading its bytes."""
        try:
            with closing(self._connect()) as conn, conn:
                row = conn.execute(
                    'SELECT 1 FROM thumbnails WHERE key = ?', (key,)
                ).fetchone()
            return row is not None
        except sqlite3.Error:
            return False

    def count(self) -> int:
        """Number of stored thumbnails."""
        try:
            with closing(self._connect()) as conn, conn:
                return conn.execute('SELECT COUNT(*) FROM thumbnails').fetchone()[0]
        except sqlite3.Error:
            return 0

    def total_bytes(self) -> int:
        """Total size of stored thumbnail data in bytes."""
        try:
            with closing(self._connect()) as conn, conn:
                value = conn.execute(
                    'SELECT COALESCE(SUM(LENGTH(data)), 0) FROM thumbnails'
                ).fetchone()[0]
            return int(value or 0)
        except sqlite3.Error:
            return 0
