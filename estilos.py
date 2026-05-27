"""
estilos.py — Solo estilos especificos de paginas internas (tarjetas, indices).
Los estilos globales (botones, inputs, tabs, etc.) viven en main.py para
evitar que se sobreescriban los estilos de la navbar.
"""
import streamlit as st

# Solo lo que no esta en main.py
_HTML_PAGINAS = """
<style>
  /* ── Tarjetas de activos ────────────────────────────────── */
  .asset-card {
    background: #1e222d; border: 1px solid #2a2e39; border-radius: 12px;
    padding: 16px; transition: border-color 0.15s, background 0.15s; cursor: pointer;
  }
  .asset-card:hover { background: #232836; border-color: #2962ff; }
  .asset-sym  { font-size: 0.9rem; font-weight: 700; color: #d1d4dc; letter-spacing: 0.5px; }
  .asset-name { font-size: 0.7rem; color: #5d6168; margin: 3px 0 10px;
                white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .asset-price { font-size: 1.05rem; font-weight: 600; color: #d1d4dc; margin-bottom: 4px; }
  .chg-up   { color: #26a69a; font-size: 0.82rem; font-weight: 600; }
  .chg-down { color: #ef5350; font-size: 0.82rem; font-weight: 600; }

  /* Cursor pointer en toda la columna / bloque que contiene una tarjeta */
  div[data-testid="column"]:has(.asset-card),
  div[data-testid="stVerticalBlock"]:has(.asset-card) {
    cursor: pointer !important;
  }

  /*
   * El stElementContainer que envuelve el stButton (el circulo gris)
   * debe colapsar a 0 sin desaparecer del DOM para que JS pueda clicar el boton.
   * Se apunta tanto al wrapper (stElementContainer) como al propio stButton y button.
   */
  div[data-testid="column"]:has(.asset-card) [data-testid="stElementContainer"]:has([data-testid="stButton"]),
  div[data-testid="stVerticalBlock"]:has(.asset-card) [data-testid="stElementContainer"]:has([data-testid="stButton"]) {
    height: 0 !important;
    min-height: 0 !important;
    max-height: 0 !important;
    overflow: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
    visibility: hidden !important;
  }

  div[data-testid="column"]:has(.asset-card) [data-testid="stButton"],
  div[data-testid="stVerticalBlock"]:has(.asset-card) [data-testid="stButton"],
  div[data-testid="column"]:has(.asset-card) [data-testid="stButton"] *,
  div[data-testid="stVerticalBlock"]:has(.asset-card) [data-testid="stButton"] * {
    height: 0 !important;
    min-height: 0 !important;
    max-height: 0 !important;
    overflow: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
    background: transparent !important;
    visibility: hidden !important;
    line-height: 0 !important;
  }

  /* ── Barra de indices ───────────────────────────────────── */
  .idx-bar { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 4px; }
  .idx-card {
    background: #1e222d; border: 1px solid #2a2e39; border-radius: 10px;
    padding: 10px 16px; display: inline-block; transition: border-color 0.15s;
  }
  .idx-card:hover { border-color: #3d4255; }
  .idx-sym  { font-size: 0.65rem; font-weight: 700; color: #5d6168; letter-spacing: 1.2px; text-transform: uppercase; }
  .idx-val  { font-size: 0.95rem; font-weight: 600; color: #d1d4dc; }
  .idx-chg  { font-size: 0.78rem; margin-left: 7px; font-weight: 600; }

  /* ── Titulo de seccion ──────────────────────────────────── */
  .sec-h {
    font-size: 0.65rem; font-weight: 700; color: #5d6168;
    text-transform: uppercase; letter-spacing: 2px; margin: 22px 0 12px;
  }
</style>
"""

_JS_CARDS = """
<script>
(function attach() {
    var doc = window.parent.document;
    var cards = doc.querySelectorAll('.asset-card');
    cards.forEach(function(card) {
        if (card.dataset.handled) return;
        card.dataset.handled = '1';
        card.addEventListener('click', function() {
            // Subir al column o al stVerticalBlock segun la version de Streamlit
            var container = this.closest('[data-testid="column"]')
                         || this.closest('[data-testid="stVerticalBlock"]');
            if (!container) return;

            // El boton puede estar colapsado (visibility:hidden, height:0)
            // pero sigue en el DOM y acepta .click() programatico
            var btn = container.querySelector('[data-testid="stButton"] button');
            if (btn) btn.click();
        });
    });
    setTimeout(attach, 600);
})();
</script>
"""


def aplicar_estilos() -> None:
    try:
        st.html(_HTML_PAGINAS)
    except AttributeError:
        st.markdown(_HTML_PAGINAS, unsafe_allow_html=True)


def activar_tarjetas_clickables() -> None:
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
