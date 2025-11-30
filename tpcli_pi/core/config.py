"""Configuration management for tpcli-pi-tools."""

import logging
import os
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


def _get_config_paths() -> list[str]:
    """Get list of config file paths in order of precedence (highest to lowest)."""
    home = Path.home()
    xdg_config = os.getenv("XDG_CONFIG_HOME", "")

    paths = []

    # XDG standard location (if set)
    if xdg_config:
        paths.append(str(Path(xdg_config) / "tpcli" / "config.yaml"))

    # Global user config (~/.config/tpcli/config.yaml)
    paths.append(str(home / ".config" / "tpcli" / "config.yaml"))

    # Legacy home config (~/.tpcli.yaml)
    paths.append(str(home / ".tpcli.yaml"))

    # Local config in current directory
    paths.append("./.tpcli.yaml")

    return paths


def load_config() -> dict[str, Any]:
    """Load configuration from file.

    Returns the first config file found, following precedence order.
    Returns empty dict if no config file found.
    """
    for config_path in _get_config_paths():
        if Path(config_path).exists():
            try:
                with open(config_path) as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                # If we can't read it, log and try next path
                logger.debug(f"Failed to load config from {config_path}: {e}")
                continue

    return {}


def get_default_art() -> str | None:
    """Get default ART from config.

    Returns:
        Default ART name from config, or None if not set
    """
    config = load_config()
    return config.get("default-art")


def get_default_team() -> str | None:
    """Get default team from config.

    Returns:
        Default team name from config, or None if not set
    """
    config = load_config()
    return config.get("default-team")
