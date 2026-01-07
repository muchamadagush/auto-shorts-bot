import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('youtube', 'v3', credentials=creds)

def upload_video(file_path, title, description, privacy_status="public"):
    try:
        youtube = get_authenticated_service()
        body = {
            'snippet': {'title': title[:100], 'description': description, 'categoryId': '22'},
            'status': {'privacyStatus': privacy_status, 'selfDeclaredMadeForKids': False}
        }
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(part=','.join(body.keys()), body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status: print(f"      Uploading... {int(status.progress() * 100)}%")
        print(f"      ✅ YouTube Upload Done: ID {response.get('id')}")
        return True
    except Exception as e:
        print(f"      ❌ YouTube Error: {e}")
        return False