"""
GeoPilot AI — Configurações globais
"""

APP_CONFIG = {
    "name": "GeoPilot AI",
    "version": "1.0.0",
    "description": "Análise geoespacial com Google Earth Engine e Gemini AI",
    "gemini_model": "gemini-1.5-pro",
    "gee_project": "",          # Definido pelo usuário em runtime
    "default_map_center": [-14.235, -51.925],  # Centro do Brasil
    "default_map_zoom": 4,
    "max_aoi_area_km2": 100_000,
    "links": {
        "gemini_api_key": "https://aistudio.google.com/app/apikey",
        "gee_signup":     "https://earthengine.google.com/",
        "gee_docs":       "https://developers.google.com/earth-engine",
    },
}

# Prompt base enviado ao Gemini para geração de código GEE
GEMINI_SYSTEM_PROMPT = """
Você é um especialista em Google Earth Engine (GEE) e sensoriamento remoto.
Sua única função é gerar código Python puro e funcional para o GEE.

REGRAS ABSOLUTAS:
- Retorne APENAS código Python. Nenhum texto fora do código.
- Não inclua explicações, comentários extensos, justificativas ou conversas.
- O código deve ser executável diretamente pelo interpretador Python.
- Use a variável `aoi` (ee.Geometry já definida) como área de interesse.
- Use as datas `start_date` e `end_date` (strings 'YYYY-MM-DD' já definidas).
- Importe apenas bibliotecas disponíveis: ee, geemap, pandas, numpy.
- O código deve inicializar o GEE com `ee.Initialize()` no topo.
- Gere visualização usando geemap.Map() ou folium.
- Calcule estatísticas básicas da análise (mean, min, max, std).
- Exporte resultados quando solicitado.
- Trate erros com try/except básico.
- Mantenha o código limpo, conciso e Pythônico.
"""
