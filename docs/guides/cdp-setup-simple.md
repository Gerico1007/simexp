# 🎯 Chrome CDP Setup - Explained Like You're a Kid

**♠️🌿🎸🧵 G.Music Assembly - SimExp Beginner Guide**

---

## 🤔 What's This All About?

Think of Chrome like a **robot** that can browse websites. Normally, you control it with your **mouse and keyboard**. But we want **Python code** (SimExp) to control it too!

**CDP (Chrome DevTools Protocol)** is like a **remote control** for Chrome. It opens a special "door" (called a **port**) that lets SimExp send commands to Chrome.

---

## 🚪 What's a Port?

A **port** is like an apartment number for your computer. Your computer has thousands of "apartments" (ports). When a program wants to talk to another program, it knocks on a specific apartment door (port number).

**Port 9222** = The standard "apartment" where Chrome listens for remote control commands.

---

## 📝 The Magic Command (Copy & Paste This!)

###  On Linux/Mac/Termux:
```bash
chromium --remote-debugging-port=9222 --user-data-dir=~/.chrome-simexp &
```

### 🪟 On Windows:
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=%USERPROFILE%\.chrome-simexp
```

---

## 🔍 Let's Break Down What This Does

```
chromium --remote-debugging-port=9222 --user-data-dir=~/.chrome-simexp &
│         │                            │                              │
│         │                            │                              └─ Run in background
│         │                            └─ Where to save cookies/passwords
│         └─ Open remote control door at apartment #9222
└─ Start Chrome browser
```

###  Part 1: `chromium`
- Starts the Chrome browser
- On your system it might be called: `chrome`, `google-chrome`, or `chromium-browser`
- **Find yours**: Type `which chromium` or `which google-chrome` in terminal

### 🚪 Part 2: `--remote-debugging-port=9222`
- Opens the "remote control door" at port **9222**
- This is the **magic number** that SimExp will connect to
- **9222** is the industry standard (everyone uses this number!)

### 📁 Part 3: `--user-data-dir=~/.chrome-simexp`
- Where Chrome saves your login cookies, passwords, history
- `~/.chrome-simexp` = a folder in your home directory
- **Why needed?** So you can have:
  - Your normal Chrome (your regular browsing)
  - SimExp Chrome (with Simplenote login) **at the same time!**
- **REQUIRED** for Chrome 136+ (security feature added in 2025)

### 🏃 Part 4: `&`
- Runs Chrome in the background
- Lets you keep using the terminal
- **Windows**: Remove this, or run in a separate command window

---

## 🎬 Step-by-Step Setup (First Time)

### Step 1: Start Chrome with CDP

Copy and paste the command for your system:

**Linux/Mac**:
```bash
chromium --remote-debugging-port=9222 --user-data-dir=~/.chrome-simexp &
```

**Windows**:
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=%USERPROFILE%\.chrome-simexp
```

You should see a **new Chrome window** open!

### Step 2: Login to Simplenote

1. In the new Chrome window, go to: https://app.simplenote.com
2. Login with your Simplenote account
3. **Keep this window open!** (Don't close it)

### Step 3: Configure SimExp

Tell SimExp where to find your Chrome:

```bash
simexp init
```

When it asks for CDP URL, just press **Enter** (uses default localhost:9222).

### Step 4: Test It!

```bash
simexp session start --ai claude
```

If everything works, SimExp will create a note in your Simplenote! 🎉

---

## 🔧 Troubleshooting (When Things Go Wrong)

### ❌ Error: "ECONNREFUSED localhost:9222"

**Problem**: SimExp can't find Chrome's remote control door.

**Solution**:
1. **Check if Chrome is running**:
   ```bash
   curl http://localhost:9222/json/version
   ```
   - ✅ If you see JSON with Chrome version → Chrome is running!
   - ❌ If you see "Connection refused" → Chrome is NOT running with CDP

2. **Kill any old Chrome and start fresh**:
   ```bash
   pkill -f "remote-debugging-port"
   chromium --remote-debugging-port=9222 --user-data-dir=~/.chrome-simexp &
   ```

### ❌ Error: "User data directory is already in use"

**Problem**: Chrome is already running with that folder.

**Solution**:
```bash
# Kill all Chrome processes
pkill chrome
pkill chromium

# Start fresh
chromium --remote-debugging-port=9222 --user-data-dir=~/.chrome-simexp &
```

### ❌ Error: "Cannot find 'chromium' command"

**Problem**: Chrome/Chromium not installed or has different name.

**Solution**:
1. **Find Chrome on your system**:
   ```bash
   which chromium
   which google-chrome
   which chrome
   ```

2. **Use the one that works**:
   ```bash
   google-chrome --remote-debugging-port=9222 --user-data-dir=~/.chrome-simexp &
   ```

### ❌ SimExp connects but can't find notes

**Problem**: You're not logged into Simplenote in the CDP Chrome window.

**Solution**:
1. Look for the Chrome window that opened with the CDP command
2. Go to https://app.simplenote.com
3. Login
4. Try SimExp again

---

## 🎯 Quick Reference

### Start CDP Chrome:
```bash
chromium --remote-debugging-port=9222 --user-data-dir=~/.chrome-simexp &
```

### Check if it's running:
```bash
curl http://localhost:9222/json/version
```

### Stop CDP Chrome:
```bash
pkill -f "remote-debugging-port"
```

### Configure SimExp:
```bash
simexp init
# CDP URL: [just press Enter for default]
```

### Test it works:
```bash
simexp session start
```

---

## 🌐 Multi-Network Setup (Advanced)

If Chrome is running on a **different computer** (like a server):

### On the Server (running Chrome):
```bash
chromium --remote-debugging-port=9222 --user-data-dir=~/.chrome-simexp &
```

### On Your Computer (running SimExp):
```bash
# Option 1: During simexp init
simexp init
# CDP URL: http://192.168.1.100:9222  (server's IP)

# Option 2: Environment variable
export SIMEXP_CDP_URL=http://192.168.1.100:9222

# Option 3: Command-line flag
simexp session start --cdp-url http://192.168.1.100:9222
```

**Priority** (what wins):
1. `--cdp-url` flag (highest - overrides everything)
2. `SIMEXP_CDP_URL` environment variable
3. `CDP_URL` in `~/.simexp/simexp.yaml` config file
4. `http://localhost:9222` (default)

---

## 📚 Visual Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Your Terminal                                              │
│  ┌─────────────┐                                           │
│  │ simexp      │  "Create a note!"                         │
│  │ (Python)    │────────┐                                  │
│  └─────────────┘        │                                  │
│                         │ Sends commands via CDP           │
│                         ▼                                   │
│  ┌───────────────────────────────────────┐                │
│  │  Chrome (with CDP)                    │                │
│  │  Port 9222 is open                    │                │
│  │  ┌─────────────────────────────────┐  │                │
│  │  │  Simplenote Tab                 │  │                │
│  │  │  (you're logged in)             │  │                │
│  │  │                                 │  │                │
│  │  │  ✍️  Note gets created!          │  │                │
│  │  └─────────────────────────────────┘  │                │
│  └───────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎓 Why Port 9222?

- ✅ **Industry Standard**: Chrome DevTools Protocol official convention
- ✅ **Every Tool Uses It**: Puppeteer, Playwright, Selenium all expect 9222
- ✅ **All Tutorials Use It**: Every guide and documentation uses 9222
- ✅ **Easy to Remember**: 9-Two-Two-Two (repeating pattern!)
- ✅ **No Conflicts**: Not used by other common services

---

## ❓ Frequently Asked Questions

### Q: Do I need to keep Chrome open all the time?
**A**: Yes! SimExp connects to the running Chrome. If you close Chrome, SimExp can't talk to it.

### Q: Can I use my regular Chrome while SimExp is running?
**A**: Yes! The CDP Chrome is separate. You can browse normally in your regular Chrome.

### Q: Is this safe?
**A**: Yes, if you use `--user-data-dir` to create a separate profile. Never use your main Chrome profile with CDP enabled.

### Q: Why not just use Simplenote API?
**A**: Simplenote API is limited. Using Chrome lets us access ALL features (sharing, publishing, collaboration) that the web app has.

### Q: What if I'm on a different network than the Chrome server?
**A**: Use the multi-network setup above. SimExp can connect to Chrome running anywhere on the internet!

---

## 🎉 Success Checklist

- [ ] Chrome starts with `--remote-debugging-port=9222`
- [ ] `curl http://localhost:9222/json/version` returns JSON
- [ ] Chrome window shows Simplenote and you're logged in
- [ ] `simexp init` completed successfully
- [ ] `simexp session start` creates a note in Simplenote
- [ ] You see the note in your Simplenote app!

If all checkboxes are ✅, you're ready to rock! 🎸

---

## 🆘 Still Stuck?

1. **Read error messages carefully** - they usually tell you what's wrong
2. **Check Chrome is running**: `curl http://localhost:9222/json/version`
3. **Check you're logged in**: Open the CDP Chrome window and verify
4. **Try the diagnostic**: `simexp cdp-check` (coming soon!)
5. **Create a GitHub issue**: https://github.com/Gerico1007/simexp/issues

---

**♠️🌿🎸🧵 G.Music Assembly**
*Making complex things simple, one port at a time!*

**Session**: October 12, 2025
**Issue**: #13 - CDP Standardization
**Port**: 9222 (The One True Port™)
