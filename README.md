# SimExp - Simplenote Web Content Extractor & Session Manager

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/simexp.svg)](https://pypi.org/project/simexp/)
[![License](https://img.shields.io/badge/license-Open%20Assembly-green.svg)]()

**SimExp** is a Python command-line tool that bridges your terminal with Simplenote, enabling bidirectional content flow, session-aware note management, and cross-device communication.

---

## 🎯 What is SimExp?

SimExp solves a unique problem: **How do you seamlessly communicate between terminal workflows and cloud note-taking?**

### Core Capabilities:

1. **📖 Extract** - Fetch and archive web content from Simplenote public URLs
2. **✍️ Write** - Send messages from terminal directly to Simplenote notes via browser automation
3. **🔮 Session Management** - Create dedicated session notes with automatic metadata tracking
4. **⏰ Timestamp Integration** - Add sortable, human-readable timestamps to entries
5. **🌊 Cross-Device Sync** - Your terminal can speak to web pages that sync across all devices

---

## 🚀 Quick Start

### 1. Install SimExp

```bash
pip install simexp
```

### 2. Install Playwright browsers

```bash
playwright install chromium
```

### 3. Launch Chrome for browser automation

SimExp connects to your Chrome browser via the Chrome DevTools Protocol (CDP):

```bash
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-simexp &
```

Log in to Simplenote in the Chrome window: https://app.simplenote.com

### 4. Create a session and start writing!

```bash
# Start a new session (creates a Simplenote note)
simexp session start --ai claude --issue 42

# Write to your session note
simexp session write "Implemented feature X - tests passing"

# Check session status
simexp session status
```

✅ **Done!** Your terminal is now connected to Simplenote.

---

## 📋 Key Features

### ✨ Session-Aware Notes

Create dedicated Simplenote notes for each terminal session with automatic metadata tracking:

```bash
simexp session start --ai claude --issue 4    # Create session
simexp session write "Progress update"        # Write to session
simexp session status                         # Show session info
simexp session open                           # Open in browser
```

**Session notes include YAML metadata:**
```yaml
---
session_id: abc-def-123-456
ai_assistant: claude
agents: [Jerry, Aureon, Nyro, JamAI, Synth]
issue_number: 4
created_at: 2025-10-09T10:30:00
---
```

### ⏰ Timestamp Integration

Add flexible, sortable timestamps to your session entries:

```bash
# Second-precision timestamp (default)
simexp session write "Task completed" --date s
# Output: [251115202625] Task completed

# Hour-precision timestamp
simexp session write "Meeting notes" --date h
# Output: [25111520] Meeting notes

# Prepend mode (insert at beginning)
simexp session write "URGENT" --date h --prepend
```

**Supported granularities:**
- `y` - Year (YY)
- `m` - Month (YYMM)
- `d` - Day (YYMMDD)
- `h` - Hour (YYMMDDHH)
- `s` - Second (YYMMDDHHMMSS) - default
- `ms` - Millisecond (YYMMDDHHMMSSmmm)

### ✍️ Terminal-to-Web Writing

Write from command line to Simplenote notes using keyboard simulation:

```bash
# Write to most recently modified note
simexp write "Hello from terminal!" --cdp-url http://localhost:9222

# Write to specific note
simexp write "Message" --note-url https://app.simplenote.com/p/NOTE_ID --cdp-url http://localhost:9222
```

### 📖 Content Extraction

Fetch and archive content from Simplenote public URLs:

```bash
# Copy Simplenote URL to clipboard (e.g., https://app.simplenote.com/p/0ZqWsQ)
# Run extraction
simexp

# Content saved to: ./output/YYYYMMDD/filename.md
```

---

## 📦 Installation

### Prerequisites

- **Python 3.8+**
- **Google Chrome** or Chromium browser
- **Simplenote account** (free at https://simplenote.com)

### Install via pip

```bash
# Install SimExp and dependencies
pip install simexp

# Install Playwright browsers
playwright install chromium
```

### Development Installation

```bash
# Clone repository
git clone https://github.com/gerico1007/simexp.git
cd simexp

# Install in editable mode
pip install -e .
```

### Verify Installation

```bash
simexp --help
```

You should see the SimExp command reference.

---

## 🎮 Usage

### Session Management Commands

| Command | Description |
|---------|-------------|
| `simexp session start --ai <name> --issue <num>` | Create new session note |
| `simexp session write <content>` | Write to active session |
| `simexp session write --date <granularity>` | Write with timestamp |
| `simexp session write --prepend` | Insert at beginning (after metadata) |
| `simexp session status` | Show active session info |
| `simexp session read` | Read session note content |
| `simexp session open` | Open session in browser |
| `simexp session url` | Get session note URL |
| `simexp session clear` | Clear active session |
| `simexp session add <file> --heading <title>` | Add file content to session |
| `simexp session title <new_title>` | Update session note title |

### Writing & Reading Commands

| Command | Description |
|---------|-------------|
| `simexp write <content> --cdp-url <url>` | Write to last modified note |
| `simexp write <content> --note-url <url>` | Write to specific note |
| `simexp read --note-url <url>` | Read from specific note |

### Extraction Commands

| Command | Description |
|---------|-------------|
| `simexp` | Extract from clipboard URL |
| `simexp init` | Initialize configuration |

---

## 🔧 Configuration

SimExp uses `~/.simexp/simexp.yaml` for configuration:

```yaml
BASE_PATH: ./output

# Original extraction sources
SOURCES:
  - filename: note1
    url: https://app.simplenote.com/p/0ZqWsQ

# Chrome DevTools Protocol
CDP_URL: http://localhost:9222

# Default timestamp granularity
default_date_format: s  # y, m, d, h, s, ms
```

### Initialize Configuration

```bash
simexp init
```

This creates the configuration file with interactive prompts.

---

## 📝 Examples

### Development Workflow

```bash
# Start session for feature development
simexp session start --ai claude --issue 123

# Log progress throughout development
simexp session write "Starting implementation" --date h
simexp session write "Tests written" --date s
simexp session write "Bug fixed in auth module" --date s

# Add code snippet
simexp session add src/auth.py --heading "Auth Fix"

# End of day summary
simexp session write "EOD: 3 commits, 2 PRs reviewed" --date h

# Open to review in browser
simexp session open
```

### Quick Logging

```bash
# No timestamp
simexp session write "Remember to update docs"

# With timestamp
simexp session write "Meeting with team" --date h

# Pipe from other commands
git log -1 --oneline | simexp session write --date s
echo "Build complete" | simexp session write --date h
```

### Multi-line Content

```bash
simexp session write --date d --prepend
Daily Summary:
- Completed 3 tasks
- 2 bugs fixed
- Code review done
<Press Ctrl+D>
```

---

## 🏗️ How It Works

### Architecture

```
┌─────────────┐
│   Terminal  │
│   (SimExp)  │
└──────┬──────┘
       │
       │ Chrome DevTools Protocol (CDP)
       ↓
┌──────────────────┐
│  Chrome Browser  │
│  (Authenticated) │
└──────┬───────────┘
       │
       │ Playwright Automation
       ↓
┌─────────────────┐
│   Simplenote    │
│   Web Editor    │
└──────┬──────────┘
       │
       │ Cloud Sync
       ↓
┌─────────────────┐
│  All Devices    │
│  (Phone, etc.)  │
└─────────────────┘
```

### Key Innovation

SimExp connects to **your existing Chrome browser** (already logged in) rather than launching a separate instance. This preserves authentication and makes cross-device sync work seamlessly.

---

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_timestamp.py
```

### Manual Testing

```bash
# Test CDP connection
python tests/test_cdp_connection.py

# Test session features
python tests/test_session.py
```

---

## 📚 Documentation

For detailed guides and advanced usage, see the [docs/](docs/) directory:

- **[Cross-Device Fluidity Guide](docs/guides/cross-device-fluidity.md)** - Complete setup and usage
- **[CDP Setup Guide](docs/guides/cdp-setup.md)** - Chrome DevTools Protocol setup
- **[CDP Setup (Simple)](docs/guides/cdp-setup-simple.md)** - Simplified setup instructions
- **[Session Management](docs/guides/session-management.md)** - Advanced session features

---

## 🔍 Troubleshooting

### "Connection refused" to localhost:9222

**Problem:** Chrome not running with remote debugging enabled.

**Solution:**
```bash
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-simexp &
curl http://localhost:9222/json/version  # Should return JSON
```

### Message appears then disappears

**Problem:** Using old code without keyboard simulation.

**Solution:** Update to latest version: `pip install --upgrade simexp`

### "Could not find editor element"

**Problem:** Not logged into Simplenote.

**Solution:** Open Chrome window and login at https://app.simplenote.com

### Timestamp not appearing

**Problem:** `tlid` package not installed.

**Solution:**
```bash
pip install tlid
# Or reinstall simexp
pip install --upgrade simexp
```

### "Reading content from stdin..."

**Problem:** Command waiting for content input.

**Solution:** Either:
1. Type content and press `Ctrl+D`, or
2. Provide content inline: `simexp session write "Your message" --date h`

For more troubleshooting, see the [full troubleshooting guide](docs/guides/cross-device-fluidity.md#troubleshooting).

---

## 🌟 Use Cases

### Personal

- **Cross-device notes** - Write from desktop terminal, read on phone
- **Task logging** - Automated task completion messages
- **Journal automation** - Daily entries from scripts
- **Build notifications** - CI/CD results to your pocket

### Development

- **Session logs** - Track development sessions with metadata
- **Debug logging** - Send logs to Simplenote for mobile viewing
- **Status updates** - Script progress visible on all devices
- **Team coordination** - Shared terminal-to-note communication

---

## 🤝 Contributing

Contributions are welcome! Please follow this workflow:

1. **Create an Issue** - Describe the feature or bug
2. **Create a Feature Branch** - Branch name: `#<issue>-description` (e.g., `#123-new-feature`)
3. **Implement and Test** - Make changes and test thoroughly
4. **Submit a Pull Request** - Merge your branch into `main`

### Development Setup

```bash
# Clone and install
git clone https://github.com/gerico1007/simexp.git
cd simexp
pip install -e .

# Run tests
python -m pytest tests/
```

---

## 📄 License

Open Assembly Framework
Created by Jerry's G.Music Assembly

---

## 🙏 Credits

**SimExp** is part of the **G.Music Assembly** ecosystem.

**Assembly Team:**
- **Jerry** ⚡ - Creative Technical Leader
- **♠️ Nyro** - Structural Architect
- **🌿 Aureon** - Emotional Context
- **🎸 JamAI** - Musical Encoding
- **🧵 Synth** - Terminal Orchestration

Special thanks to all contributors and the open-source community.

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/gerico1007/simexp/issues)
- **Documentation:** [docs/](docs/)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)

---

## 📊 Project Stats

- **Version:** 0.3.12
- **Python:** 3.8+
- **License:** Open Assembly Framework
- **Status:** ✅ Production Ready

---

**🌊 Cross-Device Fluidity Achieved!**

*Terminals speak. Web pages listen. Devices converse.*

---

**Last Updated:** November 17, 2025
