"""
Timestamp utility functions for SimExp
Integrates tlid package for flexible, human-readable timestamp generation

Issue #33: tlid Integration for temporal backbone
♠️ Nyro: Temporal glyph architecture for chronological storytelling
"""

import os
import yaml
from datetime import datetime


def get_timestamp(granularity=None, manual_override=None):
    """
    Generate timestamp using tlid package with configurable granularity

    Args:
        granularity (str): Time precision level
            - 'y': Year (YY)
            - 'm': Month (YYMM)
            - 'd': Day (YYMMDD)
            - 'h': Hour (YYMMDDHH)
            - 's': Second (YYMMDDHHMMSS) - DEFAULT
            - 'ms': Millisecond (YYMMDDHHMMSSmmm)
        manual_override (str): Manual timestamp string to use directly

    Returns:
        str: Formatted timestamp string

    Examples:
        get_timestamp()           # → '251023162145' (default: seconds)
        get_timestamp('ms')       # → '251023162145123' (milliseconds)
        get_timestamp('h')        # → '25102316' (hour)
        get_timestamp('d')        # → '251023' (day)
        get_timestamp(manual_override='2510231621')  # → '2510231621'
    """
    # If manual override provided, use it directly
    if manual_override:
        return str(manual_override)

    try:
        import tlid

        # Map granularity to tlid functions
        if granularity == 'ms':
            return tlid.get_milliseconds()
        elif granularity == 's' or granularity is None:
            return tlid.get_seconds()
        elif granularity == 'h':
            return tlid.get_hour()
        elif granularity == 'd':
            return tlid.get_day()
        elif granularity == 'm':
            return tlid.get_month()
        elif granularity == 'y':
            return tlid.get_year()
        else:
            # Unknown granularity, default to seconds
            return tlid.get_seconds()

    except ImportError:
        # Fallback if tlid not installed: use datetime
        return _fallback_timestamp(granularity)


def _fallback_timestamp(granularity=None):
    """
    Fallback timestamp generation if tlid is not available
    Uses datetime to generate TLID-compatible format

    Args:
        granularity (str): Time precision level

    Returns:
        str: Formatted timestamp string
    """
    now = datetime.now()

    # Format: YY = last 2 digits of year
    year = now.strftime('%y')
    month = now.strftime('%m')
    day = now.strftime('%d')
    hour = now.strftime('%H')
    minute = now.strftime('%M')
    second = now.strftime('%S')
    millisecond = now.strftime('%f')[:3]  # First 3 digits of microseconds

    if granularity == 'y':
        return year
    elif granularity == 'm':
        return f"{year}{month}"
    elif granularity == 'd':
        return f"{year}{month}{day}"
    elif granularity == 'h':
        return f"{year}{month}{day}{hour}"
    elif granularity == 'ms':
        return f"{year}{month}{day}{hour}{minute}{second}{millisecond}"
    else:  # 's' or None (default)
        return f"{year}{month}{day}{hour}{minute}{second}"


def get_default_granularity():
    """
    Get default timestamp granularity from config file

    Checks ~/.simexp/simexp.yaml for 'default_date_format' setting

    Returns:
        str: Default granularity ('s' if not configured)
    """
    config_file = os.path.expanduser('~/.simexp/simexp.yaml')

    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                if config and 'default_date_format' in config:
                    return config['default_date_format']
        except Exception:
            pass  # Fall through to default

    return 's'  # Default: seconds


def format_timestamped_entry(content, date_flag=None, prepend=False):
    """
    Format content with optional timestamp prefix

    Args:
        content (str): Content to format
        date_flag (str|bool): Timestamp granularity or True for default
        prepend (bool): Whether entry will be prepended (affects formatting)

    Returns:
        str: Formatted content with optional timestamp

    Examples:
        format_timestamped_entry("Test", date_flag='s')
        # → '[251023162145] Test'

        format_timestamped_entry("Test", date_flag=True)
        # → '[251023162145] Test' (uses default granularity)

        format_timestamped_entry("Test", date_flag=None)
        # → 'Test' (no timestamp)
    """
    if not date_flag:
        return content

    # Determine granularity
    if date_flag is True:
        granularity = get_default_granularity()
    elif isinstance(date_flag, str) and date_flag in ['y', 'm', 'd', 'h', 's', 'ms']:
        granularity = date_flag
    else:
        # Treat as manual override timestamp
        timestamp = str(date_flag)
        return f"[{timestamp}] {content}"

    # Generate timestamp with specified granularity
    timestamp = get_timestamp(granularity)
    return f"[{timestamp}] {content}"


def insert_after_metadata(note_content, entry):
    """
    Insert entry after HTML comment metadata block (if present)

    Handles both:
    - HTML comment metadata: <!-- session_metadata ... -->
    - Legacy YAML frontmatter: ---\\n...\\n---

    Args:
        note_content (str): Full note content
        entry (str): Entry to insert

    Returns:
        str: Modified note content with entry inserted after metadata

    Example:
        note = "<!-- session_metadata\\nsession_id: 123\\n-->\\n\\nExisting content"
        insert_after_metadata(note, "[timestamp] New entry")
        # → "<!-- session_metadata\\nsession_id: 123\\n-->\\n\\n[timestamp] New entry\\n\\nExisting content"
    """
    # Check for HTML comment metadata first (new format)
    if note_content.strip().startswith('<!--'):
        # Find the closing -->
        end_marker = note_content.find('-->')
        if end_marker != -1:
            # Insert after the --> and any following blank lines
            after_comment = end_marker + 3  # Length of '-->'

            # Skip newlines after the comment
            while after_comment < len(note_content) and note_content[after_comment] in '\n\r':
                after_comment += 1

            # Insert the entry
            return note_content[:after_comment] + f"{entry}\n\n" + note_content[after_comment:]

    # Check for legacy YAML frontmatter (for backward compatibility)
    lines = note_content.split('\n')
    if lines and lines[0].strip() == '---':
        # Find end of frontmatter
        end_marker_idx = None
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                end_marker_idx = i
                break

        if end_marker_idx is not None:
            # Insert after the closing --- marker
            insert_idx = end_marker_idx + 1

            # Skip any blank lines immediately after metadata
            while insert_idx < len(lines) and not lines[insert_idx].strip():
                insert_idx += 1

            # Insert the entry with blank line separation
            lines.insert(insert_idx, f"{entry}\n")
            return '\n'.join(lines)

    # No metadata block found, prepend to beginning
    return f"{entry}\n\n{note_content}"
