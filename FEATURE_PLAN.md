# Feature Plan: Session-Aware Notes

This document outlines the implementation plan for the new "session-aware notes" feature in `simexp`.

## User Story

As a user, I want to be able to create a new Simplenote note for each of my terminal sessions, so that I can keep my work organized and easily accessible.

## Acceptance Criteria

*   A new `session` command is created in the `simexp` CLI.
*   The `session start` command generates a unique UUID for the session.
*   The `session start` command creates a new note in Simplenote.
*   The new note contains a YAML header with the session metadata (session_id, ai_assistant, agents, etc.).
*   The `session write` command writes to the note associated with the current session.
*   The `session read` command reads the content of the session note.
*   The `session open` command opens the session note in the browser.
*   The `session url` command prints the URL of the session note.
*   The `session status` command shows the current session ID and note URL.
*   The session state (session ID and note URL) is persisted locally, allowing the user to resume a session later.

## Implementation Plan

1.  **Session ID Generation:** We will use a standard UUID library to generate a unique ID for each session (e.g., `801e26b2-a656-4ce4-828e-cd8714672f26`).

2.  **New Note Creation:** We will use Playwright to create a new note in Simplenote. This will involve:
    *   Navigating to the main Simplenote page.
    *   Finding and clicking the "new note" button.
    *   Waiting for the new note to be created and getting its URL.

3.  **Metadata Header:** We will use a YAML-based format for the metadata header. The header will be written to the new note upon creation.

    ```yaml
    ---
    session_id: <UUID>
    ai_assistant: <gemini|claude>
    agents:
      - Jerry
      - Aureon
      - Nyro
      - JamAI
      - Synth
    issue_number: <issue_number>
    pr_number: null
    ---
    ```

4.  **New `session` Command Suite:** We will create a new `session` command in `simexp/simex.py` with the following sub-commands:
    *   `session start`: Creates a new session, a new note, and saves the session ID and note URL locally.
    *   `session write "My message"`: Writes to the current session's note.
    *   `session read`: Reads the content of the current session's note.
    *   `session open`: Opens the current session's note in the browser.
    *   `session url`: Prints the URL of the current session's note.
    *   `session status`: Shows the current session ID and note URL.

5.  **Local Session State:** We will create a new file, `.simexp/session.json`, to store the current session ID and note URL. This will allow the `session` commands to know which note to interact with. The file will look something like this:

    ```json
    {
      "session_id": "801e26b2-a656-4ce4-828e-cd8714672f26",
      "note_url": "https://app.simplenote.com/p/NOTE_ID"
    }
    ```

## Next Steps

1.  Create a GitHub issue for this feature using the information in this document.
2.  Provide the issue number to the AI assistant.
3.  The AI assistant will then create a new feature branch and begin the implementation.
