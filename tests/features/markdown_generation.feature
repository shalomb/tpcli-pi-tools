Feature: Markdown Generation from TargetProcess Data

  Markdown generator exports PI planning data from TargetProcess into editable markdown files.
  Supports YAML frontmatter for metadata, Program Objectives as reference, and nested Team
  Objectives with Epics (Features). Compatible with git-native workflows for collaborative editing.

  Background:
    Given Team "Platform Eco" exists in ART "Data, Analytics and Digital"
    And Release "PI-4/25" exists for the ART
    And Program Objective "Data Quality Improvements" exists for release
    And Program Objective "Security Hardening" exists for release
    And Team Objective "Platform governance" (ID=2019099) exists with status="Pending" effort=21 owner="Norbert Borský"
    And Team Objective "Supporting the DQ initiative" (ID=2027963) exists with status="In Progress" effort=34 owner="Sarah Chen"
    And Feature "Governance Framework Definition" (ID=1001) linked to objective 2019099 with effort=8 owner="John Smith"
    And Feature "Process Documentation" (ID=1002) linked to objective 2019099 with effort=8 owner="Jane Doe"
    And Feature "Training and Enablement" (ID=1003) linked to objective 2019099 with effort=5

  Scenario: Generate markdown with team objectives and epics
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then markdown file is generated
    And markdown includes H2 section for "Team Objective: Platform governance"
    And section includes TP ID field: "2019099"
    And section includes Status field: "Pending"
    And section includes Effort field: "21"
    And section includes Owner field: "Norbert Borský"
    And markdown includes H3 section for epic "Governance Framework Definition"
    And epic section includes Effort field: "8"
    And epic section includes Owner field: "John Smith"

  Scenario: YAML frontmatter includes sync metadata
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then markdown file has YAML frontmatter
    And frontmatter includes field: "release" with value "PI-4/25"
    And frontmatter includes field: "team" with value "Platform Eco"
    And frontmatter includes field: "art" with value "Data, Analytics and Digital"
    And frontmatter includes field: "exported_at" with timestamp
    And frontmatter includes objectives array
    And objectives array contains entry with id=2019099 name="Platform governance"
    And objectives array entry includes synced_at timestamp

  Scenario: Program objectives appear as read-only reference section
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then markdown includes H2 section "Program Objectives (for reference/alignment)"
    And section lists all program objectives for the release
    And program objectives are marked as read-only reference

  Scenario: Multiple team objectives organized with proper hierarchy
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then markdown includes H2 section for objective 2019099 "Platform governance"
    And markdown includes H2 section for objective 2027963 "Supporting the DQ initiative"
    And sections appear in order by objective ID
    And each section contains all its related epics as H3 subsections
    And epics within a section appear in order by epic ID

  Scenario: Markdown metadata is preserved in YAML frontmatter
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then markdown frontmatter preserves all objective metadata for sync
    And metadata includes objective id, name, synced_at timestamp for each
    And exported_at timestamp reflects current time
    And exported_at is formatted as ISO 8601 timestamp

  Scenario: Epic metadata includes all required fields
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then each epic H3 section includes:
      | field   |
      | Owner   |
      | Status  |
      | Effort  |
    And optional epic fields are included if present in TargetProcess

  Scenario: Epics without owner field are handled gracefully
    Given Feature "Orphan Epic" (ID=1004) linked to objective 2019099 with effort=3 owner=null
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then epic "Orphan Epic" appears in markdown
    And epic Owner field shows placeholder or is omitted gracefully

  Scenario: Empty objective description is handled
    Given Team Objective "No Description" (ID=2099999) exists with status="Pending" effort=13 description=null
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then objective section includes Description header
    And description section is empty or omitted gracefully

  Scenario: Objective with long description is formatted properly
    Given Team Objective "Long Description" (ID=2088888) exists with status="Pending" effort=21 description="This is a very long description spanning multiple sentences and paragraphs that should be properly formatted in the markdown output without breaking the structure."
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then objective section includes Description header with full text
    And description text is readable and well-formatted in markdown

  Scenario: Status field values are preserved
    Given Team Objective "Various Status" (ID=2077777) exists with status="In Progress" effort=13
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then objective status field shows "In Progress"
    And status field value matches exact TargetProcess value

  Scenario: Objective effort can be zero or negative values
    Given Team Objective "Unknown Effort" (ID=2066666) exists with status="Pending" effort=0
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then objective effort field shows "0"
    And zero/invalid effort values are preserved correctly

  Scenario: Markdown output is valid GitHub-flavored Markdown
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then markdown output is valid GFM syntax
    And all headers are properly formatted with # notation
    And YAML frontmatter is properly delimited with ---
    And no invalid markdown syntax errors

  Scenario: Markdown can be parsed back to extract metadata
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then markdown content can be parsed to extract:
      | field       |
      | release     |
      | team        |
      | art         |
      | exported_at |
      | objectives  |
    And objective IDs can be extracted from markdown
    And epic names can be extracted from markdown sections

  Scenario: Exported markdown round-trips through git
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then markdown can be committed to git
    And markdown can be pushed to remote
    And markdown preserves all metadata through git operations
    And subsequent pull reflects same metadata

  Scenario: Different teams generate different markdown files
    Given Team "Cloud Enablement" exists in ART "Data, Analytics and Digital"
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    And markdown generator exports objectives for team="Cloud Enablement" release="PI-4/25"
    Then two markdown files are generated
    And each file contains only the respective team's objectives
    And metadata (team, art) matches the export context

  Scenario: Different releases generate separate markdown files
    Given Release "PI-5/25" exists for the ART
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    And markdown generator exports objectives for team="Platform Eco" release="PI-5/25"
    Then two markdown files are generated
    And PI-4/25 markdown contains only PI-4/25 objectives
    And PI-5/25 markdown contains only PI-5/25 objectives
    And release field in frontmatter matches export context

  Scenario: Markdown filename reflects team and release
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then generated markdown filename follows pattern
    And filename includes team name "Platform Eco" or normalized version
    And filename includes release "PI-4/25" or normalized version
    And filename has .md extension

  Scenario: Special characters in team/release names are handled
    Given Team "Team (Special-Chars)" exists
    And Release "PI-4/25 (Q2 Planning)" exists for the ART
    When markdown generator exports objectives for team="Team (Special-Chars)" release="PI-4/25 (Q2 Planning)"
    Then markdown filename is valid for filesystem
    And frontmatter preserves exact team and release names
    And no filename encoding issues

  Scenario: Unicode characters in objective names are preserved
    Given Team Objective "🚀 Performance Initiative" (ID=2055555) exists with status="Pending" effort=21
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then markdown includes emoji in objective title
    And unicode characters are preserved correctly
    And markdown renders emoji properly

  Scenario: HTML-like syntax in descriptions is escaped
    Given Team Objective "With HTML" (ID=2044444) exists with description="This has <script> and & special chars"
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then description text is properly escaped
    And no markdown injection vulnerabilities
    And special characters rendered literally

