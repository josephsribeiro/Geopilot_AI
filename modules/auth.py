"""
GeoPilot AI — Módulo de autenticação (Gemini + GEE)
Compatível com Streamlit Cloud (sem terminal disponível).
"""

import json
import tempfile
import os
import streamlit as st
from config.settings import APP_CONFIG


def render_auth_sidebar():
    """Renderiza controles de autenticação na sidebar."""

    # ── Gemini API Key ──
    st.markdown(
        f'🔑 **Gemini API** — [Obter chave]({APP_CONFIG["links"]["gemini_api_key"]})',
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
        st.markdown(
            '<span style="color:#39ff14;font-size:0.78rem">✓ Chave Gemini configurada</span>',
            unsafe_allow_html=True,
        )
    else:
        st.session_state["gemini_key"] = ""

    st.markdown("---")

    # ── Google Earth Engine ──
    st.markdown(
        f'🌍 **Google Earth Engine** — [Registrar conta]({APP_CONFIG["links"]["gee_signup"]})',
    )

    # No Streamlit Cloud só funciona Service Account
    st.markdown(
        '<div style="background:rgba(255,107,43,0.08);border:1px solid rgba(255,107,43,0.3);'
        'border-radius:4px;padding:0.6rem 0.8rem;font-size:0.78rem;color:#c4856a;margin-bottom:0.6rem">'
        '⚠️ No Streamlit Cloud use <strong>Service Account JSON</strong>. '
        'O método "Credenciais do sistema" só funciona localmente.</div>',
        unsafe_allow_html=True,
    )

    auth_method = st.radio(
        "Método",
        ["Service Account JSON", "Credenciais do sistema (apenas local)"],
        key="gee_auth_method",
        label_visibility="collapsed",
    )

    gee_project = st.text_input(
        "GEE Project ID (opcional)",
        placeholder="ex: ee-meuusuario",
        key="gee_project_input",
        label_visibility="collapsed",
    )

    service_account_json = None

    if auth_method == "Service Account JSON":
        st.markdown(
            "📎 Faça upload do arquivo `.json` da sua Service Account. "
            "[Como criar?](https://developers.google.com/earth-engine/guides/service_account)",
            unsafe_allow_html=False,
        )
        uploaded = st.file_uploader(
            "Service Account JSON",
            type=["json"],
            key="sa_json_upload",
            label_visibility="collapsed",
        )
        if uploaded:
            service_account_json = uploaded.read().decode()
            # Mantém no session_state para não perder no rerun
            st.session_state["_sa_json_cache"] = service_account_json
        elif st.session_state.get("_sa_json_cache"):
            service_account_json = st.session_state["_sa_json_cache"]
            st.markdown(
                '<span style="color:#39ff14;font-size:0.78rem">✓ JSON carregado</span>',
                unsafe_allow_html=True,
            )

    if st.button("Conectar ao GEE", use_container_width=True):
        if auth_method == "Service Account JSON" and not service_account_json:
            st.error("Faça upload do arquivo JSON antes de conectar.")
        else:
            _authenticate_gee(
                project=gee_project,
                service_account_json=service_account_json,
                use_system_creds=(auth_method != "Service Account JSON"),
            )

    # Mostra status atual
    if st.session_state.get("gee_authenticated"):
        st.markdown(
            '<span style="color:#39ff14;font-size:0.78rem">✓ GEE conectado</span>',
            unsafe_allow_html=True,
        )


def _authenticate_gee(
    project: str,
    service_account_json: str | None,
    use_system_creds: bool = False,
):
    """Tenta autenticar no Google Earth Engine."""
    try:
        import ee  # type: ignore

        # Reinicializa caso já tenha sido inicializado antes
        try:
            ee.Reset()
        except Exception:
            pass

        if service_account_json:
            # ── Service Account ──
            sa_data = json.loads(service_account_json)
            sa_email = sa_data.get("client_email")

            if not sa_email:
                st.error("JSON inválido: campo 'client_email' não encontrado.")
                st.session_state["gee_authenticated"] = False
                return

            # Escreve JSON em arquivo temporário (exigido pela API do EE)
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as f:
                json.dump(sa_data, f)
                tmp_path = f.name

            try:
                credentials = ee.ServiceAccountCredentials(
                    email=sa_email, key_file=tmp_path
                )
                if project:
                    ee.Initialize(credentials, project=project)
                else:
                    ee.Initialize(credentials)
            finally:
                os.unlink(tmp_path)

        elif use_system_creds:
            # ── Credenciais locais (earthengine authenticate) ──
            if project:
                ee.Initialize(project=project)
            else:
                ee.Initialize()
        else:
            st.error("Nenhum método de autenticação válido selecionado.")
            st.session_state["gee_authenticated"] = False
            return

        # Testa a conexão
        test = ee.Number(1).add(1).getInfo()
        if test == 2:
            st.session_state["gee_authenticated"] = True
            st.success("✓ Conectado ao Google Earth Engine!")
        else:
            raise RuntimeError("Teste de conexão retornou valor inesperado.")

    except ImportError:
        st.error(
            "⚠️ Biblioteca `earthengine-api` não instalada. "
            "Verifique o requirements.txt."
        )
        st.session_state["gee_authenticated"] = False
    except json.JSONDecodeError:
        st.error("✗ Arquivo JSON inválido ou corrompido.")
        st.session_state["gee_authenticated"] = False
    except Exception as e:
        msg = str(e)
        if "not been registered" in msg or "not registered" in msg:
            st.error(
                "✗ Esta Service Account não está registrada no Earth Engine. "
                "Registre em: https://signup.earthengine.google.com/#!/service_accounts"
            )
        elif "quota" in msg.lower():
            st.error("✗ Cota do projeto GEE excedida.")
        else:
            st.error(f"✗ Falha na autenticação GEE: {msg}")
        st.session_state["gee_authenticated"] = False
