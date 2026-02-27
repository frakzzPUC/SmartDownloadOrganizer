import shutil
import tempfile
from pathlib import Path

import pytest

from src.models.database import Database
from src.models.file_record import FileStatus
from src.services.file_organizer import FileOrganizer
from src.utils.config import AppConfig


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    d = tempfile.mkdtemp()
    yield Path(d)
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def db(temp_dir):
    """Create an in-memory-like database in the temp directory."""
    return Database(db_path=temp_dir / "test.db")


@pytest.fixture
def config(temp_dir):
    """Create a test AppConfig pointing to temp dirs."""
    watch = temp_dir / "downloads"
    watch.mkdir()
    dest = temp_dir / "organized"
    dest.mkdir()
    return AppConfig(
        watch_folder=str(watch),
        destination_folder=str(dest),
    )


@pytest.fixture
def organizer(config, db):
    """Create a FileOrganizer with test config."""
    return FileOrganizer(config=config, database=db)


class TestFileOrganizer:
    """Test suite for the FileOrganizer service."""

    def test_organize_pdf(self, organizer, config):
        """PDF files should be moved to the Documents folder."""
        pdf = Path(config.watch_folder) / "report.pdf"
        pdf.write_text("fake pdf content")

        record = organizer.organize_file(pdf)

        assert record is not None
        assert record.status == FileStatus.MOVED.value
        assert record.category == "Documents"
        assert not pdf.exists()
        assert (Path(config.destination_folder) / "Documents" / "report.pdf").exists()

    def test_organize_image(self, organizer, config):
        """Image files should be moved to the Images folder."""
        img = Path(config.watch_folder) / "photo.jpg"
        img.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        record = organizer.organize_file(img)

        assert record is not None
        assert record.category == "Images"

    def test_skip_temp_file(self, organizer, config):
        """Temporary download files should be skipped."""
        temp = Path(config.watch_folder) / "download.crdownload"
        temp.write_text("incomplete")

        record = organizer.organize_file(temp)

        assert record is None
        assert temp.exists()  # file should not be moved

    def test_skip_empty_file(self, organizer, config):
        """Empty files (0 bytes) should be skipped."""
        empty = Path(config.watch_folder) / "empty.txt"
        empty.write_text("")

        record = organizer.organize_file(empty)
        assert record is None

    def test_unique_naming(self, organizer, config):
        """Duplicate filenames should get a counter suffix."""
        dest_docs = Path(config.destination_folder) / "Documents"
        dest_docs.mkdir(parents=True, exist_ok=True)
        (dest_docs / "report.pdf").write_text("existing")

        new_pdf = Path(config.watch_folder) / "report.pdf"
        new_pdf.write_text("new content")

        record = organizer.organize_file(new_pdf)

        assert record is not None
        assert "report (1).pdf" in record.destination_path

    def test_organize_existing_files(self, organizer, config):
        """organize_existing_files should process all files in the watch folder."""
        for name in ["a.pdf", "b.png", "c.mp4"]:
            (Path(config.watch_folder) / name).write_text("content")

        results = organizer.organize_existing_files()
        assert len(results) == 3

    def test_uncategorized_file(self, organizer, config):
        """Files with unknown extensions go to 'Others'."""
        unknown = Path(config.watch_folder) / "mystery.xyz123"
        unknown.write_text("what is this")

        record = organizer.organize_file(unknown)

        assert record is not None
        assert record.category == "Others"
