
def _limpiar_fecha(valor):
    if not valor:
        return None
    import re
    meses = {'enero':'01','febrero':'02','marzo':'03','abril':'04','mayo':'05','junio':'06','julio':'07','agosto':'08','septiembre':'09','octubre':'10','noviembre':'11','diciembre':'12'}
    if re.match(r'\d{4}-\d{2}-\d{2}', str(valor)):
        return valor
    for mes, num in meses.items():
        if mes in str(valor).lower():
            numeros = re.findall(r'\d+', str(valor))
            if numeros:
                dia = numeros[0].zfill(2)
                anio = numeros[1] if len(numeros) > 1 else '2026'
                return f'{anio}-{num}-{dia}'
    numeros = re.findall(r'\d+', str(valor))
    if len(numeros) >= 2:
        return f'2026-{numeros[0].zfill(2)}-{numeros[1].zfill(2)}'
    return None
import re
from pyairtable import Api
from config.settings import (
    AIRTABLE_API_KEY,
    AIRTABLE_BASE_ID,
    AIRTABLE_TABLE_BRIEFS,
    AIRTABLE_TABLE_TERRITORIOS,
    AIRTABLE_TABLE_AD_RESULTS,
    AIRTABLE_TABLE_REPORTES,
    AIRTABLE_TABLE_KNOWLEDGE,
)

def _limpiar_plataformas(valor):
    if not valor:
        return []
    if isinstance(valor, list):
        texto = ' '.join([str(v) for v in valor]).lower()
    else:
        texto = str(valor).lower()
    resultado = []
    if 'meta' in texto or 'facebook' in texto: resultado.append('Facebook')
    if 'instagram' in texto: resultado.append('Instagram')
    if 'tiktok' in texto: resultado.append('Tiktok')
    if 'google' in texto: resultado.append('Google ads')
    if 'youtube' in texto: resultado.append('Youtube')
    return resultado if resultado else []

def _limpiar_budget(valor):
    if not valor:
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)
    numeros = re.findall(r"\d+", str(valor).split("(")[0])
    return float(numeros[0]) if numeros else 0.0

def get_tables():
    api = Api(AIRTABLE_API_KEY)
    base = api.base(AIRTABLE_BASE_ID)
    return {
        "briefs": base.table(AIRTABLE_TABLE_BRIEFS),
        "territorios": base.table(AIRTABLE_TABLE_TERRITORIOS),
        "ad_results": base.table(AIRTABLE_TABLE_AD_RESULTS),
        "reportes": base.table(AIRTABLE_TABLE_REPORTES),
    }

def crear_brief(datos_campana):
    tables = get_tables()
    record = tables["briefs"].create({
        "ID_campaña": datos_campana.get("id_campana", ""),
        "Nombre": datos_campana.get("nombre") or datos_campana.get("nombre_campana", ""),
        "Objetivo": datos_campana.get("objetivo", ""),
        "Audiencia": str(datos_campana.get("audiencia") or ""),
        "Budget": _limpiar_budget(datos_campana.get("budget") or datos_campana.get("budget_total") or datos_campana.get("budget_mensual")),
        "Plataformas": _limpiar_plataformas(datos_campana.get("plataformas", "")),
        "Fecha_Inicio": _limpiar_fecha(datos_campana.get("fecha_inicio") or datos_campana.get("fechas", "")),
        "Fecha_Fin": _limpiar_fecha(datos_campana.get("fecha_fin") or datos_campana.get("fechas", "")),
        "Estado": "Pendiente",
    })
    return record["id"]

def actualizar_brief(record_id, campos):
    tables = get_tables()
    tables["briefs"].update(record_id, campos)

def obtener_brief(id_campana):
    tables = get_tables()
    registros = tables["briefs"].all(formula=f"{{ID_campaña}}='{id_campana}'")
    return registros[0] if registros else None

def crear_territorio(id_campana):
    tables = get_tables()
    record = tables["territorios"].create({"ID_Campana": id_campana, "Estado": "Pendiente"})
    return record["id"]

def actualizar_territorio(record_id, campos):
    tables = get_tables()
    tables["territorios"].update(record_id, campos)

def obtener_territorio(id_campana):
    tables = get_tables()
    registros = tables["territorios"].all(formula=f"{{ID_Campana}}='{id_campana}'")
    return registros[0] if registros else None

def guardar_ad_result(datos):
    tables = get_tables()
    record = tables["ad_results"].create({
        "ID_Campana": datos["id_campana"],
        "Plataforma": datos["plataforma"],
        "Impresiones": datos.get("impresiones", 0),
        "Clics": datos.get("clics", 0),
        "Conversiones": datos.get("conversiones", 0),
        "Gasto": datos.get("gasto", 0),
        "ROAS": datos.get("roas", 0),
        "CTR": datos.get("ctr", 0),
        "CPC": datos.get("cpc", 0),
    })
    return record["id"]

def obtener_ad_results(id_campana):
    tables = get_tables()
    return tables["ad_results"].all(formula=f"{{ID_Campana}}='{id_campana}'")

def crear_reporte(id_campana, datos_reporte):
    tables = get_tables()
    record = tables["reportes"].create({
        "ID_Campana": id_campana,
        "Ranking_Imagenes": datos_reporte.get("ranking_imagenes", ""),
        "Ranking_Copy": datos_reporte.get("ranking_copy", ""),
        "Recomendaciones": datos_reporte.get("recomendaciones", ""),
        "Itera": datos_reporte.get("itera", False),
    })
    return record["id"]

def obtener_knowledge():
    try:
        api = Api(AIRTABLE_API_KEY)
        base = api.base(AIRTABLE_BASE_ID)
        table = base.table(AIRTABLE_TABLE_KNOWLEDGE)
        registros = table.all()
        knowledge = {}
        for r in registros:
            tipo = r["fields"].get("Tipo", "")
            contenido = r["fields"].get("Contenido", "")
            if tipo and contenido:
                knowledge[tipo] = contenido
        return knowledge
    except Exception as e:
        print(f"Knowledge no disponible: {e}")
        return {}
