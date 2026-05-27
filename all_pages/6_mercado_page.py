"""
6_mercado_page.py — Vista general del mercado: indices, acciones y criptomonedas.
"""
import os
import sys

import pandas as pd
import streamlit as st
import yfinance as yf

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from estilos import aplicar_estilos, activar_tarjetas_clickables, tarjeta_activo, tarjeta_indice

if not st.session_state.get("usuario_autenticado"):
    st.warning("Debes iniciar sesion para acceder.")
    st.stop()

aplicar_estilos()

# ---------------------------------------------------------------------------
# Catalogos de activos
# ---------------------------------------------------------------------------

INDICES = {
    "^GSPC":  "S&P 500",
    "^IXIC":  "NASDAQ",
    "^DJI":   "Dow Jones",
    "^DAX":   "DAX",
    "^FTSE":  "FTSE 100",
    "^N225":  "Nikkei 225",
    "GC=F":   "Oro",
    "BTC-USD": "Bitcoin",
}

ACCIONES_US = {
    "AAPL":  "Apple Inc.",
    "MSFT":  "Microsoft",
    "NVDA":  "NVIDIA",
    "AMZN":  "Amazon",
    "GOOGL": "Alphabet",
    "TSLA":  "Tesla",
    "META":  "Meta Platforms",
    "JPM":   "JPMorgan Chase",
    "V":     "Visa",
    "WMT":   "Walmart",
    "XOM":   "ExxonMobil",
    "JNJ":   "Johnson & Johnson",
}

CRYPTO = {
    "BTC-USD":  "Bitcoin",
    "ETH-USD":  "Ethereum",
    "BNB-USD":  "BNB",
    "SOL-USD":  "Solana",
    "XRP-USD":  "XRP",
    "ADA-USD":  "Cardano",
    "DOGE-USD": "Dogecoin",
    "AVAX-USD": "Avalanche",
}

EUROPA = {
    "SAN.MC":  "Santander",
    "TEF.MC":  "Telefonica",
    "BBVA.MC": "BBVA",
    "IBE.MC":  "Iberdrola",
    "REP.MC":  "Repsol",
    "ITX.MC":  "Inditex",
    "MC.PA":   "LVMH",
    "SAP.DE":  "SAP",
    "ASML.AS": "ASML",
    "SHEL":    "Shell",
    "NVO":     "Novo Nordisk",
    "BP":      "BP",
}

# ---------------------------------------------------------------------------
# Descarga de cotizaciones (cacheada 5 min)
# ---------------------------------------------------------------------------

@st.cache_data(ttl=300, show_spinner=False)
def obtener_cotizaciones(simbolos: tuple) -> dict:
    if not simbolos:
        return {}
    try:
        raw = yf.download(
            list(simbolos), period="5d",
            auto_adjust=True, progress=False, threads=True,
        )
    except Exception:
        return {}

    resultado = {}

    if isinstance(raw.columns, pd.MultiIndex):
        closes = raw["Close"]
        for sym in simbolos:
            if sym in closes.columns:
                serie = closes[sym].dropna()
                if len(serie) >= 2:
                    precio   = float(serie.iloc[-1])
                    anterior = float(serie.iloc[-2])
                    resultado[sym] = {
                        "precio":     precio,
                        "cambio_pct": (precio - anterior) / anterior * 100,
                    }
    else:
        serie = raw["Close"].dropna()
        if len(serie) >= 2 and simbolos:
            precio   = float(serie.iloc[-1])
            anterior = float(serie.iloc[-2])
            resultado[simbolos[0]] = {
                "precio":     precio,
                "cambio_pct": (precio - anterior) / anterior * 100,
            }

    return resultado


def _ir_a_grafico(sym: str) -> None:
    st.session_state["mercado_simbolo"] = sym
    st.switch_page("all_pages/7_grafico_page.py")


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

st.markdown('<h1 class="page-title">Mercado</h1>', unsafe_allow_html=True)

col_s, col_b = st.columns([4, 1])
with col_s:
    busqueda = st.text_input(
        "buscar", placeholder="Buscar simbolo: AAPL, BTC-USD, TSLA...",
        label_visibility="collapsed",
    )
with col_b:
    if st.button("Ver grafico", use_container_width=True, type="primary"):
        if busqueda.strip():
            _ir_a_grafico(busqueda.strip().upper())

st.divider()

# ── Indices globales ──────────────────────────────────────────────────────────

st.markdown('<div class="sec-h">Indices globales</div>', unsafe_allow_html=True)

with st.spinner("Cargando..."):
    datos_idx = obtener_cotizaciones(tuple(INDICES.keys()))

if datos_idx:
    partes = []
    for sym, nombre in INDICES.items():
        if sym in datos_idx:
            d = datos_idx[sym]
            partes.append(tarjeta_indice(nombre, d["precio"], d["cambio_pct"]))
    st.markdown(
        '<div class="idx-bar">' + "".join(partes) + "</div>",
        unsafe_allow_html=True,
    )

st.divider()

# ── Tabs de activos ───────────────────────────────────────────────────────────

tab_us, tab_crypto, tab_eu = st.tabs(["Acciones US", "Criptomonedas", "Europa"])


def _grilla(activos: dict, datos: dict, prefijo: str) -> None:
    simbolos = list(activos.keys())
    filas = [simbolos[i : i + 4] for i in range(0, len(simbolos), 4)]
    for fila in filas:
        cols = st.columns(4)
        for j, sym in enumerate(fila):
            with cols[j]:
                if sym in datos:
                    d = datos[sym]
                    st.markdown(
                        tarjeta_activo(sym, activos[sym], d["precio"], d["cambio_pct"]),
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div class="asset-card"><div class="asset-sym">{sym}</div>'
                        f'<div class="asset-name">{activos[sym]}</div>'
                        f'<div style="color:#4c525e;font-size:0.78rem;margin-top:8px;">Sin datos</div></div>',
                        unsafe_allow_html=True,
                    )
                # Boton invisible — hace toda la tarjeta clickable via CSS :has()
                if st.button("", key=f"{prefijo}_{sym}"):
                    _ir_a_grafico(sym)


with tab_us:
    with st.spinner("Cargando acciones..."):
        datos_us = obtener_cotizaciones(tuple(ACCIONES_US.keys()))
    _grilla(ACCIONES_US, datos_us, "us")

with tab_crypto:
    with st.spinner("Cargando criptomonedas..."):
        datos_cr = obtener_cotizaciones(tuple(CRYPTO.keys()))
    _grilla(CRYPTO, datos_cr, "cr")

with tab_eu:
    with st.spinner("Cargando acciones europeas..."):
        datos_eu = obtener_cotizaciones(tuple(EUROPA.keys()))
    _grilla(EUROPA, datos_eu, "eu")

# JS que hace las tarjetas clickables
activar_tarjetas_clickables()
