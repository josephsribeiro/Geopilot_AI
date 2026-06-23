"""
GeoPilot AI — Aplicativo principal Streamlit
"""

import streamlit as st
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

from config.settings import APP_CONFIG
from modules.auth import render_auth_sidebar
from modules.map_tools import render_map_section
from modules.analysis_catalog import get_analysis_catalog
from modules.satellite_catalog import get_satellites_for_analysis
from modules.gemini_generator import generate_gee_code
from modules.execution_engine import execute_gee_code

# ─────────────────────────────────────────────
# Configuração da página
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="GeoPilot AI",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS — Hero header + design system
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  /* ── Reset & base ── */
  html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
  }
  .main .block-container {
    padding-top: 0 !important;
    max-width: 1280px;
  }

  /* ── Paleta ── */
  :root {
    --void:       #080c10;
    --deep:       #0d1117;
    --panel:      #131920;
    --border:     #1e2d3d;
    --signal:     #00e5ff;    /* ciano satélite */
    --pulse:      #39ff14;    /* verde radar */
    --warn:       #ff6b2b;
    --text-hi:    #e8f4f8;
    --text-lo:    #6b8fa3;
    --card-bg:    rgba(19, 25, 32, 0.85);
  }

  /* ── Hero ── */
  .hero-wrapper {
    position: relative;
    background: var(--void);
    overflow: hidden;
    padding: 0 0 2.5rem 0;
    margin: 0 -1rem 2rem -1rem;
  }
  .hero-grid {
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(0,229,255,0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,229,255,0.04) 1px, transparent 1px);
    background-size: 48px 48px;
    animation: gridDrift 20s linear infinite;
  }
  @keyframes gridDrift {
    from { background-position: 0 0; }
    to   { background-position: 48px 48px; }
  }
  .hero-scanline {
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 3px,
      rgba(0,0,0,0.08) 3px,
      rgba(0,0,0,0.08) 4px
    );
    pointer-events: none;
  }
  .hero-glow {
    position: absolute;
    top: -120px;
    left: 50%;
    transform: translateX(-50%);
    width: 700px;
    height: 340px;
    background: radial-gradient(ellipse, rgba(0,229,255,0.12) 0%, transparent 70%);
    pointer-events: none;
  }
  .hero-content {
    position: relative;
    z-index: 10;
    text-align: center;
    padding: 3.5rem 2rem 1.5rem;
  }
  .hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--signal);
    background: rgba(0,229,255,0.08);
    border: 1px solid rgba(0,229,255,0.2);
    border-radius: 2px;
    padding: 0.3rem 0.85rem;
    margin-bottom: 1.4rem;
  }
  .hero-eyebrow::before {
    content: '';
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--pulse);
    animation: blink 1.4s ease-in-out infinite;
  }
  @keyframes blink {
    0%,100% { opacity: 1; }
    50%      { opacity: 0.2; }
  }
  .hero-title {
    font-size: clamp(2.6rem, 6vw, 4.4rem);
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.05;
    color: var(--text-hi);
    margin: 0 0 0.6rem;
  }
  .hero-title .accent {
    color: var(--signal);
    text-shadow: 0 0 40px rgba(0,229,255,0.35);
  }
  .hero-sub {
    font-size: 1.05rem;
    font-weight: 400;
    color: var(--text-lo);
    max-width: 600px;
    margin: 0 auto 2rem;
    line-height: 1.65;
  }
  .hero-stats {
    display: flex;
    justify-content: center;
    gap: 3rem;
    flex-wrap: wrap;
  }
  .stat-item {
    text-align: center;
  }
  .stat-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem;
    font-weight: 500;
    color: var(--signal);
    display: block;
  }
  .stat-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text-lo);
  }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: var(--deep) !important;
    border-right: 1px solid var(--border);
  }
  [data-testid="stSidebar"] * {
    color: var(--text-hi) !important;
  }
  .sidebar-section-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--text-lo) !important;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.4rem;
    margin: 1.2rem 0 0.7rem;
  }

  /* ── Cards de análise ── */
  .analysis-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
  }
  .analysis-card:hover { border-color: var(--signal); }
  .card-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text-hi);
    margin-bottom: 0.3rem;
  }
  .card-desc {
    font-size: 0.82rem;
    color: var(--text-lo);
    line-height: 1.5;
  }

  /* ── Code block ── */
  .code-output {
    background: #0a0f14;
    border: 1px solid var(--border);
    border-left: 3px solid var(--pulse);
    border-radius: 4px;
    padding: 1.2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #b0d4e0;
    white-space: pre-wrap;
    overflow-x: auto;
    max-height: 480px;
    overflow-y: auto;
  }

  /* ── Status badge ── */
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    padding: 0.2rem 0.55rem;
    border-radius: 2px;
  }
  .badge-ok   { background: rgba(57,255,20,0.1);  color: var(--pulse);  border: 1px solid rgba(57,255,20,0.25); }
  .badge-err  { background: rgba(255,107,43,0.1); color: var(--warn);   border: 1px solid rgba(255,107,43,0.25); }
  .badge-info { background: rgba(0,229,255,0.1);  color: var(--signal); border: 1px solid rgba(0,229,255,0.2); }

  /* ── Botões Streamlit ── */
  .stButton > button {
    background: transparent;
    border: 1px solid var(--signal);
    color: var(--signal);
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.85rem;
    font-weight: 500;
    letter-spacing: 0.05em;
    border-radius: 3px;
    padding: 0.5rem 1.4rem;
    transition: background 0.2s, color 0.2s;
  }
  .stButton > button:hover {
    background: var(--signal);
    color: var(--void);
  }
  .stButton > button[kind="primary"] {
    background: var(--signal);
    color: var(--void);
    font-weight: 600;
  }
  .stButton > button[kind="primary"]:hover {
    background: #33eeff;
  }

  /* ── Inputs ── */
  .stTextInput input, .stTextArea textarea, .stSelectbox select {
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-hi) !important;
    border-radius: 3px !important;
    font-family: 'Space Grotesk', sans-serif !important;
  }
  .stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--signal) !important;
    box-shadow: 0 0 0 2px rgba(0,229,255,0.12) !important;
  }

  /* ── Divider temático ── */
  .section-divider {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 2rem 0 1.5rem;
  }
  .section-divider-line {
    flex: 1;
    height: 1px;
    background: var(--border);
  }
  .section-divider-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-lo);
  }

  /* ── Info panels ── */
  .info-panel {
    background: rgba(0,229,255,0.05);
    border: 1px solid rgba(0,229,255,0.15);
    border-radius: 4px;
    padding: 0.9rem 1.1rem;
    font-size: 0.84rem;
    color: var(--text-lo);
    line-height: 1.6;
    margin-bottom: 1rem;
  }
  .warn-panel {
    background: rgba(255,107,43,0.05);
    border: 1px solid rgba(255,107,43,0.2);
    border-radius: 4px;
    padding: 0.9rem 1.1rem;
    font-size: 0.84rem;
    color: #c4856a;
    line-height: 1.6;
    margin-bottom: 1rem;
  }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Hero Header
# ─────────────────────────────────────────────
def render_hero():
    st.markdown("""
    <div class="hero-wrapper">
      <div class="hero-grid"></div>
      <div class="hero-scanline"></div>
      <div class="hero-glow"></div>
      <div class="hero-content">
        <div class="hero-eyebrow">🛰️ &nbsp;Geospatial Intelligence Platform</div>
        <h1 class="hero-title">Geo<span class="accent">Pilot</span> AI</h1>
        <p class="hero-sub">
          Análise geoespacial avançada com Google Earth Engine e inteligência artificial —
          sem escrever uma linha de código.
        </p>
        <div class="hero-stats">
          <div class="stat-item">
            <span class="stat-num">20+</span>
            <span class="stat-label">Análises pré-configuradas</span>
          </div>
          <div class="stat-item">
            <span class="stat-num">6</span>
            <span class="stat-label">Satélites suportados</span>
          </div>
          <div class="stat-item">
            <span class="stat-num">∞</span>
            <span class="stat-label">Análises personalizadas</span>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def section_divider(label: str):
    st.markdown(f"""
    <div class="section-divider">
      <div class="section-divider-line"></div>
      <div class="section-divider-label">{label}</div>
      <div class="section-divider-line"></div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Inicialização do session state
# ─────────────────────────────────────────────
def init_session():
    defaults = {
        "gemini_key": "",
        "gee_authenticated": False,
        "aoi_geojson": None,
        "aoi_ee_geometry": None,
        "selected_analysis": None,
        "selected_satellite": None,
        "generated_code": None,
        "execution_result": None,
        "custom_analysis_text": "",
        "map_data": None,
        "date_start": "2023-01-01",
        "date_end": "2023-12-31",
        "cloud_cover": 20,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown('<p class="sidebar-section-title">🔐 Credenciais</p>', unsafe_allow_html=True)
        render_auth_sidebar()

        catalog = get_analysis_catalog()

        st.markdown('<p class="sidebar-section-title">📡 Análises Disponíveis</p>', unsafe_allow_html=True)

        analysis_options = {"Análise Personalizada 🤖": "__custom__"}
        for category, analyses in catalog.items():
            for key, meta in analyses.items():
                label = f"{meta['icon']} {meta['name']}"
                analysis_options[label] = key

        selected_label = st.selectbox(
            "Selecione a análise",
            options=list(analysis_options.keys()),
            key="analysis_selector",
            label_visibility="collapsed",
        )
        st.session_state["selected_analysis"] = analysis_options[selected_label]

        # Satélites dinâmicos
        if st.session_state["selected_analysis"] != "__custom__":
            satellites = get_satellites_for_analysis(st.session_state["selected_analysis"])
            if satellites:
                st.markdown('<p class="sidebar-section-title">🛰️ Satélite</p>', unsafe_allow_html=True)
                sat_names = [s["name"] for s in satellites]
                selected_sat = st.selectbox(
                    "Satélite",
                    sat_names,
                    label_visibility="collapsed",
                )
                st.session_state["selected_satellite"] = next(
                    (s for s in satellites if s["name"] == selected_sat), satellites[0]
                )

        # Datas — widgets usam keys próprias; valores são lidos pelo retorno
        st.markdown('<p class="sidebar-section-title">📅 Período</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Início", key="widget_start_date", label_visibility="visible")
        with col2:
            end_date = st.date_input("Fim", key="widget_end_date", label_visibility="visible")
        # Armazena em chaves separadas das chaves dos widgets
        st.session_state["date_start"] = str(start_date)
        st.session_state["date_end"] = str(end_date)

        # Parâmetros extras
        st.markdown('<p class="sidebar-section-title">⚙️ Parâmetros</p>', unsafe_allow_html=True)
        cloud_val = st.slider(
            "Cobertura de nuvens máx. (%)", 0, 100, 20, key="cloud_slider"
        )
        st.session_state["cloud_cover"] = cloud_val


# ─────────────────────────────────────────────
# Área principal
# ─────────────────────────────────────────────
def render_main():
    # ── Etapa 1: Mapa ──
    section_divider("01 · Área de Interesse")
    aoi_geojson, aoi_ee_geom = render_map_section()
    st.session_state["aoi_geojson"] = aoi_geojson
    st.session_state["aoi_ee_geometry"] = aoi_ee_geom

    if aoi_geojson:
        st.markdown('<span class="badge badge-ok">✓ AOI definida</span>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="info-panel">🖊️ Desenhe um polígono no mapa ou importe um arquivo GeoJSON / Shapefile / KML para definir sua área de interesse.</div>',
            unsafe_allow_html=True,
        )

    # ── Etapa 2: Análise personalizada ──
    if st.session_state["selected_analysis"] == "__custom__":
        section_divider("02 · Análise Personalizada")
        st.markdown(
            '<div class="info-panel">Descreva a análise desejada em linguagem natural. O Gemini selecionará o satélite mais adequado e gerará o código GEE automaticamente.</div>',
            unsafe_allow_html=True,
        )
        custom_text = st.text_area(
            "Descreva sua análise",
            placeholder='Ex: "Mapear áreas queimadas entre 2020 e 2025 utilizando Sentinel-2 na Amazônia."',
            height=120,
            key="custom_text_area",
        )
        st.session_state["custom_analysis_text"] = custom_text

    # ── Etapa 3: Gerar código ──
    section_divider("03 · Geração de Código")

    ready = (
        st.session_state.get("gemini_key")
        and st.session_state.get("gee_authenticated")
        and st.session_state.get("aoi_geojson")
    )

    if not ready:
        missing = []
        if not st.session_state.get("gemini_key"):
            missing.append("chave Gemini API")
        if not st.session_state.get("gee_authenticated"):
            missing.append("autenticação GEE")
        if not st.session_state.get("aoi_geojson"):
            missing.append("área de interesse (AOI)")
        st.markdown(
            f'<div class="warn-panel">⚠️ Para gerar o código, configure: <strong>{", ".join(missing)}</strong></div>',
            unsafe_allow_html=True,
        )

    col_gen, col_run = st.columns([1, 1], gap="medium")

    with col_gen:
        if st.button("⚡ Gerar Código com Gemini", type="primary", disabled=not ready, use_container_width=True):
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
                    st.markdown('<span class="badge badge-ok">✓ Código gerado</span>', unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f'<span class="badge badge-err">✗ Erro: {e}</span>', unsafe_allow_html=True)

    with col_run:
        if st.button(
            "▶ Executar no GEE",
            disabled=not (ready and st.session_state.get("generated_code")),
            use_container_width=True,
        ):
            with st.spinner("Executando no Google Earth Engine…"):
                try:
                    result = execute_gee_code(
                        code=st.session_state["generated_code"],
                        aoi_geojson=st.session_state["aoi_geojson"],
                    )
                    st.session_state["execution_result"] = result
                except Exception as e:
                    st.session_state["execution_result"] = {"error": str(e)}

    # ── Exibe código gerado ──
    if st.session_state.get("generated_code"):
        section_divider("04 · Código Gerado")
        with st.expander("Ver / editar código Python", expanded=True):
            edited_code = st.text_area(
                "Código GEE",
                value=st.session_state["generated_code"],
                height=380,
                label_visibility="collapsed",
                key="code_editor",
            )
            st.session_state["generated_code"] = edited_code

        col_dl, _ = st.columns([1, 3])
        with col_dl:
            st.download_button(
                "⬇ Baixar .py",
                data=st.session_state["generated_code"],
                file_name="geopilot_analysis.py",
                mime="text/plain",
            )

    # ── Resultados ──
    if st.session_state.get("execution_result"):
        section_divider("05 · Resultados")
        result = st.session_state["execution_result"]

        if "error" in result:
            st.markdown(
                f'<div class="warn-panel">✗ Erro na execução:<br><code>{result["error"]}</code></div>',
                unsafe_allow_html=True,
            )
        else:
            if result.get("map_html"):
                st.components.v1.html(result["map_html"], height=520, scrolling=False)

            if result.get("stats"):
                st.markdown("**Estatísticas**")
                import pandas as pd
                stats_df = pd.DataFrame([result["stats"]])
                st.dataframe(stats_df, use_container_width=True)

            if result.get("charts"):
                for chart in result["charts"]:
                    st.plotly_chart(chart, use_container_width=True)

            if result.get("export_url"):
                st.markdown(
                    f'<div class="info-panel">📦 Exportação disponível: <a href="{result["export_url"]}" target="_blank">{result["export_url"]}</a></div>',
                    unsafe_allow_html=True,
                )


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
def main():
    init_session()
    render_hero()
    render_sidebar()
    render_main()


if __name__ == "__main__":
    main()
