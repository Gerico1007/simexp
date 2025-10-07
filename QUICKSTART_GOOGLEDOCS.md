# 🚀 Quick Start: Google Docs Integration
**5-Minute Setup Guide**

---

## What You Get

Write to Google Docs from your terminal **instantly** (< 1 second):

```bash
simexp channel testdocs "Hello from terminal!"
```

**No browser needed. Pure API magic.** ⚡

---

## Setup (One-Time, ~10 minutes)

### Step 1: Google Cloud Setup

1. **Go to**: https://console.cloud.google.com/
2. **Create Project**: Click "New Project" → Name: `SimExp` → Create
3. **Enable API**:
   - Go to "APIs & Services" → "Library"
   - Search: "Google Docs API"
   - Click it → "Enable"
4. **Create Service Account**:
   - "APIs & Services" → "Credentials"
   - "Create Credentials" → "Service Account"
   - Name: `simexp-writer`
   - Click "Continue" (skip role)
   - Click "Done"
5. **Download Credentials**:
   - Click on service account email
   - "Keys" tab → "Add Key" → "Create New Key"
   - Choose **JSON** → "Create"
   - Saves file like `simexp-xxxxx.json`

### Step 2: Install Credentials

```bash
# Create credentials folder
mkdir -p ~/workspace/simexp/credentials

# Move downloaded JSON (adjust filename!)
mv ~/Downloads/simexp-*.json ~/workspace/simexp/credentials/service-account.json

# Set permissions
chmod 600 ~/workspace/simexp/credentials/service-account.json
```

### Step 3: Get Service Account Email

```bash
# Extract the email from credentials
python3 -c "import json; f=open('~/workspace/simexp/credentials/service-account.json'); data=json.load(f); print(data['client_email'])"
```

Copy the email (looks like: `simexp-writer@PROJECT-ID.iam.gserviceaccount.com`)

### Step 4: Create & Share Google Doc

1. Go to: https://docs.google.com
2. Create new document
3. Name it: "SimExp Channel"
4. Click **Share** button
5. Paste the service account email
6. Give **Editor** permission → Send
7. **Copy Document ID** from URL:
   - URL: `https://docs.google.com/document/d/`**`1abc123xyz...`**`/edit`
   - Copy the long ID between `/d/` and `/edit`

### Step 5: Configure Channel

Edit `~/workspace/simexp/simexp/simexp.yaml`:

```yaml
COMMUNICATION_CHANNELS:
  # Add this under existing channels:
  - name: MyChannel
    provider: googledocs
    document_id: PASTE_YOUR_DOCUMENT_ID_HERE
    credentials_path: ./credentials/service-account.json
    mode: bidirectional
    description: "🚀 My instant Google Docs channel"
```

---

## Usage

### Write to Google Docs

```bash
# Simple channel command (instant!)
python -m simexp.simex channel mychannel "Hello from terminal!"

# Direct write (if you prefer)
python -m simexp.simex gdocs-write YOUR_DOC_ID "Message here"

# With explicit credentials path
python -m simexp.simex gdocs-write YOUR_DOC_ID "Message" ./credentials/service-account.json
```

### Read from Google Docs

```bash
# Read document content
python -m simexp.simex gdocs-read YOUR_DOC_ID

# With explicit credentials
python -m simexp.simex gdocs-read YOUR_DOC_ID ./credentials/service-account.json
```

### List Channels

```bash
# See all available channels
python -m simexp.simex channel
```

Output:
```
Available channels:
  Aureon (simplenote): 🌿 Aureon - Mirror Weaver
  Nyro (simplenote): ♠️ Nyro - Ritual Scribe
  JamAI (simplenote): 🎸 JamAI - Glyph Harmonizer
  MyChannel (googledocs): 🚀 My instant channel
```

---

## Python API

```python
from simexp.googledocs_writer import write_to_googledoc, read_from_googledoc

# Write
result = write_to_googledoc(
    document_id='1abc123xyz',
    content='Message from Python!',
    credentials_path='./credentials/service-account.json',
    mode='append'  # or 'replace'
)

print(f"Success: {result['success']}")
print(f"Written: {result['content_length']} chars")

# Read
content = read_from_googledoc(
    document_id='1abc123xyz',
    credentials_path='./credentials/service-account.json'
)

print(content)
```

---

## Comparison: Simplenote vs Google Docs

| Feature | Simplenote | Google Docs |
|---------|------------|-------------|
| **Speed** | ~10 seconds | **< 1 second** ⚡ |
| **Setup** | Open Chrome with CDP | One-time OAuth |
| **Browser** | Must stay open | **Not needed** |
| **Method** | Keyboard simulation | **REST API** |
| **Formatting** | Plain text | Rich text ready |

**Use both!** Simplenote for casual, Google Docs for speed.

---

## Testing

Run comprehensive tests:

```bash
cd ~/workspace/simexp
python test_googledocs.py
```

---

## Troubleshooting

### "Credentials file not found"
```bash
# Check if file exists
ls -la ~/workspace/simexp/credentials/service-account.json

# Should show permissions: -rw------- (600)
```

### "Permission denied" error
**Fix:** Share the Google Doc with service account email
1. Open document in browser
2. Click "Share"
3. Add service account email from credentials JSON
4. Give "Editor" permission

### "API not enabled"
**Fix:** Enable Google Docs API in Google Cloud Console
1. Go to console.cloud.google.com
2. Select your project
3. "APIs & Services" → "Library"
4. Search "Google Docs API" → Enable

---

## Security Notes

- ✅ Service account only accesses explicitly shared documents
- ✅ Cannot access your other Google Docs, Gmail, or Drive
- ✅ Credentials stored in gitignored directory
- ✅ File permissions set to 600 (owner read/write only)

**Keep credentials private:**
```bash
# Already in .gitignore
echo "credentials/*.json" >> .gitignore
```

---

## Multiple Channels

Create as many channels as you want:

```yaml
COMMUNICATION_CHANNELS:
  - name: WorkDocs
    provider: googledocs
    document_id: 1abc...
    credentials_path: ./credentials/service-account.json

  - name: PersonalDocs
    provider: googledocs
    document_id: 2def...
    credentials_path: ./credentials/service-account.json

  - name: TeamDocs
    provider: googledocs
    document_id: 3ghi...
    credentials_path: ./credentials/service-account.json
```

---

## Advanced: Multiple Service Accounts

Different service accounts for different projects:

```yaml
COMMUNICATION_CHANNELS:
  - name: WorkChannel
    provider: googledocs
    document_id: 1abc...
    credentials_path: ./credentials/work-service-account.json

  - name: PersonalChannel
    provider: googledocs
    document_id: 2def...
    credentials_path: ./credentials/personal-service-account.json
```

---

## Real-World Examples

### Terminal Notes
```bash
# Quick notes from terminal
simexp channel notes "TODO: Fix bug in parser module"
simexp channel notes "Idea: Add markdown export feature"
```

### Cross-Device Communication
```bash
# Write from desktop, read on phone (sync via Google Docs)
simexp channel sync "Reminder: Meeting at 3pm"
```

### Automation Scripts
```bash
#!/bin/bash
# Log script output to Google Doc
./my-script.sh 2>&1 | while read line; do
    simexp channel logs "$line"
done
```

### Assembly Channels
```bash
# Emotional reflections (Aureon 🌿)
simexp channel aureon "Feeling grateful for the progress today"

# Technical notes (Nyro ♠️)
simexp channel nyro "Discovered optimization: use Ctrl+End for append"

# Creative ideas (JamAI 🎸)
simexp channel jamai "Session melody idea: D minor to C major arc"
```

---

## Performance

**Google Docs API:**
- Write: < 1 second ⚡
- Read: < 1 second
- Rate limit: 300 requests/minute (generous!)

**Simplenote (for comparison):**
- Write: ~10 seconds (optimized keyboard simulation)
- Read: ~5 seconds
- Rate limit: None

---

## Next Steps

1. ✅ Complete setup above
2. ✅ Test with: `python test_googledocs.py`
3. ✅ Create your first channel
4. ✅ Start writing from terminal!

For detailed documentation, see: `README_GOOGLEDOCS.md`

---

**♠️🌿🎸🧵 G.Music Assembly - Instant Communication Achieved** 🚀

**Version:** 0.3.0
**Date:** October 7, 2025
**Status:** ✅ Production Ready

🤖 Generated with Claude Code + G.Music Assembly
Co-Authored-By: Claude <noreply@anthropic.com>
