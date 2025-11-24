# SimExp MCP

An MCP (Model Context Protocol) server that exposes all SimExp functionality for use with Claude and other AI agents.

## Installation

Install from PyPI:

```bash
pip install simexp-mcp
```

Or install with development dependencies:

```bash
pip install simexp-mcp[dev]
```

## Quick Start

Start the MCP server:

```bash
simexp-mcp
```

The server will start listening for MCP protocol connections.

## Features

### Session Management Tools
- **simexp_session_start** - Start a new session with optional file/AI/issue/repo parameters
- **simexp_session_list** - List all sessions
- **simexp_session_info** - Show current session & directory context
- **simexp_session_clear** - Clear active session
- **simexp_session_write** - Write message to session note
- **simexp_session_read** - Read session note content
- **simexp_session_add** - Add file to session note
- **simexp_session_title** - Set session note title
- **simexp_session_open** - Open session note in browser
- **simexp_session_url** - Print session note URL

### Collaboration Tools
- **simexp_session_collab** - Share with Assembly (♠, 🌿, 🎸, 🧵)
- **simexp_session_collab_add** - Add collaborator by email
- **simexp_session_collab_list** - List all collaborators
- **simexp_session_publish** - Publish note (get public URL)

### Reflection & Wisdom Tools
- **simexp_session_reflect** - Open editor for reflection notes
- **simexp_session_observe_pattern** - Record an observed pattern
- **simexp_session_extract_wisdom** - Extract and record wisdom
- **simexp_session_complete** - Complete session with ceremony

### Core Extraction Tools
- **simexp_init** - Initialize session with browser authentication
- **simexp_extract** - Extract content from URL
- **simexp_write** - Write content to Simplenote
- **simexp_read** - Read content from Simplenote
- **simexp_archive** - Archive content
- **simexp_fetch** - Fetch using Simfetcher capabilities
- **simexp_session_browser** - Launch browser for authentication

## Authentication

SimExp MCP requires Simplenote credentials. When you first use the `simexp_init` tool, it will:

1. Detect that you don't have an active session
2. Launch your browser to Simplenote login page
3. Prompt you to log in manually
4. Persist the session for subsequent tool calls

Once authenticated, all subsequent tools can access your Simplenote data.

## Architecture

### Package Structure

```
simexp-mcp/
├── simexp_mcp/
│   ├── __init__.py       # Package initialization
│   ├── server.py         # MCP server and tool handlers
│   └── tools.py          # Tool implementations
├── tests/                # Test suite
├── pyproject.toml        # Modern Python packaging
├── Makefile              # Build automation
└── release.sh            # Release automation
```

### Main Components

**server.py** - MCP protocol server that:
- Handles all MCP protocol messages
- Routes tool calls to appropriate handlers
- Manages resource and prompt endpoints

**tools.py** - All tool implementations that:
- Wrap SimExp CLI commands
- Provide user-friendly MCP interfaces
- Handle input validation and error reporting

## Development

### Install for Development

```bash
cd simexp-mcp
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Build Distribution

```bash
make clean
make build
```

### Release Workflow

```bash
# Full test release
./release.sh

# Or use Makefile
make test-release  # Test PyPI
make upload        # Production PyPI
```

## Version Management

Version 0.1.0 and above. See `release.sh` or `Makefile` for automated version bumping:

```bash
make bump          # Auto-increment patch version
./release.sh       # Interactive release with all steps
```

## Configuration

SimExp MCP uses the parent `simexp` package configuration. See the main [SimExp documentation](https://github.com/Gerico1007/simexp) for configuration details.

## Troubleshooting

### "simexp_init must be called first"
The MCP server requires an active Simplenote session. Call `simexp_init` to authenticate:
```
→ simexp_init
← Opens browser for Simplenote login
```

### "Cannot find module mcp"
Ensure the `mcp` package is installed:
```bash
pip install mcp>=1.0.0
```

### Tests failing
Ensure all dependencies are installed and Python 3.10+ is available:
```bash
pip install -e ".[dev]"
python --version  # Should be 3.10+
```

## Contributing

Contributions welcome! Please ensure:
- All tests pass: `pytest`
- Code is formatted: `black .`
- Type hints are included

## License

MIT License - see LICENSE file for details

## Links

- **Main Package**: [SimExp on GitHub](https://github.com/Gerico1007/simexp)
- **Issue Tracking**: [SimExp Issues](https://github.com/Gerico1007/simexp/issues)
- **PyPI**: [simexp-mcp on PyPI](https://pypi.org/project/simexp-mcp/)

## Support

For issues, feature requests, or questions, please open an issue on the [main SimExp repository](https://github.com/Gerico1007/simexp/issues).
