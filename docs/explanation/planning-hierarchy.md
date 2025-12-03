TEAM PLANNING HIERARCHY - HOW IT WORKS
══════════════════════════════════════════════════════════════════════════════

THE PLANNING FLOW
─────────────────

Program (ART)
 │
 └─→ Program Objective
      "Enable MSK for all services"
      Effort: 50 points
      Owner: ART PM
      │
      └─→ Team Objectives (commitments)
           ├─ Cloud Enablement: "Enable MSK repeatable deployments" (21 pts)
           ├─ Data Platform: "MSK data integration" (13 pts)
           └─ Security: "MSK compliance & monitoring" (16 pts)
           │
           └─→ Features (implementation)
                ├─ "Amazon MSK Building Block" (13 pts)
                ├─ "MSK Topic Management Templates" (8 pts)
                └─ "MSK Security Policies" (5 pts)
                │
                └─→ Stories (execution)
                     ├─ Story: "Set up MSK cluster in dev"
                     ├─ Story: "Configure topic auto-creation"
                     └─ Story: "Add monitoring to topics"


HOW TEAMS USE THIS
──────────────────

Team Lead (Cloud Enablement)
  "What is our team committed to this PI?"
     ↓
  SCRIPT: team-objectives
     ↓
  Output: List of team objectives for PI-4/25
     - "Enable MSK repeatable deployments" (21 pts) [In Progress]
     - "Prove observability pattern for CIM" (13 pts) [Not Started]
     - "Optimize RDS for dev/test" (13 pts) [In Progress]


Team Lead wants to understand the work
  "What features are we building to achieve this?"
     ↓
  SCRIPT: team-features
     ↓
  Output: Features assigned to Cloud Enablement team
     - Objective: "Enable MSK repeatable deployments" [21 pts]
       ├─ Feature: "Amazon MSK Building Block v1.0" [13 pts]
       └─ Feature: "Amazon MSK Terraform templates" [8 pts]
     
     - Objective: "Prove observability pattern" [13 pts]
       └─ Feature: "Splunk Logs Building Block" [13 pts]


Team Lead wants quick status
  "What's my team's health at a glance?"
     ↓
  SCRIPT: team-dashboard
     ↓
  Output: Team snapshot
     ┌──────────────────────────────────────┐
     │ Cloud Enablement & Delivery Team     │
     │                                      │
     │ Objectives:        3 committed       │
     │ Features:          4 features        │
     │ Total Effort:      47 points         │
     │ Capacity:          40 points/PI      │
     │ Utilization:       117% ⚠️            │ ← OVER COMMITTED!
     │ Risks:             2 high, 1 critical
     │ Blockers:          3 dependencies    │
     │ Health:            45/100 (Red)      │
     └──────────────────────────────────────┘


Product Owner wants to break down the objective
  "What makes up this objective?"
     ↓
  SCRIPT: team-features
     Input: --objective "Enable MSK repeatable deployments"
     ↓
  Output: Features for that specific objective
     - Feature: "Amazon MSK Building Block v1.0" [13 pts]
       Status: In Progress
       Owner: Shalom Israel Bhooshi
       Acceptance Criteria:
         ✓ MSK cluster provisioning automated
         ✓ Topic management templates created
         ☐ Security policies validated
         ☐ Monitoring dashboards configured
     
     - Feature: "Amazon MSK Terraform templates" [8 pts]
       Status: Backlog
       Owner: Alice Chen
       Acceptance Criteria:
         ☐ IaC patterns documented
         ☐ CI/CD integration tested


Capacity Planner wants to know available bandwidth
  "How much more work can the team take?"
     ↓
  SCRIPT: team-capacity
     ↓
  Output: Team capacity analysis
     ┌─────────────────────────────────────┐
     │ Team Capacity Analysis              │
     │                                     │
     │ Total PI Capacity:     40 points    │
     │ Committed Objectives:  47 points    │ ← Over by 7 points
     │ Available:             -7 points    │
     │ Utilization:           117%         │
     │ Status:                ⚠️ OVER      │
     │                                     │
     │ Recommendation: Reduce commitments  │
     │ Or: Increase team capacity          │
     │ Or: Defer lower priority items      │
     └─────────────────────────────────────┘


Program Manager wants to see the whole program
  "Which teams are working on what objectives?"
     ↓
  SCRIPT: pi-objectives
     Input: --pi "PI-4/25"
     ↓
  Output: Program objectives broken down by team
     Program Objective: "Enable MSK for all services" [50 pts]
     ├─ Cloud Enablement Team
     │  └─ Commitment: "Enable MSK repeatable deployments" [21 pts]
     │     Status: In Progress | Health: 65/100 (Yellow)
     │     Features: 2 features, 1 complete
     │
     ├─ Data Platform Team
     │  └─ Commitment: "MSK data integration" [13 pts]
     │     Status: Not Started | Health: 40/100 (Red) ⚠️
     │     Features: 1 feature, 0 complete
     │
     └─ Security Team
        └─ Commitment: "MSK compliance & monitoring" [16 pts]
           Status: Backlog | Health: 30/100 (Red) ⚠️
           Features: 2 features, 0 complete
     
     Overall Program Status: 47% Complete | Health: 45/100 (Red)


Program Manager wants to see which PIs are coming
  "What's on the roadmap?"
     ↓
  SCRIPT: pi-list
     ↓
  Output: Timeline of upcoming work
     Current: PI-4/25
       Start: 2025-01-08 | End: 2025-02-19 (43 days)
       Teams: 8 teams | Objectives: 24 objectives
       Status: In Progress
     
     Upcoming: PI-4/26
       Start: 2025-02-20 | End: 2025-04-02 (42 days)
       Teams: 8 teams | Objectives: 26 objectives
       Status: Planning
     
     Upcoming: PI-4/27
       Start: 2025-04-03 | End: 2025-05-15 (42 days)
       Teams: 8 teams | Objectives: 22 objectives
       Status: Backlog


Program Manager wants to see program-level risks
  "What could derail the program?"
     ↓
  SCRIPT: pi-risks
     Input: --pi "PI-4/25"
     ↓
  Output: Aggregated program risks
     ┌─────────────────────────────────────┐
     │ Program Risk Summary: PI-4/25       │
     │                                     │
     │ Critical Risks: 3                   │
     │ High Risks: 7                       │
     │ Medium Risks: 12                    │
     │ Program Health: 40/100 (Red)        │
     │                                     │
     │ Top 3 Risks:                        │
     │ 1. Data Platform over-committed     │
     │    (117% capacity utilization)      │
     │    Teams affected: 2                │
     │    Mitigation: Descope features     │
     │                                     │
     │ 2. MSK integration blocked on       │
     │    Schema Registry work (Team B)    │
     │    Critical path risk: HIGH         │
     │    Mitigation: Parallel approach    │
     │                                     │
     │ 3. Compliance review delayed        │
     │    Target: Feb 15                   │
     │    At Risk: -5 days                 │
     │    Mitigation: Pre-review content   │
     └─────────────────────────────────────┘


SCRIPT USAGE MATRIX
───────────────────

Role                  | Script           | Frequency | Use Case
─────────────────────────────────────────────────────────────────────────────
Team Lead            | team-dashboard   | Daily     | Team health check
                     | team-objectives  | Weekly    | What are we doing?
                     | team-features    | Weekly    | How do we do it?
                     | team-risks       | Daily     | What's threatening us?
                     | team-dependencies| Weekly    | Who do we depend on?

Product Owner        | team-objectives  | Daily     | Requirements
                     | team-features    | Daily     | Work breakdown
                     | pi-objectives    | Weekly    | Program alignment

Capacity Planner     | team-dashboard   | Weekly    | Capacity check
                     | team-capacity    | Weekly    | Bandwidth available?

Program Manager      | pi-list          | Weekly    | Roadmap
                     | pi-status        | Weekly    | Progress
                     | pi-objectives    | Weekly    | Team alignment
                     | pi-risks         | Weekly    | Program health
                     | pi-dependencies  | Weekly    | Critical path

Executive            | art-dashboard    | Monthly   | ART health
                     | pi-list          | Monthly   | Timeline
                     | pi-risks         | Monthly   | Health/risks


THE INFORMATION HIERARCHY
─────────────────────────

High-level (Executive)
  └─ ART Dashboard      (all ARTs, all teams, all objectives)
  └─ PI List            (timeline, counts, status)
  └─ PI Risks           (aggregated program health)
  └─ PI Dependencies    (critical path)

Mid-level (Program Manager)
  └─ PI Status          (progress, blockers)
  └─ PI Objectives      (which teams work on what)
  └─ PI Dependencies    (team-level blockers)

Team-level (Team Lead)
  └─ Team Dashboard     (team snapshot)
  └─ Team Objectives    (commitments)
  └─ Team Features      (implementation)
  └─ Team Capacity      (bandwidth)
  └─ Team Risks         (health)
  └─ Team Dependencies  (blockers)

Detail-level (Team Member)
  └─ Team Features      (my feature context)
  └─ Feature Stories    (my stories) [FUTURE]
  └─ Feature Analysis   (status, dependencies) [FUTURE]

═══════════════════════════════════════════════════════════════════════════════
