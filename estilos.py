"""
estilos.py — Estilos globales e inyeccion de Google Fonts.
"""
import streamlit as st

_HTML = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    box-sizing: border-box;
  }

  #MainMenu, footer, header { visibility: hidden; }

  .block-container {
    padding-top: 1.8rem !important;
    padding-bottom: 2rem !important;
    max-width: 1400px !important;
  }

  /* Tipografia */
  h1 {
    font-size: 1.45rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px !important;
    color: #d1d4dc !important;
  }
  h2 { font-size: 1.1rem !important; font-weight: 600 !important; color: #d1d4dc !important; }
  p, span, label { color: #9598a1 !important; }

  /* Metricas */
  [data-testid="stMetric"] {
    background: #1e222d;
    border: 1px solid #2a2e39;
    border-radius: 8px;
    padding: 14px 18px !important;
  }
  [data-testid="stMetricLabel"] p {
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    color: #787b86 !important;
  }
  [data-testid="stMetricValue"] {
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    color: #d1d4dc !important;
  }
  [data-testid="stMetricDelta"] svg { display: none; }

  /* Inputs */
  [data-testid="stTextInput"] input {
    background: #1e222d !important;
    border: 1px solid #363a45 !important;
    border-radius: 6px !important;
    color: #d1d4dc !important;
    font-size: 0.9rem !important;
    padding: 10px 14px !important;
    transition: border-color 0.15s !important;
  }
  [data-testid="stTextInput"] input:focus {
    border-color: #2962ff !important;
    box-shadow: 0 0 0 3px rgba(41,98,255,0.12) !important;
    outline: none !important;
  }
  [data-testid="stTextInput"] input::placeholder { color: #4c525e !important; }

  /* Selectbox */
  [data-testid="stSelectbox"] > div > div {
    background: #1e222d !important;
    border: 1px solid #363a45 !important;
    border-radius: 6px !important;
    color: #d1d4dc !important;
  }

  /* Botones */
  [data-testid="stButton"] button {
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.2px !important;
    transition: all 0.15s ease !important;
    padding: 8px 20px !important;
    border: none !important;
  }
  [data-testid="stButton"] button[kind="primary"] {
    background: #2962ff !important;
    color: #fff !important;
  }
  [data-testid="stButton"] button[kind="primary"]:hover {
    background: #1e4fd8 !important;
    box-shadow: 0 4px 14px rgba(41,98,255,0.4) !important;
    transform: translateY(-1px) !important;
  }
  [data-testid="stButton"] button[kind="secondary"] {
    background: #1e222d !important;
    border: 1px solid #363a45 !important;
    color: #9598a1 !important;
  }
  [data-testid="stButton"] button[kind="secondary"]:hover {
    border-color: #2962ff !important;
    color: #2962ff !important;
    background: rgba(41,98,255,0.07) !important;
  }

  /* Tabs */
  [data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #2a2e39 !important;
    gap: 0 !important;
  }
  [data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    color: #787b86 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 10px 22px !important;
    border-bottom: 2px solid transparent !important;
  }
  [data-testid="stTabs"] [aria-selected="true"] {
    color: #d1d4dc !important;
    border-bottom: 2px solid #2962ff !important;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: #161b27 !important;
    border-right: 1px solid #2a2e39 !important;
  }
  [data-testid="stSidebarNav"] a {
    border-radius: 6px !important;
    margin: 2px 8px !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: #9598a1 !important;
    transition: background 0.1s, color 0.1s !important;
  }
  [data-testid="stSidebarNav"] a:hover {
    background: #1e222d !important;
    color: #d1d4dc !important;
  }
  [data-testid="stSidebarNav"] [aria-selected="true"] {
    background: rgba(41,98,255,0.12) !important;
    color: #2962ff !important;
  }

  /* Divisor */
  hr { border-color: #2a2e39 !important; margin: 1rem 0 !important; }

  /* Dataframe */
  .stDataFrame { border: 1px solid #2a2e39 !important; border-radius: 8px !important; overflow: hidden !important; }

  /* === TARJETAS DE ACTIVOS === */
  .asset-card {
    background: #1e222d;
    border: 1px solid #2a2e39;
    border-radius: 10px;
    padding: 16px;
    transition: border-color 0.15s, background 0.15s;
    cursor: pointer;
  }
  .asset-card:hover { background: #232836; border-color: #2962ff; }
  .asset-sym  { font-size: 0.9rem; font-weight: 700; color: #d1d4dc; letter-spacing: 0.5px; }
  .asset-name { font-size: 0.7rem; color: #5d6168; margin: 3px 0 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .asset-price { font-size: 1.05rem; font-weight: 600; color: #d1d4dc; margin-bottom: 4px; }
  .chg-up   { color: #26a69a; font-size: 0.82rem; font-weight: 600; }
  .chg-down { color: #ef5350; font-size: 0.82rem; font-weight: 600; }

  /* Boton invisible sobre la tarjeta — hace la tarjeta clickable */
  div[data-testid="column"]:has(.asset-card) {
    position: relative !important;
    cursor: pointer !important;
  }
  div[data-testid="column"]:has(.asset-card) [data-testid="stButton"] {
    position: absolute !important;
    inset: 0 !important;
    z-index: 20 !important;
    margin: 0 !important;
    padding: 0 !important;
  }
  div[data-testid="column"]:has(.asset-card) [data-testid="stButton"] button {
    opacity: 0 !important;
    width: 100% !important;
    height: 100% !important;
    cursor: pointer !important;
    border: none !important;
    background: transparent !important;
  }

  /* === BARRA DE INDICES === */
  .idx-bar { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 4px; }
  .idx-card {
    background: #1e222d;
    border: 1px solid #2a2e39;
    border-radius: 8px;
    padding: 10px 16px;
    display: inline-block;
    transition: border-color 0.15s;
    cursor: default;
  }
  .idx-card:hover { border-color: #3d4255; }
  .idx-sym  { font-size: 0.65rem; font-weight: 700; color: #5d6168; letter-spacing: 1.2px; text-transform: uppercase; }
  .idx-val  { font-size: 0.95rem; font-weight: 600; color: #d1d4dc; }
  .idx-chg  { font-size: 0.78rem; margin-left: 7px; font-weight: 600; }

  /* Titulo de seccion */
  .sec-h {
    font-size: 0.65rem;
    font-weight: 700;
    color: #5d6168;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 22px 0 12px;
  }
</style>
"""


_JS_CARDS = """
<script>
(function attach() {
    var cards = window.parent.document.querySelectorAll('.asset-card');
    cards.forEach(function(card) {
        if (card.dataset.handled) return;
        card.dataset.handled = '1';
        card.style.cursor = 'pointer';
        card.addEventListener('click', function() {
            var col = this.closest('[data-testid="column"]');
            if (col) { var btn = col.querySelector('button'); if (btn) btn.click(); }
        });
    });
    setTimeout(attach, 800);
})();
</script>
"""


def aplicar_estilos() -> None:
    try:
        st.html(_HTML)
    except AttributeError:
        st.markdown(_HTML, unsafe_allow_html=True)


def activar_tarjetas_clickables() -> None:
    """Inyecta JS para que las tarjetas sean clickables sin boton visible."""
    import streamlit.components.v1 as components
    components.html(_JS_CARDS, height=0)


def tarjeta_activo(simbolo: str, nombre: str, precio: float, cambio_pct: float) -> str:
    cls   = "chg-up" if cambio_pct >= 0 else "chg-down"
    signo = "+" if cambio_pct >= 0 else ""
    precio_s = f"${precio:,.2f}" if precio >= 1 else f"${precio:.4f}"
    return (
        f'<div class="asset-card">'
        f'<div class="asset-sym">{simbolo}</div>'
        f'<div class="asset-name">{nombre}</div>'
        f'<div class="asset-price">{precio_s}</div>'
        f'<div class="{cls}">{signo}{cambio_pct:.2f}%</div>'
        f'</div>'
    )


def tarjeta_indice(nombre: str, precio: float, cambio_pct: float) -> str:
    color = "#26a69a" if cambio_pct >= 0 else "#ef5350"
    signo = "+" if cambio_pct >= 0 else ""
    return (
        f'<div class="idx-card">'
        f'<div class="idx-sym">{nombre}</div>'
        f'<div class="idx-val">{precio:,.2f}'
        f'<span class="idx-chg" style="color:{color};">{signo}{cambio_pct:.2f}%</span>'
        f'</div></div>'
    )
