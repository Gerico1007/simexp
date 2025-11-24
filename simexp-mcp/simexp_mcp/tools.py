"""
SimExp MCP Tools

Implements all MCP tools that wrap SimExp CLI commands and functionality.
Each tool provides:
- Tool definition (name, description, input schema)
- Argument validation
- CLI command execution
- Error handling
"""

import subprocess
import json
import os
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path
from mcp.types import Tool


# Tool Registry
_TOOLS_REGISTRY: Dict[str, Dict[str, Any]] = {}


def tool(name: str, description: str, input_schema: Dict[str, Any]):
    """Decorator to register an MCP tool"""
    def decorator(func: Callable) -> Callable:
        _TOOLS_REGISTRY[name] = {
            "name": name,
            "description": description,
            "input_schema": input_schema,
            "handler": func,
        }
        return func
    return decorator


# ============================================================================
# Session Management Tools
# ============================================================================

@tool(
    name="simexp_session_start",
    description="Start a new Simplenote session, optionally with a file, AI assistant, GitHub issue, or repository context",
    input_schema={
        "type": "object",
        "properties": {
            "file": {
                "type": "string",
                "description": "Optional file path to initialize session with"
            },
            "ai": {
                "type": "string",
                "description": "AI assistant name (e.g., 'claude', 'gpt4')"
            },
            "issue": {
                "type": "integer",
                "description": "GitHub issue number for context"
            },
            "repo": {
                "type": "string",
                "description": "Repository in format 'owner/name'"
            },
            "delay": {
                "type": "integer",
                "description": "Delay in seconds before starting"
            }
        }
    }
)
async def session_start(file: Optional[str] = None, ai: Optional[str] = None,
                        issue: Optional[int] = None, repo: Optional[str] = None,
                        delay: Optional[int] = None) -> Dict[str, Any]:
    """Start a new session"""
    cmd = ["simexp", "session", "start"]
    if file:
        cmd.append(file)
    if ai:
        cmd.extend(["--ai", ai])
    if issue:
        cmd.extend(["--issue", str(issue)])
    if repo:
        cmd.extend(["--repo", repo])
    if delay:
        cmd.extend(["--delay", str(delay)])

    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


@tool(
    name="simexp_session_list",
    description="List all sessions in directory tree format",
    input_schema={"type": "object", "properties": {}}
)
async def session_list() -> Dict[str, Any]:
    """List all sessions"""
    cmd = ["simexp", "session", "list"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


@tool(
    name="simexp_session_info",
    description="Show current session and directory context",
    input_schema={"type": "object", "properties": {}}
)
async def session_info() -> Dict[str, Any]:
    """Show current session info"""
    cmd = ["simexp", "session", "info"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


@tool(
    name="simexp_session_clear",
    description="Clear the active session",
    input_schema={"type": "object", "properties": {}}
)
async def session_clear() -> Dict[str, Any]:
    """Clear active session"""
    cmd = ["simexp", "session", "clear"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


# ============================================================================
# Session Content Tools
# ============================================================================

@tool(
    name="simexp_session_write",
    description="Write a message to the current session note",
    input_schema={
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "Message to write to session note"
            }
        },
        "required": ["message"]
    }
)
async def session_write(message: str) -> Dict[str, Any]:
    """Write to session note"""
    cmd = ["simexp", "session", "write", message]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


@tool(
    name="simexp_session_read",
    description="Read the current session note content",
    input_schema={"type": "object", "properties": {}}
)
async def session_read() -> Dict[str, Any]:
    """Read session note"""
    cmd = ["simexp", "session", "read"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


@tool(
    name="simexp_session_add",
    description="Add a file to the current session note with optional heading",
    input_schema={
        "type": "object",
        "properties": {
            "file": {
                "type": "string",
                "description": "File path to add to session note"
            },
            "heading": {
                "type": "string",
                "description": "Optional heading for the file content"
            }
        },
        "required": ["file"]
    }
)
async def session_add(file: str, heading: Optional[str] = None) -> Dict[str, Any]:
    """Add file to session note"""
    cmd = ["simexp", "session", "add", file]
    if heading:
        cmd.extend(["--heading", heading])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


@tool(
    name="simexp_session_title",
    description="Set the title of the current session note",
    input_schema={
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "New title for session note"
            }
        },
        "required": ["title"]
    }
)
async def session_title(title: str) -> Dict[str, Any]:
    """Set session note title"""
    cmd = ["simexp", "session", "title", title]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


@tool(
    name="simexp_session_open",
    description="Open the current session note in browser",
    input_schema={"type": "object", "properties": {}}
)
async def session_open() -> Dict[str, Any]:
    """Open session note in browser"""
    cmd = ["simexp", "session", "open"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


@tool(
    name="simexp_session_url",
    description="Get the URL of the current session note",
    input_schema={"type": "object", "properties": {}}
)
async def session_url() -> Dict[str, Any]:
    """Get session note URL"""
    cmd = ["simexp", "session", "url"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


# ============================================================================
# Collaboration Tools
# ============================================================================

@tool(
    name="simexp_session_collab",
    description="Share session with Assembly members or groups (♠️ Nyro, 🌿 Aureon, 🎸 JamAI, 🧵 Synth, assembly)",
    input_schema={
        "type": "object",
        "properties": {
            "member": {
                "type": "string",
                "description": "Assembly member symbol/name or 'assembly' for all"
            }
        },
        "required": ["member"]
    }
)
async def session_collab(member: str) -> Dict[str, Any]:
    """Share with Assembly member"""
    cmd = ["simexp", "session", "collab", member]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


@tool(
    name="simexp_session_collab_add",
    description="Add a collaborator by email address",
    input_schema={
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "Email address of collaborator to add"
            }
        },
        "required": ["email"]
    }
)
async def session_collab_add(email: str) -> Dict[str, Any]:
    """Add collaborator by email"""
    cmd = ["simexp", "session", "collab", "add", email]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


@tool(
    name="simexp_session_collab_list",
    description="List all collaborators on current session",
    input_schema={"type": "object", "properties": {}}
)
async def session_collab_list() -> Dict[str, Any]:
    """List collaborators"""
    cmd = ["simexp", "session", "collab", "list"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


@tool(
    name="simexp_session_publish",
    description="Publish the current session note and get a public URL",
    input_schema={"type": "object", "properties": {}}
)
async def session_publish() -> Dict[str, Any]:
    """Publish session note"""
    cmd = ["simexp", "session", "publish"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


# ============================================================================
# Reflection & Wisdom Tools
# ============================================================================

@tool(
    name="simexp_session_reflect",
    description="Open editor for reflection notes with optional prompt",
    input_schema={
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Optional prompt for reflection"
            }
        }
    }
)
async def session_reflect(prompt: Optional[str] = None) -> Dict[str, Any]:
    """Reflect on session"""
    cmd = ["simexp", "session", "reflect"]
    if prompt:
        cmd.extend(["--prompt", prompt])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


@tool(
    name="simexp_session_observe_pattern",
    description="Record an observed pattern in the session",
    input_schema={
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Pattern observation to record"
            }
        },
        "required": ["pattern"]
    }
)
async def session_observe_pattern(pattern: str) -> Dict[str, Any]:
    """Record observed pattern"""
    cmd = ["simexp", "session", "observe-pattern", pattern]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


@tool(
    name="simexp_session_extract_wisdom",
    description="Extract and record wisdom from session content",
    input_schema={
        "type": "object",
        "properties": {
            "wisdom": {
                "type": "string",
                "description": "Wisdom to extract and record"
            }
        },
        "required": ["wisdom"]
    }
)
async def session_extract_wisdom(wisdom: str) -> Dict[str, Any]:
    """Extract wisdom from session"""
    cmd = ["simexp", "session", "extract-wisdom", wisdom]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


@tool(
    name="simexp_session_complete",
    description="Complete the session with optional seed values for follow-up",
    input_schema={
        "type": "object",
        "properties": {
            "seeds": {
                "type": "string",
                "description": "Comma-separated seed values for follow-up work"
            }
        }
    }
)
async def session_complete(seeds: Optional[str] = None) -> Dict[str, Any]:
    """Complete session"""
    cmd = ["simexp", "session", "complete"]
    if seeds:
        cmd.extend(["--seeds", seeds])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


# ============================================================================
# Core Extraction Tools
# ============================================================================

@tool(
    name="simexp_init",
    description="Initialize a Simplenote session with browser-based authentication",
    input_schema={"type": "object", "properties": {}}
)
async def init() -> Dict[str, Any]:
    """Initialize SimExp session with browser auth"""
    # First check if session exists
    check_cmd = ["simexp", "session", "info"]
    check_result = subprocess.run(check_cmd, capture_output=True, text=True)

    if check_result.returncode == 0:
        return {
            "status": "success",
            "message": "Session already initialized",
            "output": check_result.stdout,
        }

    # No session, launch browser auth
    auth_cmd = ["simexp", "session", "browser", "--launch"]
    result = subprocess.run(auth_cmd, capture_output=True, text=True)

    return {
        "status": "success" if result.returncode == 0 else "error",
        "message": "Browser opened for Simplenote authentication",
        "output": result.stdout,
        "error": result.stderr,
    }


@tool(
    name="simexp_extract",
    description="Extract content from a URL",
    input_schema={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL to extract content from"
            }
        },
        "required": ["url"]
    }
)
async def extract(url: str) -> Dict[str, Any]:
    """Extract content from URL"""
    cmd = ["simexp", "extract", url]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


@tool(
    name="simexp_write",
    description="Write content to Simplenote",
    input_schema={
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Title of the note"
            },
            "content": {
                "type": "string",
                "description": "Content to write"
            }
        },
        "required": ["title", "content"]
    }
)
async def write(title: str, content: str) -> Dict[str, Any]:
    """Write to Simplenote"""
    cmd = ["simexp", "write", "--title", title, "--content", content]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


@tool(
    name="simexp_read",
    description="Read content from Simplenote",
    input_schema={
        "type": "object",
        "properties": {
            "note_id": {
                "type": "string",
                "description": "ID or title of note to read"
            }
        },
        "required": ["note_id"]
    }
)
async def read(note_id: str) -> Dict[str, Any]:
    """Read from Simplenote"""
    cmd = ["simexp", "read", note_id]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


@tool(
    name="simexp_archive",
    description="Archive content to local storage",
    input_schema={
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "Content to archive"
            },
            "title": {
                "type": "string",
                "description": "Title for archived content"
            }
        },
        "required": ["content"]
    }
)
async def archive(content: str, title: Optional[str] = None) -> Dict[str, Any]:
    """Archive content"""
    cmd = ["simexp", "archive"]
    if title:
        cmd.extend(["--title", title])
    # Pass content via stdin
    result = subprocess.run(cmd, input=content, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


@tool(
    name="simexp_fetch",
    description="Fetch content using Simfetcher capabilities",
    input_schema={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL to fetch"
            }
        },
        "required": ["url"]
    }
)
async def fetch(url: str) -> Dict[str, Any]:
    """Fetch content with Simfetcher"""
    cmd = ["simexp", "fetch", url]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


@tool(
    name="simexp_session_browser",
    description="Launch browser for Simplenote authentication and interaction",
    input_schema={"type": "object", "properties": {}}
)
async def session_browser() -> Dict[str, Any]:
    """Launch browser for authentication"""
    cmd = ["simexp", "session", "browser", "--launch"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "success" if result.returncode == 0 else "error",
        "output": result.stdout,
        "error": result.stderr,
    }


# ============================================================================
# Public API
# ============================================================================

def get_all_tools() -> List[Tool]:
    """Get all registered MCP tools"""
    tools = []
    for tool_config in _TOOLS_REGISTRY.values():
        tools.append(Tool(
            name=tool_config["name"],
            description=tool_config["description"],
            inputSchema=tool_config["input_schema"],
        ))
    return tools


async def execute_tool(name: str, arguments: dict) -> Any:
    """Execute a registered tool by name"""
    if name not in _TOOLS_REGISTRY:
        raise ValueError(f"Unknown tool: {name}")

    tool_config = _TOOLS_REGISTRY[name]
    handler = tool_config["handler"]

    # Call the handler with unpacked arguments
    return await handler(**arguments)
