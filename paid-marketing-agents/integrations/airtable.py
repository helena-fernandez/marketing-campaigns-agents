from pyairtable import Api
from config.settings import (
    AIRTABLE_API_KEY,
    AIRTABLE_BASE_ID,
    AIRTABLE_TABLE_BRIEFS,
    AIRTABLE_TABLE_TERRITORIOS,
    AIRTABLE_TABLE_AD_RESULTS,
    AIRTABLE_TABLE_REPORTES,
)

def get_tables():
    api = Api(AIRTABLE_API_KEY)
    base = api.base(AIRTABLE_BASE_ID)
    return {
        "briefs":      base.table(AIRTABLE_TABLE_BRIEFS),
        "territorios": base.table(AIRTABLE_TABLE_TERRITORIOS),
        "ad_results":  base.table(AIRTABLE_TABLE_AD_RESULTS),
        "reportes":    base.table(AIRTABLE_TABLE_REPORTES),
    }

# ── BRIEFS ────────────────────────────────────────────────

def crear_brief(datos_campana: dict) -> str:
    tables = get_tables()
    record = tables["briefs"].create({
        "ID_campaña":   datos_campana.get("id_campana", ""),
        "Nombre":       datos_campana.get("nombre", ""),
        "Objetivo":     datos_campana.get("objetivo", ""),
        "Audiencia":    datos_campana.get("audiencia", ""),
        "Budget":       datos_campana.get("budget", 0),
        "Plataformas":  datos_campana.get("plataformas", ""),
        "Fecha_Inicio": datos_campana.get("fecha_inicio", ""),
        "Fecha_Fin":    datos_campana.get("fecha_fin", ""),
        "Estado":       "Pendiente",
    })
    return record["id"]

def actualizar_brief(record_id: str, campos: dict):
    tables = get_tables()
    tables["briefs"].update(record_id, campos)

def obtener_brief(id_campana: str) -> dict:
    tables = get_tables()
    registros = tables["briefs"].all(formula=f"{{ID_campaña}}='{id_campana}'")
    return registros[0] if registros else None

# ── TERRITORIOS ───────────────────────────────────────────

def crear_territorio(id_campana: str) -> str:
    tables = get_tables()
    record = tables["territorios"].create({
        "ID_Campaña": id_campana,
        "Estado":     "Pendiente",
    })
    return record["id"]

def actualizar_territorio(record_id: str, campos: dict):
    tables = get_tables()
    tables["territorios"].update(record_id, campos)

def obtener_territorio(id_campana: str) -> dict:
    tables = get_tables()
    registros = tables["territorios"].all(formula=f"{{ID_Campaña}}='{id_campana}'")
    return registros[0] if registros else None

# ── AD RESULTS ────────────────────────────────────────────

def guardar_ad_result(datos: dict) -> str:
    tables = get_tables()
    record = tables["ad_results"].create({
        "ID_Campaña":   datos["id_campana"],
        "Plataforma":   datos["plataforma"],
        "Impresiones":  datos.get("impresiones", 0),
        "Clics":        datos.get("clics", 0),
        "Conversiones": datos.get("conversiones", 0),
        "Gasto":        datos.get("gasto", 0),
        "ROAS":         datos.get("roas", 0),
        "CTR":          datos.get("ctr", 0),
        "CPC":          datos.get("cpc", 0),
        "Fecha_Inicio": datos.get("fecha_inicio"),
        "Fecha_Fin":    datos.get("fecha_fin"),
    })
    return record["id"]

def obtener_ad_results(id_campana: str) -> list:
    tables = get_tables()
    return tables["ad_results"].all(formula=f"{{ID_Campaña}}='{id_campana}'")

# ── REPORTES ──────────────────────────────────────────────

def crear_reporte(id_campana: str, datos_reporte: dict) -> str:
    tables = get_tables()
    record = tables["reportes"].create({
        "ID_Campaña":        id_campana,
        "Ranking_Imagenes":  datos_reporte.get("ranking_imagenes", ""),
        "Ranking_Copy":      datos_reporte.get("ranking_copy", ""),
        "Ranking_Headlines": datos_reporte.get("ranking_headlines", ""),
        "Ranking_ROAS":      datos_reporte.get("ranking_roas", ""),
        "Recomendaciones":   datos_reporte.get("recomendaciones", ""),
        "Itera":             datos_reporte.get("itera", False),
        "Fecha_Reporte":     datos_reporte.get("fecha_reporte"),
    })
    return record["id"]
