# TODO: tpcli - Quality & Hygiene Focused

**Status**: MVP Feature-Complete, Quality Focus
**Current**: 406 tests passing, 54% coverage, monitoring/resilience added
**Priority**: Test coverage, docs, code quality

---

## Phase A: Essential Quality & Hygiene

### A.1: Test Coverage & Quality
- [ ] Increase coverage to 70%+ (currently 54%)
  - [ ] Cover git_integration.py edge cases
  - [ ] Cover api_client.py error paths
  - [ ] Cover markdown_generator.py all scenarios
  - [ ] Add integration tests for pull/push workflows
- [ ] Add type hints to all Python code
- [ ] Run mypy and fix type issues
- [ ] Clean up any unused imports/code
- [ ] Add docstring coverage

### A.2: Code Quality & Polish
- [ ] Improve error messages (make them actionable)
- [ ] Add logging to critical paths
- [ ] Refactor any complex functions (>20 lines)
- [ ] Remove any hardcoded values
- [ ] Consistent code style (black, isort)

### A.3: Documentation Quality
- [ ] Update PRD status from "Draft" to "Approved"
- [ ] Create TROUBLESHOOTING.md with common issues
- [ ] Add examples to PROJECT-README.md
- [ ] Document all CLI flags and options
- [ ] Create DEVELOPMENT.md for contributors

### A.4: CLI Polish
- [ ] Improve help text for all commands
- [ ] Add verbose/quiet flags where useful
- [ ] Add confirmation prompts for destructive ops (push)
- [ ] Better progress indicators for long operations
- [ ] Consistent output formatting

### A.5: Git Integration Testing
- [ ] Test with real git repos (not just mocks)
- [ ] Test merge conflict scenarios
- [ ] Test with large plans (100+ objectives)
- [ ] Test concurrent access scenarios
- [ ] Document git workflow assumptions

### A.6: Config & Secrets
- [ ] Validate config file on load
- [ ] Add config validation tests
- [ ] Document credential security
- [ ] Add config initialization command (tpcli config init)
- [ ] Handle missing credentials gracefully

---

## Phase B: MVP Ready Checklist

### B.1: Before Pilot
- [ ] Run full test suite (406 tests)
- [ ] Verify coverage is 70%+
- [ ] Test on fresh machine (not just dev env)
- [ ] Test with real TP instance
- [ ] Create RELEASE_NOTES for v1.0
- [ ] Tag release: v1.0.0

### B.2: Pilot Handoff
- [ ] User guide (quick-start + workflows)
- [ ] Installation instructions
- [ ] Known limitations document
- [ ] How to report bugs
- [ ] Support contact info

### B.3: Bug Fixes (As Found)
- [ ] Track bugs from pilot
- [ ] Fix critical issues
- [ ] Document workarounds
- [ ] Update docs with lessons learned

---

## NOT Doing (Explicitly)

These are nice-to-have but out of scope for MVP:

- ❌ Load testing (can do manually if needed)
- ❌ Operational runbooks (too early)
- ❌ Backup/rollback (git handles this)
- ❌ Bulk operations (v2 feature)
- ❌ Templates/approval workflows (v2 feature)
- ❌ GitHub/Slack integration (v2 feature)
- ❌ Enterprise scale features (v3+)

---

## Quick Reference

### What We Have
✅ Core bidirectional sync (TP ↔ Git ↔ TP)
✅ 3-way merge conflict handling
✅ Jira integration (links + stories)
✅ Monitoring & resilience infrastructure
✅ 406 passing tests
✅ Full documentation

### What We Need
- ⚠️ Higher test coverage (70%)
- ⚠️ Better error messages
- ⚠️ Type hints throughout
- ⚠️ Real-world testing
- ⚠️ User-facing docs

---

## Success Criteria for MVP

- [ ] 70%+ test coverage
- [ ] Zero critical bugs found in pilot
- [ ] Users can pull/push without manual intervention
- [ ] Conflicts detected and shown clearly
- [ ] Docs are clear enough for first-time user
- [ ] No credentials leaked or exposed
- [ ] Git history is clean and useful

---

## Done When

1. All A.1-A.6 tasks checked off
2. Coverage is 70%+
3. Types are clean (mypy passes)
4. Docs are complete
5. Ready for v1.0.0 release tag
