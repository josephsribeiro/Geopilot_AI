"""
GeoPilot AI — Catálogo de análises pré-configuradas
"""

from typing import Dict, Any


def get_analysis_catalog() -> Dict[str, Dict[str, Any]]:
    """Retorna o catálogo completo de análises organizadas por categoria."""
    return {
        "🌿 Vegetação": {
            "ndvi": {
                "name": "NDVI",
                "icon": "🌿",
                "description": "Índice de Vegetação por Diferença Normalizada",
                "bands_needed": ["NIR", "RED"],
                "output_type": "index",
                "range": [-1, 1],
            },
            "savi": {
                "name": "SAVI",
                "icon": "🌾",
                "description": "Índice de Vegetação Ajustado ao Solo",
                "bands_needed": ["NIR", "RED"],
                "output_type": "index",
                "range": [-1, 1],
            },
            "evi": {
                "name": "EVI",
                "icon": "🍀",
                "description": "Índice de Vegetação Melhorado",
                "bands_needed": ["NIR", "RED", "BLUE"],
                "output_type": "index",
                "range": [-1, 1],
            },
        },
        "💧 Recursos Hídricos": {
            "ndwi": {
                "name": "NDWI",
                "icon": "💧",
                "description": "Índice de Água por Diferença Normalizada",
                "bands_needed": ["GREEN", "NIR"],
                "output_type": "index",
                "range": [-1, 1],
            },
            "mndwi": {
                "name": "MNDWI",
                "icon": "🌊",
                "description": "Índice de Água Modificado por Diferença Normalizada",
                "bands_needed": ["GREEN", "SWIR1"],
                "output_type": "index",
                "range": [-1, 1],
            },
            "turbidity": {
                "name": "Índice de Turbidez",
                "icon": "🟤",
                "description": "Turbidez de corpos d'água superficiais",
                "bands_needed": ["RED", "GREEN"],
                "output_type": "index",
                "range": [0, 1],
            },
        },
        "🌡️ Temperatura": {
            "lst": {
                "name": "LST (Temperatura Superficial)",
                "icon": "🌡️",
                "description": "Land Surface Temperature em graus Celsius",
                "bands_needed": ["TIR"],
                "output_type": "temperature",
                "range": [-20, 60],
            },
        },
        "🏙️ Áreas Urbanas": {
            "ndbi": {
                "name": "NDBI",
                "icon": "🏗️",
                "description": "Índice de Área Construída por Diferença Normalizada",
                "bands_needed": ["SWIR1", "NIR"],
                "output_type": "index",
                "range": [-1, 1],
            },
            "urban_heat": {
                "name": "Ilhas de Calor Urbanas",
                "icon": "🔥",
                "description": "Identificação e mapeamento de ilhas de calor",
                "bands_needed": ["TIR", "SWIR1", "NIR"],
                "output_type": "classification",
                "range": [0, 5],
            },
        },
        "🟫 Solo": {
            "bsi": {
                "name": "BSI (Índice de Solo Exposto)",
                "icon": "🟫",
                "description": "Bare Soil Index — solo nu e degradado",
                "bands_needed": ["SWIR1", "RED", "NIR", "BLUE"],
                "output_type": "index",
                "range": [-1, 1],
            },
        },
        "🔥 Queimadas": {
            "nbr": {
                "name": "NBR",
                "icon": "🔥",
                "description": "Índice de Queima Normalizada",
                "bands_needed": ["NIR", "SWIR2"],
                "output_type": "index",
                "range": [-1, 1],
            },
            "dnbr": {
                "name": "dNBR",
                "icon": "💨",
                "description": "Delta NBR — severidade de queimadas",
                "bands_needed": ["NIR", "SWIR2"],
                "output_type": "index",
                "range": [-2, 2],
            },
        },
        "📈 Mudanças Temporais": {
            "change_detection": {
                "name": "Detecção de Mudanças",
                "icon": "🔄",
                "description": "Comparação temporal entre duas datas",
                "bands_needed": ["NIR", "RED"],
                "output_type": "classification",
                "range": [-2, 2],
            },
            "deforestation": {
                "name": "Monitoramento de Desmatamento",
                "icon": "🌳",
                "description": "Identificação de áreas desmatadas no período",
                "bands_needed": ["NIR", "RED", "SWIR1"],
                "output_type": "classification",
                "range": [0, 1],
            },
            "urban_expansion": {
                "name": "Expansão Urbana",
                "icon": "🏘️",
                "description": "Crescimento de áreas urbanas no período",
                "bands_needed": ["SWIR1", "NIR", "RED"],
                "output_type": "classification",
                "range": [0, 1],
            },
        },
        "🗺️ Classificação": {
            "land_use": {
                "name": "Uso e Cobertura da Terra",
                "icon": "🗺️",
                "description": "Mapeamento de classes de uso e cobertura",
                "bands_needed": ["ALL"],
                "output_type": "classification",
                "range": [1, 8],
            },
            "supervised": {
                "name": "Classificação Supervisionada",
                "icon": "🎯",
                "description": "Random Forest com amostras de treinamento",
                "bands_needed": ["ALL"],
                "output_type": "classification",
                "range": [1, 10],
            },
            "unsupervised": {
                "name": "Classificação Não Supervisionada",
                "icon": "🔮",
                "description": "Cluster K-means sem amostras de treinamento",
                "bands_needed": ["ALL"],
                "output_type": "classification",
                "range": [1, 10],
            },
        },
    }


def get_analysis_meta(analysis_key: str) -> dict:
    """Retorna metadados de uma análise pelo key."""
    catalog = get_analysis_catalog()
    for category in catalog.values():
        if analysis_key in category:
            return category[analysis_key]
    return {}
