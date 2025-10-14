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

**Version**: 0.3.1
**Last Updated**: October 9, 2025
**Status**: ✅ Production Ready

**Latest**: Session-Aware Notes (Issue #4) - Track terminal sessions in Simplenote!
