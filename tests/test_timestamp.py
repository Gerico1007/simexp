#!/usr/bin/env python3
"""
Test script for tlid timestamp integration (Issue #33)
♠️ Nyro: Temporal glyph validation suite

Tests all granularity levels and formatting functions
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simexp.timestamp_utils import (
    get_timestamp,
    format_timestamped_entry,
    insert_after_metadata,
    get_default_granularity
)


def test_timestamp_granularities():
    """Test all tlid granularity levels"""
    print("♠️ Testing Timestamp Granularities")
    print("=" * 50)

    granularities = ['y', 'm', 'd', 'h', 's', 'ms']

    for gran in granularities:
        timestamp = get_timestamp(gran)
        print(f"  {gran:3s} → {timestamp}")

    print()


def test_manual_override():
    """Test manual timestamp override"""
    print("♠️ Testing Manual Override")
    print("=" * 50)

    manual = "2510231621"
    timestamp = get_timestamp(manual_override=manual)
    print(f"  Manual: {manual} → {timestamp}")
    assert timestamp == manual, "Manual override failed"
    print("  ✅ Manual override works correctly")
    print()


def test_formatted_entries():
    """Test formatted timestamped entries"""
    print("♠️ Testing Formatted Entries")
    print("=" * 50)

    test_cases = [
        ("Test entry", 's', False),
        ("Morning reflection", 'h', True),
        ("Daily note", 'd', False),
        ("Quick note", 'ms', False),
    ]

    for content, gran, prepend in test_cases:
        formatted = format_timestamped_entry(content, gran, prepend)
        print(f"  {gran:3s} {'[P]' if prepend else '[A]'} → {formatted}")

    print()


def test_metadata_insertion():
    """Test insertion after YAML metadata"""
    print("♠️ Testing Metadata Insertion")
    print("=" * 50)

    # Test note with metadata
    note_with_metadata = """---
session_id: abc-123
ai_assistant: claude
---

Existing content here
More content"""

    entry = "[251023162145] New timestamped entry"
    result = insert_after_metadata(note_with_metadata, entry)

    print("  Original note:")
    print("  " + "\n  ".join(note_with_metadata.split('\n')[:5]))
    print("  ...")
    print()
    print("  After insertion:")
    print("  " + "\n  ".join(result.split('\n')[:8]))
    print("  ...")

    # Verify entry is after metadata
    assert "[251023162145]" in result, "Entry not found in result"
    assert result.index("[251023162145]") > result.index("---"), "Entry not after metadata"
    print("  ✅ Metadata insertion works correctly")
    print()

    # Test note without metadata
    note_without_metadata = "Just some content\nNo metadata here"
    result2 = insert_after_metadata(note_without_metadata, entry)
    assert result2.startswith("[251023162145]"), "Entry not prepended when no metadata"
    print("  ✅ Prepending works when no metadata present")
    print()


def test_config_default():
    """Test default granularity from config"""
    print("♠️ Testing Config Default Granularity")
    print("=" * 50)

    default = get_default_granularity()
    print(f"  Default granularity: {default}")
    print("  (Override in ~/.simexp/simexp.yaml with 'default_date_format: h')")
    print()


def test_fallback_mode():
    """Test fallback when tlid not available"""
    print("♠️ Testing Fallback Mode")
    print("=" * 50)

    # Temporarily hide tlid import
    import sys
    tlid_backup = sys.modules.get('tlid')

    try:
        # Remove tlid from modules to trigger fallback
        if 'tlid' in sys.modules:
            del sys.modules['tlid']

        # Force reimport to trigger fallback
        from importlib import reload
        from simexp import timestamp_utils
        reload(timestamp_utils)

        timestamp = timestamp_utils.get_timestamp('s')
        print(f"  Fallback timestamp: {timestamp}")
        print(f"  Length: {len(timestamp)} (expected: 12 for seconds)")

        assert len(timestamp) == 12, f"Unexpected timestamp length: {len(timestamp)}"
        print("  ✅ Fallback mode works correctly")

    finally:
        # Restore tlid
        if tlid_backup:
            sys.modules['tlid'] = tlid_backup

    print()


def main():
    """Run all tests"""
    print("\n🎯 SimExp Timestamp Integration Test Suite")
    print("Issue #33: tlid Integration")
    print("=" * 50)
    print()

    try:
        test_timestamp_granularities()
        test_manual_override()
        test_formatted_entries()
        test_metadata_insertion()
        test_config_default()
        test_fallback_mode()

        print("=" * 50)
        print("✅ All tests passed!")
        print()
        print("💡 Next steps:")
        print("  1. Install tlid: pip install tlid")
        print("  2. Test with CLI: simexp session write 'Test' --date h")
        print("  3. Test prepend: simexp session write 'Entry' --prepend --date s")
        print()

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
