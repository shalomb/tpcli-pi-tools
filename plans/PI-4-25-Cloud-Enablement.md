---
title: PI-4/25 Planning Export - Cloud Enablement & Delivery
team: Cloud Enablement & Delivery
team_id: 2022903
art: Data, Analytics and Digital
generated: 2025-01-03
source: TargetProcess + Jira Integration (Exploration-Driven Fixtures)
---

# PI-4/25 Plan: Cloud Enablement & Delivery

**Team:** Cloud Enablement & Delivery
**ART:** Data, Analytics and Digital
**Owner:** Norbert Borský
**Members:** 8

---

## Team Objectives (3 committed, 3 pending elsewhere)

### 1. Enable MSK repeatable deployments

- **Status:** In Progress
- **Commitment:** ✓ COMMITTED
- **Effort:** 21 points (refined from exploration)
- **ID:** TP-2029314
- **Owner:** Alice Chen (Cloud Infrastructure)
- **Description:** Establish repeatable deployment patterns for Amazon MSK with terraform and helm charts

### 2. Prove an Observability Pattern for CIM

- **Status:** In Progress
- **Commitment:** ✓ COMMITTED
- **Effort:** 13 points
- **ID:** TP-2030101
- **Description:** Validate observability patterns for Cloud Integration Mesh

### 3. Optimize RDS Resources for dev/test workloads

- **Status:** In Progress
- **Commitment:** ✓ COMMITTED
- **Effort:** 13 points
- **ID:** TP-2030144
- **Description:** Reduce RDS costs and optimize resource allocation for non-production

**Total Objective Effort:** 47 points

---

## Jira Epics & Features

### DAD-2790: Amazon Workspace Applications Building Block

**Related TP Feature:** Amazon Workspace Applications Building Block (Appstream 2.0)
**TP ID:** 2029239
**Status:** Funnel
**Effort:** 0 points

**Description:** Building block for AWS AppStream 2.0 based workspace applications enabling remote access and desktop virtualization for cloud enablement platform.

**Acceptance Criteria:**
- [x] AppStream 2.0 baseline configuration deployed (Jan 1)
- [x] Multi-user session management tested (Jan 2)
- [ ] Performance benchmarks meet requirements (target: 100ms response)
- [ ] Cost optimization analyzed (target: <$500/month for dev)
- [ ] Documentation complete with runbooks

---

### DAD-2789: Infrastructure as Code Runtime Environment - FY25Q4

**Related TP Feature:** Infrastructure as Code Runtime Environment - FY25Q4
**TP ID:** 2029238
**Status:** Funnel
**Effort:** 0 points

**Description:** Enhance and standardize IaCRE tooling for Q4 FY25, improving infrastructure deployment automation and consistency.

**Acceptance Criteria:**
- [ ] Q4 enhancements implemented
- [ ] Documentation updated
- [ ] Team training completed
- [ ] Deployment success rate > 99%

---

### DAD-2772: Amazon MSK Building Block

**Related TP Feature:** Amazon MSK Building Block
**TP ID:** 2024762
**Status:** Funnel
**Effort:** 0 points

**Description:** Create building block for Amazon Managed Streaming for Kafka (MSK) integration into cloud platform.

**Acceptance Criteria:**
- [ ] MSK cluster provisioning automated
- [ ] Topic management templates created
- [ ] Security policies validated
- [ ] Monitoring dashboards configured

---

### DAD-375: RDS Resources Optimization

**Related TP Feature:** RDS resources optimization for dev and test workloads
**TP ID:** 1940304
**Status:** Backlog
**Effort:** 13 points

**Description:** Optimize RDS resource allocation and reduce costs for development and test environments without impacting performance.

**Acceptance Criteria:**
- [ ] 20% cost reduction achieved
- [ ] Performance metrics maintained (< 5ms p95 latency)
- [ ] Automated scaling policies implemented
- [ ] Monitoring alerts configured

---

## Team Workload Summary

| Category | Count | Effort |
|----------|-------|--------|
| Committed Objectives | 3 | 47 |
| Features in Scope | 4 | 13+ |
| Jira Epics Mapped | 4 | TBD |
| Total Team Effort | 7+ items | 60+ |

---

## Sync Status

- **Last TP Sync:** 2025-01-03 12:00 UTC
- **Last Jira Sync:** 2025-01-03 12:00 UTC
- **Jira Coverage:** 100% (all features mapped)
- **Sync Tool:** tpcli + Jira API v3
- **Branch:** feature/pi-4-25-planning

---

## Notes & Decisions

### Data Source
This plan is generated from real TargetProcess and Jira data using the exploration-driven fixture pattern:
1. Queried TP for Team #2022903 structure
2. Extracted 18 features, 6 objectives from real portfolio
3. Mapped to Jira DAD project epics
4. Generated safe, anonymized test fixtures
5. Created git-native markdown plan

### Editable Format
This file is version-controlled in git and can be edited locally:
- Update effort estimates
- Modify acceptance criteria
- Add/remove features
- Track changes via git diff
- Sync back to TP/Jira

### Next Steps
- [ ] Team review and refinement
- [ ] Effort estimation refinement
- [ ] Dependency mapping
- [ ] Risk assessment
- [ ] Commit to feature branch
- [ ] Create PR for main merge

---

*Generated from exploration-driven fixtures. All data is anonymized and safe for version control.*
