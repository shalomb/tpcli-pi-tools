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


def get_jira_url() -> str:
    """Get Jira URL from config or environment.

    Priority:
    1. Config file (jira-url key)
    2. Environment variable (JIRA_URL)
    3. Default (https://jira.takeda.com)

    Returns:
        Jira instance URL
    """
    config = load_config()
    return config.get("jira-url") or os.getenv("JIRA_URL", "https://jira.takeda.com")


def get_jira_token() -> str | None:
    """Get Jira API token from config or environment.

    Priority:
    1. Config file (jira-token key)
    2. Environment variable (JIRA_TOKEN)
    3. None (will require user to set one)

    Returns:
        Jira API token, or None if not set
    """
    config = load_config()
    return config.get("jira-token") or os.getenv("JIRA_TOKEN")


def get_tp_url() -> str | None:
    """Get TargetProcess URL from config or environment.

    Priority:
    1. Config file (url key - shared with Go CLI)
    2. Config file (tp-url key - backward compatibility)
    3. Environment variable (TP_URL)
    4. None (will use API client default)

    Returns:
        TargetProcess URL, or None if not set
    """
    config = load_config()
    return config.get("url") or config.get("tp-url") or os.getenv("TP_URL")


def get_tp_token() -> str | None:
    """Get TargetProcess API token from config or environment.

    Priority:
    1. Config file (token key - shared with Go CLI)
    2. Config file (tp-token key - backward compatibility)
    3. Config file (api-token key for backward compatibility)
    4. Environment variable (TP_TOKEN)
    5. Environment variable (TARGETPROCESS_API_TOKEN for backward compatibility)
    6. None (will require user to set one)

    Returns:
        TargetProcess API token, or None if not set
    """
    config = load_config()
    # Try keys in order of preference: Go CLI shared key first, then backward compat keys
    token = (
        config.get("token")  # Shared with Go CLI
        or config.get("tp-token")  # Old Python-only key
        or config.get("api-token")  # Even older key name
        or os.getenv("TP_TOKEN")
        or os.getenv("TARGETPROCESS_API_TOKEN")
    )
    return token
