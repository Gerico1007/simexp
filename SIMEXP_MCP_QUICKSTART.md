# SimExp MCP Quick Start Guide

## What You Have

✅ **25 MCP Tools** - All SimExp functions exposed to Claude Code
✅ **Full Installation** - All dependencies resolved and tested
✅ **Virtual Environment** - Isolated testing space at `test-env/`

## Installation & Setup

### Option 1: Use Local Testing Environment (Current)
```bash
# Activate the test environment
source test-env/bin/activate

# Verify installation
pip list | grep simexp
# Output should show:
#   simexp         0.5.0
#   simexp-mcp     0.1.0
```

### Option 2: Install in Your Own Environment (Later)
```bash
# Create venv
python3 -m venv my-env
source my-env/bin/activate

# Install both packages (once published)
pip install simexp simexp-mcp
```

## Available Tools (25 Total)

### Session Management (12 tools)
```
simexp_session_start      # Create new session with context
simexp_session_list       # List all sessions
simexp_session_info       # Show current session
simexp_session_clear      # Clear active session
simexp_session_write      # Write message to note
simexp_session_read       # Read note content
simexp_session_add        # Add file to note
simexp_session_title      # Set note title
simexp_session_open       # Open in browser
simexp_session_url        # Get note URL
simexp_session_publish    # Publish and share
simexp_session_browser    # Launch auth browser
```

### Collaboration (3 tools)
```
simexp_session_collab       # Share with Assembly (♠️🌿🎸🧵)
simexp_session_collab_add   # Add collaborator by email
simexp_session_collab_list  # List collaborators
```

### Reflection & Wisdom (4 tools)
```
simexp_session_reflect        # Reflection editor
simexp_session_observe_pattern # Record pattern
simexp_session_extract_wisdom  # Extract wisdom
simexp_session_complete        # Complete session
```

### Core Extraction (6 tools)
```
simexp_init      # Initialize with browser auth
simexp_extract   # Extract from URL
simexp_write     # Write to Simplenote
simexp_read      # Read from Simplenote
simexp_archive   # Archive content
simexp_fetch     # Fetch with Simfetcher
```

## How to Use

### 1. Verify Tools Load
```bash
source test-env/bin/activate
python -c "from simexp_mcp.tools import get_all_tools; print(f'✅ {len(get_all_tools())} tools ready')"
```

### 2. Start the MCP Server (Future)
```bash
source test-env/bin/activate
simexp-mcp
```

This starts the MCP server that Claude Code will connect to.

### 3. Use with Claude Code (Future)
Once installed, Claude Code will automatically discover and provide all 25 tools.

Example usage in Claude Code:
```
User: Extract content from https://example.com
→ Claude calls: simexp_extract("https://example.com")
```

## Publishing & Release

### Test Release (TestPyPI)
```bash
# From project root
make test-release

# Or coordinated (both packages)
./release-all.sh
# Choose option 4: Test releases
```

### Production Release (PyPI)
```bash
# From project root
./release.sh  # Main package

# Or coordinated
./release-all.sh
# Choose option 3: Release both packages
```

## Project Structure

```
simexp/
├── simexp/                    # Main package (v0.5.0+)
├── simexp-mcp/                # MCP server (v0.1.0+)
│   ├── simexp_mcp/
│   │   ├── server.py         # MCP protocol handler
│   │   └── tools.py          # 25 MCP tool implementations
│   ├── pyproject.toml        # Dependencies
│   ├── Makefile              # Build automation
│   └── release.sh            # Release script
├── test-env/                  # Virtual environment (for testing)
├── Makefile                   # Main build automation
├── release.sh                 # Main release script
├── release-all.sh             # Coordinated releases
└── bump.py                    # Version management
```

## Status

| Component | Status | Version |
|-----------|--------|---------|
| simexp | ✅ Ready | 0.5.0 |
| simexp-mcp | ✅ Ready | 0.1.0 |
| MCP Server | ✅ Tested | Works with mcp 1.22.0 |
| Tools | ✅ Verified | All 25 load successfully |
| Installation | ✅ Complete | All dependencies resolved |

## Quick Commands

```bash
# Activate environment
source test-env/bin/activate

# Show all tools
python -c "from simexp_mcp.tools import get_all_tools; [print(t.name) for t in get_all_tools()]"

# List tools by category
python -c "from simexp_mcp.tools import get_all_tools; from itertools import groupby; [print(name, len(list(tools))) for name, tools in groupby((t for t in get_all_tools() if 'session' in t.name), key=lambda x: 'session')]"

# Check installation
pip list | grep -E "simexp|mcp"

# Deactivate environment
deactivate
```

## Next Steps

1. ✅ Review PR #58 on GitHub
2. ⏳ Merge to main branch
3. ⏳ Run release workflow: `./release-all.sh`
4. ⏳ Install from PyPI: `pip install simexp-mcp`
5. ⏳ Use with Claude Code: All tools automatically available

## Support

- **GitHub Issue**: #57
- **Pull Request**: #58
- **Repository**: https://github.com/Gerico1007/simexp

---

**Created**: 2025-11-23
**Last Updated**: 2025-11-23
**Maintained by**: Claude Code + G.Music Assembly
