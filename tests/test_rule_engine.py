import shutil
import tempfile
from pathlib import Path

import pytest

from src.models.database import Database
from src.services.rule_engine import RuleEngine


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield Path(d)
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def db(temp_dir):
    return Database(db_path=temp_dir / "test.db")


@pytest.fixture
def engine(db):
    return RuleEngine(database=db)


class TestRuleEngine:
    """Test suite for the custom rule engine."""

    def test_no_rules_returns_none(self, engine, temp_dir):
        """Without rules, evaluate should return None."""
        result = engine.evaluate(temp_dir / "file.pdf")
        assert result is None

    def test_substring_match(self, engine, temp_dir):
        """Substring rules should match filenames containing the pattern."""
        engine.add_rule(
            name="Invoice rule",
            pattern="invoice",
            target_folder="Finance",
        )

        assert engine.evaluate(temp_dir / "invoice_2024.pdf") == "Finance"
        assert engine.evaluate(temp_dir / "MY_INVOICE.PDF") == "Finance"
        assert engine.evaluate(temp_dir / "report.pdf") is None

    def test_case_sensitive_match(self, engine, temp_dir):
        """Case-sensitive rules should respect casing."""
        engine.add_rule(
            name="Exact case",
            pattern="README",
            target_folder="Docs",
            case_sensitive=True,
        )

        assert engine.evaluate(temp_dir / "README.md") == "Docs"
        assert engine.evaluate(temp_dir / "readme.md") is None

    def test_regex_match(self, engine, temp_dir):
        """Regex rules should match using regular expressions."""
        engine.add_rule(
            name="Date pattern",
            pattern=r"\d{4}-\d{2}-\d{2}",
            target_folder="Dated",
            is_regex=True,
        )

        assert engine.evaluate(temp_dir / "report_2024-01-15.pdf") == "Dated"
        assert engine.evaluate(temp_dir / "report.pdf") is None

    def test_priority_order(self, engine, temp_dir):
        """Higher priority (lower number) rules should win."""
        engine.add_rule(
            name="General",
            pattern="report",
            target_folder="Reports",
            priority=10,
        )
        engine.add_rule(
            name="Specific",
            pattern="report",
            target_folder="Important",
            priority=1,
        )

        assert engine.evaluate(temp_dir / "report.pdf") == "Important"

    def test_disabled_rule_skipped(self, engine, temp_dir):
        """Disabled rules should not match."""
        rule = engine.add_rule(
            name="Disabled",
            pattern="secret",
            target_folder="Hidden",
        )
        rule.enabled = False
        engine.update_rule(rule)

        assert engine.evaluate(temp_dir / "secret.txt") is None

    def test_delete_rule(self, engine, temp_dir):
        """Deleted rules should no longer match."""
        rule = engine.add_rule(
            name="Temp",
            pattern="temp",
            target_folder="Temp",
        )
        engine.delete_rule(rule.id)

        assert engine.evaluate(temp_dir / "temp_file.txt") is None
        assert len(engine.rules) == 0
