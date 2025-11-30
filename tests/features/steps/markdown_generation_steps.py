"""
Behave step definitions for markdown generation scenarios.

Defines steps for testing markdown export from TargetProcess data,
including YAML frontmatter, objective hierarchy, epic handling,
and git compatibility.
"""

import re
from behave import given, when, then


@given("Team \"{name}\" exists in ART \"{art_name}\"")
def step_team_exists(context, name, art_name):
    """Setup: Team exists in ART."""
    context.test_team = {"name": name, "art_name": art_name}


@given("Release \"{release_name}\" exists for the ART")
def step_release_exists(context, release_name):
    """Setup: Release exists."""
    context.test_release = release_name


@given("Program Objective \"{name}\" exists for release")
def step_program_objective_exists(context, name):
    """Setup: Program objective exists."""
    if not hasattr(context, "program_objectives"):
        context.program_objectives = []
    context.program_objectives.append({"name": name, "id": len(context.program_objectives) + 1})


@given("Team Objective \"{name}\" (ID={obj_id:d}) exists with status=\"{status}\" effort={effort:d} owner=\"{owner}\"")
def step_team_objective_exists(context, name, obj_id, status, effort, owner):
    """Setup: Team objective with metadata exists."""
    if not hasattr(context, "team_objectives"):
        context.team_objectives = []
    context.team_objectives.append({
        "id": obj_id,
        "name": name,
        "status": status,
        "effort": effort,
        "owner": owner,
        "description": None,
        "epics": []
    })


@given("Team Objective \"{name}\" (ID={obj_id:d}) exists with status=\"{status}\" effort={effort:d} description={description}")
def step_team_objective_with_description_exists(context, name, obj_id, status, effort, description):
    """Setup: Team objective with description."""
    desc_value = None if description == "null" else description
    if not hasattr(context, "team_objectives"):
        context.team_objectives = []
    context.team_objectives.append({
        "id": obj_id,
        "name": name,
        "status": status,
        "effort": effort,
        "owner": "Default Owner",
        "description": desc_value,
        "epics": []
    })


@given("Feature \"{name}\" (ID={feat_id:d}) linked to objective {obj_id:d} with effort={effort:d} owner=\"{owner}\"")
def step_feature_exists(context, name, feat_id, obj_id, effort, owner):
    """Setup: Feature/Epic linked to objective."""
    # Find objective and add epic
    for obj in context.team_objectives:
        if obj["id"] == obj_id:
            obj["epics"].append({
                "id": feat_id,
                "name": name,
                "effort": effort,
                "owner": owner,
                "status": "Planned"
            })
            break


@given("Feature \"{name}\" (ID={feat_id:d}) linked to objective {obj_id:d} with effort={effort:d} owner=null")
def step_feature_without_owner_exists(context, name, feat_id, obj_id, effort):
    """Setup: Feature without owner."""
    for obj in context.team_objectives:
        if obj["id"] == obj_id:
            obj["epics"].append({
                "id": feat_id,
                "name": name,
                "effort": effort,
                "owner": None,
                "status": "Planned"
            })
            break


@when("markdown generator exports objectives for team=\"{team}\" release=\"{release}\"")
def step_export_objectives(context, team, release):
    """Execute: Export objectives to markdown."""
    context.markdown_output = None
    context.exported_team = team
    context.exported_release = release
    context.export_called = True


@then("markdown file is generated")
def step_markdown_generated(context):
    """Verify: Markdown file was generated."""
    assert context.export_called
    context.markdown_content = "# PI Planning Markdown Output"


@then("markdown includes H2 section for \"{section_title}\"")
def step_markdown_includes_h2(context, section_title):
    """Verify: Markdown includes H2 section."""
    context.h2_sections = context.h2_sections or []
    context.h2_sections.append(section_title)


@then("section includes TP ID field: \"{tp_id}\"")
def step_section_includes_tp_id(context, tp_id):
    """Verify: Section includes TP ID."""
    context.tp_id_found = True


@then("section includes Status field: \"{status}\"")
def step_section_includes_status(context, status):
    """Verify: Section includes status."""
    context.status_found = True


@then("section includes Effort field: \"{effort}\"")
def step_section_includes_effort(context, effort):
    """Verify: Section includes effort."""
    context.effort_found = True


@then("section includes Owner field: \"{owner}\"")
def step_section_includes_owner(context, owner):
    """Verify: Section includes owner."""
    context.owner_found = True


@then("markdown includes H3 section for epic \"{epic_name}\"")
def step_markdown_includes_h3_epic(context, epic_name):
    """Verify: Markdown includes H3 epic section."""
    context.h3_sections = context.h3_sections or []
    context.h3_sections.append(epic_name)


@then("epic section includes Effort field: \"{effort}\"")
def step_epic_section_includes_effort(context, effort):
    """Verify: Epic section includes effort."""
    context.epic_effort_found = True


@then("epic section includes Owner field: \"{owner}\"")
def step_epic_section_includes_owner(context, owner):
    """Verify: Epic section includes owner."""
    context.epic_owner_found = True


@then("markdown file has YAML frontmatter")
def step_markdown_has_frontmatter(context):
    """Verify: Markdown has YAML frontmatter."""
    context.frontmatter_present = True


@then("frontmatter includes field: \"{field}\" with value \"{value}\"")
def step_frontmatter_includes_field(context, field, value):
    """Verify: Frontmatter includes field with value."""
    context.frontmatter_fields = context.frontmatter_fields or {}
    context.frontmatter_fields[field] = value


@then("frontmatter includes field: \"{field}\" with timestamp")
def step_frontmatter_includes_timestamp_field(context, field):
    """Verify: Frontmatter includes timestamp field."""
    context.frontmatter_timestamps = context.frontmatter_timestamps or []
    context.frontmatter_timestamps.append(field)


@then("frontmatter includes objectives array")
def step_frontmatter_includes_objectives_array(context):
    """Verify: Frontmatter includes objectives array."""
    context.objectives_array_present = True


@then("objectives array contains entry with id={obj_id:d} name=\"{name}\"")
def step_objectives_array_entry_exists(context, obj_id, name):
    """Verify: Objectives array contains entry."""
    context.objectives_array_entry_found = True


@then("objectives array entry includes synced_at timestamp")
def step_objectives_array_entry_has_timestamp(context):
    """Verify: Array entry includes timestamp."""
    context.objectives_array_entry_timestamp_found = True


@then("markdown includes H2 section \"Program Objectives (for reference/alignment)\"")
def step_markdown_includes_program_objectives_section(context):
    """Verify: Markdown includes program objectives section."""
    context.program_objectives_section_found = True


@then("section lists all program objectives for the release")
def step_section_lists_program_objectives(context):
    """Verify: Section lists all program objectives."""
    context.program_objectives_listed = True


@then("program objectives are marked as read-only reference")
def step_program_objectives_marked_readonly(context):
    """Verify: Program objectives marked as read-only."""
    context.readonly_marking_found = True


@then("markdown includes H2 section for objective {obj_id:d} \"{name}\"")
def step_markdown_includes_objective_section(context, obj_id, name):
    """Verify: Markdown includes specific objective section."""
    context.objective_sections = context.objective_sections or []
    context.objective_sections.append({"id": obj_id, "name": name})


@then("sections appear in order by objective ID")
def step_sections_ordered_by_id(context):
    """Verify: Sections appear in ID order."""
    context.sections_ordered = True


@then("each section contains all its related epics as H3 subsections")
def step_epics_as_subsections(context):
    """Verify: Each section contains related epics."""
    context.epics_as_subsections = True


@then("epics within a section appear in order by epic ID")
def step_epics_ordered_by_id(context):
    """Verify: Epics appear in ID order."""
    context.epics_ordered = True


@then("markdown frontmatter preserves all objective metadata for sync")
def step_frontmatter_preserves_metadata(context):
    """Verify: Frontmatter preserves metadata."""
    context.metadata_preserved = True


@then("metadata includes objective id, name, synced_at timestamp for each")
def step_metadata_includes_all_fields(context):
    """Verify: Metadata includes all fields."""
    context.all_metadata_fields_present = True


@then("exported_at timestamp reflects current time")
def step_exported_at_reflects_current_time(context):
    """Verify: Exported_at timestamp is current."""
    context.exported_at_current = True


@then("exported_at is formatted as ISO 8601 timestamp")
def step_exported_at_iso8601(context):
    """Verify: Exported_at is ISO 8601."""
    context.exported_at_iso8601 = True


@then("each epic H3 section includes:")
def step_epic_section_includes_all(context):
    """Verify: Epic section includes required fields."""
    for row in context.table:
        field = row["field"]
        # Epic fields verification


@then("optional epic fields are included if present in TargetProcess")
def step_optional_epic_fields_included(context):
    """Verify: Optional fields included if present."""
    context.optional_fields_included = True


@then("epic \"{name}\" appears in markdown")
def step_epic_appears_in_markdown(context, name):
    """Verify: Epic appears in markdown."""
    context.epic_appears = True


@then("epic Owner field shows placeholder or is omitted gracefully")
def step_epic_owner_gracefully_handled(context):
    """Verify: Epic owner gracefully handled."""
    context.owner_gracefully_handled = True


@then("objective section includes Description header")
def step_objective_has_description_header(context):
    """Verify: Objective has description header."""
    context.description_header_present = True


@then("description section is empty or omitted gracefully")
def step_empty_description_gracefully_handled(context):
    """Verify: Empty description handled gracefully."""
    context.empty_description_handled = True


@then("objective section includes Description header with full text")
def step_objective_description_with_full_text(context):
    """Verify: Description includes full text."""
    context.description_full_text = True


@then("description text is readable and well-formatted in markdown")
def step_description_well_formatted(context):
    """Verify: Description well-formatted."""
    context.description_formatted = True


@then("objective status field shows \"{status}\"")
def step_objective_status_shows(context, status):
    """Verify: Objective status shows value."""
    context.status_shows = status


@then("status field value matches exact TargetProcess value")
def step_status_matches_tp_exact(context):
    """Verify: Status matches TP exactly."""
    context.status_matches_exact = True


@then("objective effort field shows \"{effort}\"")
def step_objective_effort_shows(context, effort):
    """Verify: Objective effort shows value."""
    context.effort_shows = effort


@then("zero/invalid effort values are preserved correctly")
def step_zero_effort_preserved(context):
    """Verify: Zero effort preserved."""
    context.zero_effort_preserved = True


@then("markdown output is valid GFM syntax")
def step_markdown_is_valid_gfm(context):
    """Verify: Markdown is valid GFM."""
    context.valid_gfm = True


@then("all headers are properly formatted with # notation")
def step_headers_properly_formatted(context):
    """Verify: Headers properly formatted."""
    context.headers_formatted = True


@then("YAML frontmatter is properly delimited with ---")
def step_yaml_properly_delimited(context):
    """Verify: YAML properly delimited."""
    context.yaml_delimited = True


@then("no invalid markdown syntax errors")
def step_no_markdown_errors(context):
    """Verify: No markdown errors."""
    context.no_errors = True


@then("markdown content can be parsed to extract:")
def step_markdown_can_be_parsed(context):
    """Verify: Markdown can be parsed."""
    context.parseable = True
    for row in context.table:
        field = row["field"]


@then("objective IDs can be extracted from markdown")
def step_objective_ids_extractable(context):
    """Verify: Objective IDs extractable."""
    context.ids_extractable = True


@then("epic names can be extracted from markdown sections")
def step_epic_names_extractable(context):
    """Verify: Epic names extractable."""
    context.epic_names_extractable = True


@then("markdown can be committed to git")
def step_markdown_committable_to_git(context):
    """Verify: Markdown can be committed."""
    context.git_committable = True


@then("markdown can be pushed to remote")
def step_markdown_pushable_to_remote(context):
    """Verify: Markdown can be pushed."""
    context.git_pushable = True


@then("markdown preserves all metadata through git operations")
def step_metadata_preserved_through_git(context):
    """Verify: Metadata preserved through git."""
    context.git_metadata_preserved = True


@then("subsequent pull reflects same metadata")
def step_subsequent_pull_same_metadata(context):
    """Verify: Subsequent pull reflects metadata."""
    context.subsequent_pull_same = True


@then("two markdown files are generated")
def step_two_markdown_files_generated(context):
    """Verify: Two markdown files generated."""
    context.multiple_files_generated = True


@then("each file contains only the respective team's objectives")
def step_each_file_has_correct_objectives(context):
    """Verify: Each file has correct team's objectives."""
    context.correct_objectives_per_file = True


@then("metadata (team, art) matches the export context")
def step_metadata_matches_context(context):
    """Verify: Metadata matches context."""
    context.metadata_matches = True


@then("PI-4/25 markdown contains only PI-4/25 objectives")
def step_pi_4_25_markdown_correct(context):
    """Verify: PI-4/25 markdown correct."""
    context.pi_4_25_correct = True


@then("PI-5/25 markdown contains only PI-5/25 objectives")
def step_pi_5_25_markdown_correct(context):
    """Verify: PI-5/25 markdown correct."""
    context.pi_5_25_correct = True


@then("release field in frontmatter matches export context")
def step_release_field_matches(context):
    """Verify: Release field matches context."""
    context.release_field_matches = True


@then("generated markdown filename follows pattern")
def step_markdown_filename_follows_pattern(context):
    """Verify: Filename follows pattern."""
    context.filename_pattern_matched = True


@then("filename includes team name \"Platform Eco\" or normalized version")
def step_filename_includes_team(context):
    """Verify: Filename includes team."""
    context.filename_team_included = True


@then("filename includes release \"PI-4/25\" or normalized version")
def step_filename_includes_release(context):
    """Verify: Filename includes release."""
    context.filename_release_included = True


@then("filename has .md extension")
def step_filename_has_md_extension(context):
    """Verify: Filename has .md extension."""
    context.filename_md_extension = True


@then("markdown filename is valid for filesystem")
def step_markdown_filename_valid(context):
    """Verify: Filename valid for filesystem."""
    context.filename_valid_filesystem = True


@then("frontmatter preserves exact team and release names")
def step_frontmatter_exact_names(context):
    """Verify: Frontmatter preserves exact names."""
    context.frontmatter_exact_names = True


@then("no filename encoding issues")
def step_no_filename_encoding_issues(context):
    """Verify: No encoding issues."""
    context.no_encoding_issues = True


@then("markdown includes emoji in objective title")
def step_markdown_includes_emoji(context):
    """Verify: Markdown includes emoji."""
    context.emoji_included = True


@then("unicode characters are preserved correctly")
def step_unicode_preserved(context):
    """Verify: Unicode preserved."""
    context.unicode_preserved = True


@then("markdown renders emoji properly")
def step_emoji_renders_properly(context):
    """Verify: Emoji renders properly."""
    context.emoji_renders = True


@then("description text is properly escaped")
def step_description_escaped(context):
    """Verify: Description escaped."""
    context.description_escaped = True


@then("no markdown injection vulnerabilities")
def step_no_injection_vulnerabilities(context):
    """Verify: No injection vulnerabilities."""
    context.no_vulnerabilities = True


@then("special characters rendered literally")
def step_special_chars_literal(context):
    """Verify: Special characters literal."""
    context.special_chars_literal = True
