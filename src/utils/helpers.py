from __future__ import annotations

import hashlib
import time
from pathlib import Path

from src.utils.constants import (
    EXTENSION_TO_CATEGORY,
    UNCATEGORIZED_FOLDER,
    TEMP_EXTENSIONS,
    FILE_STABILITY_CHECKS,
    FILE_STABILITY_INTERVAL,
    MIN_FILE_SIZE_BYTES,
)


def classify_file(file_path: Path) -> str:
    """
    Determine the category of a file based on its extension.

    Args:
        file_path: Path to the file.

    Returns:
        Category name string.
    """
    suffix = file_path.suffix.lower()
    return EXTENSION_TO_CATEGORY.get(suffix, UNCATEGORIZED_FOLDER)


def is_temp_file(file_path: Path) -> bool:
    """Check if a file is a temporary/incomplete download."""
    return file_path.suffix.lower() in TEMP_EXTENSIONS


def is_hidden_file(file_path: Path) -> bool:
    """Check if a file is hidden (starts with dot)."""
    return file_path.name.startswith(".")


def should_skip_file(file_path: Path) -> bool:
    """
    Determine if a file should be skipped from organization.

    Skips temp files, hidden files, directories, and empty files.
    """
    if not file_path.is_file():
        return True
    if is_temp_file(file_path):
        return True
    if is_hidden_file(file_path):
        return True
    try:
        if file_path.stat().st_size < MIN_FILE_SIZE_BYTES:
            return True
    except OSError:
        return True
    return False


def wait_for_file_stability(file_path: Path) -> bool:
    """
    Wait until a file's size stabilizes (download complete).

    Compares file size across multiple checks. If size stops changing,
    the file is considered stable and ready to move.

    Args:
        file_path: Path to the file to check.

    Returns:
        True if file is stable, False if it disappeared or kept changing.
    """
    previous_size = -1
    stable_count = 0

    for _ in range(FILE_STABILITY_CHECKS * 3):
        try:
            current_size = file_path.stat().st_size
        except OSError:
            return False

        if current_size == previous_size:
            stable_count += 1
            if stable_count >= FILE_STABILITY_CHECKS:
                return True
        else:
            stable_count = 0

        previous_size = current_size
        time.sleep(FILE_STABILITY_INTERVAL)

    return False


def generate_unique_name(destination: Path, original_name: str) -> Path:
    """
    Generate a unique file path, appending a counter if the name exists.

    Example: 'report.pdf' → 'report (1).pdf' → 'report (2).pdf'

    Args:
        destination: Target directory.
        original_name: Original filename.

    Returns:
        Unique Path that does not conflict with existing files.
    """
    target = destination / original_name

    if not target.exists():
        return target

    stem = Path(original_name).stem
    suffix = Path(original_name).suffix
    counter = 1

    while True:
        new_name = f"{stem} ({counter}){suffix}"
        target = destination / new_name
        if not target.exists():
            return target
        counter += 1


def compute_file_hash(file_path: Path, algorithm: str = "md5") -> str | None:
    """
    Compute a hash of a file for duplicate detection.

    Uses chunked reading for memory efficiency with large files.

    Args:
        file_path: Path to the file.
        algorithm: Hash algorithm name (md5, sha256, etc.).

    Returns:
        Hex digest string or None if file cannot be read.
    """
    try:
        hasher = hashlib.new(algorithm)
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (OSError, ValueError):
        return None


def format_file_size(size_bytes: int) -> str:
    """
    Format file size into a human-readable string.

    Args:
        size_bytes: Size in bytes.

    Returns:
        Formatted string like '1.5 MB'.
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.1f} MB"
    else:
        return f"{size_bytes / 1024 ** 3:.2f} GB"
