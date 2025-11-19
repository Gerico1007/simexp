import os
import requests
from datetime import datetime
from typing import Optional
from .simfetcher import fetch_content
from .processor import process_content
from .archiver import save_as_markdown
import yaml
from .imp_clip import update_sources_from_clipboard, is_clipboard_content_valid
import asyncio
import pyperclip
import subprocess
import shutil
import time
import re
from .playwright_writer import write_to_note, read_from_note, SimplenoteWriter
from .session_manager import (
    create_session_note,
    get_active_session,
    clear_active_session,
    search_and_select_note,
    SessionState
)
from .session_sharing import (
    publish_session_note,
    add_session_collaborator,
    list_session_collaborators,
    share_session_note
)
from .session_manager import handle_session_add
from .timestamp_utils import format_timestamped_entry, insert_after_metadata

# Config file in user's home directory (not package directory)
CONFIG_FILE = os.path.expanduser('~/.simexp/simexp.yaml')

# ═══════════════════════════════════════════════════════════════
# PUBLIC URL RESOLUTION - Resolve public Simplenote URLs to internal UUIDs
# ♠️🌿🎸🧵 G.Music Assembly - Public to Private URL Resolution
# ═══════════════════════════════════════════════════════════════

def resolve_public_url(public_url: str, cdp_url: str = None) -> Optional[str]:
    """
    Resolve public Simplenote URL to internal note UUID

    Public URLs (https://app.simplenote.com/p/<uuid>) are read-only.
    This function tries two methods to extract the internal UUID:

    Method 1: Fetch public page and search for simplenote://note/<uuid> link
    Method 2: Use browser automation to navigate and extract from app URL

    Args:
        public_url: Public Simplenote URL (e.g., https://app.simplenote.com/p/0ZqWsQ)
        cdp_url: Chrome DevTools Protocol URL for browser automation fallback

    Returns:
        Internal note UUID (36-character UUID string) or None if not found

    Examples:
        >>> resolve_public_url('https://app.simplenote.com/p/0ZqWsQ')
        '76502186-4d7d-48d6-a961-80a48573b2c7'
    """
    print(f"🔍 Detecting public Simplenote URL...")
    print(f"   🌐 Public URL: {public_url}")

    # Method 1: Try extracting from public page HTML (if user embedded the link)
    print(f"   ⬇️  Method 1: Fetching public page content...", end=" ", flush=True)
    content = fetch_content(public_url)

    if content:
        print("✓")
        print(f"   🔎 Searching for embedded simplenote:// link...", end=" ", flush=True)
        # Pattern: simplenote://note/76502186-4d7d-48d6-a961-80a48573b2c7
        pattern = r'simplenote://note/([0-9a-fA-F-]{36})'
        match = re.search(pattern, content)

        if match:
            uuid = match.group(1)
            print("✓")
            print(f"   ♻️  Resolved UUID: {uuid}")
            return uuid
        else:
            print("❌")
    else:
        print("❌")

    # Method 2: Use browser automation to navigate from public URL
    print(f"   🌐 Method 2: Using browser navigation...")

    try:
        resolved_cdp = get_cdp_url(cdp_url)
        uuid = asyncio.run(_resolve_via_browser(public_url, resolved_cdp, debug=True))

        if uuid:
            print(f"   ♻️  Resolved UUID: {uuid}")
            return uuid
        else:
            print(f"   ❌ Browser navigation could not extract UUID")
    except Exception as e:
        print(f"   ❌ Browser navigation failed: {e}")

    print(f"\n   ⚠️  Could not resolve public URL to internal UUID")
    print(f"   💡 Tip: Add the internal link to your note:")
    print(f"   💡 1. Open the note in Simplenote app")
    print(f"   💡 2. Copy the internal link (simplenote://note/<uuid>)")
    print(f"   💡 3. Paste it anywhere in the note content")
    return None


async def _resolve_via_browser(public_url: str, cdp_url: str, debug: bool = True) -> Optional[str]:
    """
    Resolve public URL by navigating in authenticated browser and reading page content

    This opens the public URL in the browser and:
    1. Checks for auto-redirect to internal note
    2. Searches page content for simplenote:// links
    3. Tries to navigate to Simplenote app to search for the note

    Args:
        public_url: Public Simplenote URL
        cdp_url: Chrome DevTools Protocol URL
        debug: Enable debug output

    Returns:
        Internal note UUID or None
    """
    async with SimplenoteWriter(
        note_url=public_url,
        headless=False,
        debug=False,
        cdp_url=cdp_url
    ) as writer:
        # Navigate to public URL
        await writer.page.goto(public_url)
        await asyncio.sleep(2)  # Wait for potential redirect

        # Check if we're now on an internal note URL
        current_url = writer.page.url

        # Pattern: https://app.simplenote.com/n/76502186-4d7d-48d6-a961-80a48573b2c7
        # or https://app.simplenote.com/note/76502186-4d7d-48d6-a961-80a48573b2c7
        pattern = r'/(?:n|note)/([0-9a-fA-F-]{36})'
        match = re.search(pattern, current_url)

        if match:
            return match.group(1)

        # Method 2a: Try to read page content for simplenote:// link
        # (The link might be visible in the DOM even if filtered from HTML source)
        try:
            page_content = await writer.page.content()
            simplenote_pattern = r'simplenote://note/([0-9a-fA-F-]{36})'
            match = re.search(simplenote_pattern, page_content)
            if match:
                return match.group(1)
        except:
            pass

        # Method 2b: Try to find the note by searching its content in Simplenote app
        try:
            # Extract note content from the public page
            note_content_element = await writer.page.query_selector('.note-detail-markdown, .note-content, .published-note-content')

            if note_content_element:
                # Get the text content (first few words for searching)
                full_content = await note_content_element.text_content()
                # Use first 20-30 characters for search (enough to be unique)
                search_text = full_content.strip()[:30].strip()

                if debug:
                    print(f"\n   🔍 Searching by content: '{search_text}'")

                if search_text:
                    # Navigate to main Simplenote app
                    if debug:
                        print(f"   🌐 Navigating to Simplenote app...")
                    await writer.page.goto('https://app.simplenote.com/')
                    await asyncio.sleep(2)

                    # Search for the note using content
                    search_selectors = [
                        'input[placeholder*="Search"]',
                        'input[type="search"]',
                        '.search-field',
                        'input.search-bar',
                        '[aria-label*="Search"]'
                    ]

                    for selector in search_selectors:
                        try:
                            search_box = await writer.page.wait_for_selector(selector, timeout=3000)
                            if search_box:
                                if debug:
                                    print(f"   ⌨️  Found search box: {selector}")
                                # Click and type the search text
                                await search_box.click()
                                await asyncio.sleep(0.5)
                                await search_box.fill(search_text)
                                if debug:
                                    print(f"   ⏳ Waiting for search results...")
                                await asyncio.sleep(1.5)  # Wait for search results

                                # Try to click the first matching note
                                first_note_selectors = [
                                    '.note-list-item:first-child',
                                    '.note-list .note:first-child',
                                    '[role="button"].note:first-child',
                                    'article:first-child',
                                    '.note-preview:first-child'
                                ]

                                for note_selector in first_note_selectors:
                                    try:
                                        first_note = await writer.page.wait_for_selector(note_selector, timeout=2000)
                                        if first_note:
                                            if debug:
                                                print(f"   🖱️  Clicking first result: {note_selector}")
                                            await first_note.click()
                                            await asyncio.sleep(2)  # Wait for note to open in SPA

                                            # Note is now open in editor - extract UUID from the open note
                                            # Check if URL changed to internal note (might not in SPA)
                                            current_url = writer.page.url
                                            if debug:
                                                print(f"   📍 Current URL: {current_url}")
                                            match = re.search(pattern, current_url)
                                            if match:
                                                if debug:
                                                    print(f"   ✅ Found UUID in URL!")
                                                return match.group(1)

                                            # SPA mode: Note is open, extract UUID from editor content
                                            if debug:
                                                print(f"   🔍 URL didn't change (SPA mode), reading note content...")

                                            # Method 1: Read the note content for simplenote:// link
                                            try:
                                                # The note is already open in the editor
                                                editor = await writer.page.wait_for_selector('div.note-editor, .note-content-editor', timeout=2000)
                                                if editor:
                                                    editor_content = await editor.text_content()

                                                    # Search for simplenote:// link in the content
                                                    simplenote_pattern = r'simplenote://note/([0-9a-fA-F-]{36})'
                                                    match = re.search(simplenote_pattern, editor_content)
                                                    if match:
                                                        uuid_candidate = match.group(1)
                                                        if debug:
                                                            print(f"   ✅ Found UUID in note content: {uuid_candidate}")
                                                        return uuid_candidate
                                                    else:
                                                        if debug:
                                                            print(f"   ⚠️  No simplenote:// link found in note content")
                                            except Exception as e:
                                                if debug:
                                                    print(f"   ⚠️  Failed to read editor content: {e}")

                                            # Method 2: Try to click "Copy Internal Link" button
                                            if debug:
                                                print(f"   📋 Looking for 'Copy Internal Link' button...")
                                            try:
                                                copy_link_selectors = [
                                                    'button:has-text("Copy Internal Link")',
                                                    'button.button-borderless:has-text("Copy")',
                                                    '[aria-label*="Copy Internal Link"]',
                                                    'button:has-text("Internal Link")'
                                                ]

                                                for copy_selector in copy_link_selectors:
                                                    try:
                                                        copy_button = await writer.page.wait_for_selector(copy_selector, timeout=1000)
                                                        if copy_button:
                                                            if debug:
                                                                print(f"   📋 Found 'Copy Internal Link' button: {copy_selector}")
                                                            await copy_button.click()
                                                            await asyncio.sleep(0.5)

                                                            # Read from clipboard
                                                            try:
                                                                import pyperclip
                                                                clipboard_content = pyperclip.paste()
                                                                if debug:
                                                                    print(f"   📋 Clipboard: {clipboard_content}")

                                                                # Extract UUID from clipboard
                                                                simplenote_pattern = r'simplenote://note/([0-9a-fA-F-]{36})'
                                                                match = re.search(simplenote_pattern, clipboard_content)
                                                                if match:
                                                                    if debug:
                                                                        print(f"   ✅ Extracted UUID from clipboard!")
                                                                    return match.group(1)
                                                            except Exception as e:
                                                                if debug:
                                                                    print(f"   ⚠️  Clipboard read failed: {e}")
                                                    except:
                                                        continue
                                            except Exception as e:
                                                if debug:
                                                    print(f"   ⚠️  Copy button not found: {e}")

                                            # If we got here, note opened but couldn't extract UUID
                                            if debug:
                                                print(f"   ⚠️  Note opened but UUID extraction failed")
                                                print(f"   💡 Tip: Add simplenote://note/<uuid> link to your note content")
                                            break
                                    except Exception as e:
                                        if debug:
                                            print(f"   ⚠️  Selector {note_selector} failed: {e}")
                                        continue

                                # If we got here, found search box but couldn't extract UUID
                                break
                        except Exception as e:
                            if debug:
                                print(f"   ⚠️  Search selector {selector} failed: {e}")
                            continue
            else:
                if debug:
                    print(f"   ⚠️  Could not find note content element on public page")
        except Exception as e:
            if debug:
                print(f"   ⚠️  Browser search failed: {e}")

        return None


async def _write_to_public_note(
    public_url: str,
    content: str,
    mode: str,
    cdp_url: str,
    init_session: bool = False,
    ai_assistant: str = 'claude',
    issue_number: Optional[int] = None,
    debug: bool = True
) -> bool:
    """
    Write to a public note by opening it and writing directly

    This matches the session start pattern:
    1. Navigate to Simplenote app
    2. Search for note by content
    3. Click note to open it
    4. If init_session: Write metadata directly to the open note
    5. Write user content directly to the open note
    6. Save session data with search key

    Args:
        public_url: Public Simplenote URL (e.g., https://app.simplenote.com/p/0ZqWsQ)
        content: Content to write
        mode: 'append' or 'replace'
        cdp_url: Chrome DevTools Protocol URL
        init_session: Add session metadata to note
        ai_assistant: AI assistant name if init_session=True
        issue_number: GitHub issue number if init_session=True
        debug: Enable debug output

    Returns:
        True if successful
    """
    try:
        async with SimplenoteWriter(
            note_url=public_url,
            headless=False,
            debug=False,
            cdp_url=cdp_url
        ) as writer:
            # Step 1: Navigate to public URL to get note content for searching
            if debug:
                print(f"🌐 Loading public note to extract search text...")
            await writer.page.goto(public_url)
            await asyncio.sleep(2)

            # Extract note content from the public page
            note_content_element = await writer.page.query_selector('.note-detail-markdown, .note-content, .published-note-content')

            if not note_content_element:
                print("❌ Could not find note content on public page")
                return False

            # Get the text content (first few words for searching)
            full_content = await note_content_element.text_content()
            # Use first 30 characters for search (enough to be unique)
            search_text = full_content.strip()[:30].strip()

            if not search_text:
                print("❌ Public note appears to be empty")
                return False

            if debug:
                print(f"🔍 Search text: '{search_text}'")

            # Step 2: Navigate to main Simplenote app
            if debug:
                print(f"🌐 Navigating to Simplenote app...")
            await writer.page.goto('https://app.simplenote.com/')
            await asyncio.sleep(2)

            # Step 3: Search for the note using content
            search_selectors = [
                'input[placeholder*="Search"]',
                'input[type="search"]',
                '.search-field',
                'input.search-bar',
                '[aria-label*="Search"]'
            ]

            search_box = None
            for selector in search_selectors:
                try:
                    search_box = await writer.page.wait_for_selector(selector, timeout=3000)
                    if search_box:
                        if debug:
                            print(f"✅ Found search box: {selector}")
                        break
                except:
                    continue

            if not search_box:
                print("❌ Could not find search box in Simplenote")
                return False

            # Click and type the search text
            await search_box.click()
            await asyncio.sleep(0.5)
            await search_box.fill(search_text)
            if debug:
                print(f"⏳ Waiting for search results...")
            await asyncio.sleep(1.5)

            # Step 4: Click the first matching note
            first_note_selectors = [
                '.note-list-item:first-child',
                '.note-list .note:first-child',
                '[role="button"].note:first-child',
                'article:first-child',
                '.note-preview:first-child'
            ]

            note_opened = False
            for note_selector in first_note_selectors:
                try:
                    first_note = await writer.page.wait_for_selector(note_selector, timeout=2000)
                    if first_note:
                        if debug:
                            print(f"✅ Clicking note: {note_selector}")
                        await first_note.click()
                        await asyncio.sleep(2)  # Wait for note to open
                        note_opened = True
                        break
                except:
                    continue

            if not note_opened:
                print("❌ Could not find or click note in search results")
                return False

            if debug:
                print(f"✅ Note opened in editor")

            # Step 5: Extract note UUID by clicking "Copy Internal Link" button
            note_uuid = None
            if init_session or debug:
                if debug:
                    print(f"📋 Extracting note UUID from 'Copy Internal Link'...")

                # First, try to open the note actions menu/panel if it exists
                menu_selectors = [
                    # SVG-based ellipsis icon (three dots menu)
                    'button:has(.icon-ellipsis-outline)',
                    '.icon-ellipsis-outline',
                    'svg.icon-ellipsis-outline',
                    'button .icon-ellipsis-outline',

                    # Other potential menu buttons
                    'button.note-toolbar-button',
                    'button[aria-label*="More"]',
                    'button:has-text("...")',
                    '.note-toolbar .icon-ellipsis',
                    'button.icon-more',
                    '.note-actions-toggle',
                    'button.note-menu-toggle'
                ]

                for menu_selector in menu_selectors:
                    try:
                        menu_button = await writer.page.wait_for_selector(menu_selector, timeout=1000)
                        if menu_button:
                            if debug:
                                print(f"   🔍 Found potential menu button: {menu_selector}")
                            await menu_button.click()
                            # Wait 2 seconds for menu to open and render
                            await asyncio.sleep(2)
                            break
                    except:
                        continue

                # Now try to find and click the Copy Internal Link button
                # Based on note-actions-panel structure: <label class="note-actions-item">
                copy_link_selectors = [
                    # Specific structure-based selectors (highest priority)
                    'label.note-actions-item:has-text("Copy Internal Link")',
                    '.note-actions-item:has-text("Copy Internal Link")',
                    'label.note-actions-item:has-text("Internal Link")',
                    '.note-actions-name:has-text("Copy Internal Link")',

                    # Generic text-based selectors (fallback)
                    'label:has-text("Copy Internal Link")',
                    '*:has-text("Copy Internal Link")',
                    'button:has-text("Copy Internal Link")',
                    'a:has-text("Copy Internal Link")',

                    # Partial text matches
                    'label:has-text("Internal Link")',
                    'button:has-text("Internal Link")',
                    '*:has-text("Internal Link")',

                    # Aria labels (least likely)
                    '[aria-label*="Copy Internal Link"]',
                    '[aria-label*="Internal Link"]'
                ]

                copy_button_found = False
                for copy_selector in copy_link_selectors:
                    try:
                        copy_button = await writer.page.wait_for_selector(copy_selector, timeout=2000)
                        if copy_button:
                            if debug:
                                print(f"   ✅ Found 'Copy Internal Link' button: {copy_selector}")
                            await copy_button.click()
                            # Wait 2 seconds for clipboard to update
                            await asyncio.sleep(2)

                            # Read from clipboard
                            try:
                                import pyperclip
                                clipboard_content = pyperclip.paste()
                                if debug:
                                    print(f"   📋 Clipboard: {clipboard_content}")

                                # Extract UUID from clipboard (simplenote://note/<uuid>)
                                simplenote_pattern = r'simplenote://note/([0-9a-fA-F-]{36})'
                                match = re.search(simplenote_pattern, clipboard_content)
                                if match:
                                    note_uuid = match.group(1)
                                    if debug:
                                        print(f"   ✅ Extracted note UUID: {note_uuid}")
                                    copy_button_found = True
                                    break
                                else:
                                    if debug:
                                        print(f"   ⚠️  No UUID found in clipboard content")
                            except Exception as e:
                                if debug:
                                    print(f"   ⚠️  Clipboard read failed: {e}")
                    except Exception as e:
                        if debug:
                            print(f"   🔍 Selector '{copy_selector}' not found")
                        continue

                if not note_uuid and not copy_button_found:
                    # Last resort: try to get all visible text elements and search for "Internal Link"
                    if debug:
                        print(f"   🔍 Searching for any elements containing 'Internal Link'...")
                    try:
                        # Get page content to debug
                        all_buttons = await writer.page.query_selector_all('button, a, label, span')
                        for btn in all_buttons[:50]:  # Check first 50 elements
                            try:
                                text = await btn.text_content()
                                if text and 'internal' in text.lower() and 'link' in text.lower():
                                    if debug:
                                        print(f"   📍 Found element with text: '{text.strip()}'")
                                    await btn.click()
                                    # Wait 2 seconds for clipboard to update
                                    await asyncio.sleep(2)

                                    # Try clipboard
                                    import pyperclip
                                    clipboard_content = pyperclip.paste()
                                    simplenote_pattern = r'simplenote://note/([0-9a-fA-F-]{36})'
                                    match = re.search(simplenote_pattern, clipboard_content)
                                    if match:
                                        note_uuid = match.group(1)
                                        if debug:
                                            print(f"   ✅ Extracted note UUID: {note_uuid}")
                                        break
                            except:
                                continue
                    except:
                        pass

                if not note_uuid:
                    if debug:
                        print(f"   ⚠️  Could not extract note UUID, will generate session UUID instead")

            # Step 6: Write session metadata if requested (like session start)
            if init_session:
                from .session_manager import generate_html_metadata

                # Use note UUID as session_id if available, otherwise generate one
                if note_uuid:
                    session_id = note_uuid
                    if debug:
                        print(f"🔮 Using note UUID as session ID: {session_id}")
                else:
                    import uuid as uuid_module
                    session_id = str(uuid_module.uuid4())
                    if debug:
                        print(f"🔮 Generating new session ID: {session_id}")

                # Generate metadata
                metadata = generate_html_metadata(
                    session_id=session_id,
                    ai_assistant=ai_assistant,
                    issue_number=issue_number
                )

                # Find the editor element
                editor = await writer.page.wait_for_selector('div.note-editor, .note-content-editor', timeout=5000)
                await editor.click()
                await asyncio.sleep(0.5)

                # Go to beginning
                await writer.page.keyboard.press('Control+Home')
                await asyncio.sleep(0.3)

                # Type metadata
                if debug:
                    print(f"📝 Writing session metadata...")
                await writer.page.keyboard.type(metadata, delay=0)
                await asyncio.sleep(1)

                # Save session data (using note UUID and search key)
                from .session_manager import SessionState
                session_state = SessionState()
                session_data = {
                    'session_id': session_id,
                    'note_uuid': note_uuid,  # Store the actual note UUID
                    'search_key': search_text,  # Use search text to find note later
                    'public_url': public_url,  # Store public URL for reference
                    'ai_assistant': ai_assistant,
                    'issue_number': issue_number,
                    'cdp_endpoint': cdp_url,
                    'created_at': datetime.now().isoformat()
                }
                session_state.save_session(session_data)
                if debug:
                    print(f"💾 Session saved to .simexp/session.json")

            # Step 6: Write user content
            editor = await writer.page.wait_for_selector('div.note-editor, .note-content-editor', timeout=5000)
            await editor.click()
            await asyncio.sleep(0.5)

            if mode == 'replace':
                # Clear all content
                if debug:
                    print(f"🗑️  Replacing all content...")
                await writer.page.keyboard.press('Control+A')
                await writer.page.keyboard.press('Backspace')
                await asyncio.sleep(0.3)
            else:
                # Append mode - go to end
                if debug:
                    print(f"📝 Appending content...")
                await writer.page.keyboard.press('Control+End')
                await asyncio.sleep(0.3)
                # Add spacing
                await writer.page.keyboard.type('\n\n', delay=0)

            # Type the content
            await writer.page.keyboard.type(content, delay=0)
            await asyncio.sleep(2)  # Wait for autosave

            if debug:
                print(f"✅ Content written ({len(content)} chars)")
                print(f"✅ Write successful!")

            return True

    except Exception as e:
        print(f"❌ Error writing to public note: {e}")
        import traceback
        traceback.print_exc()
        return False


async def _add_session_metadata_to_note(note_url: str, uuid: str, cdp_url: str, ai_assistant: str = 'claude', issue_number: Optional[int] = None) -> None:
    """
    Add session metadata to an existing note (like session start does)

    Args:
        note_url: Internal Simplenote note URL
        uuid: Note UUID
        cdp_url: Chrome DevTools Protocol URL
        ai_assistant: AI assistant name
        issue_number: GitHub issue number
    """
    from .session_manager import generate_html_metadata

    # Generate session ID
    import uuid as uuid_module
    session_id = str(uuid_module.uuid4())

    # Generate metadata
    metadata = generate_html_metadata(
        session_id=session_id,
        ai_assistant=ai_assistant,
        issue_number=issue_number
    )

    # Write metadata to the beginning of the note
    async with SimplenoteWriter(
        note_url=note_url,
        headless=False,
        debug=False,
        cdp_url=cdp_url
    ) as writer:
        await writer.page.goto(note_url)
        await asyncio.sleep(1.5)

        # Click into editor
        editor = await writer.page.wait_for_selector('div.note-editor', timeout=5000)
        await editor.click()
        await asyncio.sleep(0.5)

        # Go to beginning
        await writer.page.keyboard.press('Control+Home')
        await asyncio.sleep(0.3)

        # Type metadata
        await writer.page.keyboard.type(metadata, delay=10)

        # Wait for autosave
        await asyncio.sleep(2)

    # Store session info in session.json
    from .session_manager import SessionState
    session_state = SessionState()
    session_data = {
        'session_id': session_id,
        'search_key': session_id,
        'ai_assistant': ai_assistant,
        'issue_number': issue_number,
        'created_at': datetime.now().isoformat(),
        'note_uuid': uuid,
        'note_url': note_url
    }
    session_state.save_session(session_data)


def store_session_uuid(uuid: str) -> None:
    """
    Store resolved UUID in session.json for reuse

    Args:
        uuid: Internal note UUID to store
    """
    session_state = SessionState()
    session_data = session_state.load_session() or {}

    # Add or update session_uuid field
    session_data['session_uuid'] = uuid
    session_data['session_uuid_updated_at'] = datetime.now().isoformat()

    session_state.save_session(session_data)
    print(f"   🧠 Stored UUID in session.json")


def get_session_uuid() -> Optional[str]:
    """
    Get stored UUID from session.json

    Returns:
        Stored UUID or None if not found
    """
    session_state = SessionState()
    session_data = session_state.load_session()

    if session_data and 'session_uuid' in session_data:
        return session_data['session_uuid']

    return None


# ═══════════════════════════════════════════════════════════════
# CDP URL RESOLUTION - Issue #11
# ♠️ Nyro: Three-tier priority chain for multi-network support
# ═══════════════════════════════════════════════════════════════

def get_cdp_url(override: str = None) -> str:
    """
    Get CDP (Chrome DevTools Protocol) URL using priority chain

    Priority order:
    1. override parameter (highest - explicit function call)
    2. SIMEXP_CDP_URL environment variable (session-specific)
    3. CDP_URL from ~/.simexp/simexp.yaml (persistent user config)
    4. http://localhost:9222 (fallback default)

    Args:
        override: Explicit CDP URL (e.g., from --cdp-url flag)

    Returns:
        CDP URL string

    Examples:
        # Command-line override (highest priority)
        get_cdp_url('http://192.168.1.100:9222')

        # Environment variable
        export SIMEXP_CDP_URL=http://10.0.0.5:9222
        get_cdp_url()  # → http://10.0.0.5:9222

        # Config file
        # ~/.simexp/simexp.yaml contains: CDP_URL: http://server:9222
        get_cdp_url()  # → http://server:9222

        # Fallback
        get_cdp_url()  # → http://localhost:9222
    """
    # Priority 1: Explicit override parameter
    if override:
        return override

    # Priority 2: Environment variable
    env_cdp = os.environ.get('SIMEXP_CDP_URL')
    if env_cdp:
        return env_cdp

    # Priority 3: Config file
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = yaml.safe_load(f)
                if config and 'CDP_URL' in config:
                    return config['CDP_URL']
        except Exception:
            pass  # Fall through to default

    # Priority 4: Default localhost (Chrome DevTools Protocol standard port)
    return 'http://localhost:9222'


# ═══════════════════════════════════════════════════════════════
# NETWORK IP DETECTION - Issue #36
# 🧵 Synth: Network-wide CDP access coordination
# ═══════════════════════════════════════════════════════════════

def get_local_ip():
    """
    Detect local network IP address for network-wide CDP access

    Returns:
        str: Local IP address (e.g., '192.168.1.100'), or None if not detected

    🧵 Synth: Enables cross-device Assembly coordination
    """
    import socket
    try:
        # Create a socket to external DNS to determine local IP
        # This doesn't actually send data, just determines routing
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            # Google DNS as routing target
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
        finally:
            s.close()
        return local_ip
    except Exception:
        return None


def get_network_cdp_url(port=9222):
    """
    Generate network-accessible CDP URL using local IP

    Args:
        port: CDP port number (default: 9222)

    Returns:
        str: Network CDP URL (e.g., 'http://192.168.1.100:9222'), or None if IP not detected

    🧵 Synth: For cross-device browser automation coordination
    """
    local_ip = get_local_ip()
    if local_ip:
        return f'http://{local_ip}:{port}'
    return None


# ═══════════════════════════════════════════════════════════════
# CHROME CDP HELPER FUNCTIONS - Issue #17
# ♠️🌿🎸🧵 G.Music Assembly - Auto-launch Chrome for init
# ═══════════════════════════════════════════════════════════════

def find_chrome_executable():
    """
    Find Chrome/Chromium executable on the system

    Returns:
        str: Chrome command name, or None if not found
    """
    candidates = ['google-chrome', 'chromium', 'chromium-browser', 'chrome']
    for cmd in candidates:
        if shutil.which(cmd):
            return cmd
    return None


def check_chrome_cdp_running(port=9222):
    """
    Check if Chrome CDP is running on specified port

    Args:
        port: CDP port number (default: 9222)

    Returns:
        bool: True if Chrome CDP is accessible, False otherwise
    """
    try:
        response = requests.get(f'http://localhost:{port}/json/version', timeout=2)
        return response.status_code == 200
    except:
        return False


def launch_chrome_cdp(port=9222, bind_address='0.0.0.0'):
    """
    Launch Chrome with CDP enabled

    Args:
        port: CDP port number (default: 9222)
        bind_address: Network interface to bind (default: '0.0.0.0' for network-wide access)
                     Use '127.0.0.1' for localhost-only (more secure)

    Returns:
        bool: True if Chrome launched successfully, False otherwise

    🧵 Synth Enhancement (Issue #36): Network-wide CDP access for cross-device coordination
    """
    chrome_cmd = find_chrome_executable()
    if not chrome_cmd:
        return False

    try:
        launch_args = [
            chrome_cmd,
            f'--remote-debugging-port={port}',
            f'--remote-debugging-address={bind_address}',
            '--user-data-dir=' + os.path.expanduser('~/.chrome-simexp')
        ]

        subprocess.Popen(launch_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Wait for Chrome to start
        time.sleep(3)
        return check_chrome_cdp_running(port)
    except Exception:
        return False


def init_config():
    """
    Initialize SimExp configuration interactively
    Creates ~/.simexp/simexp.yaml with user settings
    """
    # Create config directory if it doesn't exist
    config_dir = os.path.dirname(CONFIG_FILE)
    os.makedirs(config_dir, exist_ok=True)

    print("♠️🌿🎸🧵 SimExp Configuration Setup")
    print()

    config = {
        'BASE_PATH': input("Enter the base path for saving content: "),
        'SOURCES': []
    }

    # Source URLs configuration
    print("\n📚 Source URLs (optional):")
    while True:
        url = input("Enter source URL (or 'done' to finish): ")
        if url.lower() == 'done':
            break
        filename = input("Enter filename for this source: ")
        config['SOURCES'].append({'url': url, 'filename': filename})

    # CDP URL configuration (Issue #11)
    print("\n🌐 Chrome DevTools Protocol (CDP) Configuration:")
    print("   CDP URL allows SimExp to connect to your authenticated Chrome browser.")
    print("   Leave empty to use default (localhost:9222)")
    print()
    print("   Examples:")
    print("   - localhost:9222 (default, for single-user setup)")
    print("   - http://192.168.1.100:9222 (connect to server on local network)")
    print("   - http://10.0.0.5:9222 (connect to remote server)")
    print()

    cdp_input = input("CDP URL [default: http://localhost:9222]: ").strip()
    if cdp_input:
        config['CDP_URL'] = cdp_input
        print(f"   ✓ CDP URL set to: {cdp_input}")
    else:
        print(f"   ✓ Using default: http://localhost:9222")

    with open(CONFIG_FILE, 'w') as config_file:
        yaml.safe_dump(config, config_file)
    print(f"\n✅ Configuration saved to {CONFIG_FILE}")

    # ═══════════════════════════════════════════════════════════════
    # AUTO-LAUNCH CHROME CDP - Issue #17
    # ♠️🌿🎸🧵 G.Music Assembly - One-command setup
    # ═══════════════════════════════════════════════════════════════

    # Check if Chrome CDP is running
    if not check_chrome_cdp_running():
        print("\n🚀 Chrome CDP Setup")
        print("   SimExp needs Chrome running with remote debugging.")
        launch = input("   Launch Chrome automatically? [Y/n]: ").strip().lower()

        if launch != 'n':
            chrome_cmd = find_chrome_executable()
            if chrome_cmd:
                print(f"   🔍 Found Chrome: {chrome_cmd}")
                if launch_chrome_cdp():
                    print("   ✓ Chrome launched with CDP on port 9222")
                else:
                    print("   ⚠️  Could not launch Chrome automatically")
                    print("\n   Run manually:")
                    print(f"   {chrome_cmd} --remote-debugging-port=9222 --user-data-dir=~/.chrome-simexp &")
            else:
                print("   ⚠️  Could not find Chrome/Chromium on your system")
                print("\n   Install Chrome and run:")
                print("   google-chrome --remote-debugging-port=9222 --user-data-dir=~/.chrome-simexp &")
        else:
            print("\n   Run this command to start Chrome with CDP:")
            chrome_cmd = find_chrome_executable() or 'google-chrome'
            print(f"   {chrome_cmd} --remote-debugging-port=9222 --user-data-dir=~/.chrome-simexp &")
    else:
        print("\n✓ Chrome CDP is already running on port 9222")

    # Show login instructions
    print("\n📝 IMPORTANT - Complete Setup:")
    print("   1. A Chrome window has opened (or is already open)")
    print("   2. Go to: https://app.simplenote.com")
    print("   3. Login with your Simplenote account")
    print("   4. Keep this Chrome window open while using SimExp")
    print()
    print("💡 Ready to test? Run: simexp session start")


def write_command(note_url, content=None, mode='append', headless=False, cdp_url=None, init_session=False, ai_assistant='claude', issue_number=None):
    """
    Write content to Simplenote note via Playwright

    Supports automatic resolution of public Simplenote URLs (/p/<uuid>) to
    internal note UUIDs for writing to existing notes.

    Args:
        note_url: Simplenote note URL (supports both /n/ and /p/ URLs)
        content: Content to write (if None, read from stdin)
        mode: 'append' or 'replace'
        headless: Run browser in headless mode
        cdp_url: Chrome DevTools Protocol URL (uses priority chain if None)
        init_session: Add session metadata to resolved note (like session start)
        ai_assistant: AI assistant name if init_session=True
        issue_number: GitHub issue number if init_session=True
    """
    import sys

    # Resolve CDP URL using priority chain (Issue #11)
    resolved_cdp = get_cdp_url(cdp_url)

    # ═══════════════════════════════════════════════════════════════
    # PUBLIC URL RESOLUTION - Write directly to opened note
    # ♠️🌿🎸🧵 G.Music Assembly - Bridge public to private
    # ═══════════════════════════════════════════════════════════════

    # Detect public Simplenote URL pattern (/p/<uuid>)
    if '/p/' in note_url:
        print(f"♠️🌿🎸🧵 SimExp Public URL Resolution & Write")
        print()

        # Read from stdin if no content provided
        if content is None:
            print("📝 Reading content from stdin (Ctrl+D to finish)...")
            content = sys.stdin.read()
            if not content.strip():
                print("❌ No content provided")
                return

        # Write directly to the note using browser navigation
        success = asyncio.run(_write_to_public_note(
            public_url=note_url,
            content=content,
            mode=mode,
            cdp_url=resolved_cdp,
            init_session=init_session,
            ai_assistant=ai_assistant,
            issue_number=issue_number
        ))

        if not success:
            print("\n❌ Failed to write to note")
        return

    # Read from stdin if no content provided
    if content is None:
        print("📝 Reading content from stdin (Ctrl+D to finish)...")
        content = sys.stdin.read()
        if not content.strip():
            print("❌ No content provided")
            return

    print(f"♠️🌿🎸🧵 SimExp Write Mode - {mode.upper()}")
    print(f"🌐 Target: {note_url}")
    print(f"📄 Content length: {len(content)} chars")

    # Execute async write
    result = asyncio.run(write_to_note(
        note_url=note_url,
        content=content,
        mode=mode,
        headless=headless,
        debug=True,
        cdp_url=resolved_cdp
    ))

    if result['success']:
        print(f"\n✅ Write successful!")
        print(f"📊 Written: {result['content_length']} characters")
        print(f"📝 Preview: {result['preview']}")
    else:
        print(f"\n❌ Write failed - verification mismatch")


def read_command(note_url, headless=True):
    """
    Read content from Simplenote note via Playwright

    Args:
        note_url: Simplenote note URL
        headless: Run browser in headless mode
    """
    print(f"♠️🌿🎸🧵 SimExp Read Mode")
    print(f"🌐 Source: {note_url}")

    # Execute async read
    content = asyncio.run(read_from_note(
        note_url=note_url,
        headless=headless,
        debug=True
    ))

    print(f"\n📖 Content ({len(content)} chars):")
    print("=" * 60)
    print(content)
    print("=" * 60)

    return content


# ═══════════════════════════════════════════════════════════════
# SESSION COMMAND SUITE
# ♠️🌿🎸🧵 G.Music Assembly - Session-Aware Notes
# ═══════════════════════════════════════════════════════════════

def session_start_command(ai_assistant='claude', issue_number=None, cdp_url=None):
    """
    Start a new session and create a Simplenote note for it

    Args:
        ai_assistant: AI assistant name (claude or gemini)
        issue_number: GitHub issue number being worked on
        cdp_url: Chrome DevTools Protocol URL (uses priority chain if None)
    """
    # Resolve CDP URL using priority chain (Issue #11)
    resolved_cdp = get_cdp_url(cdp_url)

    current_dir = os.getcwd()
    session_dir = os.path.join(current_dir, '.simexp')

    print(f"♠️🌿🎸🧵 Starting New Session")
    print(f"📁 Session directory: {session_dir}/")
    print()

    session_data = asyncio.run(create_session_note(
        ai_assistant=ai_assistant,
        issue_number=issue_number,
        cdp_url=resolved_cdp
    ))

    print(f"\n✅ Session started successfully!")
    print(f"📁 Session file: {session_dir}/session.json")
    print(f"🔮 Session ID: {session_data['session_id']}")
    print(f"🔑 Search Key: {session_data['search_key']}")
    print()
    print(f"💡 This session is active for: {current_dir}")
    print(f"💡 Tip: Use 'simexp session write' to add content to your session note")


def session_add_command(file_path: str, heading: Optional[str] = None, cdp_url: Optional[str] = None):
    """
    Add file content to the current session's note using clipboard for efficiency
    
    Args:
        file_path: Path to the file to add
        heading: Optional heading to add before the file content
        cdp_url: Chrome DevTools Protocol URL (uses priority chain if None)
    """
    import sys
    from pathlib import Path
    from .session_file_handler import SessionFileHandler

    # Resolve CDP URL using priority chain (Issue #11)
    resolved_cdp = get_cdp_url(cdp_url)

    # Get active session
    session = get_active_session()
    if not session:
        print("❌ No active session. Run 'simexp session start' first.")
        sys.exit(1)

    # Check file exists
    file_path = Path(file_path).resolve()
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    print(f"♠️🌿🎸🧵 Adding File to Session Note")
    print(f"🔮 Session: {session['session_id']}")
    print(f"📄 File: {file_path.name}")

    # Read and format file content
    handler = SessionFileHandler()
    try:
        content = handler.read_file(str(file_path))
        formatted_content = handler.format_content(str(file_path), content, heading)
        print(f"📋 File content formatted ({len(formatted_content)} chars)")
    except Exception as e:
        print(f"❌ Error preparing file content: {e}")
        sys.exit(1)

    # Use the existing session_write_command to append content
    session_write_command(formatted_content, cdp_url=resolved_cdp)

def session_write_command(content=None, cdp_url=None, date_flag=None, prepend=False):
    """
    Write to the current session's note using search

    Args:
        content: Content to write (if None, read from stdin)
        cdp_url: Chrome DevTools Protocol URL (uses priority chain if None)
        date_flag: Timestamp granularity ('y', 'm', 'd', 'h', 's', 'ms') or manual timestamp
        prepend: Whether to insert at beginning (after metadata) instead of appending
    """
    import sys

    # Resolve CDP URL using priority chain (Issue #11)
    resolved_cdp = get_cdp_url(cdp_url)

    # Get active session
    session = get_active_session()
    if not session:
        print("❌ No active session. Run 'simexp session start' first.")
        sys.exit(1)

    # Read from stdin if no content provided
    if content is None:
        print("📝 Reading content from stdin (Ctrl+D to finish)...")
        content = sys.stdin.read()
        if not content.strip():
            print("❌ No content provided")
            return

    # Format content with timestamp if requested
    if date_flag:
        content = format_timestamped_entry(content, date_flag, prepend)
        print(f"⏰ Timestamp added: {date_flag if isinstance(date_flag, str) else 'default'}")

    print(f"♠️🌿🎸🧵 Writing to Session Note")
    print(f"🔮 Session: {session['session_id']}")
    print(f"📄 Content length: {len(content)} chars")
    if prepend:
        print(f"📌 Mode: PREPEND (after metadata)")

    # Execute search and write
    async def write_to_session():
        async with SimplenoteWriter(
            note_url='https://app.simplenote.com/',
            headless=False,
            debug=True,
            cdp_url=resolved_cdp
        ) as writer:
            # Navigate to Simplenote
            await writer.page.goto('https://app.simplenote.com/')
            await writer.page.wait_for_load_state('networkidle')

            # Search for and select the session note
            found = await search_and_select_note(
                session['session_id'],
                writer.page,
                debug=True
            )

            if not found:
                print("❌ Could not find session note. Note may have been deleted.")
                return False

            # Write content to the note (it's already selected)
            editor = await writer.page.wait_for_selector('div.note-editor', timeout=5000)
            await editor.click()
            await asyncio.sleep(0.5)

            if prepend:
                # Insert at beginning (after metadata if present)
                # Try to find metadata div using Playwright selector
                try:
                    metadata_div = writer.page.locator('div.simexp-session-metadata')
                    # Check if metadata div exists
                    if await metadata_div.count() > 0:
                        # Use JavaScript to insert text after the metadata div
                        await metadata_div.evaluate(
                            f'''(el) => {{
                                const entry = "\\n\\n{content}";
                                // Find the next text node or create one
                                if (el.nextSibling) {{
                                    if (el.nextSibling.nodeType === Node.TEXT_NODE) {{
                                        el.nextSibling.textContent = entry + el.nextSibling.textContent;
                                    }} else {{
                                        const textNode = document.createTextNode(entry);
                                        el.parentNode.insertBefore(textNode, el.nextSibling);
                                    }}
                                }} else {{
                                    const textNode = document.createTextNode(entry);
                                    el.parentNode.appendChild(textNode);
                                }}
                            }}'''
                        )
                        print(f"📌 Inserted after metadata div using selector")
                    else:
                        # No metadata div found, use fallback: go to beginning
                        await writer.page.keyboard.press('Control+Home')
                        await asyncio.sleep(0.2)
                        await writer.page.keyboard.type(f"{content}\n\n", delay=10)
                        print(f"📌 No metadata found, inserted at beginning")
                except Exception as e:
                    print(f"⚠️ Selector method failed: {e}, using fallback")
                    # Fallback to beginning if selector fails
                    await writer.page.keyboard.press('Control+Home')
                    await asyncio.sleep(0.2)
                    await writer.page.keyboard.type(f"{content}\n\n", delay=10)

            else:
                # Go to end and append
                await writer.page.keyboard.press('Control+End')
                await asyncio.sleep(0.3)
                await writer.page.keyboard.type(f"\n\n{content}", delay=10)  # Slow typing for reliability

            # Wait longer for Simplenote autosave (critical!)
            print(f"⏳ Waiting for Simplenote to autosave...")
            await asyncio.sleep(3)  # Increased from 1 to 3 seconds

            print(f"✅ Write successful!")
            return True

    success = asyncio.run(write_to_session())
    if not success:
        print(f"\n❌ Write failed")


def session_read_command(cdp_url=None):
    """
    Read content from the current session's note using search

    Args:
        cdp_url: Chrome DevTools Protocol URL (uses priority chain if None)
    """
    import sys

    # Resolve CDP URL using priority chain (Issue #11)
    resolved_cdp = get_cdp_url(cdp_url)

    # Get active session
    session = get_active_session()
    if not session:
        print("❌ No active session. Run 'simexp session start' first.")
        sys.exit(1)

    print(f"♠️🌿🎸🧵 Reading Session Note")
    print(f"🔮 Session: {session['session_id']}")

    # Execute search and read
    async def read_from_session():
        async with SimplenoteWriter(
            note_url='https://app.simplenote.com/',
            headless=False,
            debug=True,
            cdp_url=resolved_cdp
        ) as writer:
            # Navigate to Simplenote
            await writer.page.goto('https://app.simplenote.com/')
            await writer.page.wait_for_load_state('networkidle')

            # Search for and select the session note
            found = await search_and_select_note(
                session['session_id'],
                writer.page,
                debug=True
            )

            if not found:
                print("❌ Could not find session note. Note may have been deleted.")
                return None

            # Read content from the note
            editor = await writer.page.wait_for_selector('div.note-editor', timeout=5000)
            content = await editor.text_content()
            return content

    content = asyncio.run(read_from_session())

    if content:
        print(f"\n📖 Session Content ({len(content)} chars):")
        print("=" * 60)
        print(content)
        print("=" * 60)
    else:
        print(f"\n❌ Could not read session note")


def session_open_command(cdp_url=None):
    """
    Open session note in browser using Playwright automation

    Args:
        cdp_url: Chrome DevTools Protocol URL (uses priority chain if None)
    """
    import sys

    # Resolve CDP URL using priority chain (Issue #11)
    resolved_cdp = get_cdp_url(cdp_url)

    # Get active session
    session = get_active_session()
    if not session:
        print("❌ No active session. Run 'simexp session start' first.")
        sys.exit(1)

    print(f"♠️🌿🎸🧵 Opening Session Note in Browser")
    print(f"🔮 Session: {session['session_id']}")

    # Execute search and open
    async def open_session_note():
        async with SimplenoteWriter(
            note_url='https://app.simplenote.com/',
            headless=False,
            debug=True,
            cdp_url=resolved_cdp
        ) as writer:
            # Navigate to Simplenote
            await writer.page.goto('https://app.simplenote.com/')
            await writer.page.wait_for_load_state('networkidle')

            # Search for and select the session note
            found = await search_and_select_note(
                session['session_id'],
                writer.page,
                debug=True
            )

            if not found:
                print("❌ Could not find session note. Note may have been deleted.")
                return False

            print(f"✅ Session note opened in browser!")
            print(f"💡 Browser will stay open for you to view/edit the note")

            # Keep the browser open by waiting (user can Ctrl+C to close)
            print(f"\n🎯 Press Ctrl+C when done viewing/editing...")
            try:
                await asyncio.sleep(300)  # Wait 5 minutes or until Ctrl+C
            except KeyboardInterrupt:
                print(f"\n👋 Closing browser connection...")

            return True

    success = asyncio.run(open_session_note())
    if success:
        print(f"✅ Done!")
    else:
        print(f"❌ Failed to open session note")


def session_url_command():
    """Print the session search key"""
    import sys

    # Get active session
    session = get_active_session()
    if not session:
        print("❌ No active session. Run 'simexp session start' first.")
        sys.exit(1)

    print(f"🔑 Session search key: {session['search_key']}")
    print(f"💡 Use this in Simplenote search to find your session note")


def session_clear_command():
    """Clear the current session"""
    clear_active_session()
    print("✅ Session cleared")


def session_title_command(title, cdp_url=None):
    """Set a title for the current session note"""
    from .session_manager import set_session_title

    # Resolve CDP URL using priority chain (Issue #11)
    resolved_cdp = get_cdp_url(cdp_url)

    success = asyncio.run(set_session_title(title, cdp_url=resolved_cdp))

    if not success:
        print(f"\n❌ Failed to set session title")


def session_list_command():
    """List all sessions across directory tree"""
    from .session_manager import list_all_sessions

    sessions = list_all_sessions()

    if not sessions:
        print("❌ No sessions found")
        print("💡 Run 'simexp session start' to create a new session")
        return

    print(f"♠️🌿🎸🧵 SimExp Sessions")
    print()

    for session in sessions:
        session_dir = session.get('_session_dir', 'Unknown')
        is_active = session.get('_is_active', False)

        print(f"📁 {session_dir}/session.json")
        print(f"   🔮 Session: {session['session_id'][:16]}...")
        print(f"   🤝 AI: {session.get('ai_assistant', 'unknown')}")
        if session.get('issue_number'):
            print(f"   🎯 Issue: #{session['issue_number']}")
        print(f"   📅 Created: {session.get('created_at', 'unknown')}")
        if is_active:
            print(f"   ⭐ ACTIVE (current directory)")
        print()

    print(f"💡 {len(sessions)} session(s) found")
    print(f"💡 Session lookup: current dir → parent dirs → home dir")


def session_info_command():
    """Show detailed info about current session and directory context"""
    import sys
    from .session_manager import get_session_directory

    session = get_active_session()
    if not session:
        print("❌ No active session")
        print("💡 Run 'simexp session start' to create a new session")
        print()
        print("📁 Sessions are directory-based:")
        print("   SimExp looks for .simexp/session.json in:")
        print("   1. Current directory")
        print("   2. Parent directories (walking up)")
        print("   3. Home directory")
        sys.exit(1)

    session_dir = session.get('_session_dir', get_session_directory())
    current_dir = os.getcwd()

    print(f"♠️🌿🎸🧵 Current Session Info")
    print()
    print(f"📁 Session Directory: {session_dir}/")
    print(f"🔮 Session ID: {session['session_id']}")
    print(f"🔑 Search Key: {session.get('search_key', session['session_id'])}")
    print(f"🤝 AI Assistant: {session.get('ai_assistant', 'unknown')}")
    if session.get('issue_number'):
        print(f"🎯 Issue: #{session['issue_number']}")
    print(f"📅 Created: {session.get('created_at', 'unknown')}")
    print()
    print(f"📍 Current Directory: {current_dir}")
    print()
    print(f"💡 This session is active because you are in:")
    if session_dir:
        parent_dir = os.path.dirname(session_dir)
        print(f"   {parent_dir}")
    print()
    print(f"💡 To see all sessions: simexp session list")


def session_publish_command(cdp_url=None):
    """Publish the current session's note"""
    import sys

    # Resolve CDP URL using priority chain (Issue #11)
    resolved_cdp = get_cdp_url(cdp_url)

    session = get_active_session()
    if not session:
        print("❌ No active session. Run 'simexp session start' first.")
        sys.exit(1)

    print(f"♠️🌿🎸🧵 Publishing Session Note")
    print(f"🔮 Session: {session['session_id']}")

    public_url = asyncio.run(publish_session_note(cdp_url=resolved_cdp))

    if public_url:
        # Copy to clipboard
        try:
            pyperclip.copy(public_url)
            clipboard_status = "📋 Copied to clipboard!"
        except Exception as e:
            clipboard_status = f"⚠️  Could not copy to clipboard: {e}"

        print(f"\n✅ Note published successfully!")
        print(f"🌐 Public URL: {public_url}")
        print(f"{clipboard_status}")
    else:
        print(f"\n⚠️  Publish completed but could not extract URL")
        print(f"💡 Check Simplenote UI for the public URL")


def session_collab_add_command(email, cdp_url=None):
    """Add a collaborator to the current session's note"""
    import sys

    # Resolve CDP URL using priority chain (Issue #11)
    resolved_cdp = get_cdp_url(cdp_url)

    session = get_active_session()
    if not session:
        print("❌ No active session. Run 'simexp session start' first.")
        sys.exit(1)

    print(f"♠️🌿🎸🧵 Adding Collaborator to Session Note")
    print(f"🔮 Session: {session['session_id']}")
    print(f"👤 Collaborator: {email}")

    success = asyncio.run(add_session_collaborator(email, cdp_url=resolved_cdp))

    if success:
        print(f"\n✅ Collaborator added successfully!")
    else:
        print(f"\n❌ Failed to add collaborator")


def session_collab_list_command(cdp_url=None):
    """List all collaborators on the current session's note"""
    import sys

    # Resolve CDP URL using priority chain (Issue #11)
    resolved_cdp = get_cdp_url(cdp_url)

    session = get_active_session()
    if not session:
        print("❌ No active session. Run 'simexp session start' first.")
        sys.exit(1)

    print(f"♠️🌿🎸🧵 Listing Collaborators on Session Note")
    print(f"🔮 Session: {session['session_id']}")

    collaborators = asyncio.run(list_session_collaborators(cdp_url=resolved_cdp))

    if collaborators:
        print(f"\n✅ Found {len(collaborators)} collaborator(s):")
        for email in collaborators:
            print(f"   👤 {email}")
    else:
        print(f"\n📭 No collaborators found")


def session_share_command(identifier, cdp_url=None):
    """
    Share session note using glyph/alias/group/email

    Examples:
        simexp session share ♠️              - Share with Nyro
        simexp session share nyro            - Share with Nyro (alias)
        simexp session share assembly        - Share with all Assembly members
        simexp session share user@email.com  - Share with custom email
    """
    import sys

    # Resolve CDP URL using priority chain (Issue #11)
    resolved_cdp = get_cdp_url(cdp_url)

    session = get_active_session()
    if not session:
        print("❌ No active session. Run 'simexp session start' first.")
        sys.exit(1)

    print(f"♠️🌿🎸🧵 Sharing Session Note via Glyph Resolution")
    print(f"🔮 Session: {session['session_id']}")
    print(f"🔑 Identifier: {identifier}")

    result = asyncio.run(share_session_note(identifier, cdp_url=resolved_cdp, debug=True))

    # Result dict already prints summary in share_session_note()
    # Just handle exit code based on success
    if not result['success']:
        sys.exit(1)


def run_extraction():
    """
    Original extraction workflow - fetches content from clipboard/config sources
    This is the legacy feature of simexp
    """
    print("♠️🌿🎸🧵 SimExp Extraction Mode")
    print()

    # Update sources from clipboard
    update_sources_from_clipboard()

    # Load configuration from YAML file
    config_path = CONFIG_FILE
    if not os.path.exists(config_path):
        print(f"❌ Configuration file '{config_path}' not found.")
        print(f"💡 Please run 'simexp init' to create it.")
        return

    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)

    # Check if clipboard content is valid
    if not is_clipboard_content_valid():
        print("📋 No valid URL in clipboard. Using sources from configuration.")
        sources = config.get('SOURCES', [])
    else:
        print("📋 Valid URL found in clipboard! Using clipboard sources.")
        sources = config.get('CLIPBOARD_SOURCES', [])

    if not sources:
        print("❌ No sources configured.")
        print("💡 Run 'simexp init' and add source URLs to your configuration.")
        return

    base_path = config['BASE_PATH']

    # Create a folder for the current date
    current_date = datetime.now().strftime('%Y%m%d')
    daily_folder = os.path.join(base_path, current_date)
    os.makedirs(daily_folder, exist_ok=True)

    print(f"📁 Output: {daily_folder}/")
    print()
    print(f"📚 Fetching {len(sources)} source(s)...")
    print()

    # Track statistics
    success_count = 0
    fail_count = 0

    # Fetch, process, and save content for each source
    for i, source in enumerate(sources, 1):
        url = source['url']
        filename = source['filename']

        # Determine emoji based on filename
        emoji_map = {
            'aureon': '🌿',
            'nyro': '♠️',
            'jamai': '🎸',
            'synth': '🧵'
        }
        emoji = emoji_map.get(filename.lower(), '📄')

        print(f"{emoji} {filename.title()}")
        print(f"   🌐 {url}")
        print(f"   ⬇️  Fetching...", end=" ", flush=True)

        raw_content = fetch_content(url)

        if raw_content is None:
            print("❌")
            print(f"   ⚠️  Failed to fetch content")
            print()
            fail_count += 1
            continue

        print("✓")

        # Process content
        title, cleaned_content = process_content(raw_content)
        content_length = len(cleaned_content)
        print(f"   📄 {content_length:,} characters extracted")

        # Save to markdown
        success, result = save_as_markdown(title, cleaned_content, base_path, daily_folder, filename)

        if success:
            print(f"   💾 Saved: {result}")
            success_count += 1
        else:
            print(f"   ❌ Save failed: {result}")
            fail_count += 1

        print()

    # Summary
    print("=" * 60)
    if fail_count == 0:
        print(f"✅ Extraction complete! {success_count} source(s) archived.")
    else:
        print(f"⚠️  Extraction finished with errors:")
        print(f"   ✓ Success: {success_count}")
        print(f"   ✗ Failed: {fail_count}")
    print("=" * 60)


# ═══════════════════════════════════════════════════════════════
# BROWSER/CDP TESTING COMMANDS - Issue #36 Enhancement
# 🧵 Synth: Quick CDP testing without full init
# ═══════════════════════════════════════════════════════════════

def browser_test_command():
    """
    Test Chrome CDP connection and show network binding status

    🧵 Synth: Quick testing command for developers
    """
    import subprocess

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  🧵 Chrome CDP Connection Test                               ║")
    print("║  ♠️🌿🎸🧵 G.Music Assembly                                    ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    # 1. Check CDP URL configuration
    cdp_url = get_cdp_url()
    print(f"📡 CDP URL Configuration:")
    print(f"   {cdp_url}")
    print()

    # 2. Detect network IP
    local_ip = get_local_ip()
    if local_ip:
        network_url = get_network_cdp_url()
        print(f"🌐 Network IP Detected:")
        print(f"   {local_ip}")
        print(f"   Network CDP URL: {network_url}")
    else:
        print(f"⚠️  Could not detect network IP")
    print()

    # 3. Check if Chrome is running
    print("🔍 Chrome CDP Status:")
    if check_chrome_cdp_running():
        print("   ✅ Chrome CDP is RUNNING on port 9222")
        print()

        # 4. Check network binding
        print("🔌 Network Binding Check:")
        try:
            result = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True)
            netstat_output = result.stdout

            if '0.0.0.0:9222' in netstat_output:
                print("   ✅ Bound to: 0.0.0.0 (NETWORK-WIDE ACCESS)")
                print("   📱 Accessible from all devices on WiFi")
            elif '127.0.0.1:9222' in netstat_output:
                print("   ✅ Bound to: 127.0.0.1 (LOCALHOST-ONLY)")
                print("   🔒 Secure mode - only this machine can access")
            else:
                print("   ⚠️  Could not determine binding (port 9222 not found in netstat)")
        except Exception as e:
            print(f"   ⚠️  Could not run netstat: {e}")
        print()

        # 5. Test connection
        print("🧪 Connection Test:")
        try:
            response = requests.get(f'{cdp_url}/json/version', timeout=3)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Connection SUCCESSFUL")
                print(f"   Browser: {data.get('Browser', 'Unknown')}")
                print(f"   User-Agent: {data.get('User-Agent', 'Unknown')[:60]}...")

                # Test network access if we have network IP
                if local_ip and '127.0.0.1' not in cdp_url:
                    print()
                    print("🌐 Network Access Test:")
                    network_test_url = f'http://{local_ip}:9222/json/version'
                    try:
                        network_response = requests.get(network_test_url, timeout=2)
                        if network_response.status_code == 200:
                            print(f"   ✅ Network access WORKING")
                            print(f"   📱 You can access from other devices: {network_test_url}")
                        else:
                            print(f"   ❌ Network access failed (status: {network_response.status_code})")
                    except Exception as ne:
                        print(f"   ❌ Network access BLOCKED: {ne}")
                        print(f"   💡 Chrome might be bound to localhost only")
            else:
                print(f"   ❌ Connection failed (status: {response.status_code})")
        except Exception as e:
            print(f"   ❌ Connection FAILED: {e}")
            print(f"   💡 Chrome CDP might not be running or accessible")
    else:
        print("   ❌ Chrome CDP is NOT running")
        print()
        print("💡 To start Chrome with CDP:")
        print(f"   Localhost-only (secure):")
        print(f"   google-chrome --remote-debugging-port=9222 --remote-debugging-address=127.0.0.1 --user-data-dir=~/.chrome-simexp &")
        print()
        print(f"   Network-wide (WiFi access):")
        print(f"   google-chrome --remote-debugging-port=9222 --remote-debugging-address=0.0.0.0 --user-data-dir=~/.chrome-simexp &")
        print()
        print(f"   Or use: simexp browser launch [--network]")

    print()
    print("=" * 62)


def browser_launch_command(port=9222, bind_address='127.0.0.1'):
    """
    Launch Chrome with CDP enabled

    Args:
        port: CDP port (default: 9222)
        bind_address: Network binding ('0.0.0.0' for network, '127.0.0.1' for localhost)

    🧵 Synth: Convenient Chrome launcher with network options
    """
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  🚀 Chrome CDP Launch                                        ║")
    print("║  ♠️🌿🎸🧵 G.Music Assembly                                    ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    # Check if Chrome is already running
    if check_chrome_cdp_running(port):
        print(f"⚠️  Chrome CDP is already running on port {port}")
        print()
        print("   To restart with different binding:")
        print(f"   1. Stop Chrome: pkill chrome")
        print(f"   2. Rerun: simexp browser launch [--network]")
        return

    # Show what we're about to do
    mode = "NETWORK-WIDE ACCESS" if bind_address == '0.0.0.0' else "LOCALHOST-ONLY"
    security = "⚠️  Accessible from WiFi devices" if bind_address == '0.0.0.0' else "🔒 Secure - only this machine"

    print(f"📡 Launching Chrome CDP:")
    print(f"   Port: {port}")
    print(f"   Bind Address: {bind_address}")
    print(f"   Mode: {mode}")
    print(f"   {security}")
    print()

    # Find Chrome
    chrome_cmd = find_chrome_executable()
    if not chrome_cmd:
        print("❌ Could not find Chrome/Chromium on your system")
        print()
        print("   Install Chrome and try again")
        return

    print(f"🔍 Found: {chrome_cmd}")
    print()

    # Launch Chrome
    print("🚀 Launching...")
    if launch_chrome_cdp(port=port, bind_address=bind_address):
        print("✅ Chrome launched successfully!")
        print()

        # Show CDP URL
        cdp_url = f'http://localhost:{port}'
        print(f"📡 CDP URL: {cdp_url}")

        # Show network URL if network binding
        if bind_address == '0.0.0.0':
            local_ip = get_local_ip()
            if local_ip:
                network_url = f'http://{local_ip}:{port}'
                print(f"🌐 Network URL: {network_url}")
                print()
                print(f"📱 Access from other devices:")
                print(f"   export SIMEXP_CDP_URL={network_url}")
                print(f"   simexp session start --ai claude --issue XX")

        print()
        print("✅ Chrome is ready for SimExp!")
        print()
        print("Next steps:")
        print("  1. Go to https://app.simplenote.com in the Chrome window")
        print("  2. Login to Simplenote")
        print("  3. Run: simexp browser test")
    else:
        print("❌ Failed to launch Chrome")
        print()
        print("   Try manually:")
        print(f"   {chrome_cmd} --remote-debugging-port={port} --remote-debugging-address={bind_address} --user-data-dir=~/.chrome-simexp &")


def main():
    """
    Main CLI entry point - parses arguments FIRST, then dispatches to appropriate command
    This fixes Issue #9 - CLI commands now work without requiring valid config/clipboard
    """
    import sys

    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'init':
            init_config()

        elif command == 'write':
            import argparse
            parser = argparse.ArgumentParser(
                description='Write content to a Simplenote note. Automatically resolves public URLs (/p/<uuid>) to internal UUIDs.',
                prog='simexp write')
            parser.add_argument('note_url', help='The URL of the Simplenote note. Supports public URLs (https://app.simplenote.com/p/<uuid>) and internal URLs (https://app.simplenote.com/n/<uuid>).')
            parser.add_argument('content', nargs='?', default=None, help='The content to write. If not provided, reads from stdin.')
            parser.add_argument('--mode', choices=['append', 'replace'], default='append', help='Write mode.')
            parser.add_argument('--headless', action='store_true', help='Run in headless mode.')
            parser.add_argument('--cdp-url', default=None, help='Chrome DevTools Protocol URL to connect to an existing browser.')
            parser.add_argument('--init-session', action='store_true', help='Initialize session metadata in resolved note (adds YAML header like session start).')
            parser.add_argument('--ai', default='claude', choices=['claude', 'gemini'], help='AI assistant name (used with --init-session).')
            parser.add_argument('--issue', type=int, default=None, help='GitHub issue number (used with --init-session).')

            args = parser.parse_args(sys.argv[2:])

            write_command(
                args.note_url,
                args.content,
                mode=args.mode,
                headless=args.headless,
                cdp_url=args.cdp_url,
                init_session=args.init_session,
                ai_assistant=args.ai,
                issue_number=args.issue
            )

        elif command == 'read':
            # Usage: simexp read <note_url>
            if len(sys.argv) < 3:
                print("Usage: simexp read <note_url>")
                sys.exit(1)

            note_url = sys.argv[2]
            read_command(note_url, headless=True)

        elif command == 'session':
            # Session command suite
            if len(sys.argv) < 3:
                print("♠️🌿🎸🧵 SimExp Session Management")
                print("\nUsage: simexp session <subcommand>")
                print("\nSession Management:")
                print("  start [--ai <assistant>] [--issue <number>]  - Start new session")
                print("  list                                         - List all sessions (directory tree)")
                print("  info                                         - Show current session & directory context")
                print("  clear                                        - Clear active session")
                print("\nSession Content:")
                print("  write <message>                              - Write to session note")
                print("  read                                         - Read session note")
                print("  add <file> [--heading <text>]                - Add file to session note")
                print("  title <title>                                - Set session note title")
                print("  open                                         - Open session note in browser")
                print("  url                                          - Print session note URL")
                print("\nCollaboration & Sharing (Issue #6):")
                print("  collab <glyph|alias|group>                   - Share with Assembly (♠, 🌿, 🎸, 🧵, assembly)")
                print("  collab add <email>                           - Add collaborator by email")
                print("  collab list                                  - List all collaborators")
                print("  publish                                      - Publish note (get public URL)")
                print("\nExamples:")
                print("  simexp session start --ai claude --issue 42  # Start new session")
                print("  simexp session write 'Progress update'       # Write to session")
                print("  simexp session collab ♠                      # Share with Nyro")
                print("  simexp session collab assembly               # Share with all Assembly")
                print("  simexp session publish                       # Get public URL")
                sys.exit(1)

            subcommand = sys.argv[2]

            # Handle --help and -h explicitly
            if subcommand in ('--help', '-h', 'help'):
                print("♠️🌿🎸🧵 SimExp Session Management")
                print("\nUsage: simexp session <subcommand>")
                print("\nSession Management:")
                print("  start [--ai <assistant>] [--issue <number>]  - Start new session")
                print("  list                                         - List all sessions (directory tree)")
                print("  info                                         - Show current session & directory context")
                print("  clear                                        - Clear active session")
                print("\nSession Content:")
                print("  write <message>                              - Write to session note")
                print("  read                                         - Read session note")
                print("  add <file> [--heading <text>]                - Add file to session note")
                print("  title <title>                                - Set session note title")
                print("  open                                         - Open session note in browser")
                print("  url                                          - Print session note URL")
                print("\nCollaboration & Sharing (Issue #6):")
                print("  collab <glyph|alias|group>                   - Share with Assembly (♠, 🌿, 🎸, 🧵, assembly)")
                print("  collab add <email>                           - Add collaborator by email")
                print("  collab list                                  - List all collaborators")
                print("  publish                                      - Publish note (get public URL)")
                print("\nExamples:")
                print("  simexp session start --ai claude --issue 42  # Start new session")
                print("  simexp session write 'Progress update'       # Write to session")
                print("  simexp session collab ♠                      # Share with Nyro")
                print("  simexp session collab assembly               # Share with all Assembly")
                print("  simexp session publish                       # Get public URL")
                sys.exit(0)

            if subcommand == 'start':
                import argparse
                parser = argparse.ArgumentParser(
                    description='Start a new session',
                    prog='simexp session start')
                parser.add_argument('--ai', default='claude', choices=['claude', 'gemini'], help='AI assistant name')
                parser.add_argument('--issue', type=int, help='GitHub issue number')
                parser.add_argument('--cdp-url', default=None, help='Chrome DevTools Protocol URL')

                args = parser.parse_args(sys.argv[3:])
                session_start_command(ai_assistant=args.ai, issue_number=args.issue, cdp_url=args.cdp_url)

            elif subcommand == 'write':
                import argparse
                parser = argparse.ArgumentParser(
                    description='Write to session note',
                    prog='simexp session write')
                parser.add_argument('content', nargs='?', help='Content to write (optional, reads from stdin if not provided)')
                parser.add_argument('--cdp-url', default=None, help='Chrome DevTools Protocol URL')
                parser.add_argument('--date', nargs='?', const=True, default=None,
                                    help='Add timestamp prefix. Optional granularity: y, m, d, h, s (default), ms. Or provide manual timestamp.')
                parser.add_argument('--prepend', action='store_true',
                                    help='Insert at beginning (after metadata) instead of appending')

                args = parser.parse_args(sys.argv[3:])
                session_write_command(content=args.content, cdp_url=args.cdp_url,
                                      date_flag=args.date, prepend=args.prepend)

            elif subcommand == 'read':
                import argparse
                parser = argparse.ArgumentParser(
                    description='Read session note',
                    prog='simexp session read')
                parser.add_argument('--cdp-url', default=None, help='Chrome DevTools Protocol URL')

                args = parser.parse_args(sys.argv[3:])
                session_read_command(cdp_url=args.cdp_url)

            elif subcommand == 'open':
                import argparse
                parser = argparse.ArgumentParser(
                    description='Open session note in browser',
                    prog='simexp session open')
                parser.add_argument('--cdp-url', default=None, help='Chrome DevTools Protocol URL')

                args = parser.parse_args(sys.argv[3:])
                session_open_command(cdp_url=args.cdp_url)

            elif subcommand == 'url':
                session_url_command()

            elif subcommand == 'clear':
                session_clear_command()

            elif subcommand == 'title':
                import argparse
                parser = argparse.ArgumentParser(
                    description='Set a title for the session note',
                    prog='simexp session title')
                parser.add_argument('title', help='Title for the session note')
                parser.add_argument('--cdp-url', default=None, help='Chrome DevTools Protocol URL')

                args = parser.parse_args(sys.argv[3:])
                session_title_command(args.title, cdp_url=args.cdp_url)

            elif subcommand == 'list':
                session_list_command()

            elif subcommand == 'info':
                session_info_command()

            elif subcommand == 'add':
                import argparse
                parser = argparse.ArgumentParser(
                    description='Add file content to session note',
                    prog='simexp session add')
                parser.add_argument('file', help='Path to the file to add')
                parser.add_argument('--heading', help='Optional heading to add before the file content')
                parser.add_argument('--cdp-url', default=None, help='Chrome DevTools Protocol URL')

                args = parser.parse_args(sys.argv[3:])
                session_add_command(args.file, heading=args.heading, cdp_url=args.cdp_url)

            elif subcommand == 'publish':
                import argparse
                parser = argparse.ArgumentParser(
                    description='Publish session note',
                    prog='simexp session publish')
                parser.add_argument('--cdp-url', default=None, help='Chrome DevTools Protocol URL')

                args = parser.parse_args(sys.argv[3:])
                session_publish_command(cdp_url=args.cdp_url)

            elif subcommand == 'collab':
                # Collaborator management subcommands
                if len(sys.argv) < 4:
                    print("♠️🌿🎸🧵 SimExp Collaboration Management")
                    print("\nUsage: simexp session collab <subcommand|glyph|alias|group>")
                    print("\nShare with Assembly Members:")
                    print("  <glyph|alias|group>    - Share using glyph (♠, 🌿, 🎸, 🧵), alias, or 'assembly'")
                    print("\nManage Collaborators:")
                    print("  add <email>            - Add collaborator by email")
                    print("  list                   - List all collaborators")
                    print("\nExamples:")
                    print("  simexp session collab ♠                      # Share with Nyro (glyph)")
                    print("  simexp session collab nyro                   # Share with Nyro (alias)")
                    print("  simexp session collab assembly               # Share with all Assembly")
                    print("  simexp session collab add jerry@example.com  # Add collaborator")
                    print("  simexp session collab list                   # List collaborators")
                    sys.exit(1)

                collab_action = sys.argv[3]

                # Handle --help and -h explicitly
                if collab_action in ('--help', '-h', 'help'):
                    print("♠️🌿🎸🧵 SimExp Collaboration Management")
                    print("\nUsage: simexp session collab <subcommand|glyph|alias|group>")
                    print("\nShare with Assembly Members:")
                    print("  <glyph|alias|group>    - Share using glyph (♠, 🌿, 🎸, 🧵), alias, or 'assembly'")
                    print("\nManage Collaborators:")
                    print("  add <email>            - Add collaborator by email")
                    print("  list                   - List all collaborators")
                    print("\nExamples:")
                    print("  simexp session collab ♠                      # Share with Nyro (glyph)")
                    print("  simexp session collab nyro                   # Share with Nyro (alias)")
                    print("  simexp session collab assembly               # Share with all Assembly")
                    print("  simexp session collab add jerry@example.com  # Add collaborator")
                    print("  simexp session collab list                   # List collaborators")
                    sys.exit(0)

                if collab_action == 'add':
                    import argparse
                    parser = argparse.ArgumentParser(
                        description='Add collaborator',
                        prog='simexp session collab add')
                    parser.add_argument('email', help='Collaborator email address')
                    parser.add_argument('--cdp-url', default=None, help='Chrome DevTools Protocol URL')

                    args = parser.parse_args(sys.argv[4:])
                    session_collab_add_command(args.email, cdp_url=args.cdp_url)

                elif collab_action == 'list':
                    import argparse
                    parser = argparse.ArgumentParser(
                        description='List collaborators',
                        prog='simexp session collab list')
                    parser.add_argument('--cdp-url', default=None, help='Chrome DevTools Protocol URL')

                    args = parser.parse_args(sys.argv[4:])
                    session_collab_list_command(cdp_url=args.cdp_url)

                else:
                    # Not a known subcommand - treat as glyph/alias/group sharing
                    import argparse
                    parser = argparse.ArgumentParser(
                        description='Share session note with collaborator(s) using glyph/alias/group',
                        prog='simexp session collab')
                    parser.add_argument('identifier', help='Glyph (♠, 🌿, 🎸, 🧵), alias (nyro, aureon, jamai, synth), group (assembly), or email')
                    parser.add_argument('--cdp-url', default=None, help='Chrome DevTools Protocol URL')

                    # Re-parse with the identifier
                    args = parser.parse_args(sys.argv[3:])
                    session_share_command(args.identifier, cdp_url=args.cdp_url)

            elif subcommand == 'share':
                import argparse
                parser = argparse.ArgumentParser(
                    description='Share session note with collaborator(s) using glyph/alias/group/email',
                    prog='simexp session share')
                parser.add_argument('identifier', help='Glyph (♠️), alias (nyro), group (assembly), or email address')
                parser.add_argument('--cdp-url', default=None, help='Chrome DevTools Protocol URL')

                args = parser.parse_args(sys.argv[3:])
                session_share_command(args.identifier, cdp_url=args.cdp_url)

            else:
                print(f"Unknown session subcommand: {subcommand}")
                print("Run 'simexp session' for usage information")
                sys.exit(1)

        elif command == 'browser':
            # Browser/CDP testing command suite (Issue #36 enhancement)
            if len(sys.argv) < 3:
                print("♠️🌿🎸🧵 SimExp Browser/CDP Management")
                print("\nUsage: simexp browser <subcommand>")
                print("\nBrowser/CDP Commands (Issue #36):")
                print("  test                    - Test Chrome CDP connection and network binding")
                print("  launch                  - Launch Chrome with CDP (localhost-only, secure)")
                print("  launch --network        - Launch Chrome with network-wide access (WiFi)")
                print("\nExamples:")
                print("  simexp browser test                           # Test CDP connection")
                print("  simexp browser launch                         # Launch Chrome (localhost)")
                print("  simexp browser launch --network               # Launch Chrome (network-wide)")
                print("  simexp browser launch --network --port 9223   # Custom port")
                print("\nNetwork-wide access allows SimExp to connect from other devices on WiFi.")
                print("Use 'simexp browser test' to verify your configuration.")
                sys.exit(1)

            subcommand = sys.argv[2]

            # Handle --help and -h explicitly
            if subcommand in ('--help', '-h', 'help'):
                print("♠️🌿🎸🧵 SimExp Browser/CDP Management")
                print("\nUsage: simexp browser <subcommand>")
                print("\nBrowser/CDP Commands (Issue #36):")
                print("  test                    - Test Chrome CDP connection and network binding")
                print("  launch                  - Launch Chrome with CDP (localhost-only, secure)")
                print("  launch --network        - Launch Chrome with network-wide access (WiFi)")
                print("\nExamples:")
                print("  simexp browser test                           # Test CDP connection")
                print("  simexp browser launch                         # Launch Chrome (localhost)")
                print("  simexp browser launch --network               # Launch Chrome (network-wide)")
                print("  simexp browser launch --network --port 9223   # Custom port")
                print("\nNetwork-wide access allows SimExp to connect from other devices on WiFi.")
                print("Use 'simexp browser test' to verify your configuration.")
                sys.exit(0)

            if subcommand == 'test':
                browser_test_command()

            elif subcommand == 'launch':
                import argparse
                parser = argparse.ArgumentParser(
                    description='Launch Chrome with CDP',
                    prog='simexp browser launch')
                parser.add_argument('--network', action='store_true', help='Enable network-wide access (0.0.0.0)')
                parser.add_argument('--port', type=int, default=9222, help='CDP port (default: 9222)')

                args = parser.parse_args(sys.argv[3:])
                bind_address = '0.0.0.0' if args.network else '127.0.0.1'
                browser_launch_command(port=args.port, bind_address=bind_address)

            else:
                print(f"Unknown browser subcommand: {subcommand}")
                print("Run 'simexp browser' for usage information")
                sys.exit(1)

        elif command == 'help' or command == '--help' or command == '-h':
            print("♠️🌿🎸🧵 SimExp - Simplenote Web Content Extractor & Writer")
            print("\nCommands:")
            print("  simexp                       - Run extraction from clipboard/config")
            print("  simexp init                  - Initialize configuration")
            print("  simexp session <subcommand>  - Session management (use --help for details)")
            print("  simexp browser <subcommand>  - Browser/CDP testing & management (use --help for details)")
            print("  simexp help                  - Show this help")
            print("\nFor detailed help on any command, use:")
            print("  simexp session --help")
            print("  simexp browser --help")

        else:
            print(f"Unknown command: {command}")
            print("Run 'simexp help' for usage information")
            sys.exit(1)

    else:
        # No arguments - run normal extraction
        run_extraction()

if __name__ == "__main__":
    main()
