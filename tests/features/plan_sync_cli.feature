Feature: Plan Sync Workflow via CLI

  Background:
    Given git repository is initialized
    And TargetProcess API is running
    And local team="Platform Eco" with release="PI-4/25"

  Scenario: Initialize plan tracking with init subcommand
    When user runs: tpcli plan init --release PI-4/25 --team "Platform Eco"
    Then command succeeds with exit code 0
    And output contains "Initialized plan tracking"
    And tracking branch "TP-PI-4-25-platform-eco" is created
    And feature branch "feature/plan-pi-4-25" is created
    And markdown file is committed to tracking branch

  Scenario: Init fails without required flags
    When user runs: tpcli plan init --release PI-4/25
    Then command fails with exit code 1
    And error message contains "required" or "team"

  Scenario: Init fails without release flag
    When user runs: tpcli plan init --team "Platform Eco"
    Then command fails with exit code 1
    And error message contains "required" or "release"

  Scenario: Pull latest changes from TargetProcess
    Given user has initialized plan tracking for PI-4/25
    When TargetProcess has updated objective 2019099 effort to 40
    And user runs: tpcli plan pull
    Then command succeeds with exit code 0
    And output contains "Successfully pulled"
    And markdown file reflects the updated effort=40
    And tracking branch is updated with latest TP state

  Scenario: Pull with no changes returns success
    Given user has initialized plan tracking for PI-4/25
    When user runs: tpcli plan pull
    Then command succeeds with exit code 0
    And output contains "No changes" or "Successfully pulled"

  Scenario: Pull detects rebase conflicts
    Given user has initialized plan tracking for PI-4/25
    And user has local commit updating objective 2019099 effort to 40
    And TargetProcess has updated objective 2019099 effort to 30
    When user runs: tpcli plan pull
    Then command fails with exit code 1
    And output contains "conflict" or "rebase"
    And error message contains instructions for conflict resolution

  Scenario: Push changes to TargetProcess
    Given user has initialized plan tracking for PI-4/25
    And user has edited and committed objective 2019099 effort 21→34
    When user runs: tpcli plan push
    Then command succeeds with exit code 0
    And output contains "Successfully pushed" or "changes"
    And TP API is called to update objective 2019099 with effort=34
    And tracking branch is updated

  Scenario: Push with no changes returns success
    Given user has initialized plan tracking for PI-4/25
    When user runs: tpcli plan push
    Then command succeeds with exit code 0
    And output contains "No changes" or "Successfully pushed"

  Scenario: Push fails with validation error
    Given user has initialized plan tracking for PI-4/25
    And user has edited markdown with missing required field
    When user runs: tpcli plan push
    Then command fails with exit code 1
    And error message contains "validation" or "required field"

  Scenario: Init creates with correct branch naming
    When user runs: tpcli plan init --release "PI-5/25" --team "Cloud Enablement"
    Then command succeeds with exit code 0
    And tracking branch "TP-PI-5-25-cloud-enablement" is created
    And feature branch "feature/plan-pi-5-25" is created
