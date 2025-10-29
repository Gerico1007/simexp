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
from .playwright_writer import write_to_note, read_from_note, SimplenoteWriter
from .session_manager import (
    create_session_note,
    get_active_session,
    clear_active_session,
    search_and_select_note
)
from .session_sharing import (
    publish_session_note,
    unpublish_session_note,
    add_session_collaborator,
    remove_session_collaborator,
    list_session_collaborators,
    share_session_note
)
from .session_manager import handle_session_add

# Config file in user's home directory (not package directory)
CONFIG_FILE = os.path.expanduser('~/.simexp/simexp.yaml')

# ═══════════════════════════════════════════════════════════════
# CDP URL RESOLUTION - Issue #11
# ♠️ Nyro: Three-tier priority chain for multi-network support
# ═══════════════════════════════════════════════════════════════

def get_cdp_url(override: str = None) -> str:
    """
    Get CDP (Chrome DevTools Protocol) URL using priority chain

    Priority order:
    1. override parameter (highest - explicit function call)
    2. SIMEXP_PORT environment variable (just port number) - Issue #38
    3. SIMEXP_CDP_URL environment variable (full URL)
    4. CDP_URL from ~/.simexp/simexp.yaml (persistent user config)
    5. http://localhost:9223 (fallback default)

    Args:
        override: Explicit CDP URL (e.g., from --cdp-url flag)

    Returns:
        CDP URL string

    Examples:
        # Command-line override (highest priority)
        get_cdp_url('http://192.168.1.100:9223')

        # SIMEXP_PORT environment variable (Issue #38)
        export SIMEXP_PORT=9223
        get_cdp_url()  # → http://localhost:9223

        # SIMEXP_CDP_URL environment variable
        export SIMEXP_CDP_URL=http://10.0.0.5:9223
        get_cdp_url()  # → http://10.0.0.5:9223

        # Config file
        # ~/.simexp/simexp.yaml contains: CDP_URL: http://server:9223
        get_cdp_url()  # → http://server:9223

        # Fallback
        get_cdp_url()  # → http://localhost:9223
    """
    # Priority 1: Explicit override parameter
    if override:
        return override

    # Priority 2: SIMEXP_PORT environment variable (Issue #38)
    # Convenient for just setting a port number
    env_port = os.environ.get('SIMEXP_PORT')
    if env_port:
        try:
            port_num = int(env_port)
            return f'http://localhost:{port_num}'
        except ValueError:
            pass  # Fall through if invalid port number

    # Priority 3: SIMEXP_CDP_URL environment variable (full URL)
    env_cdp = os.environ.get('SIMEXP_CDP_URL')
    if env_cdp:
        return env_cdp

    # Priority 4: Config file
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = yaml.safe_load(f)
                if config and 'CDP_URL' in config:
                    return config['CDP_URL']
        except Exception:
            pass  # Fall through to default

    # Priority 5: Default localhost (Chrome DevTools Protocol standard port)
    return 'http://localhost:9223'


def normalize_cdp_url(input_str: str) -> str:
    """
    Normalize CDP URL input - handles various formats

    Handles:
    - Full URLs: http://localhost:9223 → no change
    - Just port: 9223 → http://localhost:9223
    - IP:Port: 192.168.1.100:9223 → http://192.168.1.100:9223

    Args:
        input_str: User input for CDP URL

    Returns:
        Properly formatted CDP URL

    🧵 Synth (Issue #38): Fix URL formatting bug in simexp init
    """
    input_str = input_str.strip()

    # Already a full URL
    if input_str.startswith('http://') or input_str.startswith('https://'):
        return input_str

    # Just a port number
    if input_str.isdigit():
        return f'http://localhost:{input_str}'

    # IP:Port format (e.g., 192.168.1.100:9222)
    if ':' in input_str and not input_str.startswith('http'):
        return f'http://{input_str}'

    # Fallback: assume it's meant to be localhost:port
    return f'http://localhost:{input_str}'


def extract_port_from_url(cdp_url: str) -> int:
    """
    Extract port number from CDP URL

    Args:
        cdp_url: CDP URL (e.g., 'http://localhost:9223')

    Returns:
        Port number (default: 9223 if not found)

    Examples:
        http://localhost:9223 → 9223
        http://192.168.1.100:9222 → 9222
        http://localhost → 9223 (default)

    🧵 Synth (Issue #38): Extract port for auto-launch
    """
    from urllib.parse import urlparse

    try:
        parsed = urlparse(cdp_url)
        if parsed.port:
            return parsed.port
        # No port specified, return default
        return 9223
    except Exception:
        # Parsing failed, return default
        return 9223


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


def get_network_cdp_url(port=9223):
    """
    Generate network-accessible CDP URL using local IP

    Args:
        port: CDP port number (default: 9223)

    Returns:
        str: Network CDP URL (e.g., 'http://192.168.1.100:9223'), or None if IP not detected

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


def check_chrome_cdp_running(port=9223):
    """
    Check if Chrome CDP is running on specified port

    Args:
        port: CDP port number (default: 9223)

    Returns:
        bool: True if Chrome CDP is accessible, False otherwise
    """
    try:
        response = requests.get(f'http://localhost:{port}/json/version', timeout=2)
        return response.status_code == 200
    except:
        return False


def launch_chrome_cdp(port=9223, bind_address='0.0.0.0'):
    """
    Launch Chrome with CDP enabled

    Args:
        port: CDP port number (default: 9223)
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

    # CDP URL configuration (Issue #11, Issue #38)
    print("\n🌐 Chrome DevTools Protocol (CDP) Configuration:")
    print("   CDP URL allows SimExp to connect to your authenticated Chrome browser.")
    print("   Leave empty to use default (localhost:9223)")
    print()
    print("   Examples:")
    print("   - 9223 (just port number - default)")
    print("   - localhost:9223 (default, for single-user setup)")
    print("   - http://192.168.1.100:9223 (connect to server on local network)")
    print("   - http://10.0.0.5:9223 (connect to remote server)")
    print()

    cdp_input = input("CDP URL [default: http://localhost:9223]: ").strip()
    if cdp_input:
        # Normalize the input (Issue #38: handle just port numbers like "9223")
        normalized_url = normalize_cdp_url(cdp_input)
        config['CDP_URL'] = normalized_url
        print(f"   ✓ CDP URL set to: {normalized_url}")
    else:
        config['CDP_URL'] = 'http://localhost:9223'
        print(f"   ✓ Using default: http://localhost:9223")

    with open(CONFIG_FILE, 'w') as config_file:
        yaml.safe_dump(config, config_file)
    print(f"\n✅ Configuration saved to {CONFIG_FILE}")

    # ═══════════════════════════════════════════════════════════════
    # AUTO-LAUNCH CHROME CDP - Issue #17, Issue #38
    # ♠️🌿🎸🧵 G.Music Assembly - One-command setup
    # ═══════════════════════════════════════════════════════════════

    # Extract port from configured CDP URL (Issue #38)
    configured_cdp = config.get('CDP_URL', 'http://localhost:9223')
    port = extract_port_from_url(configured_cdp)

    # Check if Chrome CDP is running on configured port
    if not check_chrome_cdp_running(port):
        print(f"\n🚀 Chrome CDP Setup (Port {port})")
        print("   SimExp needs Chrome running with remote debugging.")
        launch = input("   Launch Chrome automatically? [Y/n]: ").strip().lower()

        if launch != 'n':
            chrome_cmd = find_chrome_executable()
            if chrome_cmd:
                print(f"   🔍 Found Chrome: {chrome_cmd}")
                # Launch with network-wide access (0.0.0.0) as per Issue #36
                if launch_chrome_cdp(port=port, bind_address='0.0.0.0'):
                    print(f"   ✓ Chrome launched with CDP on port {port}")
                    print(f"   🌐 Network-wide access enabled")
                else:
                    print("   ⚠️  Could not launch Chrome automatically")
                    print("\n   Run manually:")
                    print(f"   {chrome_cmd} --remote-debugging-port={port} --remote-debugging-address=0.0.0.0 --user-data-dir=~/.chrome-simexp &")
            else:
                print("   ⚠️  Could not find Chrome/Chromium on your system")
                print("\n   Install Chrome and run:")
                print(f"   google-chrome --remote-debugging-port={port} --remote-debugging-address=0.0.0.0 --user-data-dir=~/.chrome-simexp &")
        else:
            print("\n   Run this command to start Chrome with CDP:")
            chrome_cmd = find_chrome_executable() or 'google-chrome'
            print(f"   {chrome_cmd} --remote-debugging-port={port} --remote-debugging-address=0.0.0.0 --user-data-dir=~/.chrome-simexp &")
    else:
        print(f"\n✓ Chrome CDP is already running on port {port}")

    # Show login instructions
    print("\n📝 IMPORTANT - Complete Setup:")
    print("   1. A Chrome window has opened (or is already open)")
    print("   2. Go to: https://app.simplenote.com")
    print("   3. Login with your Simplenote account")
    print("   4. Keep this Chrome window open while using SimExp")
    print()
    print("💡 Ready to test? Run: simexp session start")


def write_command(note_url, content=None, mode='append', headless=False, cdp_url=None):
    """
    Write content to Simplenote note via Playwright

    Args:
        note_url: Simplenote note URL
        content: Content to write (if None, read from stdin)
        mode: 'append' or 'replace'
        headless: Run browser in headless mode
        cdp_url: Chrome DevTools Protocol URL (uses priority chain if None)
    """
    import sys

    # Resolve CDP URL using priority chain (Issue #11)
    resolved_cdp = get_cdp_url(cdp_url)

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

    # Auto-launch Chrome if not running (Issue #38)
    port = extract_port_from_url(resolved_cdp)

    if not check_chrome_cdp_running(port):
        print(f"⚠️  Chrome CDP is not running on port {port}")
        print()
        response = input(f"Would you like to launch Chrome now? (y/n): ").strip().lower()

        if response == 'y' or response == 'yes':
            print()
            print("🚀 Launching Chrome with network-wide CDP access...")

            if launch_chrome_cdp(port=port, bind_address='0.0.0.0'):
                print("✅ Chrome launched successfully!")
                print()
                print("📋 Next steps:")
                print("  1. Go to https://app.simplenote.com in the Chrome window")
                print("  2. Login to Simplenote")
                print("  3. Press Enter to continue session creation")
                print()
                input("Press Enter when ready...")
            else:
                print("❌ Failed to launch Chrome")
                print()
                print(f"Please launch Chrome manually on port {port} and try again.")
                return
        else:
            print()
            print(f"❌ Chrome is required for session creation")
            print(f"Please launch Chrome on port {port} and try again:")
            print(f"  simexp browser launch --port {port} --network")
            return

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

def session_write_command(content=None, cdp_url=None):
    """
    Write to the current session's note using search

    Args:
        content: Content to write (if None, read from stdin)
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

    # Read from stdin if no content provided
    if content is None:
        print("📝 Reading content from stdin (Ctrl+D to finish)...")
        content = sys.stdin.read()
        if not content.strip():
            print("❌ No content provided")
            return

    print(f"♠️🌿🎸🧵 Writing to Session Note")
    print(f"🔮 Session: {session['session_id']}")
    print(f"📄 Content length: {len(content)} chars")

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


def session_status_command():
    """Show current session status"""
    import sys
    from .session_manager import get_session_directory

    # Get active session
    session = get_active_session()
    if not session:
        print("❌ No active session")
        print("💡 Run 'simexp session start' to create a new session")
        sys.exit(1)

    session_dir = session.get('_session_dir', get_session_directory())
    current_dir = os.getcwd()

    print(f"♠️🌿🎸🧵 Active Session Status")
    print()
    print(f"📁 Session file: {session_dir}/session.json" if session_dir else "📁 Session file: Unknown")
    print(f"🔮 Session ID: {session['session_id']}")
    print(f"🔑 Search Key: {session['search_key']}")
    print(f"🤝 AI Assistant: {session['ai_assistant']}")
    if session.get('issue_number'):
        print(f"🎯 Issue: #{session['issue_number']}")
    print(f"📅 Created: {session['created_at']}")
    print()
    print(f"📍 Current directory: {current_dir}")
    print(f"💡 Run 'simexp session info' for more details")


def session_clear_command():
    """Clear the current session"""
    clear_active_session()
    print("✅ Session cleared")


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


def session_unpublish_command(cdp_url=None):
    """Unpublish the current session's note"""
    import sys

    # Resolve CDP URL using priority chain (Issue #11)
    resolved_cdp = get_cdp_url(cdp_url)

    session = get_active_session()
    if not session:
        print("❌ No active session. Run 'simexp session start' first.")
        sys.exit(1)

    print(f"♠️🌿🎸🧵 Unpublishing Session Note")
    print(f"🔮 Session: {session['session_id']}")

    success = asyncio.run(unpublish_session_note(cdp_url=resolved_cdp))

    if success:
        print(f"\n✅ Note unpublished successfully!")
    else:
        print(f"\n❌ Unpublish failed")


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


def session_collab_remove_command(email, cdp_url=None):
    """Remove a collaborator from the current session's note"""
    import sys

    # Resolve CDP URL using priority chain (Issue #11)
    resolved_cdp = get_cdp_url(cdp_url)

    session = get_active_session()
    if not session:
        print("❌ No active session. Run 'simexp session start' first.")
        sys.exit(1)

    print(f"♠️🌿🎸🧵 Removing Collaborator from Session Note")
    print(f"🔮 Session: {session['session_id']}")
    print(f"👤 Collaborator: {email}")

    success = asyncio.run(remove_session_collaborator(email, cdp_url=resolved_cdp))

    if success:
        print(f"\n✅ Collaborator removed successfully!")
    else:
        print(f"\n❌ Failed to remove collaborator")


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


def browser_launch_command(port=9223, bind_address='127.0.0.1'):
    """
    Launch Chrome with CDP enabled

    Args:
        port: CDP port (default: 9223)
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
                description='Write content to a Simplenote note.',
                prog='simexp write')
            parser.add_argument('content', help='The content to write. If not provided, reads from stdin.')
            parser.add_argument('--note-url', default='https://app.simplenote.com/', help='The URL of the Simplenote note. Defaults to the main page, which will select the most recent note.')
            parser.add_argument('--mode', choices=['append', 'replace'], default='append', help='Write mode.')
            parser.add_argument('--headless', action='store_true', help='Run in headless mode.')
            parser.add_argument('--cdp-url', default=None, help='Chrome DevTools Protocol URL to connect to an existing browser.')
            
            args = parser.parse_args(sys.argv[2:])

            write_command(args.note_url, args.content, mode=args.mode, headless=args.headless, cdp_url=args.cdp_url)

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
                print("Usage: simexp session <subcommand>")
                print("\nSession Management:")
                print("  start [--ai <assistant>] [--issue <number>]  - Start new session")
                print("  list                                         - List all sessions (directory tree)")
                print("  info                                         - Show current session & directory context")
                print("  status                                       - Show session status")
                print("  clear                                        - Clear active session")
                print("\nSession Content:")
                print("  write <message>                              - Write to session note")
                print("  read                                         - Read session note")
                print("  add <file> [--heading <text>]                - Add file to session note")
                print("  open                                         - Open session note in browser")
                print("  url                                          - Print session note URL")
                print("\nSharing & Publishing (Issue #6):")
                print("  share <glyph|alias|group|email>              - Share with collaborator(s)")
                print("  publish                                      - Publish note (get public URL)")
                print("  unpublish                                    - Unpublish note (make private)")
                print("  collab add <email>                           - Add collaborator")
                print("  collab remove <email>                        - Remove collaborator")
                print("  collab list                                  - List all collaborators")
                sys.exit(1)

            subcommand = sys.argv[2]

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

                args = parser.parse_args(sys.argv[3:])
                session_write_command(content=args.content, cdp_url=args.cdp_url)

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

            elif subcommand == 'status':
                session_status_command()

            elif subcommand == 'clear':
                session_clear_command()

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

            elif subcommand == 'unpublish':
                import argparse
                parser = argparse.ArgumentParser(
                    description='Unpublish session note',
                    prog='simexp session unpublish')
                parser.add_argument('--cdp-url', default=None, help='Chrome DevTools Protocol URL')

                args = parser.parse_args(sys.argv[3:])
                session_unpublish_command(cdp_url=args.cdp_url)

            elif subcommand == 'collab':
                # Collaborator management subcommands
                if len(sys.argv) < 4:
                    print("Usage: simexp session collab <add|remove|list> [email]")
                    print("\nSubcommands:")
                    print("  add <email>     - Add collaborator by email")
                    print("  remove <email>  - Remove collaborator by email")
                    print("  list            - List all collaborators")
                    sys.exit(1)

                collab_action = sys.argv[3]

                if collab_action == 'add':
                    import argparse
                    parser = argparse.ArgumentParser(
                        description='Add collaborator',
                        prog='simexp session collab add')
                    parser.add_argument('email', help='Collaborator email address')
                    parser.add_argument('--cdp-url', default=None, help='Chrome DevTools Protocol URL')

                    args = parser.parse_args(sys.argv[4:])
                    session_collab_add_command(args.email, cdp_url=args.cdp_url)

                elif collab_action == 'remove':
                    import argparse
                    parser = argparse.ArgumentParser(
                        description='Remove collaborator',
                        prog='simexp session collab remove')
                    parser.add_argument('email', help='Collaborator email address')
                    parser.add_argument('--cdp-url', default=None, help='Chrome DevTools Protocol URL')

                    args = parser.parse_args(sys.argv[4:])
                    session_collab_remove_command(args.email, cdp_url=args.cdp_url)

                elif collab_action == 'list':
                    import argparse
                    parser = argparse.ArgumentParser(
                        description='List collaborators',
                        prog='simexp session collab list')
                    parser.add_argument('--cdp-url', default=None, help='Chrome DevTools Protocol URL')

                    args = parser.parse_args(sys.argv[4:])
                    session_collab_list_command(cdp_url=args.cdp_url)

                else:
                    print(f"Unknown collab action: {collab_action}")
                    print("Run 'simexp session collab' for usage information")
                    sys.exit(1)

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
                print("Usage: simexp browser <subcommand>")
                print("\nBrowser/CDP Commands:")
                print("  test                    - Test Chrome CDP connection and network binding")
                print("  launch [--network]      - Launch Chrome with CDP (--network for WiFi access)")
                sys.exit(1)

            subcommand = sys.argv[2]

            if subcommand == 'test':
                browser_test_command()

            elif subcommand == 'launch':
                import argparse
                parser = argparse.ArgumentParser(
                    description='Launch Chrome with CDP',
                    prog='simexp browser launch')
                parser.add_argument('--network', action='store_true', help='Enable network-wide access (0.0.0.0)')
                parser.add_argument('--port', type=int, default=9223, help='CDP port (default: 9223)')

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
            print("  simexp write <url> [msg]     - Write to Simplenote note")
            print("  simexp read <url>            - Read from Simplenote note")
            print("  simexp session <subcommand>  - Session management")
            print("  simexp browser <subcommand>  - Browser/CDP testing & management")
            print("  simexp help                  - Show this help")
            print("\nBrowser/CDP Commands (Issue #36):")
            print("  simexp browser test          - Test Chrome CDP connection & network binding")
            print("  simexp browser launch        - Launch Chrome with CDP (localhost-only)")
            print("  simexp browser launch --network  - Launch Chrome with network-wide access")
            print("\nSession Commands:")
            print("  simexp session start [--ai <assistant>] [--issue <number>]")
            print("                               - Start new session with Simplenote note")
            print("  simexp session list          - List all sessions across directory tree")
            print("  simexp session info          - Show current session & directory context")
            print("  simexp session status        - Show current session info")
            print("  simexp session clear         - Clear active session")
            print("  simexp session write <msg>   - Write to current session's note")
            print("  simexp session add <file>    - Add file content to session note")
            print("  simexp session read          - Read current session's note")
            print("  simexp session open          - Open session note in browser")
            print("  simexp session url           - Print session note URL")
            print("\nSharing Commands (Issue #6):")
            print("  simexp session share <glyph|alias|group|email>  - Share with collaborator(s)")
            print("  simexp session publish       - Publish note (get public URL)")
            print("  simexp session unpublish     - Unpublish note (make private)")
            print("  simexp session collab add <email>    - Add collaborator")
            print("  simexp session collab remove <email> - Remove collaborator")
            print("  simexp session collab list   - List all collaborators")
            print("\nChrome CDP Configuration (Issue #11):")
            print("  SimExp connects to Chrome via Chrome DevTools Protocol (CDP).")
            print("  CDP URL resolution priority:")
            print("    1. --cdp-url flag (highest priority)")
            print("    2. SIMEXP_CDP_URL environment variable")
            print("    3. CDP_URL in ~/.simexp/simexp.yaml")
            print("    4. http://localhost:9222 (default)")
            print("\n  Run 'simexp init' to configure CDP URL in config file.")
            print("  Use --cdp-url flag to override: simexp session write 'msg' --cdp-url http://server:9222")
            print("  Use env var: export SIMEXP_CDP_URL=http://192.168.1.100:9222")
            print("\nExamples:")
            print("  # Original features:")
            print("  simexp write https://app.simplenote.com/p/0ZqWsQ 'Hello!'")
            print("  echo 'Message' | simexp write https://app.simplenote.com/p/0ZqWsQ")
            print("  simexp read https://app.simplenote.com/p/0ZqWsQ")
            print("\n  # Session-aware notes:")
            print("  simexp session start --ai claude --issue 42")
            print("  simexp session write 'Implemented feature X'")
            print("  echo 'Progress update' | simexp session write")
            print("  simexp session status")
            print("  simexp session open")
            print("\n  # Multi-network CDP (Issue #11):")
            print("  simexp init                              # Configure CDP URL during setup")
            print("  export SIMEXP_CDP_URL=http://server:9222  # Use environment variable")
            print("  simexp session start --cdp-url http://192.168.1.100:9222  # Override with flag")
            print("\n  # Sharing & publishing:")
            print("  simexp session share ♠️                        # Share with Nyro (glyph)")
            print("  simexp session share nyro                     # Share with Nyro (alias)")
            print("  simexp session share assembly                 # Share with Assembly group")
            print("  simexp session share custom@example.com       # Share with custom email")
            print("  simexp session publish")
            print("  simexp session collab add jerry@example.com")
            print("  simexp session collab list")
            print("  simexp session unpublish")

        else:
            print(f"Unknown command: {command}")
            print("Run 'simexp help' for usage information")
            sys.exit(1)

    else:
        # No arguments - run normal extraction
        run_extraction()

if __name__ == "__main__":
    main()
