from googleapiclient.discovery import build
from integrations.google_drive import get_credentials, mover_a_carpeta, compartir_con_usuario, obtener_link
from config.settings import GOOGLE_DRIVE_FOLDER_ID

# Colores seQura
VERDE_TEAL = {"red": 0.0, "green": 0.706, "blue": 0.635}   # #00B4A2
AZUL_OSCURO = {"red": 0.102, "green": 0.102, "blue": 0.180} # #1A1A2E
GRIS_TEXTO  = {"red": 0.2, "green": 0.2, "blue": 0.2}       # #333333
BLANCO      = {"red": 1.0, "green": 1.0, "blue": 1.0}
GRIS_FILA   = {"red": 0.949, "green": 0.949, "blue": 0.949} # #F2F2F2

def get_docs_service():
    return build("docs", "v1", credentials=get_credentials())

def crear_brief_google_doc(brief_data: dict) -> str:
    """
    Crea un Google Doc con el brief completo y formato seQura.
    Devuelve la URL del documento.

    brief_data = {
        "nombre": "Campaña Always-On Q2 2026",
        "periodo": "Q2 2026",
        "tipo": "ALWAYS-ON",
        "fecha": "12/03/2026",
        "brief_generado": "...",   # secciones 1-5
        "keywords": "...",          # sección 6
        "analisis_competencia": "...", # sección 7
        "insights": "...",          # sección 8
        "assets_produccion": "...", # secciones 10-14
        "planning_presupuesto": "..." # secciones 15-20
    }
    """
    docs_service = get_docs_service()

    tipo    = brief_data.get("tipo", "ALWAYS-ON").upper()
    periodo = brief_data.get("periodo", "2026")
    nombre  = f"BRIEF CAMPAÑA {tipo} {periodo} — seQura"

    # 1. Crear documento vacío
    doc = docs_service.documents().create(body={"title": nombre}).execute()
    doc_id = doc["documentId"]
    print(f"[Docs] Documento creado: {doc_id}")

    # 2. Construir el contenido completo
    contenido = _construir_contenido(brief_data)

    # 3. Insertar texto e índice de requests de formato
    requests = _construir_requests(contenido)

    # 4. Ejecutar batch de requests
    if requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": requests}
        ).execute()
    print(f"[Docs] Contenido y formato aplicados")

    # 5. Mover a carpeta de Drive y compartir
    mover_a_carpeta(doc_id, GOOGLE_DRIVE_FOLDER_ID)
    compartir_con_usuario(doc_id)

    url = obtener_link(doc_id)
    print(f"[Docs] Brief disponible en: {url}")
    return doc_id, url


def _construir_contenido(brief_data: dict) -> list:
    """
    Devuelve una lista de bloques: {"type": "heading1/heading2/body/...", "text": "..."}
    """
    tipo    = brief_data.get("tipo", "ALWAYS-ON").upper()
    periodo = brief_data.get("periodo", "2026")
    fecha   = brief_data.get("fecha", "")

    bloques = []

    # Portada
    bloques.append({"type": "title",    "text": f"BRIEF CAMPAÑA {tipo}"})
    bloques.append({"type": "title",    "text": periodo})
    bloques.append({"type": "subtitle", "text": "seQura shopper acquisition & engagement"})
    bloques.append({"type": "body",     "text": f"Fecha de elaboración: {fecha}"})
    bloques.append({"type": "body",     "text": "Equipo de Marketing — seQura"})
    bloques.append({"type": "pagebreak"})

    # Secciones 1-5
    bloques.append({"type": "heading1", "text": "Brief de Campaña"})
    bloques += _texto_a_bloques(brief_data.get("brief_generado", "PENDIENTE — completar antes del kick-off"))

    # Sección 6
    bloques.append({"type": "heading1", "text": "6. Research de Keywords"})
    bloques += _texto_a_bloques(brief_data.get("keywords", "PENDIENTE"))

    # Sección 7
    bloques.append({"type": "heading1", "text": "7. Análisis de Competencia"})
    bloques += _texto_a_bloques(brief_data.get("analisis_competencia", "PENDIENTE"))

    # Sección 8
    bloques.append({"type": "heading1", "text": "8. Insights Clave"})
    bloques += _texto_a_bloques(brief_data.get("insights", "PENDIENTE"))

    # Secciones 10-14
    bloques.append({"type": "heading1", "text": "Assets, Producción y Canales"})
    bloques += _texto_a_bloques(brief_data.get("assets_produccion", "PENDIENTE"))

    # Secciones 15-20
    bloques.append({"type": "heading1", "text": "Planning, Presupuesto y Checklist"})
    bloques += _texto_a_bloques(brief_data.get("planning_presupuesto", "PENDIENTE"))

    return bloques


def _texto_a_bloques(texto: str) -> list:
    """Convierte texto plano con markdown básico a bloques tipados."""
    bloques = []
    for linea in texto.split("\n"):
        t = linea.strip()
        if not t:
            bloques.append({"type": "body", "text": " "})
        elif t.startswith("### "):
            bloques.append({"type": "heading3", "text": t[4:]})
        elif t.startswith("## "):
            bloques.append({"type": "heading2", "text": t[3:]})
        elif t.startswith("# "):
            bloques.append({"type": "heading1", "text": t[2:]})
        elif t.startswith("- ") or t.startswith("• "):
            bloques.append({"type": "bullet", "text": t[2:]})
        elif t.startswith("**") and t.endswith("**"):
            bloques.append({"type": "bold", "text": t[2:-2]})
        else:
            bloques.append({"type": "body", "text": t})
    return bloques


def _construir_requests(bloques: list) -> list:
    """
    Convierte los bloques en requests de Google Docs API.
    Inserta texto de atrás hacia adelante para mantener índices correctos.
    """
    requests = []
    # Construir texto completo primero para insertar de una vez
    texto_completo = ""
    for bloque in bloques:
        if bloque["type"] == "pagebreak":
            texto_completo += "\f"  # form feed = page break en Docs
        else:
            texto_completo += bloque["text"] + "\n"

    # Insertar todo el texto al inicio del documento
    requests.append({
        "insertText": {
            "location": {"index": 1},
            "text": texto_completo
        }
    })

    # Aplicar estilos recorriendo el texto y calculando índices
    index = 1
    for bloque in bloques:
        if bloque["type"] == "pagebreak":
            index += 1
            continue

        texto = bloque["text"]
        fin   = index + len(texto)
        tipo  = bloque["type"]

        # Estilo de párrafo (heading, etc.)
        named_style = None
        if tipo == "title":
            named_style = "TITLE"
        elif tipo == "subtitle":
            named_style = "SUBTITLE"
        elif tipo == "heading1":
            named_style = "HEADING_1"
        elif tipo == "heading2":
            named_style = "HEADING_2"
        elif tipo == "heading3":
            named_style = "HEADING_3"

        if named_style:
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": index, "endIndex": fin},
                    "paragraphStyle": {"namedStyleType": named_style},
                    "fields": "namedStyleType"
                }
            })

        # Color de texto según tipo
        color = None
        if tipo in ("heading1", "title"):
            color = VERDE_TEAL
        elif tipo in ("heading2", "subtitle"):
            color = AZUL_OSCURO
        elif tipo == "heading3":
            color = VERDE_TEAL

        if color:
            requests.append({
                "updateTextStyle": {
                    "range": {"startIndex": index, "endIndex": fin},
                    "textStyle": {"foregroundColor": {"color": {"rgbColor": color}}},
                    "fields": "foregroundColor"
                }
            })

        # Bold para tipo bold
        if tipo == "bold":
            requests.append({
                "updateTextStyle": {
                    "range": {"startIndex": index, "endIndex": fin},
                    "textStyle": {"bold": True},
                    "fields": "bold"
                }
            })

        # Bullet list
        if tipo == "bullet":
            requests.append({
                "createParagraphBullets": {
                    "range": {"startIndex": index, "endIndex": fin},
                    "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
                }
            })

        index = fin + 1  # +1 por el \n

    return requests


def leer_sugerencias(doc_id: str) -> list:
    """
    Lee las sugerencias pendientes de un Google Doc.
    Devuelve lista de sugerencias con texto sugerido y contexto.
    """
    docs_service = get_docs_service()
    doc = docs_service.documents().get(
        documentId=doc_id,
        suggestionsViewMode="SUGGESTIONS_INLINE"
    ).execute()

    sugerencias = []
    body = doc.get("body", {}).get("content", [])

    for elemento in body:
        paragraph = elemento.get("paragraph", {})
        for run in paragraph.get("elements", []):
            # Texto con sugerencia de inserción
            texto_run = run.get("textRun", {})
            suggested_insertions = texto_run.get("suggestedInsertionIds", [])
            suggested_deletions  = texto_run.get("suggestedDeletionIds", [])

            if suggested_insertions:
                sugerencias.append({
                    "tipo":    "inserción",
                    "texto":   texto_run.get("content", ""),
                    "ids":     suggested_insertions
                })
            if suggested_deletions:
                sugerencias.append({
                    "tipo":    "eliminación",
                    "texto":   texto_run.get("content", ""),
                    "ids":     suggested_deletions
                })

    print(f"[Docs] {len(sugerencias)} sugerencias encontradas")
    return sugerencias


def actualizar_doc_con_cambios(doc_id: str, contenido_nuevo: str):
    """
    Reemplaza el contenido de un Google Doc existente con el brief actualizado.
    Se usa después de aplicar el feedback del manager.
    """
    docs_service = get_docs_service()

    # Obtener longitud actual del documento
    doc = docs_service.documents().get(documentId=doc_id).execute()
    end_index = doc["body"]["content"][-1]["endIndex"] - 1

    requests = [
        # Borrar contenido actual
        {
            "deleteContentRange": {
                "range": {"startIndex": 1, "endIndex": end_index}
            }
        },
        # Insertar nuevo contenido
        {
            "insertText": {
                "location": {"index": 1},
                "text": contenido_nuevo
            }
        }
    ]

    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": requests}
    ).execute()
    print(f"[Docs] Documento {doc_id} actualizado con cambios")
