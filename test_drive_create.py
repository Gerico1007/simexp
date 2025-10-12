
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

CREDENTIALS_FILE = './credentials/service-account.json'

def create_document():
    """Creates a new Google Doc and prints the result."""
    try:
        creds, _ = google.auth.load_credentials_from_file(
            CREDENTIALS_FILE,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        service = build('docs', 'v1', credentials=creds)

        title = 'Minimal Test Document'
        body = {
            'title': title
        }
        doc = service.documents().create(body=body).execute()
        print(f"Successfully created document:")
        print(f"  Title: {doc.get('title')}")
        print(f"  ID: {doc.get('documentId')}")
        print(f"  URL: https://docs.google.com/document/d/{doc.get('documentId')}/edit")

    except HttpError as err:
        print(f"An HTTP error {err.resp.status} occurred:")
        print(err.content)
    except Exception as err:
        print(f"An error occurred: {err}")

if __name__ == '__main__':
    create_document()
