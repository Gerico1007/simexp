# 🧵 Synth - MCP Chrome DevTools Integration Guide
**SimExp Cross-Device Communication Protocol**

## 🌐 Vision: Terminal ↔ Web Bidirectional Flow

Jerry's vision: Use Simplenote as a communication medium between devices, with terminals able to **write** to web pages through MCP Chrome DevTools integration.

## ✅ Current Infrastructure Status

### Completed (Ready for MCP):
- ✅ Playwright async architecture (`simexp/playwright_writer.py`)
- ✅ DOM injection logic with multiple selector strategies
- ✅ CLI commands: `simexp write` and `simexp read`
- ✅ Configuration system with communication channels
- ✅ Aureon note configured as primary channel
- ✅ Test scripts ready (`test_mcp_write.py`)

### Waiting for:
- ⏳ MCP Chrome DevTools server connection to Claude Code
- ⏳ Authenticated browser session with Simplenote login

## 🎯 Aureon Communication Channel

**Configured in** `simexp/simexp.yaml`:

```yaml
COMMUNICATION_CHANNELS:
  - name: Aureon
    note_id: e6702a7b90e64aae99df2fba1662bb81
    public_url: https://app.simplenote.com/p/gk6V2v
    auth_url: https://app.simplenote.com/note/e6702a7b90e64aae99df2fba1662bb81
    protocol_url: simplenote://note/e6702a7b90e64aae99df2fba1662bb81
    mode: bidirectional
    description: "🌿 Aureon - Mirror Weaver communication channel"
```

**Current Status:**
- ✅ Public URL readable
- ⚠️ Auth URL requires login (waiting for MCP)

## 🔧 MCP Integration Setup

### Step 1: Install MCP Chrome DevTools Server

```bash
# Install the MCP server (when available)
npm install -g @modelcontextprotocol/server-chrome-devtools

# Or follow Claude Code documentation
```

### Step 2: Connect to Claude Code

Add to your Claude Code MCP configuration:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "chrome-devtools-mcp",
      "args": ["--port", "9222"]
    }
  }
}
```

### Step 3: Ensure Browser Session

1. Open Chrome with remote debugging:
   ```bash
   chromium --remote-debugging-port=9222
   ```

2. Log into Simplenote: `https://app.simplenote.com`

3. Keep browser session active

### Step 4: Test Write Flow

```bash
# Run test script
python test_mcp_write.py

# Or use CLI directly
python -m simexp.simex write https://app.simplenote.com/note/e6702a7b90e64aae99df2fba1662bb81 "Test message"
```

## 🎼 Architecture Flow

```
┌─────────────────┐
│  Terminal       │
│  (Jerry types)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ SimExp CLI      │
│ simexp write    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Playwright      │
│ Writer Module   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ MCP Chrome      │
│ DevTools Server │ ← Connected to authenticated Chrome
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Simplenote Web  │
│ (Aureon Note)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Other Devices   │
│ (Read changes)  │
└─────────────────┘
```

## 🔍 DOM Selector Strategy

When MCP connects, Playwright will try these selectors in order:

1. `textarea.note-editor`
2. `textarea[class*="note"]`
3. `textarea[class*="editor"]`
4. `div.note-editor`
5. `div[contenteditable="true"]`
6. `[contenteditable="true"]`
7. `textarea`
8. `.CodeMirror textarea`

**Fallback:** Screenshot saved to `/tmp/simplenote_debug.png` for debugging

## 🛠️ Troubleshooting

### Issue: "Could not find editor element"
**Cause:** Not authenticated or wrong URL format
**Solution:** Ensure logged into Simplenote and using `auth_url` not `public_url`

### Issue: "Write verification failed"
**Cause:** Simplenote autosave may be delayed
**Solution:** Increase wait time after injection (currently 1 second)

### Issue: MCP not connecting
**Cause:** Chrome not running with remote debugging
**Solution:**
```bash
chromium --remote-debugging-port=9222 &
```

## 📝 Usage Examples

### Write to Aureon Note:
```bash
# Direct message
simexp write https://app.simplenote.com/note/e6702a7b90e64aae99df2fba1662bb81 "Hello from terminal!"

# From stdin
echo "Cross-device message" | simexp write https://app.simplenote.com/note/e6702a7b90e64aae99df2fba1662bb81

# Multi-line
cat message.txt | simexp write https://app.simplenote.com/note/e6702a7b90e64aae99df2fba1662bb81
```

### Read from Aureon Note:
```bash
simexp read https://app.simplenote.com/note/e6702a7b90e64aae99df2fba1662bb81
```

## 🔮 Future Enhancements

- **Monitor Mode**: Real-time change detection with polling
- **Sync Daemon**: Bidirectional background sync
- **Multi-Channel**: Support multiple Assembly perspective channels (Nyro, JamAI, Synth)
- **Encryption**: Optional message encryption for sensitive content
- **API Integration**: Simperium API for more stable sync

## 🎸 Assembly Perspectives

**♠️ Nyro**: DOM structure analysis and selector pattern optimization
**🌿 Aureon**: Content emotional context and communication flow
**🎸 JamAI**: Musical encoding of cross-device conversations
**🧵 Synth**: MCP orchestration, authentication synthesis, execution anchor

---

**Status**: Infrastructure ready, awaiting MCP connection
**Next Step**: Connect Chrome DevTools MCP server to Claude Code
**Test Command**: `python test_mcp_write.py`

**♠️🌿🎸🧵 Assembly Ready for Cross-Device Flow!**
