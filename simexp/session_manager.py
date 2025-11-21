"""
SimExp Session Manager
Manages terminal session state and Simplenote note creation

♠️🌿🎸🧵 G.Music Assembly - Session-Aware Notes Feature
"""

import os
import json
import uuid
import asyncio
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
import yaml

from .playwright_writer import SimplenoteWriter, write_to_note
from .session_file_handler import SessionFileHandler

async def handle_session_add(file_path: str, heading: Optional[str] = None, cdp_url: Optional[str] = None) -> None:
    """
    Handle the session add command

    Args:
        file_path: Path to the file to add
        heading: Optional heading to add before the file content
        cdp_url: Optional CDP URL for browser connection
    """
    # Get CDP URL from config if not provided
    if not cdp_url:
        from .simex import get_cdp_url
        cdp_url = get_cdp_url()

    session = get_active_session()
    if not session:
        print("❌ No active session. Start a session first with 'simexp session start'")
        return

    file_path = str(Path(file_path).resolve())
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return

    try:
        # ⚡ FIX Issue #24: Create writer context to get page object for search_and_select_note
        async with SimplenoteWriter(note_url='https://app.simplenote.com/', cdp_url=cdp_url) as writer:
            # Navigate to Simplenote
            print(f"🌐 Adding File to Session Note")
            print(f"🔮 Session: {session['session_id']}")
            print(f"📄 File: {Path(file_path).name}")

            await writer.page.goto('https://app.simplenote.com/')
            await writer.page.wait_for_load_state('networkidle')

            # First find and select the session note (now passing the page!)
            if not await search_and_select_note(session['session_id'], writer.page):
                print("❌ Could not find session note")
                return

            # Read and format the file content
            handler = SessionFileHandler()
            content = handler.read_file(file_path)
            formatted_content = handler.format_content(file_path, content, heading)

            # Print formatted content info
            print(f"📄 File content formatted ({len(formatted_content)} chars)")
            print(f"✍️ Writing to Session Note")
            print(f"🔮 Session: {session['session_id']}")
            print(f"📝 Content length: {len(formatted_content)} chars")

            # Write the content to the selected note
            await writer.append_content(formatted_content)

            print(f"✅ Added file: {Path(file_path).name} to session")

    except Exception as e:
        print(f"❌ Error adding file: {e}")
        import traceback
        traceback.print_exc()


class SessionState:
    """
    Manages local session state persistence

    State is stored in .simexp/session.json in the current working directory
    """

    STATE_DIR = '.simexp'
    STATE_FILE = 'session.json'

    def __init__(self, workspace_dir: str = None):
        """
        Initialize SessionState

        Args:
            workspace_dir: Workspace directory (defaults to current working directory)
        """
        self.workspace_dir = workspace_dir or os.getcwd()
        self.state_dir = os.path.join(self.workspace_dir, self.STATE_DIR)
        self.state_file = os.path.join(self.state_dir, self.STATE_FILE)

    def ensure_state_dir(self):
        """Create .simexp directory if it doesn't exist"""
        os.makedirs(self.state_dir, exist_ok=True)

    def save_session(self, session_data: Dict) -> None:
        """
        Save session data to .simexp/session.json

        Args:
            session_data: Dictionary containing session information
        """
        self.ensure_state_dir()
        with open(self.state_file, 'w') as f:
            json.dump(session_data, f, indent=2)

    def load_session(self) -> Optional[Dict]:
        """
        Load session data from .simexp/session.json

        Returns:
            Session data dictionary or None if no active session
        """
        if not os.path.exists(self.state_file):
            return None

        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def clear_session(self) -> None:
        """Remove session state file"""
        if os.path.exists(self.state_file):
            os.remove(self.state_file)


def generate_html_metadata(
    session_id: str,
    ai_assistant: str = 'claude',
    agents: List[str] = None,
    issue_number: Optional[int] = None,
    pr_number: Optional[int] = None
) -> str:
    """
    Generate HTML tag metadata header for session note

    Uses hidden <div> tag for invisible, navigable metadata storage.
    This approach:
    - Keeps metadata invisible with 'hidden' attribute
    - Prevents live-editor formatting corruption
    - Enables easy Playwright selector navigation
    - Maintains searchability (session_id still in text content)
    - Provides cleaner user experience

    Args:
        session_id: Unique session UUID
        ai_assistant: AI assistant name (claude or gemini)
        agents: List of agent names (defaults to Assembly agents)
        issue_number: GitHub issue number being worked on
        pr_number: GitHub PR number (if applicable)

    Returns:
        Hidden div with YAML metadata as string
    """
    if agents is None:
        agents = ['Jerry', 'Aureon', 'Nyro', 'JamAI', 'Synth']

    metadata = {
        'session_id': session_id,
        'ai_assistant': ai_assistant,
        'agents': agents,
        'issue_number': issue_number,
        'pr_number': pr_number,
        'created_at': datetime.now().isoformat()
    }

    yaml_content = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
    # Use hidden div with class for easy selector navigation
    return f'<div class="simexp-session-metadata" hidden>\n{yaml_content}</div>\n\n'


async def create_session_note(
    ai_assistant: str = 'claude',
    issue_number: Optional[int] = None,
    repo: Optional[str] = None,
    cdp_url: str = 'http://localhost:9223',
    headless: bool = False,
    debug: bool = True,
    post_write_delay: float = 3.0
) -> Dict:
    """
    Create a new Simplenote note for the current session

    This function:
    1. Generates a unique session UUID
    2. Uses Playwright to create a new note in Simplenote
    3. Writes YAML metadata header to the note
    4. Fetches GitHub issue data if issue_number is provided
    5. Saves session state to .simexp/session.json

    Args:
        ai_assistant: AI assistant name (claude or gemini)
        issue_number: GitHub issue number being worked on
        repo: GitHub repository in format 'owner/name' (auto-detected if not provided)
        cdp_url: Chrome DevTools Protocol URL
        headless: Run browser in headless mode
        debug: Enable debug logging
        post_write_delay: Delay (in seconds) after metadata write for Simplenote to index the note (default: 3.0)

    Returns:
        Dictionary with session info (session_id, note_url, etc.)
    """
    # Generate session ID
    session_id = str(uuid.uuid4())

    print(f"♠️🌿🎸🧵 Creating Session Note")
    print(f"🔮 Session ID: {session_id}")
    print(f"🤝 AI Assistant: {ai_assistant}")

    # Fetch GitHub issue if provided
    issue_data = None
    issue_content = ""
    if issue_number:
        print(f"🎯 Issue: #{issue_number}")
        from .github_issue import GitHubIssueFetcher
        fetcher = GitHubIssueFetcher()
        issue_data = fetcher.fetch_issue(issue_number, repo)
        if issue_data:
            print(f"✅ Fetched issue #{issue_number}")
            issue_content = fetcher.format_for_session(issue_data)
        else:
            print(f"⚠️ Could not fetch issue #{issue_number}")

    # Connect to Simplenote and create new note
    # ⚡ FIX: Direct metadata write to avoid navigation bug
    async with SimplenoteWriter(
        note_url='https://app.simplenote.com/',
        headless=headless,
        debug=debug,
        cdp_url=cdp_url
    ) as writer:
        # Navigate to Simplenote
        await writer.page.goto('https://app.simplenote.com/')
        await writer.page.wait_for_load_state('networkidle')

        # Find and click "New Note" button
        # Try multiple selectors for the new note button
        new_note_selectors = [
            'button[aria-label*="New Note"]',  # Matches "New Note • Ctrl+Shift+I"
            'button[aria-label="New Note"]',
            'button[title="New Note"]',
            '.button-new-note',
            'button:has-text("New")',
            '[data-action="new-note"]'
        ]

        new_note_clicked = False
        for selector in new_note_selectors:
            try:
                element = await writer.page.wait_for_selector(selector, timeout=3000)
                if element:
                    await element.click()
                    new_note_clicked = True
                    print(f"✅ Clicked new note button: {selector}")
                    break
            except:
                continue

        if not new_note_clicked:
            raise Exception("Could not find 'New Note' button. Please ensure you're logged into Simplenote.")

        # Wait for note creation and editor to be ready
        await asyncio.sleep(2)
        await writer.page.wait_for_load_state('networkidle')

        # Generate HTML tag metadata header
        metadata_header = generate_html_metadata(
            session_id=session_id,
            ai_assistant=ai_assistant,
            issue_number=issue_number
        )

        # ⚡ FIX: Write metadata DIRECTLY to the new note (already focused!)
        # Don't use writer.write_content() - it would navigate and select wrong note
        print(f"📝 Writing metadata directly to new note...")

        # Find the editor element
        editor = await writer.page.wait_for_selector('div.note-editor', timeout=5000)
        await editor.click()
        await asyncio.sleep(0.5)

        # Type the HTML tag metadata directly
        await writer.page.keyboard.type(metadata_header, delay=0)

        # Add issue content if available
        if issue_content:
            print(f"📄 Adding issue content to note...")
            await writer.page.keyboard.type(issue_content, delay=0)

        await asyncio.sleep(post_write_delay)  # Wait for Simplenote to index the note

        print(f"✅ Metadata written to new note")
        if issue_content:
            print(f"✅ Issue content added to new note")

    # Save session state
    # ⚡ FIX: Use session_id as search key, not note_url
    # 🧵 Enhancement (Issue #36): Store CDP endpoint for cross-device coordination
    session_data = {
        'session_id': session_id,
        'search_key': session_id,  # Use session_id to find the note via search
        'ai_assistant': ai_assistant,
        'issue_number': issue_number,
        'cdp_endpoint': cdp_url,  # Store CDP URL for network-wide access
        'created_at': datetime.now().isoformat()
    }

    state = SessionState()
    state.save_session(session_data)
    print(f"💾 Session state saved to {state.state_file}")
    print(f"🔑 Search key: {session_id}")

    return session_data


def get_active_session() -> Optional[Dict]:
    """
    Get the currently active session

    Searches for session.json in this order:
    1. Current directory: ./.simexp/session.json
    2. Parent directories: ../.simexp/session.json (walking up)
    3. Home directory: ~/.simexp/session.json

    Returns:
        Session data dictionary or None if no active session
    """
    # Start from current directory
    current_dir = os.getcwd()

    # Walk up directory tree looking for .simexp/session.json
    check_dir = current_dir
    while True:
        state = SessionState(workspace_dir=check_dir)
        session = state.load_session()
        if session:
            # Add directory info to session data
            session['_session_dir'] = state.state_dir
            return session

        # Move to parent directory
        parent = os.path.dirname(check_dir)
        if parent == check_dir:  # Reached root
            break
        check_dir = parent

    # Finally check home directory
    home_dir = os.path.expanduser('~')
    state = SessionState(workspace_dir=home_dir)
    session = state.load_session()
    if session:
        session['_session_dir'] = state.state_dir
    return session


def get_session_directory() -> Optional[str]:
    """
    Get the directory containing the active session

    Returns:
        Path to .simexp directory containing session.json, or None
    """
    session = get_active_session()
    if session and '_session_dir' in session:
        return session['_session_dir']
    return None


def list_all_sessions() -> List[Dict]:
    """
    Find all session.json files in directory tree and home directory

    Searches from current directory upward, then home directory.

    Returns:
        List of dicts with session data and directory info
    """
    sessions = []
    seen_dirs = set()

    # Start from current directory and walk up
    current_dir = os.getcwd()
    check_dir = current_dir

    while True:
        state = SessionState(workspace_dir=check_dir)
        if os.path.exists(state.state_file) and check_dir not in seen_dirs:
            session = state.load_session()
            if session:
                session['_session_dir'] = state.state_dir
                session['_is_active'] = (check_dir == current_dir)
                sessions.append(session)
                seen_dirs.add(check_dir)

        # Move to parent
        parent = os.path.dirname(check_dir)
        if parent == check_dir:  # Reached root
            break
        check_dir = parent

    # Check home directory if not already found
    home_dir = os.path.expanduser('~')
    if home_dir not in seen_dirs:
        state = SessionState(workspace_dir=home_dir)
        if os.path.exists(state.state_file):
            session = state.load_session()
            if session:
                session['_session_dir'] = state.state_dir
                session['_is_active'] = (home_dir == current_dir)
                sessions.append(session)

    # Sort by creation date (newest first)
    sessions.sort(key=lambda s: s.get('created_at', ''), reverse=True)

    return sessions


def clear_active_session() -> None:
    """Clear the currently active session"""
    state = SessionState()
    state.clear_session()
    print("🧹 Session cleared")


async def set_session_title(title: str, cdp_url: str = 'http://localhost:9223') -> bool:
    """
    Set a title for the current session note

    This function:
    1. Gets the active session from session.json
    2. Searches for the note using session_id
    3. Goes to the beginning of the note (Ctrl+Home)
    4. Writes the title at the top
    5. Saves the title to session.json

    Args:
        title: The title to set for the session
        cdp_url: Chrome DevTools Protocol URL

    Returns:
        True if successful, False otherwise
    """
    try:
        # Get active session
        session = get_active_session()
        if not session:
            print("❌ No active session. Run 'simexp session start' first.")
            return False

        print(f"♠️🌿🎸🧵 Setting Session Title")
        print(f"🔮 Session: {session['session_id']}")
        print(f"📝 Title: {title}")

        # Search for and update the note
        async with SimplenoteWriter(
            note_url='https://app.simplenote.com/',
            headless=False,
            debug=True,
            cdp_url=cdp_url
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
                print("❌ Could not find session note.")
                return False

            # Get the editor and position cursor at beginning
            editor = await writer.page.wait_for_selector('div.note-editor', timeout=5000)
            await editor.click()
            await asyncio.sleep(0.3)

            # Go to beginning
            await writer.page.keyboard.press('Control+Home')
            await asyncio.sleep(0.2)

            # Type the title with a separator
            title_text = f"{title}\n{'='*len(title)}\n\n"
            await writer.page.keyboard.type(title_text, delay=10)
            await asyncio.sleep(2)  # Wait for autosave

            print(f"✅ Title written to note")

        # Save title to session.json
        state = SessionState()
        session_data = state.load_session()
        if session_data:
            session_data['title'] = title
            state.save_session(session_data)
            print(f"💾 Title saved to session.json")
            return True
        else:
            print("⚠️ Could not save title to session.json")
            return False

    except Exception as e:
        print(f"❌ Error setting session title: {e}")
        return False


async def search_and_select_note(
    session_id: str,
    page,
    debug: bool = True
) -> bool:
    """
    Search for a note by session_id and select it

    Args:
        session_id: The unique session UUID to search for
        page: Playwright page object
        debug: Enable debug logging

    Returns:
        True if note found and selected, False otherwise
    """
    try:
        if debug:
            print(f"🔍 Searching for session note: {session_id}")

        # Find and click the search box
        search_selectors = [
            'input[type="search"]',
            'input[placeholder*="Search"]',
            '.search-field',
            'input.search'
        ]

        search_box = None
        for selector in search_selectors:
            try:
                search_box = await page.wait_for_selector(selector, timeout=3000)
                if search_box:
                    break
            except:
                continue

        if not search_box:
            print("❌ Could not find search box")
            return False

        # Clear existing search and type session_id
        await search_box.click()
        await page.keyboard.press('Control+A')
        await page.keyboard.press('Backspace')
        await page.keyboard.type(session_id, delay=50)
        await asyncio.sleep(1)  # Wait for search results

        if debug:
            print(f"✅ Typed search query: {session_id}")

        # Click the first result (should be our note with the session_id in metadata)
        note_result = await page.wait_for_selector('.note-list-item', timeout=5000)
        if note_result:
            await note_result.click()
            await asyncio.sleep(1)  # Wait for note to load
            if debug:
                print(f"✅ Selected session note from search results")
            return True
        else:
            print("❌ No note found with that session_id")
            return False

    except Exception as e:
        print(f"❌ Error searching for note: {e}")
        return False


# CLI interface for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Create session: python session_manager.py create [--ai <assistant>] [--issue <number>]")
        print("  Get session:    python session_manager.py get")
        print("  Clear session:  python session_manager.py clear")
        print("  Add file:       python session_manager.py add <file_path> [--heading <text>]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) < 3:
            print("Error: Missing file path")
            print("Usage: python session_manager.py add <file_path> [--heading <text>]")
            sys.exit(1)
            
        file_path = sys.argv[2]
        heading = None
        
        # Check for heading argument
        if "--heading" in sys.argv:
            heading_index = sys.argv.index("--heading")
            if heading_index + 1 < len(sys.argv):
                heading = sys.argv[heading_index + 1]
                
        # Run the add command
        asyncio.run(handle_session_add(file_path, heading))
        sys.exit(0)

    command = sys.argv[1]

    if command == 'create':
        # Parse optional arguments
        ai_assistant = 'claude'
        issue_number = None

        for i, arg in enumerate(sys.argv[2:]):
            if arg == '--ai' and i+3 < len(sys.argv):
                ai_assistant = sys.argv[i+3]
            elif arg == '--issue' and i+3 < len(sys.argv):
                issue_number = int(sys.argv[i+3])

        # Create session
        session_data = asyncio.run(create_session_note(
            ai_assistant=ai_assistant,
            issue_number=issue_number
        ))

        print(f"\n✅ Session created!")
        print(f"🔮 Session ID: {session_data['session_id']}")
        print(f"🌐 Note URL: {session_data['note_url']}")

    elif command == 'get':
        session = get_active_session()
        if session:
            print(f"📋 Active Session:")
            print(f"🔮 Session ID: {session['session_id']}")
            print(f"🌐 Note URL: {session['note_url']}")
            print(f"🤝 AI Assistant: {session['ai_assistant']}")
            if session.get('issue_number'):
                print(f"🎯 Issue: #{session['issue_number']}")
        else:
            print("❌ No active session")

    elif command == 'clear':
        clear_active_session()

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
