from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from src.models.file_record import FileRecord, CustomRule
from src.utils.constants import DEFAULT_CONFIG_PATH, DATABASE_NAME
from src.utils.logger import logger


class Database:
    """SQLite database manager with context manager support."""

    def __init__(self, db_path: Path | None = None) -> None:
        self._db_path = db_path or (DEFAULT_CONFIG_PATH / DATABASE_NAME)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: sqlite3.Connection | None = None
        self._initialize()

    def _initialize(self) -> None:
        """Create tables if they don't exist."""
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS file_history (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_name   TEXT NOT NULL,
                    original_path   TEXT NOT NULL,
                    destination_path TEXT NOT NULL,
                    category        TEXT NOT NULL,
                    file_size       INTEGER DEFAULT 0,
                    file_hash       TEXT DEFAULT '',
                    status          TEXT DEFAULT 'moved',
                    timestamp       TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS custom_rules (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    name            TEXT NOT NULL,
                    pattern         TEXT NOT NULL,
                    target_folder   TEXT NOT NULL,
                    is_regex        INTEGER DEFAULT 0,
                    case_sensitive  INTEGER DEFAULT 0,
                    enabled         INTEGER DEFAULT 1,
                    priority        INTEGER DEFAULT 0
                );

                CREATE INDEX IF NOT EXISTS idx_history_timestamp
                    ON file_history(timestamp);
                CREATE INDEX IF NOT EXISTS idx_history_category
                    ON file_history(category);
                CREATE INDEX IF NOT EXISTS idx_history_hash
                    ON file_history(file_hash);
            """)
        logger.info("Database initialized at %s", self._db_path)

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create a database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(
                str(self._db_path),
                check_same_thread=False,
            )
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def close(self) -> None:
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    # File History Operations

    def add_file_record(self, record: FileRecord) -> int:
        """Insert a new file record and return its ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO file_history
                    (original_name, original_path, destination_path,
                     category, file_size, file_hash, status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.original_name,
                    record.original_path,
                    record.destination_path,
                    record.category,
                    record.file_size,
                    record.file_hash,
                    record.status,
                    record.timestamp,
                ),
            )
            record.id = cursor.lastrowid
            logger.debug("Saved file record #%d: %s", record.id, record.original_name)
            return record.id  # type: ignore[return-value]

    def get_all_records(self, limit: int = 100) -> list[FileRecord]:
        """Retrieve the most recent file records."""
        conn = self._get_connection()
        rows = conn.execute(
            "SELECT * FROM file_history ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [self._row_to_file_record(row) for row in rows]

    def get_records_by_date(self, date: datetime) -> list[FileRecord]:
        """Get all records for a specific date."""
        start = date.strftime("%Y-%m-%dT00:00:00")
        end = date.strftime("%Y-%m-%dT23:59:59")
        conn = self._get_connection()
        rows = conn.execute(
            """
            SELECT * FROM file_history
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
            """,
            (start, end),
        ).fetchall()
        return [self._row_to_file_record(row) for row in rows]

    def get_statistics(self) -> dict[str, Any]:
        """
        Compute dashboard statistics.

        Returns:
            Dictionary with total files, today's count, category breakdown, etc.
        """
        conn = self._get_connection()

        total = conn.execute(
            "SELECT COUNT(*) FROM file_history WHERE status = 'moved'"
        ).fetchone()[0]

        today = datetime.now().strftime("%Y-%m-%d")
        today_count = conn.execute(
            "SELECT COUNT(*) FROM file_history WHERE status = 'moved' AND timestamp LIKE ?",
            (f"{today}%",),
        ).fetchone()[0]

        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        week_count = conn.execute(
            "SELECT COUNT(*) FROM file_history WHERE status = 'moved' AND timestamp >= ?",
            (week_ago,),
        ).fetchone()[0]

        categories = conn.execute(
            """
            SELECT category, COUNT(*) as count
            FROM file_history WHERE status = 'moved'
            GROUP BY category ORDER BY count DESC
            """
        ).fetchall()

        total_size = conn.execute(
            "SELECT COALESCE(SUM(file_size), 0) FROM file_history WHERE status = 'moved'"
        ).fetchone()[0]

        return {
            "total_files": total,
            "today_files": today_count,
            "week_files": week_count,
            "categories": {row["category"]: row["count"] for row in categories},
            "total_size": total_size,
        }

    def find_by_hash(self, file_hash: str) -> FileRecord | None:
        """Find an existing record by file hash (duplicate detection)."""
        if not file_hash:
            return None
        conn = self._get_connection()
        row = conn.execute(
            "SELECT * FROM file_history WHERE file_hash = ? AND status = 'moved' LIMIT 1",
            (file_hash,),
        ).fetchone()
        return self._row_to_file_record(row) if row else None

    # Custom Rule Operations

    def add_rule(self, rule: CustomRule) -> int:
        """Insert a new custom rule and return its ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO custom_rules
                    (name, pattern, target_folder, is_regex,
                     case_sensitive, enabled, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rule.name,
                    rule.pattern,
                    rule.target_folder,
                    int(rule.is_regex),
                    int(rule.case_sensitive),
                    int(rule.enabled),
                    rule.priority,
                ),
            )
            rule.id = cursor.lastrowid
            return rule.id  # type: ignore[return-value]

    def get_all_rules(self) -> list[CustomRule]:
        """Retrieve all custom rules ordered by priority."""
        conn = self._get_connection()
        rows = conn.execute(
            "SELECT * FROM custom_rules ORDER BY priority ASC"
        ).fetchall()
        return [self._row_to_rule(row) for row in rows]

    def update_rule(self, rule: CustomRule) -> None:
        """Update an existing custom rule."""
        with self._get_connection() as conn:
            conn.execute(
                """
                UPDATE custom_rules SET
                    name=?, pattern=?, target_folder=?, is_regex=?,
                    case_sensitive=?, enabled=?, priority=?
                WHERE id=?
                """,
                (
                    rule.name,
                    rule.pattern,
                    rule.target_folder,
                    int(rule.is_regex),
                    int(rule.case_sensitive),
                    int(rule.enabled),
                    rule.priority,
                    rule.id,
                ),
            )

    def delete_rule(self, rule_id: int) -> None:
        """Delete a custom rule by ID."""
        with self._get_connection() as conn:
            conn.execute(
                "DELETE FROM custom_rules WHERE id = ?", (rule_id,)
            )

    # Internal Helpers

    @staticmethod
    def _row_to_file_record(row: sqlite3.Row) -> FileRecord:
        return FileRecord(
            id=row["id"],
            original_name=row["original_name"],
            original_path=row["original_path"],
            destination_path=row["destination_path"],
            category=row["category"],
            file_size=row["file_size"],
            file_hash=row["file_hash"],
            status=row["status"],
            timestamp=row["timestamp"],
        )

    @staticmethod
    def _row_to_rule(row: sqlite3.Row) -> CustomRule:
        return CustomRule(
            id=row["id"],
            name=row["name"],
            pattern=row["pattern"],
            target_folder=row["target_folder"],
            is_regex=bool(row["is_regex"]),
            case_sensitive=bool(row["case_sensitive"]),
            enabled=bool(row["enabled"]),
            priority=row["priority"],
        )
