Feature: Python API Client Wrapper Methods

  Background:
    Given TargetProcess API is available
    And test team ID is 1935991
    And test release ID is 1942235
    And test objective ID is 12345
    And test feature ID is 5678

  Scenario: Create team objective via Python client
    When Python code calls: client.create_team_objective("API Performance", team_id=1935991, release_id=1942235, effort=34)
    Then subprocess "tpcli plan create TeamPIObjective --data ..." is called
    And JSON response is parsed
    And TeamPIObjective object is returned with id=12345
    And returned objective has name="API Performance"
    And returned objective has effort=34
    And object is added to cache

  Scenario: Update team objective via Python client
    Given TeamPIObjective 12345 exists in cache with name="API Perf"
    When Python code calls: client.update_team_objective(12345, name="API Performance", effort=40)
    Then subprocess "tpcli plan update TeamPIObjective 12345 --data ..." is called
    And JSON response is parsed
    And updated TeamPIObjective object is returned
    And returned objective has name="API Performance"
    And returned objective has effort=40
    And cache is updated with new objective

  Scenario: Create feature via Python client
    When Python code calls: client.create_feature("User Authentication", parent_epic_id=2018883, effort=21)
    Then subprocess "tpcli plan create Feature --data ..." is called
    And JSON response is parsed
    And Feature object is returned with id=5678
    And returned feature has name="User Authentication"
    And returned feature has effort=21
    And object is added to cache

  Scenario: Update feature via Python client
    Given Feature 5678 exists in cache with name="User Auth"
    When Python code calls: client.update_feature(5678, name="User Authentication", effort=13)
    Then subprocess "tpcli plan update Feature 5678 --data ..." is called
    And updated Feature object is returned
    And returned feature has name="User Authentication"
    And returned feature has effort=13
    And cache is updated with new feature

  Scenario: Create fails with invalid JSON response from subprocess
    Given subprocess will return invalid JSON
    When Python code calls: client.create_team_objective("Test", team_id=1935991, release_id=1942235)
    Then TPAPIError is raised
    And error message contains "Failed to parse"

  Scenario: Create fails with subprocess error
    Given subprocess will fail with exit code 1
    And subprocess error is "entity validation failed"
    When Python code calls: client.create_team_objective("Invalid", team_id=1935991, release_id=1942235)
    Then TPAPIError is raised
    And error message contains "tpcli command failed"

  Scenario: Update fails when objective not found
    Given subprocess returns 404 error
    When Python code calls: client.update_team_objective(99999, name="Not Found")
    Then TPAPIError is raised
    And error message contains "not found" or "404"

  Scenario: Create objective returns fully populated typed object
    When Python code calls: client.create_team_objective("Test", team_id=1935991, release_id=1942235)
    Then returned object is instance of TeamPIObjective
    And returned object has all required fields:
      | field           | required |
      | id              | true     |
      | name            | true     |
      | team_id         | true     |
      | release_id      | true     |
      | status          | false    |
      | effort          | false    |
      | created_date    | false    |

  Scenario: Create preserves optional fields if provided
    When Python code calls: client.create_team_objective("Obj", team_id=1935991, release_id=1942235, effort=34, description="Test desc")
    Then returned objective has effort=34
    And returned objective has description="Test desc"

  Scenario: Update preserves unchanged fields
    Given cached objective with name="API Perf" and effort=34 and status="Pending"
    When Python code calls: client.update_team_objective(12345, effort=40)
    Then returned objective has name="API Perf" (preserved)
    And returned objective has effort=40 (updated)
    And returned objective has status="Pending" (preserved)

  Scenario: Cache is invalidated on update
    Given objective 12345 is in cache
    And another process might have updated objective 12345 in TP
    When Python code calls: client.update_team_objective(12345, name="Updated")
    Then cache is updated with latest from API
    And subsequent get_team_pi_objectives() returns updated objective

  Scenario: Multiple creates use correct endpoints
    When Python code calls: client.create_team_objective("Obj1", team_id=1935991, release_id=1942235)
    And Python code calls: client.create_feature("Feature1", parent_epic_id=2018883)
    Then first call used "tpcli plan create TeamPIObjective"
    And second call used "tpcli plan create Feature"

  Scenario: Create with minimal required fields only
    When Python code calls: client.create_team_objective(name="Test", team_id=1935991, release_id=1942235)
    Then subprocess receives JSON with only required fields
    And subprocess does not receive optional fields like description, effort

  Scenario: Update with single field works
    When Python code calls: client.update_team_objective(12345, effort=50)
    Then subprocess receives JSON with only effort field
    And other fields are not included in update payload
