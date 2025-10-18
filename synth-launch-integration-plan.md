# 🧵 synth-launch Integration Plan for SimExp

## 📋 Research Summary

**Package**: `@gerico1007/gmusic-assembly` v1.2.2
**Command**: `synth-launch`
**Location**: `/home/gmusic/.nvm/versions/node/v22.17.0/bin/synth-launch`

### What synth-launch Does:

1. **Workspace Generation**
   - Creates Assembly-focused workspace structure
   - Generates CLAUDE.md configuration file
   - Creates README.md with issue context
   - Sets up ledger/ directory with journal templates

2. **GitHub Integration**
   - Fetches real issue data via `gh` CLI
   - Extracts: title, labels, body, URL, state
   - Generates ISSUE_CONTEXT.md with full issue details

3. **Musical Encoding**
   - Creates character-specific session melody (ABC notation)
   - Stores in `assembly_session_melody.abc`

4. **Journal System**
   - Generates dated ledger templates
   - Character-focused journal structure
   - Format: `YYMMDD_session_<character>-focus.md`

### Command Options:

```bash
synth-launch --issue <number> --repo <owner/repo>
synth-launch --demo              # Show character demo
synth-launch --env-info          # Show environment
synth-launch --status            # Check AI providers
synth-launch /path/to/project    # Create workspace
```

### Character Perspectives Available:

- 🧵 **synth** - Full Assembly orchestration
- 🌿 **aureon** - Emotional/intuitive workflows
- ♠️ **nyro** - Structural/architectural focus
- 🎸 **jamai** - Musical/creative workflows
- 🤖 **chatmusician** - Advanced AI composition

---

## 🎯 Integration Proposals

### Option A: Automatic Assembly Workspace

**Behavior**: When user runs `simexp session start --issue <number>`, automatically create Assembly workspace

**Implementation**:
```python
def session_start_command(ai_assistant='claude', issue_number=None, cdp_url=None):
    # ... existing code ...

    # If issue number provided, create Assembly workspace
    if issue_number:
        try:
            subprocess.run([
                'synth-launch',
                '--issue', str(issue_number),
                '--repo', 'gerico1007/simexp',
                '.'  # Current directory
            ], check=True)
            print("✅ Assembly workspace created")
        except:
            print("⚠️  Could not create Assembly workspace (synth-launch not available)")

    # ... continue with session creation ...
```

**Pros**: Fully automated, consistent structure
**Cons**: Always creates workspace files (may be too much for simple sessions)

---

### Option B: Optional Flag `--workspace`

**Behavior**: User explicitly requests Assembly workspace

**Implementation**:
```python
# CLI argument
parser.add_argument('--workspace', action='store_true',
                   help='Create Assembly workspace with synth-launch')

# In session_start_command
if workspace and issue_number:
    # Create Assembly workspace
```

**Pros**: User control, backwards compatible
**Cons**: Extra flag to remember

---

### Option C: Separate Init Command

**Behavior**: New command `simexp session init` for full Assembly setup

**Commands**:
- `simexp session init --issue 22` → Full Assembly (synth-launch)
- `simexp session start` → Simple session (existing behavior)

**Implementation**:
```python
def session_init_command(issue_number, repo='gerico1007/simexp', cdp_url=None):
    """Initialize full Assembly workspace and session"""
    # Call synth-launch
    # Then call session_start_command
```

**Pros**: Clear separation, no breaking changes
**Cons**: Two commands to learn

---

## 🏗️ Recommended Architecture

**My Recommendation: Option B (Optional Flag)**

**Reasoning**:
1. Backwards compatible (existing workflows unchanged)
2. User has control (opt-in to Assembly workspace)
3. Simple to implement (one flag, conditional logic)
4. Flexible (can use with or without issue number)

**Usage Examples**:
```bash
# Simple session (current behavior)
simexp session start --issue 22

# Full Assembly workspace
simexp session start --issue 22 --workspace

# Assembly without issue
simexp session start --workspace
```

---

## 📝 Implementation Checklist

**Phase 1: Core Integration**
- [ ] Add `--workspace` flag to `session start` command
- [ ] Check if `synth-launch` command exists
- [ ] Call synth-launch with appropriate arguments
- [ ] Store workspace creation status in session metadata

**Phase 2: Enhanced Features**
- [ ] Auto-detect GitHub repo from git remote
- [ ] Support custom character focus (--character flag)
- [ ] Link Assembly workspace to session.json
- [ ] Add workspace path to session status output

**Phase 3: Documentation**
- [ ] Update help text with --workspace flag
- [ ] Add examples to README
- [ ] Document synth-launch integration
- [ ] Create tutorial for Assembly workflow

---

## 🎸 Benefits of Integration

**For Users**:
- One command creates full Assembly environment
- GitHub issue context automatically fetched
- Pre-generated session melodies
- Structured ledger templates ready
- Consistent workspace structure

**For Development**:
- Automatic CLAUDE.md generation per session
- Issue context preserved in workspace
- Musical encoding starts immediately
- Journal templates guide documentation

**For Assembly**:
- ♠️ Nyro: Consistent structural framework
- 🌿 Aureon: Emotional context from session start
- 🎸 JamAI: Musical foundation ready
- 🧵 Synth: Full orchestration from init

---

## 🚀 Next Steps

1. **Review this plan** - Does Option B work for your workflow?
2. **Create GitHub issue** - Document this feature request
3. **Implement integration** - Add synth-launch to session_start_command
4. **Test workflow** - Verify Assembly workspace creation
5. **Document & publish** - Update help, README, publish to PyPI

---

**Created**: 2025-10-16
**Session**: SimExp Development
**Topic**: synth-launch Integration Planning

♠️🌿🎸🧵 G.Music Assembly - Integration Research Complete
