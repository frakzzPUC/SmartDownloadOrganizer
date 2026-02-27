from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

from src.utils.constants import (
    DEFAULT_CONFIG_PATH,
    DEFAULT_DOWNLOADS_PATH,
    FILE_CATEGORIES,
)


@dataclass
class AppConfig:
    """Application configuration with sensible defaults."""

    watch_folder: str = str(DEFAULT_DOWNLOADS_PATH)
    destination_folder: str = str(DEFAULT_DOWNLOADS_PATH)
    auto_start_monitoring: bool = False
    start_with_system: bool = False
    show_notifications: bool = True
    theme: str = "dark"
    custom_rules: list[dict[str, str]] = field(default_factory=list)
    category_overrides: dict[str, list[str]] = field(default_factory=dict)

    @property
    def watch_path(self) -> Path:
        return Path(self.watch_folder)

    @property
    def destination_path(self) -> Path:
        return Path(self.destination_folder)

    def get_categories(self) -> dict[str, list[str]]:
        """Return merged file categories (defaults + user overrides)."""
        merged = dict(FILE_CATEGORIES)
        merged.update(self.category_overrides)
        return merged


class ConfigManager:
    """Manages persistence of application configuration."""

    def __init__(self, config_dir: Path | None = None) -> None:
        self._config_dir = config_dir or DEFAULT_CONFIG_PATH
        self._config_file = self._config_dir / "config.json"
        self._config_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> AppConfig:
        """Load configuration from disk, returning defaults if not found."""
        if not self._config_file.exists():
            config = AppConfig()
            self.save(config)
            return config

        try:
            with open(self._config_file, "r", encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)
            return AppConfig(**{
                k: v for k, v in data.items()
                if k in AppConfig.__dataclass_fields__
            })
        except (json.JSONDecodeError, TypeError, KeyError):
            return AppConfig()

    def save(self, config: AppConfig) -> None:
        """Persist configuration to disk."""
        with open(self._config_file, "w", encoding="utf-8") as f:
            json.dump(asdict(config), f, indent=2, ensure_ascii=False)

    @property
    def config_path(self) -> Path:
        return self._config_file
