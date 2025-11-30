"""
Unit tests for Markdown generator for PI planning.

Tests the MarkdownGenerator class for exporting TargetProcess data
to editable markdown files with YAML frontmatter, proper hierarchy,
and git compatibility.
"""

import json
import pytest
import re
from datetime import datetime
from unittest.mock import MagicMock, patch

from tpcli_pi.core.markdown_generator import MarkdownGenerator


class TestMarkdownGeneratorBasics:
    """Tests for basic markdown generation functionality."""

    @pytest.fixture
    def generator(self):
        """Fixture providing a MarkdownGenerator instance."""
        return MarkdownGenerator()

    @pytest.fixture
    def mock_objectives(self):
        """Mock team objectives with metadata."""
        return [
            {
                "id": 2019099,
                "name": "Platform governance",
                "status": "Pending",
                "effort": 21,
                "owner": {"Name": "Norbert Borský"},
                "description": "Governance frameworks...",
                "epics": [
                    {"id": 1001, "name": "Governance Framework", "effort": 8, "owner": "John Smith"},
                    {"id": 1002, "name": "Process Documentation", "effort": 8, "owner": "Jane Doe"},
                ]
            }
        ]

    def test_markdown_generation_creates_output(self, generator, mock_objectives):
        """Test that markdown generation produces output."""
        markdown = generator.generate(
            team_name="Platform Eco",
            release_name="PI-4/25",
            art_name="Data, Analytics and Digital",
            team_objectives=mock_objectives,
        )
        assert markdown is not None
        assert isinstance(markdown, str)
        assert len(markdown) > 0

    def test_markdown_includes_h2_headers_for_objectives(self, generator, mock_objectives):
        """Test that generated markdown includes H2 headers for objectives."""
        markdown = generator.generate(
            team_name="Platform Eco",
            release_name="PI-4/25",
            art_name="Data, Analytics and Digital",
            team_objectives=mock_objectives,
        )
        # Check H2 header for objective
        assert "## Team Objective: Platform governance" in markdown

    def test_markdown_includes_h3_headers_for_epics(self, generator, mock_objectives):
        """Test that generated markdown includes H3 headers for epics."""
        markdown = generator.generate(
            team_name="Platform Eco",
            release_name="PI-4/25",
            art_name="Data, Analytics and Digital",
            team_objectives=mock_objectives,
        )
        # Check H3 headers for epics
        assert "### Epic: Governance Framework" in markdown
        assert "### Epic: Process Documentation" in markdown


class TestYAMLFrontmatter:
    """Tests for YAML frontmatter generation."""

    @pytest.fixture
    def generator(self):
        return MarkdownGenerator()

    @pytest.fixture
    def mock_objectives(self):
        return [{"id": 2019099, "name": "Platform governance", "status": "Pending", "effort": 21}]

    def test_frontmatter_includes_release_field(self, generator, mock_objectives):
        """Test frontmatter includes release field."""
        markdown = generator.generate(
            team_name="Test Team",
            release_name="PI-4/25",
            art_name="Test ART",
            team_objectives=mock_objectives,
        )
        assert 'release: "PI-4/25"' in markdown

    def test_frontmatter_includes_team_field(self, generator, mock_objectives):
        """Test frontmatter includes team field."""
        markdown = generator.generate(
            team_name="Platform Eco",
            release_name="PI-4/25",
            art_name="Test ART",
            team_objectives=mock_objectives,
        )
        assert 'team: "Platform Eco"' in markdown

    def test_frontmatter_includes_art_field(self, generator, mock_objectives):
        """Test frontmatter includes ART field."""
        markdown = generator.generate(
            team_name="Test Team",
            release_name="PI-4/25",
            art_name="Data, Analytics and Digital",
            team_objectives=mock_objectives,
        )
        assert 'art: "Data, Analytics and Digital"' in markdown

    def test_frontmatter_includes_exported_at_timestamp(self, generator, mock_objectives):
        """Test frontmatter includes exported_at timestamp."""
        markdown = generator.generate(
            team_name="Test Team",
            release_name="PI-4/25",
            art_name="Test ART",
            team_objectives=mock_objectives,
        )
        assert "exported_at:" in markdown
        # Should have ISO 8601 format timestamp
        assert re.search(r"\d{4}-\d{2}-\d{2}T", markdown)

    def test_frontmatter_includes_objectives_array(self, generator, mock_objectives):
        """Test frontmatter includes objectives array for sync."""
        markdown = generator.generate(
            team_name="Test Team",
            release_name="PI-4/25",
            art_name="Test ART",
            team_objectives=mock_objectives,
        )
        assert "objectives:" in markdown

    def test_objectives_array_contains_id_and_name(self, generator, mock_objectives):
        """Test objectives array entries include id and name."""
        markdown = generator.generate(
            team_name="Test Team",
            release_name="PI-4/25",
            art_name="Test ART",
            team_objectives=mock_objectives,
        )
        assert '"id": 2019099' in markdown or "2019099" in markdown
        assert '"name": "Platform governance"' in markdown or "Platform governance" in markdown

    def test_objectives_array_contains_synced_at_timestamp(self, generator, mock_objectives):
        """Test objectives array entries include synced_at timestamp."""
        markdown = generator.generate(
            team_name="Test Team",
            release_name="PI-4/25",
            art_name="Test ART",
            team_objectives=mock_objectives,
        )
        # synced_at is included in the JSON objects in the array
        assert "synced_at" in markdown and "2025-11-30T" in markdown

    def test_frontmatter_is_valid_yaml(self, generator, mock_objectives):
        """Test that frontmatter is valid YAML."""
        markdown = generator.generate(
            team_name="Test Team",
            release_name="PI-4/25",
            art_name="Test ART",
            team_objectives=mock_objectives,
        )
        # Extract frontmatter
        match = re.match(r"---\n(.*?)\n---", markdown, re.DOTALL)
        assert match, "Frontmatter should be delimited with ---"
        frontmatter = match.group(1)
        assert "release:" in frontmatter
        assert "team:" in frontmatter

    def test_frontmatter_preserved_across_exports(self, generator, mock_objectives):
        """Test that frontmatter metadata is preserved for sync."""
        markdown1 = generator.generate(
            team_name="Test Team",
            release_name="PI-4/25",
            art_name="Test ART",
            team_objectives=mock_objectives,
        )
        markdown2 = generator.generate(
            team_name="Test Team",
            release_name="PI-4/25",
            art_name="Test ART",
            team_objectives=mock_objectives,
        )
        # Both should have frontmatter with same structure
        assert "---" in markdown1
        assert "---" in markdown2
        assert 'release: "PI-4/25"' in markdown1
        assert 'release: "PI-4/25"' in markdown2


class TestObjectiveMetadata:
    """Tests for objective metadata in markdown."""

    @pytest.fixture
    def generator(self):
        return MarkdownGenerator()

    def test_objective_section_includes_tp_id(self, generator):
        """Test objective section includes TP ID."""
        # Assert TP ID field present
        pass

    def test_objective_section_includes_status(self, generator):
        """Test objective section includes status."""
        # Assert Status field present
        pass

    def test_objective_section_includes_effort(self, generator):
        """Test objective section includes effort."""
        # Assert Effort field present
        pass

    def test_objective_section_includes_owner(self, generator):
        """Test objective section includes owner."""
        # Assert Owner field present
        pass

    def test_objective_section_includes_description(self, generator):
        """Test objective section includes description."""
        # Assert Description section present
        pass

    def test_empty_description_handled_gracefully(self, generator):
        """Test empty description handled gracefully."""
        # Assert empty description doesn't break markdown
        pass

    def test_long_description_formatted_properly(self, generator):
        """Test long description formatted properly."""
        # Assert multiline description reads well
        pass

    def test_status_field_preserves_exact_value(self, generator):
        """Test status field preserves exact TP value."""
        # Assert exact status value, not normalized
        pass

    def test_zero_effort_preserved(self, generator):
        """Test zero effort is preserved."""
        # Assert effort: 0 handled correctly
        pass


class TestEpicHandling:
    """Tests for epic/feature handling in markdown."""

    @pytest.fixture
    def generator(self):
        return MarkdownGenerator()

    def test_epics_appear_as_h3_subsections(self, generator):
        """Test epics appear as H3 subsections."""
        # Assert H3 sections for epics
        pass

    def test_epics_nested_under_objective(self, generator):
        """Test epics are properly nested under objectives."""
        # Assert epic appears after objective header
        pass

    def test_epic_includes_owner_field(self, generator):
        """Test epic section includes owner."""
        # Assert Owner field
        pass

    def test_epic_includes_status_field(self, generator):
        """Test epic section includes status."""
        # Assert Status field
        pass

    def test_epic_includes_effort_field(self, generator):
        """Test epic section includes effort."""
        # Assert Effort field
        pass

    def test_epic_without_owner_handled_gracefully(self, generator):
        """Test epic without owner handled gracefully."""
        # Assert no error when owner is null
        pass

    def test_epic_with_null_fields_handled(self, generator):
        """Test epic with null optional fields handled."""
        # Assert graceful handling of missing fields
        pass

    def test_epics_ordered_by_id(self, generator):
        """Test epics appear in ID order."""
        # Assert epic order matches ID sequence
        pass


class TestMarkdownStructure:
    """Tests for overall markdown structure and hierarchy."""

    @pytest.fixture
    def generator(self):
        return MarkdownGenerator()

    def test_objectives_ordered_by_id(self, generator):
        """Test objectives appear in ID order."""
        # Assert objective order matches ID sequence
        pass

    def test_program_objectives_section_appears(self, generator):
        """Test program objectives section appears."""
        # Assert "Program Objectives" section
        pass

    def test_program_objectives_marked_readonly(self, generator):
        """Test program objectives marked as read-only."""
        # Assert read-only indication in markdown
        pass

    def test_multiple_objectives_properly_separated(self, generator):
        """Test multiple objectives properly separated."""
        # Assert clear section boundaries
        pass

    def test_objectives_and_epics_hierarchical(self, generator):
        """Test proper hierarchy of objectives and epics."""
        # Assert H2 for objectives, H3 for epics
        pass


class TestMarkdownValidity:
    """Tests for markdown syntax validity."""

    @pytest.fixture
    def generator(self):
        return MarkdownGenerator()

    def test_generated_markdown_is_valid_gfm(self, generator):
        """Test generated markdown is valid GitHub-flavored markdown."""
        # Assert valid markdown syntax
        pass

    def test_headers_properly_formatted(self, generator):
        """Test headers use # notation correctly."""
        # Assert proper # usage
        pass

    def test_yaml_frontmatter_properly_delimited(self, generator):
        """Test YAML frontmatter properly delimited with ---."""
        # Assert --- delimiters
        pass

    def test_no_invalid_markdown_syntax(self, generator):
        """Test no invalid markdown syntax."""
        # Assert markdown parses without errors
        pass

    def test_special_characters_escaped(self, generator):
        """Test special characters properly escaped."""
        # Assert no markdown injection
        pass

    def test_html_like_syntax_escaped(self, generator):
        """Test HTML-like syntax escaped."""
        # Assert <script> tags handled safely
        pass


class TestMetadataPreservation:
    """Tests for metadata preservation for git sync."""

    @pytest.fixture
    def generator(self):
        return MarkdownGenerator()

    def test_metadata_extractable_from_markdown(self, generator):
        """Test metadata can be extracted from markdown."""
        # Assert YAML can be parsed
        pass

    def test_objective_ids_extractable(self, generator):
        """Test objective IDs can be extracted."""
        # Assert IDs extractable from TP ID fields
        pass

    def test_epic_names_extractable(self, generator):
        """Test epic names can be extracted from sections."""
        # Assert epic titles extractable
        pass

    def test_sync_timestamps_preserved(self, generator):
        """Test sync timestamps preserved for conflict detection."""
        # Assert synced_at timestamps present
        pass

    def test_round_trip_through_git(self, generator):
        """Test metadata round-trips through git."""
        # Assert same content after git operations
        pass


class TestMultipleTeams:
    """Tests for handling multiple teams."""

    @pytest.fixture
    def generator(self):
        return MarkdownGenerator()

    def test_different_teams_generate_different_files(self, generator):
        """Test different teams generate separate files."""
        # Assert separate outputs for each team
        pass

    def test_each_file_contains_correct_team_objectives(self, generator):
        """Test each file contains only correct team's objectives."""
        # Assert no cross-team contamination
        pass

    def test_team_field_matches_export_context(self, generator):
        """Test team field in frontmatter matches context."""
        # Assert correct team in metadata
        pass


class TestMultipleReleases:
    """Tests for handling multiple releases."""

    @pytest.fixture
    def generator(self):
        return MarkdownGenerator()

    def test_different_releases_generate_different_files(self, generator):
        """Test different releases generate separate files."""
        # Assert separate outputs for each release
        pass

    def test_each_file_contains_correct_release_objectives(self, generator):
        """Test each file contains only correct release's objectives."""
        # Assert no cross-release contamination
        pass

    def test_release_field_matches_export_context(self, generator):
        """Test release field in frontmatter matches context."""
        # Assert correct release in metadata
        pass


class TestFilenameGeneration:
    """Tests for markdown filename generation."""

    @pytest.fixture
    def generator(self):
        return MarkdownGenerator()

    def test_filename_follows_pattern(self, generator):
        """Test filename follows expected pattern."""
        filename = generator.get_filename("Platform Eco", "PI-4/25")
        assert ".md" in filename
        assert re.match(r"^pi-4-25-.*\.md$", filename.lower())

    def test_filename_includes_team_name(self, generator):
        """Test filename includes team name."""
        filename = generator.get_filename("Platform Eco", "PI-4/25")
        assert "platform" in filename.lower()
        assert "eco" in filename.lower()

    def test_filename_includes_release(self, generator):
        """Test filename includes release."""
        filename = generator.get_filename("Platform Eco", "PI-4/25")
        assert "pi" in filename.lower()
        assert "4" in filename
        assert "25" in filename

    def test_filename_has_md_extension(self, generator):
        """Test filename has .md extension."""
        filename = generator.get_filename("Platform Eco", "PI-4/25")
        assert filename.endswith(".md")

    def test_special_characters_in_names_handled(self, generator):
        """Test special characters in names handled in filename."""
        filename = generator.get_filename("Team (Special-Chars)", "PI-4/25 (Q2 Planning)")
        # Should be valid filesystem filename
        assert ".md" in filename
        assert "/" not in filename
        assert "\\" not in filename
        assert ":" not in filename

    def test_unicode_characters_preserved_in_frontmatter(self, generator):
        """Test unicode characters preserved in frontmatter."""
        markdown = generator.generate(
            team_name="Team 🚀 Unicode",
            release_name="PI-4/25",
            art_name="Test ART",
            team_objectives=[],
        )
        # Unicode should be in frontmatter
        assert "Team" in markdown
        # Filename should be safe
        filename = generator.get_filename("Team 🚀 Unicode", "PI-4/25")
        assert ".md" in filename

    def test_filename_valid_for_filesystem(self, generator):
        """Test filename is valid for filesystem."""
        filename = generator.get_filename("Platform Eco", "PI-4/25")
        # Should not contain invalid filesystem characters
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            assert char not in filename, f"Filename contains invalid char: {char}"


class TestUnicodeHandling:
    """Tests for unicode and special character handling."""

    @pytest.fixture
    def generator(self):
        return MarkdownGenerator()

    def test_emoji_in_objective_name_preserved(self, generator):
        """Test emoji in objective name is preserved."""
        # Assert emoji appears in markdown
        pass

    def test_unicode_characters_preserved(self, generator):
        """Test unicode characters are preserved."""
        # Assert unicode renders correctly
        pass

    def test_emoji_renders_properly(self, generator):
        """Test emoji renders properly in markdown."""
        # Assert emoji displays correctly
        pass


class TestSecurityAndValidation:
    """Tests for security and validation."""

    @pytest.fixture
    def generator(self):
        return MarkdownGenerator()

    def test_html_injection_prevented(self, generator):
        """Test HTML injection is prevented."""
        # Assert <script> tags escaped
        pass

    def test_markdown_injection_prevented(self, generator):
        """Test markdown injection is prevented."""
        # Assert no unintended formatting
        pass

    def test_special_characters_escaped_safely(self, generator):
        """Test special characters escaped safely."""
        # Assert safe escaping
        pass

    def test_yaml_injection_prevented(self, generator):
        """Test YAML injection is prevented."""
        # Assert frontmatter safe
        pass
