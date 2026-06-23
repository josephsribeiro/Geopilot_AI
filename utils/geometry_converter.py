"""
GeoPilot AI — Conversor de geometrias GeoJSON ↔ GEE
"""

import json
from typing import Any, Dict, List, Optional, Union


def geojson_to_ee_geometry(geojson: dict) -> Any:
    """
    Converte um dicionário GeoJSON em ee.Geometry.

    Suporta: Point, MultiPoint, LineString, MultiLineString,
             Polygon, MultiPolygon, GeometryCollection, Feature, FeatureCollection

    Args:
        geojson: Dicionário com a geometria GeoJSON

    Returns:
        ee.Geometry object
    """
    try:
        import ee  # type: ignore
    except ImportError:
        raise ImportError("earthengine-api não instalado")

    geo_type = geojson.get("type", "")

    # Extrai geometria de Feature ou FeatureCollection
    if geo_type == "Feature":
        return geojson_to_ee_geometry(geojson["geometry"])

    if geo_type == "FeatureCollection":
        geometries = [geojson_to_ee_geometry(f["geometry"]) for f in geojson.get("features", [])]
        if not geometries:
            raise ValueError("FeatureCollection vazia")
        if len(geometries) == 1:
            return geometries[0]
        return ee.Geometry.MultiPolygon(
            [g.coordinates().getInfo() for g in geometries]
        )

    coords = geojson.get("coordinates")
    if coords is None:
        raise ValueError(f"GeoJSON sem coordenadas: {geojson}")

    handlers = {
        "Point":           lambda c: ee.Geometry.Point(c),
        "MultiPoint":      lambda c: ee.Geometry.MultiPoint(c),
        "LineString":      lambda c: ee.Geometry.LineString(c),
        "MultiLineString": lambda c: ee.Geometry.MultiLineString(c),
        "Polygon":         lambda c: ee.Geometry.Polygon(c),
        "MultiPolygon":    lambda c: ee.Geometry.MultiPolygon(c),
    }

    handler = handlers.get(geo_type)
    if handler is None:
        raise ValueError(f"Tipo de geometria não suportado: {geo_type}")

    return handler(coords)


def ee_geometry_to_geojson(ee_geom: Any) -> dict:
    """
    Converte um ee.Geometry em dicionário GeoJSON.

    Args:
        ee_geom: Objeto ee.Geometry

    Returns:
        Dict GeoJSON
    """
    return ee_geom.getInfo()


def bbox_from_geojson(geojson: dict) -> List[float]:
    """
    Calcula o bounding box (minx, miny, maxx, maxy) de uma geometria GeoJSON.

    Returns:
        [min_lon, min_lat, max_lon, max_lat]
    """
    coords = _flatten_coords(geojson)
    if not coords:
        raise ValueError("Não foi possível extrair coordenadas")

    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    return [min(lons), min(lats), max(lons), max(lats)]


def centroid_from_geojson(geojson: dict) -> tuple:
    """Retorna o centroide (lon, lat) de uma geometria GeoJSON."""
    bbox = bbox_from_geojson(geojson)
    return (
        (bbox[0] + bbox[2]) / 2,
        (bbox[1] + bbox[3]) / 2,
    )


def _flatten_coords(geojson: dict) -> List[List[float]]:
    """Achata todas as coordenadas de qualquer tipo de geometria."""
    geo_type = geojson.get("type", "")
    coords = geojson.get("coordinates", [])

    if geo_type == "Point":
        return [coords]
    if geo_type in ("MultiPoint", "LineString"):
        return coords
    if geo_type in ("MultiLineString", "Polygon"):
        return [p for ring in coords for p in ring]
    if geo_type == "MultiPolygon":
        return [p for poly in coords for ring in poly for p in ring]
    if geo_type == "Feature":
        return _flatten_coords(geojson.get("geometry", {}))
    if geo_type == "FeatureCollection":
        result = []
        for f in geojson.get("features", []):
            result.extend(_flatten_coords(f.get("geometry", {})))
        return result
    return []
