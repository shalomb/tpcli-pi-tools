Feature: End-to-End Integration Tests for PI Plan Sync

  Complete integration workflows testing the full bidirectional sync between
  TargetProcess and git for collaborative PI planning.

  Background:
    Given TargetProcess is accessible with valid API token
    And local git repository is initialized
    And ART "Data, Analytics and Digital" exists
    And Team "Platform Eco" belongs to ART
    And Release "PI-4/25" exists for ART
    And Release "PI-5/25" exists for ART

  Scenario: Complete workflow: init → edit → pull → push
    When user initializes plan tracking for team="Platform Eco" release="PI-4/25"
    Then tracking branch TP-PI-4-25-platform-eco is created and pushed
    And feature branch feature/plan-pi-4-25 is created and checked out
    And markdown file pi-4-25-platform-eco.md is committed with TP data
    And user is ready to edit plan

    When user edits objectives.md to update objective 2019099 effort 21→34
    And user commits with message "Refine Platform Governance objective"
    Then feature branch has 1 new commit

    When user pulls latest from TargetProcess
    And TP has no conflicting changes
    Then rebase completes cleanly
    And feature branch is updated with latest TP state

    When user pushes changes to TargetProcess
    Then TP API is called to update objective 2019099 with effort=34
    And tracking branch is updated with new markdown
    And feature branch remains ahead by 1 commit

  Scenario: Multi-objective sync with create and update
    Given user has initialized plan tracking for PI-4/25
    When user adds new objective "Security Initiative" to markdown
    And user updates existing objective 2019099 effort from 21→40
    And user commits both changes

    When user pushes to TargetProcess
    Then API call to create new TeamPIObjective is made
    And API call to update objective 2019099 is made
    And both operations succeed
    And tracking branch reflects new objective
    And user can see new objective ID in exported markdown

  Scenario: Conflict resolution workflow
    Given user has initialized plan tracking
    And user has local commit updating objective 2019099 effort to 40
    And another team member updated TP changing effort to 30

    When user pulls from TargetProcess
    Then rebase detects conflict in objectives.md
    And conflict markers show both versions (40 vs 30)
    And user can manually resolve

    When user keeps local version (40) and removes conflict markers
    And user stages resolved file
    And user continues rebase
    Then rebase completes
    And final result shows effort=40
    And feature branch is cleanly updated

  Scenario: Multiple teams, same PI, independent sync
    Given user is working on PI-4/25 for Platform Eco team
    When user initializes second tracking for team="Cloud Enablement" release="PI-4/25"
    Then second tracking branch TP-PI-4-25-cloud-enablement is created
    And two independent feature branches exist
    And Platform Eco objectives are independent from Cloud Enablement
    And both can sync independently

    When user edits and pushes Platform Eco changes
    Then Cloud Enablement sync is unaffected
    And Cloud Enablement can independently push without conflicts

  Scenario: Epic (Feature) lifecycle
    Given user initialized plan tracking for PI-4/25
    When user adds epic "Security Framework" under objective 2019099
    And user commits the change

    When user pushes to TargetProcess
    Then API call to create Feature is made
    And new feature is linked to objective 2019099
    And feature appears in exported markdown with TP ID

    When user edits epic effort from 8→13
    And user commits and pushes
    Then API call to update Feature is made
    And effort is updated in TargetProcess

  Scenario: Data integrity across sync cycles
    Given user has pushed PI-4/25 planning to TargetProcess
    And exported markdown contains all objectives and epics
    When user pulls again without making changes
    Then markdown is identical to previous export
    And no unexpected modifications appear
    And TP IDs are preserved

    When user makes change: update objective 2019099 name
    And user pulls, makes another change: update objective 2027963 status
    And user pushes both changes
    Then both changes are in TargetProcess
    And git history shows both commits
    And markdown metadata is preserved

  Scenario: Offline workflow: edit without network, sync later
    Given user has synchronized PI-4/25 to local repository
    When network becomes unavailable
    And user continues editing objectives locally
    And user commits multiple changes
    Then all commits are recorded locally
    And git history is complete

    When network becomes available
    And user pulls from TargetProcess
    Then pull succeeds (may have conflicts if TP changed)
    And local commits are preserved
    And user can push changes after resolving any conflicts

  Scenario: Large-scale sync: many objectives and epics
    Given PI-4/25 has 10 team objectives
    And each objective has 3-5 epics
    And total of 50+ entities to sync
    When user pulls from TargetProcess
    Then markdown file is generated with all 50+ entities
    And performance is acceptable (seconds, not minutes)
    And all entities are correctly represented

    When user edits 15 entities (mix of objectives and epics)
    And user pushes changes
    Then all 15 API calls are made correctly
    And TargetProcess is updated with all changes
    And no entities are missed

  Scenario: Concurrent users on same team, same PI
    Given alice and bob both work on PI-4/25 for Platform Eco
    And both have initialized tracking locally
    When alice pushes changes updating objective 2019099 name
    And bob pushes changes updating objective 2019099 effort
    Then alice's push succeeds first
    And bob's push detects change in TP
    And bob is notified to pull and resolve

    When bob pulls from TargetProcess
    Then pull gets alice's changes
    And bob's feature branch is rebased cleanly (non-overlapping edits)
    And both changes are preserved

    When bob pushes again
    Then both alice's and bob's changes are in TargetProcess
    And git history shows both commits

  Scenario: Plan refinement across multiple weeks
    When user initializes PI-4/25 planning (Week 1)
    And commits initial objectives
    And pushes to TargetProcess
    Then PI-4/25 is reflected in TargetProcess

    When user continues refinement (Week 2)
    And pulls latest from TP (other teams made changes)
    And updates objectives based on dependencies
    And pushes changes
    Then Week 2 changes are in TargetProcess
    And Week 1 planning is preserved

    When user finalizes planning (Week 3)
    And makes final adjustments
    And pushes to TargetProcess
    Then full planning history is in git
    And TargetProcess has final state
    And tracking branch shows evolution

  Scenario: Error recovery: failed push retry
    Given user has local changes ready to push
    When push attempt fails due to network error
    Then error is reported with actionable message
    And local changes are preserved
    And tracking branch is not modified

    When network recovers and user retries push
    Then push succeeds
    And changes are applied to TargetProcess

  Scenario: Validation errors prevent incorrect updates
    Given markdown has objective with missing required field
    When user attempts to push
    Then validation error is reported
    And user is shown which field is missing
    And no partial updates are made

    When user fixes markdown and retries
    Then push succeeds
    And TargetProcess has correct data

  Scenario: Revert and rollback capabilities
    Given user has pushed PI-4/25 changes to TargetProcess
    When user realizes mistake (created wrong epic)
    And user runs git revert <commit>
    And user pushes the revert
    Then revert commit is created
    And TargetProcess shows epic removed
    And full history is preserved for audit trail

  Scenario: Atomic operations: all-or-nothing
    Given user makes 5 changes to 5 different objectives
    When one change causes validation error in API
    Then push operation stops
    And none of the changes are applied
    And user can fix issue and retry
    And no partial updates occur

  Scenario: Performance: sync completes in reasonable time
    Given large PI with 100+ objectives and epics
    When user initializes tracking for large PI
    Then initialization completes in < 5 seconds
    And markdown file is generated correctly

    When user makes 20 edits and pushes
    Then push completes in < 10 seconds
    And all API calls are made successfully

    When user pulls with 30 changes from TP
    Then pull completes in < 5 seconds
    And rebase handles all changes correctly

  Scenario: Metadata preservation: YAML frontmatter consistency
    Given markdown file with YAML frontmatter
    When user pulls and pushes multiple times
    Then YAML frontmatter is preserved across cycles
    And release, team, art fields remain accurate
    And objectives array is updated correctly
    And synced_at timestamps reflect actual syncs

  Scenario: Cross-release planning
    Given user is planning both PI-4/25 and PI-5/25
    When user initializes tracking for PI-4/25
    And separately initializes tracking for PI-5/25
    Then both tracking branches exist independently
    And feature branches are separate
    And can work on both in parallel

    When user edits PI-4/25 and commits
    And edits PI-5/25 and commits
    And pushes both
    Then PI-4/25 updates go to PI-4/25 tracking
    And PI-5/25 updates go to PI-5/25 tracking
    And no cross-contamination occurs

