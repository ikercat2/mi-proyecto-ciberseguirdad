"""
estilos.py — Estilos compartidos y componentes HTML para el dashboard.
"""
import streamlit as st

_FONT = "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"

_CSS = f"""
<link href="{_FONT}" rel="stylesheet">
<style>
  html, body, [class*="css"], .stMarkdown p,
  .stButton button, input, select, label, span,
  .stTextInput input, .stSelectbox div {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
  }}

  #MainMenu {{ visibility: hidden; }}
  footer    {{ visibility: hidden; }}

  /* Tarjetas de activos */
  .asset-card {{
    background: #1e222d;
    border: 1px solid #2a2e39;
    border-radius: 8px;
    padding: 14px 16px;
    min-height: 96px;
    margin-bottom: 2px;
  }}
  .asset-sym {{
    font-size: 0.88rem;
    font-weight: 600;
    color: #d1d4dc;
    letter-spacing: 0.3px;
  }}
  .asset-name {{
    font-size: 0.7rem;
    color: #787b86;
    margin: 2px 0 8px 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  .asset-price {{
    font-size: 1rem;
    font-weight: 500;
    color: #d1d4dc;
    margin-bottom: 3px;
  }}
  .chg-up   {{ color: #26a69a; font-size: 0.82rem; font-weight: 500; }}
  .chg-down {{ color: #ef5350; font-size: 0.82rem; font-weight: 500; }}

  /* Barra de índices */
  .idx-bar {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 8px;
  }}
  .idx-card {{
    background: #1e222d;
    border: 1px solid #2a2e39;
    border-radius: 6px;
    padding: 8px 14px;
    display: inline-block;
  }}
  .idx-sym {{ font-size: 0.7rem; font-weight: 600; color: #787b86; letter-spacing: 0.8px; text-transform: uppercase; }}
  .idx-val {{ font-size: 0.92rem; font-weight: 500; color: #d1d4dc; }}
  .idx-chg {{ font-size: 0.78rem; margin-left: 6px; }}

  /* Títulos de sección */
  .sec-h {{
    font-size: 0.72rem;
    font-weight: 600;
    color: #787b86;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 20px 0 10px;
  }}

  /* Botones secundarios */
  div[data-testid="stButton"] button[kind="secondary"] {{
    background: transparent !important;
    border: 1px solid #2a2e39 !important;
    color: #9598a1 !important;
    font-size: 0.75rem !important;
    border-radius: 4px !important;
  }}
  div[data-testid="stButton"] button[kind="secondary"]:hover {{
    border-color: #434651 !important;
    color: #d1d4dc !important;
  }}
</style>
"""


def aplicar_estilos() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def tarjeta_activo(simbolo: str, nombre: str, precio: float, cambio_pct: float) -> str:
    cls   = "chg-up" if cambio_pct >= 0 else "chg-down"
    signo = "+" if cambio_pct >= 0 else ""
    precio_s = f"${precio:,.2f}" if precio >= 1 else f"${precio:.4f}"
    return (
        f'<div class="asset-card">'
        f'  <div class="asset-sym">{simbolo}</div>'
        f'  <div class="asset-name">{nombre}</div>'
        f'  <div class="asset-price">{precio_s}</div>'
        f'  <div class="{cls}">{signo}{cambio_pct:.2f}%</div>'
        f'</div>'
    )


def tarjeta_indice(nombre: str, precio: float, cambio_pct: float) -> str:
    color = "#26a69a" if cambio_pct >= 0 else "#ef5350"
    signo = "+" if cambio_pct >= 0 else ""
    return (
        f'<div class="idx-card">'
        f'  <div class="idx-sym">{nombre}</div>'
        f'  <div class="idx-val">{precio:,.2f}'
        f'    <span class="idx-chg" style="color:{color};">{signo}{cambio_pct:.2f}%</span>'
        f'  </div>'
        f'</div>'
    )
