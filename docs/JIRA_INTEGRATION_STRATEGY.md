# Jira Integration: High-Level Strategy & User Stories

## Executive Intent

**Goal**: Provide users visibility into Jira story details without adding operational complexity or creating new system dependencies.

**Approach**: Three-phase rollout strategy that grows with user feedback:
- **MVP (Phase A)**: Read-only Jira links + acceptance criteria display
- **Phase B**: Direct Jira API integration for full story decomposition
- **Phase C**: Change attribution and conflict resolution enhancements

---

## Current Situation Analysis

### What TargetProcess Already Does

TargetProcess maintains **automatic bidirectional sync with Jira at the Feature level**:
- Features linked to Jira issues via Jira Key (e.g., `DAD-2652`)
- Automatic sync: Changes in Jira → reflected in TP (and vice versa) within seconds
- Metadata exposed via TP API:
  - Jira Key, Project, Priority, Issue Type
  - Acceptance Criteria (as HTML in CustomFields)
  - Status (synced with Jira status)
  - Dates (Start Date, Due Date)
  - URL back to Jira

### What TargetProcess Does NOT Expose

TP API limitations (cannot be bypassed without direct Jira API):
- **No story decomposition**: TP doesn't expose Jira's Epic → Stories → Sub-tasks tree
- **No story details**: Can't fetch individual story AC, status, or owners
- **No cross-dependencies**: Jira issue links not exposed in TP API
- **No story status tracking**: Only top-level Feature status, not individual stories

**Reality**: To show full story hierarchy, we MUST query Jira directly (not possible via TP alone).

---

## Phase A: MVP (2-3 days) - Read-Only Jira Links

### Intent
Get to market quickly with partial Jira visibility. Users can click through to Jira for details, removing friction from manual lookup.

### What Gets Delivered

**In Markdown Output**:
```markdown
### Epic: Semantic Versioning & CI/CD
- **TP ID**: 2018883
- **Jira Epic**: [DAD-2652](https://jira.takeda.com/browse/DAD-2652)
- **Owner**: Venkatesh Ravi
- **Status**: Analyzing
- **Effort**: 21 pts
- **Acceptance Criteria**:
  - CPU and memory limits configured at pod level
  - Alerting implemented for backend pods
  - Semantic versioning for Docker images
  - Unified branching strategy established

For detailed story decomposition, see [Jira Epic DAD-2652](link)
```

### How It Works

1. TP already provides Jira Key in CustomFields
2. MarkdownGenerator reads Jira Key from TP data
3. Formats it as clickable link: `[DAD-2652](https://jira.takeda.com/browse/DAD-2652)`
4. Cleans HTML acceptance criteria from TP CustomFields
5. Users click link to view full Jira story tree in browser

### User Stories (Phase A)

#### US-PA-1: Display Jira Epic Links in Markdown
**As a** planning manager
**I want** to see which TP features map to Jira epics
**So that** I can quickly navigate between systems

**Acceptance Criteria**:
- Jira Key appears in epic section (e.g., `[DAD-2652]`)
- Key is formatted as clickable link to Jira (using Jira URL template)
- Works for all features with Jira links
- Features without Jira links show gracefully (no errors, no broken links)

**Implementation**:
```python
# In MarkdownGenerator._epic_section()
if jira_key := epic.get('JiraKey'):
    link = f"[{jira_key}](https://jira.takeda.com/browse/{jira_key})"
    markdown += f"- **Jira Epic**: {link}\n"
```

---

#### US-PA-2: Display Acceptance Criteria from TP
**As a** team member planning
**I want** to see acceptance criteria in the markdown without switching systems
**So that** I have full context for scope discussions

**Acceptance Criteria**:
- Acceptance criteria from TP CustomField rendered as markdown list
- HTML entities decoded (&#44; → ,, &nbsp; → space)
- HTML tags stripped but structure preserved (lists, paragraphs)
- Handles missing/null AC gracefully
- Supports rich formatting (bold, italic, code)

**Implementation**:
```python
# In MarkdownGenerator._clean_html()
# Already implemented in Section 1.3
criteria_text = clean_html(epic.get('AcceptanceCriteria', ''))
if criteria_text:
    markdown += "- **Acceptance Criteria**:\n"
    for line in criteria_text.split('\n'):
        if line.strip():
            markdown += f"  - {line.strip()}\n"
```

---

#### US-PA-3: Note Directing Users to Jira for Stories
**As a** planner
**I want** clear indication that detailed stories are in Jira
**So that** I don't spend time looking for story details in markdown

**Acceptance Criteria**:
- Each epic section includes note like: "For detailed story decomposition, see [Jira DAD-2652](link)"
- Note appears at end of epic section
- Helps users understand system boundaries (TP shows epics, Jira shows stories)

**Implementation**:
```python
# In MarkdownGenerator._epic_section()
if jira_key:
    markdown += f"\n*For detailed story decomposition, see [Jira {jira_key}]"
    markdown += f"(https://jira.takeda.com/browse/{jira_key})*\n"
```

---

#### US-PA-4: Handle Missing/Invalid Jira Keys Gracefully
**As a** system
**I want** to not break when Jira Key is missing or invalid
**So that** users with unlinked features get usable output

**Acceptance Criteria**:
- Features without Jira Key still render in markdown
- No error messages, no broken links
- AC section still appears (if available)
- User can manually link to Jira if needed

---

### Why Phase A Works

✅ **Low complexity**: Uses existing TP data (no new API calls)
✅ **Fast to implement**: 2-3 days (mostly already done in Section 1.3)
✅ **No new dependencies**: No Jira API credentials needed
✅ **Clear boundaries**: Users understand story data is in Jira
✅ **Gathers feedback**: Can measure Jira link click-through rates
✅ **MVP ready**: Solves core need without overengineering

---

## Phase B: Direct Jira API Integration (3-5 days) - Post-MVP

### Intent
Based on Phase A feedback, add story decomposition directly in markdown. Users can see full tree without context-switching.

### What Gets Delivered

**Enhanced Markdown Output**:
```markdown
### Epic: Semantic Versioning & CI/CD
- **TP ID**: 2018883
- **Jira Epic**: [DAD-2652](https://jira.takeda.com/browse/DAD-2652)
- **Status**: Analyzing
- **Effort**: 21 pts

#### Story: Set up pod resource limits
- **Key**: [DAD-2653](https://jira.takeda.com/browse/DAD-2653)
- **Status**: In Progress
- **Assignee**: Alice Chen
- **Story Points**: 5
- **Acceptance Criteria**:
  - Memory limit: 512MB
  - CPU limit: 250m
  - Tests pass in staging

#### Story: Implement alerting rules
- **Key**: [DAD-2654](https://jira.takeda.com/browse/DAD-2654)
- **Status**: To Do
- **Assignee**: Bob Kumar
```

### How It Works

1. User provides Jira API credentials (in tpcli config)
2. On `tpcli plan pull`:
   - Fetch TP objectives/epics (as before)
   - For each epic with Jira Key, query Jira for child stories
   - Fetch story details (title, status, assignee, AC, points)
3. Generate markdown with nested story sections (H4 level)
4. Users get full context in single markdown file
5. On `tpcli plan push`: Only epics are synced back (stories stay in Jira)

### User Stories (Phase B)

#### US-PB-1: Fetch Stories from Jira API
**As a** planner
**I want** to see Jira stories directly in the markdown plan
**So that** I have full scope context without context-switching

**Acceptance Criteria**:
- Stories appear as H4 subsections under epics
- Each story shows: Key (linked), Status, Assignee, Story Points
- Stories ordered by Jira Issue Key
- Works with Jira API token (stored in tpcli config)
- Handles API rate limits gracefully

---

#### US-PB-2: Display Story Acceptance Criteria
**As a** team member
**I want** to see story-level AC in the markdown
**So that** I understand detailed scope

**Acceptance Criteria**:
- Story AC from Jira rendered in markdown
- Formatted same as epic AC (lists, etc.)
- Empty AC handled gracefully

---

#### US-PB-3: Handle Story Status Changes
**As a** planner
**I want** to see story status from Jira (To Do, In Progress, Done, etc.)
**So that** I can track overall progress

**Acceptance Criteria**:
- Story status displayed (e.g., `- **Status**: In Progress`)
- Status in markdown is read-only (not synced back to Jira)
- On pull, latest story status is fetched

---

#### US-PB-4: Manage Jira Credentials
**As a** user
**I want** to store Jira API token securely
**So that** plan sync can authenticate with Jira API

**Acceptance Criteria**:
- Jira token stored in tpcli config (same as TP token)
- Token passed via environment variable or config file
- Token NOT logged or printed
- Clear error if token is missing or invalid

---

### Trade-offs of Phase B

⚠️ **Added complexity**:
- Now syncing 3 systems (Git ← TP ← Jira)
- More potential failure points
- Jira API rate limits can slow down pulls

⚠️ **Conflict resolution harder**:
- If story data changes in Jira while user is editing markdown, merge conflicts possible
- Must decide: user edit wins, or Jira change wins?

⚠️ **Implementation effort**: 3-5 days

✅ **But solves real problem**: Users don't have to switch to Jira constantly

---

## Phase C: Change Attribution & Conflict Resolution (TBD)

### Intent (Not Phase A - Deferred)
Help users understand:
- When Jira last synced with TP
- Which changes came from Jira vs user edit
- How to resolve conflicts between systems

### Concepts (Not Implemented Yet)
- Track sync timestamps for each story/epic
- Detect if change came from Jira or user
- Smarter merge conflict hints
- Audit trail of all sync operations

---

## Recommended Rollout

### Timeline

**Week 1**: Phase A (MVP)
- Implement Jira link display (2-3 days)
- Deploy to test environment
- Gather user feedback (3-4 days)

**Week 2+**: Phase B (if justified by feedback)
- Implement direct Jira API integration (3-5 days)
- Add story decomposition
- Deploy to production

### Success Metrics

**Phase A**:
- [ ] All Jira links render correctly
- [ ] Click-through rate tracked (analytics)
- [ ] User feedback on whether they need story decomposition

**Phase B** (if pursued):
- [ ] Stories appear in markdown
- [ ] No Jira API rate limit issues
- [ ] Merge conflicts rare (<5% of pulls)
- [ ] User satisfaction with story visibility improved

---

## Decision Questions for the Team

1. **MVP Scope**: Should we stop at Phase A (links only) or commit to Phase B eventually?

2. **Jira Credentials**: How should users securely store Jira tokens?
   - Environment variable?
   - Local tpcli config?
   - GitHub Secrets (if automating)?

3. **Story Read-Only**: Should stories be truly read-only (no markdown edits), or allow user edits with back-sync?

4. **Scope Creep**: Any other Jira data that's critical for planning?
   - Custom fields?
   - Labels/Tags?
   - Linked issues (dependencies)?

5. **Feedback Loop**: How do we measure if users actually need Phase B?
   - Usage analytics?
   - User surveys?
   - Support ticket tracking?

---

## Implementation Checklist

### Phase A (MVP - Ready to Start)
- [ ] Modify `MarkdownGenerator` to include Jira Key from TP data
- [ ] Add clickable link formatting (already partial in Section 1.3)
- [ ] Add "See Jira for details" note
- [ ] Test with real TP data containing Jira keys
- [ ] Update BDD scenarios in `markdown_generation.feature`
- [ ] Gather metrics on Jira link usage

### Phase B (Post-MVP - Deferred)
- [ ] Add Jira API client to tpcli (new module)
- [ ] Modify `GitPlanSync.pull()` to fetch Jira stories
- [ ] Update `MarkdownGenerator` for H4 story sections
- [ ] Handle Jira API errors gracefully
- [ ] Add Jira token to tpcli config
- [ ] Test with real Jira instances
- [ ] Update documentation

---

## Key Design Principles

1. **TargetProcess is Source of Truth**: We pull from TP, not Jira directly
2. **Read-Only Stories**: User edits epics in markdown; stories edited in Jira
3. **No Implicit Sync**: TP ↔ Jira sync is automatic (Takeda manages it); we just read TP
4. **Graceful Degradation**: Missing Jira keys don't break markdown rendering
5. **User Control**: Users can choose to enable/disable Jira integration

---

## Summary for Decision Makers

| Aspect | Phase A | Phase B |
|--------|---------|---------|
| **Timeline** | 2-3 days | 3-5 days (after feedback) |
| **Complexity** | Low | Medium |
| **MVP Ready** | Yes | No |
| **User Satisfaction** | ~70% | ~95% |
| **Risk** | Low | Medium |
| **Implementation Effort** | Low | Medium |
| **Operational Burden** | None | Jira API dependency |
| **Recommended** | Do it for MVP | Do if user feedback justifies |
