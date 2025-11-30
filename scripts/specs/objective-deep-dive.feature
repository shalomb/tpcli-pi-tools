# Feature: Objective Deep Dive
# A Lead/Principal Engineer needs to understand individual PI objectives in depth,
# including linked features, dependencies, risks, and Jira correlation.
#
# File: scripts/specs/objective-deep-dive.feature
# Related: scripts/user-stories/us-003-objective-deep-dive.md

Feature: Drill into Objective Details and Dependencies
  As a Lead/Principal Engineer
  I want to drill into a specific PI objective to see all its details and relationships
  So that I can understand dependencies, risks, and linked work across TargetProcess and Jira

  Background:
    Given I am authenticated to TargetProcess
    And I know the objective ID or name
    And I have access to scripts/

  Scenario: View objective core information
    When I run: ./scripts/objective-deep-dive.sh --objective 2029314
    Then I should see objective details:
      | Attribute           | Example                          |
      | Objective name      | Enable Data Transfer using MSK   |
      | Objective type      | TeamPIObjective or ProgramPI... |
      | Objective ID        | 2029314                          |
      | Status              | Pending, Accepted, In Progress   |
      | Owner               | Shalom Bhooshi                   |
      | Description         | (Full text if available)         |
      | Release             | PI-4/25                          |
      | Team (if team obj)  | Cloud Enablement & Delivery      |
      | Start date          | Jan 2, 2025                      |
      | End date            | Jan 13, 2025                     |
      | Created by          | Shalom Israel Bhooshi            |
      | Created on          | Oct 28, 2025                     |

  Scenario: View objective's description/context
    When I run: ./scripts/objective-deep-dive.sh --objective 2029314 --show description
    Then I should see the full objective description
    And if description is structured (YAML/JSON), it should be parsed
    And key fields should be highlighted (e.g., "decision_owner", "action_items")

  Scenario: View linked features and user stories
    When I run: ./scripts/objective-deep-dive.sh --objective 2029314 --show features
    Then I should see linked work items:
      | Attribute     | Example                    |
      | Feature name  | S3-to-S3 replication POC   |
      | Feature ID    | 1234567                    |
      | Feature status| Backlog, In Progress, Done |
      | Effort        | 21 points                  |
      | Owner         | Team name                  |
      | Parent epic   | If applicable              |

  Scenario: View cross-objective dependencies
    When I run: ./scripts/objective-deep-dive.sh --objective 2029314 --show dependencies
    Then I should see identified dependencies:
      | Dependency Type    | Example                                    |
      | Blocks             | "Waiting for infrastructure from Team X"  |
      | Blocked by         | "Depends on Team Y's MSK setup"           |
      | Related objectives | "ECS1-13937 (original story)"             |
      | External deps      | "AWS Transfer Family approval needed"     |

  Scenario: View risk assessment and mitigation
    When I run: ./scripts/objective-deep-dive.sh --objective 2029314 --show risks
    Then I should see risk analysis:
      | Risk Category      | Example                                  |
      | Technical risks    | "GxP compliance needed, AWS TF not app" |
      | Schedule risks     | "4TB transfer may take longer than PI"  |
      | Resource risks     | "Need AWS/GxP expertise"                |
      | Dependency risks   | "External vendor account access"        |
      | Capacity risks     | "Effort estimate not provided yet"      |
      | Mitigations        | Action items to address risks           |

  Scenario: View Jira correlation
    When I run: ./scripts/objective-deep-dive.sh --objective 2029314 --show jira
    Then I should see Jira integration:
      | Aspect                | Example              |
      | Matching Jira epic    | DAD-2527             |
      | Epic status           | Funnel (In Progress) |
      | Linked issues in epic | DAD-2527, DAD-2528.. |
      | External issue IDs    | If custom field      |
      | Suggested epic name   | If not yet linked    |

  Scenario: View stakeholder information
    When I run: ./scripts/objective-deep-dive.sh --objective 2029314 --show stakeholders
    Then I should see stakeholder details:
      | Role             | Example                     |
      | Owner            | Shalom Bhooshi              |
      | Team             | Cloud Enablement & Delivery |
      | Sponsor/Requester| Saso Jezernik               |
      | Collaborators    | List of people              |
      | Watchers         | Who's tracking this         |

  Scenario: View decision history and comments
    When I run: ./scripts/objective-deep-dive.sh --objective 2029314 --show history
    Then I should see:
      | Content         | Example                              |
      | Status changes  | When it moved to Pending/Accepted   |
      | Key decisions   | "Chose S3-S3 over SFTP on Nov 20"  |
      | Comments        | Discussion/notes from stakeholders  |
      | Last update     | "2 days ago"                        |

  Scenario: Export objective with all context
    When I run: ./scripts/objective-deep-dive.sh --objective 2029314 --format markdown
    Then I should get a markdown report with:
      - Full objective details
      - Linked features
      - Dependencies
      - Risks and mitigations
      - Stakeholders
      - Jira correlation
      - Ready to share or include in documents

    When I run: ./scripts/objective-deep-dive.sh --objective 2029314 --format json
    Then I should get structured JSON for programmatic use

  Scenario: Quick health check on objective
    When I run: ./scripts/objective-deep-dive.sh --objective 2029314
    Then I should see a status indicator:
      """
      ✅ OBJECTIVE STATUS:
      Status: Pending (not yet committed)
      Effort: Not estimated
      Features: None linked yet
      Risks: 3 identified (GxP, AWS TF, expertise)
      Recommendation: Get effort estimate, consider timeline for SFTP/S3 decision
      """

  Scenario: Handle objective not found
    When I run: ./scripts/objective-deep-dive.sh --objective 9999999
    Then I should see:
      """
      Error: Objective 9999999 not found
      Available objectives in PI-4/25:
        - 2029314: Enable Data Transfer using MSK
        - 2023681: MDM implementation
        - [... more objectives]
      """

  Scenario: Compare with related objectives
    When I run: ./scripts/objective-deep-dive.sh --objective 2029314 --compare-with 2023681
    Then I should see comparison:
      | Attribute    | Obj 2029314                | Obj 2023681            |
      | Team         | Cloud Enablement & Delivery| DG & MDM POD           |
      | Release      | PI-4/25                   | PI-4/25                |
      | Status       | Pending                   | Pending                |
      | Effort       | TBD                       | TBD                    |
      | Dependencies| 2 identified               | 1 identified           |
      | Risks       | 3                          | 1                      |
