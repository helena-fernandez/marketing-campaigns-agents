import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from config.settings import GOOGLE_DRIVE_FOLDER_ID

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
]

OAUTH_CLIENT_PATH = os.path.join(os.path.dirname(__file__), "../credentials/oauth_client.json")
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "../credentials/token.json")

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(OAUTH_CLIENT_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    return creds

def get_drive_service():
    return build("drive", "v3", credentials=get_credentials())

def mover_a_carpeta(file_id: str, carpeta_id: str = None):
    service = get_drive_service()
    carpeta = carpeta_id or GOOGLE_DRIVE_FOLDER_ID
    file = service.files().get(fileId=file_id, fields="parents").execute()
    parents_actuales = ",".join(file.get("parents", []))
    service.files().update(
        fileId=file_id,
        addParents=carpeta,
        removeParents=parents_actuales,
        fields="id, parents, webViewLink"
    ).execute()
    print(f"[Drive] Archivo {file_id} movido a carpeta {carpeta}")

def compartir_con_usuario(file_id: str, email: str = "helena.fernandez@sequra.es"):
    service = get_drive_service()
    service.permissions().create(
        fileId=file_id,
        body={"type": "user", "role": "writer", "emailAddress": email},
    ).execute()
    print(f"[Drive] Archivo compartido con {email}")

def obtener_link(file_id: str) -> str:
    service = get_drive_service()
    file = service.files().get(fileId=file_id, fields="webViewLink").execute()
    return file.get("webViewLink", "")
