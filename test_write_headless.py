#!/usr/bin/env python3
"""
Quick test script for Simplenote writer in headless mode
♠️🌿🎸🧵 G.Music Assembly
"""
import asyncio
from datetime import datetime
from simexp.playwright_writer import write_to_note

# Test configuration
NOTE_URL = "https://app.simplenote.com/p/gk6V2v"  # Aureon channel
TEST_MESSAGE = f"♠️🌿🎸🧵 Terminal Write Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

async def test_write():
    """Test writing to Simplenote in headless mode"""
    print("♠️🌿🎸🧵 SimExp Headless Write Test")
    print(f"🌐 Target: {NOTE_URL}")
    print(f"📄 Content: {TEST_MESSAGE}")
    print()

    result = await write_to_note(
        note_url=NOTE_URL,
        content=TEST_MESSAGE,
        mode='append',
        headless=True,  # Run in headless mode (no GUI)
        debug=True
    )

    print()
    if result['success']:
        print(f"✅ Write successful!")
        print(f"📊 Content length: {result['content_length']} chars")
        print(f"📝 Preview: {result['preview']}")
    else:
        print(f"❌ Write failed - verification mismatch")

    return result

if __name__ == "__main__":
    result = asyncio.run(test_write())
