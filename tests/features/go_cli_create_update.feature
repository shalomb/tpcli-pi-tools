Feature: Create and Update TargetProcess Entities via CLI

  Scenario: Create TeamPIObjective with valid data
    When user runs: tpcli create TeamPIObjective --data '{"name":"API Perf","team_id":1935991,"release_id":1942235,"effort":34}'
    Then command succeeds with exit code 0
    And output contains JSON with "id" field
    And returned entity has all provided fields

  Scenario: Update TeamPIObjective with valid data
    Given TeamPIObjective 12345 exists in TP
    When user runs: tpcli update TeamPIObjective 12345 --data '{"name":"New Name","effort":40}'
    Then command succeeds with exit code 0
    And output contains updated JSON
    And TP API was called with PUT to /api/v1/TeamPIObjective/12345

  Scenario: Create Feature with valid data
    When user runs: tpcli create Feature --data '{"name":"User Auth","parent_id":2018883,"effort":21}'
    Then command succeeds with exit code 0
    And output contains JSON with "id" field
    And returned entity has all provided fields

  Scenario: Update Feature with valid data
    Given Feature 5678 exists in TP
    When user runs: tpcli update Feature 5678 --data '{"name":"Auth Flow","effort":13}'
    Then command succeeds with exit code 0
    And output contains updated JSON

  Scenario: Create fails with invalid JSON
    When user runs: tpcli create Feature --data 'invalid-json'
    Then command fails with exit code 1
    And error message contains "invalid JSON"

  Scenario: Create fails with missing required fields
    When user runs: tpcli create TeamPIObjective --data '{"team_id":1935991}'
    Then command fails with exit code 1
    And error message contains "required field" or "name"

  Scenario: Update fails with entity not found
    When user runs: tpcli update TeamPIObjective 99999 --data '{"name":"x"}'
    Then command fails with exit code 1
    And error message contains "not found" or "404"

  Scenario: Update fails with invalid ID format
    When user runs: tpcli update TeamPIObjective invalid-id --data '{"name":"x"}'
    Then command fails with exit code 1
    And error message contains "invalid" or "ID"

  Scenario: Create returns complete entity with ID and timestamps
    When user runs: tpcli create TeamPIObjective --data '{"name":"API Perf","team_id":1935991,"release_id":1942235}'
    Then command succeeds with exit code 0
    And output JSON includes:
      | field             | present |
      | id                | true    |
      | name              | true    |
      | team_id           | true    |
      | release_id        | true    |
      | create_date       | true    |
      | modify_date       | true    |

  Scenario: Update preserves unchanged fields
    Given TeamPIObjective 12345 exists with name="API Perf" and effort=34
    When user runs: tpcli update TeamPIObjective 12345 --data '{"effort":40}'
    Then command succeeds with exit code 0
    And returned entity still has name="API Perf"
    And returned entity has effort=40
