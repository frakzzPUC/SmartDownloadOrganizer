import shutil
import tempfile
from pathlib import Path

import pytest

from src.models.database import Database
from src.models.file_record import FileRecord, FileStatus
from src.services.duplicate_detector import DuplicateDetector
from src.utils.helpers import compute_file_hash


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield Path(d)
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def db(temp_dir):
    return Database(db_path=temp_dir / "test.db")


@pytest.fixture
def detector(db):
    return DuplicateDetector(database=db)


class TestDuplicateDetector:
    """Test suite for duplicate file detection."""

    def test_no_duplicate_for_new_file(self, detector, temp_dir):
        """A brand new file should not be detected as a duplicate."""
        f = temp_dir / "unique.txt"
        f.write_text("unique content 12345")

        result = detector.check(f)
        assert result is None

    def test_detects_duplicate(self, detector, db, temp_dir):
        """A file with the same hash as an existing record should be flagged."""
        original = temp_dir / "original.txt"
        original.write_text("duplicate content")
        file_hash = compute_file_hash(original)

        # Simulate a previously organized file
        db.add_file_record(FileRecord(
            original_name="original.txt",
            original_path=str(original),
            destination_path=str(temp_dir / "Documents" / "original.txt"),
            category="Documents",
            file_size=100,
            file_hash=file_hash or "",
            status=FileStatus.MOVED.value,
        ))

        # Create a copy with the same content
        copy = temp_dir / "copy.txt"
        copy.write_text("duplicate content")

        result = detector.check(copy)
        assert result is not None
        assert result.original_name == "original.txt"

    def test_different_content_not_duplicate(self, detector, db, temp_dir):
        """Files with different content should not match."""
        original = temp_dir / "file_a.txt"
        original.write_text("content A")
        file_hash = compute_file_hash(original)

        db.add_file_record(FileRecord(
            original_name="file_a.txt",
            original_path=str(original),
            destination_path=str(temp_dir / "Documents" / "file_a.txt"),
            category="Documents",
            file_size=50,
            file_hash=file_hash or "",
            status=FileStatus.MOVED.value,
        ))

        different = temp_dir / "file_b.txt"
        different.write_text("completely different content")

        result = detector.check(different)
        assert result is None
