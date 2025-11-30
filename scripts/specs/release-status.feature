# Feature: Release/PI Status Report
# A Lead/Principal Engineer needs to track the status of a program increment,
# including progress, blockers, at-risk items, and cross-team dependencies.
#
# File: scripts/specs/release-status.feature
# Related: scripts/user-stories/us-004-release-status.md

Feature: View Release/PI Status and Progress
  As a Lead/Principal Engineer
  I want to see the status of a program increment including progress, risks, and blockers
  So that I can manage the PI and identify issues early

  Background:
    Given I am authenticated to TargetProcess
    And I know the release name or ID
    And I have access to scripts/

  Scenario: View release information and timeline
    When I run: ./scripts/release-status.sh --release "PI-4/25"
    Then I should see release details:
      | Attribute       | Example                     |
      | Release name    | PI-4/25                     |
      | Release ID      | 1942235                     |
      | ART             | Data, Analytics and Digital |
      | Status          | Current, Upcoming, Past     |
      | Start date      | Jan 2, 2025                 |
      | End date        | Jan 13, 2025                |
      | Duration        | 12 days / 2 weeks           |
      | Days remaining  | 5 days (if in progress)     |

  Scenario: View all teams and their objectives in the PI
    When I run: ./scripts/release-status.sh --release "PI-4/25" --show teams
    Then I should see team summary:
      | Team Name               | Obj Count | Status    | Committed | Effort |
      | Cloud Enablement & Del. | 1         | Pending   | No        | TBD    |
      | Team Superman (DQH)     | 3         | Pending   | No        | TBD    |
      | PIC - Thanos            | 4         | Pending   | No        | TBD    |
      | DG & MDM POD            | 5         | Pending   | No        | TBD    |
      | [... 23 more teams]     | 27 total  | -         | -         | -      |

  Scenario: View program objectives status
    When I run: ./scripts/release-status.sh --release "PI-4/25" --show program-objectives
    Then I should see program objective summary:
      | Attribute      | Example                |
      | Objective name | "Objective 1"          |
      | Status         | Draft, Accepted, Done  |
      | Completion     | % complete (if tracked)|
      | Risks          | Count of identified    |
      | Dependencies   | Count of cross-team    |

  Scenario: View PI progress and completion
    When I run: ./scripts/release-status.sh --release "PI-3/25"
    Then I should see progress metrics:
      | Metric                    | Example              |
      | Total objectives          | 47                   |
      | Objectives completed      | 8 (17%)              |
      | Objectives in progress    | 15 (32%)             |
      | Objectives pending        | 24 (51%)             |
      | At-risk objectives        | 3                    |
      | Total effort estimated    | 426 points           |
      | Effort completed          | 89 points (21%)      |
      | Velocity trend            | Up/Stable/Down       |

  Scenario: Identify blockers and at-risk items
    When I run: ./scripts/release-status.sh --release "PI-4/25" --show risks
    Then I should see risk summary:
      | Risk Category          | Example                               |
      | At-risk objectives     | 3 (effort estimates missing, etc)    |
      | Cross-team blockers    | "Team A waiting on Team B for X"     |
      | Dependency risks       | "External approval still pending"    |
      | Resource constraints   | "2 teams at max capacity"            |
      | Technical risks        | "GxP compliance impacts 4 objectives" |
      | Schedule risks         | "5-day holidays overlap with PI"    |

  Scenario: View inter-team dependencies
    When I run: ./scripts/release-status.sh --release "PI-4/25" --show dependencies
    Then I should see dependency graph:
      | From Team    | To Team              | Type        | Objective            |
      | Team A       | Team B               | Blocks      | "Setup infrastructure"|
      | Team C       | Team D               | Depends on  | "API contract"       |
      | Team E       | External (AWS)       | Approval    | "GxP clearance"      |

  Scenario: Comparison with previous PI
    When I run: ./scripts/release-status.sh --release "PI-4/25" --compare-with "PI-3/25"
    Then I should see comparison:
      | Metric                | PI-3/25 | PI-4/25 | Change    |
      | Number of teams       | 28      | 27      | -1        |
      | Number of objectives  | 48      | 47      | -1        |
      | Total effort (est)    | 426     | TBD     | -         |
      | Avg effort/objective  | 8.9     | TBD     | -         |
      | Completion % (midway) | 21%     | -       | -         |

  Scenario: Extract key metrics for reporting
    When I run: ./scripts/release-status.sh --release "PI-4/25" --format summary
    Then I should see executive summary:
      """
      PI-4/25 Status Summary
      =====================
      ART: Data, Analytics and Digital
      Timeline: Jan 2-13, 2025 (12 days)

      Participation:
      - 27 teams committed
      - 47 objectives (1 program, 46 team)

      Status:
      - Pending: 45 objectives (96%)
      - Accepted: 2 objectives (4%)
      - Not yet committed

      Effort:
      - Estimated: 0 / TBD (0 objectives estimated)
      - Average per team: TBD
      - Recommendation: Get effort estimates before mid-PI

      Risks:
      - 3 at-risk items identified
      - 2 cross-team blockers
      - 4 teams need capacity review
      - Action required: Clarify GxP/AWS Transfer Family constraints
      """

  Scenario: Export release status
    When I run: ./scripts/release-status.sh --release "PI-4/25" --format json
    Then I should get comprehensive JSON with all metrics

    When I run: ./scripts/release-status.sh --release "PI-4/25" --format html
    Then I should get a viewable HTML report for sharing/archiving

  Scenario: Drill down from release to team/objective
    When I run: ./scripts/release-status.sh --release "PI-4/25"
    And I see team "Cloud Enablement & Delivery"
    And I run: ./scripts/team-deep-dive.sh --team "Cloud Enablement & Delivery" --pi "PI-4/25"
    Then I should see detailed team information for that PI

  Scenario: Handle release not found
    When I run: ./scripts/release-status.sh --release "PI-99/99"
    Then I should see:
      """
      Error: Release 'PI-99/99' not found
      Available releases in Data, Analytics and Digital ART:
        - PI-4/25 (upcoming)
        - PI-3/25 (current)
        - PI-2/25 (past)
        - [... more releases]
      """
