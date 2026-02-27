from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Callable

from src.models.database import Database
from src.models.file_record import FileRecord, FileStatus
from src.services.rule_engine import RuleEngine
from src.services.duplicate_detector import DuplicateDetector
from src.utils.config import AppConfig
from src.utils.helpers import (
    classify_file,
    should_skip_file,
    wait_for_file_stability,
    generate_unique_name,
    compute_file_hash,
    format_file_size,
)
from src.utils.logger import logger


# Type alias for the callback that notifies UI about events
OrganizeCallback = Callable[[FileRecord], None]


class FileOrganizer:
    """
    Orchestrates file organization: classification, rule matching,
    duplicate detection, and physical file movement.
    """

    def __init__(
        self,
        config: AppConfig,
        database: Database,
        on_file_organized: OrganizeCallback | None = None,
    ) -> None:
        self._config = config
        self._db = database
        self._rule_engine = RuleEngine(database)
        self._duplicate_detector = DuplicateDetector(database)
        self._on_file_organized = on_file_organized

    @property
    def rule_engine(self) -> RuleEngine:
        return self._rule_engine

    @property
    def duplicate_detector(self) -> DuplicateDetector:
        return self._duplicate_detector

    def organize_file(self, file_path: Path) -> FileRecord | None:
        """
        Process a single file: classify, check duplicates, move it.

        This is the main entry point called by the file monitor.

        Args:
            file_path: Absolute path to the new file.

        Returns:
            FileRecord with the result, or None if the file was skipped.
        """
        # Step 1: Validate
        if should_skip_file(file_path):
            logger.debug("Skipping file: %s", file_path.name)
            return None

        # Step 2: Wait for stability
        if not wait_for_file_stability(file_path):
            logger.warning("File unstable or disappeared: %s", file_path.name)
            return None

        # Double-check existence after waiting
        if not file_path.exists():
            return None

        logger.info("Processing file: %s", file_path.name)

        try:
            file_size = file_path.stat().st_size
            file_hash = compute_file_hash(file_path) or ""

            # Step 3: Check duplicates
            existing = self._duplicate_detector.check(file_path)
            if existing:
                record = self._create_record(
                    file_path, file_path, "", file_size, file_hash,
                    FileStatus.DUPLICATE,
                )
                self._notify(record)
                return record

            # Step 4: Determine category
            # Custom rules take precedence over extension classification
            category = self._rule_engine.evaluate(file_path)
            if category is None:
                category = classify_file(file_path)

            # Step 5: Create destination & move
            dest_dir = self._config.destination_path / category
            dest_dir.mkdir(parents=True, exist_ok=True)

            dest_path = generate_unique_name(dest_dir, file_path.name)
            shutil.move(str(file_path), str(dest_path))

            logger.info(
                "Moved '%s' → %s/%s (%s)",
                file_path.name, category, dest_path.name,
                format_file_size(file_size),
            )

            # Step 6: Record in database
            record = self._create_record(
                file_path, dest_path, category, file_size, file_hash,
                FileStatus.MOVED,
            )
            self._db.add_file_record(record)
            self._notify(record)
            return record

        except PermissionError:
            logger.error("Permission denied: %s", file_path.name)
            record = self._create_record(
                file_path, file_path, "", 0, "",
                FileStatus.ERROR,
            )
            self._notify(record)
            return record

        except OSError as e:
            logger.error("Error organizing '%s': %s", file_path.name, e)
            record = self._create_record(
                file_path, file_path, "", 0, "",
                FileStatus.ERROR,
            )
            self._notify(record)
            return record

    def organize_existing_files(self) -> list[FileRecord]:
        """
        Organize all existing files in the watch folder.

        Useful for initial cleanup or re-scan.

        Returns:
            List of FileRecords for all processed files.
        """
        watch_path = self._config.watch_path
        results: list[FileRecord] = []

        if not watch_path.exists():
            logger.warning("Watch folder does not exist: %s", watch_path)
            return results

        for item in watch_path.iterdir():
            if item.is_file():
                record = self.organize_file(item)
                if record:
                    results.append(record)

        logger.info("Organized %d existing files", len(results))
        return results

    # Internal Helpers

    @staticmethod
    def _create_record(
        original: Path,
        destination: Path,
        category: str,
        size: int,
        file_hash: str,
        status: FileStatus,
    ) -> FileRecord:
        return FileRecord(
            original_name=original.name,
            original_path=str(original),
            destination_path=str(destination),
            category=category,
            file_size=size,
            file_hash=file_hash,
            status=status.value,
            timestamp=datetime.now().isoformat(),
        )

    def _notify(self, record: FileRecord) -> None:
        """Notify the UI callback if registered."""
        if self._on_file_organized:
            try:
                self._on_file_organized(record)
            except Exception as e:
                logger.error("Callback error: %s", e)
