# Enhancement #53: GitHub Issue Integration for Session Start

**Issue**: [#53 - Fetch GitHub issue data on session start](https://github.com/Gerico1007/simexp/issues/53)

**Companion Issue**: [jgwill/EchoThreads#412 - Port issue-processor logic to Python for simexp integration](https://github.com/jgwill/EchoThreads/issues/412)

---

## Current State (v0.4.3)

**Main Branch**:
- Latest commit: `0fe0cdb Release: Version 0.4.3`
- Status: Clean working tree, up to date with origin/main
- Recent features:
  - #52: Initialize session with file content
  - #51: Add missing note_url parameter to SimplenoteWriter
  - #50: Configurable delay after metadata write

**Key Files**:
- `simexp/session_manager.py` - Session state management
- `simexp/simex.py` - Main CLI (103KB)
- `simexp/playwright_writer.py` - Simplenote writer
- `setup.py` - Package configuration (v0.4.3)

---

## Enhancement Overview

Add GitHub issue fetching to `simexp session start --issue <N>` command.

### User Story
```
As a developer working on GitHub issues,
I want to run: simexp session start --issue 53 --repo gerico1007/simexp
So that my session note is automatically contextualized with issue details
```

### Expected Behavior
1. User runs: `simexp session start --issue 53 --repo gerico1007/simexp`
2. Command fetches issue #53 from gerico1007/simexp
3. Creates Simplenote with:
   - Title: `Issue #53: Fetch GitHub issue data on session start`
   - Content includes: status, labels, assignees, description
4. Session is initialized and ready for work

---

## Implementation Plan

### Step 1: Create `simexp/github_issue.py`
New module with:
- `GitHubIssueFetcher` class
- Methods:
  - `fetch_issue(repo, issue_number)` - Fetch from GitHub
  - `format_for_session(issue_data)` - Format for Simplenote
  - `create_session_title(issue_data)` - Generate title

**Features**:
- Use `gh` CLI when available
- Fallback to GitHub REST API
- Graceful error handling

### Step 2: Modify `simexp/session_manager.py`
Update session initialization:
- Add `--issue` parameter support
- Add `--repo` parameter support
- Call `github_issue.fetch_issue()` when issue provided
- Format issue content and prepend to session

### Step 3: Modify `simexp/simex.py`
Update CLI:
- Add `--issue <N>` option to `session start`
- Add `--repo <owner/name>` option
- Auto-detect repo from git remote if in a repo

### Step 4: Update `setup.py`
- Increment version to 0.4.4
- No new dependencies needed (gh CLI is standard, requests already included)

---

## Files to Modify

| File | Changes |
|------|---------|
| `simexp/github_issue.py` | **NEW** - GitHub issue fetcher |
| `simexp/session_manager.py` | Add issue integration to session init |
| `simexp/simex.py` | Add CLI options for --issue and --repo |
| `setup.py` | Version bump to 0.4.4 |
| `README.md` | Add usage examples |

---

## Implementation Details

### CLI Usage Examples
```bash
# Explicit repo specification
simexp session start --issue 53 --repo gerico1007/simexp

# Auto-detect repo (if in a git repo)
simexp session start --issue 53

# With AI provider
simexp session start --issue 53 --ai claude

# Existing usage still works
simexp session start --ai gemini
```

### Session Note Format
```markdown
## Issue #53: Fetch GitHub issue data on session start

**Status**: `OPEN`
**Labels**: `enhancement`, `feature`
**Assignees**: gerico1007
**Created**: 2025-11-21T14:30:00Z
**Link**: https://github.com/Gerico1007/simexp/issues/53

### Description

Enable `simexp session start --issue <N>` to automatically fetch and
contextualize GitHub issue data within session notes.

...

---
### Session Notes

[user adds notes here]
```

---

## Testing Plan

### Unit Tests
- Test `GitHubIssueFetcher.fetch_issue()` with mock data
- Test `format_for_session()` with various issue types
- Test gh CLI detection and fallback

### Integration Tests
1. Create session with real GitHub issue:
   ```bash
   simexp session start --issue 53 --repo gerico1007/simexp
   ```
2. Verify:
   - Session note created with correct title
   - Issue data included in content
   - Session state saved correctly

3. Test with missing issue:
   ```bash
   simexp session start --issue 99999 --repo gerico1007/simexp
   ```
   - Should handle gracefully with error message

4. Test repo auto-detection:
   ```bash
   cd /path/to/gerico1007/simexp
   simexp session start --issue 53
   ```
   - Should auto-detect gerico1007/simexp from git remote

---

## Success Criteria

- ✅ `github_issue.py` module created and tested
- ✅ CLI accepts `--issue` and `--repo` parameters
- ✅ Issue data fetched and formatted correctly
- ✅ Session note created with issue context
- ✅ Backward compatible (existing usage still works)
- ✅ All tests passing
- ✅ Documentation updated with examples
- ✅ Version bumped to 0.4.4

---

## Branch Strategy

**Branch Name**: `53-github-issue-integration`

**Commits**:
1. Create `github_issue.py` module
2. Integrate issue fetching into session manager
3. Update CLI for --issue and --repo options
4. Update version to 0.4.4
5. Add documentation and examples

**PR Checklist**:
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Examples provided
- [ ] Cross-reference issue #412 in EchoThreads
- [ ] Ready to merge to main for 0.4.4 release

---

## Related Resources

**EchoThreads Reference**:
- Issue: [#412](https://github.com/jgwill/EchoThreads/issues/412)
- Plan: See `412ENHANCEMENT_PLAN.md`
- Code: `music/packages/gmusic-assembly/lib/issue-processor.js`

**simexp Current State**:
- Version: 0.4.3
- Latest: `0fe0cdb Release: Version 0.4.3`
- Repo: https://github.com/Gerico1007/simexp

---

**Created**: 2025-11-21
**Assembly**: ♠️🌿🎸🧵
