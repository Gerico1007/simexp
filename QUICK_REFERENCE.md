# Four Directions Enhancement - Quick Reference Card

**Status:** Phase 0 ✅ Complete | Ready for Phase 1
**Issue:** #55
**Branch:** `55-four-directions-enhancement`
**Target:** v0.5.0

---

## The Four Directions

```
         🌅 EAST
      (Intention)
           ↓
🌱 SOUTH ← ⭐ → 🌄 WEST
(Growth)      (Publishing)
           ↑
         🌐 NORTH
      (Reflection)
```

---

## Phase Breakdown

| Phase | Name | Focus | Status |
|-------|------|-------|--------|
| 0 | Preparation | Issue, branch, planning | ✅ Complete |
| 1 | Core Infrastructure | 4 functions, data structure | ⏳ Next |
| 2 | South - Files | File tracking, --direction flag | ⏳ |
| 3 | South - Write/Collab | Write & collaboration tracking | ⏳ |
| 4 | West - Publishing | Publication tracking, opens | ⏳ |
| 5 | North - Reflection | 4 NEW commands + ceremony | ⏳ |
| 6 | East - Intention | --intention flag at start | ⏳ |
| 7 | Session Info | Display Four Directions status | ⏳ |
| 8 | Documentation | README, help, guide | ⏳ |
| 9 | Integration Testing | Full cycle, migration, edge cases | ⏳ |
| 10 | Code Review | Quality gates, alignment | ⏳ |
| 11 | Release Prep | v0.5.0, CHANGELOG, notes | ⏳ |
| 12 | Deployment | Merge, tag, announce | ⏳ |

---

## Key Documents

- **55-FOUR_DIRECTIONS_ENHANCEMENT_PLAN.md** - Full implementation guide
- **ENHANCEMENT_PLAN_SUMMARY.txt** - All phase details
- **PHASE_0_SUMMARY.md** - Phase 0 completion summary
- **simexp_four_directions_enhancement_spec.md** - Data structures
- **simexp_four_directions_team_communication.md** - Team alignment

---

## Phase 1: Core Infrastructure

**File:** `simexp/session_manager.py`

**Add 4 Functions:**
```python
initialize_four_directions_session(session_data: dict) -> dict
  └─ Create session with Four Directions structure

update_session_data(direction: str, action_type: str, action_data: dict) -> None
  └─ Append action to direction, update JSON, recalculate stats

calculate_session_stats(session: dict) -> dict
  └─ Count files, writes, collaborators, duration, completion %

migrate_legacy_session(session: dict) -> dict
  └─ Convert old format to new, preserve data
```

**New session.json Structure:**
```json
{
  "session_id": "uuid",
  "east": { "vision_statement": "...", "goals": [] },
  "south": { "files_added": [], "content_written": [], "collaborations": [] },
  "west": { "published": false, "public_url": null, "opened_in_browser": [] },
  "north": { "reflection_notes": [], "observed_patterns": [], "extracted_wisdom": [], "seeds_for_next": [] },
  "stats": { "total_files": 0, "total_writes": 0, "completion_percentage": 0 }
}
```

---

## North Direction Commands (Phase 5)

```bash
# Open editor for reflection
simexp session reflect [--prompt "What did we learn?"]

# Record observed pattern
simexp session observe-pattern "Pattern description"

# Extract wisdom
simexp session extract-wisdom "Wisdom text"

# Mark completion and show ceremony
simexp session complete [--seeds "seed1, seed2"]
```

---

## Completion Ceremony Output

```
♠️🌿🎸🧵 Session Completion Summary
🔮 Session: [id]
📅 Duration: X days
📁 Files: N | 👥 Collaborators: N | ✍️ Writes: N | 🌐 Published: Yes/No

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

---

## CLI Enhancements

**Existing commands with new options:**
- `session start --intention "text"` - Capture intention
- `session add file.md --direction south|east|west|north` - Direction flag
- `session publish` - Track publication
- `session open` - Track browser opens
- `session info` - Show Four Directions status

**New commands:**
- `session reflect [--prompt "text"]` - Reflection editor
- `session observe-pattern "text"` - Record pattern
- `session extract-wisdom "text"` - Capture wisdom
- `session complete [--seeds "text"]` - Ceremonial completion

---

## Git Commands

```bash
# Current state
git status                          # Check branch status
git log --oneline -5                # View recent commits

# To continue from here
git checkout 55-four-directions-enhancement  # On the branch
git pull origin 55-four-directions-enhancement # Get latest

# When committing Phase changes
git commit -am "Phase N: [description]"
git push origin 55-four-directions-enhancement
```

---

## Success Metrics

**Technical:**
- All tests passing (unit + integration)
- Code quality standards met
- Zero data loss incidents
- Operations < 1 second

**Functional:**
- Sessions track all Four Directions
- North commands operational
- Completion ceremony works
- Migration seamless

**Ceremonial:**
- Technology honors Indigenous teachings
- Sessions become ceremonial vessels
- Wisdom extractable and shareable
- Team aligned with vision

---

## Testing Strategy

**Phase 1:**
- Unit tests for each function
- Manual verification of structure

**Phase 9 (Integration):**
- Complete ceremonial cycle test
- Legacy session migration test
- Minimal session test
- North-heavy session test
- Schema validation
- Stats accuracy
- Performance benchmarks

---

## Important Notes

- All timestamps must be ISO8601 format
- Session.json updates must be atomic
- Legacy sessions auto-migrate on first action
- Direction flag defaults to 'south'
- North direction is the key differentiator
- Completion summary is the ceremonial moment
- Documentation is critical for adoption

---

## Links

- **GitHub Issue:** https://github.com/Gerico1007/simexp/issues/55
- **Feature Branch:** `55-four-directions-enhancement`
- **Files to Modify:**
  - `simexp/session_manager.py` - Phases 1, 2, 3
  - `simexp/simex.py` - Phases 2-7
  - `simexp/session_sharing.py` - Phase 3

---

**Ready for Phase 1?** Begin with `simexp/session_manager.py`

Prepared by: Nyro ♠️ | Aureon 🌿 | JamAI 🎸
