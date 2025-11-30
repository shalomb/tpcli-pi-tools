# Feature: Team Deep Dive
# A Lead/Principal Engineer needs to drill down into a specific team to understand
# their commitments, capacity, risks, and dependencies.
#
# File: scripts/specs/team-deep-dive.feature
# Related: scripts/user-stories/us-002-team-deep-dive.md

Feature: Drill into Team Details for PI
  As a Lead/Principal Engineer
  I want to drill into a team's PI objectives, features, and risks
  So that I can understand their capacity, commitments, and potential blockers

  Background:
    Given I am authenticated to TargetProcess
    And I know the team name or ID
    And I have access to scripts/

  Scenario: View team profile and capacity
    When I run: ./scripts/team-deep-dive.sh --team "Example Team"
    Then I should see team information:
      | Attribute        | Example                   |
      | Team name        | Example Team |
      | Team ID          | 2022903                   |
      | ART              | Data, Analytics and Digital |
      | Owner            | Shalom Bhooshi            |
      | Member count     | 2 people                  |
      | Status           | Active                    |

  Scenario: View team's PI objectives for current/upcoming PI
    When I run: ./scripts/team-deep-dive.sh --team "Example Team" --pi current
    Then I should see team PI objectives:
      | Attribute       | Example                         |
      | Objective name  | Enable Data Transfer using MSK  |
      | Release         | PI-3/25                         |
      | Status          | Pending, Accepted, In Progress  |
      | Committed       | Yes/No                          |
      | Effort          | 0 points (if estimated)         |
      | Start date      | Jan 2, 2025                     |
      | End date        | Jan 13, 2025                    |

  Scenario: View features linked to team objectives
    When I run: ./scripts/team-deep-dive.sh --team "Example Team" --show features
    Then I should see for each objective:
      | Linked Features |
      | Feature name    |
      | Feature status  |
      | Feature effort  |
      | Feature owner   |

  Scenario: View team's capacity and workload
    When I run: ./scripts/team-deep-dive.sh --team "Example Team" --show capacity
    Then I should see capacity information:
      | Metric              | Example        |
      | Team size           | 2 people       |
      | Total committed effort | 81 points   |
      | Effort per person   | 40.5 points    |
      | Effort by objective | Breakdown list |
      | Risk: overcommitted | ⚠️ Yes/No      |

  Scenario: View team's risks and blockers
    When I run: ./scripts/team-deep-dive.sh --team "Example Team" --show risks
    Then I should see identified risks:
      | Risk Category   | Example                                    |
      | Dependencies    | "Waiting on Team X for infrastructure"    |
      | Skills gap      | "Need Kubernetes expertise"                |
      | Resource risk   | "Key person on vacation Jan 5-12"        |
      | Overcommitment  | "63 points / 2 people = 31.5 pts/person" |
      | Unknown risks   | "Flag: Description empty on 3 objectives" |

  Scenario: View team's previous/historical PI performance
    When I run: ./scripts/team-deep-dive.sh --team "Example Team" --show history
    Then I should see last N PIs with:
      | Metric               | Example    |
      | Release name         | PI-2/25    |
      | Committed objectives | 2          |
      | Completed objectives | 1          |
      | Completion rate      | 50%        |
      | Average effort/obj   | 20 points  |

  Scenario: Link to related Jira epics
    When I run: ./scripts/team-deep-dive.sh --team "Example Team" --show jira-links
    Then I should see for each objective:
      | Jira Integration         |
      | Matching Jira epics      |
      | Epic status (if linked)  |
      | External issue keys      |

  Scenario: Export team details
    When I run: ./scripts/team-deep-dive.sh --team "Example Team" --format json
    Then I should get JSON output with all team data

    When I run: ./scripts/team-deep-dive.sh --team "Example Team" --format markdown
    Then I should get a markdown report suitable for sharing

  Scenario: Show context for decision making
    When I run: ./scripts/team-deep-dive.sh --team "Example Team"
    Then I should see a summary section:
      """
      EXECUTIVE SUMMARY:
      - Team capacity: 2 people
      - PI commitments: 1 objective
      - Committed effort: TBD (not estimated yet)
      - Status: Objectives pending commitment
      - Key blockers: None identified
      - Recommendations: Get effort estimates, consider capacity vs. demand
      """

  Scenario: Handle team not found
    When I run: ./scripts/team-deep-dive.sh --team "Nonexistent Team"
    Then I should see:
      """
      Error: Team 'Nonexistent Team' not found
      Available teams:
        - Example Team
        - Team Superman (DQH)
        - PIC - Thanos
        - [... more teams]
      """

  Scenario: Drill down from team to objective details
    When I run: ./scripts/team-deep-dive.sh --team "Example Team"
    And I see objective "Enable Data Transfer using MSK (ID: 2029314)"
    And I run: ./scripts/objective-deep-dive.sh --objective 2029314
    Then I should see full objective details with dependencies, risks, linked features
