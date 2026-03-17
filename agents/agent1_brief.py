import anthropic
from datetime import datetime
from config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL
from integrations.airtable import crear_brief, actualizar_brief, obtener_brief, obtener_knowledge

BRAND_VOICE = """
IDENTIDAD DE MARCA seQura:
- Nombre: siempre "seQura" con Q mayúscula
- Posicionamiento: La forma más simple, rápida y flexible de comprar en miles de tiendas online
- Insight central: La Gen Z y Millennials fraccionan porque PREFIEREN distribuir el impacto económico — es planificación financiera, no necesidad

QUÉ NO QUEREMOS PARECER:
- Otro BNPL genérico ("compra ahora, paga después" sin contexto)
- Fintech fría y corporativa (sin tecnicismos: APR, scoring, underwriting)
- Solo para gente con problemas económicos (jamás "solución de emergencia")

QUÉ SÍ QUEREMOS PROYECTAR:
- Planificación financiera inteligente
- Simplicidad radical: "5 datos, 0 documentos, <1 minuto"
- Confianza masiva: 2.5M+ shoppers, 6.000+ tiendas
- Control total en manos del usuario

REGLAS DE COPY:
- seQura siempre con Q mayúscula
- Datos concretos > promesas genéricas
- Hooks de video en <3 segundos
- CTAs: "Descubre", "Explora", "Empieza" — nunca "Más información"
- Frases cortas en ads: máximo 8-10 palabras por línea

CLAIMS REPETIBLES:
- "5 datos. 0 documentos. Menos de 1 minuto."
- "Tu compra, tus reglas."
- "2.5 millones de personas compran con seQura."
- "+6.000 tiendas donde comprar."
"""

COMPETIDORES = """
COMPETIDORES BNPL — ANÁLISIS BASE:

1. KLARNA: Líder global. "Smoooth shopping". Rosa/magenta. Celebrity-driven (Paris Hilton, Shaq).
   Debilidad: costoso, genérico, no enseña el proceso real.

2. SCALAPAY: "Take your time to enjoy". Premium, sofisticado. NPS 93 en España.
   Debilidad: demasiado aspiracional para mass market.

3. PAYPAL (Paga en 3): Confianza de marca. Muy funcional/corporativo.
   Debilidad: cero emoción, BNPL es secundario en su ecosistema.

4. REVOLUT: Super-app. BNPL como feature, no como producto estrella. Fee 1.65% por compra.
   Debilidad: BNPL diluido entre 10+ productos.

5. AFTERPAY: BNPL australiano con expansión global. "Easy way to pay". App de shopping integrada.
   Debilidad: menos presente en España, menos merchants locales.

6. ROBINHOOD: Más conocido en inversión. BNPL más reciente.
   Debilidad: poco posicionamiento en Europa/España.

QUÉ NO DICE NADIE (OPORTUNIDADES):
- Nadie muestra el proceso real de checkout paso a paso
- Nadie usa UGC auténtico como formato principal
- Nadie posiciona BNPL como "para gente inteligente que planifica"
- Nadie habla del ecosistema local con merchants específicos
- Nadie usa datos de recurrencia como proof point
"""

DATOS_MERCADO = """
DATOS DE MERCADO seQura (actualizado 2026):
- 2.5M+ shoppers activos
- 6.000+ merchants en España
- Recurrencia por sector: health&beauty 37.49% (3m), fashion 39.70% (3m), bazaar 31.61% (3m)
- Mercado BNPL España: crecimiento ~22% anual, proyección $11.75B en 2026
- 67% de consumidores españoles cambiaría de tienda para acceder a BNPL
- 54% de Gen Z usó BNPL en Navidad 2024 (vs 50% tarjetas — primera vez en la historia)
- 40% de Gen Z usa BNPL semanalmente o más
- Proceso seQura: 5 datos, 0 documentos, <1 minuto
- Regulación: CCD2 se implementa en 2026

DATOS INTERNOS (GA4 2025):
- 4.6M sesiones anuales
- 2M usuarios activos
- 1.7M usuarios nuevos (+297.8%)
- Engagement rate: 67.15%

DATOS APP (Mixpanel, Feb 2026):
- 152.600 unique users últimos 30 días
- MAU noviembre 2025: ~120.000 (+26.3% MoM)
"""

TEMPLATE_BRIEF = """
ESTRUCTURA EXACTA DEL BRIEF (secciones obligatorias):

1. CONTEXTO: Datos de campaña, situación actual con datos, contexto estratégico, contexto estacional, objetivo estratégico
2. OBJETIVOS DE CAMPAÑA: Objetivo principal, KPIs primarios (tabla), métrica norte, definición de éxito
3. AUDIENCIAS TARGET: Demografía, psicografía, comportamientos, segmentación por sector (tabla con % recurrencia)
4. PAIN POINTS A RESOLVER: Fricción percibida (tabla creencia errónea vs realidad seQura), necesidades no satisfechas, barreras emocionales
5. PROPUESTA DE VALOR Y MENSAJES CLAVE: Posicionamiento central, 5 pilares de valor
6. RESEARCH DE KEYWORDS: Keywords principales (tabla), keywords por vertical, keywords estacionales, recomendaciones de mensajes
7. ANÁLISIS DE COMPETENCIA: Mapa competitivo (tabla), qué dicen todos, qué NO dice nadie, URLs Meta Ads Library para revisión manual
8. INSIGHTS CLAVE: Insight central, 5 insights secundarios
9. ASSETS Y FORMATOS: Video UGC real, Video UGC AI HeyGen, materiales de soporte, piezas estáticas
10. GUÍA DE TONO Y VOZ: Qué NO queremos parecer, qué SÍ queremos proyectar, reglas de copy
11. GUÍA VISUAL PARA DISEÑO: Paleta de colores, tipografía, estilo fotográfico, formatos y tamaños
12. CANALES Y DISTRIBUCIÓN: Meta (FB+IG), TikTok — formatos, objetivos, audiencias
13. MERCADOS Y LOCALIZACIÓN: Mercados activos, % budget, consideraciones de producción
14. TIMING Y FASES: Fase 1 Lanzamiento, Fase 2 Optimización, Fase 3 Escalado
15. PRESUPUESTO Y RECURSOS: Media budget, distribución por mercado y canal
16. CRITERIOS DE ÉXITO: Cuantitativos (KPIs), cualitativos (mensajes, awareness)
17. PRÓXIMOS PASOS Y CHECKLIST: Checklist pre-kickoff, responsables y deadlines (tabla)
18. DATOS INVESTIGADOS: Research de soporte con fuentes
19. ANEXOS Y REFERENCIAS: Links clave, documentos internos
"""

# ── Función principal ─────────────────────────────────────────────────────────

def generar_brief(datos_campana: dict) -> dict:
    """
    Flujo completo:
    1. Guarda input en Airtable
    2. Genera brief con Claude
    3. Guarda secciones en Airtable con nombres exactos de campos
    4. Crea Google Doc con formato seQura
    5. Mueve a carpeta Drive y comparte con helena.fernandez@sequra.es
    6. Guarda URL en Airtable
    7. Devuelve link del doc
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # 1. Guardar input en Airtable
    nombre = datos_campana.get('nombre') or datos_campana.get('nombre_campana') or datos_campana.get('name', 'Sin nombre')
    datos_campana['nombre'] = nombre
    print(f"\n[Agente 1] 🚀 Iniciando brief para: {nombre}")
    record_id = crear_brief(datos_campana)
    print(f"[Agente 1] ✅ Registro creado en Airtable: {record_id}")

    # 2. Cargar knowledge base de Airtable
    print(f"[Agente 1] 📚 Cargando knowledge base...")
    knowledge = obtener_knowledge()
    datos_campana["knowledge"] = knowledge
    print(f"[Agente 1] ✅ Knowledge cargado: {list(knowledge.keys())}")

    # 3. Generar brief con Claude
    prompt = _construir_prompt(datos_campana)
    print(f"[Agente 1] 🤖 Generando brief con Claude...")
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )
    brief_completo = message.content[0].text
    print(f"[Agente 1] ✅ Brief generado ({len(brief_completo)} caracteres)")

    # 3. Extraer secciones y guardar en Airtable con nombres exactos
    secciones = _extraer_secciones(brief_completo)
    actualizar_brief(record_id, {
        "Brief_Generado":       secciones["brief_principal"],
        "Keywords":             secciones["Keywords"],
        "Analisis_Competencia": secciones["competencia"],
        "Insights":             secciones["Insights"],
        "Assets_Produccion":    secciones["assets"],
        "Planning_Presupuesto": secciones["planning"],
        "Aprendizajes_Previos": datos_campana.get("aprendizajes_previos", ""),
        "Estado":               "Pendiente",
        "Fecha_Creacion":       datetime.now().strftime("%Y-%m-%d"),
    })
    print(f"[Agente 1] ✅ Secciones guardadas en Airtable")

    # 4. Crear Google Doc y subir a Drive
    print(f"[Agente 1] 📄 Creando Google Doc...")
    doc_id, url_drive = _crear_google_doc(datos_campana, secciones, record_id)
    print(f"[Agente 1] ✅ Google Doc disponible en: {url_drive}")

    return {
        "record_id": record_id,
        "doc_id":    doc_id,
        "url_drive": url_drive,
        "brief":     brief_completo,
        "Estado":    "pendiente_aprobacion",
    }


def _construir_prompt(datos_campana: dict) -> str:
    return f"""Eres el Sub-agente 1 del pipeline de campañas paid marketing de seQura.
Tu tarea es generar un brief de campaña completo y profesional.

=== DATOS DE LA CAMPAÑA ===
- ID: {datos_campana.get('id_campana')}
- Nombre: {datos_campana.get('nombre')}
- Objetivo: {datos_campana.get('objetivo')}
- Audiencia: {datos_campana.get('audiencia')}
- Budget: €{datos_campana.get('budget', 'PENDIENTE')}
- Plataformas: {datos_campana.get('plataformas')}
- Fecha inicio: {datos_campana.get('fecha_inicio')}
- Fecha fin: {datos_campana.get('fecha_fin')}
- Duración: {datos_campana.get('duracion', 'PENDIENTE')}
- Mercados: {datos_campana.get('mercados', 'España')}
- Assets/formatos: {datos_campana.get('assets_formatos', 'PENDIENTE')}
- Qué NO queremos parecer: {datos_campana.get('no_queremos_parecer', 'Ver guía de marca')}
- Qué SÍ queremos proyectar: {datos_campana.get('si_queremos_proyectar', 'Ver guía de marca')}
- Aprendizajes previos: {datos_campana.get('aprendizajes_previos', 'Primera campaña')}

=== GUÍA DE MARCA Y VOZ ===
{BRAND_VOICE}

=== ANÁLISIS DE COMPETENCIA ===
{COMPETIDORES}

=== DATOS DE MERCADO Y PRODUCTO ===
{DATOS_MERCADO}

=== ESTRUCTURA DEL BRIEF ===
{TEMPLATE_BRIEF}

=== INSTRUCCIONES ===
1. Genera el brief COMPLETO con todas las secciones. No omitas ninguna.
2. Usa datos reales de seQura (2.5M shoppers, 6.000 tiendas, datos de recurrencia, etc.)
3. Si un dato no está disponible escribe: "PENDIENTE — confirmar antes del kick-off"
4. Para la sección 7, añade las URLs de Meta Ads Library de cada competidor para revisión manual.
5. Genera keywords reales y relevantes para el sector BNPL en los mercados indicados.
6. Escribe en español. Tono: profesional pero cercano, directo, basado en datos.
7. Usa ## para secciones principales y ### para subsecciones.
8. El output debe estar listo para entregar al equipo creativo tras un kick-off de 15 minutos.

Genera el brief completo ahora:"""


def _extraer_secciones(texto: str) -> dict:
    """Divide el brief completo en secciones para los campos de Airtable."""

    def extraer(desde: list, hasta: list) -> str:
        lineas = texto.split("\n")
        dentro = False
        resultado = []
        for linea in lineas:
            if any(m.upper() in linea.upper() for m in desde):
                dentro = True
                resultado.append(linea)
                continue
            if dentro and any(m.upper() in linea.upper() for m in hasta):
                break
            if dentro:
                resultado.append(linea)
        return "\n".join(resultado).strip()

    return {
        "brief_principal": extraer(
            ["1. CONTEXTO", "## 1"],
            ["6. RESEARCH", "## 6"]
        ),
        "Keywords": extraer(
            ["6. RESEARCH DE KEYWORDS", "## 6"],
            ["7. ANÁLISIS", "## 7"]
        ),
        "competencia": extraer(
            ["7. ANÁLISIS DE COMPETENCIA", "## 7"],
            ["8. INSIGHTS", "## 8"]
        ),
        "Insights": extraer(
            ["8. INSIGHTS CLAVE", "## 8"],
            ["9. ASSETS", "## 9"]
        ),
        "assets": extraer(
            ["9. ASSETS", "## 9"],
            ["14. TIMING", "15. TIMING", "## 14", "## 15"]
        ),
        "planning": extraer(
            ["14. TIMING", "15. TIMING", "## 14", "## 15"],
            ["ZZZZZ"]
        ),
    }


def _crear_google_doc(datos_campana: dict, secciones: dict, record_id: str) -> tuple:
    """Crea el Google Doc, lo comparte con Helena y guarda la URL en Airtable."""
    from integrations.google_docs import crear_brief_google_doc

    fecha_inicio = datos_campana.get("fecha_inicio", "")
    periodo      = datos_campana.get("duracion", fecha_inicio[:7] if fecha_inicio else "2026")

    brief_data = {
        "nombre":               datos_campana.get("nombre", "Campaña seQura"),
        "periodo":              periodo,
        "tipo":                 "ALWAYS-ON",
        "fecha":                datetime.now().strftime("%d/%m/%Y"),
        "brief_generado":       secciones["brief_principal"],
        "Keywords":             secciones["Keywords"],
        "analisis_competencia": secciones["competencia"],
        "Insights":             secciones["Insights"],
        "assets_produccion":    secciones["assets"],
        "planning_presupuesto": secciones["planning"],
    }

    doc_id, url = crear_brief_google_doc(brief_data)
    actualizar_brief(record_id, {"URL_Drive": url})
    return doc_id, url


# ── Gate 1 ────────────────────────────────────────────────────────────────────

def gate1_procesar_feedback(record_id: str, doc_id: str, aprobado: bool, feedback: str = "") -> dict:
    """
    Aprobado → pipeline continúa al Agente 2
    Rechazado → lee sugerencias del Google Doc y regenera
    """
    if aprobado:
        actualizar_brief(record_id, {"Estado": "Aprobado"})
        print(f"[Gate 1] ✅ Brief APROBADO — pasando al Agente 2")
        return {"Estado": "aprobado", "record_id": record_id, "doc_id": doc_id}

    # Leer sugerencias del Google Doc
    print(f"[Gate 1] ❌ Brief RECHAZADO — leyendo sugerencias del Google Doc...")
    from integrations.google_docs import leer_sugerencias
    sugerencias = leer_sugerencias(doc_id)

    feedback_completo = feedback
    if sugerencias:
        feedback_sugerencias = "\n".join([
            f"- [{s['tipo']}] {s['texto']}" for s in sugerencias
        ])
        feedback_completo = f"{feedback}\n\nSUGERENCIAS DEL GOOGLE DOC:\n{feedback_sugerencias}"

    actualizar_brief(record_id, {
        "Estado":           "Rechazado",
        "Feedback_Manager": feedback_completo,
    })

    print(f"[Gate 1] 🔄 Regenerando con {len(sugerencias)} sugerencias...")
    registro = _obtener_por_record_id(record_id)
    if registro:
        datos = registro["fields"]
        datos["aprendizajes_previos"] = f"FEEDBACK MANAGER:\n{feedback_completo}"
        return generar_brief(datos)

    return {"Estado": "rechazado", "feedback": feedback_completo}


def _obtener_por_record_id(record_id: str) -> dict:
    from pyairtable import Api
    from config.settings import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_BRIEFS
    api   = Api(AIRTABLE_API_KEY)
    tabla = api.base(AIRTABLE_BASE_ID).table(AIRTABLE_TABLE_BRIEFS)
    return tabla.get(record_id)
