"""
GeoPilot AI — Catálogo de satélites com mapeamento de bandas
"""

from typing import List, Dict, Any

# ─────────────────────────────────────────────
# Definição dos satélites
# ─────────────────────────────────────────────
SATELLITE_CATALOG: Dict[str, Dict[str, Any]] = {
    "sentinel2": {
        "name": "Sentinel-2",
        "collection": "COPERNICUS/S2_SR_HARMONIZED",
        "resolution_m": 10,
        "cloud_property": "CLOUDY_PIXEL_PERCENTAGE",
        "bands": {
            "BLUE":  "B2",
            "GREEN": "B3",
            "RED":   "B4",
            "RE1":   "B5",
            "RE2":   "B6",
            "RE3":   "B7",
            "NIR":   "B8",
            "NIRn":  "B8A",
            "SWIR1": "B11",
            "SWIR2": "B12",
        },
        "capabilities": [
            "ndvi", "savi", "evi", "ndwi", "mndwi", "turbidity",
            "ndbi", "urban_heat", "bsi", "nbr", "dnbr",
            "change_detection", "deforestation", "urban_expansion",
            "land_use", "supervised", "unsupervised",
        ],
    },
    "landsat9": {
        "name": "Landsat 9",
        "collection": "LANDSAT/LC09/C02/T1_L2",
        "resolution_m": 30,
        "cloud_property": "CLOUD_COVER",
        "scale_factor": {
            "optical": 0.0000275,
            "optical_offset": -0.2,
            "thermal": 0.00341802,
            "thermal_offset": 149.0,
        },
        "bands": {
            "BLUE":  "SR_B2",
            "GREEN": "SR_B3",
            "RED":   "SR_B4",
            "NIR":   "SR_B5",
            "SWIR1": "SR_B6",
            "SWIR2": "SR_B7",
            "TIR":   "ST_B10",
        },
        "capabilities": [
            "ndvi", "savi", "evi", "ndwi", "mndwi", "turbidity",
            "lst", "ndbi", "urban_heat", "bsi", "nbr", "dnbr",
            "change_detection", "deforestation", "urban_expansion",
            "land_use", "supervised", "unsupervised",
        ],
    },
    "landsat8": {
        "name": "Landsat 8",
        "collection": "LANDSAT/LC08/C02/T1_L2",
        "resolution_m": 30,
        "cloud_property": "CLOUD_COVER",
        "scale_factor": {
            "optical": 0.0000275,
            "optical_offset": -0.2,
            "thermal": 0.00341802,
            "thermal_offset": 149.0,
        },
        "bands": {
            "BLUE":  "SR_B2",
            "GREEN": "SR_B3",
            "RED":   "SR_B4",
            "NIR":   "SR_B5",
            "SWIR1": "SR_B6",
            "SWIR2": "SR_B7",
            "TIR":   "ST_B10",
        },
        "capabilities": [
            "ndvi", "savi", "evi", "ndwi", "mndwi", "turbidity",
            "lst", "ndbi", "urban_heat", "bsi", "nbr", "dnbr",
            "change_detection", "deforestation", "urban_expansion",
            "land_use", "supervised", "unsupervised",
        ],
    },
    "landsat7": {
        "name": "Landsat 7",
        "collection": "LANDSAT/LE07/C02/T1_L2",
        "resolution_m": 30,
        "cloud_property": "CLOUD_COVER",
        "bands": {
            "BLUE":  "SR_B1",
            "GREEN": "SR_B2",
            "RED":   "SR_B3",
            "NIR":   "SR_B4",
            "SWIR1": "SR_B5",
            "SWIR2": "SR_B7",
            "TIR":   "ST_B6",
        },
        "capabilities": [
            "ndvi", "savi", "evi", "ndwi", "mndwi",
            "lst", "ndbi", "bsi", "nbr", "dnbr",
            "change_detection", "deforestation", "land_use",
        ],
    },
    "landsat5": {
        "name": "Landsat 5",
        "collection": "LANDSAT/LT05/C02/T1_L2",
        "resolution_m": 30,
        "cloud_property": "CLOUD_COVER",
        "bands": {
            "BLUE":  "SR_B1",
            "GREEN": "SR_B2",
            "RED":   "SR_B3",
            "NIR":   "SR_B4",
            "SWIR1": "SR_B5",
            "SWIR2": "SR_B7",
            "TIR":   "ST_B6",
        },
        "capabilities": [
            "ndvi", "savi", "evi", "ndwi", "mndwi",
            "lst", "ndbi", "bsi", "nbr", "dnbr",
            "change_detection", "deforestation", "land_use",
        ],
    },
    "modis_terra": {
        "name": "MODIS Terra",
        "collection": "MODIS/061/MOD13A2",
        "resolution_m": 500,
        "cloud_property": "SummaryQA",
        "bands": {
            "NDVI":  "NDVI",
            "EVI":   "EVI",
            "RED":   "sur_refl_b01",
            "NIR":   "sur_refl_b02",
            "BLUE":  "sur_refl_b03",
            "GREEN": "sur_refl_b04",
            "SWIR1": "sur_refl_b06",
            "SWIR2": "sur_refl_b07",
        },
        "capabilities": [
            "ndvi", "evi", "ndwi",
            "lst", "change_detection", "deforestation",
        ],
    },
}


def get_satellites_for_analysis(analysis_key: str) -> List[Dict[str, Any]]:
    """
    Retorna lista de satélites compatíveis com a análise solicitada.

    Args:
        analysis_key: Chave da análise (ex: 'ndvi', 'lst')

    Returns:
        Lista de dicts com metadados dos satélites compatíveis
    """
    compatible = []
    for sat_key, sat_meta in SATELLITE_CATALOG.items():
        if analysis_key in sat_meta.get("capabilities", []):
            compatible.append({
                "key": sat_key,
                "name": sat_meta["name"],
                "collection": sat_meta["collection"],
                "resolution_m": sat_meta["resolution_m"],
                "cloud_property": sat_meta["cloud_property"],
                "bands": sat_meta["bands"],
                "scale_factor": sat_meta.get("scale_factor", {}),
            })
    return compatible


def get_satellite_meta(satellite_key: str) -> Dict[str, Any]:
    """Retorna metadados completos de um satélite pelo key."""
    return SATELLITE_CATALOG.get(satellite_key, {})
