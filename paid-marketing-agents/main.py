import anthropic
import json
from datetime import datetime
from config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ── Prompt del orquestador conversacional ─────────────────────────────────────

SYSTEM_PROMPT = """Eres el asistente de marketing de seQura. Tu trabajo es ayudar a Helena a crear y gestionar campañas de paid marketing.

Tienes acceso a dos acciones principales:
1. GENERAR_BRIEF — cuando Helena quiere crear un nuevo brief de campaña
2. APLICAR_FEEDBACK — cuando Helena quiere aplicar las sugerencias de un Google Doc

=== FLUJO PARA GENERAR UN BRIEF ===
Cuando Helena quiera crear un brief, hazle estas preguntas de forma conversacional (no todas a la vez):

BLOQUE 1 — Lo esencial:
- ¿Cómo se llama la campaña y cuál es su objetivo principal?
- ¿Qué mercados cubre y cuándo empieza y termina?
- ¿Cuál es el budget aproximado?

BLOQUE 2 — El público y los canales:
- ¿A qué audiencia va dirigida?
- ¿En qué plataformas va a correr? (Meta, TikTok, Google...)
- ¿Qué formatos y assets necesitáis? (UGC, estáticas, carruseles...)

BLOQUE 3 — El tono y aprendizajes:
- ¿Qué NO queremos parecer en esta campaña?
- ¿Qué SÍ queremos proyectar?
- ¿Hay aprendizajes de campañas anteriores a tener en cuenta?

Una vez tengas toda la información, muestra un resumen estructurado y pregunta si puede arrancar.

Cuando Helena confirme, responde EXACTAMENTE con este JSON (sin texto adicional):
{"accion": "GENERAR_BRIEF", "datos": {<datos estructurados>}}

=== FLUJO PARA APLICAR FEEDBACK ===
Cuando Helena diga algo como "aplica las sugerencias", "revisa el doc", "aplica los cambios", pregúntale el ID del documento o la URL del Google Doc si no lo tienes.

Cuando tengas el doc_id, responde EXACTAMENTE con este JSON:
{"accion": "APLICAR_FEEDBACK", "doc_id": "<id>", "record_id": "<id>", "feedback": "<feedback adicional si lo hay>"}

=== REGLAS ===
- Habla siempre en español
- Sé conciso y directo — Helena es una profesional ocupada
- No hagas más de 2-3 preguntas a la vez
- Si Helena da varios datos en un mensaje, procésalos todos y pregunta solo lo que falta
- Cuando tengas todos los datos, muestra el resumen ANTES de arrancar
- Nunca inventes datos — si falta algo, pregunta o marca como PENDIENTE
"""

# ── Conversación principal ────────────────────────────────────────────────────

def main():
    print("\n" + "="*60)
    print("  🤖 seQura Marketing Agent")
    print("="*60)
    print("\nHola Helena! Puedo ayudarte a:")
    print("  • Crear un nuevo brief de campaña")
    print("  • Aplicar sugerencias de un Google Doc")
    print("\nEscribe 'salir' para terminar.\n")

    historial = []
    estado_pipeline = {}  # Guarda doc_id, record_id entre turnos

    while True:
        # Input de Helena
        try:
            user_input = input("Helena: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nHasta luego! 👋")
            break

        if user_input.lower() in ("salir", "exit", "quit"):
            print("\nHasta luego! 👋")
            break

        if not user_input:
            continue

        # Añadir mensaje al historial
        historial.append({"role": "user", "content": user_input})

        # Llamar a Claude
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=historial
        )

        respuesta = response.content[0].text.strip()

        # Detectar si es una acción JSON
        if respuesta.startswith("{") and '"accion"' in respuesta:
            accion_data = _procesar_accion(respuesta, estado_pipeline)
            if accion_data:
                # Añadir resultado al historial para continuar la conversación
                historial.append({"role": "assistant", "content": respuesta})
                historial.append({
                    "role": "user",
                    "content": f"[Sistema] Resultado: {json.dumps(accion_data, ensure_ascii=False)}"
                })
                # Pedir a Claude que comunique el resultado a Helena
                response2 = client.messages.create(
                    model=CLAUDE_MODEL,
                    max_tokens=1000,
                    system=SYSTEM_PROMPT,
                    messages=historial
                )
                respuesta_final = response2.content[0].text.strip()
                print(f"\n🤖 Agente: {respuesta_final}\n")
                historial.append({"role": "assistant", "content": respuesta_final})

                # Guardar estado del pipeline
                if "doc_id" in accion_data:
                    estado_pipeline["doc_id"]    = accion_data["doc_id"]
                    estado_pipeline["record_id"] = accion_data["record_id"]
            continue

        # Respuesta conversacional normal
        print(f"\n🤖 Agente: {respuesta}\n")
        historial.append({"role": "assistant", "content": respuesta})


def _procesar_accion(json_str: str, estado_pipeline: dict) -> dict:
    """Parsea la acción JSON y ejecuta el agente correspondiente."""
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        print("⚠️  Error parseando acción")
        return None

    accion = data.get("accion")

    # ── GENERAR BRIEF ──────────────────────────────────────
    if accion == "GENERAR_BRIEF":
        datos = data.get("datos", {})
        print("\n" + "─"*60)
        print("🚀 Arrancando pipeline de generación de brief...")
        print("─"*60)

        try:
            from agents.agent1_brief import generar_brief

            # Generar ID único para la campaña
            if not datos.get("id_campana"):
                datos["id_campana"] = f"CAMP-{datetime.now().strftime('%Y%m%d-%H%M')}"

            resultado = generar_brief(datos)

            print("\n" + "─"*60)
            print("✅ BRIEF GENERADO")
            print(f"   📄 Google Doc: {resultado['url_drive']}")
            print(f"   🗃️  Airtable ID: {resultado['record_id']}")
            print("─"*60 + "\n")

            return {
                "exito":     True,
                "doc_id":    resultado["doc_id"],
                "record_id": resultado["record_id"],
                "url_drive": resultado["url_drive"],
                "mensaje":   f"Brief generado y disponible en: {resultado['url_drive']}"
            }

        except Exception as e:
            print(f"\n❌ Error generando brief: {e}")
            return {"exito": False, "error": str(e)}

    # ── APLICAR FEEDBACK ───────────────────────────────────
    elif accion == "APLICAR_FEEDBACK":
        doc_id    = data.get("doc_id") or estado_pipeline.get("doc_id")
        record_id = data.get("record_id") or estado_pipeline.get("record_id")
        feedback  = data.get("feedback", "")

        if not doc_id or not record_id:
            print("⚠️  Falta doc_id o record_id para aplicar feedback")
            return {"exito": False, "error": "Falta doc_id o record_id"}

        print("\n" + "─"*60)
        print("🔄 Leyendo sugerencias del Google Doc y regenerando...")
        print("─"*60)

        try:
            from agents.agent1_brief import gate1_procesar_feedback

            resultado = gate1_procesar_feedback(
                record_id=record_id,
                doc_id=doc_id,
                aprobado=False,
                feedback=feedback
            )

            if resultado.get("estado") == "aprobado":
                return {"exito": True, "mensaje": "Brief aprobado, pasando al Agente 2"}

            print("\n" + "─"*60)
            print("✅ BRIEF ACTUALIZADO")
            print(f"   📄 Google Doc: {resultado.get('url_drive', '')}")
            print("─"*60 + "\n")

            return {
                "exito":     True,
                "doc_id":    resultado.get("doc_id"),
                "record_id": resultado.get("record_id"),
                "url_drive": resultado.get("url_drive"),
                "mensaje":   f"Brief actualizado con las sugerencias: {resultado.get('url_drive', '')}"
            }

        except Exception as e:
            print(f"\n❌ Error aplicando feedback: {e}")
            return {"exito": False, "error": str(e)}

    # ── APROBAR BRIEF → ARRANCAR AGENTE 2 ─────────────────
    elif accion == "APROBAR_BRIEF":
        record_id = data.get("record_id") or estado_pipeline.get("record_id")
        doc_id    = data.get("doc_id") or estado_pipeline.get("doc_id")

        print("\n" + "─"*60)
        print("✅ Brief aprobado — arrancando Agente 2...")
        print("─"*60)

        try:
            from agents.agent1_brief import gate1_procesar_feedback
            from agents.agent2_creative import generar_territorios

            gate1_procesar_feedback(record_id=record_id, doc_id=doc_id, aprobado=True)

            # Obtener ID_campaña del registro
            from agents.agent1_brief import _obtener_por_record_id
            registro = _obtener_por_record_id(record_id)
            id_campana = registro["fields"].get("ID_campaña", "")

            resultado = generar_territorios(id_campana)

            print("\n" + "─"*60)
            print("✅ TERRITORIOS CREATIVOS GENERADOS")
            print(f"   🗃️  Airtable ID: {resultado['record_id']}")
            print("─"*60 + "\n")

            return {
                "exito":     True,
                "record_id": resultado["record_id"],
                "mensaje":   "Territorios creativos generados en Airtable"
            }

        except Exception as e:
            print(f"\n❌ Error arrancando Agente 2: {e}")
            return {"exito": False, "error": str(e)}

    return None


if __name__ == "__main__":
    main()
