# Four Directions Session Tracking Enhancement

**Issue:** #55
**Branch:** `55-four-directions-enhancement`
**Target Version:** 0.5.0
**PR:** TBD

---

## Enhancement Definition

The Four Directions enhancement transforms **simexp** from a simple file-capture tool into a **ceremonial session tracking system** that honors Indigenous wisdom traditions while providing comprehensive development lifecycle documentation.

### Core Concept

Sessions move through four cardinal directions:

```
         🌅 EAST (Intention)
              ↓
    🌱 SOUTH (Growth) ← → 🌄 WEST (Publishing)
              ↓
         🌐 NORTH (Reflection)
```

Each direction captures specific session metadata:
- **East:** Vision statement, goals, intention
- **South:** Files added, content written, collaborators, growth events
- **West:** Publication status, public URLs, external visibility
- **North:** Reflections, observed patterns, extracted wisdom, completion seeds

### Business Value

1. **Complete Lifecycle Documentation** - Sessions become auditable records
2. **Ceremonial Alignment** - Technology honors Indigenous teaching frameworks
3. **Wisdom Extraction** - Sessions capture and preserve learning
4. **Pattern Recognition** - Data enables future AI analysis
5. **Team Coordination** - Metadata supports collaboration tracking

---

## Implementation Phases

### Phase 0: Preparation (Ceremonial Foundation)
**Goal:** Set clear intention before building

**Tasks:**
- ✅ Create GitHub issue #55
- ✅ Document specifications
- ✅ Commit spec documents to main
- Create feature branch `55-four-directions-enhancement`
- Declare implementation intention

**Completion Criteria:**
- Issue created and linked to specs
- Branch created and checked out
- Team alignment verified

---

### Phase 1: Core Data Infrastructure
**Goal:** Build foundation functions for Four Directions tracking

**Files Modified:**
- `simexp/session_manager.py`

**Functions to Add:**
```python
initialize_four_directions_session(session_data: dict) -> dict
  - Create new session with Four Directions structure
  - Initialize east, south, west, north dictionaries
  - Set creation timestamp

update_session_data(direction: str, action_type: str, action_data: dict) -> None
  - Append action to direction.action_type array
  - Update session.json atomically
  - Recalculate stats

calculate_session_stats(session: dict) -> dict
  - Count files by direction
  - Count writes, collaborators
  - Calculate session duration
  - Determine completion percentage

migrate_legacy_session(session: dict) -> dict
  - Convert old session.json format to new
  - Preserve existing data
  - Initialize missing directions
```

**Session Structure (New):**
```json
{
  "session_id": "uuid",
  "search_key": "uuid",
  "created_at": "2025-11-23T...",

  "east": {
    "vision_statement": "optional intention text",
    "goals": []
  },

  "south": {
    "files_added": [
      {
        "timestamp": "2025-11-23T...",
        "path": "/absolute/path",
        "filename": "name.md",
        "heading": "optional",
        "content_type": "markdown",
        "size_chars": 1234,
        "direction": "south"
      }
    ],
    "content_written": [
      {
        "timestamp": "2025-11-23T...",
        "content_length": 500,
        "mode": "append",
        "prepend": false,
        "has_timestamp": true
      }
    ],
    "collaborations": [
      {
        "timestamp": "2025-11-23T...",
        "collaborator_email": "user@example.com",
        "action": "added"
      }
    ]
  },

  "west": {
    "published": false,
    "published_at": null,
    "public_url": null,
    "opened_in_browser": []
  },

  "north": {
    "reflection_notes": [],
    "observed_patterns": [],
    "extracted_wisdom": [],
    "completed": false,
    "completed_at": null,
    "seeds_for_next": []
  },

  "stats": {
    "total_files": 0,
    "total_writes": 0,
    "total_collaborators": 0,
    "session_duration_days": 0,
    "completion_percentage": 0
  }
}
```

**Testing:**
- Unit tests for each new function
- Verify structure creation
- Verify migration compatibility
- Stats calculation accuracy

**Acceptance Criteria:**
- All functions implemented
- Unit tests passing
- Manual verification complete

---

### Phase 2: South Direction - File Tracking
**Goal:** Capture comprehensive file addition metadata

**Files Modified:**
- `simexp/session_manager.py` - `handle_session_add()`
- `simexp/simex.py` - `session_add_command()`

**Changes:**
1. Modify `handle_session_add()` to:
   - Call `update_session_data('south', 'files_added', {...})`
   - Pass: path, filename, timestamp, heading, content_type, size_chars

2. Add `--direction` flag to CLI:
   ```bash
   simexp session add file.md --direction south --heading "Chapter 1"
   simexp session add intentions.md --direction east
   ```

3. Direction choices: `east`, `south`, `west`, `north` (default: south)

**Testing:**
- Add multiple files with different directions
- Verify metadata in session.json
- Check stats calculation

**Acceptance Criteria:**
- Files tracked with full metadata
- Direction flag working
- Tests passing

---

### Phase 3: South Direction - Write & Collaboration
**Goal:** Track content writes and collaboration events

**Files Modified:**
- `simexp/simex.py` - `session_write_command()`
- `simexp/session_sharing.py` - `add_session_collaborator()`

**Changes:**
1. Modify `session_write_command()`:
   - Call `update_session_data('south', 'content_written', {...})`
   - Capture: timestamp, content_length, mode, prepend flag

2. Modify `add_session_collaborator()`:
   - Call `update_session_data('south', 'collaborations', {...})`
   - Capture: timestamp, collaborator_email, action

**Testing:**
- Write content multiple times
- Add collaborators
- Verify accumulated data

**Acceptance Criteria:**
- Writes tracked with metadata
- Collaborations tracked
- Stats updated correctly

---

### Phase 4: West Direction - Publication Tracking
**Goal:** Track publication and external visibility

**Files Modified:**
- `simexp/simex.py` - `session_publish_command()`, `session_open_command()`

**Changes:**
1. Modify `session_publish_command()`:
   - Set `west.published = True`
   - Set `west.published_at = timestamp`
   - Set `west.public_url = url`

2. Modify `session_open_command()`:
   - Append to `west.opened_in_browser[]`
   - Record timestamp

**Testing:**
- Publish session and verify West data
- Open in browser and verify tracking

**Acceptance Criteria:**
- Publication tracked
- Browser opens tracked
- West direction complete

---

### Phase 5: North Direction - Reflection Commands (NEW)
**Goal:** Add ceremonial completion and wisdom extraction

**Files to Create/Modify:**
- `simexp/simex.py` - new command handlers

**New Commands:**
```bash
simexp session reflect [--prompt "What did we learn?"]
simexp session observe-pattern "Pattern description"
simexp session extract-wisdom "Wisdom text"
simexp session complete [--seeds "seed1, seed2"]
```

**Implementation Details:**

1. **`session_reflect_command(prompt=None, cdp_url=None)`**
   - Open editor (nano/vim/$EDITOR)
   - Pre-populate with prompt if provided
   - Save reflection to `north.reflection_notes[]`
   - Update session.json

2. **`session_observe_pattern_command(pattern: str)`**
   - Append pattern to `north.observed_patterns[]`
   - Update session.json

3. **`session_extract_wisdom_command(wisdom: str)`**
   - Append wisdom to `north.extracted_wisdom[]`
   - Update session.json

4. **`session_complete_command(seeds=None)`**
   - Set `north.completed = True`
   - Set `north.completed_at = timestamp`
   - Parse and store seeds in `north.seeds_for_next[]`
   - Calculate final stats
   - Print completion summary

5. **`print_completion_summary(session: dict)`**
   - Display ceremonial completion output
   - Show Four Directions journey
   - Display seeds for next cycle

**Completion Summary Format:**
```
♠️🌿🎸🧵 Session Completion Summary
🔮 Session: [ID]
📅 Duration: X days
📁 Files: N
👥 Collaborators: N
✍️ Writes: N
🌐 Published: Yes/No

🧭 Four Directions Journey:
   🌅 EAST: Intention declared
   🌱 SOUTH: Growth achieved (X files, Y collaborators)
   🌄 WEST: Published and shared
   🌐 NORTH: Wisdom integrated

🌀 Seeds for Next Spiral:
   - seed 1
   - seed 2

✅ Ceremonial circle complete!
```

**Testing:**
- Editor integration works
- Patterns recorded
- Wisdom captured
- Completion marked
- Summary displays correctly

**Acceptance Criteria:**
- All North commands implemented
- Editor integration functional
- Completion summary beautiful
- Tests passing

---

### Phase 6: Enhanced Session Start
**Goal:** Capture explicit intention at session creation

**Files Modified:**
- `simexp/simex.py` - `session_start_command()`

**Changes:**
- Add `--intention` flag to CLI
- Store in `east.vision_statement`

**Usage:**
```bash
simexp session start --ai claude --issue 42 --intention "Prepare Winter Solstice materials"
```

**Testing:**
- Start session with intention
- Verify stored in East direction

**Acceptance Criteria:**
- Intention captured at start
- Stored in East direction

---

### Phase 7: Session Info Enhancement
**Goal:** Display Four Directions status in session info

**Files Modified:**
- `simexp/simex.py` - `session_info_command()`

**Enhanced Output:**
```
♠️🌿🎸🧵 Current Session Info
🔮 Session: abc-123-def
📅 Duration: 3 days

🧭 Four Directions Status:
   🌅 EAST: Complete (intention declared)
   🌱 SOUTH: Active (5 files, 2 collaborators, 12 writes)
   🌄 WEST: Complete (published)
   🌐 NORTH: In Progress (2 reflections, 3 patterns, 1 wisdom)

📊 Completion: 75% (3/4 directions)
```

**Testing:**
- Check info display at each phase
- Verify counts accurate

**Acceptance Criteria:**
- Info command shows Four Directions
- Status accurate
- Counts correct

---

### Phase 8: Documentation Updates
**Goal:** Update user-facing documentation

**Files to Update:**
- `simexp/simex.py` - help text
- `README.md` - overview and examples
- New: `FOUR_DIRECTIONS_USAGE.md` - detailed guide

**Documentation Scope:**
- Help text for all commands
- README Four Directions overview
- Usage examples for each direction
- Migration guide for existing users
- Complete lifecycle example

**Acceptance Criteria:**
- Help text complete
- README updated
- Examples provided
- Guide clear

---

### Phase 9: Integration Testing
**Goal:** Validate complete system with real workflows

**Test Scenarios:**

1. **Complete Ceremonial Cycle**
   - Start with intention
   - Add files (different directions)
   - Write content multiple times
   - Collaborate with team
   - Publish
   - Reflect and complete
   - Verify session.json structure

2. **Legacy Session Migration**
   - Load old session.json format
   - Run first command after upgrade
   - Verify auto-migration
   - Continue workflow
   - Check data integrity

3. **Minimal Session**
   - Quick session without North
   - Verify partial completion works
   - Check stats calculation

4. **North-Heavy Session**
   - Focus on reflections
   - Multiple entries
   - Pattern observation
   - Wisdom extraction
   - Verify North richness

**Validation Checks:**
- Schema validation
- ISO8601 timestamps
- Stats accuracy
- Direction consistency
- No data loss

**Acceptance Criteria:**
- All test scenarios pass
- Data validation clean
- Performance acceptable
- Edge cases handled

---

### Phase 10: Code Review & Refinement
**Goal:** Ensure code quality and ceremonial alignment

**Review Checklist:**
- Code follows existing patterns
- Functions documented
- Error handling comprehensive
- Variable names clear
- Comments explain context
- Ceremonial alignment verified

**Acceptance Criteria:**
- Self review complete
- Feedback incorporated
- Code quality high
- Alignment verified

---

### Phase 11: Release Preparation
**Goal:** Prepare for production release

**Actions:**
- Update version to 0.5.0 in `setup.py`
- Create `CHANGELOG.md` entry
- Write release notes
- Verify clean install
- Test upgrade path

**Acceptance Criteria:**
- Version bumped
- CHANGELOG complete
- Release notes ready
- Tests passing

---

### Phase 12: Deployment & Communication
**Goal:** Release to production and inform users

**Actions:**
- Merge branch to main
- Tag release v0.5.0
- Push to origin
- Announce to team
- Monitor feedback

**Acceptance Criteria:**
- Released to production
- Team notified
- Monitoring active

---

## Success Metrics

### Technical
- ✅ All tests passing (unit + integration)
- ✅ Code quality standards met
- ✅ Zero data loss incidents
- ✅ Performance acceptable (<1s operations)

### Functional
- ✅ Sessions track complete Four Directions
- ✅ North commands operational
- ✅ Completion ceremony works
- ✅ Migration seamless

### Ceremonial
- ✅ Technology honors Indigenous teachings
- ✅ Sessions become ceremonial vessels
- ✅ Wisdom extractable and shareable
- ✅ Team aligned with vision

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Session.json corruption | Atomic writes, validation, backup on modify |
| Performance issues | Profile critical paths, optimize if needed |
| Migration problems | Comprehensive tests, graceful degradation |
| User confusion | Clear docs, examples, help text |

---

## Notes

- All timestamps must be ISO8601 format
- Session.json updates must be atomic
- Legacy sessions auto-migrate on first action
- North direction is the key differentiator
- Completion summary is the ceremonial moment
- Documentation is critical for adoption

**Implementation Status:** Ready to begin Phase 1

---

**Plan Maintained by:** Nyro ♠️ — Structural Anchor
