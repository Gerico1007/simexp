"""
Test Suite for Phase 1: Four Directions Core Infrastructure

Tests the four core functions added in Phase 1:
- initialize_four_directions_session()
- update_session_data()
- calculate_session_stats()
- migrate_legacy_session()

♠️🌿🎸🧵 G.Music Assembly - Four Directions Enhancement
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

from simexp.session_manager import (
    initialize_four_directions_session,
    update_session_data,
    calculate_session_stats,
    migrate_legacy_session,
    SessionState,
    get_active_session,
    clear_active_session
)


def test_initialize_four_directions_session():
    """Test initialize_four_directions_session function"""
    print("\n" + "=" * 70)
    print("TEST 1: initialize_four_directions_session()")
    print("=" * 70)

    # Create minimal session data
    session_data = {
        'session_id': 'test-uuid-123',
        'search_key': 'test-uuid-123',
        'created_at': datetime.now().isoformat(),
        'ai_assistant': 'claude'
    }

    # Initialize Four Directions
    result = initialize_four_directions_session(session_data)

    # Verify structure
    assert 'east' in result, "Missing 'east' direction"
    assert 'south' in result, "Missing 'south' direction"
    assert 'west' in result, "Missing 'west' direction"
    assert 'north' in result, "Missing 'north' direction"
    assert 'stats' in result, "Missing 'stats'"
    print("✅ All four directions present")

    # Verify East structure
    assert result['east']['vision_statement'] is None
    assert result['east']['goals'] == []
    print("✅ East direction structure correct")

    # Verify South structure
    assert result['south']['files_added'] == []
    assert result['south']['content_written'] == []
    assert result['south']['collaborations'] == []
    print("✅ South direction structure correct")

    # Verify West structure
    assert result['west']['published'] is False
    assert result['west']['published_at'] is None
    assert result['west']['public_url'] is None
    assert result['west']['opened_in_browser'] == []
    print("✅ West direction structure correct")

    # Verify North structure
    assert result['north']['reflection_notes'] == []
    assert result['north']['observed_patterns'] == []
    assert result['north']['extracted_wisdom'] == []
    assert result['north']['completed'] is False
    assert result['north']['completed_at'] is None
    assert result['north']['seeds_for_next'] == []
    print("✅ North direction structure correct")

    # Verify stats structure
    assert result['stats']['total_files'] == 0
    assert result['stats']['total_writes'] == 0
    assert result['stats']['total_collaborators'] == 0
    assert result['stats']['completion_percentage'] == 0
    print("✅ Stats structure correct")

    print("✅ TEST 1 PASSED")


def test_migrate_legacy_session():
    """Test migrate_legacy_session function"""
    print("\n" + "=" * 70)
    print("TEST 2: migrate_legacy_session()")
    print("=" * 70)

    # Create legacy session (without Four Directions)
    legacy_session = {
        'session_id': 'legacy-123',
        'search_key': 'legacy-123',
        'created_at': datetime.now().isoformat(),
        'ai_assistant': 'claude',
        'issue_number': 42
    }

    # Migrate
    migrated = migrate_legacy_session(legacy_session)

    # Verify all new structures exist
    assert 'east' in migrated, "Failed to add 'east' direction"
    assert 'south' in migrated, "Failed to add 'south' direction"
    assert 'west' in migrated, "Failed to add 'west' direction"
    assert 'north' in migrated, "Failed to add 'north' direction"
    assert 'stats' in migrated, "Failed to add 'stats'"
    print("✅ All four directions added during migration")

    # Verify original data preserved
    assert migrated['session_id'] == 'legacy-123'
    assert migrated['ai_assistant'] == 'claude'
    assert migrated['issue_number'] == 42
    print("✅ Original session data preserved")

    # Verify idempotency (migrating again doesn't break it)
    migrated_again = migrate_legacy_session(migrated)
    assert migrated_again['session_id'] == migrated['session_id']
    print("✅ Migration is idempotent")

    print("✅ TEST 2 PASSED")


def test_calculate_session_stats():
    """Test calculate_session_stats function"""
    print("\n" + "=" * 70)
    print("TEST 3: calculate_session_stats()")
    print("=" * 70)

    # Create session with some data
    session = initialize_four_directions_session({
        'session_id': 'stats-test-123',
        'created_at': datetime.now().isoformat(),
        'ai_assistant': 'claude'
    })

    # Add some data to track
    session['south']['files_added'] = [
        {'timestamp': datetime.now().isoformat(), 'path': '/file1.txt', 'filename': 'file1.txt'},
        {'timestamp': datetime.now().isoformat(), 'path': '/file2.txt', 'filename': 'file2.txt'},
    ]

    session['south']['content_written'] = [
        {'timestamp': datetime.now().isoformat(), 'content_length': 100},
        {'timestamp': datetime.now().isoformat(), 'content_length': 200},
        {'timestamp': datetime.now().isoformat(), 'content_length': 150},
    ]

    session['south']['collaborations'] = [
        {'timestamp': datetime.now().isoformat(), 'collaborator_email': 'user1@example.com'},
        {'timestamp': datetime.now().isoformat(), 'collaborator_email': 'user2@example.com'},
    ]

    # Calculate stats
    result = calculate_session_stats(session)

    # Verify stats
    assert result['stats']['total_files'] == 2, f"Expected 2 files, got {result['stats']['total_files']}"
    print("✅ File count correct")

    assert result['stats']['total_writes'] == 3, f"Expected 3 writes, got {result['stats']['total_writes']}"
    print("✅ Write count correct")

    assert result['stats']['total_collaborators'] == 2, f"Expected 2 collaborators, got {result['stats']['total_collaborators']}"
    print("✅ Collaborator count correct")

    # Verify completion percentage (should be 25% - only South has data)
    assert result['stats']['completion_percentage'] == 25, f"Expected 25%, got {result['stats']['completion_percentage']}%"
    print("✅ Completion percentage correct")

    # Add East data and recalculate
    result['east']['vision_statement'] = "Build amazing features"
    result = calculate_session_stats(result)
    assert result['stats']['completion_percentage'] == 50, f"Expected 50%, got {result['stats']['completion_percentage']}%"
    print("✅ Completion percentage updated with East data")

    print("✅ TEST 3 PASSED")


def test_update_session_data():
    """Test update_session_data function"""
    print("\n" + "=" * 70)
    print("TEST 4: update_session_data()")
    print("=" * 70)

    try:
        # Create and save a test session first
        test_session = initialize_four_directions_session({
            'session_id': 'update-test-123',
            'created_at': datetime.now().isoformat(),
            'ai_assistant': 'claude'
        })

        state = SessionState()
        state.save_session(test_session)
        print("✅ Test session created and saved")

        # Test adding a file to South
        update_session_data('south', 'files_added', {
            'path': '/test/file.md',
            'filename': 'file.md',
            'content_type': 'markdown',
            'size_chars': 500
        })
        print("✅ File added to south direction")

        # Reload session and verify
        loaded = get_active_session()
        assert len(loaded['south']['files_added']) > 0, "File not added"
        assert loaded['south']['files_added'][-1]['filename'] == 'file.md'
        print("✅ File persisted and retrievable")

        # Test adding a reflection note to North
        update_session_data('north', 'reflection_notes', {
            'prompt': 'What did we learn?',
            'reflection': 'This was a great learning experience'
        })
        print("✅ Reflection added to north direction")

        # Verify stats were updated
        loaded = get_active_session()
        assert loaded['stats']['total_files'] == 1
        print("✅ Stats updated after adding data")

        # Clean up
        clear_active_session()
        print("✅ Test session cleaned up")

        print("✅ TEST 4 PASSED")

    except Exception as e:
        print(f"❌ TEST 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_new_session_has_four_directions():
    """Test that new sessions automatically have Four Directions structure"""
    print("\n" + "=" * 70)
    print("TEST 5: New Session Creation Includes Four Directions")
    print("=" * 70)

    # Create a new session (simulating what create_session_note does)
    session_data = {
        'session_id': 'new-session-test',
        'search_key': 'new-session-test',
        'created_at': datetime.now().isoformat(),
        'ai_assistant': 'claude',
        'issue_number': 55
    }

    # Initialize Four Directions (this happens in create_session_note now)
    session_data = initialize_four_directions_session(session_data)

    # Save it
    state = SessionState()
    state.save_session(session_data)

    # Reload and verify
    loaded = get_active_session()
    assert loaded is not None, "Session not saved"
    assert 'east' in loaded
    assert 'south' in loaded
    assert 'west' in loaded
    assert 'north' in loaded
    assert 'stats' in loaded
    print("✅ New session includes full Four Directions structure")

    # Clean up
    clear_active_session()
    print("✅ TEST 5 PASSED")


def main():
    """Run all Phase 1 tests"""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Phase 1: Four Directions Core Infrastructure Tests".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")

    try:
        # Run all tests
        test_initialize_four_directions_session()
        test_migrate_legacy_session()
        test_calculate_session_stats()
        test_update_session_data()
        test_new_session_has_four_directions()

        print("\n" + "=" * 70)
        print("🎉 ALL PHASE 1 TESTS PASSED!")
        print("=" * 70)
        print("\n✅ Phase 1: Core Data Infrastructure is complete and tested")
        print("✅ Next: Phase 2 - South Direction File Tracking")
        print("")

    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
