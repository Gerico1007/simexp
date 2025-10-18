#!/usr/bin/env python3
"""
Comprehensive test of session add command with full diagnostic output
Shows both stdout and stderr to capture all error messages
"""

import asyncio
import sys
import os
from pathlib import Path
from simexp.session_manager import SessionManager

# Create a test content file
test_content = """
# Test Session Content
This is a test file for session add diagnostic.
Contains multiple lines to validate clipboard paste functionality.
The goal is to add this to a session note via clipboard (fast) instead of typing.
With clipboard, this should take <5 seconds.
With typing, it would take 30+ seconds.
Let's see which method actually executes!
"""

async def test_session_add():
    print("\n" + "="*60)
    print("🧪 COMPREHENSIVE SESSION ADD TEST WITH DIAGNOSTICS")
    print("="*60 + "\n")
    
    # Create test file
    test_file = Path("/tmp/test_session_add_diagnostic.txt")
    test_file.write_text(test_content)
    print(f"📝 Created test file: {test_file}")
    print(f"   Size: {len(test_content)} characters\n")
    
    # Get or create a session
    print("📋 Setting up SessionManager...")
    manager = SessionManager(
        simplenote_url="https://app.simplenote.com/",
        cdp_url="http://localhost:9222",
        session_dir="./sessions"
    )
    
    # Find or create a session
    try:
        # Try to find first available session
        sessions = manager.list_sessions()
        if sessions:
            session_id = sessions[0]
            print(f"✅ Using existing session: {session_id}\n")
        else:
            # Create a new test session
            print("⚠️  No sessions found. You'll need to run: simexp session new")
            print("   Then use: simexp session add <test-file>\n")
            return
    except Exception as e:
        print(f"⚠️  Could not list sessions: {e}\n")
        return
    
    # Now test the add command
    print("="*60)
    print("🚀 RUNNING SESSION ADD COMMAND")
    print("="*60 + "\n")
    print(f"Command: simexp session add {test_file}")
    print(f"Session: {session_id}")
    print(f"Content length: {len(test_content)} chars\n")
    
    print("-"*60)
    print("EXPECTED OUTPUT:")
    print("-"*60)
    print("📋 Attempting clipboard paste for XXX chars...")
    print("✅ paste_content(): Content copied to clipboard")
    print("🔍 paste_content(): Looking for editor...")
    print("✅ paste_content(): Found editor: [selector]")
    print("✅ paste_content(): Editor focused")
    print("🔚 paste_content(): Jumped to end of note")
    print("🔗 paste_content(): Sending paste shortcut (Control+V)...")
    print("✅ paste_content(): Content pasted successfully")
    print("🧹 paste_content(): Clipboard cleared (security)")
    print("✅ Clipboard paste succeeded!")
    print("-"*60 + "\n")
    
    print("🔍 ACTUAL OUTPUT CAPTURED:\n")
    print("-"*60)
    
    # Run simexp session add and capture output
    os.system(f"simexp session add {test_file}")
    
    print("-"*60 + "\n")
    print("="*60)
    print("✅ TEST COMPLETE - Check output above for actual behavior")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(test_session_add())
