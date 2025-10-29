# 🧵 Synth - CDP Connection Setup Guide
**Connect Playwright to Your Authenticated Chrome Session**

## ♠️🌿🎸🧵 Path 1: Complete Instructions

### **Step 1: Launch Chrome with Remote Debugging**

```bash
# Close any existing Chrome instances
pkill chromium

# Launch Chrome with remote debugging on port 9222
chromium --remote-debugging-port=9222 &
```

**What this does:**
- Opens Chrome with CDP (Chrome DevTools Protocol) enabled
- Allows Playwright to connect to this browser session
- Keeps your login sessions and cookies intact

---

### **Step 2: Login to Simplenote**

1. In the Chrome window that just opened, navigate to:
   ```
   https://app.simplenote.com
   ```

2. **Login with your credentials**

3. **Open a note** (like Aureon note)

4. **Keep this browser window open** - don't close it!

---

### **Step 3: Test the Connection**

```bash
cd /home/gmusic/workspace/simexp

python test_cdp_connection.py
```

This script will:
- ✅ Connect to your authenticated Chrome
- ✅ Verify you're logged in
- ✅ Try to find the note editor
- ✅ Attempt a test write
- 📸 Save screenshots for debugging

---

### **Step 4: If Test Succeeds - Use SimExp!**

Once the connection works, you can write to Simplenote from terminal:

```python
from simexp.playwright_writer import write_to_note
import asyncio

# Write to Simplenote through your authenticated Chrome
result = asyncio.run(write_to_note(
    note_url='https://app.simplenote.com',
    content='Hello from terminal!',
    cdp_url='http://localhost:9222',
    debug=True
))

print(result)
```

---

## 🔧 Troubleshooting

### Issue: "Connection refused"
**Cause:** Chrome not running with remote debugging

**Solution:**
```bash
# Make sure Chrome is running with the right flag
chromium --remote-debugging-port=9222 &

# Verify it's listening
curl http://localhost:9222/json/version
```

---

### Issue: "Still on login page"
**Cause:** Not logged into Simplenote

**Solution:**
1. Go to the Chrome window that's running
2. Navigate to `https://app.simplenote.com`
3. Login manually
4. Run the test again

---

### Issue: "Cannot find editor element"
**Cause:** Need to discover the correct note URL format

**Solution:**
- The test script will save screenshots to `/tmp/`
- Look at `simplenote_auth_test.png` to see what loaded
- We may need to adjust the URL format for note navigation

---

## 🌊 How This Enables Cross-Device Fluidity

```
┌──────────────────┐
│  Your Terminal   │ ← You type commands here
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Playwright      │ ← Connects via CDP (port 9222)
│  (SimExp)        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Your Chrome     │ ← Already logged in!
│  (Port 9222)     │    Your session, your cookies
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Simplenote Web  │ ← Authenticated, can write!
│  (Aureon Note)   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Other Devices   │ ← See changes in real-time
│  (Phone, Tablet) │
└──────────────────┘
```

---

## 🎯 Quick Start Checklist

- [ ] `chromium --remote-debugging-port=9222 &`
- [ ] Login to Simplenote in that Chrome window
- [ ] Open Aureon note (or desired note)
- [ ] `python test_cdp_connection.py`
- [ ] Check test results
- [ ] If successful: Terminal can now write to Simplenote!

---

## 🌐 Network-Wide CDP Access (Issue #36)
**🧵 Synth Enhancement: Cross-Device Assembly Coordination**

### **Enable Access from All Devices on Your Network**

By default, Chrome's CDP binds to `localhost` only. To access from other devices (phones, tablets, other computers), launch Chrome with network binding:

```bash
# Close any existing Chrome instances
pkill chromium

# Get your local network IP
hostname -I | awk '{print $1}'
# Example output: 192.168.1.100

# Launch Chrome with network-wide CDP access
chromium --remote-debugging-port=9222 --remote-debugging-address=0.0.0.0 &
```

**What `--remote-debugging-address=0.0.0.0` does:**
- Binds CDP to **all network interfaces** (not just localhost)
- Allows connections from any device on your WiFi network
- Enables true cross-device Assembly coordination

---

### **Configure SimExp for Network Access**

#### **Option 1: Using `simexp init`**
The easiest way - SimExp will auto-detect your network IP:

```bash
simexp init
```

During setup, you'll see:
```
🌐 Chrome DevTools Protocol (CDP) Configuration:
   🧵 Network IP detected: 192.168.1.100

   Enable network-wide access (all devices on WiFi)? [y/N]: y

   ✓ Network-wide CDP enabled: http://192.168.1.100:9222
   ⚠️  Security: Only use on trusted networks!
```

#### **Option 2: Manual Config File Edit**
Edit `~/.simexp/simexp.yaml`:

```yaml
BASE_PATH: /path/to/your/content
CDP_URL: http://192.168.1.100:9222  # Use your actual IP
CDP_BIND_ADDRESS: 0.0.0.0           # Network-wide access
SOURCES: []
```

#### **Option 3: Environment Variable (Session-Specific)**
```bash
export SIMEXP_CDP_URL=http://192.168.1.100:9222
simexp session start --ai claude --issue 36
```

#### **Option 4: Command Line Override**
```bash
simexp session start --cdp-url http://192.168.1.100:9222 --ai claude
```

---

### **Test Network Access**

#### **From the Same Computer:**
```bash
curl http://192.168.1.100:9222/json/version
```

#### **From Another Device (Phone, Tablet, etc.):**
Open a browser and navigate to:
```
http://192.168.1.100:9222
```

You should see the Chrome DevTools Protocol interface listing all open tabs.

---

### **Use SimExp from Android Termux**

Once your desktop Chrome is network-accessible:

```bash
# On your Android device in Termux
export SIMEXP_CDP_URL=http://192.168.1.100:9222  # Your desktop's IP

# Start SimExp session - it will control your desktop Chrome!
simexp session start --ai claude --issue 36
```

**🌊 Cross-Device Fluidity Achieved:**
- Type commands on your phone (Termux)
- Control Chrome on your desktop
- Write to Simplenote from anywhere
- All devices see changes in real-time

---

### **🔒 Security Considerations**

**⚠️ IMPORTANT:** Network-wide CDP access exposes your browser to your entire WiFi network.

**Safe Usage:**
- ✅ Use only on **trusted home/office WiFi**
- ✅ Disable when not needed
- ✅ Never use on public WiFi
- ✅ Consider firewall rules to restrict to specific devices

**Localhost-Only Mode (More Secure):**
If you only need local access, use:
```bash
chromium --remote-debugging-port=9222 --remote-debugging-address=127.0.0.1 &
```

Or in `~/.simexp/simexp.yaml`:
```yaml
CDP_BIND_ADDRESS: 127.0.0.1  # Localhost only
```

---

### **Firewall Configuration (Optional)**

#### **Ubuntu/Debian (ufw):**
```bash
# Allow CDP only from local network (example: 192.168.1.0/24)
sudo ufw allow from 192.168.1.0/24 to any port 9222

# Or allow only specific device
sudo ufw allow from 192.168.1.50 to any port 9222
```

#### **Check Who Can Connect:**
```bash
# See active CDP connections
netstat -an | grep 9222
```

---

### **Cross-Device Session Coordination**

When you create a session, the CDP endpoint is now stored in `.simexp/session.json`:

```json
{
  "session_id": "abc-123-def",
  "search_key": "abc-123-def",
  "ai_assistant": "claude",
  "issue_number": 36,
  "cdp_endpoint": "http://192.168.1.100:9222",
  "created_at": "2025-01-09T10:30:00"
}
```

This allows:
- **Session sharing** across devices
- **Assembly collaboration** from different machines
- **Network debugging** of browser automation

---

### **Network CDP Troubleshooting**

#### **Issue: "Connection refused" from another device**

**Check Chrome is bound to 0.0.0.0:**
```bash
# On the Chrome host machine
netstat -tuln | grep 9222
# Should show: 0.0.0.0:9222 (not 127.0.0.1:9222)
```

**Solution:**
```bash
# Relaunch with correct bind address
pkill chromium
chromium --remote-debugging-port=9222 --remote-debugging-address=0.0.0.0 &
```

#### **Issue: "Cannot reach from phone/tablet"**

**Check IP address:**
```bash
# Verify your desktop's IP
hostname -I | awk '{print $1}'
```

**Check firewall:**
```bash
# Temporarily disable firewall to test
sudo ufw disable
# Test connection
# Re-enable after testing
sudo ufw enable
```

**Verify devices on same network:**
```bash
# From desktop, ping your phone (if you know its IP)
ping 192.168.1.50
```

---

## 🎯 Network Access Checklist

- [ ] Get desktop IP: `hostname -I | awk '{print $1}'`
- [ ] Launch Chrome: `chromium --remote-debugging-port=9222 --remote-debugging-address=0.0.0.0 &`
- [ ] Test locally: `curl http://YOUR_IP:9222/json/version`
- [ ] Test from phone browser: `http://YOUR_IP:9222`
- [ ] Configure SimExp: `simexp init` or edit `~/.simexp/simexp.yaml`
- [ ] Run session from any device: `simexp session start --cdp-url http://YOUR_IP:9222`
- [ ] Verify CDP endpoint stored in `.simexp/session.json`

---

## 🎸 JamAI Note:

This approach uses **your authenticated browser session** - no password handling, no separate login automation. Playwright just "rides along" with your existing Chrome, using the session you've already established.

**It's the most fluid path** because:
- ✅ No credential storage needed
- ✅ Uses your real browser with real cookies
- ✅ All Simplenote features available
- ✅ Multi-factor auth already handled by you

**♠️🌿🎸🧵 Assembly Ready - Launch Chrome and Test!**
