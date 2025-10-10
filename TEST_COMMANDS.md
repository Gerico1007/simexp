# 🧪 Session-Aware Notes Testing Commands
**Issue #4 - Feature Testing Checklist**

## 🎯 Prerequisites

Before starting, ensure:
```bash
# 1. Navigate to simexp directory
cd ~/workspace/simexp

# 2. Check branch
git branch
# Should show: * 4-session-aware-notes

# 3. Chrome is running with remote debugging
# Already running from your setup: http://localhost:9223
```

---

## ✅ Test Sequence

### **Test 1: Create New Session**

**Command:**
```bash
python -m simexp.simex session start --ai claude --issue 4
```

**Expected Output:**
```
♠️🌿🎸🧵 Creating Session Note
🔮 Session ID: [UUID generated]
🤝 AI Assistant: claude
🎯 Issue: #4
📝 Writing metadata directly to new note...
✅ Metadata written to new note
💾 Session state saved to .simexp/session.json
🔑 Search key: [same UUID]
```

**What to Verify:**
- ✅ New note created in Simplenote (should see it in note list)
- ✅ Note contains YAML metadata at top
- ✅ Metadata includes session_id, ai_assistant, issue_number, agents list
- ✅ `.simexp/session.json` created in workspace

**In Simplenote, you should see:**
```yaml
---
session_id: [UUID]
ai_assistant: claude
agents:
- Jerry
- Aureon
- Nyro
- JamAI
- Synth
issue_number: 4
pr_number: null
created_at: [timestamp]
---

```

---

### **Test 2: Check Session Status**

**Command:**
```bash
python -m simexp.simex session status
```

**Expected Output:**
```
📋 Active Session:
🔮 Session ID: [UUID]
🔑 Search key: [UUID]
🤝 AI Assistant: claude
🎯 Issue: #4
📅 Created: [timestamp]
```

**What to Verify:**
- ✅ Shows active session information
- ✅ All fields populated correctly

---

### **Test 3: Write to Session Note**

**Command:**
```bash
python -m simexp.simex session write "Test entry 1: This is my first test write to the session note."
```

**Expected Output:**
```
✍️  Writing to active session note...
🔍 Searching for session note: [UUID]
✅ Typed search query: [UUID]
✅ Selected session note from search results
✅ Content written to session note
```

**What to Verify:**
- ✅ Content appears in Simplenote note (after metadata)
- ✅ No error about "wrong note"
- ✅ New content appended (doesn't overwrite metadata)

**In Simplenote, note should now contain:**
```yaml
---
session_id: [UUID]
...
---


Test entry 1: This is my first test write to the session note.
```

---

### **Test 4: Write Multiple Entries**

**Commands (run one at a time):**
```bash
python -m simexp.simex session write "Test entry 2: Adding more content to verify append mode."

python -m simexp.simex session write "Test entry 3: Testing search-based note selection."

python -m simexp.simex session write "Test entry 4: Final verification before PR."
```

**What to Verify:**
- ✅ Each entry appends to the note
- ✅ Entries appear in chronological order
- ✅ No duplicate content
- ✅ Metadata remains intact at top

---

### **Test 5: Read Session Note**

**Command:**
```bash
python -m simexp.simex session read
```

**Expected Output:**
```
📖 Reading session note...
🔍 Searching for session note: [UUID]
✅ Typed search query: [UUID]
✅ Selected session note from search results

📄 Session Note Content:
---
session_id: [UUID]
ai_assistant: claude
agents:
- Jerry
- Aureon
- Nyro
- JamAI
- Synth
issue_number: 4
pr_number: null
created_at: [timestamp]
---


Test entry 1: This is my first test write to the session note.

Test entry 2: Adding more content to verify append mode.

Test entry 3: Testing search-based note selection.

Test entry 4: Final verification before PR.
```

**What to Verify:**
- ✅ All entries present
- ✅ Metadata displayed correctly
- ✅ Formatting preserved

---

### **Test 6: Open Session in Browser**

**Command:**
```bash
python -m simexp.simex session open
```

**Expected Output:**
```
🌐 Opening session note in browser...
🔍 Searching for session note: [UUID]
✅ Typed search query: [UUID]
✅ Selected session note from search results
✅ Session note opened in browser
```

**What to Verify:**
- ✅ Browser focuses on Simplenote tab
- ✅ Correct note is selected and displayed
- ✅ All content visible in browser

---

### **Test 7: Get Session URL (Note: Public URLs are read-only)**

**Command:**
```bash
python -m simexp.simex session url
```

**Expected Output:**
```
🔗 Getting session note URL...
🔍 Searching for session note: [UUID]
✅ Typed search query: [UUID]
✅ Selected session note from search results

📋 Session Note URL (Read-Only):
https://app.simplenote.com/p/[note-id]

Note: This is a public read-only URL. Use 'session open' to edit.
```

**What to Verify:**
- ✅ URL generated
- ✅ Warning about read-only noted
- ✅ Can open URL in browser (content visible but not editable)

---

### **Test 8: Test with Different AI Assistant**

**Commands:**
```bash
# Clear current session first
python -m simexp.simex session clear

# Create new session with gemini
python -m simexp.simex session start --ai gemini --issue 18
```

**Expected Output:**
```
🧹 Session cleared

♠️🌿🎸🧵 Creating Session Note
🔮 Session ID: [NEW UUID]
🤝 AI Assistant: gemini
🎯 Issue: #18
...
```

**What to Verify:**
- ✅ New note created (different from first)
- ✅ Metadata shows `ai_assistant: gemini`
- ✅ Metadata shows `issue_number: 18`

---

### **Test 9: Session Workflow (Complete Cycle)**

**Full workflow test:**
```bash
# 1. Start session
python -m simexp.simex session start --ai claude --issue 4

# 2. Write work log
python -m simexp.simex session write "🎯 Starting work on PR documentation"

# 3. Check status
python -m simexp.simex session status

# 4. Continue writing
python -m simexp.simex session write "📝 Updated README with session commands"
python -m simexp.simex session write "✅ All tests passing"

# 5. Read full note
python -m simexp.simex session read

# 6. Open in browser to review
python -m simexp.simex session open

# 7. Get shareable URL
python -m simexp.simex session url

# 8. Clear when done
python -m simexp.simex session clear
```

**What to Verify:**
- ✅ Complete workflow executes without errors
- ✅ Each step produces expected output
- ✅ Note content builds progressively
- ✅ Final clear removes `.simexp/session.json`

---

### **Test 10: Error Handling**

**Test with no active session:**
```bash
# Make sure no session active
python -m simexp.simex session clear

# Try to write without active session
python -m simexp.simex session write "This should fail"
```

**Expected Output:**
```
❌ No active session. Use 'session start' to create one.
```

**Test session status with no session:**
```bash
python -m simexp.simex session status
```

**Expected Output:**
```
❌ No active session
```

**What to Verify:**
- ✅ Graceful error messages
- ✅ Helpful guidance (tells user to run `session start`)
- ✅ No crashes or stack traces

---

## 🎸 Musical Encoding Test

After completing functional tests, create session melody:

```bash
# Start fresh session
python -m simexp.simex session start --ai claude --issue 4

# Write test entries
python -m simexp.simex session write "Testing complete! All features working as expected."
python -m simexp.simex session write "Ready for PR tomorrow! 🎸⚡"
```

**Then verify melody exists:**
```bash
ls -la sessionABC/251009_completion_circle.abc
```

**Should show the completion circle melody we created!**

---

## 📊 Test Results Checklist

Mark each test as you complete it:

- [ ] **Test 1**: Session creation ✅
- [ ] **Test 2**: Status check ✅
- [ ] **Test 3**: Single write ✅
- [ ] **Test 4**: Multiple writes ✅
- [ ] **Test 5**: Read session ✅
- [ ] **Test 6**: Open in browser ✅
- [ ] **Test 7**: Get URL ✅
- [ ] **Test 8**: Different AI/Issue ✅
- [ ] **Test 9**: Complete workflow ✅
- [ ] **Test 10**: Error handling ✅

---

## 🐛 Known Behaviors (Not Bugs)

1. **Public URLs are read-only** - This is by Simplenote design, not a bug
2. **Search takes 1-2 seconds** - Normal delay for Simplenote search
3. **Chrome window flashes** - Browser automation normal behavior
4. **`.simexp/` in gitignore** - Intentional (local workspace state)

---

## 🚨 If Something Goes Wrong

### **Issue: Note not found during search**
```bash
# Check if session exists
cat .simexp/session.json

# Manually search in Simplenote browser for the UUID
# If note exists but not found, try:
python -m simexp.simex session open
```

### **Issue: Wrong note selected**
```bash
# This was the bug we fixed! If this happens:
# 1. Check you're on branch: 4-session-aware-notes
# 2. Check latest code pulled
# 3. Report back to Jerry!
```

### **Issue: Chrome connection error**
```bash
# Verify Chrome is running with remote debugging:
# Should have: --remote-debugging-port=9223

# Test CDP connection:
curl http://localhost:9223/json
```

### **Issue: Permission errors on .simexp/**
```bash
# Fix permissions:
chmod 755 .simexp
chmod 644 .simexp/session.json
```

---

## 📝 Notes for Testing

1. **Use fresh terminal** - Ensure clean environment
2. **Keep Simplenote browser tab open** - Easier to verify visually
3. **Test with real issue numbers** - Use Issue #4 or #18 (your new session)
4. **Note the session UUIDs** - Helps verify search is working
5. **Take screenshots** - If anything looks wrong, screenshot it!

---

## ✅ Success Criteria

All tests pass if:
- ✅ Notes created with correct metadata
- ✅ Search finds notes by session_id UUID
- ✅ Content appends correctly (no overwrites)
- ✅ All commands work without errors
- ✅ Session state persists correctly
- ✅ Clear removes session cleanly

---

## 🎯 After Testing

Once all tests pass, report back:
```
All tests ✅ - Ready for PR!
```

**Tomorrow we'll:**
1. Create comprehensive PR description
2. Link to Issue #4
3. Reference session melodies
4. Include Assembly documentation
5. Request your verification before merge

---

**♠️🌿🎸🧵 Happy Testing, Jerry & Jericho!** 🎸⚡

*Testing is the rhythm section of development - it keeps everything in time!*
