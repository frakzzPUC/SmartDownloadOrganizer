from __future__ import annotations

from pathlib import Path

from src.models.database import Database
from src.models.file_record import FileRecord
from src.utils.helpers import compute_file_hash
from src.utils.logger import logger


class DuplicateDetector:
    """
    Detects duplicate files using content hashing.

    Compares the hash of a new file against the history database
    to identify files that have already been organized.
    """

    def __init__(self, database: Database) -> None:
        self._db = database

    def check(self, file_path: Path) -> FileRecord | None:
        """
        Check if a file is a duplicate of a previously organized file.

        Args:
            file_path: Path to the file to check.

        Returns:
            The existing FileRecord if duplicate, None if unique.
        """
        file_hash = compute_file_hash(file_path)
        if not file_hash:
            return None

        existing = self._db.find_by_hash(file_hash)
        if existing:
            logger.info(
                "Duplicate detected: '%s' matches '%s' (hash: %s)",
                file_path.name,
                existing.original_name,
                file_hash[:12],
            )
        return existing

    @staticmethod
    def compute_hash(file_path: Path) -> str:
        """Compute and return the MD5 hash of a file."""
        return compute_file_hash(file_path) or ""
