"""Unit tests for configuration management module.

Tests config file loading, YAML parsing, precedence order,
and default value retrieval.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from tpcli_pi.core.config import (
    _get_config_paths,
    load_config,
    get_default_art,
    get_default_team,
)


class TestGetConfigPaths:
    """Tests for config path resolution."""

    def test_config_paths_without_xdg_config_home(self) -> None:
        """Test default paths when XDG_CONFIG_HOME is not set."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("tpcli_pi.core.config.Path.home") as mock_home:
                mock_home.return_value = Path("/home/testuser")
                paths = _get_config_paths()

                # Should include ~.config, legacy, and local paths
                assert len(paths) >= 3
                assert "/home/testuser/.config/tpcli/config.yaml" in paths
                assert "/home/testuser/.tpcli.yaml" in paths
                assert "./.tpcli.yaml" in paths

    def test_config_paths_with_xdg_config_home(self) -> None:
        """Test paths when XDG_CONFIG_HOME is set."""
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": "/custom/xdg"}):
            with patch("tpcli_pi.core.config.Path.home") as mock_home:
                mock_home.return_value = Path("/home/testuser")
                paths = _get_config_paths()

                # Should include XDG path first
                assert len(paths) >= 4
                assert "/custom/xdg/tpcli/config.yaml" in paths
                # XDG should be first (highest precedence)
                assert paths[0] == "/custom/xdg/tpcli/config.yaml"

    def test_config_paths_precedence_order(self) -> None:
        """Test that paths are in correct precedence order."""
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": "/xdg"}):
            with patch("tpcli_pi.core.config.Path.home") as mock_home:
                mock_home.return_value = Path("/home/testuser")
                paths = _get_config_paths()

                # XDG should be first (highest priority)
                assert paths[0] == "/xdg/tpcli/config.yaml"
                # ~/.config should be second
                assert paths[1] == "/home/testuser/.config/tpcli/config.yaml"
                # Legacy ~/.tpcli.yaml should be third
                assert paths[2] == "/home/testuser/.tpcli.yaml"
                # Local ./.tpcli.yaml should be last (lowest priority)
                assert paths[3] == "./.tpcli.yaml"


class TestLoadConfig:
    """Tests for loading and parsing YAML config files."""

    def test_load_config_returns_empty_dict_when_no_file_exists(self) -> None:
        """Test that empty dict is returned when no config file exists."""
        with patch("tpcli_pi.core.config._get_config_paths") as mock_paths:
            mock_paths.return_value = ["/nonexistent/path.yaml"]
            config = load_config()
            assert config == {}

    def test_load_config_parses_valid_yaml(self) -> None:
        """Test loading and parsing valid YAML config."""
        yaml_content = """
default-art: "Data, Analytics and Digital"
default-team: "Platform Eco"
tp-url: "https://company.tpondemand.com"
api-token: "test-token-123"
"""
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("tpcli_pi.core.config._get_config_paths") as mock_paths:
                mock_paths.return_value = ["/path/to/config.yaml"]
                with patch("pathlib.Path.exists", return_value=True):
                    config = load_config()

                    assert config["default-art"] == "Data, Analytics and Digital"
                    assert config["default-team"] == "Platform Eco"
                    assert config["tp-url"] == "https://company.tpondemand.com"
                    assert config["api-token"] == "test-token-123"

    def test_load_config_returns_empty_dict_for_empty_file(self) -> None:
        """Test that empty YAML returns empty dict (not None)."""
        with patch("builtins.open", mock_open(read_data="")):
            with patch("tpcli_pi.core.config._get_config_paths") as mock_paths:
                mock_paths.return_value = ["/path/to/config.yaml"]
                with patch("pathlib.Path.exists", return_value=True):
                    config = load_config()
                    assert config == {}

    def test_load_config_uses_first_existing_file(self) -> None:
        """Test that first existing config file is used."""
        yaml_content = "default-art: TestART"

        def mock_exists(self):
            # First path doesn't exist, second path exists
            return str(self) == "/second/path.yaml"

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("tpcli_pi.core.config._get_config_paths") as mock_paths:
                mock_paths.return_value = ["/first/path.yaml", "/second/path.yaml"]
                with patch("pathlib.Path.exists", mock_exists):
                    config = load_config()
                    assert config["default-art"] == "TestART"

    def test_load_config_skips_unreadable_file(self) -> None:
        """Test that unreadable files are skipped in precedence order."""
        yaml_content = "default-art: FoundART"

        def mock_exists(self):
            return True

        def mock_open_func(*args, **kwargs):
            if "/first/path" in str(args):
                raise IOError("Permission denied")
            return mock_open(read_data=yaml_content)()

        with patch("tpcli_pi.core.config._get_config_paths") as mock_paths:
            mock_paths.return_value = ["/first/path.yaml", "/second/path.yaml"]
            with patch("pathlib.Path.exists", mock_exists):
                with patch("builtins.open", side_effect=mock_open_func):
                    config = load_config()
                    # Should skip first file and load second
                    assert config["default-art"] == "FoundART"

    def test_load_config_handles_invalid_yaml(self) -> None:
        """Test graceful handling of invalid YAML syntax."""
        invalid_yaml = """
        default-art: value
        invalid: [unclosed bracket
        """

        with patch("tpcli_pi.core.config._get_config_paths") as mock_paths:
            mock_paths.return_value = ["/only/path.yaml"]
            with patch("pathlib.Path.exists", return_value=True):
                with patch("builtins.open", mock_open(read_data=invalid_yaml)):
                    config = load_config()
                    # Should return empty dict due to parse error
                    assert config == {}

    def test_load_config_with_complex_yaml_structure(self) -> None:
        """Test loading complex YAML with nested structures."""
        yaml_content = """
default-art: "Platform Evolution"
default-team: "Backend Team"
api-config:
  timeout: 30
  retry-count: 3
  headers:
    content-type: "application/json"
teams:
  - name: "Team A"
    id: 1
  - name: "Team B"
    id: 2
"""
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("tpcli_pi.core.config._get_config_paths") as mock_paths:
                mock_paths.return_value = ["/path/to/config.yaml"]
                with patch("pathlib.Path.exists", return_value=True):
                    config = load_config()

                    assert config["default-art"] == "Platform Evolution"
                    assert config["api-config"]["timeout"] == 30
                    assert config["api-config"]["retry-count"] == 3
                    assert len(config["teams"]) == 2
                    assert config["teams"][0]["name"] == "Team A"


class TestGetDefaultArt:
    """Tests for get_default_art() function."""

    def test_get_default_art_returns_value_from_config(self) -> None:
        """Test retrieving default ART from config."""
        with patch("tpcli_pi.core.config.load_config") as mock_load:
            mock_load.return_value = {"default-art": "Data, Analytics and Digital"}
            art = get_default_art()
            assert art == "Data, Analytics and Digital"

    def test_get_default_art_returns_none_when_not_set(self) -> None:
        """Test that None is returned when default-art not in config."""
        with patch("tpcli_pi.core.config.load_config") as mock_load:
            mock_load.return_value = {}
            art = get_default_art()
            assert art is None

    def test_get_default_art_returns_none_from_empty_config(self) -> None:
        """Test None return when config is empty."""
        with patch("tpcli_pi.core.config.load_config") as mock_load:
            mock_load.return_value = {"other-key": "other-value"}
            art = get_default_art()
            assert art is None

    def test_get_default_art_with_special_characters(self) -> None:
        """Test ART name with special characters."""
        special_art = "R&D / Next Gen (AI-ML)"
        with patch("tpcli_pi.core.config.load_config") as mock_load:
            mock_load.return_value = {"default-art": special_art}
            art = get_default_art()
            assert art == special_art


class TestGetDefaultTeam:
    """Tests for get_default_team() function."""

    def test_get_default_team_returns_value_from_config(self) -> None:
        """Test retrieving default team from config."""
        with patch("tpcli_pi.core.config.load_config") as mock_load:
            mock_load.return_value = {"default-team": "Platform Eco"}
            team = get_default_team()
            assert team == "Platform Eco"

    def test_get_default_team_returns_none_when_not_set(self) -> None:
        """Test that None is returned when default-team not in config."""
        with patch("tpcli_pi.core.config.load_config") as mock_load:
            mock_load.return_value = {}
            team = get_default_team()
            assert team is None

    def test_get_default_team_returns_none_from_empty_config(self) -> None:
        """Test None return when config is empty."""
        with patch("tpcli_pi.core.config.load_config") as mock_load:
            mock_load.return_value = {"other-key": "other-value"}
            team = get_default_team()
            assert team is None

    def test_get_default_team_with_special_characters(self) -> None:
        """Test team name with special characters."""
        special_team = "Cloud Enablement & Delivery (CED)"
        with patch("tpcli_pi.core.config.load_config") as mock_load:
            mock_load.return_value = {"default-team": special_team}
            team = get_default_team()
            assert team == special_team


class TestConfigIntegration:
    """Integration tests for config module with real temp files."""

    def test_load_config_with_real_temp_file(self) -> None:
        """Test loading config from actual temp file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("""
default-art: "Test ART"
default-team: "Test Team"
tp-url: "https://test.tpondemand.com"
""")
            f.flush()
            temp_path = f.name

        try:
            with patch("tpcli_pi.core.config._get_config_paths") as mock_paths:
                mock_paths.return_value = [temp_path]
                config = load_config()

                assert config["default-art"] == "Test ART"
                assert config["default-team"] == "Test Team"
                assert config["tp-url"] == "https://test.tpondemand.com"
        finally:
            Path(temp_path).unlink()

    def test_load_config_precedence_with_temp_files(self) -> None:
        """Test precedence order with multiple temp files."""
        # Create first config
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f1:
            f1.write("default-art: FirstART\n")
            f1.flush()
            first_path = f1.name

        # Create second config
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f2:
            f2.write("default-art: SecondART\n")
            f2.flush()
            second_path = f2.name

        try:
            # First path should be used (highest precedence)
            with patch("tpcli_pi.core.config._get_config_paths") as mock_paths:
                mock_paths.return_value = [first_path, second_path]
                config = load_config()
                assert config["default-art"] == "FirstART"

            # If first doesn't exist, second should be used
            with patch("tpcli_pi.core.config._get_config_paths") as mock_paths:
                mock_paths.return_value = ["/nonexistent.yaml", second_path]
                config = load_config()
                assert config["default-art"] == "SecondART"
        finally:
            Path(first_path).unlink()
            Path(second_path).unlink()

    def test_config_with_unicode_characters(self) -> None:
        """Test config file with Unicode characters."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            f.write("""
default-art: "数据分析 (Data Analytics)"
default-team: "πρωτοποίηση (Prototyping)"
""")
            f.flush()
            temp_path = f.name

        try:
            with patch("tpcli_pi.core.config._get_config_paths") as mock_paths:
                mock_paths.return_value = [temp_path]
                config = load_config()

                assert "数据分析" in config["default-art"]
                assert "πρωτοποίηση" in config["default-team"]
        finally:
            Path(temp_path).unlink()
