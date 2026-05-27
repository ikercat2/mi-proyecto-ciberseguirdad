import streamlit as st

st.set_page_config(page_title="Nuu", page_icon="N", layout="wide")

# ---------------------------------------------------------------------------
# CSS global — oculta sidebar, estilos de la navbar
# ---------------------------------------------------------------------------

_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
  }

  /* Ocultar sidebar completamente */
  [data-testid="stSidebar"],
  [data-testid="stSidebarContent"],
  [data-testid="stSidebarNav"],
  section[data-testid="stSidebar"] { display: none !important; }

  /* Ajuste de layout sin sidebar */
  .main .block-container {
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    padding-top: 0.4rem !important;
    max-width: 1400px !important;
  }

  /* Ocultar marcadores de navbar (los span.nb) */
  p:has(span.nb),
  p:has(span.nb-logo),
  p:has(span.nb-out) {
    margin: 0 !important; padding: 0 !important;
    line-height: 0 !important; height: 0 !important;
    overflow: hidden !important; display: block !important;
  }

  /* Botones de navbar — via :has() + selector adyacente */
  div:has(span.nb) + div[data-testid="stButton"] button {
    background: transparent !important;
    border: none !important;
    color: #787b86 !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 6px 14px !important;
    border-radius: 4px !important;
    box-shadow: none !important;
    letter-spacing: 0.1px !important;
    transition: color 0.12s, background 0.12s !important;
  }
  div:has(span.nb) + div[data-testid="stButton"] button:hover {
    color: #d1d4dc !important;
    background: rgba(255,255,255,0.06) !important;
    transform: none !important;
    box-shadow: none !important;
  }

  /* Logo navbar */
  div:has(span.nb-logo) + div[data-testid="stButton"] button {
    background: transparent !important;
    border: none !important;
    color: #d1d4dc !important;
    font-size: 1.25rem !important;
    font-weight: 800 !important;
    padding: 2px 6px !important;
    letter-spacing: -1px !important;
    box-shadow: none !important;
    transform: none !important;
  }
  div:has(span.nb-logo) + div[data-testid="stButton"] button:hover {
    background: transparent !important;
    color: #fff !important;
    box-shadow: none !important;
    transform: none !important;
  }

  /* Boton salir */
  div:has(span.nb-out) + div[data-testid="stButton"] button {
    background: transparent !important;
    border: 1px solid #363a45 !important;
    color: #787b86 !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    padding: 5px 14px !important;
    border-radius: 6px !important;
    box-shadow: none !important;
    transform: none !important;
  }
  div:has(span.nb-out) + div[data-testid="stButton"] button:hover {
    border-color: #ef5350 !important;
    color: #ef5350 !important;
    background: rgba(239,83,80,0.06) !important;
    box-shadow: none !important;
    transform: none !important;
  }

  /* Linea separadora bajo la navbar */
  .nav-divider {
    height: 1px;
    background: #1e222d;
    margin: 4px 0 16px;
  }

  /* Metricas */
  [data-testid="stMetric"] {
    background: #1e222d; border: 1px solid #2a2e39;
    border-radius: 8px; padding: 14px 18px !important;
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

  /* Inputs */
  [data-testid="stTextInput"] input {
    background: #1e222d !important; border: 1px solid #363a45 !important;
    border-radius: 6px !important; color: #d1d4dc !important;
    font-size: 0.9rem !important; padding: 10px 14px !important;
  }
  [data-testid="stTextInput"] input:focus {
    border-color: #2962ff !important;
    box-shadow: 0 0 0 3px rgba(41,98,255,0.12) !important;
  }
  [data-testid="stTextInput"] input::placeholder { color: #4c525e !important; }

  /* Selectbox */
  [data-testid="stSelectbox"] > div > div {
    background: #1e222d !important; border: 1px solid #363a45 !important;
    border-radius: 6px !important; color: #d1d4dc !important;
  }

  /* Botones generales */
  [data-testid="stButton"] button {
    border-radius: 6px !important; font-weight: 600 !important;
    font-size: 0.85rem !important; letter-spacing: 0.2px !important;
    transition: all 0.15s ease !important; padding: 8px 20px !important;
    border: none !important;
  }
  [data-testid="stButton"] button[kind="primary"] {
    background: #2962ff !important; color: #fff !important;
  }
  [data-testid="stButton"] button[kind="primary"]:hover {
    background: #1e4fd8 !important;
    box-shadow: 0 4px 14px rgba(41,98,255,0.4) !important;
    transform: translateY(-1px) !important;
  }
  [data-testid="stButton"] button[kind="secondary"] {
    background: #1e222d !important; border: 1px solid #363a45 !important; color: #9598a1 !important;
  }
  [data-testid="stButton"] button[kind="secondary"]:hover {
    border-color: #2962ff !important; color: #2962ff !important;
    background: rgba(41,98,255,0.07) !important;
  }

  /* Tabs */
  [data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important; border-bottom: 1px solid #2a2e39 !important; gap: 0 !important;
  }
  [data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important; color: #787b86 !important;
    font-size: 0.85rem !important; font-weight: 500 !important;
    padding: 10px 22px !important; border-bottom: 2px solid transparent !important;
  }
  [data-testid="stTabs"] [aria-selected="true"] {
    color: #d1d4dc !important; border-bottom: 2px solid #2962ff !important;
  }

  hr { border-color: #2a2e39 !important; margin: 0.8rem 0 !important; }

  /* Tarjetas de activos */
  .asset-card {
    background: #1e222d; border: 1px solid #2a2e39; border-radius: 10px;
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
    background: #1e222d; border: 1px solid #2a2e39; border-radius: 8px;
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
    border-radius: 12px; padding: 24px !important;
  }

  /* Dataframe */
  .stDataFrame { border: 1px solid #2a2e39 !important; border-radius: 8px !important; overflow: hidden !important; }

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
    st.Page("all_pages/8_modelo_page.py",  title="Modelo IA"),
    st.Page("all_pages/9_admin_page.py",   title="Admin"),
]

usuario = st.session_state.get("usuario_autenticado")

# ---------------------------------------------------------------------------
# Helpers para navbar
# ---------------------------------------------------------------------------

def _nb(cls="nb"):
    st.markdown(f'<span class="{cls}"></span>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Navbar — usuario autenticado
# ---------------------------------------------------------------------------

if usuario:
    c_logo, c1, c2, c3, c4, c5, c_sp, c_u, c_out = st.columns(
        [1.1, 1, 1, 1, 1, 1, 3.8, 1.8, 0.9]
    )
    with c_logo:
        _nb("nb-logo")
        if st.button("nuu.", key="logo"):
            st.switch_page("all_pages/1_landing_page.py")

    nav_items = [
        (c1, "Inicio",    "all_pages/1_landing_page.py"),
        (c2, "Mercado",   "all_pages/6_mercado_page.py"),
        (c3, "Analisis",  "all_pages/7_grafico_page.py"),
        (c4, "Modelo IA", "all_pages/8_modelo_page.py"),
        (c5, "Admin",     "all_pages/9_admin_page.py"),
    ]
    for col, name, path in nav_items:
        with col:
            _nb()
            if st.button(name, key=f"nav_{name}"):
                st.switch_page(path)

    with c_u:
        st.markdown(
            f'<div style="text-align:right;padding:10px 0 0;font-size:0.8rem;'
            f'color:#9598a1;font-weight:500;">{usuario["nombre"]}</div>',
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
# Navbar — usuario no autenticado
# ---------------------------------------------------------------------------

else:
    c_logo, c_sp, c_acc = st.columns([1.1, 10, 1.2])
    with c_logo:
        _nb("nb-logo")
        if st.button("nuu.", key="logo_pub"):
            st.switch_page("all_pages/1_landing_page.py")
    with c_acc:
        if st.button("Acceder", key="nav_acceder", type="primary"):
            st.switch_page("all_pages/2_auth_page.py")

    try:
        st.html('<div class="nav-divider"></div>')
    except AttributeError:
        st.divider()

    try:
        pg = st.navigation(paginas_publicas, position="hidden")
    except TypeError:
        pg = st.navigation(paginas_publicas)

pg.run()
