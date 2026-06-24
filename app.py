"""
GeoPilot AI — Gerador de código GEE com Gemini
Fluxo: Delimita AOI → Escolhe análise → Gemini gera código → Copia para GEE Code Editor ou baixa notebook
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import sys
import os
import urllib.parse

sys.path.insert(0, os.path.dirname(__file__))

from config.settings import APP_CONFIG
from modules.analysis_catalog import get_analysis_catalog
from modules.satellite_catalog import get_satellites_for_analysis
from modules.gemini_generator import generate_gee_code

# ─────────────────────────────────────────────
# Página
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="GeoPilot AI",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
.main .block-container { padding-top: 0 !important; max-width: 1280px; }

:root {
  --void:    #080c10;
  --deep:    #0d1117;
  --panel:   #131920;
  --border:  #1e2d3d;
  --signal:  #00e5ff;
  --pulse:   #39ff14;
  --warn:    #ff6b2b;
  --text-hi: #e8f4f8;
  --text-lo: #6b8fa3;
}

/* ── Hero ── */
.hero-wrapper {
  position: relative; background: var(--void);
  overflow: hidden; padding: 0 0 2rem 0; margin: 0 -1rem 2rem -1rem;
}
.hero-grid {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(0,229,255,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,229,255,0.04) 1px, transparent 1px);
  background-size: 48px 48px;
  animation: gridDrift 20s linear infinite;
}
@keyframes gridDrift { from{background-position:0 0} to{background-position:48px 48px} }
.hero-glow {
  position:absolute; top:-120px; left:50%; transform:translateX(-50%);
  width:700px; height:340px;
  background: radial-gradient(ellipse, rgba(0,229,255,0.12) 0%, transparent 70%);
  pointer-events:none;
}
.hero-content { position:relative; z-index:10; text-align:center; padding:3rem 2rem 1.5rem; }
.hero-eyebrow {
  display:inline-flex; align-items:center; gap:0.5rem;
  font-family:'JetBrains Mono',monospace; font-size:0.72rem;
  letter-spacing:0.22em; text-transform:uppercase; color:var(--signal);
  background:rgba(0,229,255,0.08); border:1px solid rgba(0,229,255,0.2);
  border-radius:2px; padding:0.3rem 0.85rem; margin-bottom:1.2rem;
}
.hero-eyebrow::before {
  content:''; display:inline-block; width:6px; height:6px;
  border-radius:50%; background:var(--pulse);
  animation: blink 1.4s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }
.hero-title {
  font-size: clamp(2.4rem,6vw,4rem); font-weight:700;
  letter-spacing:-0.03em; line-height:1.05; color:var(--text-hi); margin:0 0 0.5rem;
}
.hero-title .accent { color:var(--signal); text-shadow:0 0 40px rgba(0,229,255,0.35); }
.hero-sub {
  font-size:1rem; color:var(--text-lo); max-width:560px;
  margin:0 auto 1.8rem; line-height:1.65;
}
.hero-steps {
  display:flex; justify-content:center; gap:2rem; flex-wrap:wrap;
}
.step-item { text-align:center; }
.step-num {
  font-family:'JetBrains Mono',monospace; font-size:1.4rem;
  font-weight:500; color:var(--signal); display:block;
}
.step-label { font-size:0.7rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-lo); }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background:var(--deep) !important; border-right:1px solid var(--border); }
[data-testid="stSidebar"] * { color:var(--text-hi) !important; }
.sidebar-title {
  font-family:'JetBrains Mono',monospace; font-size:0.64rem;
  letter-spacing:0.18em; text-transform:uppercase; color:var(--text-lo) !important;
  border-bottom:1px solid var(--border); padding-bottom:0.4rem; margin:1rem 0 0.6rem;
}

/* ── Divisor ── */
.divider {
  display:flex; align-items:center; gap:1rem; margin:2rem 0 1.4rem;
}
.divider-line { flex:1; height:1px; background:var(--border); }
.divider-label {
  font-family:'JetBrains Mono',monospace; font-size:0.66rem;
  letter-spacing:0.15em; text-transform:uppercase; color:var(--text-lo);
}

/* ── Info / Warn panels ── */
.info-panel {
  background:rgba(0,229,255,0.05); border:1px solid rgba(0,229,255,0.15);
  border-radius:4px; padding:0.85rem 1rem; font-size:0.83rem;
  color:var(--text-lo); line-height:1.6; margin-bottom:1rem;
}
.warn-panel {
  background:rgba(255,107,43,0.05); border:1px solid rgba(255,107,43,0.2);
  border-radius:4px; padding:0.85rem 1rem; font-size:0.83rem;
  color:#c4856a; line-height:1.6; margin-bottom:1rem;
}
.success-panel {
  background:rgba(57,255,20,0.05); border:1px solid rgba(57,255,20,0.2);
  border-radius:4px; padding:0.85rem 1rem; font-size:0.83rem;
  color:#7bdb52; line-height:1.6; margin-bottom:1rem;
}

/* ── Botões ── */
.stButton > button {
  background:transparent; border:1px solid var(--signal); color:var(--signal);
  font-family:'Space Grotesk',sans-serif; font-size:0.85rem; font-weight:500;
  letter-spacing:0.04em; border-radius:3px; padding:0.5rem 1.2rem;
  transition:background 0.18s, color 0.18s;
}
.stButton > button:hover { background:var(--signal); color:var(--void); }
.stButton > button[kind="primary"] { background:var(--signal); color:var(--void); font-weight:600; }
.stButton > button[kind="primary"]:hover { background:#33eeff; }

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
  background:var(--panel) !important; border:1px solid var(--border) !important;
  color:var(--text-hi) !important; border-radius:3px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color:var(--signal) !important;
  box-shadow:0 0 0 2px rgba(0,229,255,0.12) !important;
}

/* ── Código gerado ── */
.code-box {
  background:#060a0e; border:1px solid var(--border); border-left:3px solid var(--pulse);
  border-radius:4px; padding:1.2rem; font-family:'JetBrains Mono',monospace;
  font-size:0.78rem; color:#9ecfde; white-space:pre-wrap; overflow-x:auto;
  max-height:500px; overflow-y:auto; line-height:1.55;
}

/* ── Badge ── */
.badge-ok  { display:inline-block; background:rgba(57,255,20,0.1); color:var(--pulse);
             border:1px solid rgba(57,255,20,0.25); border-radius:2px;
             font-family:'JetBrains Mono',monospace; font-size:0.68rem;
             padding:0.18rem 0.5rem; }

/* ── Destaque do passo de uso ── */
.use-card {
  background:var(--panel); border:1px solid var(--border); border-radius:6px;
  padding:1.1rem 1.3rem; text-align:center;
}
.use-card-num {
  font-family:'JetBrains Mono',monospace; font-size:1.6rem;
  color:var(--signal); display:block; margin-bottom:0.2rem;
}
.use-card-label { font-size:0.78rem; color:var(--text-lo); }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────
def init_session():
    defaults = {
        "gemini_key": "",
        "aoi_geojson": None,
        "selected_analysis": None,
        "selected_satellite": None,
        "generated_code": None,
        "custom_analysis_text": "",
        "date_start": "2023-01-01",
        "date_end": "2023-12-31",
        "cloud_cover": 20,
        "_sa_json_cache": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─────────────────────────────────────────────
# Hero
# ─────────────────────────────────────────────
def render_hero():
    st.markdown("""
    <div class="hero-wrapper">
      <div class="hero-grid"></div>
      <div class="hero-glow"></div>
      <div class="hero-content">
        <div class="hero-eyebrow">🛰️ &nbsp;Geospatial Intelligence Platform</div>
        <h1 class="hero-title">Geo<span class="accent">Pilot</span> AI</h1>
        <p class="hero-sub">
          Delimite sua área no mapa, escolha a análise —
          o Gemini gera o código GEE pronto para executar.
        </p>
        <div class="hero-steps">
          <div class="step-item"><span class="step-num">01</span><span class="step-label">Delimite a área</span></div>
          <div class="step-item"><span class="step-num">02</span><span class="step-label">Escolha a análise</span></div>
          <div class="step-item"><span class="step-num">03</span><span class="step-label">Gemini gera o código</span></div>
          <div class="step-item"><span class="step-num">04</span><span class="step-label">Execute no GEE</span></div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def divider(label):
    st.markdown(f"""
    <div class="divider">
      <div class="divider-line"></div>
      <div class="divider-label">{label}</div>
      <div class="divider-line"></div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # Gemini Key
        st.markdown('<p class="sidebar-title">🔑 Gemini API Key</p>', unsafe_allow_html=True)
        st.markdown(f'[Obter chave gratuita →]({APP_CONFIG["links"]["gemini_api_key"]})')
        key = st.text_input("API Key", type="password", placeholder="AIza…",
                            key="gemini_key_input", label_visibility="collapsed")
        st.session_state["gemini_key"] = key
        if key:
            st.markdown('<span class="badge-ok">✓ Chave configurada</span>', unsafe_allow_html=True)

        # Análise
        st.markdown('<p class="sidebar-title">📡 Análise</p>', unsafe_allow_html=True)
        catalog = get_analysis_catalog()
        options = {"🤖 Análise Personalizada": "__custom__"}
        for category, analyses in catalog.items():
            for k, meta in analyses.items():
                options[f"{meta['icon']} {meta['name']}"] = k

        selected_label = st.selectbox("Análise", list(options.keys()),
                                      label_visibility="collapsed", key="analysis_select")
        st.session_state["selected_analysis"] = options[selected_label]

        # Satélite (dinâmico)
        if st.session_state["selected_analysis"] != "__custom__":
            sats = get_satellites_for_analysis(st.session_state["selected_analysis"])
            if sats:
                st.markdown('<p class="sidebar-title">🛰️ Satélite</p>', unsafe_allow_html=True)
                sat_names = [s["name"] for s in sats]
                chosen = st.selectbox("Satélite", sat_names,
                                      label_visibility="collapsed", key="sat_select")
                st.session_state["selected_satellite"] = next(
                    (s for s in sats if s["name"] == chosen), sats[0])

        # Período
        st.markdown('<p class="sidebar-title">📅 Período</p>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            sd = st.date_input("Início", key="widget_start_date", label_visibility="visible")
        with c2:
            ed = st.date_input("Fim", key="widget_end_date", label_visibility="visible")
        st.session_state["date_start"] = str(sd)
        st.session_state["date_end"] = str(ed)

        # Nuvens
        st.markdown('<p class="sidebar-title">☁️ Cobertura de nuvens máx.</p>', unsafe_allow_html=True)
        cc = st.slider("Nuvens", 0, 100, 20, key="cloud_slider", label_visibility="collapsed")
        st.session_state["cloud_cover"] = cc

        # Análise personalizada
        if st.session_state["selected_analysis"] == "__custom__":
            st.markdown('<p class="sidebar-title">✏️ Descreva a análise</p>', unsafe_allow_html=True)
            txt = st.text_area("Análise", height=130, label_visibility="collapsed",
                               placeholder='Ex: "Mapear queimadas entre 2020 e 2023 com Sentinel-2"',
                               key="custom_text_input")
            st.session_state["custom_analysis_text"] = txt


# ─────────────────────────────────────────────
# Mapa interativo
# ─────────────────────────────────────────────
def render_map():
    divider("01 · Delimite sua Área de Interesse")

    st.markdown("""
    <div class="info-panel">
    🖊️ <strong>Desenhe um polígono</strong> no mapa usando a ferramenta de desenho (ícone de pentágono na barra esquerda do mapa).
    Após desenhar, clique em <strong>"Usar esta área"</strong>.
    Você também pode colar um GeoJSON manualmente.
    </div>
    """, unsafe_allow_html=True)

    # Mapa com Folium + Draw
    map_html = _build_folium_map()
    components.html(map_html, height=480, scrolling=False)

    # Área para colar GeoJSON manualmente
    col_paste, col_file = st.columns([2, 1], gap="medium")

    with col_paste:
        st.markdown("**Cole o GeoJSON da área desenhada:**")
        raw = st.text_area(
            "GeoJSON",
            height=90,
            key="geojson_paste",
            label_visibility="collapsed",
            placeholder='{"type":"Polygon","coordinates":[[[...]]]}',
        )
        if st.button("✔ Usar esta área", use_container_width=True):
            if raw.strip():
                try:
                    geom = json.loads(raw.strip())
                    # Aceita Feature ou Geometry
                    if geom.get("type") == "Feature":
                        geom = geom["geometry"]
                    if geom.get("type") == "FeatureCollection":
                        geom = geom["features"][0]["geometry"]
                    st.session_state["aoi_geojson"] = geom
                    st.success("✓ Área definida com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"GeoJSON inválido: {e}")
            else:
                st.warning("Cole o GeoJSON antes de confirmar.")

    with col_file:
        st.markdown("**Ou importe um arquivo:**")
        uploaded = st.file_uploader(
            "GeoJSON / Shapefile (zip) / KML",
            type=["geojson", "json", "zip", "kml"],
            key="aoi_upload",
            label_visibility="collapsed",
        )
        if uploaded:
            _handle_upload(uploaded)

    # Status da AOI
    if st.session_state.get("aoi_geojson"):
        aoi = st.session_state["aoi_geojson"]
        coords = aoi.get("coordinates", [[]])[0] if aoi.get("type") == "Polygon" else []
        st.markdown(
            f'<div class="success-panel">✓ <strong>AOI definida</strong> — '
            f'{len(coords)} vértices · tipo: {aoi.get("type","—")}</div>',
            unsafe_allow_html=True,
        )
        col_show, col_clear = st.columns([3, 1])
        with col_show:
            with st.expander("Ver GeoJSON da AOI"):
                st.code(json.dumps(aoi, indent=2), language="json")
        with col_clear:
            if st.button("🗑️ Limpar AOI", use_container_width=True):
                st.session_state["aoi_geojson"] = None
                st.rerun()


def _build_folium_map() -> str:
    """Constrói o HTML do mapa Folium com ferramentas de desenho."""
    try:
        import folium
        from folium.plugins import Draw, MousePosition

        m = folium.Map(location=[-14.235, -51.925], zoom_start=4, tiles="OpenStreetMap")

        Draw(
            draw_options={
                "polygon":      {"allowIntersection": False,
                                 "shapeOptions": {"color": "#00e5ff", "weight": 2, "fillOpacity": 0.1}},
                "rectangle":    {"shapeOptions": {"color": "#00e5ff", "weight": 2, "fillOpacity": 0.1}},
                "circle":       False,
                "marker":       False,
                "polyline":     False,
                "circlemarker": False,
            },
            edit_options={"edit": True, "remove": True},
            export=True,
        ).add_to(m)

        MousePosition().add_to(m)

        # Se já há AOI, mostra no mapa
        if st.session_state.get("aoi_geojson"):
            folium.GeoJson(
                st.session_state["aoi_geojson"],
                style_function=lambda _: {
                    "fillColor": "#00e5ff", "fillOpacity": 0.15,
                    "color": "#00e5ff", "weight": 2,
                },
            ).add_to(m)

        # Injeta instrução para copiar GeoJSON
        extra_js = """
        <script>
        document.addEventListener('DOMContentLoaded', function() {
          setTimeout(function() {
            var maps = document.querySelectorAll('.folium-map');
            if (!maps.length) return;
            var mapEl = maps[0];
            var leafletMap = Object.values(window).find(function(v){
              return v && v._container && v._container === mapEl;
            });
            if (!leafletMap) return;
            leafletMap.on('draw:created', function(e) {
              var geojson = JSON.stringify(e.layer.toGeoJSON().geometry, null, 2);
              var ta = window.parent.document.querySelector('textarea[data-testid="stTextArea"]');
              if (ta) { ta.value = geojson; ta.dispatchEvent(new Event('input', {bubbles:true})); }
            });
          }, 1000);
        });
        </script>
        """
        return m._repr_html_() + extra_js

    except ImportError:
        return "<p style='color:#6b8fa3;padding:1rem'>Instale folium: pip install folium</p>"


def _handle_upload(uploaded):
    """Processa arquivo enviado (GeoJSON, ZIP com shapefile, KML)."""
    try:
        name = uploaded.name.lower()
        if name.endswith((".geojson", ".json")):
            data = json.loads(uploaded.read())
            if data.get("type") == "Feature":
                data = data["geometry"]
            elif data.get("type") == "FeatureCollection":
                data = data["features"][0]["geometry"]
            st.session_state["aoi_geojson"] = data
            st.success("✓ GeoJSON importado")

        elif name.endswith(".zip"):
            import geopandas as gpd
            import tempfile, zipfile
            with tempfile.TemporaryDirectory() as tmp:
                zpath = os.path.join(tmp, "shp.zip")
                with open(zpath, "wb") as f:
                    f.write(uploaded.read())
                with zipfile.ZipFile(zpath) as z:
                    z.extractall(tmp)
                shps = [f for f in os.listdir(tmp) if f.endswith(".shp")]
                if shps:
                    gdf = gpd.read_file(os.path.join(tmp, shps[0]))
                    geom = json.loads(gdf.geometry.union_all().to_json()
                                      if hasattr(gdf.geometry, "union_all")
                                      else gdf.geometry.unary_union.to_json())
                    st.session_state["aoi_geojson"] = geom
                    st.success("✓ Shapefile importado")

        elif name.endswith(".kml"):
            import geopandas as gpd
            import fiona
            fiona.drvsupport.supported_drivers["KML"] = "rw"
            gdf = gpd.read_file(uploaded, driver="KML")
            geom = json.loads(gdf.geometry.union_all().to_json()
                              if hasattr(gdf.geometry, "union_all")
                              else gdf.geometry.unary_union.to_json())
            st.session_state["aoi_geojson"] = geom
            st.success("✓ KML importado")

        st.rerun()
    except Exception as e:
        st.error(f"Erro ao importar: {e}")


# ─────────────────────────────────────────────
# Geração de código
# ─────────────────────────────────────────────
def render_generate():
    divider("02 · Gerar Código GEE com Gemini")

    # Validações
    missing = []
    if not st.session_state.get("gemini_key"):
        missing.append("🔑 Chave Gemini API (sidebar)")
    if not st.session_state.get("aoi_geojson"):
        missing.append("🗺️ Área de Interesse (mapa acima)")
    if st.session_state.get("selected_analysis") == "__custom__" \
            and not st.session_state.get("custom_analysis_text", "").strip():
        missing.append("✏️ Descrição da análise personalizada (sidebar)")

    if missing:
        items = "".join(f"<li>{m}</li>" for m in missing)
        st.markdown(
            f'<div class="warn-panel">⚠️ Configure antes de gerar:<ul style="margin:0.4rem 0 0 1rem">{items}</ul></div>',
            unsafe_allow_html=True,
        )

    if st.button("⚡ Gerar Código com Gemini", type="primary",
                 disabled=bool(missing), use_container_width=False):
        with st.spinner("Consultando Gemini AI…"):
            try:
                code = generate_gee_code(
                    gemini_key=st.session_state["gemini_key"],
                    analysis_key=st.session_state["selected_analysis"],
                    satellite=st.session_state.get("selected_satellite"),
                    aoi_geojson=st.session_state["aoi_geojson"],
                    start_date=st.session_state.get("date_start", "2023-01-01"),
                    end_date=st.session_state.get("date_end", "2023-12-31"),
                    cloud_cover=st.session_state.get("cloud_cover", 20),
                    custom_text=st.session_state.get("custom_analysis_text", ""),
                )
                st.session_state["generated_code"] = code
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao chamar Gemini: {e}")


# ─────────────────────────────────────────────
# Exibição do código + instruções de uso
# ─────────────────────────────────────────────
def render_code_output():
    code = st.session_state.get("generated_code")
    if not code:
        return

    divider("03 · Código Gerado")

    st.markdown('<span class="badge-ok">✓ Código gerado pelo Gemini</span>', unsafe_allow_html=True)
    st.markdown("")

    # Código com syntax highlight
    st.code(code, language="python")

    # Botões de ação
    col1, col2, col3 = st.columns([1, 1, 1], gap="small")

    with col1:
        st.download_button(
            "⬇ Baixar .py",
            data=code,
            file_name="geopilot_analysis.py",
            mime="text/plain",
            use_container_width=True,
        )

    with col2:
        # Gera link para abrir o GEE Code Editor
        gee_editor_url = "https://code.earthengine.google.com/"
        st.link_button("🌍 Abrir GEE Code Editor", gee_editor_url, use_container_width=True)

    with col3:
        # Gera notebook Colab com o código
        notebook_content = _build_colab_notebook(code)
        st.download_button(
            "📓 Baixar notebook Colab",
            data=json.dumps(notebook_content, indent=2),
            file_name="geopilot_analysis.ipynb",
            mime="application/json",
            use_container_width=True,
        )

    # Instruções de uso
    divider("04 · Como Executar")

    tab1, tab2 = st.tabs(["🌍 GEE Code Editor (recomendado)", "📓 Google Colab"])

    with tab1:
        st.markdown("""
**3 passos para executar no GEE Code Editor:**

**1.** Clique em **"Abrir GEE Code Editor"** acima — abre o editor oficial do Google Earth Engine

**2.** Copie o código gerado (botão ⬇ ou selecione tudo com `Ctrl+A`) e cole no editor

**3.** Clique em **"Run"** — o resultado aparece no mapa e no painel Console

> 💡 O GEE Code Editor aceita Python e JavaScript. O código gerado é Python puro via `earthengine-api`.
> Se preferir JavaScript, peça ao Gemini: basta mudar a descrição para "gere em JavaScript para GEE".
        """)

    with tab2:
        colab_url = _build_colab_url(code)
        st.markdown(f"""
**3 passos para executar no Google Colab:**

**1.** Baixe o arquivo `.ipynb` (botão acima) ou [abra direto no Colab]({colab_url})

**2.** Execute a primeira célula — ela instala as dependências e autentica no GEE via `ee.Authenticate()`

**3.** Execute as células seguintes — os mapas aparecem inline no notebook

> 💡 O Colab usa sua conta Google para autenticar no GEE automaticamente. Não precisa configurar nada.
        """)


def _build_colab_notebook(code: str) -> dict:
    """Gera estrutura de notebook Jupyter/Colab com o código."""
    install_cell = (
        "# Instalar dependências\n"
        "!pip install earthengine-api geemap folium -q\n\n"
        "# Autenticar no Google Earth Engine\n"
        "import ee\n"
        "ee.Authenticate()\n"
        "ee.Initialize(project='YOUR_PROJECT_ID')  # Substitua pelo seu Project ID"
    )

    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.10.0"},
            "colab": {"provenance": []},
        },
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# 🛰️ GeoPilot AI — Análise Geoespacial\n",
                    "> Código gerado automaticamente pelo GeoPilot AI com Google Gemini.\n",
                    "> Execute as células em ordem. O GEE pedirá autorização na primeira execução."
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [install_cell],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [code],
            },
        ],
    }


def _build_colab_url(code: str) -> str:
    """Retorna URL do Colab com o código pré-carregado via gist (fallback para url simples)."""
    return "https://colab.research.google.com/#create=true"


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
def main():
    init_session()
    render_hero()
    render_sidebar()
    render_map()
    render_generate()
    render_code_output()


if __name__ == "__main__":
    main()
