"""
7_grafico_page.py — Analisis detallado de un activo.
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
# Catalogos
# ---------------------------------------------------------------------------

SIMBOLOS = {
    "Acciones US":        ["AAPL","MSFT","NVDA","AMZN","GOOGL","TSLA","META","JPM","V","WMT","XOM","JNJ","BRK-B","UNH","MA"],
    "Criptomonedas":      ["BTC-USD","ETH-USD","BNB-USD","SOL-USD","XRP-USD","ADA-USD","DOGE-USD","AVAX-USD"],
    "Europa":             ["SAN.MC","TEF.MC","BBVA.MC","IBE.MC","REP.MC","ITX.MC","MC.PA","SAP.DE","ASML.AS","SHEL","BP"],
    "Indices":            ["^GSPC","^IXIC","^DJI","^DAX","^FTSE","^N225","GC=F","SI=F","CL=F"],
}

TODOS = [s for lista in SIMBOLOS.values() for s in lista]

# ---------------------------------------------------------------------------
# Indicadores
# ---------------------------------------------------------------------------

def calcular_rsi(serie: pd.Series, n: int = 14) -> pd.Series:
    d = serie.diff()
    g = d.clip(lower=0).rolling(n).mean()
    p = (-d.clip(upper=0)).rolling(n).mean()
    return 100 - (100 / (1 + g / p))


def calcular_macd(serie: pd.Series):
    e12  = serie.ewm(span=12, adjust=False).mean()
    e26  = serie.ewm(span=26, adjust=False).mean()
    macd = e12 - e26
    return macd, macd.ewm(span=9, adjust=False).mean()


@st.cache_data(ttl=3600, show_spinner=False)
def descargar(simbolo: str, periodo: str) -> pd.DataFrame:
    df = yf.download(simbolo, period=periodo, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def obtener_info(simbolo: str) -> dict:
    try:
        return yf.Ticker(simbolo).info
    except Exception:
        return {}

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

try:
    st.html('<style>.block-container{padding-top:1.2rem!important}</style>')
except AttributeError:
    pass

st.markdown('<h1 class="page-title">Analisis</h1>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Selector de simbolo
# ---------------------------------------------------------------------------

c1, c2, c3, c4 = st.columns([2, 1, 1, 1])

with c1:
    categoria = st.selectbox("Categoria", list(SIMBOLOS.keys()), label_visibility="collapsed")
    opciones  = ["Escribir simbolo..."] + SIMBOLOS[categoria]
    sel       = st.selectbox("Simbolo", opciones, label_visibility="collapsed",
                              key="sel_sym",
                              index=(opciones.index(st.session_state.get("mercado_simbolo","AAPL"))
                                     if st.session_state.get("mercado_simbolo","AAPL") in opciones else 0))

    if sel == "Escribir simbolo...":
        simbolo_input = st.text_input("Simbolo personalizado",
                                       value=st.session_state.get("mercado_simbolo","AAPL"),
                                       label_visibility="collapsed",
                                       placeholder="Ej: NFLX, BABA, 005930.KS...").upper().strip()
    else:
        simbolo_input = sel

with c2:
    periodo = st.selectbox("Periodo", ["1mo","3mo","6mo","1y","2y","5y"],
                            index=3, label_visibility="collapsed")
with c3:
    indicador = st.selectbox("Indicador", ["SMA 20/50","Bandas de Bollinger"],
                              label_visibility="collapsed")
with c4:
    if st.button("Analizar", use_container_width=True, type="primary"):
        st.session_state["mercado_simbolo"] = simbolo_input
        st.session_state["mercado_periodo"] = periodo
        st.rerun()

simbolo = st.session_state.get("mercado_simbolo", "AAPL")
periodo = st.session_state.get("mercado_periodo", "1y")

# ---------------------------------------------------------------------------
# Datos
# ---------------------------------------------------------------------------

with st.spinner(f"Cargando {simbolo}..."):
    df = descargar(simbolo, periodo)

if df.empty:
    st.error(f"No se encontraron datos para '{simbolo}'.")
    st.stop()

db.registrar_busqueda(usuario["id"], simbolo)

# Indicadores
df["sma20"]      = df["Close"].rolling(20).mean()
df["sma50"]      = df["Close"].rolling(50).mean()
df["ema12"]      = df["Close"].ewm(span=12, adjust=False).mean()
df["bb_mid"]     = df["Close"].rolling(20).mean()
df["bb_up"]      = df["bb_mid"] + 2 * df["Close"].rolling(20).std()
df["bb_down"]    = df["bb_mid"] - 2 * df["Close"].rolling(20).std()
df["rsi"]        = calcular_rsi(df["Close"])
df["macd"], df["macd_senal"] = calcular_macd(df["Close"])
df["histograma"] = df["macd"] - df["macd_senal"]
df["vol_sma20"]  = df["Volume"].rolling(20).mean()

# Metricas clave
precio_act   = float(df["Close"].iloc[-1])
precio_ant   = float(df["Close"].iloc[-2])
cambio       = precio_act - precio_ant
cambio_pct   = cambio / precio_ant * 100
signo        = "+" if cambio >= 0 else ""
rsi_val      = float(df["rsi"].dropna().iloc[-1]) if not df["rsi"].dropna().empty else 0.0
max_52       = float(df["Close"].tail(252).max())
min_52       = float(df["Close"].tail(252).min())
vol_hoy      = float(df["Volume"].iloc[-1])
vol_prom     = float(df["Volume"].mean())
vol_ratio    = vol_hoy / vol_prom if vol_prom > 0 else 1.0
macd_val     = float(df["macd"].dropna().iloc[-1]) if not df["macd"].dropna().empty else 0.0
bb_pos       = 0.0
if not df[["bb_up","bb_down"]].dropna().empty:
    bu = float(df["bb_up"].dropna().iloc[-1])
    bd = float(df["bb_down"].dropna().iloc[-1])
    bb_pos = (precio_act - bd) / (bu - bd) * 100 if (bu - bd) > 0 else 50.0

# ---------------------------------------------------------------------------
# Metricas — fila 1
# ---------------------------------------------------------------------------

st.write("")
c1,c2,c3,c4,c5,c6 = st.columns(6)
c1.metric("Precio actual",    f"${precio_act:,.2f}")
c2.metric("Cambio (1d)",      f"{signo}{cambio_pct:.2f}%", delta=f"{signo}{cambio:.2f}")
c3.metric("Maximo 52 sem.",   f"${max_52:,.2f}")
c4.metric("Minimo 52 sem.",   f"${min_52:,.2f}")
c5.metric("RSI (14)",         f"{rsi_val:.1f}")
c6.metric("MACD",             f"{macd_val:.3f}")

# Fila 2
c7,c8,c9,c10,c11,c12 = st.columns(6)
c7.metric("Volumen hoy",      f"{vol_hoy:,.0f}")
c8.metric("Vol. promedio",    f"{vol_prom:,.0f}")
c9.metric("Ratio volumen",    f"{vol_ratio:.2f}x",
           help="Volumen de hoy vs promedio 20 dias. >1 = mayor actividad")
c10.metric("Rango BB (%)",    f"{bb_pos:.1f}%",
            help="Posicion del precio dentro de las Bandas de Bollinger. >80=sobrecompra, <20=sobreventa")
c11.metric("SMA 20",          f"${float(df['sma20'].dropna().iloc[-1]):,.2f}" if not df["sma20"].dropna().empty else "N/A")
c12.metric("SMA 50",          f"${float(df['sma50'].dropna().iloc[-1]):,.2f}" if not df["sma50"].dropna().empty else "N/A")

st.divider()

# ---------------------------------------------------------------------------
# Grafico principal
# ---------------------------------------------------------------------------

fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    row_heights=[0.57, 0.22, 0.21],
    vertical_spacing=0.025,
    subplot_titles=(f"{simbolo} — Precio", "RSI (14)", "MACD"),
)

# Velas
fig.add_trace(go.Candlestick(
    x=df.index, open=df["Open"], high=df["High"],
    low=df["Low"], close=df["Close"], name=simbolo,
    increasing_line_color="#26a69a", decreasing_line_color="#ef5350",
), row=1, col=1)

# Indicador seleccionado
if indicador == "SMA 20/50":
    fig.add_trace(go.Scatter(x=df.index, y=df["sma20"], name="SMA 20",
                             line=dict(color="#ffa726", width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["sma50"], name="SMA 50",
                             line=dict(color="#42a5f5", width=1.5)), row=1, col=1)
else:
    fig.add_trace(go.Scatter(x=df.index, y=df["bb_up"],   name="BB Superior",
                             line=dict(color="#9575cd", width=1, dash="dot")), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["bb_mid"],  name="BB Media",
                             line=dict(color="#9575cd", width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["bb_down"], name="BB Inferior",
                             line=dict(color="#9575cd", width=1, dash="dot"),
                             fill="tonexty", fillcolor="rgba(149,117,205,0.05)"), row=1, col=1)

# RSI
fig.add_trace(go.Scatter(x=df.index, y=df["rsi"], name="RSI",
                         line=dict(color="#ab47bc", width=1.5)), row=2, col=1)
fig.add_hrect(y0=70, y1=100, row=2, col=1, fillcolor="red",   opacity=0.07, line_width=0)
fig.add_hrect(y0=0,  y1=30,  row=2, col=1, fillcolor="green", opacity=0.07, line_width=0)
fig.add_hline(y=70,  row=2, col=1, line=dict(color="red",   width=1, dash="dash"))
fig.add_hline(y=30,  row=2, col=1, line=dict(color="green", width=1, dash="dash"))

# MACD
fig.add_trace(go.Scatter(x=df.index, y=df["macd"],       name="MACD",
                         line=dict(color="#26a69a", width=1.5)), row=3, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["macd_senal"], name="Senal",
                         line=dict(color="#ef5350",  width=1.5)), row=3, col=1)
hist_colors = ["#26a69a" if v >= 0 else "#ef5350" for v in df["histograma"].fillna(0)]
fig.add_trace(go.Bar(x=df.index, y=df["histograma"], name="Histograma",
                     marker_color=hist_colors, opacity=0.65), row=3, col=1)

fig.update_layout(
    height=660, xaxis_rangeslider_visible=False,
    template="plotly_dark", paper_bgcolor="#131722", plot_bgcolor="#131722",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
    margin=dict(l=0, r=0, t=36, b=0),
)
for i in range(1, 4):
    fig.update_xaxes(gridcolor="#1e222d", row=i, col=1)
    fig.update_yaxes(gridcolor="#1e222d", row=i, col=1)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# Interpretacion de indicadores
# ---------------------------------------------------------------------------

st.divider()
st.markdown("**Interpretacion de indicadores**")

col_rsi, col_macd, col_bb = st.columns(3)

with col_rsi:
    if rsi_val > 70:
        nivel, color, desc = "Sobrecompra", "#ef5350", "El activo podria estar sobrevaluado. Posible correccion."
    elif rsi_val < 30:
        nivel, color, desc = "Sobreventa", "#26a69a", "El activo podria estar subvaluado. Posible rebote."
    elif rsi_val > 50:
        nivel, color, desc = "Zona alcista", "#26a69a", "Momentum positivo. Tendencia favorable."
    else:
        nivel, color, desc = "Zona bajista", "#ef5350", "Momentum negativo. Tendencia desfavorable."
    st.markdown(f"""
    <div style="background:#1e222d;border:1px solid #2a2e39;border-radius:8px;padding:14px">
        <div style="font-size:0.68rem;color:#787b86;text-transform:uppercase;letter-spacing:1px;">RSI</div>
        <div style="font-size:1.1rem;font-weight:700;color:{color};margin:4px 0">{nivel} · {rsi_val:.1f}</div>
        <div style="font-size:0.78rem;color:#787b86">{desc}</div>
    </div>""", unsafe_allow_html=True)

with col_macd:
    if macd_val > 0:
        nivel, color, desc = "Positivo", "#26a69a", "MACD por encima de cero. Tendencia alcista en curso."
    else:
        nivel, color, desc = "Negativo", "#ef5350", "MACD por debajo de cero. Tendencia bajista en curso."
    st.markdown(f"""
    <div style="background:#1e222d;border:1px solid #2a2e39;border-radius:8px;padding:14px">
        <div style="font-size:0.68rem;color:#787b86;text-transform:uppercase;letter-spacing:1px;">MACD</div>
        <div style="font-size:1.1rem;font-weight:700;color:{color};margin:4px 0">{nivel} · {macd_val:.3f}</div>
        <div style="font-size:0.78rem;color:#787b86">{desc}</div>
    </div>""", unsafe_allow_html=True)

with col_bb:
    if bb_pos > 80:
        nivel, color, desc = "Banda superior", "#ef5350", "Precio cerca del limite superior. Posible sobrecompra."
    elif bb_pos < 20:
        nivel, color, desc = "Banda inferior", "#26a69a", "Precio cerca del limite inferior. Posible sobreventa."
    else:
        nivel, color, desc = "Zona media", "#ffa726", "Precio dentro del rango normal de las bandas."
    st.markdown(f"""
    <div style="background:#1e222d;border:1px solid #2a2e39;border-radius:8px;padding:14px">
        <div style="font-size:0.68rem;color:#787b86;text-transform:uppercase;letter-spacing:1px;">Bollinger</div>
        <div style="font-size:1.1rem;font-weight:700;color:{color};margin:4px 0">{nivel} · {bb_pos:.0f}%</div>
        <div style="font-size:0.78rem;color:#787b86">{desc}</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------------------------
# Busquedas recientes
# ---------------------------------------------------------------------------

recientes = db.obtener_busquedas_recientes(usuario["id"], limite=8)
if recientes:
    st.markdown('<div class="sec-h">Recientes</div>', unsafe_allow_html=True)
    cols = st.columns(min(len(recientes), 8))
    for i, b in enumerate(recientes):
        if cols[i].button(b["simbolo"], key=f"rec_{i}"):
            st.session_state["mercado_simbolo"] = b["simbolo"]
            st.rerun()
