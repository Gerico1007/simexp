"""
SimExp Playwright Writer Module
Chrome browser automation for writing to Simplenote web pages

♠️🌿🎸🧵 G.Music Assembly - Bidirectional Flow Integration
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from typing import Optional, Literal
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimplenoteWriter:
    """
    Playwright-based writer for Simplenote web interface

    Usage:
        async with SimplenoteWriter(note_url) as writer:
            result = await writer.write_content("Hello from terminal!")
    """

    # Selector strategies for Simplenote editor (tried in order)
    EDITOR_SELECTORS = [
        'textarea.note-editor',
        'textarea[class*="note"]',
        'textarea[class*="editor"]',
        'div.note-editor',
        'div[contenteditable="true"]',
        '[contenteditable="true"]',
        'textarea',
        '.CodeMirror textarea',  # In case Simplenote uses CodeMirror
    ]

    def __init__(
        self,
        note_url: str,
        headless: bool = False,
        debug: bool = False,
        timeout: int = 30000,
        cdp_url: str = None
    ):
        """
        Initialize SimplenoteWriter

        Args:
            note_url: Full Simplenote note URL (e.g., https://app.simplenote.com/p/0ZqWsQ)
            headless: Run browser in headless mode (default: False for debugging)
            debug: Enable verbose debug logging
            timeout: Page load timeout in milliseconds
            cdp_url: Chrome DevTools Protocol URL to connect to existing browser
                    (e.g., 'http://localhost:9222') - if None, launches new browser
        """
        self.note_url = note_url
        self.headless = headless
        self.debug = debug
        self.timeout = timeout
        self.cdp_url = cdp_url

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

        if debug:
            logger.setLevel(logging.DEBUG)

    async def __aenter__(self):
        """Async context manager entry - launches browser"""
        await self.connect()
        return self

    async def __aexit__(self, *args):
        """Async context manager exit - closes browser"""
        await self.close()

    async def connect(self):
        """Launch Playwright and connect to browser (existing or new)"""
        self.playwright = await async_playwright().start()

        if self.cdp_url:
            # Connect to existing Chrome with authentication
            logger.info(f"🔗 Connecting to existing Chrome at {self.cdp_url}...")
            self.browser = await self.playwright.chromium.connect_over_cdp(self.cdp_url)

            # Use the default context (which has your login session)
            contexts = self.browser.contexts
            if contexts:
                self.context = contexts[0]
                logger.info(f"✅ Using existing browser context with {len(self.context.pages)} pages")
            else:
                # Create new context if none exists
                self.context = await self.browser.new_context()
                logger.info("✅ Created new context in existing browser")

            # Create a new page in the existing context
            self.page = await self.context.new_page()
            logger.info("✅ Connected to authenticated Chrome session!")

        else:
            # Launch new browser instance
            logger.info("🚀 Launching new Playwright Chromium...")
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--remote-debugging-port=9222',  # Keep CDP access available
                    '--disable-blink-features=AutomationControlled',  # Avoid detection
                ]
            )

            # Create persistent context (could add auth cookies here later)
            self.context = await self.browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            )

            self.page = await self.context.new_page()
            logger.info("✅ Browser launched successfully")

        if self.debug:
            self.page.on('console', lambda msg: logger.debug(f"Browser console: {msg.text}"))

    async def close(self):
        """Close browser and Playwright"""
        if self.cdp_url:
            # Only close the page we created, not the entire browser
            if self.page:
                await self.page.close()
            logger.info("🔒 Page closed (browser remains open)")
        else:
            # We launched the browser, so we close it
            if self.browser:
                await self.browser.close()
            logger.info("🔒 Browser closed")

        if self.playwright:
            await self.playwright.stop()

    async def navigate(self):
        """Navigate to Simplenote note URL"""
        logger.info(f"🌐 Navigating to: {self.note_url}")
        response = await self.page.goto(self.note_url, timeout=self.timeout)

        if not response or not response.ok:
            raise Exception(f"Failed to load {self.note_url}: {response.status if response else 'No response'}")

        # Wait for page to be fully loaded
        await self.page.wait_for_load_state('networkidle', timeout=self.timeout)
        logger.info("✅ Page loaded")

        # If the URL is the base URL, click the first note
        if self.note_url == "https://app.simplenote.com/":
            logger.info("🔍 Base URL detected, finding most recent note...")
            try:
                first_note_selector = "div.note-list-item"
                await self.page.wait_for_selector(first_note_selector, timeout=10000)
                await self.page.click(first_note_selector)
                logger.info("✅ Clicked on the most recent note.")
                await self.page.wait_for_load_state('networkidle', timeout=self.timeout)
            except PlaywrightTimeout:
                raise Exception("Could not find the note list. Are you logged in?")

    async def find_editor(self) -> str:
        """
        Find the editor element using multiple selector strategies

        Returns:
            Selector string that successfully found the editor

        Raises:
            Exception if no editor found
        """
        logger.info("🔍 Searching for editor element...")

        for selector in self.EDITOR_SELECTORS:
            try:
                element = await self.page.wait_for_selector(
                    selector,
                    timeout=5000,
                    state='visible'
                )
                if element:
                    logger.info(f"✅ Found editor with selector: {selector}")
                    return selector
            except PlaywrightTimeout:
                if self.debug:
                    logger.debug(f"❌ Selector failed: {selector}")
                continue

        # If we get here, no selector worked
        # Take a screenshot for debugging
        screenshot_path = "/tmp/simplenote_debug.png"
        await self.page.screenshot(path=screenshot_path)

        raise Exception(
            f"Could not find editor element on {self.note_url}\n"
            f"Tried selectors: {self.EDITOR_SELECTORS}\n"
            f"Screenshot saved to: {screenshot_path}\n"
            f"Page title: {await self.page.title()}"
        )

    async def get_current_content(self, selector: str) -> str:
        """Get current content from editor"""
        try:
            # Try input_value first (for textarea)
            content = await self.page.input_value(selector)
            return content
        except:
            # Fallback to text_content (for contenteditable divs)
            element = await self.page.query_selector(selector)
            if element:
                content = await element.text_content()
                return content or ""
            return ""

    async def write_content(
        self,
        content: str,
        mode: Literal['append', 'replace'] = 'append',
        separator: str = '\n\n---\n\n'
    ) -> dict:
        """
        Write content to Simplenote note

        Args:
            content: Text to write
            mode: 'append' to add to existing content, 'replace' to overwrite
            separator: String to insert between existing and new content (append mode)

        Returns:
            dict with status, written content preview, and metadata
        """
        await self.navigate()

        # Find the editor element
        selector = await self.find_editor()

        # Get current content for verification
        current_content = ""
        if mode == 'append':
            current_content = await self.get_current_content(selector)
            logger.info(f"📄 Current content length: {len(current_content)} chars")

        # Different approaches for different editor types
        element = await self.page.query_selector(selector)
        tag_name = await element.evaluate('el => el.tagName.toLowerCase()')

        if tag_name in ['textarea', 'input']:
            # Standard form elements - can use fill()
            if mode == 'append' and current_content:
                new_content = f"{current_content}{separator}{content}"
            else:
                new_content = content
            logger.info(f"✍️  Writing {len(new_content)} characters...")
            await self.page.fill(selector, new_content)
        else:
            # ContentEditable div - use keyboard simulation
            await element.click()
            await asyncio.sleep(0.5)

            if mode == 'append':
                # Append mode: go to end and type only new content
                # ⚡ PERFORMANCE OPTIMIZATION: Types only new content instead of entire note
                logger.info(f"✍️  Appending {len(separator) + len(content)} characters...")
                await self.page.keyboard.press('Control+End')  # Go to end
                await asyncio.sleep(0.2)
                logger.info("⌨️  Typing separator and new content...")
                await self.page.keyboard.type(separator + content, delay=0)
                new_content = f"{current_content}{separator}{content}"
            else:
                # Replace mode: select all and type new content
                logger.info(f"✍️  Replacing with {len(content)} characters...")
                await self.page.keyboard.press('Control+A')
                await asyncio.sleep(0.2)
                logger.info("⌨️  Typing new content...")
                await self.page.keyboard.type(content, delay=0)
                new_content = content

        # Wait a moment for autosave
        await asyncio.sleep(1)

        # Verify write
        verify_content = await self.get_current_content(selector)

        # For append mode, verify that our new content appears at the end
        # For replace mode, verify exact match
        if mode == 'append':
            # Check if our appended content appears at the end
            expected_suffix = separator + content
            success = verify_content.endswith(expected_suffix)
            if not success:
                # Fallback: check if content appears anywhere (in case of sync delays)
                success = content in verify_content
        else:
            # Replace mode: expect exact match
            success = verify_content == new_content

        result = {
            'success': success,
            'mode': mode,
            'url': self.note_url,
            'content_length': len(verify_content),
            'expected_length': len(new_content),
            'preview': verify_content[-100:] if mode == 'append' else verify_content[:100],
            'verified': success
        }

        if success:
            logger.info(f"✅ Write successful! ({len(verify_content)} chars)")
        else:
            logger.warning(f"⚠️  Write verification failed")
            logger.warning(f"Expected length: {len(new_content)}, Got: {len(verify_content)}")
            if mode == 'append':
                logger.warning(f"Looking for content ending with: ...{expected_suffix[-50:]}")

        return result

    async def read_content(self) -> str:
        """
        Read current content from Simplenote note

        Returns:
            Current note content as string
        """
        await self.navigate()
        selector = await self.find_editor()
        content = await self.get_current_content(selector)
        logger.info(f"📖 Read {len(content)} characters")
        return content


async def write_to_note(
    note_url: str,
    content: str,
    mode: Literal['append', 'replace'] = 'append',
    headless: bool = False,
    debug: bool = False,
    cdp_url: str = None
) -> dict:
    """
    Convenience function to write to a Simplenote note

    Usage:
        # Connect to existing Chrome with login:
        result = await write_to_note(
            'https://app.simplenote.com',
            'Hello from terminal!',
            cdp_url='http://localhost:9222'
        )

        # Or launch new browser:
        result = await write_to_note(
            'https://app.simplenote.com/p/0ZqWsQ',
            'Hello from terminal!',
            mode='append'
        )
    """
    async with SimplenoteWriter(note_url, headless=headless, debug=debug, cdp_url=cdp_url) as writer:
        return await writer.write_content(content, mode=mode)


async def read_from_note(
    note_url: str,
    headless: bool = True,
    debug: bool = False,
    cdp_url: str = None
) -> str:
    """
    Convenience function to read from a Simplenote note

    Usage:
        # Connect to existing Chrome:
        content = await read_from_note(
            'https://app.simplenote.com',
            cdp_url='http://localhost:9222'
        )

        # Or launch new browser:
        content = await read_from_note('https://app.simplenote.com/p/0ZqWsQ')
    """
    async with SimplenoteWriter(note_url, headless=headless, debug=debug, cdp_url=cdp_url) as writer:
        return await writer.read_content()


# CLI interface for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage:")
        print("  Write: python playwright_writer.py write <note_url> <content>")
        print("  Read:  python playwright_writer.py read <note_url>")
        sys.exit(1)

    command = sys.argv[1]
    note_url = sys.argv[2]

    if command == 'write':
        content = sys.argv[3] if len(sys.argv) > 3 else "Test message from SimExp Playwright Writer"
        result = asyncio.run(write_to_note(note_url, content, debug=True))
        print(f"\n✅ Result: {result}")

    elif command == 'read':
        content = asyncio.run(read_from_note(note_url, debug=True))
        print(f"\n📖 Content:\n{content}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
