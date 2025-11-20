# 📖 Recovered Features - Usage Guide

This document covers all the features that were recovered from the lost commits and are now available in the `recovery/lost-features-restoration` branch.

## 🎯 Feature 1: Session Title Command

### Overview
Set a descriptive title for your session notes. The title appears at the top of the note with an underline separator.

### Usage
```bash
# Basic usage
simexp session title "My Session Title"

# With custom CDP URL
simexp session title "Project: Feature Implementation" --cdp-url http://192.168.1.100:9222

# With environment variable
export SIMEXP_CDP_URL=http://server:9222
simexp session title "Analysis Session"
```

### Output Format
```
My Session Title
================

<!-- session_metadata
session_id: 12345678-...
ai_assistant: claude
...
-->

<rest of session content>
```

### Features
- ✅ Searches for active session using session_id
- ✅ Positions cursor at beginning of note
- ✅ Writes title with underline formatting
- ✅ Saves title to `.simexp/session.json`
- ✅ Supports custom CDP URLs
- ✅ Works with all existing session features

### Help
```bash
simexp session title --help
```

---

## 🎯 Feature 2: HTML Metadata Format

### Overview
Session metadata is now stored in a structured format that:
- Doesn't interfere with note content
- Is searchable by Simplenote
- Keeps metadata organized
- Maintains compatibility with Simplenote rendering

### Format
```html
<div class="simexp-session-metadata" hidden>
session_id: 12345678-1234-1234-1234-1234567890ab
ai_assistant: claude
agents:
  - Jerry
  - Aureon
  - Nyro
  - JamAI
  - Synth
issue_number: 42
created_at: 2025-11-17T16:24:50.123456
</div>
```

### Benefits
- Metadata is hidden from visual display
- Full text search still finds session_id
- Can be navigated with Playwright selectors
- Clean separation of metadata and content
- Compatible with Simplenote's editor

---

## 🎯 Feature 3: Help Flag Support

### Overview
All major subcommands now support the `--help`, `-h`, and `help` flags with proper help text and exit codes.

### Usage

#### Session Help
```bash
simexp session --help
simexp session -h
simexp session help
```

Output:
```
♠️🌿🎸🧵 SimExp Session Management

Usage: simexp session <subcommand>

Session Management:
  start [--ai <assistant>] [--issue <number>]  - Start new session
  list                                         - List all sessions (directory tree)
  info                                         - Show current session & directory context
  status                                       - Show session status
  clear                                        - Clear active session

Session Content:
  write <message>                              - Write to session note
  read                                         - Read session note
  add <file> [--heading <text>]                - Add file to session note
  title <title>                                - Set session note title
  open                                         - Open session note in browser
  url                                          - Print session note URL

Collaboration & Sharing (Issue #6):
  collab <glyph|alias|group>                   - Share with Assembly (♠, 🌿, 🎸, 🧵, assembly)
  collab add <email>                           - Add collaborator by email
  collab remove <email>                        - Remove collaborator
  collab list                                  - List all collaborators
  publish                                      - Publish note (get public URL)
  unpublish                                    - Unpublish note (make private)

Examples:
  simexp session start --ai claude --issue 42  # Start new session
  simexp session write 'Progress update'       # Write to session
  simexp session collab ♠                      # Share with Nyro
  simexp session collab assembly               # Share with all Assembly
  simexp session publish                       # Get public URL
```

#### Browser Help
```bash
simexp browser --help
simexp browser -h
simexp browser help
```

Output:
```
♠️🌿🎸🧵 SimExp Browser/CDP Management

Usage: simexp browser <subcommand>

Browser/CDP Commands (Issue #36):
  test                    - Test Chrome CDP connection and network binding
  launch                  - Launch Chrome with CDP (localhost-only, secure)
  launch --network        - Launch Chrome with network-wide access (WiFi)

Examples:
  simexp browser test                           # Test CDP connection
  simexp browser launch                         # Launch Chrome (localhost)
  simexp browser launch --network               # Launch Chrome (network-wide)
  simexp browser launch --network --port 9223   # Custom port

Network-wide access allows SimExp to connect from other devices on WiFi.
Use 'simexp browser test' to verify your configuration.
```

#### Collaboration Help
```bash
simexp session collab --help
simexp session collab -h
simexp session collab help
```

Output:
```
♠️🌿🎸🧵 SimExp Collaboration Management

Usage: simexp session collab <subcommand|glyph|alias|group>

Share with Assembly Members:
  <glyph|alias|group>    - Share using glyph (♠, 🌿, 🎸, 🧵), alias, or 'assembly'

Manage Collaborators:
  add <email>            - Add collaborator by email
  remove <email>         - Remove collaborator by email
  list                   - List all collaborators

Examples:
  simexp session collab ♠                      # Share with Nyro (glyph)
  simexp session collab nyro                   # Share with Nyro (alias)
  simexp session collab assembly               # Share with all Assembly
  simexp session collab add jerry@example.com  # Add collaborator
  simexp session collab list                   # List collaborators
```

### Features
- ✅ Exit code 0 (success) when showing help (not error code 1)
- ✅ Support for `--help`, `-h`, and `help` aliases
- ✅ Comprehensive help text with examples
- ✅ Consistent formatting across all commands

---

## 🎯 Feature 4: CLI Help Reorganization

### Overview
Help text has been reorganized to be more discoverable and user-friendly.

### Session Command Help Structure
```
Session Management:        → Basic operations
├─ start                   → Create new sessions
├─ list                    → List all sessions
├─ info                    → Session details
├─ status                  → Session status
└─ clear                   → Clear session

Session Content:          → Read/write operations
├─ write <message>
├─ read
├─ add <file>
├─ title <title>
├─ open
└─ url

Collaboration & Sharing:  → Sharing operations
├─ collab <glyph|alias|group>
├─ collab add/remove/list
├─ publish
└─ unpublish

Examples:                 → Common patterns
├─ Start new session
├─ Write to session
├─ Share with collaborators
└─ Publish publicly
```

### Smart Collab Command
The collab command now handles multiple types of inputs:

```bash
# Share with Assembly members using glyph
simexp session collab ♠                      # Nyro
simexp session collab 🌿                     # Aureon
simexp session collab 🎸                     # JamAI
simexp session collab 🧵                     # Synth

# Share with Assembly members using alias
simexp session collab nyro
simexp session collab aureon
simexp session collab jamai
simexp session collab synth

# Share with entire Assembly group
simexp session collab assembly

# Add individual collaborators
simexp session collab add jerry@example.com
simexp session collab add jane@example.com

# Remove collaborators
simexp session collab remove jerry@example.com

# List all collaborators
simexp session collab list
```

### Benefits
- ✅ Logical grouping of related commands
- ✅ Examples show common use cases
- ✅ Consistent formatting and terminology
- ✅ Assembly member shortcuts
- ✅ Clear navigation between features

---

## 🎯 Feature 5: Main Help Simplification

### Overview
The main `simexp --help` is now streamlined and hierarchical, directing users to detailed help for each subcommand.

### Main Help Output
```
♠️🌿🎸🧵 SimExp - Simplenote Web Content Extractor & Writer

Commands:
  simexp                       - Run extraction from clipboard/config
  simexp init                  - Initialize configuration
  simexp session <subcommand>  - Session management (use --help for details)
  simexp browser <subcommand>  - Browser/CDP testing & management (use --help for details)
  simexp help                  - Show this help

For detailed help on any command, use:
  simexp session --help
  simexp browser --help
```

### Benefits of Simplification
- ✅ Minimal, focused main help (10 lines vs 40+ before)
- ✅ Clear navigation to detailed help
- ✅ Reduced information overload
- ✅ Encourages discovery of --help flags
- ✅ Hierarchical help structure

### Help Navigation Tree
```
simexp help
├─ simexp session --help      (comprehensive session help)
│  ├─ Session Management
│  ├─ Session Content
│  ├─ Collaboration & Sharing
│  └─ Examples
│
└─ simexp browser --help      (comprehensive browser help)
   ├─ Browser/CDP Commands
   ├─ Examples
   └─ Network configuration
```

---

## 🔧 Configuration

### CDP URL Resolution Priority
All recovered commands respect the CDP URL priority chain:

1. **Command-line flag** (highest priority)
   ```bash
   simexp session title "Title" --cdp-url http://192.168.1.100:9222
   ```

2. **Environment variable**
   ```bash
   export SIMEXP_CDP_URL=http://server:9222
   simexp session title "Title"
   ```

3. **Config file** (~/.simexp/simexp.yaml)
   ```yaml
   CDP_URL: http://192.168.1.100:9222
   ```

4. **Default** (localhost, lowest priority)
   ```
   http://localhost:9222
   ```

---

## 📝 Session File Format

After using the title command, your `.simexp/session.json` will include:

```json
{
  "session_id": "12345678-1234-1234-1234-1234567890ab",
  "search_key": "12345678-1234-1234-1234-1234567890ab",
  "ai_assistant": "claude",
  "issue_number": 42,
  "title": "My Session Title",
  "cdp_endpoint": "http://localhost:9222",
  "created_at": "2025-11-17T16:24:50.123456"
}
```

---

## ✅ Quick Reference

### Session Title
```bash
simexp session title "My Title"
```

### Help for Any Command
```bash
simexp session --help
simexp browser --help
simexp session collab --help
```

### Share with Assembly
```bash
simexp session collab nyro          # By alias
simexp session collab ♠             # By glyph
simexp session collab assembly      # Entire group
```

### Add Collaborators
```bash
simexp session collab add email@example.com
simexp session collab list
simexp session collab remove email@example.com
```

---

## 🚀 Next Steps

1. **Review** the recovery branch: `recovery/lost-features-restoration`
2. **Test** all recovered commands in your environment
3. **Merge** to main when ready: `git merge recovery/lost-features-restoration`
4. **Deploy** with confidence knowing all features are restored

---

## 📚 Additional Resources

- See `RECOVERY_REPORT.md` for technical details
- View recovery commit: `git show aed307c`
- Compare with main: `git diff main..recovery/lost-features-restoration`
- Check original commits for implementation details
