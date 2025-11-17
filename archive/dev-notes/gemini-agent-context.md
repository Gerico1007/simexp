# SimExp Gemini Agent Context

This document provides context for the Gemini agent to effectively assist with the `SimExp` project.

## Project Overview

`SimExp` is a Python-based command-line tool that functions as a "Multi-Provider Content Writer & Extractor" for Simplenote and Google Docs. It enables bidirectional communication between the terminal and these cloud-based services.

The project is structured as a Python package with a `setup.py` file and a command-line interface (CLI) defined in `simexp/simex.py`.

### Core Features

*   **Content Extraction:** Fetches content from public Simplenote URLs, processes it, and saves it as Markdown.
*   **Content Writing:**
    *   **Simplenote:** Writes content to Simplenote notes using browser automation powered by Playwright.
    *   **Google Docs:** Writes content to Google Docs using the Google Docs API for faster, direct communication.
*   **Multi-Provider Channels:** The `simexp.yaml` configuration file allows defining "channels" that can point to either a Simplenote note or a Google Doc, enabling flexible output destinations.

### Core Technologies

*   **Python:** The primary programming language.
*   **Playwright:** Used for browser automation to interact with Simplenote.
*   **Google API Python Client:** Used for interacting with the Google Docs API.
*   **PyYAML:** For parsing the `simexp.yaml` configuration file.
*   **Beautiful Soup:** For processing HTML content during extraction.
*   **Pyperclip:** For reading from and writing to the system clipboard.

## Building and Running

### Installation

1.  **Install Python dependencies:**
    ```bash
    pip install playwright beautifulsoup4 pyyaml requests google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
    ```
2.  **Install Playwright browsers:**
    ```bash
    playwright install chromium
    ```

### Running the Tool

The tool is executed from the command line using `python -m simexp.simex`.

#### Commands

*   `python -m simexp.simex init`: Initializes the `simexp.yaml` configuration file.
*   `python -m simexp.simex write <note_url> [content]`: Writes content to a Simplenote note.
*   `python -m simexp.simex read <note_url>`: Reads content from a Simplenote note.
*   `python -m simexp.simex gdocs-write <doc_id> <content> [credentials_path]`: Writes content to a Google Docs document.
*   `python -m simexp.simex gdocs-read <doc_id> [credentials_path]`: Reads content from a Google Docs document.
*   `python -m simexp.simex gdocs-upload <file_path>`: Uploads a file to Google Docs.
*   `python -m simexp.simex channel <channel_name> <message>`: Writes a message to a pre-configured channel.
*   `python -m simexp.simex help`: Displays help information.

## Development Conventions

*   **Configuration:** Project configuration is managed through the `simexp.yaml` file. This file defines output paths, content sources, and communication channels.
*   **Source Code:** The main application logic is located in the `simexp/` directory.
*   **CLI:** The command-line interface is defined in `simexp/simex.py`.
*   **Testing:** The project includes several `test_*.py` files for testing different functionalities.
