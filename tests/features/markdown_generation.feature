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

  # Phase 2A: Jira Integration Tests

  Scenario: US-PA-1 - Jira epic key displays as clickable link
    Given Feature "Semantic Versioning & CI/CD" (ID=2018883) linked to objective 2019099 with effort=21 owner="Venkatesh Ravi"
    And Feature has Jira Key "DAD-2652"
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then markdown includes Jira link section
    And Jira link displays key "DAD-2652"
    And Jira link is formatted as markdown link
    And Jira link URL points to "https://jira.takeda.com/browse/DAD-2652"

  Scenario: US-PA-2 - Acceptance criteria from TP rendered as list
    Given Feature "Semantic Versioning & CI/CD" (ID=2018883) linked to objective 2019099
    And Feature has acceptance criteria:
      | CPU and memory limits configured at pod level |
      | Alerting implemented for backend pods |
      | Semantic versioning for Docker images |
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then markdown includes acceptance criteria section
    And acceptance criteria rendered as bullet list
    And acceptance criteria items:
      | CPU and memory limits configured at pod level |
      | Alerting implemented for backend pods |
      | Semantic versioning for Docker images |

  Scenario: US-PA-2 - HTML entities in acceptance criteria are decoded
    Given Feature "API Enhancement" (ID=2018885) linked to objective 2019099
    And Feature has acceptance criteria with HTML entities: "Item 1&#44; Item 2&nbsp;and&nbsp;Item 3"
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then acceptance criteria HTML entities are decoded
    And acceptance criteria does not contain "&#44;"
    And acceptance criteria does not contain "&nbsp;"

  Scenario: US-PA-2 - HTML tags in acceptance criteria are stripped
    Given Feature "Security Module" (ID=2018886) linked to objective 2019099
    And Feature has acceptance criteria with HTML: "<p>Requirement 1</p><p>Requirement 2</p>"
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then HTML tags are removed from acceptance criteria
    And acceptance criteria does not contain "<p>"
    And acceptance criteria does not contain "</p>"
    But acceptance criteria text preserved

  Scenario: US-PA-3 - Note directs users to Jira for story decomposition
    Given Feature "Semantic Versioning & CI/CD" (ID=2018883) linked to objective 2019099 with effort=21 owner="Venkatesh Ravi"
    And Feature has Jira Key "DAD-2652"
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then markdown includes story decomposition reference
    And reference text contains "For detailed story decomposition"
    And reference mentions Jira key "DAD-2652"
    And reference is formatted as italic

  Scenario: US-PA-4 - Epic without Jira key renders cleanly
    Given Feature "Internal Process Improvement" (ID=2018884) linked to objective 2019099 with effort=13 owner="Jane Smith"
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then Feature "Internal Process Improvement" appears in markdown
    And feature metadata renders correctly
    But no Jira link section appears
    And no broken markdown links

  Scenario: US-PA-4 - Mixed epics with and without Jira keys
    Given Feature "Semantic Versioning & CI/CD" (ID=2018883) linked to objective 2019099 with effort=21 owner="Venkatesh Ravi"
    And Feature "Semantic Versioning & CI/CD" has Jira Key "DAD-2652"
    And Feature "Internal Process Improvement" (ID=2018884) linked to objective 2019099 with effort=13 owner="Jane Smith"
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then markdown includes Jira link for "DAD-2652"
    And markdown includes feature "Internal Process Improvement"
    And no broken links in markdown
    And no orphaned markdown link syntax

  Scenario: US-PA-4 - Acceptance criteria empty/missing handled gracefully
    Given Feature "Placeholder Epic" (ID=2018887) linked to objective 2019099
    And Feature has Jira Key "TEST-1"
    And Feature has no acceptance criteria
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then Feature section renders without error
    And Jira link displays correctly
    And no empty acceptance criteria section
    And markdown remains valid

  Scenario: US-PA-1 - Jira URL format is correct
    Given Feature "Multiple Formats Test" (ID=2018888) linked to objective 2019099
    And Feature has Jira Key "PROJ-999"
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then Jira URL is properly formatted
    And Jira URL format matches "https://jira.takeda.com/browse/PROJ-999"
    And URL includes correct Jira key

  Scenario: US-PA-1 - Various Jira key formats supported
    Given Feature "Format Test 1" (ID=2018889) linked to objective 2019099 with Jira Key "DAD-123"
    And Feature "Format Test 2" (ID=2018890) linked to objective 2019099 with Jira Key "PROJ-999"
    And Feature "Format Test 3" (ID=2018891) linked to objective 2019099 with Jira Key "X-1"
    When markdown generator exports objectives for team="Platform Eco" release="PI-4/25"
    Then all Jira keys render as clickable links
    And all URLs are properly formatted
    And no key format errors

  # Phase 2B: Direct Jira API Integration Tests

  Scenario: US-PB-1 - Stories fetched from Jira API
    Given Feature "Semantic Versioning & CI/CD" (ID=2018883) linked to objective 2019099 with Jira Key "DAD-2652"
    And Jira API is available with token "test-token"
    And Jira epic "DAD-2652" has stories:
      | DAD-2653 | Set up pod resource limits | In Progress | Alice Chen | 5 |
      | DAD-2654 | Implement alerting rules | To Do | Bob Kumar | 8 |
    When markdown generator exports objectives with Jira story fetching for team="Platform Eco" release="PI-4/25"
    Then stories appear in markdown as H4 subsections
    And story "DAD-2653" appears under epic "DAD-2652"
    And story "DAD-2654" appears under epic "DAD-2652"
    And stories are ordered by key

  Scenario: US-PB-1 - Story appears with key as clickable link
    Given Feature "Semantic Versioning & CI/CD" (ID=2018883) linked to objective 2019099 with Jira Key "DAD-2652"
    And Jira epic "DAD-2652" has story "DAD-2653" titled "Set up pod resource limits"
    When markdown generator exports objectives with Jira story fetching for team="Platform Eco" release="PI-4/25"
    Then story key "DAD-2653" displays as clickable link
    And story link URL is "https://jira.takeda.com/browse/DAD-2653"

  Scenario: US-PB-2 - Story acceptance criteria displayed
    Given Feature "Semantic Versioning & CI/CD" (ID=2018883) linked to objective 2019099 with Jira Key "DAD-2652"
    And Jira epic "DAD-2652" has story "DAD-2653" with description:
      | Configure memory and CPU limits |
      | Validate in staging environment |
      | Run performance tests |
    When markdown generator exports objectives with Jira story fetching for team="Platform Eco" release="PI-4/25"
    Then story "DAD-2653" has acceptance criteria section
    And acceptance criteria contains:
      | Configure memory and CPU limits |
      | Validate in staging environment |
      | Run performance tests |

  Scenario: US-PB-3 - Story status from Jira displayed
    Given Feature "Semantic Versioning & CI/CD" (ID=2018883) linked to objective 2019099 with Jira Key "DAD-2652"
    And Jira epic "DAD-2652" has story "DAD-2653" with status "In Progress"
    And Jira epic "DAD-2652" has story "DAD-2654" with status "To Do"
    When markdown generator exports objectives with Jira story fetching for team="Platform Eco" release="PI-4/25"
    Then story "DAD-2653" shows status "In Progress"
    And story "DAD-2654" shows status "To Do"

  Scenario: US-PB-3 - Story status is read-only in markdown
    Given Feature "Semantic Versioning & CI/CD" (ID=2018883) linked to objective 2019099 with Jira Key "DAD-2652"
    And Jira epic "DAD-2652" has story "DAD-2653" with status "In Progress"
    When markdown generator exports objectives with Jira story fetching for team="Platform Eco" release="PI-4/25"
    Then story status displayed as metadata field
    And story status not editable in markdown
    But user can manually change status and push to sync

  Scenario: US-PB-1 - Story metadata (assignee and points) displayed
    Given Feature "Semantic Versioning & CI/CD" (ID=2018883) linked to objective 2019099 with Jira Key "DAD-2652"
    And Jira epic "DAD-2652" has stories:
      | DAD-2653 | Set up pod resource limits | In Progress | Alice Chen | 5 |
      | DAD-2654 | Implement alerting rules | To Do | Bob Kumar | 8 |
    When markdown generator exports objectives with Jira story fetching for team="Platform Eco" release="PI-4/25"
    Then story "DAD-2653" shows assignee "Alice Chen"
    And story "DAD-2653" shows story points "5"
    And story "DAD-2654" shows assignee "Bob Kumar"
    And story "DAD-2654" shows story points "8"

  Scenario: US-PB-4 - Jira token from environment variable
    Given environment variable "JIRA_TOKEN" is set
    And environment variable "JIRA_URL" is set to "https://jira.takeda.com"
    And Feature has Jira Key "DAD-2652"
    When markdown generator exports objectives with Jira story fetching
    Then Jira API is authenticated
    And Jira token not logged in output

  Scenario: US-PB-4 - Missing Jira credentials handled gracefully
    Given environment variable "JIRA_TOKEN" is not set
    And Feature has Jira Key "DAD-2652"
    When markdown generator tries to export with Jira story fetching
    Then clear error message about missing JIRA_TOKEN
    And fallback to Phase 2A (show epic + Jira link, no stories)
    And markdown remains valid

  Scenario: US-PB-1 - Large number of stories handled efficiently
    Given Feature "Large Epic" (ID=2018892) linked to objective 2019099 with Jira Key "DAD-2700"
    And Jira epic "DAD-2700" has 100 stories
    When markdown generator exports objectives with Jira story fetching
    Then all 100 stories appear in markdown
    And markdown generation completes in reasonable time
    And markdown file size is reasonable

  Scenario: US-PB-1 - API timeout handled gracefully
    Given Feature "Timeout Test" (ID=2018893) linked to objective 2019099 with Jira Key "DAD-2750"
    And Jira API timeout is set to 5 seconds
    And Jira API takes longer than timeout
    When markdown generator exports objectives with Jira story fetching
    Then clear error message about API timeout
    And fallback to Phase 2A (show epic + Jira link, no stories)
    And markdown remains valid

  Scenario: US-PB-1 - Missing epic returns no stories gracefully
    Given Feature "Orphan Epic" (ID=2018894) linked to objective 2019099 with Jira Key "MISSING-999"
    And Jira epic "MISSING-999" does not exist
    When markdown generator exports objectives with Jira story fetching
    Then epic section renders without error
    And no stories appear for epic
    But epic metadata (Jira link) still displays

  Scenario: US-PB-3 - Various Jira status values supported
    Given Feature "Status Test Epic" (ID=2018895) linked to objective 2019099 with Jira Key "DAD-2800"
    And Jira epic "DAD-2800" has stories with various statuses:
      | DAD-2801 | Story 1 | To Do |
      | DAD-2802 | Story 2 | In Progress |
      | DAD-2803 | Story 3 | In Review |
      | DAD-2804 | Story 4 | Done |
      | DAD-2805 | Story 5 | Blocked |
    When markdown generator exports objectives with Jira story fetching
    Then all story statuses appear correctly in markdown
    And no status rendering errors

