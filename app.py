"""
GeoPilot AI — Gerador de código GEE com Gemini
Fluxo: Delimita AOI no mapa → Escolhe análise → Verifica imagens → Gemini gera código
"""

import streamlit as st
import streamlit.components.v1 as components
import json, sys, os, datetime

sys.path.insert(0, os.path.dirname(__file__))

from config.settings import APP_CONFIG
from modules.analysis_catalog import get_analysis_catalog
from modules.satellite_catalog import get_satellites_for_analysis
from modules.gemini_generator import generate_gee_code

st.set_page_config(
    page_title="GeoPilot AI",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS global
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family:'Space Grotesk',sans-serif; }
.main .block-container { padding-top:0 !important; max-width:1280px; }

:root {
  --void:#080c10; --deep:#0d1117; --panel:#131920; --border:#1e2d3d;
  --signal:#00e5ff; --pulse:#39ff14; --warn:#ff6b2b;
  --text-hi:#e8f4f8; --text-lo:#6b8fa3;
}

/* ── Hero ── */
.hero-wrapper{position:relative;background:var(--void);overflow:hidden;padding:0 0 2rem;margin:0 -1rem 2rem}
.hero-grid{position:absolute;inset:0;
  background-image:linear-gradient(rgba(0,229,255,.04) 1px,transparent 1px),
  linear-gradient(90deg,rgba(0,229,255,.04) 1px,transparent 1px);
  background-size:48px 48px;animation:gridDrift 20s linear infinite}
@keyframes gridDrift{from{background-position:0 0}to{background-position:48px 48px}}
.hero-glow{position:absolute;top:-120px;left:50%;transform:translateX(-50%);
  width:700px;height:340px;
  background:radial-gradient(ellipse,rgba(0,229,255,.12) 0%,transparent 70%);pointer-events:none}
.hero-content{position:relative;z-index:10;text-align:center;padding:3rem 2rem 1.5rem}
.hero-eyebrow{display:inline-flex;align-items:center;gap:.5rem;
  font-family:'JetBrains Mono',monospace;font-size:.72rem;
  letter-spacing:.22em;text-transform:uppercase;color:var(--signal);
  background:rgba(0,229,255,.08);border:1px solid rgba(0,229,255,.2);
  border-radius:2px;padding:.3rem .85rem;margin-bottom:1.2rem}
.hero-eyebrow::before{content:'';display:inline-block;width:6px;height:6px;
  border-radius:50%;background:var(--pulse);animation:blink 1.4s ease-in-out infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.2}}
.hero-title{font-size:clamp(2.4rem,6vw,4rem);font-weight:700;
  letter-spacing:-.03em;line-height:1.05;color:var(--text-hi);margin:0 0 .5rem}
.hero-title .accent{color:var(--signal);text-shadow:0 0 40px rgba(0,229,255,.35)}
.hero-sub{font-size:1rem;color:var(--text-lo);max-width:560px;margin:0 auto 1.8rem;line-height:1.65}
.hero-steps{display:flex;justify-content:center;gap:2rem;flex-wrap:wrap}
.step-item{text-align:center}
.step-num{font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:500;color:var(--signal);display:block}
.step-label{font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;color:var(--text-lo)}

/* ── Sidebar ── */
[data-testid="stSidebar"]{background:var(--deep) !important;border-right:1px solid var(--border)}
[data-testid="stSidebar"] *{color:var(--text-hi) !important}
.sidebar-title{font-family:'JetBrains Mono',monospace;font-size:.64rem;
  letter-spacing:.18em;text-transform:uppercase;color:var(--text-lo) !important;
  border-bottom:1px solid var(--border);padding-bottom:.4rem;margin:1rem 0 .6rem}

/* ── Inputs — texto escuro em fundo branco (tema padrão Streamlit) ── */
.stTextInput input,
.stTextArea textarea {
  background:#ffffff !important;
  color:#1a1a2e !important;
  border:1px solid #c8d6e5 !important;
  border-radius:4px !important;
  font-size:.9rem !important;
}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder { color:#7a8fa6 !important; }
.stTextInput input:focus,
.stTextArea textarea:focus {
  border-color:var(--signal) !important;
  box-shadow:0 0 0 2px rgba(0,229,255,.15) !important;
  outline:none !important;
}
/* Sidebar inputs — fundo escuro mantém texto claro */
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextArea textarea {
  background:var(--panel) !important;
  color:var(--text-hi) !important;
  border:1px solid var(--border) !important;
}
[data-testid="stSidebar"] .stTextInput input::placeholder,
[data-testid="stSidebar"] .stTextArea textarea::placeholder { color:var(--text-lo) !important; }

/* date_input e selectbox */
[data-testid="stDateInput"] input,
[data-testid="stSelectbox"] > div > div {
  background:#ffffff !important; color:#1a1a2e !important;
  border:1px solid #c8d6e5 !important; border-radius:4px !important;
}
[data-testid="stSidebar"] [data-testid="stDateInput"] input,
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
  background:var(--panel) !important; color:var(--text-hi) !important;
  border:1px solid var(--border) !important;
}

/* ── Divisor ── */
.divider{display:flex;align-items:center;gap:1rem;margin:2rem 0 1.4rem}
.divider-line{flex:1;height:1px;background:var(--border)}
.divider-label{font-family:'JetBrains Mono',monospace;font-size:.66rem;
  letter-spacing:.15em;text-transform:uppercase;color:var(--text-lo)}

/* ── Painéis ── */
.info-panel{background:rgba(0,229,255,.05);border:1px solid rgba(0,229,255,.15);
  border-radius:4px;padding:.85rem 1rem;font-size:.83rem;color:var(--text-lo);line-height:1.6;margin-bottom:1rem}
.warn-panel{background:rgba(255,107,43,.05);border:1px solid rgba(255,107,43,.2);
  border-radius:4px;padding:.85rem 1rem;font-size:.83rem;color:#c4856a;line-height:1.6;margin-bottom:1rem}
.success-panel{background:rgba(57,255,20,.05);border:1px solid rgba(57,255,20,.2);
  border-radius:4px;padding:.85rem 1rem;font-size:.83rem;color:#7bdb52;line-height:1.6;margin-bottom:1rem}
.img-count-panel{background:rgba(0,229,255,.07);border:1px solid rgba(0,229,255,.25);
  border-radius:6px;padding:1rem 1.2rem;margin-top:.8rem}
.img-count-num{font-family:'JetBrains Mono',monospace;font-size:2rem;
  font-weight:600;color:var(--signal);display:block;line-height:1}
.img-count-label{font-size:.75rem;color:var(--text-lo);text-transform:uppercase;
  letter-spacing:.1em;display:block;margin-top:.2rem}
.img-count-zero{color:var(--warn)}

/* ── Botões ── */
.stButton>button{background:transparent;border:1px solid var(--signal);color:var(--signal);
  font-family:'Space Grotesk',sans-serif;font-size:.85rem;font-weight:500;
  border-radius:3px;padding:.5rem 1.2rem;transition:background .18s,color .18s}
.stButton>button:hover{background:var(--signal);color:var(--void)}
.stButton>button[kind="primary"]{background:var(--signal);color:var(--void);font-weight:600}
.stButton>button[kind="primary"]:hover{background:#33eeff}

/* ── Badge ── */
.badge-ok{display:inline-block;background:rgba(57,255,20,.1);color:var(--pulse);
  border:1px solid rgba(57,255,20,.25);border-radius:2px;
  font-family:'JetBrains Mono',monospace;font-size:.68rem;padding:.18rem .5rem}
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
        "img_count": None,
        "img_count_checked": False,
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
      <div class="hero-grid"></div><div class="hero-glow"></div>
      <div class="hero-content">
        <div class="hero-eyebrow">🛰️ &nbsp;Geospatial Intelligence Platform</div>
        <h1 class="hero-title">Geo<span class="accent">Pilot</span> AI</h1>
        <p class="hero-sub">Delimite sua área no mapa, escolha a análise —
        o Gemini gera o código GEE pronto para executar.</p>
        <div class="hero-steps">
          <div class="step-item"><span class="step-num">01</span><span class="step-label">Delimite a área</span></div>
          <div class="step-item"><span class="step-num">02</span><span class="step-label">Escolha a análise</span></div>
          <div class="step-item"><span class="step-num">03</span><span class="step-label">Verifique imagens</span></div>
          <div class="step-item"><span class="step-num">04</span><span class="step-label">Gere o código</span></div>
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

        prev_analysis = st.session_state.get("selected_analysis")
        selected_label = st.selectbox("Análise", list(options.keys()),
                                      label_visibility="collapsed", key="analysis_select")
        st.session_state["selected_analysis"] = options[selected_label]

        # Reseta contagem ao trocar análise ou satélite
        if st.session_state["selected_analysis"] != prev_analysis:
            st.session_state["img_count"] = None
            st.session_state["img_count_checked"] = False

        # Satélite dinâmico
        if st.session_state["selected_analysis"] != "__custom__":
            sats = get_satellites_for_analysis(st.session_state["selected_analysis"])
            if sats:
                st.markdown('<p class="sidebar-title">🛰️ Satélite</p>', unsafe_allow_html=True)
                sat_names = [s["name"] for s in sats]
                prev_sat = (st.session_state.get("selected_satellite") or {}).get("name")
                chosen = st.selectbox("Satélite", sat_names,
                                      label_visibility="collapsed", key="sat_select")
                if chosen != prev_sat:
                    st.session_state["img_count"] = None
                    st.session_state["img_count_checked"] = False
                st.session_state["selected_satellite"] = next(
                    (s for s in sats if s["name"] == chosen), sats[0])

        # Período + verificação de imagens
        st.markdown('<p class="sidebar-title">📅 Período</p>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            sd = st.date_input("Início", key="widget_start_date", label_visibility="visible")
        with c2:
            ed = st.date_input("Fim", key="widget_end_date", label_visibility="visible")
        st.session_state["date_start"] = str(sd)
        st.session_state["date_end"] = str(ed)

        # Cobertura de nuvens
        st.markdown('<p class="sidebar-title">☁️ Nuvens máx. (%)</p>', unsafe_allow_html=True)
        cc = st.slider("Nuvens", 0, 100, 20, key="cloud_slider", label_visibility="collapsed")
        st.session_state["cloud_cover"] = cc



        # Análise personalizada
        if st.session_state["selected_analysis"] == "__custom__":
            st.markdown('<p class="sidebar-title">✏️ Descreva a análise</p>', unsafe_allow_html=True)
            txt = st.text_area("Análise", height=130, label_visibility="collapsed",
                               placeholder='Ex: "Mapear queimadas entre 2020 e 2023 com Sentinel-2"',
                               key="custom_text_input")
            st.session_state["custom_analysis_text"] = txt


def _check_image_count():
    """Verifica quantas imagens estão disponíveis no GEE para o período e AOI."""
    sat = st.session_state.get("selected_satellite")
    aoi = st.session_state.get("aoi_geojson")
    start = st.session_state.get("date_start", "2023-01-01")
    end = st.session_state.get("date_end", "2023-12-31")
    cloud = st.session_state.get("cloud_cover", 20)

    if not sat or not aoi:
        return

    try:
        import ee
        # Tenta inicializar silenciosamente (pode já estar inicializado)
        try:
            ee.Initialize()
        except Exception:
            pass

        coords = aoi.get("coordinates", [])
        geo_type = aoi.get("type", "Polygon")
        if geo_type == "Polygon":
            region = ee.Geometry.Polygon(coords)
        else:
            region = ee.Geometry.MultiPolygon(coords)

        collection = (
            ee.ImageCollection(sat["collection"])
            .filterDate(start, end)
            .filterBounds(region)
            .filter(ee.Filter.lte(sat.get("cloud_property", "CLOUD_COVER"), cloud))
        )
        count = collection.size().getInfo()
        st.session_state["img_count"] = count
        st.session_state["img_count_checked"] = True

    except Exception as e:
        err = str(e)
        if "Please authorize" in err or "authenticate" in err.lower():
            # GEE não autenticado — usa estimativa via API pública de catálogo
            st.session_state["img_count"] = _estimate_count_no_auth(sat, start, end)
            st.session_state["img_count_checked"] = True
        else:
            st.session_state["img_count"] = f"erro: {err[:120]}"
            st.session_state["img_count_checked"] = True


def _estimate_count_no_auth(sat: dict, start: str, end: str) -> str:
    """
    Estimativa de imagens sem autenticação GEE,
    baseada no intervalo de revisita do satélite e duração do período.
    """
    revisit_days = {
        "Sentinel-2": 5,
        "Landsat 9":  16,
        "Landsat 8":  16,
        "Landsat 7":  16,
        "Landsat 5":  16,
        "MODIS Terra": 1,
    }
    try:
        d0 = datetime.date.fromisoformat(start)
        d1 = datetime.date.fromisoformat(end)
        days = (d1 - d0).days
        rev = revisit_days.get(sat["name"], 10)
        est = max(1, days // rev)
        return f"~{est} (estimado — sem auth GEE)"
    except Exception:
        return "N/D"


def _render_img_count():
    """Renderiza o painel de contagem de imagens na sidebar."""
    if not st.session_state.get("img_count_checked"):
        return

    count = st.session_state.get("img_count")
    sat_name = (st.session_state.get("selected_satellite") or {}).get("name", "")

    if isinstance(count, str) and count.startswith("erro:"):
        st.markdown(
            f'<div style="background:rgba(255,107,43,.08);border:1px solid rgba(255,107,43,.3);'
            f'border-radius:4px;padding:.6rem .8rem;font-size:.76rem;color:#c4856a;margin-top:.5rem">'
            f'⚠️ {count}</div>',
            unsafe_allow_html=True,
        )
        return

    is_estimate = isinstance(count, str) and "estimado" in count
    num_str = str(count)
    try:
        num_val = int(str(count).replace("~", "").split()[0])
        zero = num_val == 0
    except Exception:
        zero = False

    color_class = "img-count-zero" if zero else ""
    icon = "⚠️" if zero else ("📊" if is_estimate else "🛰️")
    label_extra = " (estimativa sem autenticação GEE)" if is_estimate else ""

    st.markdown(f"""
    <div class="img-count-panel">
      <span class="img-count-num {color_class}">{icon} {num_str}</span>
      <span class="img-count-label">{sat_name} · imagens no período{label_extra}</span>
      {"<span style='font-size:.72rem;color:#c4856a;display:block;margin-top:.4rem'>Nenhuma imagem encontrada. Amplie o período ou reduza o filtro de nuvens.</span>" if zero else ""}
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Mapa interativo com captura automática de AOI
# ─────────────────────────────────────────────
def render_map():
    divider("01 · Delimite sua Área de Interesse")

    col_map, col_side = st.columns([3, 1], gap="medium")

    with col_side:
        st.markdown("**📂 Importar arquivo**")
        uploaded = st.file_uploader(
            "GeoJSON / Shapefile (zip) / KML",
            type=["geojson", "json", "zip", "kml"],
            key="aoi_upload",
            label_visibility="collapsed",
        )
        if uploaded:
            _handle_upload(uploaded)

        st.markdown("---")

        if st.session_state.get("aoi_geojson"):
            aoi = st.session_state["aoi_geojson"]
            coords = aoi.get("coordinates", [[]])[0] if aoi.get("type") == "Polygon" else []
            st.markdown(
                f'<div class="success-panel">✓ <strong>AOI definida</strong><br>'
                f'Tipo: {aoi.get("type","—")}<br>'
                f'Vértices: {len(coords)}</div>',
                unsafe_allow_html=True,
            )
            with st.expander("Ver GeoJSON"):
                st.code(json.dumps(aoi, indent=2), language="json")
            if st.button("🗑️ Limpar AOI", use_container_width=True):
                st.session_state["aoi_geojson"] = None
                st.session_state["img_count"] = None
                st.session_state["img_count_checked"] = False
                st.rerun()
        else:
            st.markdown(
                '<div class="info-panel">🖊️ Desenhe um polígono ou retângulo no mapa ao lado.<br><br>'
                'A área será capturada automaticamente ao finalizar o desenho.</div>',
                unsafe_allow_html=True,
            )

    with col_map:
        map_html = _build_map_html()
        # Componente recebe GeoJSON via valor de retorno
        result = components.html(map_html, height=500, scrolling=False)

    # Lê AOI capturada pelo mapa via query params / st.query_params
    _read_aoi_from_query()


def _build_map_html() -> str:
    """
    Constrói HTML do mapa Folium com JS que envia o GeoJSON desenhado
    de volta ao Streamlit via window.parent.postMessage e um input oculto.
    """
    try:
        import folium
        from folium.plugins import Draw, MousePosition

        aoi_existing = st.session_state.get("aoi_geojson")
        center = [-14.235, -51.925]
        zoom = 4

        # Se já tem AOI, centraliza nela
        if aoi_existing:
            try:
                coords = aoi_existing.get("coordinates", [[]])[0]
                if coords:
                    lats = [c[1] for c in coords]
                    lons = [c[0] for c in coords]
                    center = [(min(lats)+max(lats))/2, (min(lons)+max(lons))/2]
                    zoom = 9
            except Exception:
                pass

        m = folium.Map(location=center, zoom_start=zoom, tiles="OpenStreetMap")

        Draw(
            draw_options={
                "polygon":      {"allowIntersection": False,
                                 "shapeOptions": {"color":"#00e5ff","weight":2,"fillOpacity":.12}},
                "rectangle":    {"shapeOptions": {"color":"#00e5ff","weight":2,"fillOpacity":.12}},
                "circle":       False,
                "marker":       False,
                "polyline":     False,
                "circlemarker": False,
            },
            edit_options={"edit": True, "remove": True},
            export=False,
        ).add_to(m)
        MousePosition().add_to(m)

        # Mostra AOI existente
        if aoi_existing:
            folium.GeoJson(
                aoi_existing,
                style_function=lambda _: {
                    "fillColor":"#00e5ff","fillOpacity":.15,"color":"#00e5ff","weight":2},
            ).add_to(m)

        raw_html = m._repr_html_()

        # JS: captura geometria desenhada e atualiza o campo oculto + dispara evento
        inject = """
<script>
(function(){
  function init(tries){
    tries = tries || 0;
    // Procura o objeto L.Map criado pelo Folium
    var maps = [];
    for(var k in window){ try{ if(window[k] && window[k]._container && window[k].eachLayer) maps.push(window[k]); }catch(e){} }
    if(!maps.length){ if(tries<30){ setTimeout(function(){init(tries+1);},300); } return; }
    var map = maps[0];

    function sendGeom(geojson){
      // Envia para o iframe pai via postMessage
      try{ window.parent.postMessage({type:'geopilot_aoi', geojson: JSON.stringify(geojson)}, '*'); }catch(e){}
      // Também tenta setar via URL hash para fallback
      try{ window.parent.location.hash = 'aoi=' + encodeURIComponent(JSON.stringify(geojson)); }catch(e){}
    }

    map.on('draw:created', function(e){
      var g = e.layer.toGeoJSON().geometry;
      sendGeom(g);
    });
    map.on('draw:edited', function(e){
      e.layers.eachLayer(function(l){ sendGeom(l.toGeoJSON().geometry); });
    });
    map.on('draw:deleted', function(){
      sendGeom(null);
    });
  }
  document.addEventListener('DOMContentLoaded', function(){ setTimeout(init, 500); });
  setTimeout(init, 800);
})();
</script>
"""
        return raw_html + inject

    except ImportError:
        return "<p style='color:#6b8fa3;padding:1rem'>Instale folium: pip install folium</p>"


def _read_aoi_from_query():
    """
    Lê AOI enviada pelo iframe via postMessage capturada por JS injetado na página pai.
    Como o Streamlit não expõe postMessage diretamente, usamos um st.text_input oculto
    como ponte: o JS do mapa preenche o campo e o Streamlit lê o valor.
    """
    # Campo ponte: invisível visualmente, mas funcional
    st.markdown(
        '<style>#aoi-bridge-container{position:absolute;opacity:0;pointer-events:none;height:0;overflow:hidden}</style>'
        '<div id="aoi-bridge-container">',
        unsafe_allow_html=True,
    )
    raw_geojson = st.text_input(
        "aoi_bridge",
        key="aoi_bridge_input",
        label_visibility="collapsed",
        placeholder="",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # JS que escuta o postMessage e coloca no campo ponte
    st.markdown("""
    <script>
    window.addEventListener('message', function(event){
      if(event.data && event.data.type === 'geopilot_aoi'){
        var inputs = window.document.querySelectorAll('input[aria-label="aoi_bridge"]');
        if(!inputs.length) inputs = window.document.querySelectorAll('#aoi-bridge-container input');
        if(inputs.length){
          var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
          nativeInputValueSetter.call(inputs[0], event.data.geojson || '');
          inputs[0].dispatchEvent(new Event('input', {bubbles:true}));
        }
      }
    });
    </script>
    """, unsafe_allow_html=True)

    if raw_geojson and raw_geojson.strip().startswith("{"):
        try:
            geom = json.loads(raw_geojson)
            if geom and geom != st.session_state.get("aoi_geojson"):
                st.session_state["aoi_geojson"] = geom
                st.session_state["img_count"] = None
                st.session_state["img_count_checked"] = False
                st.rerun()
        except Exception:
            pass


def _handle_upload(uploaded):
    """Importa GeoJSON, Shapefile ZIP ou KML."""
    try:
        name = uploaded.name.lower()

        if name.endswith((".geojson", ".json")):
            data = json.loads(uploaded.read())
            if data.get("type") == "Feature":
                data = data["geometry"]
            elif data.get("type") == "FeatureCollection":
                data = data["features"][0]["geometry"]
            st.session_state["aoi_geojson"] = data

        elif name.endswith(".zip"):
            import geopandas as gpd, tempfile, zipfile
            with tempfile.TemporaryDirectory() as tmp:
                zpath = os.path.join(tmp, "shp.zip")
                with open(zpath, "wb") as f:
                    f.write(uploaded.read())
                with zipfile.ZipFile(zpath) as z:
                    z.extractall(tmp)
                shps = [f for f in os.listdir(tmp) if f.endswith(".shp")]
                if shps:
                    gdf = gpd.read_file(os.path.join(tmp, shps[0]))
                    union = gdf.geometry.union_all() if hasattr(gdf.geometry,"union_all") else gdf.geometry.unary_union
                    st.session_state["aoi_geojson"] = json.loads(union.to_json())

        elif name.endswith(".kml"):
            import geopandas as gpd, fiona
            fiona.drvsupport.supported_drivers["KML"] = "rw"
            gdf = gpd.read_file(uploaded, driver="KML")
            union = gdf.geometry.union_all() if hasattr(gdf.geometry,"union_all") else gdf.geometry.unary_union
            st.session_state["aoi_geojson"] = json.loads(union.to_json())

        st.session_state["img_count"] = None
        st.session_state["img_count_checked"] = False
        st.success("✓ Arquivo importado com sucesso")
        st.rerun()

    except Exception as e:
        st.error(f"Erro ao importar: {e}")


# ─────────────────────────────────────────────
# Verificação de imagens disponíveis
# ─────────────────────────────────────────────
def _render_image_check_panel():
    """
    Painel na área principal que mostra disponibilidade de imagens.
    Usa estimativa por revisita quando GEE não está autenticado,
    e consulta real quando está. O código gerado sempre faz
    a verificação real como primeiro passo.
    """
    aoi     = st.session_state.get("aoi_geojson")
    sat     = st.session_state.get("selected_satellite")
    start   = st.session_state.get("date_start", "2023-01-01")
    end     = st.session_state.get("date_end", "2023-12-31")
    cloud   = st.session_state.get("cloud_cover", 20)
    is_custom = st.session_state.get("selected_analysis") == "__custom__"

    if not aoi or not sat or is_custom:
        return

    # Recalcula quando mudam datas, satélite, nuvens ou AOI
    check_key = f"{sat['name']}|{start}|{end}|{cloud}|{str(aoi)[:80]}"
    if st.session_state.get("_img_check_key") != check_key:
        st.session_state["_img_check_key"] = check_key
        st.session_state["img_count"] = None
        st.session_state["img_count_checked"] = False

    col_info, col_btn = st.columns([5, 1], gap="small")

    with col_btn:
        if st.button("🔍 Verificar", use_container_width=True, key="btn_check_imgs"):
            with st.spinner("Consultando…"):
                _check_image_count()

    with col_info:
        if not st.session_state.get("img_count_checked"):
            # Mostra estimativa passiva por revisita (sem clique)
            est = _estimate_count(sat, start, end)
            try:
                d0 = datetime.date.fromisoformat(start)
                d1 = datetime.date.fromisoformat(end)
                days = (d1 - d0).days
            except Exception:
                days = 0
            st.markdown(
                f'<div style="background:rgba(0,229,255,.04);border:1px solid rgba(0,229,255,.12);'
                f'border-radius:5px;padding:.7rem 1rem;font-size:.83rem;color:#6b8fa3;">'
                f'🛰️ <strong>{sat["name"]}</strong> &nbsp;·&nbsp; '
                f'Período: <strong>{days} dias</strong> &nbsp;·&nbsp; '
                f'Estimativa de imagens: <strong style="color:#00e5ff">{est}</strong> '
                f'&nbsp;<span style="font-size:.72rem">(revisita teórica)</span>'
                f'&nbsp;·&nbsp; Clique em <strong>🔍 Verificar</strong> para contagem real no GEE.'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            count = st.session_state.get("img_count")
            _show_count_result(count, sat["name"], start, end, cloud)


def _show_count_result(count, sat_name, start, end, cloud):
    """Renderiza o resultado da verificação com feedback visual claro."""
    if isinstance(count, str) and count.startswith("erro:"):
        st.markdown(
            f'<div class="warn-panel">⚠️ Não foi possível consultar o GEE: {count[6:]}<br>'
            f'<small>A verificação real acontece na primeira linha do código gerado.</small></div>',
            unsafe_allow_html=True)
        return

    is_estimate = isinstance(count, str) and "estimado" in count
    try:
        num = int(str(count).replace("~","").split()[0])
    except Exception:
        num = -1

    if num == 0:
        st.markdown(
            f'<div style="background:rgba(255,107,43,.08);border:1px solid rgba(255,107,43,.3);'
            f'border-radius:5px;padding:.8rem 1rem;">'
            f'<span style="font-size:1.5rem;color:#ff6b2b;font-family:JetBrains Mono,monospace">⚠️ 0</span>'
            f'<span style="font-size:.8rem;color:#c4856a;margin-left:.6rem">'
            f'imagens encontradas para <strong>{sat_name}</strong> entre {start} e {end} '
            f'com nuvens ≤ {cloud}%</span><br>'
            f'<span style="font-size:.76rem;color:#a07060">'
            f'💡 Tente ampliar o período, aumentar o limite de nuvens ou trocar o satélite.</span>'
            f'</div>', unsafe_allow_html=True)
    elif num > 0:
        label_extra = " <span style='font-size:.72rem;color:#6b8fa3'>(estimativa por revisita)</span>" if is_estimate else " <span style='font-size:.72rem;color:#39ff14'>✓ verificado no GEE</span>"
        st.markdown(
            f'<div style="background:rgba(57,255,20,.05);border:1px solid rgba(57,255,20,.2);'
            f'border-radius:5px;padding:.8rem 1rem;display:flex;align-items:center;gap:1rem;">'
            f'<span style="font-size:2rem;color:#39ff14;font-family:JetBrains Mono,monospace;'
            f'font-weight:600;line-height:1">{count}</span>'
            f'<div><span style="font-size:.85rem;color:#c8e6c9">imagens disponíveis</span><br>'
            f'<span style="font-size:.78rem;color:#6b8fa3">{sat_name} · {start} → {end} · nuvens ≤ {cloud}%'
            f'</span>{label_extra}</div>'
            f'</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="info-panel">📊 Resultado: <strong>{count}</strong></div>',
            unsafe_allow_html=True)


def _check_image_count():
    """Tenta contagem real via GEE; cai para estimativa se não autenticado."""
    sat   = st.session_state.get("selected_satellite")
    aoi   = st.session_state.get("aoi_geojson")
    start = st.session_state.get("date_start", "2023-01-01")
    end   = st.session_state.get("date_end", "2023-12-31")
    cloud = st.session_state.get("cloud_cover", 20)

    if not sat or not aoi:
        return

    try:
        import ee
        try:
            ee.Initialize()
        except Exception:
            pass

        coords   = aoi.get("coordinates", [])
        geo_type = aoi.get("type", "Polygon")
        region   = ee.Geometry.Polygon(coords) if geo_type == "Polygon" else ee.Geometry.MultiPolygon(coords)

        count = (
            ee.ImageCollection(sat["collection"])
            .filterDate(start, end)
            .filterBounds(region)
            .filter(ee.Filter.lte(sat.get("cloud_property", "CLOUD_COVER"), cloud))
            .size()
            .getInfo()
        )
        st.session_state["img_count"] = count

    except Exception as e:
        err = str(e)
        if "authorize" in err.lower() or "authenticate" in err.lower() or "credentials" in err.lower():
            # Sem auth GEE → estimativa
            st.session_state["img_count"] = _estimate_count(sat, start, end)
        else:
            st.session_state["img_count"] = f"erro: {err[:120]}"

    st.session_state["img_count_checked"] = True


def _estimate_count(sat: dict, start: str, end: str) -> str:
    """Estimativa por intervalo de revisita do satélite."""
    revisit = {"Sentinel-2": 5, "Landsat 9": 16, "Landsat 8": 16,
               "Landsat 7": 16, "Landsat 5": 16, "MODIS Terra": 1}
    try:
        days = (datetime.date.fromisoformat(end) - datetime.date.fromisoformat(start)).days
        rev  = revisit.get(sat["name"], 10)
        return f"~{max(1, days // rev)} (estimado)"
    except Exception:
        return "N/D"


# ─────────────────────────────────────────────
# Geração de código
# ─────────────────────────────────────────────
def render_generate():
    divider("02 · Gerar Código GEE com Gemini")

    missing = []
    if not st.session_state.get("gemini_key"):
        missing.append("🔑 Chave Gemini API (sidebar)")
    if not st.session_state.get("aoi_geojson"):
        missing.append("🗺️ Área de Interesse (desenhe no mapa)")
    if (st.session_state.get("selected_analysis") == "__custom__"
            and not st.session_state.get("custom_analysis_text", "").strip()):
        missing.append("✏️ Descrição da análise personalizada (sidebar)")

    if missing:
        items = "".join(f"<li>{m}</li>" for m in missing)
        st.markdown(
            f'<div class="warn-panel">⚠️ Configure antes de gerar:<ul style="margin:.4rem 0 0 1rem">{items}</ul></div>',
            unsafe_allow_html=True)

    # Painel de verificação de imagens disponíveis
    _render_image_check_panel()

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
# Código gerado + instruções
# ─────────────────────────────────────────────
def render_code_output():
    code = st.session_state.get("generated_code")
    if not code:
        return

    divider("03 · Código Gerado")
    st.markdown('<span class="badge-ok">✓ Código gerado pelo Gemini</span>', unsafe_allow_html=True)
    st.markdown("")
    st.code(code, language="python")

    col1, col2, col3 = st.columns(3, gap="small")
    with col1:
        st.download_button("⬇ Baixar .py", data=code,
                           file_name="geopilot_analysis.py", mime="text/plain",
                           use_container_width=True)
    with col2:
        st.link_button("🌍 Abrir GEE Code Editor",
                       "https://code.earthengine.google.com/", use_container_width=True)
    with col3:
        nb = _build_colab_notebook(code)
        st.download_button("📓 Baixar notebook Colab",
                           data=json.dumps(nb, indent=2),
                           file_name="geopilot_analysis.ipynb",
                           mime="application/json", use_container_width=True)

    divider("04 · Como Executar")
    tab1, tab2 = st.tabs(["🌍 GEE Code Editor", "📓 Google Colab"])

    with tab1:
        st.markdown("""
**1.** Clique em **"Abrir GEE Code Editor"** acima

**2.** Cole o código gerado no editor (`Ctrl+V`)

**3.** Clique em **"Run"** — resultado aparece no mapa e no Console
        """)
    with tab2:
        st.markdown("""
**1.** Baixe o `.ipynb` e abra no [Google Colab](https://colab.research.google.com)

**2.** Execute a 1ª célula — instala dependências e autentica via `ee.Authenticate()`

**3.** Execute as células seguintes — mapas aparecem inline no notebook
        """)


def _build_colab_notebook(code: str) -> dict:
    install_cell = (
        "!pip install earthengine-api geemap folium -q\n\n"
        "import ee\n"
        "ee.Authenticate()\n"
        "ee.Initialize(project='YOUR_PROJECT_ID')  # Substitua pelo seu Project ID"
    )
    return {
        "nbformat": 4, "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name":"Python 3","language":"python","name":"python3"},
            "language_info": {"name":"python","version":"3.10.0"},
            "colab": {"provenance":[]},
        },
        "cells": [
            {"cell_type":"markdown","metadata":{},"source":[
                "# 🛰️ GeoPilot AI — Análise Geoespacial\n",
                "> Código gerado automaticamente. Execute as células em ordem."]},
            {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":[install_cell]},
            {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":[code]},
        ],
    }


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
