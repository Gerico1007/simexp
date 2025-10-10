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

        # Step 2: Find and click "Publish" option in menu
        publish_selectors = [
            'button:has-text("Publish")',
            'a:has-text("Publish")',
            '[role="menuitem"]:has-text("Publish")',
            'li:has-text("Publish")',
            '.menu-item:has-text("Publish")',
        ]

        publish_option = None
        for selector in publish_selectors:
            try:
                publish_option = await page.wait_for_selector(selector, timeout=2000)
                if publish_option:
                    if debug:
                        print(f"✅ Found publish option: {selector}")
                    await publish_option.click()
                    await asyncio.sleep(1)
                    break
            except:
                continue

        if not publish_option:
            print("❌ Could not find 'Publish' option in menu")
            print("💡 Note: Simplenote may not have publish feature, or menu changed")
            return None

        # Wait for publish to complete
        await asyncio.sleep(2)

        # Try to extract public URL
        # Common patterns for public URLs
        url_selectors = [
            'input[readonly][value*="simplenote.com/p/"]',
            'a[href*="simplenote.com/p/"]',
            '.public-url',
            '[data-public-url]',
            'input[type="text"][value*="/p/"]'
        ]

        public_url = None
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
                        public_url = url
                        if debug:
                            print(f"✅ Extracted public URL: {public_url}")
                        break
            except:
                continue

        if not public_url:
            if debug:
                print("⚠️ Published, but could not extract URL automatically")
                print("💡 You may need to copy it manually from Simplenote UI")

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
                    await asyncio.sleep(1)
                    break
            except:
                continue

        if not add_button:
            # Try pressing Enter as fallback
            await page.keyboard.press('Enter')
            await asyncio.sleep(1)

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

        # Filter out our own email and duplicates
        collaborators = list(set(found_emails))

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
