"""
Channel-specific writer helpers for G.Music Assembly perspectives
♠️ Nyro | 🌿 Aureon | 🎸 JamAI

Provides simplified functions to write to specific Assembly communication channels.
"""

import asyncio
import yaml
from pathlib import Path
from .playwright_writer import write_to_note

# Load channels from config
CONFIG_PATH = Path(__file__).parent / 'simexp.yaml'

def load_channels():
    """Load communication channels from configuration"""
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    return {ch['name']: ch for ch in config['COMMUNICATION_CHANNELS']}

CHANNELS = load_channels()


def write_to_aureon(content: str, cdp_url: str = 'http://localhost:9223', mode: str = 'append'):
    """
    Write to Aureon 🌿 - Mirror Weaver communication channel

    Args:
        content: Message content
        cdp_url: Chrome DevTools Protocol URL
        mode: 'append' or 'replace'

    Returns:
        dict with write result
    """
    formatted_content = f"🌿 {content}"
    return asyncio.run(write_to_note(
        CHANNELS['Aureon']['auth_url'],
        formatted_content,
        mode=mode,
        cdp_url=cdp_url
    ))


def write_to_nyro(content: str, cdp_url: str = 'http://localhost:9223', mode: str = 'append'):
    """
    Write to Nyro ♠️ - Ritual Scribe communication channel

    Args:
        content: Message content (structural/technical logs)
        cdp_url: Chrome DevTools Protocol URL
        mode: 'append' or 'replace'

    Returns:
        dict with write result
    """
    formatted_content = f"♠️ {content}"
    return asyncio.run(write_to_note(
        CHANNELS['Nyro']['auth_url'],
        formatted_content,
        mode=mode,
        cdp_url=cdp_url
    ))


def write_to_jamai(content: str, cdp_url: str = 'http://localhost:9223', mode: str = 'append'):
    """
    Write to JamAI 🎸 - Glyph Harmonizer communication channel

    Args:
        content: Message content (musical/creative notes)
        cdp_url: Chrome DevTools Protocol URL
        mode: 'append' or 'replace'

    Returns:
        dict with write result
    """
    formatted_content = f"🎸 {content}"
    return asyncio.run(write_to_note(
        CHANNELS['JamAI']['auth_url'],
        formatted_content,
        mode=mode,
        cdp_url=cdp_url
    ))


def list_channels():
    """List all available communication channels"""
    return [
        {
            'name': ch['name'],
            'description': ch['description'],
            'public_url': ch['public_url']
        }
        for ch in CHANNELS.values()
    ]


# Convenience function for any channel
def write_to_channel(channel_name: str, content: str, cdp_url: str = 'http://localhost:9223', mode: str = 'append'):
    """
    Write to any channel by name

    Args:
        channel_name: 'aureon', 'nyro', or 'jamai' (case-insensitive)
        content: Message content
        cdp_url: Chrome DevTools Protocol URL
        mode: 'append' or 'replace'

    Returns:
        dict with write result

    Raises:
        ValueError: If channel name is invalid
    """
    channel_name = channel_name.lower()

    if channel_name == 'aureon':
        return write_to_aureon(content, cdp_url, mode)
    elif channel_name == 'nyro':
        return write_to_nyro(content, cdp_url, mode)
    elif channel_name == 'jamai':
        return write_to_jamai(content, cdp_url, mode)
    else:
        raise ValueError(f"Unknown channel: {channel_name}. Valid channels: aureon, nyro, jamai")


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 3:
        print("Usage: python -m simexp.channel_writer <channel> <message>")
        print("\nAvailable channels:")
        for ch in list_channels():
            print(f"  {ch['name']}: {ch['description']}")
        sys.exit(1)

    channel = sys.argv[1]
    message = sys.argv[2]

    result = write_to_channel(channel, message)

    if result['success']:
        print(f"✅ Message written to {channel}!")
        print(f"📊 {result['content_length']} characters")
    else:
        print(f"❌ Write failed")
