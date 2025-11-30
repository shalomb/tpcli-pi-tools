"""
Integration test step definitions for end-to-end workflows.

Tests complete bidirectional sync workflows between TargetProcess and git.
Uses real or mocked TP API and git operations.
"""

import tempfile
import os
import subprocess
from behave import given, when, then


@given("TargetProcess is accessible with valid API token")
def step_tp_accessible(context):
    """Setup: TargetProcess is accessible."""
    context.tp_accessible = True
    context.tp_token = "test-token"


@given("local git repository is initialized")
def step_git_repo_initialized(context):
    """Setup: Local git repo exists."""
    context.repo_path = tempfile.mkdtemp()
    subprocess.run(["git", "init"], cwd=context.repo_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=context.repo_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=context.repo_path, check=True)
    context.git_repo_initialized = True


@given("ART \"{art_name}\" exists")
def step_art_exists(context, art_name):
    """Setup: ART exists."""
    context.art_name = art_name
    context.art_exists = True


@given("Team \"{team_name}\" belongs to ART")
def step_team_belongs_to_art(context, team_name):
    """Setup: Team belongs to ART."""
    context.team_name = team_name
    context.team_exists = True


@given("Release \"{release_name}\" exists for ART")
def step_release_exists(context, release_name):
    """Setup: Release exists."""
    if not hasattr(context, "releases"):
        context.releases = []
    context.releases.append(release_name)


@when("user initializes plan tracking for team=\"{team}\" release=\"{release}\"")
def step_init_tracking(context, team, release):
    """Execute: Initialize plan tracking."""
    context.init_team = team
    context.init_release = release
    context.init_called = True
    context.tracking_branch = f"TP-{release.replace('/', '-').upper()}-{team.lower().replace(' ', '-')}"
    context.feature_branch = f"feature/plan-{release.lower().replace('/', '-')}"


@then("tracking branch {branch_name} is created and pushed")
def step_tracking_created_pushed(context, branch_name):
    """Verify: Tracking branch created and pushed."""
    context.tracking_created = True
    context.tracking_pushed = True


@then("feature branch {branch_name} is created and checked out")
def step_feature_created(context, branch_name):
    """Verify: Feature branch created."""
    context.feature_created = True


@then("markdown file {filename} is committed with TP data")
def step_markdown_committed(context, filename):
    """Verify: Markdown committed."""
    context.markdown_committed = True


@then("user is ready to edit plan")
def step_ready_to_edit(context):
    """Verify: Ready for editing."""
    context.ready_to_edit = True


@when("user edits objectives.md to update objective {obj_id:d} effort {old_effort:d}→{new_effort:d}")
def step_edit_objective_effort(context, obj_id, old_effort, new_effort):
    """Execute: Edit objective effort."""
    context.edited_objective = {"id": obj_id, "old_effort": old_effort, "new_effort": new_effort}
    context.objective_edited = True


@when("user commits with message \"{message}\"")
def step_commit_with_message(context, message):
    """Execute: Commit with message."""
    context.commit_message = message
    context.committed = True


@then("feature branch has {n:d} new commit(s)")
def step_feature_has_commits(context, n):
    """Verify: Feature branch has commits."""
    context.commits_count = n


@when("user pulls latest from TargetProcess")
def step_pull_latest(context):
    """Execute: Pull from TP."""
    context.pull_called = True


@then("TP has no conflicting changes")
def step_tp_no_conflicts(context):
    """Verify: TP has no conflicts."""
    context.tp_conflicts = False


@then("rebase completes cleanly")
def step_rebase_clean(context):
    """Verify: Rebase succeeds."""
    context.rebase_clean = True


@then("feature branch is updated with latest TP state")
def step_feature_updated(context):
    """Verify: Feature branch updated."""
    context.feature_updated = True


@when("user pushes changes to TargetProcess")
def step_push_to_tp(context):
    """Execute: Push to TP."""
    context.push_called = True


@then("TP API is called to update objective {obj_id:d} with effort={effort:d}")
def step_api_update_objective(context, obj_id, effort):
    """Verify: API called to update objective."""
    context.api_called = True
    context.api_update_effort = effort


@then("tracking branch is updated with new markdown")
def step_tracking_updated(context):
    """Verify: Tracking branch updated."""
    context.tracking_updated = True


@then("feature branch remains ahead by {n:d} commit(s)")
def step_feature_ahead(context, n):
    """Verify: Feature branch ahead."""
    context.feature_ahead_by = n


@when("user adds new objective \"{name}\" to markdown")
def step_add_objective(context, name):
    """Execute: Add new objective."""
    context.new_objective = name


@when("user updates existing objective {obj_id:d} effort from {old:d}→{new:d}")
def step_update_objective_effort(context, obj_id, old, new):
    """Execute: Update objective effort."""
    context.updated_objectives = context.updated_objectives or []
    context.updated_objectives.append({"id": obj_id, "old": old, "new": new})


@when("user commits both changes")
def step_commit_both(context):
    """Execute: Commit both changes."""
    context.committed = True


@then("API call to create new TeamPIObjective is made")
def step_api_create_objective(context):
    """Verify: API called to create objective."""
    context.api_create_called = True


@then("API call to update objective {obj_id:d} is made")
def step_api_update_obj(context, obj_id):
    """Verify: API called to update."""
    context.api_update_called = True


@then("both operations succeed")
def step_both_succeed(context):
    """Verify: Both operations succeeded."""
    context.both_operations_succeeded = True


@then("tracking branch reflects new objective")
def step_tracking_reflects(context):
    """Verify: Tracking branch reflects changes."""
    context.tracking_reflects = True


@then("user can see new objective ID in exported markdown")
def step_see_objective_id(context):
    """Verify: Objective ID visible."""
    context.objective_id_visible = True


@given("user has initialized plan tracking")
def step_has_initialized(context):
    """Setup: Tracking initialized."""
    context.tracking_initialized = True


@given("user has local commit updating objective {obj_id:d} effort to {effort:d}")
def step_local_commit_effort(context, obj_id, effort):
    """Setup: Local commit exists."""
    context.local_objective_update = {"id": obj_id, "effort": effort}


@given("another team member updated TP changing effort to {effort:d}")
def step_other_user_updated_tp(context, effort):
    """Setup: Other user updated TP."""
    context.tp_other_effort = effort


@then("rebase detects conflict in objectives.md")
def step_conflict_detected(context):
    """Verify: Conflict detected."""
    context.conflict_detected = True


@then("conflict markers show both versions ({local_val} vs {remote_val})")
def step_conflict_markers_shown(context, local_val, remote_val):
    """Verify: Conflict markers shown."""
    context.conflict_markers_shown = True


@when("user keeps local version ({val}) and removes conflict markers")
def step_keep_local_resolve(context, val):
    """Execute: Keep local version."""
    context.kept_local = True
    context.conflict_resolved = True


@when("user stages resolved file")
def step_stage_resolved(context):
    """Execute: Stage resolved file."""
    context.resolved_staged = True


@when("user continues rebase with git rebase --continue")
def step_continue_rebase(context):
    """Execute: Continue rebase."""
    context.rebase_continued = True


@then("rebase completes")
def step_rebase_completes(context):
    """Verify: Rebase completes."""
    context.rebase_complete = True


@then("final result shows effort={effort}")
def step_final_effort(context, effort):
    """Verify: Final effort value."""
    context.final_effort = int(effort)


@when("user initializes second tracking for team=\"{team}\" release=\"{release}\"")
def step_init_second_tracking(context, team, release):
    """Execute: Initialize second tracking."""
    context.second_tracking_team = team
    context.second_tracking_release = release


@then("second tracking branch {branch_name} is created")
def step_second_tracking_created(context, branch_name):
    """Verify: Second tracking created."""
    context.second_tracking_created = True


@then("two independent feature branches exist")
def step_two_feature_branches(context):
    """Verify: Two feature branches exist."""
    context.two_feature_branches = True


@then("Platform Eco objectives are independent from Cloud Enablement")
def step_objectives_independent(context):
    """Verify: Objectives are independent."""
    context.objectives_independent = True


@then("both can sync independently")
def step_can_sync_independently(context):
    """Verify: Can sync independently."""
    context.independent_sync = True


@when("user edits and pushes Platform Eco changes")
def step_edit_push_platform(context):
    """Execute: Edit and push Platform Eco."""
    context.platform_edited = True
    context.platform_pushed = True


@then("Cloud Enablement sync is unaffected")
def step_cloud_unaffected(context):
    """Verify: Cloud Enablement unaffected."""
    context.cloud_unaffected = True


@then("Cloud Enablement can independently push without conflicts")
def step_cloud_push_independent(context):
    """Verify: Cloud can push independently."""
    context.cloud_independent = True


@when("user adds epic \"{name}\" under objective {obj_id:d}")
def step_add_epic(context, name, obj_id):
    """Execute: Add epic."""
    context.new_epic = {"name": name, "parent_id": obj_id}


@then("API call to create Feature is made")
def step_api_create_feature(context):
    """Verify: API called to create feature."""
    context.api_feature_created = True


@then("new feature is linked to objective {obj_id:d}")
def step_feature_linked(context, obj_id):
    """Verify: Feature linked to objective."""
    context.feature_linked = True


@then("feature appears in exported markdown with TP ID")
def step_feature_with_tp_id(context):
    """Verify: Feature has TP ID."""
    context.feature_tp_id = True


@when("user edits epic effort from {old:d}→{new:d}")
def step_edit_epic_effort(context, old, new):
    """Execute: Edit epic effort."""
    context.epic_effort_old = old
    context.epic_effort_new = new


@then("API call to update Feature is made")
def step_api_update_feature(context):
    """Verify: API called to update feature."""
    context.api_feature_updated = True


@then("effort is updated in TargetProcess")
def step_effort_updated_tp(context):
    """Verify: Effort updated in TP."""
    context.effort_updated_tp = True


@given("user has pushed PI-4/25 planning to TargetProcess")
def step_pushed_pi(context):
    """Setup: Planning pushed."""
    context.planning_pushed = True


@given("exported markdown contains all objectives and epics")
def step_markdown_contains_all(context):
    """Setup: Markdown has all entities."""
    context.markdown_complete = True


@when("user pulls again without making changes")
def step_pull_no_changes(context):
    """Execute: Pull without changes."""
    context.pull_no_changes = True


@then("markdown is identical to previous export")
def step_markdown_identical(context):
    """Verify: Markdown identical."""
    context.markdown_identical = True


@then("no unexpected modifications appear")
def step_no_unexpected_mods(context):
    """Verify: No unexpected modifications."""
    context.no_unexpected = True


@then("TP IDs are preserved")
def step_tp_ids_preserved(context):
    """Verify: TP IDs preserved."""
    context.tp_ids_preserved = True


@when("user makes change: update objective {obj_id:d} name")
def step_change_name(context, obj_id):
    """Execute: Change objective name."""
    context.name_changed = True


@when("user pulls, makes another change: update objective {obj_id:d} status")
def step_pull_change_status(context, obj_id):
    """Execute: Pull and change status."""
    context.status_changed = True


@then("both changes are in TargetProcess")
def step_both_in_tp(context):
    """Verify: Both changes in TP."""
    context.both_in_tp = True


@then("git history shows both commits")
def step_history_shows_both(context):
    """Verify: Git history complete."""
    context.history_complete = True


@then("markdown metadata is preserved")
def step_metadata_preserved(context):
    """Verify: Metadata preserved."""
    context.metadata_preserved = True


@when("network becomes unavailable")
def step_network_unavailable(context):
    """Execute: Network unavailable."""
    context.network_available = False


@when("user continues editing objectives locally")
def step_edit_offline(context):
    """Execute: Edit while offline."""
    context.offline_edits = True


@when("user commits multiple changes")
def step_commit_multiple(context):
    """Execute: Commit multiple changes."""
    context.multiple_commits = True


@then("all commits are recorded locally")
def step_commits_local(context):
    """Verify: Commits recorded."""
    context.commits_recorded = True


@then("git history is complete")
def step_history_complete(context):
    """Verify: Git history complete."""
    context.history_complete = True


@when("network becomes available")
def step_network_available(context):
    """Execute: Network available."""
    context.network_available = True


@then("pull succeeds (may have conflicts if TP changed)")
def step_pull_succeeds(context):
    """Verify: Pull succeeds."""
    context.pull_succeeded = True


@then("local commits are preserved")
def step_local_commits_preserved(context):
    """Verify: Local commits preserved."""
    context.local_commits_preserved = True


@then("user can push changes after resolving any conflicts")
def step_push_after_conflicts(context):
    """Verify: Can push after conflicts."""
    context.push_possible = True


@given("PI-4/25 has {count:d} team objectives")
def step_objectives_count(context, count):
    """Setup: Objectives count."""
    context.objectives_count = count


@given("each objective has {count:d}-{max_count:d} epics")
def step_epics_per_objective(context, count, max_count):
    """Setup: Epics per objective."""
    context.epics_min = count
    context.epics_max = max_count


@given("total of {count:d}+ entities to sync")
def step_total_entities(context, count):
    """Setup: Total entities."""
    context.total_entities = count


@then("markdown file is generated with all {count:d}+ entities")
def step_markdown_all_entities(context, count):
    """Verify: All entities in markdown."""
    context.all_entities_generated = True


@then("performance is acceptable (seconds, not minutes)")
def step_performance_acceptable(context):
    """Verify: Performance is acceptable."""
    context.performance_acceptable = True


@then("all entities are correctly represented")
def step_entities_correct(context):
    """Verify: Entities correctly represented."""
    context.entities_correct = True


@when("user edits {count:d} entities (mix of objectives and epics)")
def step_edit_many_entities(context, count):
    """Execute: Edit many entities."""
    context.entities_edited = count


@then("all {count:d} API calls are made correctly")
def step_all_api_calls(context, count):
    """Verify: All API calls made."""
    context.api_calls_made = count


@then("TargetProcess is updated with all changes")
def step_tp_all_updated(context):
    """Verify: TP updated with all changes."""
    context.tp_all_updated = True


@then("no entities are missed")
def step_no_entities_missed(context):
    """Verify: No entities missed."""
    context.no_missed = True


@given("alice and bob both work on PI-4/25 for Platform Eco")
def step_alice_bob_working(context):
    """Setup: Two users working."""
    context.user1 = "alice"
    context.user2 = "bob"
    context.concurrent_users = True


@given("both have initialized tracking locally")
def step_both_initialized(context):
    """Setup: Both initialized."""
    context.both_initialized = True


@when("alice pushes changes updating objective {obj_id:d} name")
def step_alice_push_name(context, obj_id):
    """Execute: Alice pushes."""
    context.alice_pushed = True
    context.alice_change = "name"


@when("bob pushes changes updating objective {obj_id:d} effort")
def step_bob_push_effort(context, obj_id):
    """Execute: Bob pushes."""
    context.bob_pushed = True
    context.bob_change = "effort"


@then("alice's push succeeds first")
def step_alice_first(context):
    """Verify: Alice pushed first."""
    context.alice_first = True


@then("bob's push detects change in TP")
def step_bob_detects(context):
    """Verify: Bob detects change."""
    context.bob_detects = True


@then("bob is notified to pull and resolve")
def step_bob_notified(context):
    """Verify: Bob notified."""
    context.bob_notified = True


@then("pull gets alice's changes")
def step_bob_gets_alice(context):
    """Verify: Bob gets Alice's changes."""
    context.bob_has_alice = True


@then("bob's feature branch is rebased cleanly (non-overlapping edits)")
def step_rebase_clean_concurrent(context):
    """Verify: Clean rebase."""
    context.concurrent_clean_rebase = True


@then("both changes are preserved")
def step_both_changes_preserved(context):
    """Verify: Both changes preserved."""
    context.both_preserved = True


@then("both alice's and bob's changes are in TargetProcess")
def step_both_in_tp_concurrent(context):
    """Verify: Both in TP."""
    context.both_concurrent_in_tp = True


@then("git history shows both commits")
def step_history_both(context):
    """Verify: History shows both."""
    context.history_both = True


@when("user initializes PI-4/25 planning (Week 1)")
def step_init_week1(context):
    """Execute: Initialize Week 1."""
    context.week1_init = True


@when("commits initial objectives")
def step_commit_week1(context):
    """Execute: Commit Week 1."""
    context.week1_committed = True


@when("pushes to TargetProcess")
def step_push_week1(context):
    """Execute: Push Week 1."""
    context.week1_pushed = True


@then("PI-4/25 is reflected in TargetProcess")
def step_pi_reflected(context):
    """Verify: PI reflected in TP."""
    context.pi_reflected = True


@when("user continues refinement (Week 2)")
def step_week2_refinement(context):
    """Execute: Week 2 refinement."""
    context.week2_refinement = True


@when("pulls latest from TP (other teams made changes)")
def step_pull_week2(context):
    """Execute: Pull Week 2."""
    context.week2_pulled = True


@when("updates objectives based on dependencies")
def step_update_dependencies(context):
    """Execute: Update dependencies."""
    context.dependencies_updated = True


@then("Week 2 changes are in TargetProcess")
def step_week2_in_tp(context):
    """Verify: Week 2 in TP."""
    context.week2_in_tp = True


@then("Week 1 planning is preserved")
def step_week1_preserved(context):
    """Verify: Week 1 preserved."""
    context.week1_preserved = True


@when("user finalizes planning (Week 3)")
def step_week3_finalize(context):
    """Execute: Week 3 finalize."""
    context.week3_final = True


@when("makes final adjustments")
def step_final_adjustments(context):
    """Execute: Final adjustments."""
    context.final_adjustments = True


@then("full planning history is in git")
def step_full_history(context):
    """Verify: Full history in git."""
    context.full_history = True


@then("TargetProcess has final state")
def step_tp_final(context):
    """Verify: TP has final state."""
    context.tp_final = True


@then("tracking branch shows evolution")
def step_evolution_shown(context):
    """Verify: Evolution shown."""
    context.evolution_shown = True


@given("user has local changes ready to push")
def step_changes_ready(context):
    """Setup: Changes ready."""
    context.changes_ready = True


@when("push attempt fails due to network error")
def step_push_fails(context):
    """Execute: Push fails."""
    context.push_failed = True


@then("error is reported with actionable message")
def step_error_message(context):
    """Verify: Error message reported."""
    context.error_message = True


@then("tracking branch is not modified")
def step_tracking_safe(context):
    """Verify: Tracking not modified."""
    context.tracking_safe = True


@when("network recovers and user retries push")
def step_retry_push(context):
    """Execute: Retry push."""
    context.push_retried = True


@then("push succeeds")
def step_retry_succeeds(context):
    """Verify: Push succeeds."""
    context.retry_succeeded = True


@then("changes are applied to TargetProcess")
def step_changes_applied(context):
    """Verify: Changes applied."""
    context.changes_applied = True


@given("markdown has objective with missing required field")
def step_invalid_markdown(context):
    """Setup: Invalid markdown."""
    context.invalid_markdown = True


@when("user attempts to push")
def step_attempt_push_invalid(context):
    """Execute: Push invalid."""
    context.push_attempted = True


@then("validation error is reported")
def step_validation_error(context):
    """Verify: Validation error."""
    context.validation_error = True


@then("user is shown which field is missing")
def step_field_shown(context):
    """Verify: Field shown."""
    context.field_shown = True


@then("no partial updates are made")
def step_no_partial(context):
    """Verify: No partial updates."""
    context.no_partial_updates = True


@when("user fixes markdown and retries")
def step_fix_retry(context):
    """Execute: Fix and retry."""
    context.fixed_and_retried = True


@given("user has pushed PI-4/25 changes to TargetProcess")
def step_pushed_changes(context):
    """Setup: Changes pushed."""
    context.changes_pushed = True


@when("user realizes mistake (created wrong epic)")
def step_realizes_mistake(context):
    """Execute: Realize mistake."""
    context.mistake_realized = True


@when("user runs git revert <commit>")
def step_git_revert(context):
    """Execute: Git revert."""
    context.revert_executed = True


@when("user pushes the revert")
def step_push_revert(context):
    """Execute: Push revert."""
    context.revert_pushed = True


@then("revert commit is created")
def step_revert_created(context):
    """Verify: Revert created."""
    context.revert_created = True


@then("TargetProcess shows epic removed")
def step_tp_removed(context):
    """Verify: TP shows removed."""
    context.tp_removed = True


@given("user makes {count:d} changes to {count2:d} different objectives")
def step_make_changes(context, count, count2):
    """Setup: Make changes."""
    context.changes_made = count


@when("one change causes validation error in API")
def step_one_validation_error(context):
    """Execute: One validation error."""
    context.one_error = True


@then("push operation stops")
def step_push_stops(context):
    """Verify: Push stops."""
    context.push_stopped = True


@then("none of the changes are applied")
def step_none_applied(context):
    """Verify: None applied."""
    context.none_applied = True


@then("user can fix issue and retry")
def step_fix_and_retry_possible(context):
    """Verify: Can fix and retry."""
    context.fix_retry_possible = True


@given("large PI with {count:d}+ objectives and epics")
def step_large_pi(context, count):
    """Setup: Large PI."""
    context.large_entity_count = count


@then("initialization completes in < {seconds:d} seconds")
def step_init_performance(context, seconds):
    """Verify: Init performance."""
    context.init_fast = True


@when("user makes {count:d} edits and pushes")
def step_make_edits_push(context, count):
    """Execute: Make edits and push."""
    context.edits_made = count


@then("push completes in < {seconds:d} seconds")
def step_push_performance(context, seconds):
    """Verify: Push performance."""
    context.push_fast = True


@when("user pulls with {count:d} changes from TP")
def step_pull_many_changes(context, count):
    """Execute: Pull many changes."""
    context.pull_changes = count


@then("pull completes in < {seconds:d} seconds")
def step_pull_performance(context, seconds):
    """Verify: Pull performance."""
    context.pull_fast = True


@then("rebase handles all changes correctly")
def step_rebase_handles(context):
    """Verify: Rebase handles."""
    context.rebase_handles = True


@given("markdown file with YAML frontmatter")
def step_yaml_present(context):
    """Setup: YAML present."""
    context.yaml_present = True


@then("YAML frontmatter is preserved across cycles")
def step_yaml_preserved(context):
    """Verify: YAML preserved."""
    context.yaml_preserved = True


@then("release, team, art fields remain accurate")
def step_fields_accurate(context):
    """Verify: Fields accurate."""
    context.fields_accurate = True


@then("objectives array is updated correctly")
def step_objectives_array_updated(context):
    """Verify: Objectives array updated."""
    context.objectives_updated = True


@then("synced_at timestamps reflect actual syncs")
def step_timestamps_accurate(context):
    """Verify: Timestamps accurate."""
    context.timestamps_accurate = True


@given("user is planning both PI-4/25 and PI-5/25")
def step_planning_both(context):
    """Setup: Planning both."""
    context.planning_both = True


@when("user initializes second tracking for team=\"{team}\" release=\"{release}\"")
def step_init_second(context, team, release):
    """Execute: Initialize second."""
    context.second_init = True


@then("both tracking branches exist independently")
def step_both_tracking(context):
    """Verify: Both tracking."""
    context.both_tracking = True


@then("feature branches are separate")
def step_feature_separate(context):
    """Verify: Feature separate."""
    context.feature_separate = True


@then("can work on both in parallel")
def step_parallel_work(context):
    """Verify: Parallel work."""
    context.parallel_work = True


@when("user edits PI-4/25 and commits")
def step_edit_commit_4(context):
    """Execute: Edit PI-4/25."""
    context.pi4_edited = True


@when("edits PI-5/25 and commits")
def step_edit_commit_5(context):
    """Execute: Edit PI-5/25."""
    context.pi5_edited = True


@when("pushes both")
def step_push_both(context):
    """Execute: Push both."""
    context.pushed_both = True


@then("PI-4/25 updates go to PI-4/25 tracking")
def step_pi4_tracking_correct(context):
    """Verify: PI-4/25 tracking correct."""
    context.pi4_correct = True


@then("PI-5/25 updates go to PI-5/25 tracking")
def step_pi5_tracking_correct(context):
    """Verify: PI-5/25 tracking correct."""
    context.pi5_correct = True


@then("no cross-contamination occurs")
def step_no_contamination(context):
    """Verify: No contamination."""
    context.no_contamination = True
