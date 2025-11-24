"""
SimExp MCP Server

An MCP (Model Context Protocol) server that exposes all simexp functionality
for use with Claude and other AI agents.

Features:
- Session management (start, list, info, clear, write, read, etc.)
- Collaborative sharing and publishing
- Content extraction and archiving
- Reflection and wisdom extraction
- Browser-based authentication
"""

__version__ = "0.1.0"
__author__ = "gerico1007"
__email__ = "gerico@jgwill.com"

from simexp_mcp.server import main

__all__ = ["main", "__version__"]
