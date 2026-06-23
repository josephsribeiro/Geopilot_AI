"""
GeoPilot AI — Engine de execução do código GEE
"""

import sys
import io
import traceback
from typing import Any, Dict, Optional


def execute_gee_code(code: str, aoi_geojson: Optional[dict] = None) -> Dict[str, Any]:
    """
    Executa o código Python gerado pelo Gemini em um namespace isolado.

    Args:
        code:        Código Python para executar
        aoi_geojson: GeoJSON da AOI (injetado no namespace)

    Returns:
        Dict com: map_html, stats, charts, export_url, error
    """
    result: Dict[str, Any] = {
        "map_html":   None,
        "stats":      None,
        "charts":     [],
        "export_url": None,
        "error":      None,
        "stdout":     None,
    }

    # Captura stdout
    stdout_capture = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = stdout_capture

    try:
        # Namespace de execução
        exec_globals = _build_exec_namespace(aoi_geojson)

        # Executa o código
        exec(compile(code, "<geopilot_generated>", "exec"), exec_globals)  # noqa: S102

        # Restaura stdout
        sys.stdout = old_stdout
        result["stdout"] = stdout_capture.getvalue()

        # Extrai resultados do namespace
        result = _extract_results(exec_globals, result)

    except Exception:
        sys.stdout = old_stdout
        result["error"] = traceback.format_exc()

    return result


def _build_exec_namespace(aoi_geojson: Optional[dict]) -> dict:
    """Constrói o namespace de execução com imports e variáveis pré-definidas."""
    import json

    ns: dict = {}

    # Injeta imports básicos
    try:
        import ee          # type: ignore
        import geemap      # type: ignore
        import numpy as np
        import pandas as pd

        ns["ee"]      = ee
        ns["geemap"]  = geemap
        ns["np"]      = np
        ns["pd"]      = pd
        ns["numpy"]   = np
        ns["pandas"]  = pd
        ns["json"]    = json

    except ImportError as e:
        raise RuntimeError(f"Biblioteca não encontrada: {e}") from e

    # Injeta variáveis de contexto
    if aoi_geojson:
        try:
            coords = aoi_geojson.get("coordinates", [])
            geo_type = aoi_geojson.get("type", "Polygon")
            if geo_type == "Polygon":
                ns["aoi"] = ee.Geometry.Polygon(coords)
            elif geo_type == "MultiPolygon":
                ns["aoi"] = ee.Geometry.MultiPolygon(coords)
            else:
                ns["aoi"] = ee.Geometry(aoi_geojson)
        except Exception:
            ns["aoi"] = None

    # Folium disponível para visualização alternativa
    try:
        import folium  # type: ignore
        ns["folium"] = folium
    except ImportError:
        pass

    # Plotly para gráficos
    try:
        import plotly.express as px           # type: ignore
        import plotly.graph_objects as go     # type: ignore
        ns["px"] = px
        ns["go"] = go
    except ImportError:
        pass

    return ns


def _extract_results(exec_globals: dict, result: dict) -> dict:
    """Extrai e serializa os resultados do namespace pós-execução."""

    # Mapa Geemap
    if "Map" in exec_globals:
        try:
            gmap = exec_globals["Map"]
            if hasattr(gmap, "to_html"):
                result["map_html"] = gmap.to_html()
            elif hasattr(gmap, "_repr_html_"):
                result["map_html"] = gmap._repr_html_()
        except Exception:
            pass

    # Estatísticas
    for var_name in ["stats", "statistics", "result_stats", "stats_dict"]:
        if var_name in exec_globals and exec_globals[var_name] is not None:
            raw = exec_globals[var_name]
            if isinstance(raw, dict):
                result["stats"] = raw
                break
            # Tenta resolver ee.Dictionary
            try:
                if hasattr(raw, "getInfo"):
                    result["stats"] = raw.getInfo()
                    break
            except Exception:
                pass

    # Gráficos Plotly
    if "fig" in exec_globals:
        try:
            result["charts"].append(exec_globals["fig"])
        except Exception:
            pass

    # URL de exportação
    for var_name in ["export_url", "task_url", "export_link"]:
        if var_name in exec_globals and exec_globals[var_name]:
            result["export_url"] = exec_globals[var_name]
            break

    return result
