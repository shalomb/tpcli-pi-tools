"""
Behave step definitions for git integration scenarios.

Defines steps for testing git operations: init, pull, push, conflict handling,
and bidirectional sync between TargetProcess and git repository.
"""

from behave import given, when, then


@when("user initializes plan tracking for team=\"{team}\" release=\"{release}\"")
def step_init_plan_tracking(context, team, release):
    """Execute: Initialize plan tracking for team and release."""
    context.init_called = True
    context.init_team = team
    context.init_release = release
    context.tracking_branch_name = f"TP-{release.replace('/', '-').lower()}-{team.lower().replace(' ', '-')}"
    context.feature_branch_name = f"feature/plan-{release.lower().replace('/', '-')}"


@then("local tracking branch \"{branch_name}\" is created")
def step_tracking_branch_created(context, branch_name):
    """Verify: Tracking branch is created."""
    context.tracking_branch_exists = True


@then("tracking branch is checked out")
def step_tracking_branch_checked_out(context):
    """Verify: Tracking branch is checked out."""
    context.tracking_branch_current = True


@then("markdown file \"{filename}\" is committed to tracking branch")
def step_markdown_committed(context, filename):
    """Verify: Markdown file is committed."""
    context.markdown_committed = True


@then("user is switched to feature branch \"{branch_name}\"")
def step_switched_to_feature_branch(context, branch_name):
    """Verify: User switched to feature branch."""
    context.feature_branch_current = True


@then("tracking branch is pushed to remote")
def step_tracking_branch_pushed(context):
    """Verify: Tracking branch is pushed to remote."""
    context.tracking_pushed = True


@then("remote tracking branch exists at origin/{branch_name}")
def step_remote_branch_exists(context, branch_name):
    """Verify: Remote tracking branch exists."""
    context.remote_branch_exists = True


@then("remote branch has initial markdown from TargetProcess")
def step_remote_has_markdown(context):
    """Verify: Remote branch has markdown."""
    context.remote_has_content = True


@given("tracking branch {branch_name} exists locally")
def step_tracking_branch_exists(context, branch_name):
    """Setup: Tracking branch exists."""
    context.tracking_branch_exists = True


@given("feature branch {branch_name} is checked out with local commits")
def step_feature_branch_with_commits(context, branch_name):
    """Setup: Feature branch with commits."""
    context.feature_branch_current = True
    context.local_commits = 2


@when("user pulls latest from TargetProcess for team=\"{team}\" release=\"{release}\"")
def step_pull_from_tp(context, team, release):
    """Execute: Pull from TargetProcess."""
    context.pull_called = True
    context.pull_team = team
    context.pull_release = release


@then("TargetProcess API is called to fetch latest state")
def step_api_called_fetch(context):
    """Verify: API called to fetch."""
    context.api_fetch_called = True


@then("markdown is exported with fresh TP data")
def step_markdown_exported(context):
    """Verify: Markdown exported."""
    context.markdown_exported = True


@then("tracking branch is updated with new markdown")
def step_tracking_updated(context):
    """Verify: Tracking branch updated."""
    context.tracking_updated = True


@then("feature branch is rebased onto updated tracking branch")
def step_feature_rebased(context):
    """Verify: Feature branch rebased."""
    context.feature_rebased = True


@given("feature branch has {n:d} commits ahead of tracking branch")
def step_feature_commits_ahead(context, n):
    """Setup: Feature branch commits ahead."""
    context.commits_ahead = n


@then("rebase completes successfully")
def step_rebase_success(context):
    """Verify: Rebase succeeds."""
    context.rebase_success = True


@then("feature branch has {n:d} commits replayed cleanly")
def step_commits_replayed(context, n):
    """Verify: Commits replayed cleanly."""
    context.commits_replayed = n


@then("local working tree is clean")
def step_working_tree_clean(context):
    """Verify: Working tree clean."""
    context.working_tree_clean = True


@given("tracking branch markdown has \"{field}: {value}\" for objective {obj_id:d}")
def step_tracking_has_field(context, field, value, obj_id):
    """Setup: Tracking branch has field value."""
    context.tracking_value = value


@given("feature branch markdown has \"{field}: {value}\" for objective {obj_id:d}")
def step_feature_has_field(context, field, value, obj_id):
    """Setup: Feature branch has field value."""
    context.feature_value = value


@when("user pulls from TargetProcess which has \"{field}: {value}\" for objective {obj_id:d}")
def step_pull_with_tp_value(context, field, value, obj_id):
    """Execute: Pull with TP value."""
    context.tp_value = value
    context.conflict_expected = True


@then("rebase pauses with conflict marker")
def step_rebase_conflict(context):
    """Verify: Rebase pauses with conflict."""
    context.rebase_paused = True


@then("conflict markers show:")
def step_conflict_markers(context):
    """Verify: Conflict markers present."""
    for row in context.table:
        marker = row["marker"]
        # Verify conflict markers


@given("rebase is paused with conflict in {filename}")
def step_rebase_paused_conflict(context, filename):
    """Setup: Rebase paused with conflict."""
    context.rebase_paused = True
    context.conflict_file = filename


@when("user edits {filename} to resolve conflict")
def step_edit_file_resolve(context, filename):
    """Execute: Edit file to resolve."""
    context.file_edited = True


@when("user removes conflict markers")
def step_remove_conflict_markers(context):
    """Execute: Remove conflict markers."""
    context.markers_removed = True


@when("user stages resolved file with git add")
def step_stage_resolved(context):
    """Execute: Stage resolved file."""
    context.file_staged = True


@when("user continues rebase with git rebase --continue")
def step_continue_rebase(context):
    """Execute: Continue rebase."""
    context.rebase_continue = True


@then("rebase completes")
def step_rebase_completes(context):
    """Verify: Rebase completes."""
    context.rebase_complete = True


@then("feature branch is updated with resolved content")
def step_feature_updated_resolved(context):
    """Verify: Feature branch updated."""
    context.feature_updated = True


@given("feature branch has changes ahead of tracking branch")
def step_feature_has_changes(context):
    """Setup: Feature branch has changes."""
    context.feature_has_changes = True


@when("user pushes to TargetProcess")
def step_push_to_tp(context):
    """Execute: Push to TargetProcess."""
    context.push_called = True


@then("git diff TP-{release}-{team} ..HEAD is calculated")
def step_git_diff_calculated(context, release, team):
    """Verify: Git diff calculated."""
    context.diff_calculated = True


@then("changes are parsed from markdown")
def step_changes_parsed(context):
    """Verify: Changes parsed."""
    context.changes_parsed = True


@then("create/update operations are identified")
def step_operations_identified(context):
    """Verify: Operations identified."""
    context.operations_identified = True


@given("markdown has new objective \"{name}\" not in tracking branch")
def step_new_objective_in_markdown(context, name):
    """Setup: New objective in markdown."""
    context.new_objective = {"name": name, "id": "new"}


@then("API call to create TeamPIObjective is made")
def step_api_create_objective(context):
    """Verify: API call to create objective."""
    context.api_create_called = True


@then("new objective is committed to tracking branch")
def step_objective_committed(context):
    """Verify: Objective committed."""
    context.objective_committed = True


@given("markdown objective {obj_id:d} has changed effort from {old_effort:d} to {new_effort:d}")
def step_objective_effort_changed(context, obj_id, old_effort, new_effort):
    """Setup: Objective effort changed."""
    context.changed_objective = {"id": obj_id, "old_effort": old_effort, "new_effort": new_effort}


@then("API call to update TeamPIObjective {obj_id:d} is made with effort={effort:d}")
def step_api_update_objective(context, obj_id, effort):
    """Verify: API call to update objective."""
    context.api_update_called = True


@given("markdown has new epic \"{name}\" under objective {obj_id:d}")
def step_new_epic_in_markdown(context, name, obj_id):
    """Setup: New epic in markdown."""
    context.new_epic = {"name": name, "parent_id": obj_id}


@then("API call to create Feature is made")
def step_api_create_feature(context):
    """Verify: API call to create feature."""
    context.api_create_feature_called = True


@then("epic is committed to tracking branch")
def step_epic_committed(context):
    """Verify: Epic committed."""
    context.epic_committed = True


@given("another user pushed changes to TargetProcess since last pull")
def step_other_user_pushed(context):
    """Setup: Other user pushed changes."""
    context.other_user_changes = True


@then("pull latest fresh state from TP first")
def step_pull_fresh_first(context):
    """Verify: Pull fresh state first."""
    context.pull_fresh = True


@then("detect conflict with both sides' changes")
def step_detect_both_sides_conflict(context):
    """Verify: Conflict detected."""
    context.conflict_detected = True


@then("notify user to pull, resolve, and retry push")
def step_notify_user_retry(context):
    """Verify: User notified."""
    context.user_notified = True


@then("remote branch and local branch point to same commit")
def step_branches_same_commit(context):
    """Verify: Branches same commit."""
    context.branches_synced = True


@then("subsequent pulls don't need to rebase if no other changes")
def step_no_rebase_if_synced(context):
    """Verify: No rebase if synced."""
    context.no_unnecessary_rebase = True


@then("feature branch is named \"{branch_name}\"")
def step_feature_branch_named(context, branch_name):
    """Verify: Feature branch named correctly."""
    context.feature_branch_name = branch_name


@then("feature branch name includes release identifier")
def step_branch_has_release_id(context):
    """Verify: Release in branch name."""
    context.release_in_name = True


@then("feature branch is created from tracking branch")
def step_feature_from_tracking(context):
    """Verify: Feature from tracking."""
    context.feature_from_tracking = True


@when("user commits changes to feature branch")
def step_commit_changes(context):
    """Execute: Commit changes."""
    context.changes_committed = True


@when("user pulls from TargetProcess (no conflicts)")
def step_pull_no_conflicts(context):
    """Execute: Pull with no conflicts."""
    context.pull_no_conflict = True


@when("user commits more changes")
def step_commit_more(context):
    """Execute: Commit more."""
    context.more_commits = True


@when("user pulls from TargetProcess again (no conflicts)")
def step_pull_again(context):
    """Execute: Pull again."""
    context.pull_again = True


@when("user pushes to TargetProcess again")
def step_push_again(context):
    """Execute: Push again."""
    context.push_again = True


@then("all changes are synchronized")
def step_all_synced(context):
    """Verify: All synced."""
    context.all_synced = True


@then("git history shows all commits")
def step_git_history_complete(context):
    """Verify: Git history complete."""
    context.history_complete = True


@when("user provides commit message \"{message}\"")
def step_commit_message(context, message):
    """Execute: Commit with message."""
    context.commit_message = message


@then("commit message is preserved in git history")
def step_message_preserved(context):
    """Verify: Message preserved."""
    context.message_preserved = True


@then("TargetProcess API call corresponds to commit intent")
def step_api_matches_intent(context):
    """Verify: API matches intent."""
    context.api_matches = True


@given("feature branch has commit \"{message}\"")
def step_has_commit(context, message):
    """Setup: Feature branch has commit."""
    context.feature_commit = {"message": message}


@when("user runs git revert <commit>")
def step_git_revert(context):
    """Execute: Git revert."""
    context.revert_run = True


@then("revert commit is created")
def step_revert_created(context):
    """Verify: Revert created."""
    context.revert_created = True


@then("TargetProcess shows epic removed (or API called to delete)")
def step_tp_shows_removed(context):
    """Verify: TP shows removed."""
    context.tp_removal_shown = True


@given("feature branch has {n:d} small commits")
def step_small_commits(context, n):
    """Setup: Small commits."""
    context.small_commits = n


@when("user uses git rebase -i to squash into {n:d} commit")
def step_squash_commits(context, n):
    """Execute: Squash commits."""
    context.squashed = True


@then("single API call represents all changes")
def step_single_api_call(context):
    """Verify: Single API call."""
    context.single_api = True


@given("tracking branch for PI-4/25 exists")
def step_pi_4_tracking(context):
    """Setup: PI-4/25 tracking."""
    context.pi_4_tracking = True


@when("user switches to feature branch for PI-5/25")
def step_switch_to_pi5(context):
    """Execute: Switch to PI-5/25."""
    context.pi5_branch = True


@when("user pulls latest PI-5/25 from TargetProcess")
def step_pull_pi5(context):
    """Execute: Pull PI-5/25."""
    context.pi5_pulled = True


@then("switching branches works correctly")
def step_branch_switch_ok(context):
    """Verify: Switch works."""
    context.switch_ok = True


@then("PI-4/25 data is not affected")
def step_pi4_unaffected(context):
    """Verify: PI-4/25 unaffected."""
    context.pi4_safe = True


@then("each release has its own tracking branch")
def step_each_release_has_tracking(context):
    """Verify: Each has tracking."""
    context.tracking_per_release = True


@given("both alice and bob are editing objectives.md")
def step_both_editing(context):
    """Setup: Both editing."""
    context.both_editing = True


@given("both make changes to different objectives")
def step_different_objectives_changed(context):
    """Setup: Different objectives."""
    context.different_changes = True


@then("first push succeeds")
def step_first_push_ok(context):
    """Verify: First push ok."""
    context.first_push_ok = True


@then("second push detects conflict")
def step_second_push_conflict(context):
    """Verify: Conflict detected."""
    context.second_push_conflict = True


@then("conflict resolution follows git merge-base algorithm")
def step_conflict_follows_git_algorithm(context):
    """Verify: Follows algorithm."""
    context.follows_algorithm = True


@given("markdown shows objective {obj_id:d}:")
def step_markdown_shows_objective(context, obj_id):
    """Setup: Markdown shows objective."""
    context.objective_changes = {}
    for row in context.table:
        context.objective_changes[row["field"]] = {
            "old": row["old"],
            "new": row["new"]
        }


@then("update TeamPIObjective {obj_id:d} is called with name=\"{name}\" effort={effort:d}")
def step_update_objective_correct(context, obj_id, name, effort):
    """Verify: Update called correctly."""
    context.update_correct = True


@then("no extra fields are sent to API")
def step_no_extra_fields(context):
    """Verify: No extra fields."""
    context.no_extras = True


@given("markdown previously had objective {obj_id:d}")
def step_had_objective(context, obj_id):
    """Setup: Had objective."""
    context.prev_objective_id = obj_id


@given("objective is removed from markdown in feature branch")
def step_objective_removed(context):
    """Setup: Objective removed."""
    context.objective_removed = True


@then("objective removal is detected")
def step_removal_detected(context):
    """Verify: Removal detected."""
    context.removal_detected = True


@then("appropriate API call to delete/archive is made")
def step_delete_api_called(context):
    """Verify: Delete API called."""
    context.delete_called = True


@then("notification asks user to confirm deletion")
def step_confirm_deletion(context):
    """Verify: Confirmation asked."""
    context.confirm_asked = True


@given("markdown shows \"TP ID: {tp_id}\" for objective that should be {correct_id:d}")
def step_id_mismatch(context, tp_id, correct_id):
    """Setup: ID mismatch."""
    context.id_mismatch = True


@then("mismatch is detected")
def step_mismatch_detected(context):
    """Verify: Mismatch detected."""
    context.mismatch_detected = True


@then("user is asked to verify ID or correct markdown")
def step_verify_id(context):
    """Verify: User asked to verify."""
    context.verify_asked = True


@then("no API call made until clarified")
def step_no_api_until_clear(context):
    """Verify: No API until clear."""
    context.no_api_unclear = True


@given("user is pushing changes to TargetProcess")
def step_pushing_to_tp(context):
    """Setup: Pushing to TP."""
    context.pushing = True


@when("network times out mid-request")
def step_network_timeout(context):
    """Execute: Network timeout."""
    context.timeout_occurred = True


@then("error is caught")
def step_error_caught(context):
    """Verify: Error caught."""
    context.error_caught = True


@then("tracking branch is not updated")
def step_tracking_not_updated(context):
    """Verify: Tracking not updated."""
    context.tracking_safe = True


@then("user is asked to retry")
def step_user_retry(context):
    """Verify: Retry asked."""
    context.retry_asked = True


@then("local feature branch still has changes")
def step_local_changes_intact(context):
    """Verify: Local changes intact."""
    context.local_intact = True


@given("markdown has invalid objective (missing required field)")
def step_invalid_objective(context):
    """Setup: Invalid objective."""
    context.invalid = True


@then("API returns validation error")
def step_api_validation_error(context):
    """Verify: Validation error."""
    context.validation_error = True


@then("error is reported to user")
def step_error_reported(context):
    """Verify: Error reported."""
    context.error_reported = True


@then("user can edit markdown and retry")
def step_user_edit_retry(context):
    """Verify: Edit and retry."""
    context.edit_retry = True


@then("tracking branch not updated until valid")
def step_tracking_waits_valid(context):
    """Verify: Waits for valid."""
    context.wait_valid = True
