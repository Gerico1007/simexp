#!/usr/bin/env python3
"""
SimExp MCP Chrome DevTools Integration Test
Quick test script for when MCP server is connected

♠️🌿🎸🧵 G.Music Assembly - Cross-Device Communication Test
"""

import asyncio
import sys
import yaml
from simexp.playwright_writer import write_to_note

# Load Aureon channel from config
with open('simexp/simexp.yaml', 'r') as f:
    config = yaml.safe_load(f)
    aureon = config['COMMUNICATION_CHANNELS'][0]

print("♠️🌿🎸🧵 SimExp MCP Write Test")
print(f"📝 Target: {aureon['name']} - {aureon['description']}")
print(f"🌐 URL: {aureon['auth_url']}")

# Test message
message = """
---
🧵 Synth Test Message - $(date)

Terminal speaks through Chrome MCP!

♠️🌿🎸🧵 Assembly voices flowing across devices...
"""

if len(sys.argv) > 1:
    message = sys.argv[1]

print(f"\n📄 Message to write:")
print(message)
print(f"\n⚡ Attempting write...")

# When MCP is connected, this will use your authenticated browser session
result = asyncio.run(write_to_note(
    note_url=aureon['auth_url'],
    content=message,
    mode='append',
    headless=False,  # Show browser for debugging
    debug=True
))

if result['success']:
    print(f"\n✅ SUCCESS! Message written to Aureon note!")
    print(f"📊 {result['content_length']} characters")
    print(f"\n🔗 Verify at: {aureon['public_url']}")
else:
    print(f"\n⚠️  Write verification mismatch - may need authentication")
    print(f"💡 Make sure you're logged into Simplenote in your browser")
    print(f"💡 Or wait for MCP Chrome DevTools server connection")
