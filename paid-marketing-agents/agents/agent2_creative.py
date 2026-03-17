import anthropic
from datetime import datetime
from config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL
from integrations.airtable import (
    obtener_brief,
    crear_territorio,
    actualizar_territorio,
    obtener_territorio,
)

# ── Contexto creativo seQura ──────────────────────────────────────────────────

CONTEXTO_CREATIVO = """
TERRITORIOS CREATIVOS BASE seQura (adaptar y enriquecer según campaña):

TERRITORIO 1 — "La compra inteligente / Smart Shopping"
- Concepto: fraccionar es de personas que planifican bien, no de personas con problemas
- Tono: aspiracional pero realista
- Ejemplos de escena: persona en tienda de electrónica eligiendo el portátil que quiere (no el que puede pagar de golpe), pareja planificando reforma del hogar, joven eligiendo equipamiento deportivo premium

TERRITORIO 2 — "Más fácil imposible"
- Concepto: romper la creencia de que fraccionar es complicado
- Tono: directo, proof > promesa
- Ejemplos: countdown visual de 5 datos, comparaciones con procesos cotidianos ("más fácil que pedir una pizza"), demostración pantalla real del proceso

TERRITORIO 3 — "2.5 millones no se equivocan"
- Concepto: social proof masivo como argumento de confianza
- Tono: confianza colectiva, FOMO positivo
- Ejemplos: testimonios UGC reales, logos animados de merchants conocidos, cifra shoppers como protagonista

TERRITORIO 4 — "Tu compra, tus reglas"
- Concepto: flexibilidad y control como diferenciadores clave
- Tono: empoderador
- Ejemplos: interfaz mostrando opciones de pago, persona cambiando fecha de pago desde el móvil

FORMATOS DE OUTPUT:
- Video UGC (real humans): hooks <3 segundos, subtítulos always-on, 15-30s
- Video UGC AI HeyGen: mismo estilo, para mercados secundarios
- Estáticas Meta: Feed 1:1 (1080x1080), Stories 9:16 (1080x1920), Carruseles 3 cards
- Motion graphics: proceso de pago 5 pasos, animación "5 datos", social proof animado

REGLAS CREATIVAS:
- Hook en los primeros 3 segundos — crítico
- Datos concretos siempre: "5 datos" no "fácil", "2.5M+" no "millones"
- seQura siempre con Q mayúscula
- CTAs: "Descubre", "Explora", "Empieza" — nunca "Más información"
- Colores: verde teal #00B4A2 como color principal
- UGC supera a estáticas en CTR (3% vs 1.87% — datos Valentine's 2026)
"""

ESTRUCTURA_OUTPUT = """
ESTRUCTURA EXACTA DEL OUTPUT (obligatoria):

## MOODBOARD
Descripción detallada del universo visual de la campaña:
- Paleta de colores específica con códigos hex
- Estilo fotográfico (personas, ambientes, composición, luz)
- Tipografía y jerarquía visual
- Feeling general y referencias visuales

## TERRITORIO 1: [Nombre]
### Concepto
[Descripción del territorio y por qué conecta con el target]

### Concepto Madre
[La idea central en 1-2 frases. La "verdad" que ancla todo el territorio]

### Ejemplos de escenas (3 mínimo)
- Escena 1: [descripción detallada de situación, personaje, contexto, diálogo si aplica]
- Escena 2: [...]
- Escena 3: [...]

### Copy Version 1 — [Formato: Video Hook]
- Hook (0-3s): "[texto exacto]"
- Body (3-15s): "[texto exacto]"
- CTA: "[texto exacto]"

### Copy Version 2 — [Formato: Estática Feed]
- Headline: "[texto exacto]"
- Body: "[texto exacto]"
- CTA: "[texto exacto]"

### Copy Version 3 — [Formato: Stories/Reels]
- Hook: "[texto exacto]"
- Overlay text: "[texto exacto]"
- CTA: "[texto exacto]"

### Tono
[Descripción del tono específico para este territorio]

[Repetir estructura para TERRITORIOS 2, 3, 4 y 5]

## RECOMENDACIÓN DE PRIORIDAD
Tabla con ranking de territorios por potencial según brief + datos históricos:
| Territorio | Potencial | Justificación |
"""


# ── Función principal del agente ──────────────────────────────────────────────

def generar_territorios(id_campana: str) -> dict:
    """
    Sub-agente 2: Strategic Creative.
    Lee el brief aprobado de Airtable y genera los territorios creativos.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # 1. Obtener el brief aprobado de Airtable
    print(f"[Agente 2] Obteniendo brief aprobado para campaña: {id_campana}")
    registro = obtener_brief(id_campana)

    if not registro:
        raise ValueError(f"No se encontró brief para la campaña {id_campana}")

    campos = registro["fields"]
    brief_completo = campos.get("Brief_Generado", "")
    nombre_campana = campos.get("Nombre", id_campana)
    plataformas = campos.get("Plataformas", "Meta, TikTok")
    mercados = campos.get("Mercados", "España")
    objetivo = campos.get("Objetivo", "")
    audiencia = campos.get("Audiencia", "")

    print(f"[Agente 2] Brief obtenido para: {nombre_campana}")

    # 2. Crear registro en tabla Territorios
    territorio_record_id = crear_territorio(id_campana)

    # 3. Construir prompt
    prompt = f"""Eres el Sub-agente 2 del pipeline de campañas paid marketing de seQura.
Tu tarea es generar los territorios creativos a partir del brief aprobado.

=== BRIEF APROBADO ===
Campaña: {nombre_campana}
Objetivo: {objetivo}
Audiencia: {audiencia}
Plataformas: {plataformas}
Mercados: {mercados}

BRIEF COMPLETO:
{brief_completo[:4000]}

=== CONTEXTO CREATIVO seQura ===
{CONTEXTO_CREATIVO}

=== ESTRUCTURA DE OUTPUT REQUERIDA ===
{ESTRUCTURA_OUTPUT}

=== INSTRUCCIONES ===
1. Genera 5 territorios creativos (no 4 — queremos una opción extra para elegir)
2. Cada territorio debe tener: Concepto, Concepto Madre, 3 escenas, 3 versiones de copy
3. Los copies deben ser REALES y listos para usar — no placeholders
4. Adapta los territorios al objetivo y audiencia específicos de esta campaña
5. Prioriza formatos que funcionan para seQura: UGC video > estáticas (datos Valentine's 2026)
6. Los copies deben usar datos reales: "2.5M+ shoppers", "6.000+ tiendas", "5 datos, <1 minuto"
7. Incluye siempre el Concepto Madre — es la frase que el equipo creativo usará como norte
8. El moodboard debe ser suficientemente detallado para que diseño pueda empezar a trabajar
9. Escribe en español. Tono según guía de marca seQura.
10. Al final incluye tabla de recomendación de prioridad con justificación basada en datos

Genera el output completo ahora:"""

    print(f"[Agente 2] Llamando a Claude para generar territorios creativos...")

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )

    territorios_completos = message.content[0].text
    print(f"[Agente 2] Territorios generados ({len(territorios_completos)} caracteres)")

    # 4. Extraer secciones para Airtable
    moodboard = _extraer_bloque(territorios_completos, "MOODBOARD")
    copy_versiones = _extraer_copies(territorios_completos)

    # 5. Guardar en Airtable
    actualizar_territorio(territorio_record_id, {
        "Moodboard":      moodboard,
        "Territorios":    territorios_completos,
        "Concepto_Madre": _extraer_conceptos_madre(territorios_completos),
        "Copy_Versiones": copy_versiones,
        "Estado":         "Pendiente",
        "Fecha_Creacion": datetime.now().strftime("%Y-%m-%d"),
    })
    print(f"[Agente 2] Territorios guardados en Airtable: {territorio_record_id}")

    return {
        "record_id":   territorio_record_id,
        "territorios": territorios_completos,
        "moodboard":   moodboard,
        "estado":      "pendiente_aprobacion",
    }


# ── Helpers de extracción ─────────────────────────────────────────────────────

def _extraer_bloque(texto: str, titulo: str) -> str:
    """Extrae un bloque del output por título."""
    lineas = texto.split("\n")
    dentro = False
    resultado = []

    for linea in lineas:
        if f"## {titulo}" in linea or f"# {titulo}" in linea:
            dentro = True
            continue
        if dentro:
            if linea.startswith("## ") and titulo not in linea:
                break
            resultado.append(linea)

    return "\n".join(resultado).strip() or f"[Ver {titulo} en territorios completos]"


def _extraer_copies(texto: str) -> str:
    """Extrae todas las versiones de copy del output."""
    lineas = texto.split("\n")
    copies = []

    for i, linea in enumerate(lineas):
        if "Copy Version" in linea or "### Copy" in linea:
            bloque = [linea]
            for j in range(i + 1, min(i + 8, len(lineas))):
                if lineas[j].startswith("###") and j != i:
                    break
                bloque.append(lineas[j])
            copies.append("\n".join(bloque))

    return "\n\n---\n\n".join(copies) if copies else "[Ver copies en territorios completos]"


def _extraer_conceptos_madre(texto: str) -> str:
    """Extrae todos los Conceptos Madre de los territorios."""
    lineas = texto.split("\n")
    conceptos = []
    capturar = False

    for linea in lineas:
        if "Concepto Madre" in linea:
            capturar = True
            conceptos.append(f"\n{linea}")
            continue
        if capturar:
            if linea.startswith("###") or linea.startswith("##"):
                capturar = False
            else:
                conceptos.append(linea)

    return "\n".join(conceptos).strip() or "[Ver conceptos en territorios completos]"


# ── Gate 2: Aprobación del Manager ───────────────────────────────────────────

def gate2_procesar_feedback(record_id: str, id_campana: str, aprobado: bool, feedback: str = "") -> dict:
    """
    Procesa la decisión del Manager en el Gate 2.
    - Si aprobado=True: el pipeline continúa al equipo creativo
    - Si aprobado=False: el agente reintenta con el feedback
    """
    if aprobado:
        actualizar_territorio(record_id, {"Estado": "Aprobado"})
        print(f"[Gate 2] ✅ Territorios APROBADOS — pasando al equipo creativo")
        return {"estado": "aprobado", "record_id": record_id}
    else:
        actualizar_territorio(record_id, {
            "Estado":           "Rechazado",
            "Feedback_Manager": feedback,
        })
        print(f"[Gate 2] ❌ Territorios RECHAZADOS — feedback: {feedback}")
        print(f"[Gate 2] Reintentando con feedback...")

        # Regenerar incorporando el feedback en el brief
        registro_brief = obtener_brief(id_campana)
        if registro_brief:
            campos = registro_brief["fields"]
            brief_con_feedback = (
                campos.get("Brief_Generado", "") +
                f"\n\n=== FEEDBACK MANAGER GATE 2 ===\n{feedback}"
            )
            # Actualizar brief temporalmente con feedback y regenerar
            from integrations.airtable import actualizar_brief
            actualizar_brief(registro_brief["id"], {"Brief_Generado": brief_con_feedback})
            return generar_territorios(id_campana)

        return {"estado": "rechazado", "feedback": feedback}
