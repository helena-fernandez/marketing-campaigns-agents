from googleapiclient.discovery import build
from integrations.google_drive import get_credentials, get_drive_service, compartir_con_usuario
from config.settings import GOOGLE_DRIVE_FOLDER_ID

VERDE_TEAL = {"red": 0.0, "green": 0.706, "blue": 0.635}
AZUL_OSCURO = {"red": 0.102, "green": 0.102, "blue": 0.180}

def get_docs_service():
    return build("docs", "v1", credentials=get_credentials())

def crear_brief_google_doc(brief_data: dict) -> tuple:
    docs_service = get_docs_service()
    drive_service = get_drive_service()

    tipo    = brief_data.get("tipo", "ALWAYS-ON").upper()
    periodo = brief_data.get("periodo", "2026")
    nombre  = f"BRIEF CAMPAÑA {tipo} {periodo} — seQura"

    doc = docs_service.documents().create(body={"title": nombre}).execute()
    doc_id = doc["documentId"]
    print(f"[Docs] Documento creado: {doc_id}")

    contenido = _construir_contenido(brief_data)
    _aplicar_contenido(docs_service, doc_id, contenido)
    print(f"[Docs] Contenido y formato aplicados")

    try:
        file = drive_service.files().get(fileId=doc_id, fields="parents").execute()
        parents_actuales = ",".join(file.get("parents", []))
        drive_service.files().update(
            fileId=doc_id,
            addParents=GOOGLE_DRIVE_FOLDER_ID,
            removeParents=parents_actuales,
            fields="id, parents"
        ).execute()
        print(f"[Docs] Movido a carpeta Briefs seQura")
    except Exception as e:
        print(f"[Docs] No se pudo mover: {e}")

    try:
        compartir_con_usuario(doc_id)
    except Exception as e:
        print(f"[Docs] Aviso compartir: {e}")

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"[Docs] Brief disponible en: {url}")
    return doc_id, url


def _construir_contenido(brief_data: dict) -> list:
    tipo    = brief_data.get("tipo", "ALWAYS-ON").upper()
    periodo = brief_data.get("periodo", "2026")
    fecha   = brief_data.get("fecha", "")

    bloques = []
    bloques.append({"type": "title",    "text": f"BRIEF CAMPAÑA {tipo} {periodo}"})
    bloques.append({"type": "subtitle", "text": "seQura shopper acquisition & engagement"})
    bloques.append({"type": "body",     "text": f"Fecha de elaboración: {fecha}"})
    bloques.append({"type": "body",     "text": "Equipo de Marketing — seQura"})
    bloques.append({"type": "pagebreak"})
    bloques.append({"type": "heading1", "text": "Brief de Campaña"})
    bloques += _texto_a_bloques(brief_data.get("brief_generado", "PENDIENTE"))
    bloques.append({"type": "heading1", "text": "6. Research de Keywords"})
    bloques += _texto_a_bloques(brief_data.get("keywords", "PENDIENTE"))
    bloques.append({"type": "heading1", "text": "7. Análisis de Competencia"})
    bloques += _texto_a_bloques(brief_data.get("analisis_competencia", "PENDIENTE"))
    bloques.append({"type": "heading1", "text": "8. Insights Clave"})
    bloques += _texto_a_bloques(brief_data.get("insights", "PENDIENTE"))
    bloques.append({"type": "heading1", "text": "Assets, Producción y Canales"})
    bloques += _texto_a_bloques(brief_data.get("assets_produccion", "PENDIENTE"))
    bloques.append({"type": "heading1", "text": "Planning, Presupuesto y Checklist"})
    bloques += _texto_a_bloques(brief_data.get("planning_presupuesto", "PENDIENTE"))
    return bloques


def _limpiar_markdown(texto: str) -> str:
    import re
    texto = re.sub(r'\*\*(.+?)\*\*', r'\1', texto)
    texto = re.sub(r'\*(.+?)\*', r'\1', texto)
    return texto


def _texto_a_bloques(texto: str) -> list:
    bloques = []
    lineas = texto.split("\n")
    i = 0
    while i < len(lineas):
        linea = lineas[i]
        t = linea.strip()

        if t.startswith("|") and t.endswith("|"):
            filas_tabla = []
            while i < len(lineas) and lineas[i].strip().startswith("|"):
                fila = lineas[i].strip()
                if not all(c in "-| :" for c in fila):
                    celdas = [_limpiar_markdown(c.strip()) for c in fila.strip("|").split("|")]
                    filas_tabla.append(celdas)
                i += 1
            if filas_tabla:
                bloques.append({"type": "table", "rows": filas_tabla})
            continue

        if not t:
            bloques.append({"type": "body", "text": " "})
        elif t.startswith("### "):
            bloques.append({"type": "heading3", "text": _limpiar_markdown(t[4:])})
        elif t.startswith("## "):
            bloques.append({"type": "heading2", "text": _limpiar_markdown(t[3:])})
        elif t.startswith("# "):
            bloques.append({"type": "heading1", "text": _limpiar_markdown(t[2:])})
        elif t.startswith("- ") or t.startswith("* "):
            bloques.append({"type": "bullet", "text": _limpiar_markdown(t[2:])})
        else:
            bloques.append({"type": "body", "text": _limpiar_markdown(t)})
        i += 1
    return bloques


def _aplicar_contenido(docs_service, doc_id: str, bloques: list):
    grupos = []
    grupo_actual = []
    for bloque in bloques:
        if bloque["type"] == "table":
            if grupo_actual:
                grupos.append({"type": "text", "bloques": grupo_actual})
                grupo_actual = []
            grupos.append({"type": "table", "data": bloque["rows"]})
        else:
            grupo_actual.append(bloque)
    if grupo_actual:
        grupos.append({"type": "text", "bloques": grupo_actual})

    texto_completo = ""
    estructura = []
    for grupo in grupos:
        if grupo["type"] == "text":
            for bloque in grupo["bloques"]:
                if bloque["type"] == "pagebreak":
                    texto_completo += "\f"
                    estructura.append(("pagebreak", None))
                else:
                    texto_completo += bloque["text"] + "\n"
                    estructura.append(("bloque", bloque))
        else:
            texto_completo += "\n"
            estructura.append(("tabla", grupo["data"]))

    requests = [{"insertText": {"location": {"index": 1}, "text": texto_completo}}]
    index = 1
    tabla_indices = []

    for tipo_e, dato in estructura:
        if tipo_e == "pagebreak":
            index += 1
            continue
        elif tipo_e == "tabla":
            tabla_indices.append(index)
            index += 1
            continue

        bloque = dato
        texto = bloque["text"]
        fin = index + len(texto)
        tipo = bloque["type"]

        named_style = None
        if tipo == "title":       named_style = "TITLE"
        elif tipo == "subtitle":  named_style = "SUBTITLE"
        elif tipo == "heading1":  named_style = "HEADING_1"
        elif tipo == "heading2":  named_style = "HEADING_2"
        elif tipo == "heading3":  named_style = "HEADING_3"

        if named_style:
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": index, "endIndex": fin},
                    "paragraphStyle": {"namedStyleType": named_style},
                    "fields": "namedStyleType"
                }
            })

        color = None
        if tipo in ("heading1", "title"):      color = VERDE_TEAL
        elif tipo in ("heading2", "subtitle"): color = AZUL_OSCURO
        elif tipo == "heading3":               color = VERDE_TEAL

        if color:
            requests.append({
                "updateTextStyle": {
                    "range": {"startIndex": index, "endIndex": fin},
                    "textStyle": {"foregroundColor": {"color": {"rgbColor": color}}},
                    "fields": "foregroundColor"
                }
            })

        if tipo == "bullet":
            requests.append({
                "createParagraphBullets": {
                    "range": {"startIndex": index, "endIndex": fin},
                    "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
                }
            })

        index = fin + 1

    if requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": requests}
        ).execute()

    tablas_data = [g["data"] for g in grupos if g["type"] == "table"]
    for idx, filas in zip(reversed(tabla_indices), reversed(tablas_data)):
        _insertar_tabla(docs_service, doc_id, idx, filas)


def _insertar_tabla(docs_service, doc_id: str, index: int, filas: list):
    if not filas:
        return
    num_rows = len(filas)
    num_cols = max(len(f) for f in filas)

    try:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": [{"insertTable": {
                "rows": num_rows,
                "columns": num_cols,
                "location": {"index": index}
            }}]}
        ).execute()

        doc = docs_service.documents().get(documentId=doc_id).execute()
        tables = [e for e in doc["body"]["content"] if "table" in e]
        if not tables:
            return

        tabla = min(tables, key=lambda t: abs(t.get("startIndex", 0) - index))
        cell_requests = []

        for r_idx, fila in enumerate(filas):
            if r_idx >= len(tabla["table"]["tableRows"]):
                continue
            row = tabla["table"]["tableRows"][r_idx]
            for c_idx, celda_texto in enumerate(fila):
                if c_idx >= len(row["tableCells"]):
                    continue
                cell = row["tableCells"][c_idx]
                cell_index = cell["content"][0]["startIndex"]
                texto = celda_texto.strip()
                if texto:
                    cell_requests.append({
                        "insertText": {
                            "location": {"index": cell_index},
                            "text": texto
                        }
                    })
                    if r_idx == 0:
                        cell_requests.append({
                            "updateTextStyle": {
                                "range": {"startIndex": cell_index, "endIndex": cell_index + len(texto)},
                                "textStyle": {"bold": True},
                                "fields": "bold"
                            }
                        })

        if cell_requests:
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={"requests": cell_requests}
            ).execute()

    except Exception as e:
        print(f"[Docs] Error insertando tabla: {e}")


def leer_sugerencias(doc_id: str) -> list:
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
            texto_run = run.get("textRun", {})
            if texto_run.get("suggestedInsertionIds"):
                sugerencias.append({"tipo": "inserción", "texto": texto_run.get("content", "")})
            if texto_run.get("suggestedDeletionIds"):
                sugerencias.append({"tipo": "eliminación", "texto": texto_run.get("content", "")})
    print(f"[Docs] {len(sugerencias)} sugerencias encontradas")
    return sugerencias


def actualizar_doc_con_cambios(doc_id: str, contenido_nuevo: str):
    docs_service = get_docs_service()
    doc = docs_service.documents().get(documentId=doc_id).execute()
    end_index = doc["body"]["content"][-1]["endIndex"] - 1
    requests = [
        {"deleteContentRange": {"range": {"startIndex": 1, "endIndex": end_index}}},
        {"insertText": {"location": {"index": 1}, "text": contenido_nuevo}}
    ]
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": requests}
    ).execute()
    print(f"[Docs] Documento {doc_id} actualizado")
