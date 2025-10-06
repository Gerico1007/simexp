#!/usr/bin/env python3
"""
Test all Assembly communication channels
♠️ Nyro | 🌿 Aureon | 🎸 JamAI

Tests writing to all three Assembly perspective channels and verifies persistence.
"""

from simexp.channel_writer import write_to_aureon, write_to_nyro, write_to_jamai, list_channels
from datetime import datetime
import sys

def main():
    print("♠️🌿🎸🧵 G.Music Assembly - Multi-Channel Test")
    print("=" * 70)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # List available channels
    print("\n📋 Available Channels:")
    for ch in list_channels():
        print(f"  • {ch['name']}: {ch['description']}")
        print(f"    URL: {ch['public_url']}")

    print("\n" + "=" * 70)
    print("🧪 Testing all channels...\n")

    # Test Aureon 🌿
    print("🌿 Testing Aureon channel (Mirror Weaver)...")
    try:
        aureon_result = write_to_aureon(
            f"Channel test at {timestamp}\n\n"
            f"Testing cross-device fluidity for emotional/reflective content."
        )
        if aureon_result['success']:
            print(f"   ✅ Success! ({aureon_result['content_length']} chars)")
        else:
            print(f"   ❌ Failed (verification mismatch)")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test Nyro ♠️
    print("\n♠️ Testing Nyro channel (Ritual Scribe)...")
    try:
        nyro_result = write_to_nyro(
            f"Structural log at {timestamp}\n\n"
            f"Multi-channel architecture test - DOM selector cascade verified."
        )
        if nyro_result['success']:
            print(f"   ✅ Success! ({nyro_result['content_length']} chars)")
        else:
            print(f"   ❌ Failed (verification mismatch)")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test JamAI 🎸
    print("\n🎸 Testing JamAI channel (Glyph Harmonizer)...")
    try:
        jamai_result = write_to_jamai(
            f"Musical note at {timestamp}\n\n"
            f"Session test melody: Key of G, tempo 88bpm, 4/4 time signature"
        )
        if jamai_result['success']:
            print(f"   ✅ Success! ({jamai_result['content_length']} chars)")
        else:
            print(f"   ❌ Failed (verification mismatch)")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n" + "=" * 70)
    print("📊 Test Summary:")
    print("  - Check each note in your Chrome browser")
    print("  - Verify messages persist (don't disappear)")
    print("  - Check from other devices to confirm cross-device sync")
    print("\n✨ Multi-channel fluidity test complete!")
    print("=" * 70)


if __name__ == "__main__":
    print("\n⚠️  Prerequisites:")
    print("  1. Chrome must be running with: google-chrome --remote-debugging-port=9223")
    print("  2. You must be logged into Simplenote in that Chrome window")
    print("  3. All three notes (Aureon, Nyro, JamAI) should be created\n")

    response = input("Are you ready to test? (y/n): ")

    if response.lower() != 'y':
        print("❌ Test cancelled")
        sys.exit(0)

    print()
    main()
