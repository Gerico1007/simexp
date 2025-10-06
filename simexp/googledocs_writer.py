"""
SimExp Google Docs Writer Module
Google Docs API integration for cross-device communication

♠️🌿🎸🧵 G.Music Assembly - API-Based Communication Flow
"""

import os
import logging
from typing import Optional, Literal
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleDocsWriter:
    """
    Google Docs API writer for cross-device communication

    Features:
    - Service account or OAuth2 authentication
    - Read document content as plain text
    - Append text to end of document (instant API write)
    - Replace entire document content
    - Cross-device sync via Google Docs cloud

    Usage:
        # With service account
        writer = GoogleDocsWriter(
            document_id='1abc123xyz...',
            credentials_path='./credentials/service-account.json'
        )
        writer.authenticate()
        writer.append_content("Hello from terminal!")

        # With OAuth2 (user credentials)
        writer = GoogleDocsWriter(
            document_id='1abc123xyz...',
            credentials_path='./credentials/token.json',
            use_service_account=False
        )
        writer.authenticate()
        content = writer.read_content()
    """

    # Google Docs API scopes
    SCOPES = ['https://www.googleapis.com/auth/documents']

    def __init__(
        self,
        document_id: str,
        credentials_path: str,
        use_service_account: bool = True,
        debug: bool = False
    ):
        """
        Initialize GoogleDocsWriter

        Args:
            document_id: Google Docs document ID (from URL)
            credentials_path: Path to credentials JSON file
                             (service account or OAuth2 token)
            use_service_account: If True, use service account auth
                                If False, use OAuth2 user flow
            debug: Enable verbose debug logging
        """
        self.document_id = document_id
        self.credentials_path = credentials_path
        self.use_service_account = use_service_account
        self.debug = debug

        self.creds = None
        self.service = None

        if debug:
            logger.setLevel(logging.DEBUG)

    def authenticate(self):
        """
        Authenticate with Google Docs API

        Uses either:
        - Service Account: For automated access (recommended)
        - OAuth2: For user-specific access

        Raises:
            FileNotFoundError: If credentials file doesn't exist
            ValueError: If credentials are invalid
        """
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                f"Credentials file not found: {self.credentials_path}\n"
                f"Please set up Google Cloud credentials first."
            )

        if self.use_service_account:
            # Service Account authentication
            logger.info(f"🔑 Authenticating with service account: {self.credentials_path}")
            try:
                self.creds = service_account.Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=self.SCOPES
                )
                logger.info("✅ Service account authentication successful")
            except Exception as e:
                raise ValueError(f"Service account authentication failed: {e}")
        else:
            # OAuth2 user flow (for future expansion)
            logger.info(f"🔑 Authenticating with OAuth2: {self.credentials_path}")
            try:
                self.creds = Credentials.from_authorized_user_file(
                    self.credentials_path,
                    self.SCOPES
                )
                # Refresh if expired
                if not self.creds or not self.creds.valid:
                    if self.creds and self.creds.expired and self.creds.refresh_token:
                        self.creds.refresh(Request())
                logger.info("✅ OAuth2 authentication successful")
            except Exception as e:
                raise ValueError(f"OAuth2 authentication failed: {e}")

        # Build the Google Docs API service
        try:
            self.service = build('docs', 'v1', credentials=self.creds)
            logger.info("✅ Google Docs API service initialized")
        except Exception as e:
            raise ValueError(f"Failed to build API service: {e}")

    def read_content(self) -> str:
        """
        Read current content from Google Docs document

        Returns:
            Plain text content of the document

        Raises:
            ValueError: If not authenticated
            HttpError: If API request fails
        """
        if not self.service:
            raise ValueError("Not authenticated. Call authenticate() first.")

        logger.info(f"📖 Reading document: {self.document_id}")

        try:
            # Fetch the document
            document = self.service.documents().get(documentId=self.document_id).execute()

            # Extract plain text from document structure
            content = self._extract_text_from_document(document)

            logger.info(f"✅ Read {len(content)} characters")
            return content

        except HttpError as error:
            logger.error(f"❌ API request failed: {error}")
            raise

    def _extract_text_from_document(self, document: dict) -> str:
        """
        Extract plain text from Google Docs document structure

        Args:
            document: Document resource from API

        Returns:
            Plain text content
        """
        content = []
        body = document.get('body', {})

        for element in body.get('content', []):
            if 'paragraph' in element:
                paragraph = element['paragraph']
                for elem in paragraph.get('elements', []):
                    if 'textRun' in elem:
                        text_run = elem['textRun']
                        content.append(text_run.get('content', ''))

        return ''.join(content)

    def append_content(
        self,
        content: str,
        separator: str = '\n\n---\n\n'
    ) -> dict:
        """
        Append content to end of Google Docs document

        ⚡ INSTANT API WRITE - No typing simulation needed!

        Args:
            content: Text to append
            separator: String to insert before new content

        Returns:
            dict with status and metadata

        Raises:
            ValueError: If not authenticated
            HttpError: If API request fails
        """
        if not self.service:
            raise ValueError("Not authenticated. Call authenticate() first.")

        # Get current document to find end index
        logger.info(f"📄 Appending to document: {self.document_id}")

        try:
            # Fetch document to get structure
            document = self.service.documents().get(documentId=self.document_id).execute()

            # Get the end of document index (last content index)
            body = document.get('body', {})
            end_index = body.get('content', [{}])[-1].get('endIndex', 1)

            # Prepare content with separator
            full_content = f"{separator}{content}"

            logger.info(f"✍️  Appending {len(full_content)} characters at index {end_index}")

            # Build batch update request
            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': end_index - 1  # Insert before the final newline
                        },
                        'text': full_content
                    }
                }
            ]

            # Execute the batch update
            result = self.service.documents().batchUpdate(
                documentId=self.document_id,
                body={'requests': requests}
            ).execute()

            logger.info(f"✅ Append successful!")

            return {
                'success': True,
                'mode': 'append',
                'document_id': self.document_id,
                'content_length': len(full_content),
                'preview': content[:100] + ('...' if len(content) > 100 else ''),
                'api_response': result
            }

        except HttpError as error:
            logger.error(f"❌ API request failed: {error}")
            return {
                'success': False,
                'error': str(error)
            }

    def replace_content(self, content: str) -> dict:
        """
        Replace entire document content

        Args:
            content: New text for the document

        Returns:
            dict with status and metadata

        Raises:
            ValueError: If not authenticated
            HttpError: If API request fails
        """
        if not self.service:
            raise ValueError("Not authenticated. Call authenticate() first.")

        logger.info(f"✍️  Replacing document content: {self.document_id}")

        try:
            # Fetch document to get current structure
            document = self.service.documents().get(documentId=self.document_id).execute()

            # Get document bounds
            body = document.get('body', {})
            end_index = body.get('content', [{}])[-1].get('endIndex', 1)

            logger.info(f"🗑️  Deleting {end_index} characters")

            # Build batch update: delete all, then insert new
            requests = [
                {
                    'deleteContentRange': {
                        'range': {
                            'startIndex': 1,
                            'endIndex': end_index - 1
                        }
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': 1
                        },
                        'text': content
                    }
                }
            ]

            logger.info(f"✍️  Writing {len(content)} characters")

            # Execute the batch update
            result = self.service.documents().batchUpdate(
                documentId=self.document_id,
                body={'requests': requests}
            ).execute()

            logger.info(f"✅ Replace successful!")

            return {
                'success': True,
                'mode': 'replace',
                'document_id': self.document_id,
                'content_length': len(content),
                'preview': content[:100] + ('...' if len(content) > 100 else ''),
                'api_response': result
            }

        except HttpError as error:
            logger.error(f"❌ API request failed: {error}")
            return {
                'success': False,
                'error': str(error)
            }

    def get_document_info(self) -> dict:
        """
        Get document metadata (title, revision ID, etc.)

        Returns:
            dict with document metadata
        """
        if not self.service:
            raise ValueError("Not authenticated. Call authenticate() first.")

        try:
            document = self.service.documents().get(documentId=self.document_id).execute()

            return {
                'document_id': self.document_id,
                'title': document.get('title', 'Untitled'),
                'revision_id': document.get('revisionId', 'Unknown'),
                'document_url': f"https://docs.google.com/document/d/{self.document_id}/edit"
            }
        except HttpError as error:
            logger.error(f"❌ Failed to get document info: {error}")
            return {'error': str(error)}


# Convenience functions (async-compatible for future expansion)
def write_to_googledoc(
    document_id: str,
    content: str,
    credentials_path: str,
    mode: Literal['append', 'replace'] = 'append',
    separator: str = '\n\n---\n\n'
) -> dict:
    """
    Convenience function to write to a Google Docs document

    Usage:
        result = write_to_googledoc(
            document_id='1abc123xyz...',
            content='Hello from terminal!',
            credentials_path='./credentials/service-account.json',
            mode='append'
        )

    Args:
        document_id: Google Docs document ID
        content: Text to write
        credentials_path: Path to service account JSON
        mode: 'append' or 'replace'
        separator: Separator for append mode

    Returns:
        dict with write result
    """
    writer = GoogleDocsWriter(document_id, credentials_path)
    writer.authenticate()

    if mode == 'append':
        return writer.append_content(content, separator=separator)
    else:
        return writer.replace_content(content)


def read_from_googledoc(
    document_id: str,
    credentials_path: str
) -> str:
    """
    Convenience function to read from a Google Docs document

    Usage:
        content = read_from_googledoc(
            document_id='1abc123xyz...',
            credentials_path='./credentials/service-account.json'
        )

    Args:
        document_id: Google Docs document ID
        credentials_path: Path to service account JSON

    Returns:
        Document content as string
    """
    writer = GoogleDocsWriter(document_id, credentials_path)
    writer.authenticate()
    return writer.read_content()


# CLI interface for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print("Usage:")
        print("  Write: python googledocs_writer.py write <doc_id> <credentials_path> <content>")
        print("  Read:  python googledocs_writer.py read <doc_id> <credentials_path>")
        print("  Info:  python googledocs_writer.py info <doc_id> <credentials_path>")
        sys.exit(1)

    command = sys.argv[1]
    doc_id = sys.argv[2]
    creds_path = sys.argv[3]

    if command == 'write':
        content = sys.argv[4] if len(sys.argv) > 4 else "Test message from SimExp Google Docs Writer"
        result = write_to_googledoc(doc_id, content, creds_path, debug=True)
        print(f"\n✅ Result: {result}")

    elif command == 'read':
        content = read_from_googledoc(doc_id, creds_path)
        print(f"\n📖 Content:\n{content}")

    elif command == 'info':
        writer = GoogleDocsWriter(doc_id, creds_path)
        writer.authenticate()
        info = writer.get_document_info()
        print(f"\n📄 Document Info:")
        for key, value in info.items():
            print(f"  {key}: {value}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
