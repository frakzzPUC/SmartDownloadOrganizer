from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum


class FileStatus(Enum):
    """Status of a file organization operation."""
    MOVED = "moved"
    DUPLICATE = "duplicate"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class FileRecord:
    """Represents a record of an organized file."""

    id: int | None = None
    original_name: str = ""
    original_path: str = ""
    destination_path: str = ""
    category: str = ""
    file_size: int = 0
    file_hash: str = ""
    status: str = FileStatus.MOVED.value
    timestamp: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    @property
    def original_path_obj(self) -> Path:
        return Path(self.original_path)

    @property
    def destination_path_obj(self) -> Path:
        return Path(self.destination_path)

    @property
    def size_display(self) -> str:
        from src.utils.helpers import format_file_size
        return format_file_size(self.file_size)

    @property
    def timestamp_display(self) -> str:
        try:
            dt = datetime.fromisoformat(self.timestamp)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return self.timestamp


@dataclass
class CustomRule:
    """
    A user-defined rule for file organization.

    Rules are evaluated in priority order (lower number = higher priority).
    """

    id: int | None = None
    name: str = ""
    pattern: str = ""              # Substring or regex to match filename
    target_folder: str = ""        # Destination subfolder name
    is_regex: bool = False         # Treat pattern as regex
    case_sensitive: bool = False
    enabled: bool = True
    priority: int = 0              # Lower = higher priority

    def __post_init__(self) -> None:
        if not self.name and self.pattern:
            self.name = f"Rule: '{self.pattern}' → {self.target_folder}"
