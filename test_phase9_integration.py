"""
Integration Test Suite for Phase 9: Complete Four Directions Cycle

Tests the complete end-to-end workflow including:
- Full session lifecycle across all four directions
- Legacy session migration with data preservation
- Edge cases and error handling
- Stats accuracy and completion percentage
- Session persistence and recovery

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


def test_complete_ceremonial_cycle():
    """
    Test complete session lifecycle through all four directions
    Simulates a real-world session from start to completion
    """
    print("\n" + "=" * 70)
    print("TEST 1: Complete Ceremonial Cycle")
    print("=" * 70)

    try:
        # 1. START - Create session with intention (EAST)
        session = initialize_four_directions_session({
            'session_id': 'cycle-test-123',
            'created_at': datetime.now().isoformat(),
            'ai_assistant': 'claude'
        })

        # Set intention
        session['east']['vision_statement'] = "Build comprehensive test suite"
        session['east']['goals'] = [
            {'timestamp': datetime.now().isoformat(), 'goal': 'Complete integration tests'},
            {'timestamp': datetime.now().isoformat(), 'goal': 'Validate all features'}
        ]

        # Save
        state = SessionState()
        state.save_session(session)
        print("✅ EAST: Intention set - 'Build comprehensive test suite'")

        # 2. BUILD - Add files and content (SOUTH)
        session = get_active_session()

        # Add files
        update_session_data('south', 'files_added', {
            'path': '/test/file1.py',
            'filename': 'file1.py',
            'content_type': 'python',
            'size_chars': 1500
        })

        update_session_data('south', 'files_added', {
            'path': '/test/file2.md',
            'filename': 'file2.md',
            'content_type': 'markdown',
            'size_chars': 800
        })

        # Add writes
        update_session_data('south', 'content_written', {
            'content_length': 500,
            'mode': 'append',
            'has_timestamp': True
        })

        # Add collaborators
        update_session_data('south', 'collaborations', {
            'collaborator_email': 'alice@example.com',
            'glyph_used': '♠️'
        })

        print("✅ SOUTH: Added 2 files, 1 write, 1 collaborator")

        # 3. SHARE - Publish (WEST)
        session = get_active_session()
        session['west']['published'] = True
        session['west']['published_at'] = datetime.now().isoformat()
        session['west']['public_url'] = 'https://app.simplenote.com/p/TEST123'
        session['west']['opened_in_browser'] = [
            {'timestamp': datetime.now().isoformat(), 'action': 'opened'}
        ]

        state = SessionState()
        state.save_session(session)
        print("✅ WEST: Published - https://app.simplenote.com/p/TEST123")

        # 4. REFLECT - Add wisdom (NORTH)
        update_session_data('north', 'reflection_notes', {
            'prompt': 'What worked well?',
            'reflection': 'The Four Directions framework made organization natural'
        })

        update_session_data('north', 'observed_patterns', {
            'pattern': 'Session tracking reduces context switching'
        })

        update_session_data('north', 'extracted_wisdom', {
            'wisdom': 'Intentional sessions produce higher quality work'
        })

        # 5. COMPLETE - Mark completion
        session = get_active_session()
        session['north']['completed'] = True
        session['north']['completed_at'] = datetime.now().isoformat()
        session['north']['seeds_for_next'] = [
            {'timestamp': datetime.now().isoformat(), 'seed': 'Extend wisdom extraction'}
        ]

        # Recalculate stats
        session = calculate_session_stats(session)

        state = SessionState()
        state.save_session(session)

        print("✅ NORTH: Reflections, patterns, and wisdom recorded")
        print()

        # Verify completion stats
        session = get_active_session()
        assert session['stats']['total_files'] == 2, "Should have 2 files"
        assert session['stats']['total_writes'] == 1, "Should have 1 write"
        assert session['stats']['total_collaborators'] == 1, "Should have 1 collaborator"
        assert session['north']['completed'] == True, "Session should be completed"
        assert session['stats']['completion_percentage'] == 100, "Should be 100% complete (all directions touched)"

        print(f"📊 Session Stats:")
        print(f"   Files: {session['stats']['total_files']}")
        print(f"   Writes: {session['stats']['total_writes']}")
        print(f"   Collaborators: {session['stats']['total_collaborators']}")
        print(f"   Completion: {session['stats']['completion_percentage']}%")

        # Cleanup
        clear_active_session()
        print("\n✅ TEST 1 PASSED: Complete ceremonial cycle works")

    except Exception as e:
        print(f"❌ TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_legacy_migration_with_data():
    """
    Test migrating legacy sessions with existing data
    Ensures no data loss during upgrade
    """
    print("\n" + "=" * 70)
    print("TEST 2: Legacy Migration with Data Preservation")
    print("=" * 70)

    try:
        # Create legacy session with real data
        legacy = {
            'session_id': 'legacy-data-123',
            'search_key': 'legacy-data-123',
            'created_at': '2025-11-20T10:00:00',
            'ai_assistant': 'claude',
            'issue_number': 42,
            'custom_field': 'should be preserved'
        }

        # Migrate
        migrated = migrate_legacy_session(legacy)

        # Verify all original data preserved
        assert migrated['session_id'] == legacy['session_id']
        assert migrated['ai_assistant'] == legacy['ai_assistant']
        assert migrated['issue_number'] == legacy['issue_number']
        assert migrated['custom_field'] == legacy['custom_field']
        print("✅ All original data preserved")

        # Verify new structure added
        assert 'east' in migrated
        assert 'south' in migrated
        assert 'west' in migrated
        assert 'north' in migrated
        assert 'stats' in migrated
        print("✅ Four Directions structure added")

        # Verify idempotency (migrate again)
        migrated2 = migrate_legacy_session(migrated)
        assert migrated2['session_id'] == migrated['session_id']
        assert len(migrated2['east']) == len(migrated['east'])
        print("✅ Migration is idempotent (safe to run multiple times)")

        print("\n✅ TEST 2 PASSED: Legacy migration preserves data")

    except Exception as e:
        print(f"❌ TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_minimal_session():
    """
    Test minimal session with no data
    Ensures system handles edge case of empty sessions
    """
    print("\n" + "=" * 70)
    print("TEST 3: Minimal Session (Edge Case)")
    print("=" * 70)

    try:
        # Create minimal session
        session = initialize_four_directions_session({
            'session_id': 'minimal-123',
            'created_at': datetime.now().isoformat(),
            'ai_assistant': 'gemini'
        })

        state = SessionState()
        state.save_session(session)

        # Verify structure exists but is empty
        session = get_active_session()
        assert session['east']['vision_statement'] is None
        assert session['east']['goals'] == []
        assert session['south']['files_added'] == []
        assert session['stats']['total_files'] == 0
        assert session['stats']['completion_percentage'] == 0
        print("✅ Minimal session structure valid")

        # Verify stats calculation works on empty session
        session = calculate_session_stats(session)
        assert session['stats']['completion_percentage'] == 0
        print("✅ Stats calculation handles empty session")

        # Cleanup
        clear_active_session()
        print("\n✅ TEST 3 PASSED: Minimal sessions work")

    except Exception as e:
        print(f"❌ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_stats_accuracy():
    """
    Test accuracy of stats calculation across all directions
    Verifies completion percentage calculation
    """
    print("\n" + "=" * 70)
    print("TEST 4: Stats Accuracy")
    print("=" * 70)

    try:
        session = initialize_four_directions_session({
            'session_id': 'stats-test-123',
            'created_at': datetime.now().isoformat(),
            'ai_assistant': 'claude'
        })

        state = SessionState()
        state.save_session(session)

        # Test 1: No data = 0% completion
        session = get_active_session()
        session = calculate_session_stats(session)
        assert session['stats']['completion_percentage'] == 0
        print("✅ 0% completion: no data in any direction")

        # Test 2: Only South data = 25% completion
        session = get_active_session()
        session['south']['files_added'] = [{'path': '/test.txt'}]
        session = calculate_session_stats(session)
        assert session['stats']['completion_percentage'] == 25
        state.save_session(session)
        print("✅ 25% completion: South direction has data")

        # Test 3: South + West = 50% completion
        session = get_active_session()
        session['west']['published'] = True
        session = calculate_session_stats(session)
        assert session['stats']['completion_percentage'] == 50
        state.save_session(session)
        print("✅ 50% completion: South + West have data")

        # Test 4: All four directions = 100% completion
        # (requires north['completed'] = True)
        session = get_active_session()
        session['east']['vision_statement'] = "Test vision"
        session['north']['reflection_notes'] = [{'reflection': 'test'}]
        session['north']['completed'] = True  # Key requirement for 100%
        session = calculate_session_stats(session)
        assert session['stats']['completion_percentage'] == 100
        state.save_session(session)
        print("✅ 100% completion: All four directions have data + north.completed = True")

        # Cleanup
        clear_active_session()
        print("\n✅ TEST 4 PASSED: Stats accuracy verified")

    except Exception as e:
        print(f"❌ TEST 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_multiple_entries_tracking():
    """
    Test that multiple entries in arrays are tracked correctly
    Verifies count accuracy with multiple files, writes, etc.
    """
    print("\n" + "=" * 70)
    print("TEST 5: Multiple Entries Tracking")
    print("=" * 70)

    try:
        session = initialize_four_directions_session({
            'session_id': 'multi-test-123',
            'created_at': datetime.now().isoformat(),
            'ai_assistant': 'claude'
        })

        state = SessionState()
        state.save_session(session)

        # Add multiple files
        for i in range(5):
            update_session_data('south', 'files_added', {
                'path': f'/file{i}.txt',
                'filename': f'file{i}.txt',
                'content_type': 'text'
            })

        # Add multiple writes
        for i in range(3):
            update_session_data('south', 'content_written', {
                'content_length': 100 * (i + 1),
                'mode': 'append'
            })

        # Add multiple collaborators
        emails = ['alice@example.com', 'bob@example.com', 'charlie@example.com', 'alice@example.com']
        for email in emails:
            update_session_data('south', 'collaborations', {
                'collaborator_email': email
            })

        session = get_active_session()
        assert session['stats']['total_files'] == 5, f"Expected 5 files, got {session['stats']['total_files']}"
        assert session['stats']['total_writes'] == 3, f"Expected 3 writes, got {session['stats']['total_writes']}"
        # Note: collaborators should be unique count
        expected_collabs = 3  # alice, bob, charlie (alice counted once)
        assert session['stats']['total_collaborators'] == expected_collabs, f"Expected {expected_collabs} unique collaborators, got {session['stats']['total_collaborators']}"

        print(f"✅ Files: {session['stats']['total_files']}")
        print(f"✅ Writes: {session['stats']['total_writes']}")
        print(f"✅ Collaborators (unique): {session['stats']['total_collaborators']}")

        # Cleanup
        clear_active_session()
        print("\n✅ TEST 5 PASSED: Multiple entries tracked accurately")

    except Exception as e:
        print(f"❌ TEST 5 FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise


def main():
    """Run all integration tests"""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Phase 9: Integration Testing - Complete Cycle".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")

    try:
        test_complete_ceremonial_cycle()
        test_legacy_migration_with_data()
        test_minimal_session()
        test_stats_accuracy()
        test_multiple_entries_tracking()

        print("\n" + "=" * 70)
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("=" * 70)
        print("\n✅ Phase 9: Integration Testing Complete")
        print("✅ Ready for Phase 10: Code Review & Refinement")
        print()
        return True

    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
