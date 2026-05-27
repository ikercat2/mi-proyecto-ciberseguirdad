import streamlit as st

st.set_page_config(page_title="Nuu", page_icon="N", layout="wide")

# ---------------------------------------------------------------------------
# CSS global
# ---------------------------------------------------------------------------

_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
  }

  /* Ocultar sidebar completamente */
  [data-testid="stSidebar"],
  [data-testid="stSidebarContent"],
  [data-testid="stSidebarNav"],
  section[data-testid="stSidebar"] { display: none !important; }

  /* Layout sin sidebar */
  .main .block-container {
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    padding-top: 0.4rem !important;
    max-width: 1400px !important;
  }

  /* Ocultar marcadores de navbar */
  p:has(span.nb),
  p:has(span.nb-logo),
  p:has(span.nb-out) {
    margin: 0 !important; padding: 0 !important;
    line-height: 0 !important; height: 0 !important;
    overflow: hidden !important; display: block !important;
  }

  /* ── Botones de navbar ─────────────────────────────────── */
  div:has(span.nb) + div[data-testid="stButton"] button {
    background: transparent !important;
    border: none !important;
    color: #9598a1 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 7px 18px !important;
    border-radius: 22px !important;
    min-width: 96px !important;
    white-space: nowrap !important;
    box-shadow: none !important;
    letter-spacing: 0.2px !important;
    transition: color 0.15s, background 0.15s !important;
  }
  div:has(span.nb) + div[data-testid="stButton"] button:hover {
    color: #fff !important;
    background: rgba(41,98,255,0.18) !important;
    transform: none !important;
    box-shadow: none !important;
  }

  /* ── Logo navbar ────────────────────────────────────────── */
  div:has(span.nb-logo) + div[data-testid="stButton"] button {
    background: transparent !important;
    border: none !important;
    color: #d1d4dc !important;
    font-size: 1.25rem !important;
    font-weight: 800 !important;
    padding: 2px 8px !important;
    letter-spacing: -1px !important;
    min-width: unset !important;
    box-shadow: none !important;
    transform: none !important;
    white-space: nowrap !important;
  }
  div:has(span.nb-logo) + div[data-testid="stButton"] button:hover {
    background: transparent !important;
    color: #fff !important;
    box-shadow: none !important;
    transform: none !important;
  }

  /* ── Boton Salir ────────────────────────────────────────── */
  div:has(span.nb-out) + div[data-testid="stButton"] button {
    background: transparent !important;
    border: 1px solid #363a45 !important;
    color: #9598a1 !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    padding: 6px 16px !important;
    border-radius: 22px !important;
    min-width: unset !important;
    white-space: nowrap !important;
    box-shadow: none !important;
    transform: none !important;
  }
  div:has(span.nb-out) + div[data-testid="stButton"] button:hover {
    border-color: #ef5350 !important;
    color: #ef5350 !important;
    background: rgba(239,83,80,0.07) !important;
    box-shadow: none !important;
    transform: none !important;
  }

  /* Linea separadora bajo la navbar */
  .nav-divider {
    height: 1px;
    background: #1e222d;
    margin: 4px 0 16px;
  }

  /* ── Titulo de pagina (centrado, grande, blanco) ────────── */
  .page-title {
    text-align: center !important;
    font-size: 2.6rem !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    letter-spacing: -1.5px !important;
    margin: 0.4rem 0 1.4rem !important;
    line-height: 1.1 !important;
  }

  /* ── Metricas ───────────────────────────────────────────── */
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

  /* ── Inputs ─────────────────────────────────────────────── */
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

  /* ── Selectbox ──────────────────────────────────────────── */
  [data-testid="stSelectbox"] > div > div {
    background: #1e222d !important; border: 1px solid #363a45 !important;
    border-radius: 10px !important; color: #d1d4dc !important;
  }

  /* ── Botones generales ──────────────────────────────────── */
  [data-testid="stButton"] button {
    border-radius: 22px !important; font-weight: 600 !important;
    font-size: 0.85rem !important; letter-spacing: 0.2px !important;
    transition: all 0.15s ease !important; padding: 8px 22px !important;
    border: none !important;
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
    background: #1e222d !important; border: 1px solid #363a45 !important; color: #9598a1 !important;
  }
  [data-testid="stButton"] button[kind="secondary"]:hover {
    border-color: #2962ff !important; color: #2962ff !important;
    background: rgba(41,98,255,0.07) !important;
  }

  /* ── Download button ────────────────────────────────────── */
  [data-testid="stDownloadButton"] button {
    border-radius: 22px !important;
    background: #2962ff !important; color: #fff !important;
    font-weight: 600 !important; padding: 8px 22px !important;
    transition: all 0.15s ease !important;
  }
  [data-testid="stDownloadButton"] button:hover {
    background: #1e4fd8 !important;
    box-shadow: 0 4px 18px rgba(41,98,255,0.45) !important;
    transform: translateY(-1px) !important;
  }

  /* ── Tabs ───────────────────────────────────────────────── */
  [data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important; border-bottom: 1px solid #2a2e39 !important; gap: 0 !important;
  }
  [data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important; color: #787b86 !important;
    font-size: 0.85rem !important; font-weight: 500 !important;
    padding: 10px 22px !important; border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
  }
  [data-testid="stTabs"] [aria-selected="true"] {
    color: #d1d4dc !important; border-bottom: 2px solid #2962ff !important;
  }

  hr { border-color: #2a2e39 !important; margin: 0.8rem 0 !important; }

  /* ── Tarjetas de activos ────────────────────────────────── */
  .asset-card {
    background: #1e222d; border: 1px solid #2a2e39; border-radius: 12px;
    padding: 16px; transition: border-color 0.15s, background 0.15s; cursor: pointer;
  }
  .asset-card:hover { background: #232836; border-color: #2962ff; }
  .asset-sym  { font-size: 0.9rem; font-weight: 700; color: #d1d4dc; letter-spacing: 0.5px; }
  .asset-name { font-size: 0.7rem; color: #5d6168; margin: 3px 0 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .asset-price { font-size: 1.05rem; font-weight: 600; color: #d1d4dc; margin-bottom: 4px; }
  .chg-up   { color: #26a69a; font-size: 0.82rem; font-weight: 600; }
  .chg-down { color: #ef5350; font-size: 0.82rem; font-weight: 600; }

  div[data-testid="column"]:has(.asset-card) { position: relative !important; cursor: pointer !important; }
  div[data-testid="column"]:has(.asset-card) [data-testid="stButton"] {
    position: absolute !important; inset: 0 !important; z-index: 20 !important;
  }
  div[data-testid="column"]:has(.asset-card) [data-testid="stButton"] button {
    opacity: 0 !important; width: 100% !important; height: 100% !important;
    cursor: pointer !important; border: none !important; background: transparent !important;
  }

  .idx-bar { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 4px; }
  .idx-card {
    background: #1e222d; border: 1px solid #2a2e39; border-radius: 10px;
    padding: 10px 16px; display: inline-block; transition: border-color 0.15s;
  }
  .idx-card:hover { border-color: #3d4255; }
  .idx-sym  { font-size: 0.65rem; font-weight: 700; color: #5d6168; letter-spacing: 1.2px; text-transform: uppercase; }
  .idx-val  { font-size: 0.95rem; font-weight: 600; color: #d1d4dc; }
  .idx-chg  { font-size: 0.78rem; margin-left: 7px; font-weight: 600; }

  .sec-h {
    font-size: 0.65rem; font-weight: 700; color: #5d6168;
    text-transform: uppercase; letter-spacing: 2px; margin: 22px 0 12px;
  }

  /* Formularios */
  div[data-testid="stForm"] {
    background: #1a1e2c; border: 1px solid #2a2e39;
    border-radius: 14px; padding: 24px !important;
  }

  /* Dataframe */
  .stDataFrame { border: 1px solid #2a2e39 !important; border-radius: 10px !important; overflow: hidden !important; }

  /* Material Symbols */
  .material-symbols-outlined {
    font-family: 'Material Symbols Outlined' !important;
    font-weight: normal; font-style: normal;
    line-height: 1; letter-spacing: normal; text-transform: none;
    display: inline-block; white-space: nowrap;
    word-wrap: normal; direction: ltr;
    -webkit-font-smoothing: antialiased;
  }

  /* Usuario en navbar */
  .nav-user {
    display: flex; align-items: center; justify-content: flex-end;
    gap: 7px; padding-top: 9px;
  }
  .nav-user .material-symbols-outlined {
    font-size: 18px !important; color: #5d6168;
    font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 20;
  }
  .nav-user span.name {
    font-size: 0.8rem !important; color: #9598a1 !important; font-weight: 500 !important;
  }

  #MainMenu, footer, header { visibility: hidden; }
</style>
"""

try:
    st.html(_CSS)
except AttributeError:
    st.markdown(_CSS, unsafe_allow_html=True)

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
# Helpers
# ---------------------------------------------------------------------------

def _nb(cls="nb"):
    st.markdown(f'<span class="{cls}"></span>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Navbar — usuario autenticado
# ---------------------------------------------------------------------------

if usuario:
    c_logo, c1, c2, c3, c4, c_sp, c_u, c_out = st.columns(
        [1.1, 1.1, 1.1, 1.1, 1.1, 3.5, 1.8, 0.9]
    )
    with c_logo:
        _nb("nb-logo")
        if st.button("nuu.", key="logo"):
            st.switch_page("all_pages/1_landing_page.py")

    nav_items = [
        (c1, "Mercado",   "all_pages/6_mercado_page.py"),
        (c2, "Analisis",  "all_pages/7_grafico_page.py"),
        (c3, "Modelo",    "all_pages/8_modelo_page.py"),
        (c4, "Admin",     "all_pages/9_admin_page.py"),
    ]
    for col, name, path in nav_items:
        with col:
            _nb()
            if st.button(name, key=f"nav_{name}"):
                st.switch_page(path)

    with c_u:
        st.markdown(
            f'<div class="nav-user">'
            f'<span class="material-symbols-outlined">account_circle</span>'
            f'<span class="name">{usuario["nombre"].split()[0]}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c_out:
        _nb("nb-out")
        if st.button("Salir", key="logout"):
            del st.session_state["usuario_autenticado"]
            st.rerun()

    try:
        st.html('<div class="nav-divider"></div>')
    except AttributeError:
        st.divider()

    try:
        pg = st.navigation(paginas_privadas, position="hidden")
    except TypeError:
        pg = st.navigation(paginas_privadas)

# ---------------------------------------------------------------------------
# Navbar — usuario no autenticado (solo logo)
# ---------------------------------------------------------------------------

else:
    c_logo, c_sp = st.columns([1.1, 10.9])
    with c_logo:
        _nb("nb-logo")
        if st.button("nuu.", key="logo_pub"):
            st.switch_page("all_pages/1_landing_page.py")

    try:
        st.html('<div class="nav-divider"></div>')
    except AttributeError:
        st.divider()

    try:
        pg = st.navigation(paginas_publicas, position="hidden")
    except TypeError:
        pg = st.navigation(paginas_publicas)

pg.run()
