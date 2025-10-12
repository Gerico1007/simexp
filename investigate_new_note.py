"""
Investigation: How does Simplenote handle new note creation?
♠️🌿🎸🧵 Assembly Debug Session
"""

import asyncio
from playwright.async_api import async_playwright

async def investigate_new_note_behavior():
    """
    Click "New Note" and observe:
    1. Does URL change?
    2. Where is the note ID stored?
    3. How can we capture the new note's URL?
    """
    playwright = await async_playwright().start()
    browser = await playwright.chromium.connect_over_cdp('http://localhost:9223')
    context = browser.contexts[0]
    page = await context.new_page()

    print("=" * 60)
    print("🔍 INVESTIGATION: New Note Creation Behavior")
    print("=" * 60)

    # Navigate to Simplenote
    print("\n1️⃣ Navigating to Simplenote...")
    await page.goto('https://app.simplenote.com/')
    await page.wait_for_load_state('networkidle')
    initial_url = page.url
    print(f"   Initial URL: {initial_url}")

    # Click New Note button
    print("\n2️⃣ Clicking 'New Note' button...")
    new_note_button = await page.wait_for_selector('button[aria-label*="New Note"]')
    await new_note_button.click()

    # Wait a bit for note creation
    await asyncio.sleep(2)

    # Check URL after clicking
    url_after_click = page.url
    print(f"   URL after click: {url_after_click}")

    # Check if URL changed
    if url_after_click != initial_url:
        print(f"   ✅ URL CHANGED! New note URL: {url_after_click}")
    else:
        print(f"   ❌ URL DID NOT CHANGE - still at base URL")

    # Wait for network idle (in case URL updates asynchronously)
    print("\n3️⃣ Waiting for network idle...")
    await page.wait_for_load_state('networkidle')
    url_after_networkidle = page.url
    print(f"   URL after network idle: {url_after_networkidle}")

    # Check for URL pattern changes
    print("\n4️⃣ Checking if URL pattern includes /p/ (note ID)...")
    if '/p/' in url_after_networkidle:
        print(f"   ✅ Found /p/ pattern in URL: {url_after_networkidle}")
        note_id = url_after_networkidle.split('/p/')[-1]
        print(f"   📝 Note ID: {note_id}")
    else:
        print(f"   ❌ No /p/ pattern - URL is still: {url_after_networkidle}")

    # Try to find note ID in the DOM
    print("\n5️⃣ Searching for note ID in DOM...")

    # Check if there's a data attribute with note ID
    editor = await page.query_selector('div.note-editor')
    if editor:
        # Get all attributes
        editor_html = await editor.evaluate('el => el.outerHTML')
        print(f"   Editor element:\n{editor_html[:500]}...")

    # Check window location
    print("\n6️⃣ Checking JavaScript window.location...")
    location_info = await page.evaluate("""
        () => ({
            href: window.location.href,
            pathname: window.location.pathname,
            hash: window.location.hash
        })
    """)
    print(f"   Location info: {location_info}")

    # Check if there's app state with note ID
    print("\n7️⃣ Checking for Simplenote app state...")
    try:
        app_state = await page.evaluate("""
            () => {
                // Try to find note ID in various places
                const results = {
                    localStorage: {},
                    sessionStorage: {},
                    hash: window.location.hash
                };

                // Check localStorage
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    if (key.includes('note') || key.includes('selected')) {
                        try {
                            results.localStorage[key] = localStorage.getItem(key).substring(0, 200);
                        } catch(e) {}
                    }
                }

                return results;
            }
        """)
        print(f"   App state search results:")
        for storage_type, data in app_state.items():
            if data:
                print(f"   {storage_type}: {data}")
    except Exception as e:
        print(f"   ⚠️  Could not access app state: {e}")

    # Check the note list to see if new note appears
    print("\n8️⃣ Checking note list for newly created note...")
    note_list_items = await page.query_selector_all('.note-list-item')
    print(f"   Found {len(note_list_items)} notes in list")

    if note_list_items:
        first_note = note_list_items[0]
        first_note_html = await first_note.evaluate('el => el.outerHTML')
        print(f"   First note (likely the new one):\n{first_note_html[:300]}...")

        # Try to extract note ID from the list item
        try:
            note_id_from_list = await first_note.evaluate("""
                el => {
                    // Check for data attributes
                    const noteKey = el.getAttribute('data-note-key');
                    const noteId = el.getAttribute('data-note-id');
                    return {
                        noteKey,
                        noteId,
                        classList: Array.from(el.classList)
                    };
                }
            """)
            print(f"   Note data from list item: {note_id_from_list}")
        except Exception as e:
            print(f"   ⚠️  Could not extract note ID: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("📊 INVESTIGATION SUMMARY")
    print("=" * 60)
    print(f"Initial URL: {initial_url}")
    print(f"Final URL: {url_after_networkidle}")
    print(f"URL Changed: {'Yes' if url_after_networkidle != initial_url else 'No'}")

    await page.close()
    await playwright.stop()

if __name__ == "__main__":
    asyncio.run(investigate_new_note_behavior())
