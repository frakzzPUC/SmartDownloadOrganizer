import tempfile
from pathlib import Path

import pytest

from src.utils.helpers import (
    classify_file,
    is_temp_file,
    is_hidden_file,
    generate_unique_name,
    compute_file_hash,
    format_file_size,
)


class TestClassifyFile:
    def test_pdf(self):
        assert classify_file(Path("report.pdf")) == "Documents"

    def test_jpg(self):
        assert classify_file(Path("photo.jpg")) == "Images"

    def test_mp4(self):
        assert classify_file(Path("video.mp4")) == "Videos"

    def test_py(self):
        assert classify_file(Path("script.py")) == "Code"

    def test_unknown(self):
        assert classify_file(Path("file.xyz999")) == "Others"

    def test_case_insensitive(self):
        assert classify_file(Path("IMG.PNG")) == "Images"


class TestIsTempFile:
    def test_crdownload(self):
        assert is_temp_file(Path("file.crdownload")) is True

    def test_part(self):
        assert is_temp_file(Path("file.part")) is True

    def test_normal(self):
        assert is_temp_file(Path("file.pdf")) is False


class TestIsHiddenFile:
    def test_hidden(self):
        assert is_hidden_file(Path(".hidden")) is True

    def test_visible(self):
        assert is_hidden_file(Path("visible.txt")) is False


class TestGenerateUniqueName:
    def test_no_conflict(self, tmp_path):
        result = generate_unique_name(tmp_path, "test.txt")
        assert result == tmp_path / "test.txt"

    def test_with_conflict(self, tmp_path):
        (tmp_path / "test.txt").write_text("existing")
        result = generate_unique_name(tmp_path, "test.txt")
        assert result == tmp_path / "test (1).txt"

    def test_multiple_conflicts(self, tmp_path):
        (tmp_path / "test.txt").write_text("1")
        (tmp_path / "test (1).txt").write_text("2")
        result = generate_unique_name(tmp_path, "test.txt")
        assert result == tmp_path / "test (2).txt"


class TestComputeFileHash:
    def test_hash_consistency(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("hello world")
        h1 = compute_file_hash(f)
        h2 = compute_file_hash(f)
        assert h1 == h2
        assert h1 is not None

    def test_different_content_different_hash(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("content A")
        f2.write_text("content B")
        assert compute_file_hash(f1) != compute_file_hash(f2)

    def test_nonexistent_file(self):
        result = compute_file_hash(Path("/nonexistent/file.txt"))
        assert result is None


class TestFormatFileSize:
    def test_bytes(self):
        assert format_file_size(500) == "500 B"

    def test_kilobytes(self):
        assert format_file_size(2048) == "2.0 KB"

    def test_megabytes(self):
        assert format_file_size(5 * 1024 * 1024) == "5.0 MB"

    def test_gigabytes(self):
        assert format_file_size(2 * 1024 ** 3) == "2.00 GB"
