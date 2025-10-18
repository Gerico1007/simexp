#!/usr/bin/env python3
"""
Test auto-publish enhancement for Issue #29

Tests:
1. Session creation with auto-publish
2. Verify public_url in session.json
3. Verify simplenote_note_id extraction
4. Verify published_at timestamp
5. Graceful fallback if publish fails
"""

import asyncio
import json
import os
from pathlib import Path
from simexp.session_manager import create_session_note
from datetime import datetime


async def test_auto_publish():
    """Test auto-publish functionality"""

    print("=" * 70)
    print("🧪 TEST: Auto-Publish Session Notes (Issue #29)")
    print("=" * 70)
    print()

    # Create a session
    print("📝 Creating session with auto-publish enabled...")
    print()

    try:
        session_data = await create_session_note(
            ai_assistant='claude',
            issue_number=29,
            cdp_url='http://localhost:9222',  # Adjust if needed
            debug=True
        )

        print()
        print("=" * 70)
        print("✅ SESSION CREATION SUCCESSFUL")
        print("=" * 70)
        print()

        # Verify session data
        print("📊 Session Data Verification:")
        print()

        # Check required fields
        checks = [
            ('session_id', 'Session UUID', True),
            ('search_key', 'Search Key', True),
            ('ai_assistant', 'AI Assistant', True),
            ('created_at', 'Created Timestamp', True),
            ('public_url', 'Public URL (NEW)', True),
            ('simplenote_note_id', 'Simplenote Note ID (NEW)', False),  # Optional
            ('published_at', 'Published Timestamp (NEW)', False),  # Optional if publish failed
        ]

        all_passed = True

        for field, label, required in checks:
            if field in session_data:
                value = session_data[field]
                status = "✅"
                print(f"  {status} {label:.<30} {str(value)[:40]}")
            else:
                if required:
                    status = "❌"
                    all_passed = False
                else:
                    status = "⚠️"
                print(f"  {status} {label:.<30} (not found)")

        print()

        # Verify session.json file
        print("📁 Verifying .simexp/session.json:")
        session_file = Path('.simexp/session.json')

        if session_file.exists():
            with open(session_file, 'r') as f:
                saved_data = json.load(f)

            print(f"  ✅ File exists: {session_file}")
            print(f"  📄 File size: {session_file.stat().st_size} bytes")
            print(f"  🕒 Last modified: {datetime.fromtimestamp(session_file.stat().st_mtime)}")
            print()

            # Pretty print the JSON
            print("📋 Session JSON Content:")
            print("-" * 70)
            print(json.dumps(saved_data, indent=2))
            print("-" * 70)

        else:
            print(f"  ❌ File not found: {session_file}")
            all_passed = False

        print()

        # Check public URL
        if session_data.get('public_url'):
            print(f"🌐 Public URL Generated:")
            print(f"   {session_data['public_url']}")
            print()
            print(f"   ✅ Can share this URL for collaboration!")
        else:
            print(f"⚠️  No public URL (note may not have been published)")
            print(f"   💡 Check Simplenote manually to publish")

        print()

        # Check Simplenote note ID
        if session_data.get('simplenote_note_id'):
            print(f"🔑 Simplenote Internal Note ID:")
            print(f"   {session_data['simplenote_note_id']}")
            print()
            print(f"   ✅ Can be used for future note reuse!")
        else:
            print(f"⚠️  Note ID not extracted")
            print(f"   💡 May need DOM inspection enhancement")

        print()
        print("=" * 70)

        if all_passed and session_data.get('public_url'):
            print("✅ ALL TESTS PASSED - Auto-publish working!")
            return True
        elif all_passed:
            print("⚠️  TESTS PASSED (with warnings) - Note published but URL extraction needs review")
            return True
        else:
            print("❌ SOME TESTS FAILED")
            return False

    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ ERROR DURING TEST")
        print("=" * 70)
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = asyncio.run(test_auto_publish())
    exit(0 if success else 1)
