# Changelog

All notable changes to the SimExp project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- Added `tlid>=1.0.0` to requirements

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
