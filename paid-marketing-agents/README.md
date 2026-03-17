# 🤖 Pipeline Campañas Paid Marketing

Sistema multi-agente para automatizar el flujo completo de campañas de paid marketing.

## Estructura

```
paid-marketing-agents/
├── agents/
│   ├── agent1_brief.py        # Sub-agente 1: Generador de Brief
│   ├── agent2_creative.py     # Sub-agente 2: Strategic Creative
│   └── agent3_results.py      # Sub-agente 3: Análisis de Resultados
├── integrations/
│   ├── airtable.py            # Lectura/escritura en Airtable
│   ├── slack.py               # Notificaciones y gates via Slack
│   ├── meta_ads.py            # Extracción datos Meta Ads
│   ├── google_ads.py          # Extracción datos Google Ads
│   └── tiktok_ads.py          # Extracción datos TikTok Ads
├── config/
│   └── settings.py            # Variables de entorno centralizadas
├── utils/
│   └── helpers.py             # Funciones auxiliares
├── main.py                    # Orquestador principal
├── .env.example               # Plantilla de variables de entorno
└── requirements.txt
```

## Flujo del Pipeline

1. **Input** → Datos de campaña (nombre, objetivo, audiencia, budget, plataformas, fecha)
2. **Sub-agente 1** → Genera brief (keywords, análisis competencia, aprendizajes previos)
3. **Gate 1** → Manager aprueba el brief via Slack
4. **Sub-agente 2** → Genera territorios creativos (moodboard, 5 territorios, copy)
5. **Gate 2** → Manager aprueba el creative via Slack
6. **Equipo humano** → Produce piezas y lanza campaña (15 días)
7. **Sub-agente 3** → Extrae y analiza resultados de Meta/TikTok/Google Ads
8. **Gate 3** → Manager decide si iterar o cerrar campaña

## Setup

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 3. Correr el pipeline
python main.py
```

## Próximos pasos
- [ ] Configurar cuenta Airtable y crear las tablas
- [ ] Configurar Slack Bot
- [ ] Obtener API keys de plataformas de Ads
