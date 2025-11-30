Feature: Git Integration for PI Plan Sync

  Git-native bidirectional sync between TargetProcess and local git repository.
  Manages tracking branches, conflict detection, and coordinated push/pull operations.

  Scenario: Initialize plan tracking creates tracking branch
    When user initializes plan tracking for team="Platform Eco" release="PI-4/25"
    Then local tracking branch "TP-PI-4-25-platform-eco" is created
    And tracking branch is checked out
    And markdown file "pi-4-25-platform-eco.md" is committed to tracking branch
    And user is switched to feature branch "feature/plan-pi-4-25"

  Scenario: Initialize push syncs to remote
    When user initializes plan tracking for team="Platform Eco" release="PI-4/25"
    Then tracking branch is pushed to remote
    And remote tracking branch exists at origin/TP-PI-4-25-platform-eco
    And remote branch has initial markdown from TargetProcess

  Scenario: Pull from TargetProcess updates tracking branch
    Given tracking branch TP-PI-4-25-platform-eco exists locally
    And feature branch feature/plan-pi-4-25 is checked out with local commits
    When user pulls latest from TargetProcess for team="Platform Eco" release="PI-4/25"
    Then TargetProcess API is called to fetch latest state
    And markdown is exported with fresh TP data
    And tracking branch is updated with new markdown
    And tracking branch is pushed to remote
    And feature branch is rebased onto updated tracking branch

  Scenario: Pull succeeds with no conflicts
    Given feature branch has 2 commits ahead of tracking branch
    When user pulls from TargetProcess
    Then rebase completes successfully
    And feature branch has 2 commits replayed cleanly
    And local working tree is clean

  Scenario: Pull detects conflicts
    Given tracking branch markdown has "Effort: 20" for objective 2019099
    And feature branch markdown has "Effort: 34" for objective 2019099
    When user pulls from TargetProcess which has "Effort: 25" for objective 2019099
    Then rebase pauses with conflict marker
    And conflict markers show:
      | marker     | content       |
      | <<<<<<< HEAD | Effort: 25    |
      | =======     |               |
      | >>>>>>> | Effort: 34        |

  Scenario: User resolves conflict manually
    Given rebase is paused with conflict in objectives.md
    When user edits objectives.md to resolve conflict
    And user removes conflict markers
    And user stages resolved file with git add
    And user continues rebase with git rebase --continue
    Then rebase completes
    And feature branch is updated with resolved content

  Scenario: Push to TargetProcess identifies changes
    Given feature branch has changes ahead of tracking branch
    When user pushes to TargetProcess
    Then git diff TP-PI-4-25-platform-eco..HEAD is calculated
    And changes are parsed from markdown
    And create/update operations are identified

  Scenario: Push creates new objective
    Given markdown has new objective "Security Initiative" not in tracking branch
    When user pushes to TargetProcess
    Then API call to create TeamPIObjective is made
    And new objective is committed to tracking branch
    And tracking branch is pushed to remote

  Scenario: Push updates existing objective
    Given markdown objective 2019099 has changed effort from 21 to 34
    When user pushes to TargetProcess
    Then API call to update TeamPIObjective 2019099 is made with effort=34
    And updated objective is committed to tracking branch
    And tracking branch is pushed to remote

  Scenario: Push creates new epic
    Given markdown has new epic "Security Framework" under objective 2019099
    When user pushes to TargetProcess
    Then API call to create Feature is made
    And epic is committed to tracking branch

  Scenario: Push handles TP conflicts
    Given another user pushed changes to TargetProcess since last pull
    When user pushes changes
    Then pull latest fresh state from TP first
    And detect conflict with both sides' changes
    And notify user to pull, resolve, and retry push

  Scenario: Tracking branch synchronizes with remote
    When user initializes plan tracking
    And tracking branch is created and pushed
    Then remote branch and local branch point to same commit
    And subsequent pulls don't need to rebase if no other changes

  Scenario: Feature branch name follows convention
    When user initializes plan tracking for release="PI-4/25"
    Then feature branch is named "feature/plan-pi-4-25"
    And feature branch name includes release identifier
    And feature branch is created from tracking branch

  Scenario: Multiple pull/push cycles work correctly
    When user initializes plan tracking
    And user commits changes to feature branch
    And user pulls from TargetProcess (no conflicts)
    And user pushes to TargetProcess
    And user commits more changes
    And user pulls from TargetProcess again (no conflicts)
    And user pushes to TargetProcess again
    Then all changes are synchronized
    And git history shows all commits

  Scenario: Commit messages reference changes made
    When user commits change to objectives.md that updates effort
    And user provides commit message "Refine Platform Governance: increase effort 21→34"
    And user pushes to TargetProcess
    Then commit message is preserved in git history
    And TargetProcess API call corresponds to commit intent

  Scenario: Rollback local changes via git revert
    Given feature branch has commit "Add Security Epic"
    When user runs git revert <commit>
    And user pushes to TargetProcess
    Then revert commit is created
    And TargetProcess shows epic removed (or API called to delete)
    And full git history preserved

  Scenario: Squash commits before push
    Given feature branch has 5 small commits
    When user uses git rebase -i to squash into 1 commit
    And user pushes to TargetProcess
    Then single API call represents all changes
    And git history shows 1 squashed commit

  Scenario: Switching between releases
    Given tracking branch for PI-4/25 exists
    When user switches to feature branch for PI-5/25
    And user pulls latest PI-5/25 from TargetProcess
    Then switching branches works correctly
    And PI-4/25 data is not affected
    And each release has its own tracking branch

  Scenario: Concurrent edits with proper conflict detection
    Given both alice and bob are editing objectives.md
    And both make changes to different objectives
    When both push to TargetProcess
    Then first push succeeds
    And second push detects conflict
    And conflict resolution follows git merge-base algorithm

  Scenario: Markdown changes map to correct API calls
    Given markdown shows objective 2019099:
      | field  | old | new |
      | name   | "API Perf" | "API Performance" |
      | effort | 21 | 34 |
    When user pushes to TargetProcess
    Then update TeamPIObjective 2019099 is called with name="API Performance" effort=34
    And no extra fields are sent to API

  Scenario: Deleted objective in markdown triggers removal
    Given markdown previously had objective 2019099
    And objective is removed from markdown in feature branch
    When user pushes to TargetProcess
    Then objective removal is detected
    And appropriate API call to delete/archive is made
    Or notification asks user to confirm deletion

  Scenario: Edge case: Objective ID mismatch in markdown
    Given markdown shows "TP ID: 99999" for objective that should be 2019099
    When user pushes to TargetProcess
    Then mismatch is detected
    And user is asked to verify ID or correct markdown
    And no API call made until clarified

  Scenario: Error handling: Network timeout during push
    Given user is pushing changes to TargetProcess
    When network times out mid-request
    Then error is caught
    And tracking branch is not updated
    And user is asked to retry
    And local feature branch still has changes

  Scenario: Error handling: TargetProcess validation error
    Given markdown has invalid objective (missing required field)
    When user pushes to TargetProcess
    Then API returns validation error
    And error is reported to user
    And user can edit markdown and retry
    And tracking branch not updated until valid

