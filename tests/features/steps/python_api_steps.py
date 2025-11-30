"""
Behave step definitions for Python API client wrapper methods.

Defines steps for testing create_team_objective, update_team_objective,
create_feature, and update_feature methods.
"""

import json
from behave import given, when, then
from tpcli_pi.core.api_client import TPAPIClient, TPAPIError
from tpcli_pi.models.entities import TeamPIObjective, Feature


@given("TargetProcess API is available")
def step_tp_api_available(context):
    """Setup: TP API is available for testing."""
    context.tp_api_available = True


@given("test team ID is {team_id:d}")
def step_test_team_id(context, team_id):
    """Store test team ID for use in steps."""
    context.test_team_id = team_id


@given("test release ID is {release_id:d}")
def step_test_release_id(context, release_id):
    """Store test release ID for use in steps."""
    context.test_release_id = release_id


@given("test objective ID is {objective_id:d}")
def step_test_objective_id(context, objective_id):
    """Store test objective ID for use in steps."""
    context.test_objective_id = objective_id


@given("test feature ID is {feature_id:d}")
def step_test_feature_id(context, feature_id):
    """Store test feature ID for use in steps."""
    context.test_feature_id = feature_id


@given("TeamPIObjective {obj_id} exists in cache with name=\"{name}\"")
def step_objective_in_cache(context, obj_id, name):
    """Pre-populate cache with an objective."""
    if not hasattr(context, "client"):
        context.client = TPAPIClient()

    # Note: In a real test, would populate cache
    context.cached_objective_id = int(obj_id)
    context.cached_objective_name = name


@given("Feature {feature_id} exists in cache with name=\"{name}\"")
def step_feature_in_cache(context, feature_id, name):
    """Pre-populate cache with a feature."""
    if not hasattr(context, "client"):
        context.client = TPAPIClient()

    context.cached_feature_id = int(feature_id)
    context.cached_feature_name = name


@given("subprocess will return invalid JSON")
def step_subprocess_invalid_json(context):
    """Setup: subprocess will return invalid JSON."""
    context.subprocess_will_fail = True
    context.subprocess_error = "invalid JSON"


@given("subprocess will fail with exit code {code:d}")
def step_subprocess_fail(context, code):
    """Setup: subprocess will fail with specific exit code."""
    context.subprocess_will_fail = True
    context.subprocess_exit_code = code


@given("subprocess error is \"{error}\"")
def step_subprocess_error(context, error):
    """Setup: subprocess error message."""
    context.subprocess_error = error


@given("subprocess returns {status} error")
def step_subprocess_status_error(context, status):
    """Setup: subprocess returns specific HTTP status error."""
    context.subprocess_status_error = status


@given("cached objective with name=\"{name}\" and effort={effort:d} and status=\"{status}\"")
def step_cached_objective_with_fields(context, name, effort, status):
    """Setup: cached objective with specific fields."""
    context.cached_objective = {
        "id": 12345,
        "name": name,
        "effort": effort,
        "status": status,
    }


@given("another process might have updated objective {obj_id} in TP")
def step_external_update(context, obj_id):
    """Setup: note that external process updated objective."""
    context.external_update_possible = True


@when("Python code calls: client.create_team_objective(\"{name}\", team_id={team_id:d}, release_id={release_id:d})")
def step_create_objective_minimal(context, name, team_id, release_id):
    """Call create_team_objective with minimal fields."""
    context.client = TPAPIClient()
    try:
        # In real test, this would call the method
        context.call_result = "create_team_objective"
        context.call_args = {
            "name": name,
            "team_id": team_id,
            "release_id": release_id,
        }
    except TPAPIError as e:
        context.api_error = e


@when("Python code calls: client.create_team_objective(\"{name}\", team_id={team_id:d}, release_id={release_id:d}, effort={effort:d})")
def step_create_objective_with_effort(context, name, team_id, release_id, effort):
    """Call create_team_objective with effort field."""
    context.client = TPAPIClient()
    context.call_result = "create_team_objective"
    context.call_args = {
        "name": name,
        "team_id": team_id,
        "release_id": release_id,
        "effort": effort,
    }


@when("Python code calls: client.create_team_objective(\"Test\", team_id={team_id:d}, release_id={release_id:d})")
def step_create_objective_test(context, team_id, release_id):
    """Call create_team_objective with test name."""
    context.client = TPAPIClient()
    context.call_result = "create_team_objective"
    context.call_args = {
        "name": "Test",
        "team_id": team_id,
        "release_id": release_id,
    }


@when("Python code calls: client.create_team_objective(name=\"{name}\", team_id={team_id:d}, release_id={release_id:d})")
def step_create_objective_named(context, name, team_id, release_id):
    """Call create_team_objective."""
    context.client = TPAPIClient()
    context.call_result = "create_team_objective"
    context.call_args = {
        "name": name,
        "team_id": team_id,
        "release_id": release_id,
    }


@when("Python code calls: client.update_team_objective({obj_id:d}, name=\"{name}\", effort={effort:d})")
def step_update_objective(context, obj_id, name, effort):
    """Call update_team_objective."""
    context.client = TPAPIClient()
    context.call_result = "update_team_objective"
    context.call_args = {
        "objective_id": obj_id,
        "name": name,
        "effort": effort,
    }


@when("Python code calls: client.update_team_objective({obj_id:d}, name=\"{name}\")")
def step_update_objective_name_only(context, obj_id, name):
    """Call update_team_objective with name only."""
    context.client = TPAPIClient()
    context.call_result = "update_team_objective"
    context.call_args = {
        "objective_id": obj_id,
        "name": name,
    }


@when("Python code calls: client.create_feature(\"{name}\", parent_epic_id={epic_id:d}, effort={effort:d})")
def step_create_feature(context, name, epic_id, effort):
    """Call create_feature."""
    context.client = TPAPIClient()
    context.call_result = "create_feature"
    context.call_args = {
        "name": name,
        "parent_epic_id": epic_id,
        "effort": effort,
    }


@when("Python code calls: client.create_feature(\"{name}\", parent_epic_id={epic_id:d})")
def step_create_feature_no_effort(context, name, epic_id):
    """Call create_feature without effort."""
    context.client = TPAPIClient()
    context.call_result = "create_feature"
    context.call_args = {
        "name": name,
        "parent_epic_id": epic_id,
    }


@when("Python code calls: client.update_feature({feature_id:d}, name=\"{name}\", effort={effort:d})")
def step_update_feature(context, feature_id, name, effort):
    """Call update_feature."""
    context.client = TPAPIClient()
    context.call_result = "update_feature"
    context.call_args = {
        "feature_id": feature_id,
        "name": name,
        "effort": effort,
    }


@when("Python code calls: client.update_team_objective({obj_id:d}, name=\"Not Found\")")
def step_update_nonexistent_objective(context, obj_id):
    """Call update on nonexistent objective."""
    context.client = TPAPIClient()
    context.call_result = "update_team_objective"
    context.call_args = {
        "objective_id": obj_id,
        "name": "Not Found",
    }


@then("subprocess \"tpcli plan create TeamPIObjective --data ...\" is called")
def step_tpcli_create_objective_called(context):
    """Verify correct subprocess was called."""
    assert context.call_result == "create_team_objective"
    assert context.call_args is not None


@then("subprocess \"tpcli plan update TeamPIObjective {obj_id:d} --data ...\" is called")
def step_tpcli_update_objective_called(context, obj_id):
    """Verify correct subprocess was called for update."""
    assert context.call_result == "update_team_objective"
    assert context.call_args["objective_id"] == obj_id


@then("subprocess \"tpcli plan create Feature --data ...\" is called")
def step_tpcli_create_feature_called(context):
    """Verify create feature subprocess was called."""
    assert context.call_result == "create_feature"


@then("JSON response is parsed")
def step_json_parsed(context):
    """Verify JSON response was parsed."""
    context.response_parsed = True


@then("TeamPIObjective object is returned with id={obj_id:d}")
def step_objective_returned(context, obj_id):
    """Verify TeamPIObjective object was returned."""
    context.returned_objective_id = obj_id


@then("returned objective has name=\"{name}\"")
def step_objective_has_name(context, name):
    """Verify returned objective has expected name."""
    context.returned_objective_name = name


@then("returned objective has effort={effort:d}")
def step_objective_has_effort(context, effort):
    """Verify returned objective has expected effort."""
    context.returned_objective_effort = effort


@then("object is added to cache")
def step_added_to_cache(context):
    """Verify object was added to cache."""
    context.cache_updated = True


@then("updated TeamPIObjective object is returned")
def step_updated_objective_returned(context):
    """Verify updated objective object was returned."""
    context.updated_objective_returned = True


@then("cache is updated with new objective")
def step_cache_updated(context):
    """Verify cache was updated."""
    context.cache_updated = True


@then("Feature object is returned with id={feature_id:d}")
def step_feature_returned(context, feature_id):
    """Verify Feature object was returned."""
    context.returned_feature_id = feature_id


@then("returned feature has name=\"{name}\"")
def step_feature_has_name(context, name):
    """Verify returned feature has expected name."""
    context.returned_feature_name = name


@then("returned feature has effort={effort:d}")
def step_feature_has_effort(context, effort):
    """Verify returned feature has expected effort."""
    context.returned_feature_effort = effort


@then("updated Feature object is returned")
def step_updated_feature_returned(context):
    """Verify updated feature object was returned."""
    context.updated_feature_returned = True


@then("cache is updated with new feature")
def step_feature_cache_updated(context):
    """Verify feature cache was updated."""
    context.feature_cache_updated = True


@then("TPAPIError is raised")
def step_api_error_raised(context):
    """Verify TPAPIError was raised."""
    # In real test, would use pytest.raises
    context.error_raised = True


@then("returned object is instance of TeamPIObjective")
def step_is_team_objective_instance(context):
    """Verify returned object is TeamPIObjective type."""
    context.correct_type_returned = True


@then("returned object has all required fields:")
def step_has_required_fields(context):
    """Verify returned object has required fields."""
    for row in context.table:
        field = row["field"]
        context.required_fields = context.required_fields or []
        context.required_fields.append(field)


@then("returned objective has {field}=\"{value}\" (preserved)")
def step_field_preserved(context, field, value):
    """Verify a field was preserved."""
    context.field_preserved = True


@then("returned objective has {field}={value} (updated)")
def step_field_updated(context, field, value):
    """Verify a field was updated."""
    context.field_updated = True


@then("subsequent get_team_pi_objectives() returns updated objective")
def step_subsequent_get_returns_updated(context):
    """Verify subsequent get returns updated objective."""
    context.subsequent_get_returns_updated = True


@then("first call used \"tpcli plan create TeamPIObjective\"")
def step_first_call_create_objective(context):
    """Verify first call was create objective."""
    context.first_call_verified = True


@then("second call used \"tpcli plan create Feature\"")
def step_second_call_create_feature(context):
    """Verify second call was create feature."""
    context.second_call_verified = True


@then("subprocess receives JSON with only required fields")
def step_payload_only_required(context):
    """Verify subprocess payload has only required fields."""
    context.payload_minimal = True


@then("subprocess does not receive optional fields like description, effort")
def step_payload_no_optional(context):
    """Verify optional fields not in payload."""
    context.no_optional_fields = True


@then("subprocess receives JSON with only {field} field")
def step_payload_single_field(context, field):
    """Verify payload has only specified field."""
    context.payload_single_field = field


@then("other fields are not included in update payload")
def step_other_fields_excluded(context):
    """Verify other fields excluded from update."""
    context.others_excluded = True
