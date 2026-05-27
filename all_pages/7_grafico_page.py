"""
7_grafico_page.py — Grafico detallado de un activo con indicadores tecnicos.
"""
import os
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from plotly.subplots import make_subplots

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import db
from estilos import aplicar_estilos

if not st.session_state.get("usuario_autenticado"):
    st.warning("Debes iniciar sesion para acceder.")
    st.stop()

usuario = st.session_state["usuario_autenticado"]
db.init_mercado_db()
aplicar_estilos()

# ---------------------------------------------------------------------------
# Indicadores tecnicos
# ---------------------------------------------------------------------------

def calcular_rsi(serie: pd.Series, n: int = 14) -> pd.Series:
    delta    = serie.diff()
    ganancia = delta.clip(lower=0).rolling(n).mean()
    perdida  = (-delta.clip(upper=0)).rolling(n).mean()
    return 100 - (100 / (1 + ganancia / perdida))


def calcular_macd(serie: pd.Series):
    e12   = serie.ewm(span=12, adjust=False).mean()
    e26   = serie.ewm(span=26, adjust=False).mean()
    macd  = e12 - e26
    senal = macd.ewm(span=9, adjust=False).mean()
    return macd, senal


@st.cache_data(ttl=3600, show_spinner=False)
def descargar(simbolo: str, periodo: str) -> pd.DataFrame:
    df = yf.download(simbolo, period=periodo, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


# ---------------------------------------------------------------------------
# Buscador
# ---------------------------------------------------------------------------

st.title("Grafico")

c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
with c1:
    simbolo_input = st.text_input(
        "simbolo",
        value=st.session_state.get("mercado_simbolo", "AAPL"),
        placeholder="AAPL, TSLA, BTC-USD...",
        label_visibility="collapsed",
    ).upper().strip()
with c2:
    periodo = st.selectbox(
        "periodo",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=3,
        label_visibility="collapsed",
    )
with c3:
    indicador = st.selectbox(
        "indicador",
        ["SMA 20 / 50", "Bandas de Bollinger"],
        label_visibility="collapsed",
    )
with c4:
    if st.button("Analizar", use_container_width=True, type="primary"):
        st.session_state["mercado_simbolo"] = simbolo_input
        st.session_state["mercado_periodo"] = periodo
        st.rerun()

simbolo = st.session_state.get("mercado_simbolo", "AAPL")
periodo = st.session_state.get("mercado_periodo", "1y")

# ---------------------------------------------------------------------------
# Carga y calculo de indicadores
# ---------------------------------------------------------------------------

with st.spinner(f"Cargando {simbolo}..."):
    df = descargar(simbolo, periodo)

if df.empty:
    st.error(f"No se encontraron datos para '{simbolo}'. Verifica el simbolo.")
    st.stop()

db.registrar_busqueda(usuario["id"], simbolo)

df["sma20"]      = df["Close"].rolling(20).mean()
df["sma50"]      = df["Close"].rolling(50).mean()
df["bb_mid"]     = df["Close"].rolling(20).mean()
df["bb_up"]      = df["bb_mid"] + 2 * df["Close"].rolling(20).std()
df["bb_down"]    = df["bb_mid"] - 2 * df["Close"].rolling(20).std()
df["rsi"]        = calcular_rsi(df["Close"])
df["macd"], df["macd_senal"] = calcular_macd(df["Close"])
df["histograma"] = df["macd"] - df["macd_senal"]

# ---------------------------------------------------------------------------
# Metricas
# ---------------------------------------------------------------------------

precio_act  = float(df["Close"].iloc[-1])
precio_ant  = float(df["Close"].iloc[-2])
cambio      = precio_act - precio_ant
cambio_pct  = cambio / precio_ant * 100
signo       = "+" if cambio >= 0 else ""
rsi_actual  = df["rsi"].dropna().iloc[-1] if not df["rsi"].dropna().empty else 0.0

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Precio",        f"${precio_act:,.2f}")
c2.metric("Cambio (1d)",   f"{signo}{cambio_pct:.2f}%", delta=f"{signo}{cambio:.2f}")
c3.metric("Maximo",        f"${float(df['High'].max()):,.2f}")
c4.metric("Minimo",        f"${float(df['Low'].min()):,.2f}")
c5.metric("RSI (14)",      f"{float(rsi_actual):.1f}")
c6.metric("Vol. promedio", f"{float(df['Volume'].mean()):,.0f}")

# ---------------------------------------------------------------------------
# Grafico
# ---------------------------------------------------------------------------

fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    row_heights=[0.58, 0.21, 0.21],
    vertical_spacing=0.03,
    subplot_titles=(simbolo, "RSI (14)", "MACD"),
)

# Velas japonesas
fig.add_trace(
    go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"],   close=df["Close"],
        name=simbolo,
        increasing_line_color="#26a69a",
        decreasing_line_color="#ef5350",
    ),
    row=1, col=1,
)

# SMA o Bollinger
if indicador == "SMA 20 / 50":
    fig.add_trace(go.Scatter(x=df.index, y=df["sma20"], name="SMA 20",
                             line=dict(color="#ffa726", width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["sma50"], name="SMA 50",
                             line=dict(color="#42a5f5", width=1.5)), row=1, col=1)
else:
    fig.add_trace(go.Scatter(x=df.index, y=df["bb_up"], name="BB Superior",
                             line=dict(color="#9575cd", width=1, dash="dot")), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["bb_mid"], name="BB Media",
                             line=dict(color="#9575cd", width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["bb_down"], name="BB Inferior",
                             line=dict(color="#9575cd", width=1, dash="dot"),
                             fill="tonexty", fillcolor="rgba(149,117,205,0.05)"), row=1, col=1)

# RSI
fig.add_trace(go.Scatter(x=df.index, y=df["rsi"], name="RSI",
                         line=dict(color="#ab47bc", width=1.5)), row=2, col=1)
fig.add_hrect(y0=70, y1=100, row=2, col=1, fillcolor="red",   opacity=0.07, line_width=0)
fig.add_hrect(y0=0,  y1=30,  row=2, col=1, fillcolor="green", opacity=0.07, line_width=0)
fig.add_hline(y=70, row=2, col=1, line=dict(color="red",   width=1, dash="dash"))
fig.add_hline(y=30, row=2, col=1, line=dict(color="green", width=1, dash="dash"))

# MACD
fig.add_trace(go.Scatter(x=df.index, y=df["macd"],       name="MACD",
                         line=dict(color="#26a69a", width=1.5)), row=3, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["macd_senal"], name="Senal",
                         line=dict(color="#ef5350",  width=1.5)), row=3, col=1)
hist_colors = ["#26a69a" if v >= 0 else "#ef5350" for v in df["histograma"].fillna(0)]
fig.add_trace(go.Bar(x=df.index, y=df["histograma"], name="Histograma",
                     marker_color=hist_colors, opacity=0.7), row=3, col=1)

fig.update_layout(
    height=640,
    xaxis_rangeslider_visible=False,
    template="plotly_dark",
    paper_bgcolor="#131722",
    plot_bgcolor="#131722",
    legend=dict(orientation="h", yanchor="bottom", y=1.02,
                xanchor="right", x=1, font=dict(size=11)),
    margin=dict(l=0, r=0, t=36, b=0),
)
for i in range(1, 4):
    fig.update_xaxes(gridcolor="#1e222d", row=i, col=1)
    fig.update_yaxes(gridcolor="#1e222d", row=i, col=1)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Busquedas recientes
# ---------------------------------------------------------------------------

recientes = db.obtener_busquedas_recientes(usuario["id"], limite=8)
if recientes:
    st.markdown('<div class="sec-h">Busquedas recientes</div>', unsafe_allow_html=True)
    cols = st.columns(min(len(recientes), 8))
    for i, b in enumerate(recientes):
        if cols[i].button(b["simbolo"], key=f"rec_{i}"):
            st.session_state["mercado_simbolo"] = b["simbolo"]
            st.rerun()
