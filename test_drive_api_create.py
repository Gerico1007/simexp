
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

CREDENTIALS_FILE = './credentials/service-account.json'
FOLDER_ID = '1tTlk5_3P-XwidwFT5Np9PmubP8nA7H_d'

def create_document_in_folder():
    """Creates a new Google Doc in a specific folder and prints the result."""
    try:
        creds, _ = google.auth.load_credentials_from_file(
            CREDENTIALS_FILE,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name': 'Drive API Test Document',
            'mimeType': 'application/vnd.google-apps.document',
            'parents': [FOLDER_ID]
        }
        file = service.files().create(body=file_metadata, fields='id,name,webViewLink').execute()
        print(f"Successfully created document in folder:")
        print(f"  Name: {file.get('name')}")
        print(f"  ID: {file.get('id')}")
        print(f"  URL: {file.get('webViewLink')}")

    except HttpError as err:
        print(f"An HTTP error {err.resp.status} occurred:")
        print(err.content)
    except Exception as err:
        print(f"An error occurred: {err}")

if __name__ == '__main__':
    create_document_in_folder()
