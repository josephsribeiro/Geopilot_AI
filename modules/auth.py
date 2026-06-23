"""
GeoPilot AI — Módulo de autenticação (Gemini + GEE)
"""

import streamlit as st
from config.settings import APP_CONFIG


def render_auth_sidebar():
    """Renderiza controles de autenticação na sidebar."""

    # ── Gemini API Key ──
    st.markdown(
        f'🔑 **Gemini API** — [Obter chave]({APP_CONFIG["links"]["gemini_api_key"]})',
        unsafe_allow_html=False,
    )
    gemini_key = st.text_input(
        "Chave Gemini API",
        type="password",
        placeholder="AIza…",
        key="gemini_key_input",
        label_visibility="collapsed",
    )
    if gemini_key:
        st.session_state["gemini_key"] = gemini_key
        st.markdown('<span style="color:#39ff14;font-size:0.78rem">✓ Chave Gemini configurada</span>', unsafe_allow_html=True)
    else:
        st.session_state["gemini_key"] = ""

    st.markdown("---")

    # ── Google Earth Engine ──
    st.markdown(
        f'🌍 **Google Earth Engine** — [Registrar conta]({APP_CONFIG["links"]["gee_signup"]})',
        unsafe_allow_html=False,
    )

    gee_project = st.text_input(
        "GEE Project ID (opcional)",
        placeholder="my-gee-project",
        key="gee_project_input",
        label_visibility="collapsed",
    )

    auth_method = st.radio(
        "Método de autenticação",
        ["Credenciais do sistema", "Token de serviço (JSON)"],
        key="gee_auth_method",
        label_visibility="collapsed",
    )

    service_account_json = None
    if auth_method == "Token de serviço (JSON)":
        uploaded = st.file_uploader(
            "Service Account JSON",
            type=["json"],
            key="sa_json_upload",
            label_visibility="collapsed",
        )
        if uploaded:
            service_account_json = uploaded.read().decode()

    if st.button("Conectar ao GEE", use_container_width=True):
        _authenticate_gee(gee_project, service_account_json)


def _authenticate_gee(project: str, service_account_json: str | None):
    """Tenta autenticar no Google Earth Engine."""
    try:
        import ee  # type: ignore

        if service_account_json:
            import json, tempfile, os
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                f.write(service_account_json)
                tmp_path = f.name

            credentials = ee.ServiceAccountCredentials(None, key_file=tmp_path)
            ee.Initialize(credentials, project=project or None)
            os.unlink(tmp_path)
        else:
            if project:
                ee.Initialize(project=project)
            else:
                ee.Initialize()

        # Testa a conexão com uma operação simples
        test = ee.Number(1).add(1).getInfo()
        if test == 2:
            st.session_state["gee_authenticated"] = True
            st.success("✓ Conectado ao Google Earth Engine")
        else:
            raise RuntimeError("Teste de conexão falhou.")

    except ImportError:
        st.error("⚠️ Biblioteca `earthengine-api` não instalada. Execute: pip install earthengine-api")
        st.session_state["gee_authenticated"] = False
    except Exception as e:
        st.error(f"✗ Falha na autenticação GEE: {e}")
        st.session_state["gee_authenticated"] = False
