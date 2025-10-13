"""
Test Session-Aware Notes Feature
♠️🌿🎸🧵 G.Music Assembly

Usage:
    python test_session.py

Requirements:
    - Chrome running with CDP: google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-simexp &
    - Logged into Simplenote
"""

import asyncio
import json
import os
from simexp.session_manager import (
    SessionState,
    generate_yaml_header,
    create_session_note,
    get_active_session,
    clear_active_session
)


def test_session_state():
    """Test SessionState class"""
    print("=" * 60)
    print("TEST 1: SessionState Persistence")
    print("=" * 60)

    # Create session state
    state = SessionState()

    # Save test session
    test_data = {
        'session_id': 'test-123-456',
        'note_url': 'https://app.simplenote.com/p/TEST',
        'ai_assistant': 'claude',
        'issue_number': 42
    }

    state.save_session(test_data)
    print(f"✅ Saved session data to {state.state_file}")

    # Load session
    loaded = state.load_session()
    assert loaded == test_data, "Session data mismatch!"
    print(f"✅ Loaded session matches saved data")

    # Clear session
    state.clear_session()
    assert state.load_session() is None, "Session not cleared!"
    print(f"✅ Session cleared successfully")

    print()


def test_yaml_generation():
    """Test YAML metadata generation"""
    print("=" * 60)
    print("TEST 2: YAML Metadata Generation")
    print("=" * 60)

    yaml_header = generate_yaml_header(
        session_id='abc-def-123',
        ai_assistant='claude',
        issue_number=4
    )

    print("Generated YAML:")
    print(yaml_header)

    # Verify YAML structure
    assert 'session_id: abc-def-123' in yaml_header
    assert 'ai_assistant: claude' in yaml_header
    assert 'issue_number: 4' in yaml_header
    assert '---' in yaml_header
    assert 'Jerry' in yaml_header
    assert 'Nyro' in yaml_header
    print("✅ YAML header generation successful")

    print()


async def test_session_creation():
    """Test session note creation"""
    print("=" * 60)
    print("TEST 3: Session Note Creation")
    print("=" * 60)

    # Verify Chrome is running
    import requests
    try:
        response = requests.get('http://localhost:9222/json/version', timeout=2)
        print(f"✅ Chrome CDP accessible: {response.json().get('Browser', 'Unknown')}")
    except:
        print("❌ Chrome not running with CDP!")
        print("   Run: google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-simexp &")
        return

    print("\n🔮 Creating test session note...")
    print("   (This will create an actual note in your Simplenote)")

    # Create session
    session_data = await create_session_note(
        ai_assistant='claude',
        issue_number=4,
        cdp_url='http://localhost:9222',
        debug=True
    )

    print(f"\n✅ Session created successfully!")
    print(f"   Session ID: {session_data['session_id']}")
    print(f"   Note URL: {session_data['note_url']}")

    # Verify session was saved
    loaded_session = get_active_session()
    assert loaded_session is not None, "Session not saved!"
    assert loaded_session['session_id'] == session_data['session_id']
    print(f"✅ Session state persisted correctly")

    # Clean up test session
    clear_active_session()
    print(f"✅ Test session cleared")

    print()


def test_get_active_session():
    """Test getting active session when none exists"""
    print("=" * 60)
    print("TEST 4: Get Active Session (No Session)")
    print("=" * 60)

    clear_active_session()  # Ensure no session exists

    session = get_active_session()
    assert session is None, "Should return None when no session exists"
    print("✅ Correctly returns None when no active session")

    print()


async def main():
    """Run all tests"""
    print("♠️🌿🎸🧵 Session-Aware Notes Test Suite")
    print("Testing Issue #4 Implementation\n")

    try:
        # Test 1: SessionState persistence
        test_session_state()

        # Test 2: YAML generation
        test_yaml_generation()

        # Test 3: Session creation (requires Chrome + Simplenote)
        await test_session_creation()

        # Test 4: Get active session (no session)
        test_get_active_session()

        print("=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\n💡 Next steps:")
        print("   1. Try: python -m simexp.simex session start --ai claude --issue 4")
        print("   2. Try: python -m simexp.simex session write 'Test message'")
        print("   3. Try: python -m simexp.simex session status")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
