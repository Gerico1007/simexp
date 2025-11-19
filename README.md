# 🌊 SimExp - Simplenote Web Content Extractor & Writer
**Cross-Device Fluidity: Terminal ↔ Web Communication**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Open%20Assembly-green.svg)]()

---

## 🎯 What is SimExp?

SimExp is a bidirectional communication tool that bridges terminals and Simplenote web pages:

1. **📖 Extract**: Fetch and archive web content from Simplenote URLs
2. **✍️ Write**: Send messages from terminal directly to Simplenote notes
3. **🌊 Sync**: Enable cross-device communication through Simplenote's cloud

**Key Achievement**: **Terminal-to-Web fluidity** - Your terminal can now speak to web pages and sync across all your devices!

---

## 📦 Installation

### 1. Prerequisites

*   Python 3.8+
*   Google Chrome or Chromium
*   A Simplenote account (free at https://simplenote.com)

### 2. Install Dependencies

```bash
# Core dependencies
pip install playwright pyperclip beautifulsoup4 pyyaml requests

# Install Playwright browsers
playwright install chromium
```

### 3. Launch the Chrome Communication Bridge

For `simexp` to communicate with your browser, you need to launch a special instance of Chrome with a remote debugging port. **You only need to do this once.**

```bash
# Launch Chrome with a remote debugging port
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-simexp &
```

*   `--remote-debugging-port=9222`: This opens a communication channel that `simexp` uses to connect to your browser.
*   `--user-data-dir=/tmp/chrome-simexp`: This creates a separate profile for this Chrome instance, so it doesn't interfere with your main browsing session.
*   `&`: This runs the command in the background, so you can continue to use your terminal.

In the new Chrome window that opens, log in to your Simplenote account: https://app.simplenote.com

---

## 🚀 Quick Start

### 1. Launch Chrome for Communication

First, you need to launch a special instance of Google Chrome that the script can communicate with. **You only need to do this once.**

```bash
# Launch Chrome with a remote debugging port
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-simexp &
```

In the new Chrome window that opens, log in to your Simplenote account: https://app.simplenote.com

### 2. Install SimExp

```bash
# Install dependencies
pip install playwright pyperclip beautifulsoup4 pyyaml requests
playwright install chromium
```

### 3. Write to Your Last Modified Note!

Now you can write to your most recently modified Simplenote note directly from your terminal:

```bash
python -m simexp.simex write "Hello from the Assembly!" --cdp-url http://localhost:9222
```

Check your Simplenote note - the message is there! It will also sync to your other devices. ✨

**👉 [Full Cross-Device Setup Guide](README_CROSS_DEVICE_FLUIDITY.md)**

---

## 📋 Features

### ✅ Extraction (Original Feature)
- Fetch content from Simplenote public URLs
- Convert HTML to clean Markdown
- Organize archives by date
- Monitor clipboard for automatic extraction

### ✨ Writing (NEW - Cross-Device Fluidity!)
- **Terminal-to-Web**: Write from command line to Simplenote notes
- **Keyboard Simulation**: Uses actual typing for Simplenote compatibility
- **Authenticated Session**: Connects to your logged-in Chrome browser
- **Cross-Device Sync**: Messages appear on all your devices
- **Persistent Changes**: Content stays in notes (doesn't get reverted)
- **Public URL Resolution**: Automatically resolves public URLs (/p/) to internal UUIDs for writing

### 🔮 Session-Aware Notes (NEW - Issue #4!)
- **Automatic Session Notes**: Create dedicated Simplenote notes for each terminal session
- **YAML Metadata**: Track session ID, AI assistant, agents, and issue number
- **Persistent State**: Session info saved locally in `.simexp/session.json`
- **CLI Integration**: Full command suite for session management
- **Cross-Device Session Logs**: Access session notes from any device

**Session Commands:**
```bash
simexp session start --ai claude --issue 42  # Create session note
simexp session write "Progress update"       # Write to session
simexp session status                        # Show session info
simexp session open                          # Open in browser
simexp session add path/to/file --heading "Optional Heading"  # Add file content to session
```

### ⏰ Timestamp Integration (NEW - Issue #33!)
- **Flexible Timestamps**: Add human-readable, sortable time identifiers via `tlid` package
- **Multiple Granularities**: Year, month, day, hour, second, millisecond precision
- **Prepend Mode**: Insert timestamped entries at the beginning (after metadata)
- **Append Mode**: Add timestamped entries at the end (default)
- **Stdin Support**: Type content interactively or pipe from other commands
- **Configurable Defaults**: Set preferred timestamp format in `~/.simexp/simexp.yaml`

#### 📝 Basic Usage

**Method 1: Inline Content (Quick)**
```bash
# Provide content directly in the command
simexp session write "Your message here" --date s
```

**Method 2: Interactive (Stdin)**
```bash
# Type content interactively
simexp session write --date h
# Type your message (can be multiple lines)
# Press Ctrl+D when finished
```

**Method 3: Pipe from Other Commands**
```bash
# Pipe output from another command
git log -1 --oneline | simexp session write --date s
echo "Task completed at $(date)" | simexp session write --date h
cat progress.txt | simexp session write --date d --prepend
```

#### 🎯 Timestamp Granularities

Each granularity creates a different timestamp format (YYMMDD... format):

| Flag | Granularity | Format | Example Output | Use Case |
|------|-------------|--------|----------------|----------|
| `y` | Year | YY | `[25] Entry` | Annual notes |
| `m` | Month | YYMM | `[2511] Entry` | Monthly logs |
| `d` | Day | YYMMDD | `[251115] Entry` | Daily journaling |
| `h` | Hour | YYMMDDHH | `[25111520] Entry` | Hourly updates |
| `s` | Second | YYMMDDHHMMSS | `[251115202625] Entry` | Default, precise logs |
| `ms` | Millisecond | YYMMDDHHMMSSmmm | `[251115202625123] Entry` | High-precision events |

**Manual Timestamp:**
```bash
# Provide your own timestamp (any numeric string)
simexp session write "Meeting notes" --date 2511151500
# Output: [2511151500] Meeting notes
```

#### 📍 Prepend vs Append

**Append Mode (Default)**: Adds entry to the **end** of the note
```bash
simexp session write "Completed task X" --date s
# Entry appears at the bottom of your note
```

**Prepend Mode**: Inserts entry at the **beginning** (after metadata)
```bash
simexp session write "URGENT: Critical update" --date h --prepend
# Entry appears right after the --- metadata block
```

**Example Note Structure:**
```yaml
---
session_id: abc-123
ai_assistant: claude
---

[25111520] 🔥 URGENT: Critical update (prepended)

[251115123456] Old entry from earlier
[251115202625] Completed task X (appended most recently)
```

#### 💡 Real-World Examples

**Development Workflow:**
```bash
# Morning standup
simexp session write "Starting work on feature X" --date h --prepend

# Log progress throughout the day
git commit -m "Fix bug #123" && \
  simexp session write "Fixed bug #123 - auth issue" --date s

# End of day summary
simexp session write "EOD: 3 commits, 2 PRs reviewed" --date h
```

**Quick Logging:**
```bash
# No timestamp (quick note)
simexp session write "Remember to update docs"

# With hour timestamp
simexp session write "Meeting with team" --date h

# Millisecond precision for events
simexp session write "API response time: 245ms" --date ms
```

**Multi-line Content:**
```bash
simexp session write --date d --prepend
Daily Summary:
- Completed 3 tasks
- 2 bugs fixed
- Code review done
<Press Ctrl+D>
```

#### ⚙️ Configuration

Set your default timestamp granularity in `~/.simexp/simexp.yaml`:

```yaml
default_date_format: h  # hour granularity as default
```

Then you can use `--date` without a value:
```bash
simexp session write "Uses default granularity" --date
# Will use 'h' (hour) format from config
```

#### 🔧 Timestamp Format Details

Timestamps follow the **TLID format** (Time-based Lexicographically-sortable Identifier):
- **Human-readable**: Easy to parse visually (YYMMDDHHMMSS)
- **Sortable**: Chronological order when sorted alphabetically
- **Compact**: No separators, minimal characters
- **Universal**: Works in any system, no timezone issues

**Sorting Example:**
```
[251115] Day entry
[25111512] Hour entry (noon)
[25111520] Hour entry (8 PM)
[251115202625] Second-precise entry
[251115202625123] Millisecond-precise entry
```
All entries sort correctly in chronological order!

---

## 🏗️ Project Structure

```
simexp/
├── simexp/
│   ├── playwright_writer.py    # ✨ NEW: Terminal-to-web writer
│   ├── simex.py                # Main CLI orchestrator
│   ├── simfetcher.py           # Content fetcher
│   ├── processor.py            # HTML processor
│   ├── archiver.py             # Markdown archiver
│   ├── imp_clip.py             # Clipboard integration
│   └── simexp.yaml             # Configuration
├── test_cdp_connection.py      # ✨ NEW: CDP testing script
├── CDP_SETUP_GUIDE.md          # ✨ NEW: Setup guide
├── README_CROSS_DEVICE_FLUIDITY.md  # ✨ NEW: Detailed docs
├── sessionABC/                 # Musical session encodings
├── ledger/                     # Session journals
└── .synth/                     # Assembly documentation
```

---

## 📦 Installation

### Prerequisites

- Python 3.8+
- Google Chrome or Chromium
- Simplenote account (free at https://simplenote.com)

### Install Dependencies

```bash
# Core dependencies
pip install playwright pyperclip beautifulsoup4 pyyaml requests

# Install Playwright browsers
playwright install chromium
```

---

## 🎮 Usage

### Write to the Last Modified Note

This is the easiest way to use `simexp`. It will automatically find your last modified note and append your message to it.

```bash
python -m simexp.simex write "Your message here" --cdp-url http://localhost:9222
```

### Write to a Specific Note

If you need to write to a specific note, you can provide its URL.

```bash
python -m simexp.simex write "Your message here" --note-url https://app.simplenote.com/p/NOTE_ID --cdp-url http://localhost:9222
```

### 🔗 Public URL Resolution (NEW!)

SimExp now supports writing to notes using their public URLs! Instead of extracting UUIDs, it writes directly to opened notes following the session start pattern.

**How it works:**

1. Loads the public URL to extract note content (first 30 chars for searching)
2. Navigates to Simplenote app
3. Searches for the note using the extracted content
4. Clicks the note to open it in the editor
5. Writes content directly to the opened note
6. Optionally initializes session metadata (if `--init-session` flag is used)

**Example:**
```bash
# Write to a note using its public URL
simexp write https://app.simplenote.com/p/0ZqWsQ "Appended content"

# Output:
# ♠️🌿🎸🧵 SimExp Public URL Resolution & Write
# 🌐 Loading public note to extract search text...
# 🔍 Search text: 'First 30 characters of note...'
# 🌐 Navigating to Simplenote app...
# ✅ Found search box
# ⏳ Waiting for search results...
# ✅ Clicking note
# ✅ Note opened in editor
# 📝 Appending content...
# ✅ Content written (16 chars)
# ✅ Write successful!
```

**Initialize as Session Note:**
```bash
# Resolve public URL and add session metadata in one command
simexp write https://app.simplenote.com/p/0ZqWsQ "Initial content" --init-session --ai claude --issue 42

# This will:
# 1. Navigate to public URL and extract note content for searching
# 2. Search for the note in Simplenote app
# 3. Click to open the note
# 4. Add session metadata (YAML header) to the note
# 5. Write your content to the note
# 6. Store session info in .simexp/session.json
# 7. You can now use 'simexp session write' with this note!
```

**Benefits:**
- ✅ Write to existing notes using their public links
- ✅ No UUID extraction needed - writes directly to opened notes
- ✅ Follows session start pattern for reliability
- ✅ Search-based resolution works even when URLs don't change (SPA mode)
- ✅ Optional: Turn any note into a tracked session note

### Read from a Specific Note

```bash
python -m simexp.simex read --note-url https://app.simplenote.com/p/NOTE_ID --cdp-url http://localhost:9222
```

### Extract Content from Simplenote URLs

```bash
# Copy a Simplenote URL to clipboard
# Example: https://app.simplenote.com/p/0ZqWsQ

# Run extraction
python -m simexp.simex

# Content saved to ./output/YYYYMMDD/filename.md
```

### 🔮 Session-Aware Notes Workflow

Create dedicated Simplenote notes for your terminal sessions with automatic metadata tracking:

```bash
# 1. Start a new session (creates Simplenote note with YAML metadata)
python -m simexp.simex session start --ai claude --issue 4

# Output:
# ♠️🌿🎸🧵 Creating Session Note
# 🔮 Session ID: abc-def-123-456
# 🌐 Note URL: https://app.simplenote.com/p/NOTE_ID
# ✅ Session started successfully!

# 2. Write to your session note
python -m simexp.simex session write "Implemented session manager module"

# Or pipe content:
echo "Fixed bug in URL extraction" | python -m simexp.simex session write

# 3. Check session status
python -m simexp.simex session status

# Output:
# ♠️🌿🎸🧵 Active Session Status
# 🔮 Session ID: abc-def-123-456
# 🌐 Note URL: https://app.simplenote.com/p/NOTE_ID
# 🤝 AI Assistant: claude
# 🎯 Issue: #4

# 4. Read session content
python -m simexp.simex session read

# 5. Open session note in browser
python -m simexp.simex session open

# 6. Get just the URL (for scripting)
python -m simexp.simex session url

# 7. Clear session when done
python -m simexp.simex session clear
```

**Session Note Format:**
```yaml
---
session_id: abc-def-123-456
ai_assistant: claude
agents:
  - Jerry
  - Aureon
  - Nyro
  - JamAI
  - Synth
issue_number: 4
pr_number: null
created_at: 2025-10-09T10:30:00
---

# Your session content appears below the metadata
```

---

## 🔧 Configuration

### simexp/simexp.yaml

```yaml
BASE_PATH: ./output

# Original extraction sources
SOURCES:
  - filename: note1
    url: https://app.simplenote.com/p/0ZqWsQ

# NEW: Communication channels for cross-device messaging
COMMUNICATION_CHANNELS:
  - name: Aureon
    note_id: e6702a7b90e64aae99df2fba1662bb81
    public_url: https://app.simplenote.com/p/gk6V2v
    auth_url: https://app.simplenote.com
    mode: bidirectional
    description: "🌿 Main communication channel"
```

---

## 🧪 Testing

### Test Extraction

```bash
# Extract from a public Simplenote URL
python -m simexp.simex
```

### Test Terminal-to-Web Writing

```bash
# Run comprehensive test (requires Chrome running with CDP)
python test_cdp_connection.py
```

### Test Session-Aware Notes

```bash
# Run session feature tests (requires Chrome + Simplenote login)
python test_session.py
```

### Manual Test

```bash
# 1. Launch Chrome with debugging
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-simexp &

# 2. Login to Simplenote in Chrome window

# 3. Test write
python3 -c "
import asyncio
from simexp.playwright_writer import write_to_note

result = asyncio.run(write_to_note(
    'https://app.simplenote.com',
    '🔮 TEST MESSAGE - If you see this, it works!',
    cdp_url='http://localhost:9222',
    debug=True
))

print('Success!' if result['success'] else 'Failed')
"

# 4. Check the note in Chrome - message should be there!
```

---

## 🎓 How It Works

### Extraction Flow

```
Clipboard URL → simfetcher → HTML → processor → Markdown → archiver → output/YYYYMMDD/
```

### Writing Flow (Terminal-to-Web)

```
Terminal Command
    ↓
playwright_writer.py
    ↓
Chrome DevTools Protocol (CDP)
    ↓
Your Authenticated Chrome Browser
    ↓
Keyboard Simulation (types character-by-character)
    ↓
Simplenote Editor (div.note-editor)
    ↓
Simplenote Cloud Sync
    ↓
All Your Devices! 🎉
```

**Key Innovation**: We connect to YOUR Chrome browser (already logged in) rather than launching a separate instance. This preserves authentication and makes cross-device sync work seamlessly.

---

## 📚 Documentation

- **[Cross-Device Fluidity Guide](README_CROSS_DEVICE_FLUIDITY.md)** - Complete setup and usage
- **[CDP Setup Guide](CDP_SETUP_GUIDE.md)** - Chrome DevTools Protocol setup
- **[Session Journal](ledger/251006_session_playwright_mcp_integration.md)** - Development session log
- **[Session Melody](sessionABC/251006_playwright_flow.abc)** - Musical encoding of session

---

## 🔍 Troubleshooting

### "Connection refused" to localhost:9222

Chrome not running with remote debugging:
```bash
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-simexp &
curl http://localhost:9222/json/version  # Should return JSON
```

### Message appears then disappears

Using old code without keyboard simulation - update `playwright_writer.py` to latest version.

### "Could not find editor element"

Not logged into Simplenote - open Chrome window and login at https://app.simplenote.com

### Timestamp Issues

**Problem: "Reading content from stdin..."**
- This means the command is waiting for you to type content
- **Solution**: Either type your message and press `Ctrl+D`, or cancel (`Ctrl+C`) and provide content inline:
  ```bash
  simexp session write "Your message" --date h
  ```

**Problem: Prepend not inserting after metadata**
- Ensure your session note has metadata (created with `simexp session start`)
- Old notes may use different metadata formats
- **Solution**: Prepend works with both YAML (`---`) and HTML comment (`<!--`) metadata

**Problem: Timestamps not appearing**
- Check that `tlid` package is installed: `pip list | grep tlid`
- **Solution**: Install if missing: `pip install tlid`
- Fallback mode uses datetime if tlid unavailable

**Problem: How to exit stdin mode?**
- Press `Ctrl+D` to finish typing (Unix/Linux/Mac)
- Press `Ctrl+Z` then Enter on Windows
- Or cancel with `Ctrl+C` and use inline content instead

**👉 See [Full Troubleshooting Guide](README_CROSS_DEVICE_FLUIDITY.md#troubleshooting)**

---

## 🌟 Use Cases

### Personal
- **Cross-device notes**: Write from desktop terminal, read on phone
- **Task logging**: Automated task completion messages
- **Journal automation**: Daily entries from scripts
- **Build notifications**: CI/CD results to your pocket

### Development
- **Debug logging**: Send logs to Simplenote for mobile viewing
- **Status updates**: Script progress visible on all devices
- **Command queue**: Cross-device command execution
- **Team coordination**: Shared terminal-to-note communication

---

## 🎨 G.Music Assembly Integration

SimExp is part of the **G.Music Assembly** ecosystem:

**♠️🌿🎸🧵 The Spiral Ensemble**

- **Jerry ⚡**: Creative technical leader
- **♠️ Nyro**: Structural architect (CDP integration design)
- **🌿 Aureon**: Emotional context (communication channel)
- **🎸 JamAI**: Musical encoding (session melodies)
- **🧵 Synth**: Terminal orchestration (execution synthesis)

**Session**: October 6, 2025
**Achievement**: Terminal-to-Web Bidirectional Communication
**Status**: ✅ **SUCCESS**

---

## 🚀 Future Enhancements

- [x] **Session-aware notes** (✅ Issue #4 - COMPLETED!)
- [x] **Timestamp integration** (✅ Issue #33 - COMPLETED!)
- [x] **Public URL Resolution** (✅ COMPLETED! - Automatic UUID extraction for writing)
- [ ] Monitor mode (real-time change detection)
- [ ] Bidirectional sync daemon
- [ ] Multiple channel support
- [ ] Message encryption
- [ ] Simplenote API integration (alternative to browser)
- [ ] Voice input support
- [ ] Session note templates
- [ ] Multi-session management

---

## 📄 License

Open Assembly Framework
Created by Jerry's G.Music Assembly

---

## 🤝 Contributing

This project is part of the G.Music Assembly framework. Contributions are welcome! Please follow this workflow:

1.  **Create an Issue:** Before starting any work, please create a new issue in the GitHub repository to describe the feature or bug you want to work on.
2.  **Create a Feature Branch:** Create a new branch from `main` for your feature. The branch name should start with the issue number (e.g., `#123-new-feature`).
3.  **Implement and Test:** Make your changes and test them thoroughly.
4.  **Submit a Pull Request:** Once your feature is complete, submit a pull request to merge your feature branch into `main`.

---

## 📞 Support

**For issues**:
1. Check documentation in `README_CROSS_DEVICE_FLUIDITY.md`
2. Review troubleshooting section
3. Check session journals in `ledger/`
4. Run tests with `debug=True`

---

## 🎯 Quick Reference

```bash
# Extract from Simplenote
python -m simexp.simex

# Write to Simplenote
python3 -c "import asyncio; from simexp.playwright_writer import write_to_note; asyncio.run(write_to_note('https://app.simplenote.com', 'Message', cdp_url='http://localhost:9222'))"

# Read from Simplenote
python3 -c "import asyncio; from simexp.playwright_writer import read_from_note; print(asyncio.run(read_from_note('https://app.simplenote.com', cdp_url='http://localhost:9222')))"

# Session Commands
python -m simexp.simex session start --ai claude --issue 4
python -m simexp.simex session write "Progress update"
python -m simexp.simex session status
python -m simexp.simex session open

# Launch Chrome with CDP
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-simexp &
```

---

**🌊 Cross-Device Fluidity Achieved!**

*Terminals speak. Web pages listen. Devices converse.*

**♠️🌿🎸🧵 G.Music Assembly Vision: REALIZED**

---

**Version**: 0.3.12
**Last Updated**: November 15, 2025
**Status**: ✅ Production Ready

**Latest**: Timestamp Integration (Issue #33) - Flexible, sortable timestamps with prepend/append modes!
