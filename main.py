import streamlit as st
import extra_streamlit_components as stx
from session_utils import crear_token, leer_token

st.set_page_config(page_title="Nuu", page_icon="N", layout="wide")

# ---------------------------------------------------------------------------
# CSS global — inyectado PRIMERO para que nada lo sobreescriba
# ---------------------------------------------------------------------------

_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
  }

  /* Ocultar sidebar */
  [data-testid="stSidebar"],
  [data-testid="stSidebarContent"],
  [data-testid="stSidebarNav"],
  section[data-testid="stSidebar"] { display: none !important; }

  /* Layout */
  .main .block-container {
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    padding-top: 0.4rem !important;
    max-width: 1400px !important;
  }

  /* Ocultar marcadores de navbar */
  p:has(span.nb), p:has(span.nb-act), p:has(span.nb-logo),
  p:has(span.nb-out), p:has(span.nb-user) {
    margin: 0 !important; padding: 0 !important;
    line-height: 0 !important; height: 0 !important;
    overflow: hidden !important;
  }

  /* ── Navbar: logo ────────────────────────────────────────── */
  div:has(> span.nb-logo) + div[data-testid="stButton"] > button,
  div:has(span.nb-logo) + div[data-testid="stButton"] button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #d1d4dc !important;
    font-size: 1.2rem !important;
    font-weight: 800 !important;
    letter-spacing: -1px !important;
    padding: 4px 8px !important;
    border-radius: 8px !important;
    white-space: nowrap !important;
    transition: color 0.15s !important;
    transform: none !important;
  }
  div:has(span.nb-logo) + div[data-testid="stButton"] button:hover {
    color: #fff !important;
    background: transparent !important;
    box-shadow: none !important;
    transform: none !important;
  }

  /* ── Navbar: enlaces normales ────────────────────────────── */
  div:has(span.nb) + div[data-testid="stButton"] button {
    background: transparent !important;
    border: 1px solid transparent !important;
    box-shadow: none !important;
    color: #5d6270 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 7px 18px !important;
    border-radius: 8px !important;
    white-space: nowrap !important;
    width: auto !important;
    letter-spacing: 0.15px !important;
    transition: color 0.15s, background 0.15s, border-color 0.15s !important;
    transform: none !important;
  }
  div:has(span.nb) + div[data-testid="stButton"] button:hover {
    color: #b0b3be !important;
    background: rgba(255,255,255,0.05) !important;
    border-color: #2a2e39 !important;
    box-shadow: none !important;
    transform: none !important;
  }

  /* ── Navbar: enlace ACTIVO ───────────────────────────────── */
  div:has(span.nb-act) + div[data-testid="stButton"] button {
    background: rgba(41,98,255,0.13) !important;
    border: 1px solid rgba(41,98,255,0.35) !important;
    box-shadow: none !important;
    color: #6b9eff !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    padding: 7px 18px !important;
    border-radius: 8px !important;
    white-space: nowrap !important;
    width: auto !important;
    letter-spacing: 0.15px !important;
    transform: none !important;
    transition: background 0.15s, color 0.15s !important;
  }
  div:has(span.nb-act) + div[data-testid="stButton"] button:hover {
    background: rgba(41,98,255,0.20) !important;
    border-color: rgba(41,98,255,0.5) !important;
    color: #88b1ff !important;
    transform: none !important;
    box-shadow: none !important;
  }

  /* ── Navbar: boton Salir ─────────────────────────────────── */
  div:has(span.nb-out) + div[data-testid="stButton"] button {
    background: transparent !important;
    border: 1px solid #363a45 !important;
    box-shadow: none !important;
    color: #787b86 !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    padding: 5px 14px !important;
    border-radius: 20px !important;
    white-space: nowrap !important;
    transform: none !important;
    transition: border-color 0.15s, color 0.15s !important;
  }
  div:has(span.nb-out) + div[data-testid="stButton"] button:hover {
    border-color: #ef5350 !important;
    color: #ef5350 !important;
    background: rgba(239,83,80,0.07) !important;
    box-shadow: none !important;
    transform: none !important;
  }

  /* ── Divisor navbar ──────────────────────────────────────── */
  .nav-divider {
    height: 1px;
    background: #1e222d;
    margin: 4px 0 16px;
  }

  /* ── Titulo de pagina ────────────────────────────────────── */
  .page-title {
    text-align: center !important;
    font-size: 2.6rem !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    letter-spacing: -1.5px !important;
    margin: 0.4rem 0 1.4rem !important;
    line-height: 1.1 !important;
  }

  /* ── Metricas ────────────────────────────────────────────── */
  [data-testid="stMetric"] {
    background: #1e222d; border: 1px solid #2a2e39;
    border-radius: 10px; padding: 14px 18px !important;
  }
  [data-testid="stMetricLabel"] p {
    font-size: 0.68rem !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: 1px !important;
    color: #787b86 !important;
  }
  [data-testid="stMetricValue"] {
    font-size: 1.25rem !important; font-weight: 700 !important; color: #d1d4dc !important;
  }
  [data-testid="stMetricDelta"] svg { display: none; }

  /* ── Inputs ──────────────────────────────────────────────── */
  [data-testid="stTextInput"] input {
    background: #1e222d !important; border: 1px solid #363a45 !important;
    border-radius: 10px !important; color: #d1d4dc !important;
    font-size: 0.9rem !important; padding: 10px 14px !important;
  }
  [data-testid="stTextInput"] input:focus {
    border-color: #2962ff !important;
    box-shadow: 0 0 0 3px rgba(41,98,255,0.12) !important;
  }
  [data-testid="stTextInput"] input::placeholder { color: #4c525e !important; }

  /* ── Selectbox ───────────────────────────────────────────── */
  [data-testid="stSelectbox"] > div > div {
    background: #1e222d !important; border: 1px solid #363a45 !important;
    border-radius: 10px !important; color: #d1d4dc !important;
  }

  /* ── Botones generales (NO navbar) ──────────────────────── */
  [data-testid="stButton"] button {
    border-radius: 22px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.2px !important;
    transition: all 0.15s ease !important;
    padding: 8px 22px !important;
    border: none !important;
    box-shadow: none !important;
  }
  [data-testid="stButton"] button[kind="primary"] {
    background: #2962ff !important; color: #fff !important;
  }
  [data-testid="stButton"] button[kind="primary"]:hover {
    background: #1e4fd8 !important;
    box-shadow: 0 4px 18px rgba(41,98,255,0.45) !important;
    transform: translateY(-1px) !important;
  }
  [data-testid="stButton"] button[kind="secondary"] {
    background: #1e222d !important;
    border: 1px solid #2a2e39 !important;
    color: #9598a1 !important;
  }
  [data-testid="stButton"] button[kind="secondary"]:hover {
    border-color: #2962ff !important; color: #2962ff !important;
    background: rgba(41,98,255,0.07) !important;
  }

  /* ── Download button ─────────────────────────────────────── */
  [data-testid="stDownloadButton"] button {
    border-radius: 22px !important;
    background: #2962ff !important; color: #fff !important;
    font-weight: 600 !important; padding: 8px 22px !important;
  }
  [data-testid="stDownloadButton"] button:hover {
    background: #1e4fd8 !important;
    box-shadow: 0 4px 18px rgba(41,98,255,0.45) !important;
    transform: translateY(-1px) !important;
  }

  /* ── Tabs ────────────────────────────────────────────────── */
  [data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important; border-bottom: 1px solid #2a2e39 !important; gap: 0 !important;
  }
  [data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important; color: #787b86 !important;
    font-size: 0.85rem !important; font-weight: 500 !important;
    padding: 10px 22px !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
  }
  [data-testid="stTabs"] [aria-selected="true"] {
    color: #d1d4dc !important; border-bottom: 2px solid #2962ff !important;
    border-radius: 0 !important;
  }

  hr { border-color: #2a2e39 !important; margin: 0.8rem 0 !important; }

  /* ── Formularios ─────────────────────────────────────────── */
  div[data-testid="stForm"] {
    background: #1a1e2c; border: 1px solid #2a2e39;
    border-radius: 14px; padding: 24px !important;
  }

  /* ── Dataframe ───────────────────────────────────────────── */
  .stDataFrame { border: 1px solid #2a2e39 !important; border-radius: 10px !important; overflow: hidden !important; }

  /* ── Usuario en navbar — pill distinto de los botones de navegacion ── */
  div:has(span.nb-user) + div[data-testid="stButton"] button {
    background: #13161e !important;
    border: 1px solid #2a2e39 !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04),
                0 1px 4px rgba(0,0,0,0.35) !important;
    color: #9598a1 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 7px 16px 7px 36px !important;
    border-radius: 999px !important;
    white-space: nowrap !important;
    cursor: default !important;
    transform: none !important;
    position: relative !important;
    letter-spacing: 0.1px !important;
  }
  div:has(span.nb-user) + div[data-testid="stButton"] button:hover {
    background: #13161e !important;
    border-color: #363a45 !important;
    color: #b0b3be !important;
    transform: none !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04),
                0 1px 4px rgba(0,0,0,0.35) !important;
  }
  /* Avatar circular */
  div:has(span.nb-user) + div[data-testid="stButton"] button::before {
    content: '' !important;
    position: absolute !important;
    left: 12px !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    width: 16px !important;
    height: 16px !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, #4d80ff 0%, #2952dd 100%) !important;
    box-shadow: 0 0 0 2px rgba(41,98,255,0.18) !important;
    pointer-events: none !important;
  }

  #MainMenu, footer, header { visibility: hidden; }
</style>
"""

try:
    st.html(_CSS)
except AttributeError:
    st.markdown(_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Cookie manager
# ---------------------------------------------------------------------------

_cm = stx.CookieManager(key="nuu_cm")

# ── Restaurar sesion desde cookie al recargar la pagina ─────────────────────
# (no restaurar si hay un logout en curso)
if not st.session_state.get("usuario_autenticado") and not st.session_state.get("_logging_out"):
    if "cm_init" not in st.session_state:
        st.session_state["cm_init"] = True
        st.rerun()
    raw = _cm.get("nuu_sess")
    if raw:
        recuperado = leer_token(raw)   # devuelve None si el token es invalido
        if recuperado:
            st.session_state["usuario_autenticado"] = recuperado
            st.session_state["cm_restaurado"] = True
            st.rerun()

# ── Escribir cookie despues de un login fresco ───────────────────────────────
elif (
    st.session_state.get("usuario_autenticado")
    and not st.session_state.get("cm_escrito")
    and not st.session_state.get("cm_restaurado")
):
    st.session_state["cm_escrito"] = True
    _cm.set("nuu_sess", crear_token(st.session_state["usuario_autenticado"]))

# ---------------------------------------------------------------------------
# Paginas
# ---------------------------------------------------------------------------

paginas_publicas = [
    st.Page("all_pages/1_landing_page.py", title="Inicio"),
    st.Page("all_pages/2_auth_page.py",    title="Acceso"),
]
paginas_privadas = [
    st.Page("all_pages/1_landing_page.py", title="Inicio"),
    st.Page("all_pages/6_mercado_page.py", title="Mercado"),
    st.Page("all_pages/7_grafico_page.py", title="Analisis"),
    st.Page("all_pages/8_modelo_page.py",  title="Modelo"),
    st.Page("all_pages/9_admin_page.py",   title="Admin"),
]

usuario = st.session_state.get("usuario_autenticado")

# ---------------------------------------------------------------------------
# Navegacion — obtener pg ANTES del navbar para saber la pagina activa
# ---------------------------------------------------------------------------

if usuario:
    try:
        pg = st.navigation(paginas_privadas, position="hidden")
    except TypeError:
        pg = st.navigation(paginas_privadas)
else:
    try:
        pg = st.navigation(paginas_publicas, position="hidden")
    except TypeError:
        pg = st.navigation(paginas_publicas)

pagina_actual = getattr(pg, "title", "")

# ── Paso 2 del logout: navegacion ya registrada, switch_page es valido ───────
if st.session_state.pop("_logging_out", False):
    st.session_state.clear()
    st.switch_page("all_pages/2_auth_page.py")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _nb(cls="nb"):
    st.markdown(f'<span class="{cls}"></span>', unsafe_allow_html=True)

def _cls_nav(titulo: str) -> str:
    """Devuelve 'nb-act' si es la pagina activa, 'nb' si no."""
    return "nb-act" if pagina_actual == titulo else "nb"


# ---------------------------------------------------------------------------
# Navbar — usuario autenticado
# ---------------------------------------------------------------------------

if usuario:
    try:
        c_logo, c1, c2, c3, c4, c_sp, c_u, c_out = st.columns(
            [1.0, 1.1, 1.1, 1.1, 1.0, 3.8, 1.3, 0.85],
            gap="small"
        )
    except TypeError:
        c_logo, c1, c2, c3, c4, c_sp, c_u, c_out = st.columns(
            [1.0, 1.1, 1.1, 1.1, 1.0, 3.8, 1.3, 0.85]
        )

    with c_logo:
        _nb("nb-logo")
        if st.button("nuu.", key="logo"):
            st.switch_page("all_pages/1_landing_page.py")

    nav_items = [
        (c1, "Mercado",  "all_pages/6_mercado_page.py"),
        (c2, "Analisis", "all_pages/7_grafico_page.py"),
        (c3, "Modelo",   "all_pages/8_modelo_page.py"),
        (c4, "Admin",    "all_pages/9_admin_page.py"),
    ]
    for col, titulo, path in nav_items:
        with col:
            _nb(_cls_nav(titulo))
            if st.button(titulo, key=f"nav_{titulo}"):
                st.switch_page(path)

    with c_u:
        nombre_corto = usuario["nombre"].split()[0]
        _nb("nb-user")
        st.button(nombre_corto, key="btn_user")   # click = rerun inocuo

    with c_out:
        _nb("nb-out")
        if st.button("Salir", key="logout"):
            # Paso 1: sobreescribir cookie con valor invalido y marcar logout.
            # El rerun procesa el set() del CookieManager antes de navegar.
            try:
                _cm.set("nuu_sess", "__x__")
            except Exception:
                pass
            del st.session_state["usuario_autenticado"]
            st.session_state["_logging_out"] = True
            st.rerun()

    try:
        st.html('<div class="nav-divider"></div>')
    except AttributeError:
        st.divider()

# ---------------------------------------------------------------------------
# Sin navbar — usuario no autenticado
# ---------------------------------------------------------------------------

pg.run()
