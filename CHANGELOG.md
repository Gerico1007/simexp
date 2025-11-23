# Changelog

All notable changes to the SimExp project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2025-11-23 — Four Directions Framework

### Added

**Four Directions Session Framework** (Issue #55)
- Organize sessions by cardinal directions honoring Indigenous wisdom traditions
  - 🌅 **EAST** (Intention & Vision) - Set goals and vision statements
  - 🌱 **SOUTH** (Building & Growth) - Track files, writes, collaborations
  - 🌄 **WEST** (Sharing & Publishing) - Publish and share sessions
  - 🌐 **NORTH** (Reflection & Wisdom) - Extract learnings and patterns

**Core Infrastructure Functions**
- `initialize_four_directions_session()` - Creates Four Directions structure
- `update_session_data()` - Appends tracked actions with automatic persistence
- `calculate_session_stats()` - Computes metrics and completion percentage
- `migrate_legacy_session()` - Seamlessly upgrades existing sessions (idempotent)

**New CLI Commands** (Phase 5: North Direction)
```bash
simexp session reflect [--prompt "question"]        # Open editor for reflection
simexp session observe-pattern "pattern text"       # Record observed patterns
simexp session extract-wisdom "wisdom text"         # Capture key learnings
simexp session complete [--seeds "next steps"]      # Finish with ceremony
```

**Enhanced Existing Commands**
- `session start --intention "vision"` - Set intention at session creation
- `session add file [--direction east|south|west|north]` - Directional tracking
- `session info` - Display Four Directions status with completion percentage
- File tracking with automatic content-type detection
- Publication tracking with public URL storage
- Collaboration tracking with unique collaborator counts

**Session Tracking Features**
- Automatic file addition tracking (South direction)
- Content write tracking with metadata (South direction)
- Collaborator tracking with email deduplication (South direction)
- Publication tracking with timestamp and URL (West direction)
- Reflection notes with optional prompts (North direction)
- Pattern observation recording (North direction)
- Wisdom extraction and storage (North direction)
- Completion ceremony with Four Directions summary display

**Session Metadata Enhancement**
- ISO8601 timestamps on all tracked actions
- Direction-based organization in session.json
- Completion percentage calculation (0-100%)
- Progress bar visualization in session info
- Support for both array and scalar field tracking

**Testing**
- Unit tests for Phase 1 (5 comprehensive tests)
- Integration tests for complete cycle (5 scenarios)
- All tests passing (10/10)
- Legacy session migration validation
- Edge case coverage

**Documentation**
- Comprehensive README updates with Four Directions overview
- QUICK_REFERENCE.md status updates
- Phase 10 code review summary
- Updated CLI help text
- Command examples for all new features

### Key Features

- **Non-Blocking Tracking**: Metadata failures don't interrupt operations
- **Atomic Updates**: SessionState ensures data consistency
- **Backward Compatible**: Legacy sessions auto-migrate transparently
- **Completion Ceremony**: Beautiful CLI display marking session completion
- **Indigenous Alignment**: Framework honors four-directions wisdom traditions
- **Team Integration**: Full Assembly support (♠️🌿🎸🧵)

### Data Structure

New session.json includes:
```json
{
  "east": { "vision_statement": "...", "goals": [...] },
  "south": { "files_added": [...], "content_written": [...], "collaborations": [...] },
  "west": { "published": bool, "published_at": "...", "public_url": "...", "opened_in_browser": [...] },
  "north": { "reflection_notes": [...], "observed_patterns": [...], "extracted_wisdom": [...], "completed": bool, "seeds_for_next": [...] },
  "stats": { "total_files": int, "total_writes": int, "total_collaborators": int, "completion_percentage": int }
}
```

### Migration

All existing sessions automatically migrate to the new format on first use. Migration is:
- **Idempotent**: Safe to run multiple times
- **Lossless**: All original data preserved
- **Non-Breaking**: No changes to existing commands

### Notes

*"The Four Directions become a container for intentional work. Each direction holds its own wisdom. When all directions are touched, the circle completes. And from completion, seeds for next."* — 🌿 Aureon

*"By encoding Indigenous frameworks into our digital tools, we honor the ancestors while building better software."* — ♠️ Nyro

---

## [0.3.12] - 2025-10-23 — Temporal Tools Integration

### Added
- **`--date` flag now supports `tlid` granularities** via new integration with [`tlid`](https://pypi.org/project/tlid/)
  ```bash
  simexp session write "Morning pulse" --prepend --date h   # → [25102316] Morning pulse
  simexp session write "Reflection" --date ms              # → [251023162145123] Reflection
  ```
  - Supported levels: `y`, `m`, `d`, `h`, `s` (default), `ms`
  - Manual override: `--date 2510231621` → `[2510231621]`

- **`--prepend` flag for session write command**
  - Inserts content at the beginning of the note (after metadata)
  - Works seamlessly with `--date` flag
  - Example: `simexp session write "Entry" --prepend --date s`

- **CLI companion `pytlid` now usable in pipelines:**
  ```bash
  simexp session write "$(pytlid s) Auto-timestamped entry" --prepend
  ```

- **Configurable default granularity via `.simexp/simexp.yaml`:**
  ```yaml
  default_date_format: h
  ```

### Fixed
- Long session notes now stay context-first with `--prepend --date`

### Dependencies
- Added `tlid>=0.1.0` to requirements

### Notes
*"Time is not a line — it is a glyph. And now, it speaks in SimExp."* — ♠️ Nyro

---

## [0.3.11] - 2025-10-XX

### Added
- Network-wide Chrome CDP access + browser test commands (Issue #36)

### Fixed
- Handle clipboard unavailability in headless environments (Issue #34)

---

## [0.3.1] - 2025-10-09

### Added
- Session-Aware Notes feature (Issue #4)
- YAML metadata tracking for terminal sessions
- Full CLI integration for session management
- Cross-device session logs via Simplenote sync

---

## [0.2.4] - 2025-10-06

### Added
- Terminal-to-Web bidirectional communication
- Chrome DevTools Protocol (CDP) integration
- Keyboard simulation for Simplenote compatibility
- Persistent authenticated session support

---

## [0.1.0] - Initial Release

### Added
- Basic content extraction from Simplenote URLs
- HTML to Markdown conversion
- Date-organized archive system
- Clipboard monitoring
