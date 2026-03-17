import subprocess
import os
import json
import re
from datetime import datetime

def generar_brief_docx(brief_data: dict, output_path: str) -> str:
    """
    Genera el .docx del brief de campaña seQura.
    Usa el formato exacto del skill: colores seQura, tablas, headings.
    
    brief_data = {
        "nombre": "Campaña Always-On Q2 2026",
        "periodo": "Q2 2026",
        "tipo": "ALWAYS-ON",
        "fecha": "2026-04-01",
        "brief_generado": "...",
        "keywords": "...",
        "analisis_competencia": "...",
        "insights": "...",
        "assets_produccion": "...",
        "planning_presupuesto": "...",
    }
    """

    nombre = brief_data.get("nombre", "Campaña seQura")
    periodo = brief_data.get("periodo", datetime.now().strftime("%Y"))
    tipo = brief_data.get("tipo", "ALWAYS-ON").upper()
    fecha = brief_data.get("fecha", datetime.now().strftime("%d/%m/%Y"))

    # Nombre del archivo
    filename = f"BRIEF_CAMPAÑA_{tipo}_{periodo.replace(' ', '_')}_SeQura.docx"
    full_path = os.path.join(output_path, filename)

    # Escapar contenido para JSON
    def esc(text):
        if not text:
            return ""
        return (text
            .replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\r", ""))

    brief_texto = esc(brief_data.get("brief_generado", "PENDIENTE — completar antes del kick-off"))
    keywords_texto = esc(brief_data.get("keywords", "PENDIENTE"))
    competencia_texto = esc(brief_data.get("analisis_competencia", "PENDIENTE"))
    insights_texto = esc(brief_data.get("insights", "PENDIENTE"))
    assets_texto = esc(brief_data.get("assets_produccion", "PENDIENTE"))
    planning_texto = esc(brief_data.get("planning_presupuesto", "PENDIENTE"))

    js_code = f"""
const {{ Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, VerticalAlign, PageNumber, PageBreak, LevelFormat }} = require('docx');
const fs = require('fs');
const path = require('path');

// Colores seQura
const VERDE_TEAL = "00B4A2";
const AZUL_OSCURO = "1A1A2E";
const GRIS_FONDO = "F5F5F5";
const TEXTO_PRINCIPAL = "333333";
const BLANCO = "FFFFFF";
const GRIS_BORDE = "CCCCCC";
const GRIS_FILA = "F2F2F2";

// Helpers
function h1(text) {{
  return new Paragraph({{
    heading: HeadingLevel.HEADING_1,
    pageBreakBefore: true,
    children: [new TextRun({{ text, bold: true, size: 32, color: VERDE_TEAL, font: "Arial" }})]
  }});
}}

function h2(text) {{
  return new Paragraph({{
    heading: HeadingLevel.HEADING_2,
    children: [new TextRun({{ text, bold: true, size: 26, color: AZUL_OSCURO, font: "Arial" }})]
  }});
}}

function h3(text) {{
  return new Paragraph({{
    heading: HeadingLevel.HEADING_3,
    children: [new TextRun({{ text, bold: true, size: 22, color: VERDE_TEAL, font: "Arial" }})]
  }});
}}

function p(text, opts = {{}}) {{
  return new Paragraph({{
    children: [new TextRun({{ 
      text: text || " ", 
      size: opts.size || 22,
      color: opts.color || TEXTO_PRINCIPAL,
      bold: opts.bold || false,
      font: "Arial"
    }})]
  }});
}}

function spacer() {{
  return new Paragraph({{ children: [new TextRun({{ text: " ", size: 22 }})] }});
}}

// Convertir texto plano con secciones a paragrafos
function textToParas(text) {{
  if (!text) return [p("PENDIENTE — completar antes del kick-off")];
  const lines = text.split("\\n");
  return lines.map(line => {{
    const trimmed = line.trim();
    if (!trimmed) return spacer();
    if (trimmed.startsWith("## ")) return h2(trimmed.replace("## ", ""));
    if (trimmed.startsWith("### ")) return h3(trimmed.replace("### ", ""));
    if (trimmed.startsWith("**") && trimmed.endsWith("**")) 
      return p(trimmed.replace(/\\*\\*/g, ""), {{ bold: true }});
    if (trimmed.startsWith("- ") || trimmed.startsWith("• "))
      return new Paragraph({{
        numbering: {{ reference: "bullets", level: 0 }},
        children: [new TextRun({{ text: trimmed.replace(/^[-•] /, ""), size: 22, color: TEXTO_PRINCIPAL, font: "Arial" }})]
      }});
    return p(trimmed);
  }});
}}

const border = {{ style: BorderStyle.SINGLE, size: 1, color: GRIS_BORDE }};
const borders = {{ top: border, bottom: border, left: border, right: border }};

function headerCell(text, width) {{
  return new TableCell({{
    borders,
    width: {{ size: width, type: WidthType.DXA }},
    shading: {{ fill: VERDE_TEAL, type: ShadingType.CLEAR }},
    margins: {{ top: 80, bottom: 80, left: 120, right: 120 }},
    children: [new Paragraph({{ children: [new TextRun({{ text, bold: true, color: BLANCO, size: 20, font: "Arial" }})] }})]
  }});
}}

const doc = new Document({{
  numbering: {{
    config: [{{
      reference: "bullets",
      levels: [{{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
        style: {{ paragraph: {{ indent: {{ left: 720, hanging: 360 }} }} }} }}]
    }}]
  }},
  styles: {{
    default: {{ document: {{ run: {{ font: "Arial", size: 22, color: TEXTO_PRINCIPAL }} }} }},
    paragraphStyles: [
      {{ id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: {{ size: 32, bold: true, color: VERDE_TEAL, font: "Arial" }},
        paragraph: {{ spacing: {{ before: 240, after: 120 }}, outlineLevel: 0 }} }},
      {{ id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: {{ size: 26, bold: true, color: AZUL_OSCURO, font: "Arial" }},
        paragraph: {{ spacing: {{ before: 200, after: 100 }}, outlineLevel: 1 }} }},
      {{ id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: {{ size: 22, bold: true, color: VERDE_TEAL, font: "Arial" }},
        paragraph: {{ spacing: {{ before: 160, after: 80 }}, outlineLevel: 2 }} }},
    ]
  }},
  sections: [{{
    properties: {{
      page: {{
        size: {{ width: 11906, height: 16838 }},
        margin: {{ top: 1440, right: 1440, bottom: 1440, left: 1440 }}
      }}
    }},
    headers: {{
      default: new Header({{
        children: [new Paragraph({{
          border: {{ bottom: {{ style: BorderStyle.SINGLE, size: 6, color: VERDE_TEAL, space: 1 }} }},
          children: [
            new TextRun({{ text: "BRIEF CAMPAÑA {tipo} {periodo} | seQura", bold: true, size: 18, color: AZUL_OSCURO, font: "Arial" }}),
          ]
        }})]
      }})
    }},
    footers: {{
      default: new Footer({{
        children: [new Paragraph({{
          alignment: AlignmentType.RIGHT,
          children: [
            new TextRun({{ text: "Página ", size: 18, color: "999999", font: "Arial" }}),
            new TextRun({{ children: [new PageNumber()], size: 18, color: "999999", font: "Arial" }}),
          ]
        }})]
      }})
    }},
    children: [
      // ── PORTADA ──────────────────────────────────────────────────
      spacer(), spacer(), spacer(),
      new Paragraph({{
        alignment: AlignmentType.CENTER,
        children: [new TextRun({{ text: "BRIEF CAMPAÑA {tipo}", bold: true, size: 52, color: VERDE_TEAL, font: "Arial" }})]
      }}),
      new Paragraph({{
        alignment: AlignmentType.CENTER,
        children: [new TextRun({{ text: "{periodo}", bold: true, size: 44, color: AZUL_OSCURO, font: "Arial" }})]
      }}),
      spacer(),
      new Paragraph({{
        alignment: AlignmentType.CENTER,
        border: {{ bottom: {{ style: BorderStyle.SINGLE, size: 6, color: VERDE_TEAL, space: 1 }} }},
        children: [new TextRun({{ text: "seQura shopper acquisition & engagement", size: 26, color: "666666", font: "Arial" }})]
      }}),
      spacer(),
      new Paragraph({{
        alignment: AlignmentType.CENTER,
        children: [new TextRun({{ text: "Fecha de elaboración: {fecha}", size: 22, color: TEXTO_PRINCIPAL, font: "Arial" }})]
      }}),
      new Paragraph({{
        alignment: AlignmentType.CENTER,
        children: [new TextRun({{ text: "Equipo de Marketing — seQura", size: 22, color: TEXTO_PRINCIPAL, font: "Arial" }})]
      }}),
      new Paragraph({{ children: [new PageBreak()] }}),

      // ── SECCIONES 1-5: BRIEF PRINCIPAL ───────────────────────────
      h1("Brief de Campaña"),
      ...textToParas("{brief_texto}"),
      spacer(),

      // ── SECCIÓN 6: KEYWORDS ──────────────────────────────────────
      h1("6. Research de Keywords"),
      ...textToParas("{keywords_texto}"),
      spacer(),

      // ── SECCIÓN 7: COMPETENCIA ───────────────────────────────────
      h1("7. Análisis de Competencia"),
      ...textToParas("{competencia_texto}"),
      spacer(),

      // ── SECCIÓN 8: INSIGHTS ──────────────────────────────────────
      h1("8. Insights Clave"),
      ...textToParas("{insights_texto}"),
      spacer(),

      // ── SECCIONES 10-14: ASSETS Y PRODUCCIÓN ─────────────────────
      h1("Assets, Producción y Canales"),
      ...textToParas("{assets_texto}"),
      spacer(),

      // ── SECCIONES 15-20: PLANNING ────────────────────────────────
      h1("Planning, Presupuesto y Checklist"),
      ...textToParas("{planning_texto}"),
      spacer(),
    ]
  }}]
}});

const outputPath = "{full_path.replace(os.sep, '/')}";
Packer.toBuffer(doc).then(buffer => {{
  fs.writeFileSync(outputPath, buffer);
  console.log("OK:" + outputPath);
}}).catch(err => {{
  console.error("ERROR:" + err.message);
  process.exit(1);
}});
"""

    # Escribir y ejecutar el script JS
    js_path = "/tmp/generate_brief.js"
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js_code)

    result = subprocess.run(
        ["node", js_path],
        capture_output=True, text=True
    )

    if result.returncode != 0 or "ERROR:" in result.stdout:
        raise RuntimeError(f"Error generando .docx: {result.stderr or result.stdout}")

    print(f"[DOCX] Documento generado: {full_path}")
    return full_path, filename
