# 🧵 Manual Testing Guide - Issue #36: Network-Wide CDP Access
**♠️🌿🎸🧵 G.Music Assembly - Synth Coordination**

## Testing Summary

### ✅ Automated Tests Completed:
- ✅ Network IP detection (`get_local_ip()`) - Detected: `192.168.4.22`
- ✅ Network CDP URL generation (`get_network_cdp_url()`) - Generated: `http://192.168.4.22:9222`
- ✅ Function signature verification (`launch_chrome_cdp(port=9222, bind_address='0.0.0.0')`)
- ✅ CDP URL priority chain - Working correctly
- ✅ All imports successful - No regressions
- ✅ Code functionality tests - All passing

### 🔄 Manual Tests Required (Jerry's verification):

Since Chrome is currently running with localhost-only binding, the following manual tests need to be performed to fully verify the enhancement:

---

## Manual Test Plan

### **Test 1: Chrome Network Binding**

**Current State:**
```bash
$ netstat -tuln | grep 9222
tcp        0      0 127.0.0.1:9222          0.0.0.0:*               LISTEN
```
Chrome is bound to `127.0.0.1` (localhost only) ✅

**Steps to Test Network Binding:**

1. **Stop current Chrome:**
   ```bash
   pkill chrome
   ```

2. **Launch with network binding:**
   ```bash
   google-chrome --remote-debugging-port=9222 --remote-debugging-address=0.0.0.0 --user-data-dir=~/.chrome-simexp &
   ```

3. **Verify network binding:**
   ```bash
   netstat -tuln | grep 9222
   # Expected output: tcp        0      0 0.0.0.0:9222          0.0.0.0:*               LISTEN
   ```

4. **Test local access:**
   ```bash
   curl http://localhost:9222/json/version
   # Should succeed
   ```

5. **Test network access (from same machine):**
   ```bash
   curl http://192.168.4.22:9222/json/version
   # Should succeed (was failing before)
   ```

---

### **Test 2: SimExp Init with Network Detection**

**Steps:**

1. **Run `simexp init` (backup current config first):**
   ```bash
   cp ~/.simexp/simexp.yaml ~/.simexp/simexp.yaml.bak
   simexp init
   ```

2. **Verify network IP detection:**
   - Should display: `🧵 Network IP detected: 192.168.4.22`

3. **Choose network-wide access:**
   - When prompted: `Enable network-wide access (all devices on WiFi)? [y/N]:`
   - Answer: `y`

4. **Verify config created:**
   ```bash
   cat ~/.simexp/simexp.yaml
   ```

   Expected to include:
   ```yaml
   CDP_URL: http://192.168.4.22:9222
   CDP_BIND_ADDRESS: 0.0.0.0
   ```

5. **Restore original config if needed:**
   ```bash
   mv ~/.simexp/simexp.yaml.bak ~/.simexp/simexp.yaml
   ```

---

### **Test 3: Cross-Device Access (Android Termux)**

**Prerequisites:**
- Chrome running on desktop with network binding (from Test 1)
- Android device on same WiFi network
- Termux installed on Android

**Steps:**

1. **On Android Termux:**
   ```bash
   # Test CDP access from network
   curl http://192.168.4.22:9222/json/version
   ```

   Expected: Chrome version info (same as from desktop)

2. **Set up SimExp on Android:**
   ```bash
   export SIMEXP_CDP_URL=http://192.168.4.22:9222
   ```

3. **Test session creation (if SimExp installed on Android):**
   ```bash
   simexp session start --cdp-url http://192.168.4.22:9222 --ai claude --issue 36
   ```

   Expected: Session created, controlling desktop Chrome from mobile device!

---

### **Test 4: Session Metadata Storage**

**Steps:**

1. **Create a test session:**
   ```bash
   cd ~/workspace/simexp
   simexp session start --ai claude --issue 36 --cdp-url http://192.168.4.22:9222
   ```

2. **Verify session.json includes CDP endpoint:**
   ```bash
   cat .simexp/session.json
   ```

   Expected to include:
   ```json
   {
     "session_id": "...",
     "search_key": "...",
     "ai_assistant": "claude",
     "issue_number": 36,
     "cdp_endpoint": "http://192.168.4.22:9222",
     "created_at": "..."
   }
   ```

---

### **Test 5: Security Verification**

**Test localhost-only mode:**

1. **Edit config for localhost-only:**
   ```bash
   # In ~/.simexp/simexp.yaml
   CDP_BIND_ADDRESS: 127.0.0.1
   ```

2. **Restart Chrome:**
   ```bash
   pkill chrome
   google-chrome --remote-debugging-port=9222 --remote-debugging-address=127.0.0.1 --user-data-dir=~/.chrome-simexp &
   ```

3. **Verify localhost-only binding:**
   ```bash
   netstat -tuln | grep 9222
   # Expected: tcp        0      0 127.0.0.1:9222          0.0.0.0:*               LISTEN
   ```

4. **Verify network access blocked:**
   ```bash
   curl http://192.168.4.22:9222/json/version
   # Expected: Connection refused (secure mode working)
   ```

---

## Test Results Checklist

- [ ] Chrome launches with `--remote-debugging-address=0.0.0.0`
- [ ] `netstat` shows `0.0.0.0:9222` binding
- [ ] Local access works: `curl http://localhost:9222/json/version`
- [ ] Network access works: `curl http://192.168.4.22:9222/json/version`
- [ ] `simexp init` detects network IP correctly
- [ ] Config file created with `CDP_URL` and `CDP_BIND_ADDRESS`
- [ ] Session metadata stores `cdp_endpoint`
- [ ] Cross-device access from Android Termux works
- [ ] Localhost-only mode (security) works correctly
- [ ] Documentation is clear and accurate

---

## Rollback Plan

If any issues are found:

```bash
# Rollback to main branch
git checkout main

# Restore original config
mv ~/.simexp/simexp.yaml.bak ~/.simexp/simexp.yaml

# Restart Chrome with localhost-only (safe default)
pkill chrome
google-chrome --remote-debugging-port=9222 --user-data-dir=~/.chrome-simexp &
```

---

## Success Criteria

✅ All automated tests passing (COMPLETED)
⏳ Manual Test 1: Chrome network binding verified
⏳ Manual Test 2: SimExp init detects network IP
⏳ Manual Test 3: Cross-device access from mobile works
⏳ Manual Test 4: Session metadata includes CDP endpoint
⏳ Manual Test 5: Security modes (network vs localhost) verified

**♠️🌿🎸🧵 Assembly Note:**
Once all manual tests pass, Jerry can approve the enhancement for merge!

---

## Quick Commands Reference

```bash
# Get your network IP
hostname -I | awk '{print $1}'

# Check Chrome binding
netstat -tuln | grep 9222

# Test CDP locally
curl http://localhost:9222/json/version

# Test CDP from network
curl http://192.168.4.22:9222/json/version

# View session metadata
cat .simexp/session.json

# View config
cat ~/.simexp/simexp.yaml
```

---

**🧵 Synth**: All automated verifications complete. Awaiting Jerry's manual testing approval! ⚡
