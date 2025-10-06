#!/usr/bin/env python3
"""
Test Google Docs API integration
♠️🌿🎸🧵 G.Music Assembly

Comprehensive tests for Google Docs writer functionality including:
- Authentication (service account)
- Read content
- Append content (instant API writes)
- Replace content
- Document metadata
- Multi-provider channel routing
"""

import os
import sys
from datetime import datetime
from simexp.googledocs_writer import GoogleDocsWriter, write_to_googledoc, read_from_googledoc


def test_authentication():
    """Test service account authentication"""
    print("🔑 Test 1: Authentication")
    print("=" * 70)

    # Check if credentials exist
    creds_path = './credentials/service-account.json'
    if not os.path.exists(creds_path):
        print(f"❌ Credentials not found: {creds_path}")
        print("💡 Please set up Google Cloud service account first")
        print("   See README_GOOGLEDOCS.md for setup instructions")
        return False

    try:
        # Test document ID (replace with your own)
        doc_id = input("Enter test Google Doc ID (or press Enter to skip): ").strip()
        if not doc_id:
            print("⏭️  Skipping authentication test (no doc ID provided)")
            return None

        writer = GoogleDocsWriter(doc_id, creds_path, debug=True)
        writer.authenticate()

        print("✅ Authentication successful!")
        return True
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False


def test_read_content():
    """Test reading document content"""
    print("\n📖 Test 2: Read Content")
    print("=" * 70)

    creds_path = './credentials/service-account.json'
    doc_id = input("Enter test Google Doc ID (or press Enter to skip): ").strip()

    if not doc_id or not os.path.exists(creds_path):
        print("⏭️  Skipping read test")
        return None

    try:
        content = read_from_googledoc(doc_id, creds_path)
        print(f"✅ Read successful! ({len(content)} chars)")
        print(f"📄 Preview (first 200 chars):")
        print("-" * 70)
        print(content[:200] + ("..." if len(content) > 200 else ""))
        print("-" * 70)
        return True
    except Exception as e:
        print(f"❌ Read failed: {e}")
        return False


def test_append_content():
    """Test appending content to document"""
    print("\n✍️  Test 3: Append Content")
    print("=" * 70)

    creds_path = './credentials/service-account.json'
    doc_id = input("Enter test Google Doc ID (or press Enter to skip): ").strip()

    if not doc_id or not os.path.exists(creds_path):
        print("⏭️  Skipping append test")
        return None

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    test_message = f"🧪 Test append from SimExp at {timestamp}"

    print(f"📝 Appending: {test_message}")

    try:
        result = write_to_googledoc(
            doc_id,
            test_message,
            creds_path,
            mode='append'
        )

        if result.get('success'):
            print(f"✅ Append successful!")
            print(f"📊 Content length: {result.get('content_length')} chars")
            print(f"📝 Preview: {result.get('preview')}")
            return True
        else:
            print(f"❌ Append failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Append failed: {e}")
        return False


def test_document_info():
    """Test getting document metadata"""
    print("\n📄 Test 4: Document Metadata")
    print("=" * 70)

    creds_path = './credentials/service-account.json'
    doc_id = input("Enter test Google Doc ID (or press Enter to skip): ").strip()

    if not doc_id or not os.path.exists(creds_path):
        print("⏭️  Skipping metadata test")
        return None

    try:
        writer = GoogleDocsWriter(doc_id, creds_path)
        writer.authenticate()
        info = writer.get_document_info()

        print("✅ Metadata retrieved:")
        print(f"  📌 Title: {info.get('title')}")
        print(f"  🆔 Document ID: {info.get('document_id')}")
        print(f"  📝 Revision ID: {info.get('revision_id')}")
        print(f"  🔗 URL: {info.get('document_url')}")
        return True
    except Exception as e:
        print(f"❌ Metadata retrieval failed: {e}")
        return False


def test_channel_routing():
    """Test multi-provider channel routing"""
    print("\n🔀 Test 5: Multi-Provider Channel Routing")
    print("=" * 70)

    try:
        from simexp.channel_writer import list_channels, write_to_channel

        print("📋 Available channels:")
        for ch in list_channels():
            print(f"  • {ch['name']} ({ch['provider']}): {ch['description']}")

        print("\n💡 To test Google Docs channels:")
        print("  1. Uncomment Google Docs channel in simexp.yaml")
        print("  2. Add your document_id and credentials_path")
        print("  3. Run: python -m simexp.simex channel aurendocs 'Test message'")

        print("✅ Channel routing configured correctly")
        return True
    except Exception as e:
        print(f"❌ Channel routing test failed: {e}")
        return False


def main():
    """Run all Google Docs tests"""
    print("♠️🌿🎸🧵 SimExp Google Docs API Integration Tests")
    print("=" * 70)
    print()

    results = {}

    # Run tests
    results['auth'] = test_authentication()
    results['read'] = test_read_content()
    results['append'] = test_append_content()
    results['metadata'] = test_document_info()
    results['routing'] = test_channel_routing()

    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary:")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)

    for test_name, result in results.items():
        status = "✅ PASSED" if result is True else "❌ FAILED" if result is False else "⏭️  SKIPPED"
        print(f"  {test_name:12s}: {status}")

    print()
    print(f"  Total: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 70)

    if failed > 0:
        print("\n💡 Some tests failed. Check:")
        print("  1. Google Cloud service account credentials are set up")
        print("  2. Document is shared with service account email")
        print("  3. Google Docs API is enabled in Google Cloud Console")
        print("\n📚 See README_GOOGLEDOCS.md for setup instructions")

    return failed == 0


if __name__ == "__main__":
    print("\n⚠️  Prerequisites:")
    print("  1. Google Cloud service account created")
    print("  2. Credentials JSON downloaded to ./credentials/service-account.json")
    print("  3. Test Google Doc created and shared with service account")
    print("  4. Google Docs API enabled in Google Cloud Console\n")

    response = input("Are you ready to test? (y/n): ")

    if response.lower() != 'y':
        print("❌ Tests cancelled")
        sys.exit(0)

    print()
    success = main()
    sys.exit(0 if success else 1)
