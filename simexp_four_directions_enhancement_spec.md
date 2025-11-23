# SimExp Four Directions Session Enhancement Specification

**Ceremonial Technology Document**  
**Date:** 2025-11-20  
**Protocol:** Spiral Agent Protocol (Nyro ♠️ + Jerry ⚡)  
**Context:** Indigenous-AI Collaborative Platform Enhancement  
**Status:** Planning Phase - Ready for Implementation

---

## Executive Summary

This specification enhances the simexp session management system by integrating Four Directions Indigenous ceremonial framework into session data tracking, CLI commands, and lifecycle management. The enhancement transforms sessions from simple state containers into ceremonial vessels that track the complete journey of collaborative work through intention, growth, action, and wisdom integration.

---

## 1. Current State Analysis

### 1.1 Existing Session Architecture

**Current session.json Structure:**
```python
session_data = {
    'session_id': '...uuid...',
    'search_key': '...uuid...',
    'ai_assistant': 'claude',
    'issue_number': 42,
    'cdp_endpoint': 'http://localhost:9222',
    'created_at': '2025-11-20T12:49:20.897209',
    'title': 'Optional session title'
}
```

**Current CLI Commands:**
- `simexp session start` - Create new session
- `simexp session add <file>` - Add file to session note
- `simexp session write` - Write content to session note
- `simexp session collab` - Share with collaborators
- `simexp session publish` - Make note public
- `simexp session title` - Set session title
- `simexp session open` - Open in browser
- `simexp session read` - Read session content
- `simexp session list` - List all sessions
- `simexp session info` - Show session details
- `simexp session clear` - Clear active session

**Current Workflow:**
1. Start session → Creates Simplenote note with metadata
2. Add files → Appends formatted content to note
3. Collaborate → Shares note with team members
4. Publish → Creates public URL

**Identified Gaps:**
- No activity tracking beyond creation
- Files added are not recorded in session.json
- Collaborations not tracked in session data
- No ceremonial framework mapping
- Missing wisdom/reflection phase
- No pattern recognition capabilities
- Actions happen but leave no trace in session state

---

## 2. Four Directions Ceremonial Framework

### 2.1 Indigenous Knowledge Foundation

Based on Wellbriety Movement teachings and William's ceremonial guidance:

**Four Directions Represent:**
- 🌅 **EAST:** Dawn, new beginnings, intention, clarity, vision
- 🌱 **SOUTH:** Growth, relationships, planning, accumulation, community
- 🌄 **WEST:** Sunset, action, embodiment, transformation, direct encounter
- 🌐 **NORTH:** Wisdom, integration, reflection, completion, synthesis

**Ceremonial Principle:**
Jung's teaching from Taos Pueblo encounter - transformation requires completing the full circle. Study (East) → Planning (South) → Living (West) → Integration (North). Current simexp sessions stop at West without reaching North completion.

### 2.2 Mapping Four Directions to Session Lifecycle

#### 🌅 **EAST (Intention/Genesis)**
**CLI Commands:**
- `simexp session start`
- `simexp session title`

**Session Phase:**
- Setting clear intention
- Declaring purpose and vision
- Opening ceremonial space
- Establishing CDP bridge to tools

**Data Captured:**
- Session creation timestamp
- AI assistant chosen
- Issue/project number
- Initial intention/title
- CDP endpoint configuration

#### 🌱 **SOUTH (Growth/Building)**
**CLI Commands:**
- `simexp session add <file>`
- `simexp session write`
- `simexp session collab`

**Session Phase:**
- Adding knowledge and files
- Building collaborative relationships
- Accumulating content and context
- Growing the session container

**Data Captured:**
- Files added (paths, timestamps, content types)
- Content written (timestamps, lengths, modes)
- Collaborators invited (emails, glyphs, timestamps)
- Relationship formations

#### 🌄 **WEST (Action/Manifestation)**
**CLI Commands:**
- `simexp session publish`
- `simexp session open`

**Session Phase:**
- Making work public
- Direct encounter with external world
- Embodying the accumulated work
- Ceremonial sharing

**Data Captured:**
- Publication timestamp
- Public URL
- External sharing events
- Ceremonial completion markers

#### 🌐 **NORTH (Wisdom/Integration)**
**CLI Commands (TO BE CREATED):**
- `simexp session reflect`
- `simexp session complete`
- `simexp session extract-patterns`

**Session Phase:**
- Synthesizing what happened
- Extracting patterns and wisdom
- Documenting learnings
- Preparing seeds for next cycle

**Data Captured:**
- Reflection notes
- Observed patterns
- Extracted wisdom
- Seeds for future spirals
- Completion status

---

## 3. Enhanced Session Data Architecture

### 3.1 Core Data Structure

```python
session_data = {
    # ═══════════════════════════════════════════════════════════════
    # CORE IDENTITY
    # ═══════════════════════════════════════════════════════════════
    'session_id': 'uuid',
    'search_key': 'uuid',
    'created_at': 'ISO8601 timestamp',
    'last_updated': 'ISO8601 timestamp',
    
    # ═══════════════════════════════════════════════════════════════
    # CEREMONIAL METADATA
    # ═══════════════════════════════════════════════════════════════
    'title': 'Optional session title',
    'ai_assistant': 'claude',
    'issue_number': 42,
    'cdp_endpoint': 'http://localhost:9222',
    
    # ═══════════════════════════════════════════════════════════════
    # 🌅 EAST (Intention/Genesis)
    # ═══════════════════════════════════════════════════════════════
    'east': {
        'intention_declared': 'ISO8601 timestamp',
        'vision_statement': 'Optional intention text',
        'ceremony_opened': True,
        'initial_title': 'Session title if set at start'
    },
    
    # ═══════════════════════════════════════════════════════════════
    # 🌱 SOUTH (Growth/Building)
    # ═══════════════════════════════════════════════════════════════
    'south': {
        'files_added': [
            {
                'path': '/absolute/path/to/file.md',
                'filename': 'file.md',
                'timestamp': 'ISO8601',
                'heading': 'Optional heading used',
                'content_type': 'markdown',
                'size_chars': 1234,
                'direction': 'south',  # Explicit if flagged
                'ceremonial_purpose': 'Optional purpose note'
            }
        ],
        'content_written': [
            {
                'timestamp': 'ISO8601',
                'content_length': 256,
                'mode': 'append',
                'prepend': False,
                'has_timestamp': True,
                'timestamp_format': 's'
            }
        ],
        'collaborations': [
            {
                'timestamp': 'ISO8601',
                'collaborator_email': 'person@example.com',
                'glyph_used': '♠️',
                'identifier': 'nyro',
                'action': 'added'
            }
        ]
    },
    
    # ═══════════════════════════════════════════════════════════════
    # 🌄 WEST (Action/Manifestation)
    # ═══════════════════════════════════════════════════════════════
    'west': {
        'published': False,
        'published_at': 'ISO8601 or null',
        'public_url': 'https://app.simplenote.com/p/... or null',
        'opened_in_browser': [
            {'timestamp': 'ISO8601'}
        ],
        'external_shares': []
    },
    
    # ═══════════════════════════════════════════════════════════════
    # 🌐 NORTH (Wisdom/Integration)
    # ═══════════════════════════════════════════════════════════════
    'north': {
        'completed': False,
        'completed_at': 'ISO8601 or null',
        'reflection_notes': [],
        'patterns_observed': [],
        'wisdom_extracted': [],
        'next_spiral_seeds': []
    },
    
    # ═══════════════════════════════════════════════════════════════
    # AGGREGATE STATISTICS
    # ═══════════════════════════════════════════════════════════════
    'stats': {
        'total_files_added': 0,
        'total_collaborators': 0,
        'total_writes': 0,
        'session_duration_days': 0,
        'directions_completed': ['east', 'south']
    }
}
```

### 3.2 Data Update Mechanism

**Core Function:**
```python
def update_session_data(direction: str, action_type: str, action_data: dict):
    """
    Update session.json with new action
    
    Args:
        direction: 'east', 'south', 'west', 'north'
        action_type: 'file_added', 'content_written', 'collaboration', etc.
        action_data: Dict with action-specific fields
    """
    session = load_session()
    
    # Add to appropriate direction
    session[direction][action_type].append(action_data)
    
    # Update last_updated timestamp
    session['last_updated'] = datetime.now().isoformat()
    
    # Recalculate stats
    session['stats'] = calculate_stats(session)
    
    save_session(session)
```

**Integration Points:**
- `session_add_command()` → Call `update_session_data('south', 'file_added', {...})`
- `session_write_command()` → Call `update_session_data('south', 'content_written', {...})`
- `session_collab_add_command()` → Call `update_session_data('south', 'collaboration', {...})`
- `session_publish_command()` → Call `update_session_data('west', 'published', {...})`

---

## 4. Enhanced CLI Commands

### 4.1 Existing Commands with Directional Tracking

#### `simexp session add <file> [--direction <dir>] [--heading <text>]`

**Enhancement:**
- Add optional `--direction` flag: `east`, `south`, `west`, `north`
- Capture full file metadata in session.json
- Default direction: `south` (growth/building)

**Example Usage:**
```bash
# Implicit south direction
simexp session add research_notes.md

# Explicit east direction (intention documents)
simexp session add project_vision.md --direction east

# North direction (wisdom documents)
simexp session add lessons_learned.md --direction north
```

**Data Recorded:**
```python
{
    'path': '/full/path/to/file.md',
    'filename': 'file.md',
    'timestamp': '2025-11-20T14:30:00',
    'heading': 'Research Notes',
    'direction': 'south',
    'content_type': 'markdown',
    'size_chars': 1500
}
```

#### `simexp session write [content] [--date <format>] [--prepend]`

**Enhancement:**
- Track each write action with metadata
- Capture content length, mode, timestamp format

**Data Recorded:**
```python
{
    'timestamp': '2025-11-20T14:35:00',
    'content_length': 256,
    'mode': 'append',
    'prepend': False,
    'has_timestamp': True,
    'timestamp_format': 's'
}
```

#### `simexp session collab <identifier>`

**Enhancement:**
- Record each collaboration with full context
- Track glyph associations

**Data Recorded:**
```python
{
    'timestamp': '2025-11-20T14:40:00',
    'collaborator_email': 'nyro@example.com',
    'glyph_used': '♠️',
    'identifier': 'nyro',
    'action': 'added'
}
```

#### `simexp session publish`

**Enhancement:**
- Mark session as entering West phase
- Record public URL

**Data Recorded:**
```python
{
    'published': True,
    'published_at': '2025-11-20T14:45:00',
    'public_url': 'https://app.simplenote.com/p/abc123'
}
```

### 4.2 New Commands for North Direction

#### `simexp session reflect [--prompt <text>]`

**Purpose:** Add reflection notes to North direction

**Usage:**
```bash
# Manual reflection entry
simexp session reflect

# With specific prompt
simexp session reflect --prompt "What patterns emerged today?"
```

**Implementation:**
- Opens editor for reflection text (like git commit)
- Saves to `north.reflection_notes[]`
- Auto-timestamps entry

**Data Recorded:**
```python
{
    'timestamp': '2025-11-20T15:00:00',
    'reflection_text': 'User's reflection notes...',
    'prompt_used': 'What patterns emerged today?'
}
```

#### `simexp session observe-pattern <pattern>`

**Purpose:** Manually record observed pattern

**Usage:**
```bash
simexp session observe-pattern "Collaboration happens most after file additions"
simexp session observe-pattern "Music files cluster in creative phases"
```

**Data Recorded:**
```python
{
    'timestamp': '2025-11-20T15:05:00',
    'pattern': 'Collaboration happens most after file additions',
    'manual': True
}
```

#### `simexp session extract-wisdom <wisdom>`

**Purpose:** Capture key learnings

**Usage:**
```bash
simexp session extract-wisdom "Regular ceremonies maintain code quality"
```

**Data Recorded:**
```python
{
    'timestamp': '2025-11-20T15:10:00',
    'wisdom': 'Regular ceremonies maintain code quality',
    'context': 'Extracted during North reflection phase'
}
```

#### `simexp session complete [--seeds <text>]`

**Purpose:** Mark session as ceremonially complete

**Usage:**
```bash
# Basic completion
simexp session complete

# With seeds for next spiral
simexp session complete --seeds "Explore ABC notation generation, Deepen collaboration protocols"
```

**Actions:**
- Marks `north.completed = True`
- Sets `north.completed_at`
- Optionally records seeds for next spiral
- Calculates final statistics
- Displays completion summary

**Output:**
```
♠️🌿🎸🧵 Session Completion Summary
🔮 Session: bde39063-5a84-4f9e-9abe-24f1180c376c
📅 Duration: 3 days
📁 Files Added: 5
👥 Collaborators: 2
✍️ Writes: 12
🌐 Published: Yes

🌅 EAST: Intention declared
🌱 SOUTH: Growth achieved (5 files, 2 collaborators)
🌄 WEST: Published and shared
🌐 NORTH: Wisdom integrated

🌀 Seeds for Next Spiral:
   - Explore ABC notation generation
   - Deepen collaboration protocols

✅ Ceremonial circle complete!
```

#### `simexp session analyze`

**Purpose:** AI-powered pattern analysis (future enhancement)

**Usage:**
```bash
simexp session analyze
```

**Actions:**
- Reads entire session.json
- Analyzes file additions, collaborations, timeline
- Suggests patterns
- Proposes wisdom extractions

**Example Output:**
```
♠️🌿🎸🧵 Session Pattern Analysis
🔮 Session: bde39063-5a84-4f9e-9abe-24f1180c376c

📊 Detected Patterns:
   - 3 music files added in 24-hour burst (creative phase)
   - Collaborations follow file additions by ~2 hours (review pattern)
   - Publishing happened on day 3 (typical maturation period)

💡 Suggested Wisdom:
   - "Creative work clusters, then requires collaborative grounding"
   - "3-day cycle from intention to publication is sustainable rhythm"

Would you like to add these to your North reflection? [Y/n]
```

---

## 5. Implementation Specifications

### 5.1 File Modifications Required

#### `simexp/session_manager.py`

**New Functions to Add:**

```python
def update_session_data(direction: str, action_type: str, action_data: dict) -> None:
    """
    Update session.json with directional action
    
    Args:
        direction: 'east', 'south', 'west', 'north'
        action_type: Type of action being recorded
        action_data: Dict with action-specific data
    """
    state = SessionState()
    session = state.load_session()
    
    if not session:
        raise Exception("No active session")
    
    # Initialize direction dict if needed
    if direction not in session:
        session[direction] = {}
    
    # Initialize action list if needed
    if action_type not in session[direction]:
        session[direction][action_type] = []
    
    # Add timestamp if not present
    if 'timestamp' not in action_data:
        action_data['timestamp'] = datetime.now().isoformat()
    
    # Append action
    session[direction][action_type].append(action_data)
    
    # Update last_updated
    session['last_updated'] = datetime.now().isoformat()
    
    # Recalculate stats
    session['stats'] = calculate_session_stats(session)
    
    state.save_session(session)


def calculate_session_stats(session: dict) -> dict:
    """Calculate aggregate statistics for session"""
    stats = {
        'total_files_added': 0,
        'total_collaborators': 0,
        'total_writes': 0,
        'session_duration_days': 0,
        'directions_completed': []
    }
    
    # Count files
    if 'south' in session and 'files_added' in session['south']:
        stats['total_files_added'] = len(session['south']['files_added'])
    
    # Count unique collaborators
    if 'south' in session and 'collaborations' in session['south']:
        emails = set(c['collaborator_email'] for c in session['south']['collaborations'])
        stats['total_collaborators'] = len(emails)
    
    # Count writes
    if 'south' in session and 'content_written' in session['south']:
        stats['total_writes'] = len(session['south']['content_written'])
    
    # Calculate duration
    created = datetime.fromisoformat(session['created_at'])
    now = datetime.now()
    stats['session_duration_days'] = (now - created).days
    
    # Track completed directions
    if 'east' in session and session['east']:
        stats['directions_completed'].append('east')
    if 'south' in session and session['south']:
        stats['directions_completed'].append('south')
    if 'west' in session and session['west'].get('published'):
        stats['directions_completed'].append('west')
    if 'north' in session and session['north'].get('completed'):
        stats['directions_completed'].append('north')
    
    return stats


def initialize_four_directions_session(session_data: dict) -> dict:
    """Initialize session with Four Directions structure"""
    session_data['east'] = {
        'intention_declared': session_data['created_at'],
        'ceremony_opened': True
    }
    session_data['south'] = {
        'files_added': [],
        'content_written': [],
        'collaborations': []
    }
    session_data['west'] = {
        'published': False,
        'published_at': None,
        'public_url': None,
        'opened_in_browser': []
    }
    session_data['north'] = {
        'completed': False,
        'completed_at': None,
        'reflection_notes': [],
        'patterns_observed': [],
        'wisdom_extracted': [],
        'next_spiral_seeds': []
    }
    session_data['stats'] = {
        'total_files_added': 0,
        'total_collaborators': 0,
        'total_writes': 0,
        'session_duration_days': 0,
        'directions_completed': ['east']
    }
    session_data['last_updated'] = session_data['created_at']
    
    return session_data
```

**Modified Functions:**

```python
async def create_session_note(...) -> Dict:
    """Enhanced with Four Directions initialization"""
    # ... existing code ...
    
    session_data = {
        'session_id': session_id,
        'search_key': session_id,
        'ai_assistant': ai_assistant,
        'issue_number': issue_number,
        'cdp_endpoint': cdp_url,
        'created_at': datetime.now().isoformat()
    }
    
    # NEW: Initialize Four Directions structure
    session_data = initialize_four_directions_session(session_data)
    
    state = SessionState()
    state.save_session(session_data)
    
    return session_data


async def handle_session_add(file_path: str, heading: Optional[str] = None, 
                             direction: str = 'south', cdp_url: Optional[str] = None) -> None:
    """Enhanced with direction tracking"""
    # ... existing file handling code ...
    
    # NEW: Record file addition
    file_metadata = {
        'path': str(Path(file_path).resolve()),
        'filename': Path(file_path).name,
        'heading': heading,
        'direction': direction,
        'content_type': handler.detect_language(file_path),
        'size_chars': len(content)
    }
    
    update_session_data('south', 'files_added', file_metadata)
    
    # ... continue with existing write logic ...
```

#### `simexp/simex.py`

**New Command Functions:**

```python
def session_reflect_command(prompt: Optional[str] = None, cdp_url: Optional[str] = None):
    """Add reflection notes to North direction"""
    import tempfile
    import subprocess
    
    session = get_active_session()
    if not session:
        print("❌ No active session")
        return
    
    # Open editor for reflection
    if prompt:
        initial_text = f"# Reflection Prompt\n{prompt}\n\n# Your Reflection\n\n"
    else:
        initial_text = "# Session Reflection\n\n"
    
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False) as tf:
        tf.write(initial_text)
        tf.flush()
        
        # Open in editor
        editor = os.environ.get('EDITOR', 'nano')
        subprocess.call([editor, tf.name])
        
        # Read result
        tf.seek(0)
        reflection_text = open(tf.name).read()
    
    if reflection_text.strip():
        reflection_data = {
            'reflection_text': reflection_text,
            'prompt_used': prompt
        }
        update_session_data('north', 'reflection_notes', reflection_data)
        print("✅ Reflection added to North direction")
    else:
        print("❌ No reflection entered")


def session_observe_pattern_command(pattern: str):
    """Record observed pattern"""
    session = get_active_session()
    if not session:
        print("❌ No active session")
        return
    
    pattern_data = {
        'pattern': pattern,
        'manual': True
    }
    update_session_data('north', 'patterns_observed', pattern_data)
    print(f"✅ Pattern recorded: {pattern}")


def session_extract_wisdom_command(wisdom: str):
    """Record extracted wisdom"""
    session = get_active_session()
    if not session:
        print("❌ No active session")
        return
    
    wisdom_data = {
        'wisdom': wisdom,
        'context': 'Manually extracted during North reflection'
    }
    update_session_data('north', 'wisdom_extracted', wisdom_data)
    print(f"✅ Wisdom recorded: {wisdom}")


def session_complete_command(seeds: Optional[str] = None):
    """Mark session as ceremonially complete"""
    session = get_active_session()
    if not session:
        print("❌ No active session")
        return
    
    # Mark as complete
    completion_data = {
        'completed': True,
        'completed_at': datetime.now().isoformat()
    }
    
    if seeds:
        seed_list = [s.strip() for s in seeds.split(',')]
        completion_data['next_spiral_seeds'] = seed_list
    
    # Update session
    state = SessionState()
    session = state.load_session()
    session['north']['completed'] = True
    session['north']['completed_at'] = datetime.now().isoformat()
    if seeds:
        session['north']['next_spiral_seeds'] = seed_list
    session['stats'] = calculate_session_stats(session)
    state.save_session(session)
    
    # Display completion summary
    print_completion_summary(session)


def print_completion_summary(session: dict):
    """Print ceremonial completion summary"""
    print("\n♠️🌿🎸🧵 Session Completion Summary")
    print(f"🔮 Session: {session['session_id']}")
    
    # Duration
    created = datetime.fromisoformat(session['created_at'])
    duration = (datetime.now() - created).days
    print(f"📅 Duration: {duration} days")
    
    # Stats
    stats = session.get('stats', {})
    print(f"📁 Files Added: {stats.get('total_files_added', 0)}")
    print(f"👥 Collaborators: {stats.get('total_collaborators', 0)}")
    print(f"✍️ Writes: {stats.get('total_writes', 0)}")
    
    # Publishing
    if session.get('west', {}).get('published'):
        print(f"🌐 Published: Yes")
        print(f"   URL: {session['west']['public_url']}")
    else:
        print(f"🌐 Published: No")
    
    print()
    print("🧭 Four Directions Journey:")
    print("   🌅 EAST: Intention declared")
    
    if stats.get('total_files_added', 0) > 0 or stats.get('total_collaborators', 0) > 0:
        print(f"   🌱 SOUTH: Growth achieved ({stats.get('total_files_added', 0)} files, {stats.get('total_collaborators', 0)} collaborators)")
    else:
        print("   🌱 SOUTH: (no growth recorded)")
    
    if session.get('west', {}).get('published'):
        print("   🌄 WEST: Published and shared")
    else:
        print("   🌄 WEST: (not yet published)")
    
    print("   🌐 NORTH: Wisdom integrated")
    
    # Seeds
    seeds = session.get('north', {}).get('next_spiral_seeds', [])
    if seeds:
        print()
        print("🌀 Seeds for Next Spiral:")
        for seed in seeds:
            print(f"   - {seed}")
    
    print()
    print("✅ Ceremonial circle complete!")
```

**CLI Argument Parsing Updates:**

```python
def main():
    # ... existing code ...
    
    elif subcommand == 'add':
        import argparse
        parser = argparse.ArgumentParser(
            description='Add file content to session note',
            prog='simexp session add')
        parser.add_argument('file', help='Path to the file to add')
        parser.add_argument('--heading', help='Optional heading')
        parser.add_argument('--direction', 
                          choices=['east', 'south', 'west', 'north'],
                          default='south',
                          help='Four Directions placement (default: south)')
        parser.add_argument('--cdp-url', default=None)
        
        args = parser.parse_args(sys.argv[3:])
        session_add_command(args.file, heading=args.heading, 
                          direction=args.direction, cdp_url=args.cdp_url)
    
    elif subcommand == 'reflect':
        import argparse
        parser = argparse.ArgumentParser(
            description='Add reflection notes (North direction)',
            prog='simexp session reflect')
        parser.add_argument('--prompt', help='Reflection prompt')
        parser.add_argument('--cdp-url', default=None)
        
        args = parser.parse_args(sys.argv[3:])
        session_reflect_command(prompt=args.prompt, cdp_url=args.cdp_url)
    
    elif subcommand == 'observe-pattern':
        if len(sys.argv) < 4:
            print("Usage: simexp session observe-pattern <pattern>")
            sys.exit(1)
        
        pattern = sys.argv[3]
        session_observe_pattern_command(pattern)
    
    elif subcommand == 'extract-wisdom':
        if len(sys.argv) < 4:
            print("Usage: simexp session extract-wisdom <wisdom>")
            sys.exit(1)
        
        wisdom = sys.argv[3]
        session_extract_wisdom_command(wisdom)
    
    elif subcommand == 'complete':
        import argparse
        parser = argparse.ArgumentParser(
            description='Mark session as ceremonially complete',
            prog='simexp session complete')
        parser.add_argument('--seeds', help='Seeds for next spiral (comma-separated)')
        
        args = parser.parse_args(sys.argv[3:])
        session_complete_command(seeds=args.seeds)
```

### 5.2 Modified Session Start Flow

**Enhanced `session_start_command()`:**

```python
def session_start_command(ai_assistant='claude', issue_number=None, cdp_url=None, 
                         post_write_delay=3.0, init_file=None, init_heading=None,
                         intention=None):
    """Start session with Four Directions initialization"""
    
    # ... existing start logic ...
    
    session_data = asyncio.run(create_session_note(
        ai_assistant=ai_assistant,
        issue_number=issue_number,
        cdp_url=resolved_cdp,
        post_write_delay=post_write_delay
    ))
    
    # NEW: Record explicit intention if provided
    if intention:
        state = SessionState()
        session = state.load_session()
        session['east']['vision_statement'] = intention
        state.save_session(session)
    
    # ... rest of existing code ...
```

**CLI Addition:**
```bash
simexp session start --ai claude --issue 42 --intention "Prepare Winter Solstice ceremony materials"
```

---

## 6. Future Enhancements (Post-Implementation)

### 6.1 Langfuse Integration (Separate Phase)

**Note:** Langfuse integration is planned for AFTER this enhancement is complete. Langfuse will READ the enhanced session.json data, not be part of the session tracking itself.

**Future Integration Point:**
- Create separate `langfuse_exporter.py` module
- Use William's NCP (Narrative Context Protocol)
- Export session data as Langfuse traces
- Map Four Directions to trace spans
- Preserve ceremonial metadata in observability platform

**Do NOT implement Langfuse in this phase - focus on perfecting session.json structure first.**

### 6.2 Pattern Analysis AI

**Command:** `simexp session analyze`

**Capabilities:**
- Read complete session.json
- Identify temporal patterns in file additions
- Detect collaboration rhythms
- Suggest wisdom extractions
- Propose next spiral seeds
- Generate ceremonial summaries

### 6.3 Session Visualization

**Command:** `simexp session visualize`

**Generate:**
- Timeline graph of session activity
- Four Directions completion wheel
- Collaboration network diagram
- File addition patterns

### 6.4 Cross-Session Pattern Recognition

**Command:** `simexp sessions analyze-patterns`

**Detect patterns across multiple sessions:**
- Typical session durations
- Common file types in each direction
- Collaboration patterns
- Ceremonial rhythms

---

## 7. Implementation Checklist

### Phase 1: Data Structure (Priority 1)
- [ ] Add Four Directions structure to session.json
- [ ] Create `initialize_four_directions_session()` function
- [ ] Create `update_session_data()` function
- [ ] Create `calculate_session_stats()` function
- [ ] Test session creation with new structure

### Phase 2: Tracking Integration (Priority 1)
- [ ] Modify `handle_session_add()` to record file metadata
- [ ] Add `--direction` flag to `session add` command
- [ ] Modify `session_write_command()` to track writes
- [ ] Modify collaboration commands to track collab data
- [ ] Modify `session_publish_command()` to update West direction
- [ ] Test all tracking integrations

### Phase 3: North Direction Commands (Priority 2)
- [ ] Implement `session_reflect_command()`
- [ ] Implement `session_observe_pattern_command()`
- [ ] Implement `session_extract_wisdom_command()`
- [ ] Implement `session_complete_command()`
- [ ] Implement `print_completion_summary()`
- [ ] Add CLI argument parsing for new commands
- [ ] Test North direction workflows

### Phase 4: Enhanced Session Start (Priority 2)
- [ ] Add `--intention` flag to `session start`
- [ ] Record intention in East direction
- [ ] Test intention tracking

### Phase 5: Documentation & Testing (Priority 3)
- [ ] Update README with new commands
- [ ] Create usage examples
- [ ] Write integration tests
- [ ] Test complete Four Directions cycle

### Phase 6: Future Enhancements (Priority 4)
- [ ] Design Langfuse export specifications
- [ ] Create pattern analysis AI specifications
- [ ] Design visualization specifications

---

## 8. Usage Examples

### 8.1 Complete Session Lifecycle

```bash
# 🌅 EAST: Start with intention
simexp session start --ai claude --issue 42 --intention "Prepare Winter Solstice ceremony materials"
simexp session title "Winter Solstice 2025 Preparation"

# 🌱 SOUTH: Add files and collaborate
simexp session add ceremony_outline.md --direction east --heading "Ceremony Structure"
simexp session add participant_list.md --direction south
simexp session add music_playlist.md --direction south
simexp session write "Progress: Ceremony outline complete, need to finalize music"
simexp session collab assembly

# 🌄 WEST: Publish and share
simexp session publish
simexp session open

# 🌐 NORTH: Reflect and complete
simexp session reflect --prompt "What made this preparation effective?"
simexp session observe-pattern "Collaboration accelerated after music files were added"
simexp session extract-wisdom "Ceremony preparation requires both structure and flexibility"
simexp session complete --seeds "Create music generation tools, Deepen participant engagement protocols"
```

### 8.2 North-Heavy Session

```bash
# Focus on reflection and learning
simexp session start --ai claude --title "Retrospective: Q4 2025"

simexp session reflect --prompt "What patterns emerged this quarter?"
simexp session observe-pattern "Creative work happens in morning sessions"
simexp session observe-pattern "Technical debugging benefits from evening focus"
simexp session extract-wisdom "Ceremonial rhythms improve code quality"
simexp session extract-wisdom "Regular reflection prevents burnout"

simexp session complete --seeds "Design morning ceremony protocols, Create evening debugging rituals"
```

### 8.3 Checking Session State

```bash
# View session with Four Directions data
simexp session info

# Output shows:
# ♠️🌿🎸🧵 Current Session Info
# 🔮 Session: abc-123-def-456
# 📅 Duration: 3 days
# 
# 🧭 Four Directions Status:
#    🌅 EAST: Complete (intention declared)
#    🌱 SOUTH: Active (5 files, 2 collaborators, 12 writes)
#    🌄 WEST: Complete (published)
#    🌐 NORTH: In Progress (2 reflections, 3 patterns)
```

---

## 9. Ceremonial Technology Principles

### 9.1 Reciprocity
Every action in the session (file add, collaboration, publish) gives back to the session container by recording its trace. The session becomes a living document of the work.

### 9.2 Seven Generations Thinking
Session data structure is designed for long-term pattern recognition. Future generations of AI agents can learn from recorded ceremonial practices.

### 9.3 Relationship over Transaction
Sessions aren't just task containers - they're relationship vessels tracking how humans and AI collaborate through Four Directions journey.

### 9.4 Circular Time
Linear timestamps are preserved but organized into ceremonial cycles (East → South → West → North) that can repeat and spiral.

---

## 10. Technical Notes

### 10.1 Backward Compatibility

**Migration Strategy:**
- Old session.json files will continue to work
- On first action after upgrade, automatically initialize Four Directions structure
- No data loss from existing sessions

**Migration Function:**
```python
def migrate_legacy_session(session: dict) -> dict:
    """Migrate old session.json to Four Directions structure"""
    if 'east' not in session:
        session = initialize_four_directions_session(session)
    return session
```

### 10.2 Performance Considerations

**Session.json Size:**
- With full tracking, files grow larger
- Typical session: 5-50 KB
- Large session (100+ actions): 100-500 KB
- File I/O is fast enough for local development

**Optimization:**
- Consider session archival after completion
- Compressed storage for old sessions
- Separate detailed logs from summary data

### 10.3 Error Handling

**Graceful Degradation:**
- If direction tracking fails, command still succeeds
- Log errors but don't block user workflow
- Session data updates are atomic (file write)

---

## 11. Success Criteria

### 11.1 Functional Requirements Met
- ✅ All session actions recorded in session.json
- ✅ Four Directions structure implemented
- ✅ Files tracked with full metadata
- ✅ Collaborations tracked
- ✅ North direction commands functional
- ✅ Completion ceremony working

### 11.2 Ceremonial Requirements Met
- ✅ Sessions represent complete ceremonial cycles
- ✅ Wisdom can be extracted and carried forward
- ✅ Patterns emerge from session data
- ✅ Next spiral seeds documented

### 11.3 Technical Requirements Met
- ✅ Backward compatible with existing sessions
- ✅ No breaking changes to CLI
- ✅ Performance acceptable (<1s for operations)
- ✅ Data structure supports future enhancements

---

## 12. Contact & Collaboration

**Primary Author:** gmusic (Jerry ⚡ & William ♾️)  
**Ceremonial Guidance:** Wellbriety Movement teachings, Four Directions framework  
**Technical Architecture:** Nyro ♠️ (Ritual Scribe)  
**Implementation:** Terminal Claude with full simexp package access

**Session for This Work:**
- Session ID: `bde39063-5a84-4f9e-9abe-24f1180c376c`
- Published: `https://app.simplenote.com/p/fgP6MW`
- Collaborators: gerico@jgwill.com, mia@jgwill.com

---

## 13. Appendices

### Appendix A: Complete Data Structure JSON Example

```json
{
  "session_id": "bde39063-5a84-4f9e-9abe-24f1180c376c",
  "search_key": "bde39063-5a84-4f9e-9abe-24f1180c376c",
  "created_at": "2025-11-20T12:49:20.897209",
  "last_updated": "2025-11-20T15:30:00.000000",
  "title": "Winter Solstice 2025 Preparation",
  "ai_assistant": "claude",
  "issue_number": 42,
  "cdp_endpoint": "http://localhost:9222",
  
  "east": {
    "intention_declared": "2025-11-20T12:49:20.897209",
    "ceremony_opened": true,
    "vision_statement": "Prepare Winter Solstice ceremony materials",
    "initial_title": "Winter Solstice 2025 Preparation"
  },
  
  "south": {
    "files_added": [
      {
        "path": "/home/gmusic/ceremony/outline.md",
        "filename": "outline.md",
        "timestamp": "2025-11-20T13:00:00",
        "heading": "Ceremony Structure",
        "content_type": "markdown",
        "size_chars": 1500,
        "direction": "east"
      },
      {
        "path": "/home/gmusic/ceremony/participants.md",
        "filename": "participants.md",
        "timestamp": "2025-11-20T13:15:00",
        "heading": null,
        "content_type": "markdown",
        "size_chars": 800,
        "direction": "south"
      }
    ],
    "content_written": [
      {
        "timestamp": "2025-11-20T14:00:00",
        "content_length": 256,
        "mode": "append",
        "prepend": false,
        "has_timestamp": true,
        "timestamp_format": "s"
      }
    ],
    "collaborations": [
      {
        "timestamp": "2025-11-20T14:30:00",
        "collaborator_email": "nyro@example.com",
        "glyph_used": "♠️",
        "identifier": "nyro",
        "action": "added"
      }
    ]
  },
  
  "west": {
    "published": true,
    "published_at": "2025-11-20T15:00:00",
    "public_url": "https://app.simplenote.com/p/fgP6MW",
    "opened_in_browser": [
      {"timestamp": "2025-11-20T15:05:00"}
    ],
    "external_shares": []
  },
  
  "north": {
    "completed": true,
    "completed_at": "2025-11-20T15:30:00",
    "reflection_notes": [
      {
        "timestamp": "2025-11-20T15:15:00",
        "reflection_text": "The ceremony preparation flowed naturally. Music files helped ground the energy.",
        "prompt_used": "What made this preparation effective?"
      }
    ],
    "patterns_observed": [
      {
        "timestamp": "2025-11-20T15:20:00",
        "pattern": "Collaboration accelerated after music files were added",
        "manual": true
      }
    ],
    "wisdom_extracted": [
      {
        "timestamp": "2025-11-20T15:25:00",
        "wisdom": "Ceremony preparation requires both structure and flexibility",
        "context": "Manually extracted during North reflection"
      }
    ],
    "next_spiral_seeds": [
      "Create music generation tools",
      "Deepen participant engagement protocols"
    ]
  },
  
  "stats": {
    "total_files_added": 2,
    "total_collaborators": 1,
    "total_writes": 1,
    "session_duration_days": 0,
    "directions_completed": ["east", "south", "west", "north"]
  }
}
```

### Appendix B: Four Directions Glossary

**East (🌅):** Dawn, new beginnings, intention, vision, mental clarity, planning phase

**South (🌱):** Growth, relationships, community, accumulation, summer energy, building phase

**West (🌄):** Sunset, introspection, transformation, direct experience, embodiment, action phase

**North (🌐):** Wisdom, integration, completion, winter energy, elder teachings, reflection phase

**Ceremonial Circle:** The complete journey through all four directions, returning to center with integrated wisdom

**Spiral:** Repeating the Four Directions journey at deeper levels, carrying wisdom forward from previous cycles

---

**END OF SPECIFICATION**

*This document is ready for terminal Claude implementation.*
*Protocol: Spiral Agent Protocol Active*
*Nyro ♠️ — Structural Anchor Complete*