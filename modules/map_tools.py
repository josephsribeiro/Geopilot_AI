"""
GeoPilot AI — Ferramentas de mapa (Leafmap + Folium)
"""

import json
import streamlit as st
from typing import Tuple, Optional

from utils.geometry_converter import geojson_to_ee_geometry


def render_map_section() -> Tuple[Optional[dict], Optional[object]]:
    """
    Renderiza o mapa interativo e retorna (geojson_dict, ee_geometry).
    O usuário pode desenhar polígonos, importar arquivos ou limpar a AOI.
    """
    col_map, col_ctrl = st.columns([3, 1], gap="medium")

    with col_ctrl:
        st.markdown("**Importar geometria**")
        uploaded_file = st.file_uploader(
            "GeoJSON / Shapefile / KML",
            type=["geojson", "json", "kml", "zip"],
            key="aoi_file_upload",
            label_visibility="collapsed",
        )

        if uploaded_file:
            _handle_file_upload(uploaded_file)

        if st.button("🗑️ Limpar AOI", use_container_width=True):
            st.session_state["aoi_geojson"] = None
            st.session_state["aoi_ee_geometry"] = None
            st.rerun()

        # Exportar geometria atual
        if st.session_state.get("aoi_geojson"):
            geojson_str = json.dumps(st.session_state["aoi_geojson"], indent=2)
            st.download_button(
                "⬇ Exportar AOI (GeoJSON)",
                data=geojson_str,
                file_name="aoi.geojson",
                mime="application/json",
                use_container_width=True,
            )

            # Info sobre a AOI
            try:
                coords = _extract_coords(st.session_state["aoi_geojson"])
                if coords:
                    st.markdown(f"**Vértices:** {len(coords)}")
            except Exception:
                pass

    with col_map:
        _render_interactive_map()

    # Retorna o estado atual da AOI
    aoi_geojson = st.session_state.get("aoi_geojson")
    aoi_ee = None
    if aoi_geojson and st.session_state.get("gee_authenticated"):
        try:
            aoi_ee = geojson_to_ee_geometry(aoi_geojson)
        except Exception:
            pass

    return aoi_geojson, aoi_ee


def _render_interactive_map():
    """Renderiza mapa Leafmap com ferramentas de desenho."""
    try:
        import leafmap.foliumap as leafmap  # type: ignore
        import folium  # type: ignore
        from folium.plugins import Draw, MousePosition  # type: ignore
        import streamlit.components.v1 as components

        m = leafmap.Map(
            center=[-14.235, -51.925],
            zoom=4,
            draw_control=False,
        )

        # Adiciona ferramentas de desenho
        draw = Draw(
            draw_options={
                "polygon":   {"allowIntersection": False, "shapeOptions": {"color": "#00e5ff", "weight": 2}},
                "rectangle": {"shapeOptions": {"color": "#00e5ff", "weight": 2}},
                "circle":    False,
                "marker":    False,
                "polyline":  False,
                "circlemarker": False,
            },
            edit_options={"edit": True, "remove": True},
        )
        draw.add_to(m)
        MousePosition().add_to(m)

        # Se já há AOI salva, adiciona ao mapa
        if st.session_state.get("aoi_geojson"):
            folium.GeoJson(
                st.session_state["aoi_geojson"],
                style_function=lambda _: {
                    "fillColor":   "#00e5ff",
                    "fillOpacity": 0.15,
                    "color":       "#00e5ff",
                    "weight":      2,
                },
                name="AOI",
            ).add_to(m)

        # Injeta JS para capturar geometrias desenhadas e enviar ao Streamlit
        map_html = _inject_draw_callback(m)
        components.html(map_html, height=480, scrolling=False)

    except ImportError:
        _render_fallback_map()


def _inject_draw_callback(m) -> str:
    """Injeta JS para capturar polígono desenhado e passar para o Streamlit via query param."""
    raw_html = m._repr_html_()

    callback_js = """
    <script>
    (function() {
      function waitForMap(cb, tries) {
        tries = tries || 0;
        var maps = Object.values(window).filter(function(v) {
          return v && typeof v === 'object' && v._container && v.eachLayer;
        });
        if (maps.length > 0) { cb(maps[0]); }
        else if (tries < 40) { setTimeout(function(){ waitForMap(cb, tries+1); }, 250); }
      }

      waitForMap(function(map) {
        map.on('draw:created', function(e) {
          var geojson = e.layer.toGeoJSON();
          var encoded = encodeURIComponent(JSON.stringify(geojson));
          var url = window.location.pathname + '?aoi_geojson=' + encoded;
          window.parent.postMessage({type: 'streamlit:setComponentValue', value: JSON.stringify(geojson)}, '*');
        });
      });
    })();
    </script>
    """
    return raw_html + callback_js


def _render_fallback_map():
    """Mapa de fallback simples com Folium quando Leafmap não está disponível."""
    try:
        import folium  # type: ignore
        from folium.plugins import Draw  # type: ignore
        import streamlit.components.v1 as components

        m = folium.Map(location=[-14.235, -51.925], zoom_start=4, tiles="OpenStreetMap")
        Draw(export=True).add_to(m)
        components.html(m._repr_html_(), height=480, scrolling=False)

        # Importação manual via textarea
        st.markdown("**Cole o GeoJSON da geometria desenhada:**")
        raw_json = st.text_area("GeoJSON", height=100, key="manual_geojson", label_visibility="collapsed")
        if raw_json:
            try:
                geojson = json.loads(raw_json)
                st.session_state["aoi_geojson"] = geojson
                st.success("✓ AOI carregada")
            except json.JSONDecodeError:
                st.error("JSON inválido.")

    except ImportError:
        st.warning("Instale `folium` e `leafmap` para visualização do mapa.")


def _handle_file_upload(uploaded_file):
    """Processa upload de GeoJSON, Shapefile ou KML."""
    try:
        filename = uploaded_file.name.lower()

        if filename.endswith((".geojson", ".json")):
            content = json.loads(uploaded_file.read())
            # Normaliza para Feature ou FeatureCollection
            if content.get("type") == "FeatureCollection":
                geojson = content["features"][0]["geometry"] if content["features"] else None
            elif content.get("type") == "Feature":
                geojson = content["geometry"]
            else:
                geojson = content  # Geometry puro
            st.session_state["aoi_geojson"] = geojson
            st.success("✓ GeoJSON importado")

        elif filename.endswith(".zip"):
            import geopandas as gpd  # type: ignore
            import tempfile, os, zipfile
            with tempfile.TemporaryDirectory() as tmp:
                zip_path = os.path.join(tmp, "shapefile.zip")
                with open(zip_path, "wb") as f:
                    f.write(uploaded_file.read())
                with zipfile.ZipFile(zip_path, "r") as z:
                    z.extractall(tmp)
                shp_files = [f for f in os.listdir(tmp) if f.endswith(".shp")]
                if shp_files:
                    gdf = gpd.read_file(os.path.join(tmp, shp_files[0]))
                    geom = json.loads(gdf.geometry.union_all().to_json() if hasattr(gdf.geometry, 'union_all') else gdf.geometry.unary_union.to_json())
                    st.session_state["aoi_geojson"] = geom
                    st.success("✓ Shapefile importado")

        elif filename.endswith(".kml"):
            import geopandas as gpd  # type: ignore
            import fiona  # type: ignore
            fiona.drvsupport.supported_drivers["KML"] = "rw"
            gdf = gpd.read_file(uploaded_file, driver="KML")
            geom = json.loads(gdf.geometry.union_all().to_json() if hasattr(gdf.geometry, 'union_all') else gdf.geometry.unary_union.to_json())
            st.session_state["aoi_geojson"] = geom
            st.success("✓ KML importado")

    except Exception as e:
        st.error(f"Erro ao importar arquivo: {e}")


def _extract_coords(geojson: dict) -> list:
    """Extrai lista de coordenadas de uma geometry."""
    if geojson.get("type") == "Polygon":
        return geojson["coordinates"][0]
    if geojson.get("type") == "MultiPolygon":
        return geojson["coordinates"][0][0]
    return []
