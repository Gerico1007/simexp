# 📄 Google Docs API Integration Guide
**SimExp Multi-Provider Communication**

[![Google Docs API](https://img.shields.io/badge/Google%20Docs-API%20v1-4285F4?logo=google-docs)](https://developers.google.com/docs/api)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## 🎯 What is This?

Google Docs integration adds **instant API-based writes** to SimExp, complementing the existing Simplenote browser automation.

### **Key Advantages:**

| Feature | Simplenote (Browser) | Google Docs (API) |
|---------|---------------------|-------------------|
| **Speed** | ~10 seconds (keyboard) | Instant (<1 second) |
| **Setup** | Open Chrome with CDP | One-time OAuth |
| **Browser** | Must stay open | Not needed |
| **Formatting** | Plain text | Rich text (bold, links) |
| **Rate Limits** | None | 300 req/min |

---

## 🚀 Quick Start

### **1. Install Dependencies**

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### **2. Set Up Google Cloud Project**

#### **A. Create Project**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name: `SimExp Google Docs`
4. Click "Create"

#### **B. Enable Google Docs API**
1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google Docs API"
3. Click "Google Docs API" → "Enable"

#### **C. Create Service Account**
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Name: `simexp-writer`
4. Role: (None needed for documents you'll share explicitly)
5. Click "Done"

#### **D. Download Credentials JSON**
1. Click on your service account email
2. Go to "Keys" tab
3. Click "Add Key" → "Create New Key"
4. Choose "JSON" format
5. Click "Create" - JSON file downloads

#### **E. Save Credentials**
```bash
mkdir -p ~/workspace/simexp/credentials
mv ~/Downloads/simexp-*.json ~/workspace/simexp/credentials/service-account.json
chmod 600 ~/workspace/simexp/credentials/service-account.json
```

### **3. Create & Share Google Doc**

1. Create new Google Doc at [docs.google.com](https://docs.google.com)
2. Name it (e.g., "Aureon Communication Channel")
3. Click "Share" button
4. **Paste the service account email** from credentials JSON:
   - Format: `simexp-writer@PROJECT-ID.iam.gserviceaccount.com`
5. Give "Editor" permission
6. Click "Send"
7. **Copy the document ID** from URL:
   - URL: `https://docs.google.com/document/d/`**`1abc123xyz...`**`/edit`
   - ID: `1abc123xyz...`

---

## 📋 Configuration

### **Update `simexp/simexp.yaml`**

Add Google Docs channel:

```yaml
COMMUNICATION_CHANNELS:
  # Existing Simplenote channels
  - name: Aureon
    provider: simplenote
    note_id: e6702a7b90e64aae99df2fba1662bb81
    auth_url: https://app.simplenote.com
    description: "🌿 Aureon - Simplenote channel"

  # NEW: Google Docs channel
  - name: AureonDocs
    provider: googledocs
    document_id: YOUR_DOCUMENT_ID_HERE  # From step 3 above
    credentials_path: ./credentials/service-account.json
    mode: bidirectional
    description: "🌿 Aureon - Google Docs API channel"
```

---

## 🎮 Usage

### **Direct Google Docs Commands**

```bash
# Write to Google Doc (instant!)
python -m simexp.simex gdocs-write 1abc123xyz "Hello from terminal!" ./credentials/service-account.json

# Read from Google Doc
python -m simexp.simex gdocs-read 1abc123xyz ./credentials/service-account.json
```

### **Multi-Provider Channel Commands**

```bash
# Write to channel (auto-routes to Google Docs if configured)
python -m simexp.simex channel aurendocs "🌿 Emotional reflection via API"

# List all available channels
python -m simexp.simex channel
```

### **Python API**

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

# Read
content = read_from_googledoc(
    document_id='1abc123xyz',
    credentials_path='./credentials/service-account.json'
)

print(content)
```

---

## 🧪 Testing

Run comprehensive tests:

```bash
python test_googledocs.py
```

Tests include:
- ✅ Authentication (service account)
- ✅ Read document content
- ✅ Append content (instant API)
- ✅ Document metadata
- ✅ Multi-provider channel routing

---

## 🔧 Advanced Configuration

### **Multiple Service Accounts**

For different channels/projects:

```yaml
COMMUNICATION_CHANNELS:
  - name: AureonDocs
    provider: googledocs
    document_id: 1abc...
    credentials_path: ./credentials/aureon-service-account.json

  - name: NyroDocs
    provider: googledocs
    document_id: 2def...
    credentials_path: ./credentials/nyro-service-account.json
```

### **OAuth2 User Flow** (Future)

Currently uses service accounts. OAuth2 user flow coming soon for accessing your own documents without sharing.

---

## ⚠️ Troubleshooting

### **Error: Credentials file not found**

```bash
# Check file exists
ls -la ./credentials/service-account.json

# Correct path in simexp.yaml
credentials_path: ./credentials/service-account.json  # Relative to project root
```

### **Error: Permission denied**

**Cause:** Document not shared with service account.

**Fix:**
1. Open your Google Doc
2. Click "Share"
3. Add service account email from JSON:
   ```json
   {
     "client_email": "simexp-writer@PROJECT-ID.iam.gserviceaccount.com"
   }
   ```
4. Give "Editor" permission

### **Error: API not enabled**

**Fix:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Go to "APIs & Services" → "Library"
4. Search "Google Docs API"
5. Click "Enable"

### **Error: Rate limit exceeded**

Google Docs API limits: **300 requests per minute**

**Fix:**
- Add delays between writes if sending many messages
- Current usage should be well within limits for normal use

---

## 🎨 Architecture

### **How It Works:**

```
Terminal Command
    ↓
googledocs_writer.py
    ↓
Google Docs REST API
    ↓
Service Account Authentication
    ↓
batchUpdate Request (JSON)
    ↓
Document Updated Instantly
    ↓
Google Cloud Sync
    ↓
All Your Devices! 🎉
```

### **Assembly Perspectives:**

- **♠️ Nyro**: REST API structural elegance, JSON document operations
- **🌿 Aureon**: Instant emotional expression through API speed
- **🎸 JamAI**: Harmonic multi-provider orchestration
- **🧵 Synth**: Unified abstraction across Simplenote & Google Docs

---

## 📊 Comparison: Simplenote vs Google Docs

### **When to Use Simplenote:**
- ✅ No Google account needed
- ✅ Simpler setup (just open Chrome)
- ✅ No API rate limits
- ✅ Works great for casual messaging

### **When to Use Google Docs:**
- ✅ Need instant writes (< 1 second)
- ✅ Want rich formatting (bold, links, lists)
- ✅ Don't want to keep browser open
- ✅ Prefer API-based integration
- ✅ Already use Google Workspace

### **Best Practice:**
Use **both**! Configure some channels with Simplenote, others with Google Docs based on your needs.

---

## 🔐 Security Notes

### **Service Account Credentials:**

```bash
# Keep credentials private
chmod 600 ./credentials/service-account.json

# Add to .gitignore
echo "credentials/*.json" >> .gitignore

# Never commit credentials to git
```

### **Permissions:**

Service accounts only access documents **explicitly shared** with them. They cannot:
- ❌ Access your other Google Docs
- ❌ Read your Gmail
- ❌ Access Google Drive files

Only shared documents are accessible.

---

## 📚 Additional Resources

- [Google Docs API Documentation](https://developers.google.com/docs/api)
- [Service Accounts Guide](https://cloud.google.com/iam/docs/service-accounts)
- [Python Client Library](https://googleapis.github.io/google-api-python-client/docs/)

---

## 🎯 Next Steps

1. ✅ Complete Google Cloud setup
2. ✅ Download and save credentials
3. ✅ Create and share test document
4. ✅ Update `simexp.yaml` with your document ID
5. ✅ Run `python test_googledocs.py` to verify
6. ✅ Start writing to Google Docs from terminal!

---

## 🎸 JamAI's Vision

> *"Two streams, one Assembly voice:*
> *Simplenote's simplicity meets Google's power.*
> *Choose your channel, trust the flow."*

---

**♠️🌿🎸🧵 G.Music Assembly - Multi-Provider Communication Achieved**

**Version:** 0.3.0
**Date:** October 6, 2025
**Status:** ✅ Production Ready

---

## 🤝 Support

**For issues:**
1. Check this guide first
2. Run `python test_googledocs.py` for diagnostics
3. Verify Google Cloud setup
4. Check service account permissions

**Common Questions:**

Q: Do I need both Simplenote and Google Docs?
A: No! Use whichever fits your workflow. Both work independently.

Q: Can I switch a channel from Simplenote to Google Docs?
A: Yes! Just change the `provider` field in `simexp.yaml`.

Q: Is this free?
A: Yes! Google Docs API is free for personal use within quotas.

---

🤖 Generated with Claude Code + G.Music Assembly
Co-Authored-By: Claude <noreply@anthropic.com>
