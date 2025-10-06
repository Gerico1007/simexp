"""
Multi-Provider Channel Writer for G.Music Assembly
Supports Simplenote (browser) and Google Docs (API) backends

♠️ Nyro | 🌿 Aureon | 🎸 JamAI

Provides unified interface for writing to different communication channels
regardless of underlying provider (Simplenote or Google Docs).
"""

import asyncio
import yaml
import logging
from pathlib import Path
from typing import Literal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load channels from config
CONFIG_PATH = Path(__file__).parent / 'simexp.yaml'


def load_channels():
    """Load communication channels from configuration"""
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    return {ch['name']: ch for ch in config.get('COMMUNICATION_CHANNELS', [])}


CHANNELS = load_channels()


def write_to_channel(
    channel_name: str,
    content: str,
    mode: str = 'append',
    cdp_url: str = 'http://localhost:9223'
) -> dict:
    """
    Write to any channel by name - automatically routes to correct provider

    Args:
        channel_name: 'aureon', 'nyro', 'jamai', etc. (case-insensitive)
        content: Message content
        mode: 'append' or 'replace'
        cdp_url: Chrome DevTools Protocol URL (for Simplenote provider)

    Returns:
        dict with write result

    Raises:
        ValueError: If channel name is invalid or provider unsupported
    """
    channel_name_key = channel_name.capitalize()

    if channel_name_key not in CHANNELS:
        raise ValueError(
            f"Unknown channel: {channel_name}. "
            f"Valid channels: {', '.join(CHANNELS.keys())}"
        )

    channel = CHANNELS[channel_name_key]
    provider = channel.get('provider', 'simplenote').lower()

    # Add perspective marker
    markers = {
        'aureon': '🌿',
        'nyro': '♠️',
        'jamai': '🎸'
    }
    marker = markers.get(channel_name.lower(), '')
    formatted_content = f"{marker} {content}" if marker else content

    logger.info(f"✍️  Writing to {channel_name} ({provider} provider)...")

    # Route to appropriate provider
    if provider == 'simplenote':
        return _write_to_simplenote(channel, formatted_content, mode, cdp_url)
    elif provider == 'googledocs':
        return _write_to_googledocs(channel, formatted_content, mode)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def _write_to_simplenote(
    channel: dict,
    content: str,
    mode: str,
    cdp_url: str
) -> dict:
    """
    Write to Simplenote using Playwright browser automation

    Args:
        channel: Channel configuration dict
        content: Message content (with marker)
        mode: 'append' or 'replace'
        cdp_url: Chrome DevTools Protocol URL

    Returns:
        dict with write result
    """
    from .playwright_writer import write_to_note

    note_url = channel.get('auth_url', 'https://app.simplenote.com')

    return asyncio.run(write_to_note(
        note_url=note_url,
        content=content,
        mode=mode,
        cdp_url=cdp_url
    ))


def _write_to_googledocs(
    channel: dict,
    content: str,
    mode: str
) -> dict:
    """
    Write to Google Docs using REST API

    Args:
        channel: Channel configuration dict
        content: Message content (with marker)
        mode: 'append' or 'replace'

    Returns:
        dict with write result
    """
    from .googledocs_writer import write_to_googledoc

    document_id = channel.get('document_id')
    credentials_path = channel.get('credentials_path', './credentials/service-account.json')

    if not document_id:
        raise ValueError(f"Channel {channel['name']} missing 'document_id' field")

    return write_to_googledoc(
        document_id=document_id,
        content=content,
        credentials_path=credentials_path,
        mode=mode
    )


def read_from_channel(
    channel_name: str,
    cdp_url: str = 'http://localhost:9223'
) -> str:
    """
    Read content from any channel - automatically routes to correct provider

    Args:
        channel_name: 'aureon', 'nyro', 'jamai', etc.
        cdp_url: Chrome DevTools Protocol URL (for Simplenote)

    Returns:
        Channel content as string
    """
    channel_name_key = channel_name.capitalize()

    if channel_name_key not in CHANNELS:
        raise ValueError(
            f"Unknown channel: {channel_name}. "
            f"Valid channels: {', '.join(CHANNELS.keys())}"
        )

    channel = CHANNELS[channel_name_key]
    provider = channel.get('provider', 'simplenote').lower()

    logger.info(f"📖 Reading from {channel_name} ({provider} provider)...")

    # Route to appropriate provider
    if provider == 'simplenote':
        return _read_from_simplenote(channel, cdp_url)
    elif provider == 'googledocs':
        return _read_from_googledocs(channel)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def _read_from_simplenote(channel: dict, cdp_url: str) -> str:
    """Read from Simplenote using Playwright"""
    from .playwright_writer import read_from_note

    note_url = channel.get('auth_url', 'https://app.simplenote.com')

    return asyncio.run(read_from_note(
        note_url=note_url,
        cdp_url=cdp_url
    ))


def _read_from_googledocs(channel: dict) -> str:
    """Read from Google Docs using REST API"""
    from .googledocs_writer import read_from_googledoc

    document_id = channel.get('document_id')
    credentials_path = channel.get('credentials_path', './credentials/service-account.json')

    if not document_id:
        raise ValueError(f"Channel {channel['name']} missing 'document_id' field")

    return read_from_googledoc(
        document_id=document_id,
        credentials_path=credentials_path
    )


def list_channels():
    """List all available communication channels with their providers"""
    return [
        {
            'name': ch['name'],
            'provider': ch.get('provider', 'simplenote'),
            'description': ch.get('description', 'No description'),
        }
        for ch in CHANNELS.values()
    ]


# Convenience functions for specific channels
def write_to_aureon(
    content: str,
    mode: str = 'append',
    cdp_url: str = 'http://localhost:9223'
) -> dict:
    """
    Write to Aureon 🌿 channel

    Automatically routes to configured provider (Simplenote or Google Docs)
    """
    return write_to_channel('aureon', content, mode, cdp_url)


def write_to_nyro(
    content: str,
    mode: str = 'append',
    cdp_url: str = 'http://localhost:9223'
) -> dict:
    """
    Write to Nyro ♠️ channel

    Automatically routes to configured provider (Simplenote or Google Docs)
    """
    return write_to_channel('nyro', content, mode, cdp_url)


def write_to_jamai(
    content: str,
    mode: str = 'append',
    cdp_url: str = 'http://localhost:9223'
) -> dict:
    """
    Write to JamAI 🎸 channel

    Automatically routes to configured provider (Simplenote or Google Docs)
    """
    return write_to_channel('jamai', content, mode, cdp_url)


# CLI interface for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python -m simexp.channel_writer <channel> <message>")
        print("\nAvailable channels:")
        for ch in list_channels():
            print(f"  {ch['name']} ({ch['provider']}): {ch['description']}")
        sys.exit(1)

    channel = sys.argv[1]
    message = sys.argv[2]

    result = write_to_channel(channel, message)

    if result.get('success'):
        print(f"✅ Message written to {channel}!")
        print(f"📊 {result.get('content_length', 'Unknown')} characters")
    else:
        print(f"❌ Write failed: {result.get('error', 'Unknown error')}")
