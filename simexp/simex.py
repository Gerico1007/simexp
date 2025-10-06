import os
import requests
from datetime import datetime
from .simfetcher import fetch_content
from .processor import process_content
from .archiver import save_as_markdown
import yaml
from .imp_clip import update_sources_from_clipboard, is_clipboard_content_valid
import asyncio
from .playwright_writer import write_to_note, read_from_note

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'simexp.yaml')  # Add this line to set the absolute path for the config file

def init_config():
    config = {
        'BASE_PATH': input("Enter the base path for saving content: "),
        'SOURCES': []
    }
    while True:
        url = input("Enter source URL (or 'done' to finish): ")
        if url.lower() == 'done':
            break
        filename = input("Enter filename for this source: ")
        config['SOURCES'].append({'url': url, 'filename': filename})

    with open(CONFIG_FILE, 'w') as config_file:
        yaml.safe_dump(config, config_file)
    print("Configuration saved to simexp.yaml")


def write_command(note_url, content=None, mode='append', headless=False):
    """
    Write content to Simplenote note via Playwright

    Args:
        note_url: Simplenote note URL
        content: Content to write (if None, read from stdin)
        mode: 'append' or 'replace'
        headless: Run browser in headless mode
    """
    import sys

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
        debug=True
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

def main():
    # Update sources from clipboard
    update_sources_from_clipboard()

    # Load configuration from YAML file
    config_path = CONFIG_FILE
    if not os.path.exists(config_path):
        print(f"Configuration file '{config_path}' not found. Please run 'simexp init' to create it.")
        return

    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)

    # Check if clipboard content is valid
    if not is_clipboard_content_valid():
        print("Invalid clipboard content. Proceeding with existing websites from configuration.")
        sources = config['SOURCES']
    else:
        sources = config['CLIPBOARD_SOURCES']

    base_path = config['BASE_PATH']

    # Create a folder for the current date
    current_date = datetime.now().strftime('%Y%m%d')
    daily_folder = os.path.join(base_path, current_date)
    os.makedirs(daily_folder, exist_ok=True)

    # Fetch, process, and save content for each source
    for source in sources:
        url = source['url']
        filename = source['filename']
        raw_content = fetch_content(url)
        title, cleaned_content = process_content(raw_content)
        save_as_markdown(title, cleaned_content, filename)

if __name__ == "__main__":
    import sys

    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'init':
            init_config()

        elif command == 'write':
            # Usage: simexp write <note_url> [content]
            if len(sys.argv) < 3:
                print("Usage: simexp write <note_url> [content]")
                print("If content not provided, will read from stdin")
                sys.exit(1)

            note_url = sys.argv[2]
            content = sys.argv[3] if len(sys.argv) > 3 else None
            write_command(note_url, content, mode='append', headless=False)

        elif command == 'read':
            # Usage: simexp read <note_url>
            if len(sys.argv) < 3:
                print("Usage: simexp read <note_url>")
                sys.exit(1)

            note_url = sys.argv[2]
            read_command(note_url, headless=True)

        elif command == 'gdocs-write':
            # Usage: simexp gdocs-write <doc_id> <content> [credentials_path]
            if len(sys.argv) < 4:
                print("Usage: simexp gdocs-write <document_id> <content> [credentials_path]")
                print("If credentials_path not provided, defaults to ./credentials/service-account.json")
                sys.exit(1)

            from .googledocs_writer import write_to_googledoc

            doc_id = sys.argv[2]
            content = sys.argv[3]
            creds_path = sys.argv[4] if len(sys.argv) > 4 else './credentials/service-account.json'

            print(f"♠️🌿🎸🧵 SimExp Google Docs Write Mode")
            print(f"📄 Document ID: {doc_id}")
            print(f"🔑 Credentials: {creds_path}")

            result = write_to_googledoc(doc_id, content, creds_path, mode='append')

            if result.get('success'):
                print(f"\n✅ Write successful!")
                print(f"📊 Written: {result.get('content_length', 'Unknown')} characters")
                print(f"📝 Preview: {result.get('preview', '')}")
            else:
                print(f"\n❌ Write failed: {result.get('error', 'Unknown error')}")
                sys.exit(1)

        elif command == 'gdocs-read':
            # Usage: simexp gdocs-read <doc_id> [credentials_path]
            if len(sys.argv) < 3:
                print("Usage: simexp gdocs-read <document_id> [credentials_path]")
                print("If credentials_path not provided, defaults to ./credentials/service-account.json")
                sys.exit(1)

            from .googledocs_writer import read_from_googledoc

            doc_id = sys.argv[2]
            creds_path = sys.argv[3] if len(sys.argv) > 3 else './credentials/service-account.json'

            print(f"♠️🌿🎸🧵 SimExp Google Docs Read Mode")
            print(f"📄 Document ID: {doc_id}")
            print(f"🔑 Credentials: {creds_path}")

            content = read_from_googledoc(doc_id, creds_path)

            print(f"\n📖 Content ({len(content)} chars):")
            print("=" * 60)
            print(content)
            print("=" * 60)

        elif command == 'channel':
            # Usage: simexp channel <channel_name> <message>
            if len(sys.argv) < 4:
                from .channel_writer import list_channels

                print("Usage: simexp channel <channel_name> <message>")
                print("\nAvailable channels:")
                for ch in list_channels():
                    print(f"  {ch['name']} ({ch['provider']}): {ch['description']}")
                sys.exit(1)

            from .channel_writer import write_to_channel

            channel_name = sys.argv[2].lower()
            content = sys.argv[3]

            print(f"♠️🌿🎸🧵 Writing to {channel_name} channel...")

            result = write_to_channel(channel_name, content)

            if result.get('success'):
                print(f"✅ Message written to {channel_name}!")
                print(f"📊 {result.get('content_length', 'Unknown')} characters")
            else:
                print(f"❌ Write failed: {result.get('error', 'Unknown error')}")
                sys.exit(1)

        elif command == 'help' or command == '--help' or command == '-h':
            print("♠️🌿🎸🧵 SimExp - Multi-Provider Content Extractor & Writer")
            print("\nCommands:")
            print("  simexp                           - Run extraction from clipboard/config")
            print("  simexp init                      - Initialize configuration")
            print("  simexp write <url> [msg]         - Write to Simplenote note")
            print("  simexp read <url>                - Read from Simplenote note")
            print("  simexp gdocs-write <id> <msg>    - Write to Google Docs document")
            print("  simexp gdocs-read <id>           - Read from Google Docs document")
            print("  simexp channel <name> <msg>      - Write to Assembly channel (any provider)")
            print("  simexp help                      - Show this help")
            print("\nExamples:")
            print("  # Simplenote")
            print("  simexp write https://app.simplenote.com/p/0ZqWsQ 'Hello!'")
            print("  simexp read https://app.simplenote.com/p/0ZqWsQ")
            print()
            print("  # Google Docs")
            print("  simexp gdocs-write 1abc123xyz 'Message' ./credentials/service-account.json")
            print("  simexp gdocs-read 1abc123xyz")
            print()
            print("  # Multi-Provider Channels")
            print("  simexp channel aureon 'Emotional reflection'")
            print("  simexp channel nyro 'Structural insight'")
            print("  simexp channel jamai 'Musical encoding'")

        else:
            print(f"Unknown command: {command}")
            print("Run 'simexp help' for usage information")
            sys.exit(1)

    else:
        # No arguments - run normal extraction
        main()