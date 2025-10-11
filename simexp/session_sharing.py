"""
SimExp Session Sharing & Publishing
Manages Simplenote note sharing and publishing features

♠️🌿🎸🧵 G.Music Assembly - Sharing Features (Issue #6)
"""

import re
import asyncio
from typing import Optional, List, Dict
from .playwright_writer import SimplenoteWriter
from .session_manager import get_active_session, search_and_select_note
from .collaborator_config import resolve_collaborator


def validate_email(email: str) -> bool:
    """
    Validate email format

    Args:
        email: Email address to validate

    Returns:
        True if valid email format, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


async def publish_note(
    session_id: str,
    page,
    debug: bool = True
) -> Optional[str]:
    """
    Publish a Simplenote note to make it publicly accessible

    This function:
    1. Assumes note is already selected/focused
    2. Looks for publish/share button
    3. Clicks to publish
    4. Extracts and returns public URL

    Args:
        session_id: Session UUID
        page: Playwright page object
        debug: Enable debug logging

    Returns:
        Public URL if successful, None if failed
    """
    try:
        if debug:
            print(f"🌐 Publishing note...")

        # Step 1: Find and click ellipsis menu (⋯)
        ellipsis_selectors = [
            'button[aria-label*="Actions"]',
            'button[aria-label*="More"]',
            'button[title*="Actions"]',
            'button[title*="More"]',
            'button:has-text("⋯")',
            'button:has-text("...")',
            '.icon-ellipsis',
            '.actions-button',
            '[data-testid="note-actions"]',
        ]

        ellipsis_button = None
        for selector in ellipsis_selectors:
            try:
                ellipsis_button = await page.wait_for_selector(selector, timeout=2000)
                if ellipsis_button:
                    if debug:
                        print(f"✅ Found ellipsis menu: {selector}")
                    await ellipsis_button.click()
                    await asyncio.sleep(1)
                    break
            except:
                continue

        if not ellipsis_button:
            print("❌ Could not find ellipsis menu (⋯)")
            return None

        # Wait for menu to fully render
        await asyncio.sleep(1.5)

        # Step 2: Check if already published, or publish the note
        # Structure: <input type="checkbox" id="note-actions-publish-checkbox" checked="">
        # If checked, note is already published

        is_published = False
        try:
            publish_checkbox = await page.wait_for_selector('#note-actions-publish-checkbox', timeout=3000)
            if publish_checkbox:
                is_checked = await publish_checkbox.is_checked()
                is_published = is_checked
                if debug:
                    if is_published:
                        print(f"✅ Note is already published")
                    else:
                        print(f"📝 Note not published yet, publishing...")
        except:
            if debug:
                print("⚠️  Could not find publish checkbox")

        # If not published, click the label to check the checkbox
        if not is_published:
            publish_selectors = [
                'label[for="note-actions-publish-checkbox"]',
                '#note-actions-publish-checkbox',
            ]

            publish_clicked = False
            for selector in publish_selectors:
                try:
                    publish_element = await page.wait_for_selector(selector, timeout=2000)
                    if publish_element:
                        if debug:
                            print(f"✅ Found publish element: {selector}")
                        await publish_element.click()
                        if debug:
                            print(f"⏳ Waiting for publish to complete...")
                        await asyncio.sleep(2.5)
                        publish_clicked = True
                        break
                except:
                    continue

            if not publish_clicked:
                print("❌ Could not click 'Publish' checkbox")
                return None

        # Look for "Copy Link" button within the public link panel
        # Structure: <div class="note-actions-panel note-actions-public-link">
        #              <button type="button" class="button button-borderless">Copy Link</button>
        copy_link_selectors = [
            '.note-actions-public-link button:has-text("Copy Link")',
            '.note-actions-public-link button.button-borderless',
            'button.button-borderless:has-text("Copy Link")',
            'button:has-text("Copy Link")',
        ]

        copy_link_button = None
        for selector in copy_link_selectors:
            try:
                copy_link_button = await page.wait_for_selector(selector, timeout=3000)
                if copy_link_button:
                    if debug:
                        print(f"✅ Found copy link button: {selector}")
                    # Click it to copy URL to clipboard
                    await copy_link_button.click()
                    if debug:
                        print(f"⏳ Waiting for clipboard copy...")
                    await asyncio.sleep(1.5)  # Wait for clipboard
                    break
            except:
                continue

        # Try to read URL from clipboard (Simplenote auto-copies it)
        # Simplenote uses simp.ly URL shortener, e.g., http://simp.ly/p/yJ5sNZ
        # We'll transform it to https://app.simplenote.com/p/yJ5sNZ
        public_url = None
        try:
            import pyperclip
            clipboard_content = pyperclip.paste()
            # Check for simp.ly OR simplenote.com URLs with /p/ pattern
            if clipboard_content and '/p/' in clipboard_content:
                url = clipboard_content.strip()

                # Transform simp.ly to full simplenote.com URL
                if 'simp.ly' in url:
                    # Extract note ID from simp.ly URL
                    # Example: http://simp.ly/p/yJ5sNZ -> yJ5sNZ
                    import re
                    match = re.search(r'/p/([a-zA-Z0-9]+)', url)
                    if match:
                        note_id = match.group(1)
                        public_url = f"https://app.simplenote.com/p/{note_id}"
                        if debug:
                            print(f"✅ Got public URL from clipboard: {public_url}")
                            print(f"   (Transformed from: {url})")
                elif 'simplenote.com' in url:
                    # Already in correct format
                    public_url = url
                    if debug:
                        print(f"✅ Got public URL from clipboard: {public_url}")
        except Exception as e:
            if debug:
                print(f"⚠️  Could not read clipboard: {e}")

        # Fallback: Try to extract from DOM
        if not public_url:
            url_selectors = [
                'input[readonly][value*="simplenote.com/p/"]',
                'input[value*="simplenote.com/p/"]',
                'a[href*="simplenote.com/p/"]',
                '.public-url',
                '[data-public-url]',
                'input[type="text"][value*="/p/"]'
            ]

            for selector in url_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=2000)
                    if element:
                        # Try to get URL from various attributes
                        url = await element.get_attribute('value')
                        if not url:
                            url = await element.get_attribute('href')
                        if not url:
                            url = await element.text_content()

                        if url and '/p/' in url:
                            public_url = url.strip()
                            if debug:
                                print(f"✅ Extracted public URL from DOM: {public_url}")
                            break
                except:
                    continue

        if not public_url:
            if debug:
                print("⚠️ Published, but could not extract URL automatically")
                print("💡 Check clipboard or Simplenote UI for the public URL")

        return public_url

    except Exception as e:
        print(f"❌ Error publishing note: {e}")
        return None


async def unpublish_note(
    session_id: str,
    page,
    debug: bool = True
) -> bool:
    """
    Unpublish a Simplenote note to make it private again

    Args:
        session_id: Session UUID
        page: Playwright page object
        debug: Enable debug logging

    Returns:
        True if successful, False otherwise
    """
    try:
        if debug:
            print(f"🔒 Unpublishing note...")

        # Common unpublish button selectors
        unpublish_selectors = [
            'button[aria-label*="Unpublish"]',
            'button[title*="Unpublish"]',
            'button:has-text("Unpublish")',
            'button:has-text("Make Private")',
            '[data-action="unpublish"]',
            '.unpublish-button',
        ]

        # Try to find and click unpublish button
        unpublish_button = None
        for selector in unpublish_selectors:
            try:
                unpublish_button = await page.wait_for_selector(selector, timeout=2000)
                if unpublish_button:
                    if debug:
                        print(f"✅ Found unpublish button: {selector}")
                    await unpublish_button.click()
                    await asyncio.sleep(1)
                    return True
            except:
                continue

        print("❌ Could not find unpublish button")
        print("💡 Note may not be published, or UI has changed")
        return False

    except Exception as e:
        print(f"❌ Error unpublishing note: {e}")
        return False


async def add_collaborator(
    session_id: str,
    email: str,
    page,
    debug: bool = True
) -> bool:
    """
    Add a collaborator to a Simplenote note

    Args:
        session_id: Session UUID
        email: Collaborator email address
        page: Playwright page object
        debug: Enable debug logging

    Returns:
        True if successful, False otherwise
    """
    try:
        # Validate email first
        if not validate_email(email):
            print(f"❌ Invalid email format: {email}")
            return False

        if debug:
            print(f"🤝 Adding collaborator: {email}")

        # Step 1: Find and click ellipsis menu (⋯) in top right
        ellipsis_selectors = [
            'button[aria-label*="Actions"]',
            'button[aria-label*="More"]',
            'button[title*="Actions"]',
            'button[title*="More"]',
            'button:has-text("⋯")',
            'button:has-text("...")',
            '.icon-ellipsis',
            '.actions-button',
            '[data-testid="note-actions"]',
        ]

        ellipsis_button = None
        for selector in ellipsis_selectors:
            try:
                ellipsis_button = await page.wait_for_selector(selector, timeout=2000)
                if ellipsis_button:
                    if debug:
                        print(f"✅ Found ellipsis menu: {selector}")
                    await ellipsis_button.click()
                    await asyncio.sleep(1)
                    break
            except:
                continue

        if not ellipsis_button:
            print("❌ Could not find ellipsis menu (⋯)")
            print("💡 Looking for: button with Actions/More or ⋯ symbol")
            return False

        # Step 2: Find and click "Collaborate" option in menu
        collaborate_selectors = [
            'button:has-text("Collaborate")',
            'a:has-text("Collaborate")',
            '[role="menuitem"]:has-text("Collaborate")',
            'li:has-text("Collaborate")',
            '.menu-item:has-text("Collaborate")',
        ]

        collaborate_option = None
        for selector in collaborate_selectors:
            try:
                collaborate_option = await page.wait_for_selector(selector, timeout=2000)
                if collaborate_option:
                    if debug:
                        print(f"✅ Found collaborate option: {selector}")
                    await collaborate_option.click()
                    await asyncio.sleep(1)
                    break
            except:
                continue

        if not collaborate_option:
            print("❌ Could not find 'Collaborate' option in menu")
            print("💡 Menu may have opened but 'Collaborate' not found")
            return False

        # Look for email input field
        email_selectors = [
            'input[type="email"]',
            'input[placeholder*="email"]',
            'input[placeholder*="Email"]',
            'input[name="email"]',
            '.collaborator-email',
            '[data-field="email"]',
        ]

        email_input = None
        for selector in email_selectors:
            try:
                email_input = await page.wait_for_selector(selector, timeout=2000)
                if email_input:
                    if debug:
                        print(f"✅ Found email input: {selector}")
                    break
            except:
                continue

        if not email_input:
            print("❌ Could not find email input field")
            return False

        # Type the email
        await email_input.click()
        await email_input.fill(email)
        await asyncio.sleep(0.5)

        if debug:
            print(f"✅ Entered email: {email}")

        # Look for add/confirm button
        add_selectors = [
            'button[type="submit"]',
            'button:has-text("Add")',
            'button:has-text("Invite")',
            'button:has-text("Share")',
            'button[aria-label*="Add"]',
            '.add-collaborator',
        ]

        add_button = None
        for selector in add_selectors:
            try:
                add_button = await page.wait_for_selector(selector, timeout=2000)
                if add_button:
                    if debug:
                        print(f"✅ Found add button: {selector}")
                    await add_button.click()
                    if debug:
                        print(f"⏳ Waiting for Simplenote autosave...")
                    await asyncio.sleep(3)  # Increased from 1 to 3 seconds for autosave
                    break
            except:
                continue

        if not add_button:
            # Try pressing Enter as fallback
            await page.keyboard.press('Enter')
            if debug:
                print(f"⏳ Waiting for Simplenote autosave...")
            await asyncio.sleep(3)  # Wait for autosave

        if debug:
            print(f"✅ Collaborator added: {email}")

        return True

    except Exception as e:
        print(f"❌ Error adding collaborator: {e}")
        return False


async def remove_collaborator(
    session_id: str,
    email: str,
    page,
    debug: bool = True
) -> bool:
    """
    Remove a collaborator from a Simplenote note

    Args:
        session_id: Session UUID
        email: Collaborator email address to remove
        page: Playwright page object
        debug: Enable debug logging

    Returns:
        True if successful, False otherwise
    """
    try:
        if debug:
            print(f"🚫 Removing collaborator: {email}")

        # This is highly UI-dependent
        # Common pattern: find collaborator in list, click remove button next to it

        # Try to find collaborator list item containing the email
        collaborator_selectors = [
            f'[data-email="{email}"]',
            f'*:has-text("{email}")',
        ]

        collaborator_element = None
        for selector in collaborator_selectors:
            try:
                collaborator_element = await page.wait_for_selector(selector, timeout=2000)
                if collaborator_element:
                    if debug:
                        print(f"✅ Found collaborator: {email}")
                    break
            except:
                continue

        if not collaborator_element:
            print(f"❌ Collaborator not found: {email}")
            return False

        # Look for remove button near the collaborator element
        remove_selectors = [
            'button[aria-label*="Remove"]',
            'button[title*="Remove"]',
            'button:has-text("Remove")',
            'button:has-text("✕")',
            'button:has-text("×")',
            '.remove-collaborator',
        ]

        # Try to find remove button within or near the collaborator element
        remove_button = None
        for selector in remove_selectors:
            try:
                # Try within the collaborator element first
                remove_button = await collaborator_element.query_selector(selector)
                if not remove_button:
                    # Try nearby
                    remove_button = await page.wait_for_selector(selector, timeout=1000)

                if remove_button:
                    if debug:
                        print(f"✅ Found remove button: {selector}")
                    await remove_button.click()
                    await asyncio.sleep(1)

                    if debug:
                        print(f"✅ Collaborator removed: {email}")
                    return True
            except:
                continue

        print("❌ Could not find remove button")
        return False

    except Exception as e:
        print(f"❌ Error removing collaborator: {e}")
        return False


async def list_collaborators(
    session_id: str,
    page,
    debug: bool = True
) -> List[str]:
    """
    List all collaborators on a Simplenote note

    Args:
        session_id: Session UUID
        page: Playwright page object
        debug: Enable debug logging

    Returns:
        List of collaborator email addresses
    """
    try:
        if debug:
            print(f"👥 Listing collaborators...")

        # Step 1: Open ellipsis menu
        ellipsis_selectors = [
            'button[aria-label*="Actions"]',
            'button[aria-label*="More"]',
            'button[title*="Actions"]',
            'button[title*="More"]',
            'button:has-text("⋯")',
            'button:has-text("...")',
            '.icon-ellipsis',
            '.actions-button',
        ]

        for selector in ellipsis_selectors:
            try:
                ellipsis_button = await page.wait_for_selector(selector, timeout=2000)
                if ellipsis_button:
                    await ellipsis_button.click()
                    await asyncio.sleep(1)
                    break
            except:
                continue

        # Step 2: Click "Collaborate" option
        collaborate_selectors = [
            'button:has-text("Collaborate")',
            'a:has-text("Collaborate")',
            '[role="menuitem"]:has-text("Collaborate")',
            'li:has-text("Collaborate")',
        ]

        for selector in collaborate_selectors:
            try:
                collab_option = await page.wait_for_selector(selector, timeout=2000)
                if collab_option:
                    await collab_option.click()
                    await asyncio.sleep(1)
                    break
            except:
                continue

        # Try to find collaborator list
        list_selectors = [
            '.collaborator-list',
            '.collaborators',
            '[data-collaborators]',
            '.shared-with',
        ]

        collaborators = []

        # Try to extract emails from the list
        # This is very UI-dependent and may need adjustment
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

        # Get all text content and extract emails
        page_content = await page.content()
        found_emails = re.findall(email_pattern, page_content)

        # Filter out placeholder emails, our own email, and duplicates
        excluded_patterns = [
            'email@example.com',
            'user@example.com',
            'name@example.com',
            'test@example.com',
            'example@example.com',
        ]

        collaborators = [
            email for email in set(found_emails)
            if email.lower() not in excluded_patterns
        ]

        if debug:
            if collaborators:
                print(f"✅ Found {len(collaborators)} collaborator(s):")
                for email in collaborators:
                    print(f"   - {email}")
            else:
                print("📭 No collaborators found")

        return collaborators

    except Exception as e:
        print(f"❌ Error listing collaborators: {e}")
        return []


# High-level functions that combine search + action

async def publish_session_note(
    cdp_url: str = 'http://localhost:9223',
    debug: bool = True
) -> Optional[str]:
    """
    Publish the current session's note

    Returns:
        Public URL if successful, None otherwise
    """
    session = get_active_session()
    if not session:
        print("❌ No active session")
        return None

    async with SimplenoteWriter(
        note_url='https://app.simplenote.com/',
        headless=False,
        debug=debug,
        cdp_url=cdp_url
    ) as writer:
        # Navigate to Simplenote
        await writer.page.goto('https://app.simplenote.com/')
        await writer.page.wait_for_load_state('networkidle')

        # Search for and select the session note
        found = await search_and_select_note(
            session['session_id'],
            writer.page,
            debug=debug
        )

        if not found:
            print("❌ Could not find session note")
            return None

        # Publish the note
        public_url = await publish_note(
            session['session_id'],
            writer.page,
            debug=debug
        )

        return public_url


async def unpublish_session_note(
    cdp_url: str = 'http://localhost:9223',
    debug: bool = True
) -> bool:
    """
    Unpublish the current session's note

    Returns:
        True if successful, False otherwise
    """
    session = get_active_session()
    if not session:
        print("❌ No active session")
        return False

    async with SimplenoteWriter(
        note_url='https://app.simplenote.com/',
        headless=False,
        debug=debug,
        cdp_url=cdp_url
    ) as writer:
        # Navigate to Simplenote
        await writer.page.goto('https://app.simplenote.com/')
        await writer.page.wait_for_load_state('networkidle')

        # Search for and select the session note
        found = await search_and_select_note(
            session['session_id'],
            writer.page,
            debug=debug
        )

        if not found:
            print("❌ Could not find session note")
            return False

        # Unpublish the note
        success = await unpublish_note(
            session['session_id'],
            writer.page,
            debug=debug
        )

        return success


async def add_session_collaborator(
    email: str,
    cdp_url: str = 'http://localhost:9223',
    debug: bool = True
) -> bool:
    """
    Add a collaborator to the current session's note

    Args:
        email: Collaborator email address

    Returns:
        True if successful, False otherwise
    """
    session = get_active_session()
    if not session:
        print("❌ No active session")
        return False

    async with SimplenoteWriter(
        note_url='https://app.simplenote.com/',
        headless=False,
        debug=debug,
        cdp_url=cdp_url
    ) as writer:
        # Navigate to Simplenote
        await writer.page.goto('https://app.simplenote.com/')
        await writer.page.wait_for_load_state('networkidle')

        # Search for and select the session note
        found = await search_and_select_note(
            session['session_id'],
            writer.page,
            debug=debug
        )

        if not found:
            print("❌ Could not find session note")
            return False

        # Add collaborator
        success = await add_collaborator(
            session['session_id'],
            email,
            writer.page,
            debug=debug
        )

        return success


async def remove_session_collaborator(
    email: str,
    cdp_url: str = 'http://localhost:9223',
    debug: bool = True
) -> bool:
    """
    Remove a collaborator from the current session's note

    Args:
        email: Collaborator email address

    Returns:
        True if successful, False otherwise
    """
    session = get_active_session()
    if not session:
        print("❌ No active session")
        return False

    async with SimplenoteWriter(
        note_url='https://app.simplenote.com/',
        headless=False,
        debug=debug,
        cdp_url=cdp_url
    ) as writer:
        # Navigate to Simplenote
        await writer.page.goto('https://app.simplenote.com/')
        await writer.page.wait_for_load_state('networkidle')

        # Search for and select the session note
        found = await search_and_select_note(
            session['session_id'],
            writer.page,
            debug=debug
        )

        if not found:
            print("❌ Could not find session note")
            return False

        # Remove collaborator
        success = await remove_collaborator(
            session['session_id'],
            email,
            writer.page,
            debug=debug
        )

        return success


async def list_session_collaborators(
    cdp_url: str = 'http://localhost:9223',
    debug: bool = True
) -> List[str]:
    """
    List all collaborators on the current session's note

    Returns:
        List of collaborator email addresses
    """
    session = get_active_session()
    if not session:
        print("❌ No active session")
        return []

    async with SimplenoteWriter(
        note_url='https://app.simplenote.com/',
        headless=False,
        debug=debug,
        cdp_url=cdp_url
    ) as writer:
        # Navigate to Simplenote
        await writer.page.goto('https://app.simplenote.com/')
        await writer.page.wait_for_load_state('networkidle')

        # Search for and select the session note
        found = await search_and_select_note(
            session['session_id'],
            writer.page,
            debug=debug
        )

        if not found:
            print("❌ Could not find session note")
            return []

        # List collaborators
        collaborators = await list_collaborators(
            session['session_id'],
            writer.page,
            debug=debug
        )

        return collaborators


async def share_session_note(
    identifier: str,
    cdp_url: str = 'http://localhost:9223',
    debug: bool = True
) -> Dict[str, any]:
    """
    Share the current session's note with collaborator(s) using glyph/alias/group/email

    Supports:
    - Glyphs: ♠️, 🌿, 🎸, ⚡, 🧠
    - Aliases: nyro, aureon, jamai, jerry, mia
    - Groups: assembly, all, perspectives
    - Direct emails: someone@example.com

    Args:
        identifier: Glyph, alias, group, or email
        cdp_url: Chrome DevTools Protocol URL
        debug: Enable debug logging

    Returns:
        Dict with 'success', 'added', 'failed', 'total' keys

    Examples:
        share_session_note("♠️")        → Add Nyro
        share_session_note("assembly")  → Add all Assembly members
        share_session_note("custom@example.com")  → Add custom email
    """
    session = get_active_session()
    if not session:
        print("❌ No active session")
        return {'success': False, 'added': [], 'failed': [], 'total': 0}

    # Resolve identifier to email(s)
    emails = resolve_collaborator(identifier, debug=debug)

    if not emails:
        print(f"❌ Could not resolve '{identifier}'")
        print(f"💡 Run 'simexp session share --help' to see available options")
        return {'success': False, 'added': [], 'failed': [], 'total': 0}

    print(f"\n♠️🌿🎸🧵 Sharing Session Note")
    print(f"🔮 Session: {session['session_id']}")
    print(f"👥 Adding {len(emails)} collaborator(s)...")

    added = []
    failed = []

    async with SimplenoteWriter(
        note_url='https://app.simplenote.com/',
        headless=False,
        debug=debug,
        cdp_url=cdp_url
    ) as writer:
        # Navigate to Simplenote
        await writer.page.goto('https://app.simplenote.com/')
        await writer.page.wait_for_load_state('networkidle')

        # Search for and select the session note ONCE
        found = await search_and_select_note(
            session['session_id'],
            writer.page,
            debug=debug
        )

        if not found:
            print("❌ Could not find session note")
            return {'success': False, 'added': [], 'failed': emails, 'total': len(emails)}

        # Add each collaborator
        for i, email in enumerate(emails, 1):
            if debug and len(emails) > 1:
                print(f"\n[{i}/{len(emails)}] Adding: {email}")

            try:
                # Timeout protection: 15 seconds per collaborator
                success = await asyncio.wait_for(
                    add_collaborator(
                        session['session_id'],
                        email,
                        writer.page,
                        debug=debug
                    ),
                    timeout=15.0
                )

                if success:
                    added.append(email)
                else:
                    failed.append(email)

            except asyncio.TimeoutError:
                print(f"⏱️  Timeout adding {email} (15s exceeded)")
                failed.append(email)
            except Exception as e:
                print(f"❌ Error adding {email}: {e}")
                failed.append(email)

            # Cleanup: Close any open dialogs/menus before next iteration
            if i < len(emails):  # Don't cleanup after last one
                await writer.page.keyboard.press('Escape')
                await asyncio.sleep(0.5)

    # Summary
    print(f"\n📊 Sharing Summary:")
    print(f"✅ Added: {len(added)}/{len(emails)}")
    if added:
        for email in added:
            print(f"   👤 {email}")
    if failed:
        print(f"❌ Failed: {len(failed)}/{len(emails)}")
        for email in failed:
            print(f"   ❌ {email}")

    return {
        'success': len(failed) == 0,
        'added': added,
        'failed': failed,
        'total': len(emails)
    }
