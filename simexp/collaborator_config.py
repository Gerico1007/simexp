"""
SimExp Collaborator Configuration
Manages glyph-based collaborator mappings for quick sharing

♠️🌿🎸🧵 G.Music Assembly - Glyph Sharing Feature
"""

import os
import yaml
from typing import List, Optional, Dict

# Config file location
CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.simexp')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'collaborators.yaml')

# Fallback: also check in project directory
PROJECT_CONFIG = os.path.join(os.path.dirname(__file__), '..', '.simexp', 'collaborators.yaml')


def load_collaborators_config() -> Dict:
    """
    Load collaborators configuration from YAML file

    Checks in order:
    1. ~/.simexp/collaborators.yaml (user home)
    2. <project>/.simexp/collaborators.yaml (project dir)

    Returns:
        Dict with collaborators, aliases, and groups
    """
    # Try user home first
    if os.path.exists(CONFIG_FILE):
        config_path = CONFIG_FILE
    # Fall back to project directory
    elif os.path.exists(PROJECT_CONFIG):
        config_path = PROJECT_CONFIG
    else:
        # Return empty config if no file found
        return {
            'collaborators': {},
            'aliases': {},
            'groups': {}
        }

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config or {'collaborators': {}, 'aliases': {}, 'groups': {}}
    except Exception as e:
        print(f"⚠️  Error loading collaborators config: {e}")
        return {
            'collaborators': {},
            'aliases': {},
            'groups': {}
        }


def resolve_collaborator(identifier: str, debug: bool = False) -> Optional[List[str]]:
    """
    Resolve a glyph, alias, group, or email to email address(es)

    Args:
        identifier: Can be:
            - Glyph: "♠️", "🌿", "🎸", "⚡", "🧠"
            - Alias: "nyro", "aureon", "jamai", "jerry", "mia"
            - Group: "assembly", "all", "perspectives"
            - Email: "someone@example.com"
        debug: Print resolution steps

    Returns:
        List of email addresses, or None if not found

    Examples:
        resolve_collaborator("♠️")        → ["nyro@jgwill.com"]
        resolve_collaborator("nyro")      → ["nyro@jgwill.com"]
        resolve_collaborator("assembly")  → ["nyro@jgwill.com", "aureon@jgwill.com", "jamai@jgwill.com"]
        resolve_collaborator("custom@example.com") → ["custom@example.com"]
    """
    config = load_collaborators_config()

    if debug:
        print(f"🔍 Resolving identifier: {identifier}")

    # Step 1: Check if it's a direct email address
    if '@' in identifier:
        if debug:
            print(f"✅ Recognized as email address")
        return [identifier]

    # Step 2: Check if it's a glyph (direct collaborator)
    if identifier in config.get('collaborators', {}):
        email = config['collaborators'][identifier]['email']
        name = config['collaborators'][identifier]['name']
        if debug:
            print(f"✅ Found glyph {identifier} → {name} ({email})")
        return [email]

    # Step 3: Check if it's an alias (maps to glyph)
    if identifier in config.get('aliases', {}):
        glyph = config['aliases'][identifier]
        if debug:
            print(f"✅ Found alias '{identifier}' → glyph {glyph}")
        # Recursively resolve the glyph
        return resolve_collaborator(glyph, debug=debug)

    # Step 4: Check if it's a group (maps to multiple glyphs)
    if identifier in config.get('groups', {}):
        glyphs = config['groups'][identifier]
        if debug:
            print(f"✅ Found group '{identifier}' with {len(glyphs)} members")
        # Resolve each glyph in the group
        emails = []
        for glyph in glyphs:
            resolved = resolve_collaborator(glyph, debug=False)  # Don't spam debug for each
            if resolved:
                emails.extend(resolved)
        if debug:
            print(f"✅ Resolved group to {len(emails)} email(s): {', '.join(emails)}")
        return emails if emails else None

    # Step 5: Not found
    if debug:
        print(f"❌ Could not resolve '{identifier}'")
        print(f"💡 Available options:")
        print(f"   Glyphs: {', '.join(config.get('collaborators', {}).keys())}")
        print(f"   Aliases: {', '.join(config.get('aliases', {}).keys())}")
        print(f"   Groups: {', '.join(config.get('groups', {}).keys())}")

    return None


def list_available_collaborators(show_details: bool = True):
    """
    Print all available collaborators, aliases, and groups

    Args:
        show_details: Show detailed info (name, role) or just identifiers
    """
    config = load_collaborators_config()

    print("♠️🌿🎸🧵 Available Collaborators:")
    print()

    # Glyphs
    print("📋 Glyphs:")
    for glyph, info in config.get('collaborators', {}).items():
        if show_details:
            print(f"  {glyph}  {info['name']:<10} ({info['email']})")
            print(f"      {info['role']}")
        else:
            print(f"  {glyph}  {info['name']} - {info['email']}")
    print()

    # Aliases
    if config.get('aliases'):
        print("🔤 Aliases:")
        for alias, glyph in config.get('aliases', {}).items():
            collaborator_name = config['collaborators'][glyph]['name']
            print(f"  {alias:<12} → {glyph} {collaborator_name}")
        print()

    # Groups
    if config.get('groups'):
        print("👥 Groups:")
        for group_name, glyphs in config.get('groups', {}).items():
            # Resolve to names
            names = [config['collaborators'][g]['name'] for g in glyphs if g in config['collaborators']]
            print(f"  {group_name:<12} → {', '.join(names)} ({len(glyphs)} members)")
        print()

    print("💡 Usage: simexp session share <glyph|alias|group|email>")


def get_collaborator_info(identifier: str) -> Optional[Dict]:
    """
    Get detailed info about a collaborator

    Args:
        identifier: Glyph, alias, or email

    Returns:
        Dict with name, email, role, description or None
    """
    config = load_collaborators_config()

    # Resolve alias to glyph if needed
    if identifier in config.get('aliases', {}):
        identifier = config['aliases'][identifier]

    # Get collaborator info
    if identifier in config.get('collaborators', {}):
        return config['collaborators'][identifier]

    return None
