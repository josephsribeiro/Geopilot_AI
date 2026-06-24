"""
GeoPilot AI — Geração de código GEE via Gemini API
"""

import json
from typing import Optional
from config.settings import GEMINI_SYSTEM_PROMPT
from modules.analysis_catalog import get_analysis_meta


def generate_gee_code(
    gemini_key: str,
    analysis_key: str,
    satellite: Optional[dict],
    aoi_geojson: dict,
    start_date: str,
    end_date: str,
    cloud_cover: int = 20,
    custom_text: str = "",
) -> str:
    """
    Chama a API Gemini para gerar código Python GEE.

    Args:
        gemini_key:   Chave da Gemini API
        analysis_key: Chave da análise (ex: 'ndvi') ou '__custom__'
        satellite:    Dict com metadados do satélite
        aoi_geojson:  GeoJSON da área de interesse
        start_date:   Data início (YYYY-MM-DD)
        end_date:     Data fim (YYYY-MM-DD)
        cloud_cover:  % máxima de cobertura de nuvens
        custom_text:  Texto de análise personalizada

    Returns:
        String com código Python puro
    """
    try:
        import google.generativeai as genai  # type: ignore
    except ImportError:
        raise ImportError(
            "Biblioteca `google-generativeai` não instalada. "
            "Execute: pip install google-generativeai"
        )

    genai.configure(api_key=gemini_key)

    # Modelos em ordem de preferência
    model_candidates = [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
    ]

    model = None
    last_error = None
    for model_name in model_candidates:
        try:
            candidate = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=GEMINI_SYSTEM_PROMPT,
            )
            # Teste rápido para confirmar disponibilidade
            candidate.generate_content("ok", generation_config={"max_output_tokens": 3})
            model = candidate
            break
        except Exception as e:
            last_error = e
            continue

    if model is None:
        raise RuntimeError(
            f"Nenhum modelo Gemini disponível. Último erro: {last_error}"
        )

    prompt = _build_prompt(
        analysis_key=analysis_key,
        satellite=satellite,
        aoi_geojson=aoi_geojson,
        start_date=start_date,
        end_date=end_date,
        cloud_cover=cloud_cover,
        custom_text=custom_text,
    )

    response = model.generate_content(prompt)
    raw_code = response.text.strip()

    # Remove blocos de markdown caso o modelo os inclua
    raw_code = _clean_code_output(raw_code)
    return raw_code


def _build_prompt(
    analysis_key: str,
    satellite: Optional[dict],
    aoi_geojson: dict,
    start_date: str,
    end_date: str,
    cloud_cover: int,
    custom_text: str,
) -> str:
    """Monta o prompt para o Gemini com todo o contexto necessário."""

    aoi_str = json.dumps(aoi_geojson)
    sat_info = _format_satellite_info(satellite)

    if analysis_key == "__custom__":
        analysis_description = f"""
ANÁLISE PERSONALIZADA SOLICITADA PELO USUÁRIO:
{custom_text}

Selecione automaticamente o melhor satélite e coleção GEE para esta análise.
"""
    else:
        meta = get_analysis_meta(analysis_key)
        analysis_description = f"""
ANÁLISE SOLICITADA: {meta.get('name', analysis_key)}
Descrição: {meta.get('description', '')}
Bandas necessárias: {', '.join(meta.get('bands_needed', []))}
Tipo de output: {meta.get('output_type', 'index')}
Range de valores: {meta.get('range', [-1, 1])}

{sat_info}
"""

    return f"""
Gere código Python para Google Earth Engine com as seguintes especificações:

{analysis_description}

CONTEXTO OBRIGATÓRIO (use exatamente estas variáveis no início do código):
```
import ee
ee.Initialize()

aoi = ee.Geometry.Polygon({json.dumps(aoi_geojson.get('coordinates', []))})
start_date = '{start_date}'
end_date = '{end_date}'
max_cloud_cover = {cloud_cover}
```

REQUISITOS DO CÓDIGO:
1. Use a variável `aoi` já definida acima
2. Use `start_date` e `end_date` já definidas
3. Filtre por cobertura de nuvens <= max_cloud_cover
4. Calcule o índice/análise solicitada
5. Gere visualização com geemap.Map() mostrando o resultado sobre o mapa base
6. Calcule estatísticas básicas (mean, min, max, std) usando reduceRegion
7. Exporte o print das estatísticas
8. Adicione legenda ao mapa quando aplicável
9. Salve o mapa como variável `Map` para visualização

RETORNE APENAS O CÓDIGO PYTHON. SEM TEXTO ADICIONAL.
"""


def _format_satellite_info(satellite: Optional[dict]) -> str:
    """Formata as informações do satélite para o prompt."""
    if not satellite:
        return "Use o satélite mais adequado para a análise."

    bands_str = "\n".join(
        f"  - {role}: '{band_name}'"
        for role, band_name in satellite.get("bands", {}).items()
    )

    scale_info = ""
    if satellite.get("scale_factor"):
        sf = satellite["scale_factor"]
        scale_info = f"""
Fator de escala óptico: {sf.get('optical', 1)}
Offset óptico: {sf.get('optical_offset', 0)}
"""

    return f"""
SATÉLITE SELECIONADO: {satellite.get('name', 'N/A')}
Coleção GEE: {satellite.get('collection', 'N/A')}
Resolução: {satellite.get('resolution_m', 30)}m
Propriedade de nuvem: {satellite.get('cloud_property', 'CLOUD_COVER')}
{scale_info}
Mapeamento de bandas:
{bands_str}
"""


def _clean_code_output(text: str) -> str:
    """Remove marcadores de markdown do código retornado pelo modelo."""
    lines = text.split("\n")
    clean_lines = []
    in_code_block = False

    for line in lines:
        if line.strip().startswith("```python"):
            in_code_block = True
            continue
        elif line.strip() == "```" and in_code_block:
            in_code_block = False
            continue
        elif line.strip().startswith("```") and not in_code_block:
            in_code_block = True
            continue
        clean_lines.append(line)

    result = "\n".join(clean_lines).strip()

    # Se não tinha bloco de código, retorna o texto como está
    if not result:
        return text.strip()

    return result
