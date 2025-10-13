#!/usr/bin/env python3
"""
Test CDP Connection to Authenticated Chrome
Step-by-step guide for Jerry's cross-device flow

♠️🌿🎸🧵 G.Music Assembly
"""

import asyncio
from simexp.playwright_writer import SimplenoteWriter
from simexp.simex import get_cdp_url

# CDP endpoint where your Chrome is running (uses priority chain)
CDP_URL = get_cdp_url()

async def test_connection():
    """Test connecting to existing Chrome session"""

    print("♠️🌿🎸🧵 SimExp CDP Connection Test\n")
    print("=" * 60)

    # Step 1: Test connection
    print("\n🔗 Step 1: Testing CDP connection...")
    try:
        async with SimplenoteWriter(
            "https://app.simplenote.com",
            cdp_url=CDP_URL,
            debug=True
        ) as writer:
            print("✅ Successfully connected to Chrome!")

            # Step 2: Navigate to Simplenote
            print("\n🌐 Step 2: Navigating to Simplenote...")
            await writer.navigate()

            current_url = writer.page.url
            title = await writer.page.title()

            print(f"📍 Current URL: {current_url}")
            print(f"📄 Page title: {title}")

            # Check if logged in
            if "login" in current_url.lower():
                print("\n⚠️  You're on the login page!")
                print("💡 Please login to Simplenote in your Chrome browser")
                print("💡 Then run this test again")
                return False

            print("\n✅ You appear to be logged in!")

            # Step 3: Try to find a note editor
            print("\n🔍 Step 3: Looking for Simplenote editor...")
            await asyncio.sleep(2)

            # Take screenshot for debugging
            screenshot_path = "/tmp/simplenote_auth_test.png"
            await writer.page.screenshot(path=screenshot_path)
            print(f"📸 Screenshot saved: {screenshot_path}")

            return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

async def test_aureon_write():
    """Test writing to Aureon note via authenticated session"""

    print("\n" + "=" * 60)
    print("🌿 Testing Aureon Note Write")
    print("=" * 60)

    # We need to discover the correct URL format for Simplenote
    # It's likely a hash-based URL like: https://app.simplenote.com#note/{id}

    test_urls = [
        "https://app.simplenote.com",  # Main app
        "https://app.simplenote.com/#/note/e6702a7b90e64aae99df2fba1662bb81",  # Hash format
    ]

    for url in test_urls:
        print(f"\n🔍 Trying URL: {url}")
        try:
            async with SimplenoteWriter(url, cdp_url=CDP_URL, debug=True) as writer:
                await writer.navigate()
                await asyncio.sleep(3)  # Wait for app to load

                # Try to find editor
                try:
                    selector = await writer.find_editor()
                    print(f"✅ Found editor with: {selector}")

                    # Try to write
                    print("\n✍️  Attempting to write test message...")
                    result = await writer.write_content(
                        "♠️🌿🎸🧵 CDP Connection Test - Success!",
                        mode='append'
                    )

                    if result['success']:
                        print(f"\n🎉 WRITE SUCCESSFUL!")
                        print(f"📊 {result['content_length']} characters written")
                        return True

                except Exception as e:
                    print(f"❌ Could not find editor: {e}")
                    # Take screenshot
                    screenshot = f"/tmp/simplenote_test_{url.replace('/', '_')}.png"
                    await writer.page.screenshot(path=screenshot)
                    print(f"📸 Screenshot: {screenshot}")

        except Exception as e:
            print(f"❌ Error with URL: {e}")

    return False

if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  SimExp CDP Connection Guide                                ║
║  ♠️🌿🎸🧵 G.Music Assembly                                    ║
╚══════════════════════════════════════════════════════════════╝

BEFORE RUNNING THIS SCRIPT:

1. Launch Chrome with remote debugging (Chrome DevTools Protocol standard port):

   chromium --remote-debugging-port=9222 --user-data-dir=~/.chrome-simexp &

   Note: --user-data-dir is REQUIRED for Chrome 136+ security

2. In that Chrome window, open Simplenote:

   https://app.simplenote.com

3. Login to Simplenote

4. Open the Aureon note (or any note you want to test)

5. Keep Chrome window open and run this script

🔧 CDP Configuration:
   Using: {CDP_URL}
   (Priority: --cdp-url flag > SIMEXP_CDP_URL env > config file > default)

Press Enter when ready...
""")

    input()

    # Run tests
    print("\n🚀 Starting connection tests...\n")

    success = asyncio.run(test_connection())

    if success:
        print("\n✅ Connection test passed!")
        print("\n🔄 Proceeding to write test...")
        write_success = asyncio.run(test_aureon_write())

        if write_success:
            print("\n" + "=" * 60)
            print("🎉 ALL TESTS PASSED!")
            print("=" * 60)
            print("\n✅ Cross-device fluidity is ACTIVE!")
            print("🌊 Terminal can now speak to web pages!")
        else:
            print("\n💡 Connection works, but need to discover correct note URL")
            print("💡 Check the screenshots in /tmp/ to see what we found")
    else:
        print("\n❌ Connection failed - check the errors above")
        print(f"💡 Make sure Chrome is running with: chromium --remote-debugging-port=9222 --user-data-dir=~/.chrome-simexp &")
        print(f"💡 Currently trying to connect to: {CDP_URL}")
        print(f"💡 Override with: export SIMEXP_CDP_URL=http://localhost:9222")
