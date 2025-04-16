from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv(dotenv_path=Path('.env'))
GOOGLE_DRIVE_SCOPE = os.getenv('GOOGLE_DRIVE_SCOPE')
TOKEN_FILE = Path('/token.js')
CREDENTIALS_FILE = Path('/credentials.js')

def authenticate():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, GOOGLE_DRIVE_SCOPE)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, GOOGLE_DRIVE_SCOPE)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)


def upload_file_to_drive(filepath: Path, filename: str, folder_id: str = None):
    service = authenticate()
    file_metadata = {'name': filename}
    if folder_id:
        file_metadata['parents'] = [folder_id]
    media = MediaFileUpload(str(filepath), resumable=True)
    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()
    return uploaded


