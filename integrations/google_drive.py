from google.oauth2 import service_account
from googleapiclient.discovery import build
from config.settings import GOOGLE_DRIVE_CREDENTIALS_PATH, GOOGLE_DRIVE_FOLDER_ID

# Scopes necesarios para Drive + Docs
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/documents",
]

def get_credentials():
    """Devuelve las credenciales del Service Account."""
    return service_account.Credentials.from_service_account_file(
        GOOGLE_DRIVE_CREDENTIALS_PATH,
        scopes=SCOPES
    )

def get_drive_service():
    return build("drive", "v3", credentials=get_credentials())

def mover_a_carpeta(file_id: str, carpeta_id: str = None):
    """Mueve un archivo a la carpeta de briefs en Drive."""
    service = get_drive_service()
    carpeta = carpeta_id or GOOGLE_DRIVE_FOLDER_ID

    # Obtener carpetas actuales del archivo
    file = service.files().get(fileId=file_id, fields="parents").execute()
    parents_actuales = ",".join(file.get("parents", []))

    # Mover a la carpeta correcta
    service.files().update(
        fileId=file_id,
        addParents=carpeta,
        removeParents=parents_actuales,
        fields="id, parents, webViewLink"
    ).execute()
    print(f"[Drive] Archivo {file_id} movido a carpeta {carpeta}")

def compartir_con_usuario(file_id: str, email: str = "helena.fernandez@sequra.es"):
    """Hace el archivo accesible para todo el dominio seQura."""
    service = get_drive_service()
    service.permissions().create(
        fileId=file_id,
        body={"type": "user", "role": "writer", "emailAddress": email},
    ).execute()
    print(f"[Drive] Archivo compartido con {email}")

def obtener_link(file_id: str) -> str:
    """Devuelve el link de visualización del archivo."""
    service = get_drive_service()
    file = service.files().get(fileId=file_id, fields="webViewLink").execute()
    return file.get("webViewLink", "")
