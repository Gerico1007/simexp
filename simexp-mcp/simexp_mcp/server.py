"""
SimExp MCP Server

Core MCP (Model Context Protocol) server implementation that exposes
all SimExp functionality via MCP tools and resources.

This server enables Claude and other AI agents to:
- Manage Simplenote sessions
- Extract web content
- Write and read notes
- Collaborate and publish content
- Reflect and extract wisdom
"""

import asyncio
import json
import subprocess
from typing import Any, Optional
from pathlib import Path

from mcp.server import Server
from mcp.types import Tool, TextContent, CallToolResult

from simexp_mcp.tools import get_all_tools, execute_tool


class SimExpMCPServer:
    """MCP Server for SimExp functionality"""

    def __init__(self):
        self.server = Server("simexp")
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP protocol handlers"""

        @self.server.list_tools()
        async def list_tools():
            """List all available SimExp tools"""
            return get_all_tools()

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[CallToolResult]:
            """Execute a SimExp tool"""
            try:
                result = await execute_tool(name, arguments)
                return [CallToolResult(
                    type="text",
                    content=[TextContent(
                        type="text",
                        text=json.dumps(result) if isinstance(result, dict) else str(result)
                    )]
                )]
            except Exception as e:
                return [CallToolResult(
                    type="text",
                    content=[TextContent(
                        type="text",
                        text=f"Error executing tool '{name}': {str(e)}"
                    )],
                    isError=True
                )]

    async def run(self):
        """Start the MCP server"""
        async with self.server:
            print("✅ SimExp MCP Server running...")
            await self.server.wait()


def main():
    """Entry point for simexp-mcp command"""
    server = SimExpMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
