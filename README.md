# 🌊 SimExp - Multi-Provider Content Writer & Extractor
**Cross-Device Fluidity: Terminal ↔ Web Communication**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Google Docs API](https://img.shields.io/badge/Google%20Docs-API%20v1-4285F4?logo=google-docs)](https://developers.google.com/docs/api)
[![License](https://img.shields.io/badge/license-Open%20Assembly-green.svg)]()

---

## 🎯 What is SimExp?

SimExp is a bidirectional communication tool that bridges terminals with **Simplenote** and **Google Docs**:

1. **📖 Extract**: Fetch and archive web content from Simplenote URLs
2. **✍️ Write**: Send messages from terminal to Simplenote (browser) OR Google Docs (API)
3. **🌊 Sync**: Enable cross-device communication through cloud sync
4. **⚡ Instant API**: Write to Google Docs in < 1 second (no browser needed!)

**Key Achievement**: **Multi-provider communication** - Choose Simplenote's simplicity OR Google's speed!

---

## 🚀 Quick Start

### For Terminal-to-Web Writing (The Cool New Feature!)

```bash
# 1. Install dependencies
pip install playwright pyperclip beautifulsoup4 pyyaml requests
playwright install chromium

# 2. Launch Chrome with remote debugging
google-chrome --remote-debugging-port=9223 --user-data-dir=/tmp/chrome-simexp &

# 3. Login to Simplenote in the Chrome window that opens
# Go to: https://app.simplenote.com

# 4. Write from terminal to Simplenote!
python3 -c "
import asyncio
from simexp.playwright_writer import write_to_note

asyncio.run(write_to_note(
    'https://app.simplenote.com',
    'Hello from terminal! 🌊',
    cdp_url='http://localhost:9223'
))
"

# 5. Check your Simplenote note - the message is there!
# 6. Check from your phone - it synced! ✨
```

**👉 [Full Simplenote Setup Guide](README_CROSS_DEVICE_FLUIDITY.md)**

### NEW: Google Docs API (Instant Writes!)

```bash
# 1. Install Google API dependencies
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# 2. Set up Google Cloud service account (one-time, ~10 min)
#    See: QUICKSTART_GOOGLEDOCS.md

# 3. Write to Google Docs instantly!
python -m simexp.simex gdocs-write YOUR_DOC_ID "Hello from API!" ./credentials/service-account.json

# 4. Or use channel command (works for both Simplenote AND Google Docs!)
python -m simexp.simex channel mychannel "Message here"
```

**👉 [Quick Start: Google Docs](QUICKSTART_GOOGLEDOCS.md)** | **👉 [Full Google Docs Guide](README_GOOGLEDOCS.md)**

---

## 📊 Provider Comparison

| Feature | Simplenote | Google Docs |
|---------|------------|-------------|
| **Speed** | ~10 seconds | **< 1 second** ⚡ |
| **Setup** | Open Chrome with CDP | One-time OAuth |
| **Browser** | Must stay open | **Not needed** |
| **Method** | Keyboard simulation | **REST API** |
| **Formatting** | Plain text | Rich text ready |
| **Rate Limits** | None | 300 req/min |

**Use both!** Configure some channels with Simplenote, others with Google Docs.

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

### Extract Content from Simplenote URLs

```bash
# Copy a Simplenote URL to clipboard
# Example: https://app.simplenote.com/p/0ZqWsQ

# Run extraction
python -m simexp.simex

# Content saved to ./output/YYYYMMDD/filename.md
```

---

### Write from Terminal to Simplenote

**Method 1: Python Script**

```python
import asyncio
from simexp.playwright_writer import write_to_note

# Write a message
result = asyncio.run(write_to_note(
    note_url='https://app.simplenote.com',
    content='Your message here!',
    mode='append',  # or 'replace'
    cdp_url='http://localhost:9223'
))

print(f"Success: {result['success']}")
```

**Method 2: One-Liner**

```bash
python3 -c "import asyncio; from simexp.playwright_writer import write_to_note; asyncio.run(write_to_note('https://app.simplenote.com', 'Quick message!', cdp_url='http://localhost:9223'))"
```

**Method 3: Bash Alias** (add to ~/.bashrc)

```bash
alias simwrite='python3 -c "import asyncio; from simexp.playwright_writer import write_to_note; asyncio.run(write_to_note(\"https://app.simplenote.com\", \"'\''\$1'\''\", cdp_url=\"http://localhost:9223\"))"'

# Then use it:
simwrite "Message from terminal!"
```

---

### Read from Simplenote

```python
import asyncio
from simexp.playwright_writer import read_from_note

content = asyncio.run(read_from_note(
    note_url='https://app.simplenote.com',
    cdp_url='http://localhost:9223'
))

print(content)
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

### Manual Test

```bash
# 1. Launch Chrome with debugging
google-chrome --remote-debugging-port=9223 --user-data-dir=/tmp/chrome-simexp &

# 2. Login to Simplenote in Chrome window

# 3. Test write
python3 -c "
import asyncio
from simexp.playwright_writer import write_to_note

result = asyncio.run(write_to_note(
    'https://app.simplenote.com',
    '🔮 TEST MESSAGE - If you see this, it works!',
    cdp_url='http://localhost:9223',
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

### "Connection refused" to localhost:9223

Chrome not running with remote debugging:
```bash
google-chrome --remote-debugging-port=9223 --user-data-dir=/tmp/chrome-simexp &
curl http://localhost:9223/json/version  # Should return JSON
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

- [ ] Monitor mode (real-time change detection)
- [ ] Bidirectional sync daemon
- [ ] Multiple channel support
- [ ] Message encryption
- [ ] Simplenote API integration (alternative to browser)
- [ ] Voice input support

---

## 📄 License

Open Assembly Framework
Created by Jerry's G.Music Assembly

---

## 🤝 Contributing

This project is part of the G.Music Assembly framework. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Test your changes
4. Submit a pull request

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
python3 -c "import asyncio; from simexp.playwright_writer import write_to_note; asyncio.run(write_to_note('https://app.simplenote.com', 'Message', cdp_url='http://localhost:9223'))"

# Read from Simplenote
python3 -c "import asyncio; from simexp.playwright_writer import read_from_note; print(asyncio.run(read_from_note('https://app.simplenote.com', cdp_url='http://localhost:9223')))"

# Launch Chrome with CDP
google-chrome --remote-debugging-port=9223 --user-data-dir=/tmp/chrome-simexp &
```

---

**🌊 Cross-Device Fluidity Achieved!**

*Terminals speak. Web pages listen. Devices converse.*

**♠️🌿🎸🧵 G.Music Assembly Vision: REALIZED**

---

**Version**: 0.2.4
**Last Updated**: October 6, 2025
**Status**: ✅ Production Ready
