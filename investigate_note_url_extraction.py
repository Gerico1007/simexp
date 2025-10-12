"""
Investigation: How to get the note URL after creating it?
♠️🌿🎸🧵 Assembly Debug Session - Part 2
"""

import asyncio
from playwright.async_api import async_playwright

async def investigate_url_extraction():
    """
    Try different methods to extract the new note's URL:
    1. Click on note in list → check if URL changes
    2. Look for Share/Publish button
    3. Check note info/settings
    """
    playwright = await async_playwright().start()
    browser = await playwright.chromium.connect_over_cdp('http://localhost:9223')
    context = browser.contexts[0]
    page = await context.new_page()

    print("=" * 60)
    print("🔍 INVESTIGATION: How to Extract Note URL")
    print("=" * 60)

    # Navigate to Simplenote
    print("\n1️⃣ Navigating to Simplenote...")
    await page.goto('https://app.simplenote.com/')
    await page.wait_for_load_state('networkidle')

    # Click New Note
    print("\n2️⃣ Creating new note...")
    new_note_button = await page.wait_for_selector('button[aria-label*="New Note"]')
    await new_note_button.click()
    await asyncio.sleep(2)

    # Try to find and click the note info button
    print("\n3️⃣ Looking for note info/settings button...")
    info_buttons = await page.query_selector_all('button[aria-label*="Info"]')
    print(f"   Found {len(info_buttons)} info buttons")

    if info_buttons:
        print("   Clicking info button...")
        await info_buttons[0].click()
        await asyncio.sleep(1)

        # Look for share/publish URL
        print("   Looking for share URL in info panel...")
        info_panel_html = await page.evaluate("""
            () => {
                const infoPanel = document.querySelector('.note-info');
                return infoPanel ? infoPanel.outerHTML : 'Not found';
            }
        """)
        print(f"   Info panel HTML: {info_panel_html[:500]}...")

    # Try to find Share/Publish button
    print("\n4️⃣ Looking for Share/Publish button...")
    share_buttons = await page.query_selector_all('button[aria-label*="Share"], button[aria-label*="Publish"]')
    print(f"   Found {len(share_buttons)} share/publish buttons")

    # Look for any links that might contain the note URL
    print("\n5️⃣ Searching for links with /p/ pattern...")
    links = await page.query_selector_all('a[href*="/p/"]')
    print(f"   Found {len(links)} links with /p/ pattern")

    if links:
        for i, link in enumerate(links[:3]):
            href = await link.get_attribute('href')
            print(f"   Link {i}: {href}")

    # Check if we can extract note ID from the first note in list
    print("\n6️⃣ Checking if note list items have clickable links...")
    note_items = await page.query_selector_all('.note-list-item')
    if note_items:
        first_note = note_items[0]

        # Click on it
        print("   Clicking on first note in list...")
        await first_note.click()
        await asyncio.sleep(1)

        url_after_click = page.url
        print(f"   URL after clicking note: {url_after_click}")

        if '/p/' in url_after_click:
            print(f"   ✅ SUCCESS! URL changed to: {url_after_click}")
        else:
            print(f"   ❌ URL still doesn't have /p/ pattern")

    # Try right-clicking on note to see context menu
    print("\n7️⃣ Checking for 'Copy Link' or similar in context menu...")
    # (Context menus are harder to inspect programmatically)

    # Check Monaco editor for any metadata
    print("\n8️⃣ Checking Monaco editor attributes...")
    editor_attrs = await page.evaluate("""
        () => {
            const editor = document.querySelector('.monaco-editor');
            if (!editor) return null;

            return {
                id: editor.id,
                classList: Array.from(editor.classList),
                dataAttrs: Object.keys(editor.dataset)
            };
        }
    """)
    print(f"   Monaco editor: {editor_attrs}")

    # Try to find the note ID by inspecting React/Redux state
    print("\n9️⃣ Attempting to access React/Redux state...")
    try:
        react_state = await page.evaluate("""
            () => {
                // Try to find React Fiber
                const rootElement = document.querySelector('#root');
                if (!rootElement) return null;

                const fiberKey = Object.keys(rootElement).find(key =>
                    key.startsWith('__reactInternalInstance') ||
                    key.startsWith('__reactFiber')
                );

                if (!fiberKey) return null;

                // Try to traverse to find note data
                // This is a simplified attempt
                return 'Found React instance but state inspection requires deeper traversal';
            }
        """)
        print(f"   React state: {react_state}")
    except Exception as e:
        print(f"   ⚠️  Could not access React state: {e}")

    print("\n" + "=" * 60)
    print("📊 URL EXTRACTION METHODS SUMMARY")
    print("=" * 60)

    await page.close()
    await playwright.stop()

if __name__ == "__main__":
    asyncio.run(investigate_url_extraction())
