# Feature: ART Dashboard
# A Lead/Principal Engineer on an ART needs a high-level view of current and upcoming
# program increments, including releases, teams, objectives, and overall health.
#
# File: scripts/specs/art-dashboard.feature
# Related: scripts/user-stories/us-001-art-dashboard.md

Feature: View ART Dashboard for PI Planning
  As a Lead/Principal Engineer on an ART
  I want to see a dashboard of all my releases, teams, and objectives
  So that I can understand the overall state of my program at a glance

  Background:
    Given I am authenticated to TargetProcess
    And I know my ART name or ID
    And I have access to scripts/

  Scenario: View current and upcoming releases
    When I run: ./scripts/art-dashboard.sh --art "Data, Analytics and Digital"
    Then I should see:
      | Section          | Content                              |
      | Current Release  | PI-3/25 with status and dates       |
      | Next Release     | PI-4/25 with status and dates       |
      | Release Timeline | All upcoming releases in order       |
    And I should see each release's:
      | Attribute         | Example                   |
      | Name              | PI-4/25                   |
      | Start date        | Jan 2, 2025               |
      | End date          | Jan 13, 2025              |
      | ART               | Data, Analytics and Digital|
      | Is Current        | [CURRENT] badge if true   |

  Scenario: View team participation in the ART
    When I run: ./scripts/art-dashboard.sh --art "Data, Analytics and Digital"
    Then I should see a "Teams" section listing all teams with:
      | Attribute    | Example                      |
      | Team name    | Example Team  |
      | Team ID      | 2022903                      |
      | Objective count | 2 (number of PI objectives) |
      | Status       | Number of objectives by status |

  Scenario: View program objectives summary
    When I run: ./scripts/art-dashboard.sh --art "Data, Analytics and Digital"
    Then I should see a "Program PI Objectives" section with:
      | Attribute      | Example                                |
      | Objective name | "Objective 1"                          |
      | Status         | Draft, Accepted, In Progress, Done     |
      | Release        | PI-4/25                                |
    And the objectives should be grouped by release
    And I should see count of objectives by status

  Scenario: Quick health check indicators
    When I run: ./scripts/art-dashboard.sh --art "Data, Analytics and Digital"
    Then I should see high-level metrics:
      | Metric              | Example       |
      | Total Teams         | 27            |
      | Total Objectives    | 47            |
      | Objectives Pending  | 45            |
      | Objectives Accepted | 2             |
      | At-Risk Objectives  | Mark if found |

  Scenario: Filter to current or upcoming PI
    When I run: ./scripts/art-dashboard.sh --art "Data, Analytics and Digital" --pi current
    Then I should only see information about PI-3/25 (the current PI)

    When I run: ./scripts/art-dashboard.sh --art "Data, Analytics and Digital" --pi upcoming
    Then I should only see information about PI-4/25 (the next PI)

  Scenario: Output in different formats
    When I run: ./scripts/art-dashboard.sh --art "Data, Analytics and Digital" --format json
    Then I should receive structured JSON output
    And I should be able to pipe to jq for further processing

    When I run: ./scripts/art-dashboard.sh --art "Data, Analytics and Digital" --format csv
    Then I should receive CSV-formatted output
    And I should be able to import into Excel/Sheets

  Scenario: Handle ART not found
    When I run: ./scripts/art-dashboard.sh --art "Nonexistent ART"
    Then I should see an error message:
      """
      Error: ART 'Nonexistent ART' not found
      Available ARTs: [list of actual ARTs]
      """

  Scenario: Provide help and examples
    When I run: ./scripts/art-dashboard.sh --help
    Then I should see:
      | Content                                  |
      | Usage information                        |
      | Description of what dashboard shows      |
      | Example commands                         |
      | Available options/flags                  |
      | Link to documentation                    |
