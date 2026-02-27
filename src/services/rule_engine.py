from __future__ import annotations

import re
from pathlib import Path

from src.models.file_record import CustomRule
from src.models.database import Database
from src.utils.logger import logger


class RuleEngine:
    """
    Evaluates custom rules against filenames.

    Rules are processed in priority order (lowest number first).
    The first matching rule wins and determines the destination folder.
    """

    def __init__(self, database: Database) -> None:
        self._db = database
        self._rules: list[CustomRule] = []
        self.reload_rules()

    def reload_rules(self) -> None:
        """Refresh rules from the database."""
        self._rules = self._db.get_all_rules()
        logger.debug("Loaded %d custom rules", len(self._rules))

    def evaluate(self, file_path: Path) -> str | None:
        """
        Evaluate all enabled rules against a filename.

        Args:
            file_path: Path to the file being organized.

        Returns:
            Target folder name if a rule matches, None otherwise.
        """
        filename = file_path.name

        for rule in self._rules:
            if not rule.enabled:
                continue

            if self._matches(rule, filename):
                logger.info(
                    "Rule '%s' matched file '%s' → %s",
                    rule.name, filename, rule.target_folder,
                )
                return rule.target_folder

        return None

    @staticmethod
    def _matches(rule: CustomRule, filename: str) -> bool:
        """Check if a rule matches a filename."""
        pattern = rule.pattern
        target = filename

        if rule.is_regex:
            flags = 0 if rule.case_sensitive else re.IGNORECASE
            try:
                return bool(re.search(pattern, target, flags))
            except re.error:
                logger.warning("Invalid regex pattern in rule '%s': %s", rule.name, pattern)
                return False
        else:
            if not rule.case_sensitive:
                pattern = pattern.lower()
                target = target.lower()
            return pattern in target

    # Rule CRUD (delegates to database)

    def add_rule(
        self,
        name: str,
        pattern: str,
        target_folder: str,
        is_regex: bool = False,
        case_sensitive: bool = False,
        priority: int = 0,
    ) -> CustomRule:
        """Create and persist a new rule."""
        rule = CustomRule(
            name=name,
            pattern=pattern,
            target_folder=target_folder,
            is_regex=is_regex,
            case_sensitive=case_sensitive,
            priority=priority,
        )
        self._db.add_rule(rule)
        self.reload_rules()
        return rule

    def update_rule(self, rule: CustomRule) -> None:
        """Update an existing rule."""
        self._db.update_rule(rule)
        self.reload_rules()

    def delete_rule(self, rule_id: int) -> None:
        """Delete a rule by ID."""
        self._db.delete_rule(rule_id)
        self.reload_rules()

    @property
    def rules(self) -> list[CustomRule]:
        """Return the current list of rules."""
        return list(self._rules)
