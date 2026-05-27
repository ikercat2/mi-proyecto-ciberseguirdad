"""
8_modelo_page.py — Modelo ML de prediccion de tendencia.
"""
import os
import sys

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from plotly.subplots import make_subplots
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from estilos import aplicar_estilos

if not st.session_state.get("usuario_autenticado"):
    st.warning("Debes iniciar sesion para acceder.")
    st.stop()

aplicar_estilos()

# ---------------------------------------------------------------------------
# Logica ML
# ---------------------------------------------------------------------------

FEATURES = ["sma_ratio20","sma_ratio50","rsi14","macd","vol_ratio","ret_1d","ret_5d","ret_20d"]
NOMBRES_F = ["Precio/SMA20","Precio/SMA50","RSI 14","MACD","Volumen ratio","Retorno 1d","Retorno 5d","Retorno 20d"]

SIMBOLOS_RAPIDOS = ["AAPL","MSFT","NVDA","TSLA","BTC-USD","ETH-USD","AMZN","GOOGL","META","JPM","SOL-USD","BBVA.MC"]


def _rsi(s, n=14):
    d = s.diff();  g = d.clip(lower=0).rolling(n).mean();  p = (-d.clip(upper=0)).rolling(n).mean()
    return 100 - (100 / (1 + g / p))


def _preparar(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["sma20"]       = d["Close"].rolling(20).mean()
    d["sma50"]       = d["Close"].rolling(50).mean()
    d["sma_ratio20"] = d["Close"] / d["sma20"]
    d["sma_ratio50"] = d["Close"] / d["sma50"]
    d["rsi14"]       = _rsi(d["Close"])
    e12 = d["Close"].ewm(span=12, adjust=False).mean()
    e26 = d["Close"].ewm(span=26, adjust=False).mean()
    d["macd"]        = e12 - e26
    d["vol_ratio"]   = d["Volume"] / d["Volume"].rolling(20).mean()
    d["ret_1d"]      = d["Close"].pct_change(1)
    d["ret_5d"]      = d["Close"].pct_change(5)
    d["ret_20d"]     = d["Close"].pct_change(20)
    return d


@st.cache_resource(ttl=3600, show_spinner=False)
def entrenar(simbolo: str):
    df = yf.download(simbolo, period="5y", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = _preparar(df)
    df["objetivo"] = (df["Close"].shift(-1) > df["Close"]).astype(int)
    df = df.dropna()
    if len(df) < 100:
        raise ValueError("Datos insuficientes.")

    X, y  = df[FEATURES].values, df["objetivo"].values
    corte = int(len(X) * 0.8)

    sc    = StandardScaler()
    Xtr   = sc.fit_transform(X[:corte]);  Xte = sc.transform(X[corte:])
    ytr   = y[:corte];                    yte = y[corte:]

    m = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    m.fit(Xtr, ytr)

    y_pred   = m.predict(Xte)
    acc      = float(m.score(Xte, yte))
    cm       = confusion_matrix(yte, y_pred)

    # Retornos simulados (test set)
    closes_test = df["Close"].iloc[corte:].values
    senal       = (y_pred == 1).astype(float)
    ret_diario  = pd.Series(closes_test).pct_change().fillna(0).values
    strat_ret   = (senal[:-1] * ret_diario[1:])
    hold_ret    = ret_diario[1:]
    retornos_df = pd.DataFrame({
        "Modelo": (1 + strat_ret).cumprod(),
        "Buy & Hold": (1 + hold_ret).cumprod(),
    }, index=df.index[corte + 1:])

    ultimo = df[FEATURES].dropna().iloc[-1:].values
    return m, sc, acc, cm, retornos_df, ultimo


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

st.markdown(
    "<h1 style='font-size:2rem;font-weight:800;color:#d1d4dc;letter-spacing:-1px'>Modelo de Prediccion IA</h1>",
    unsafe_allow_html=True,
)
st.caption("Random Forest entrenado con 5 anos de datos historicos — predice la direccion del siguiente cierre.")

opciones_sym = ["Escribir simbolo..."] + SIMBOLOS_RAPIDOS
c1, c2 = st.columns([3, 1])
with c1:
    sel = st.selectbox("Simbolo rapido", opciones_sym, label_visibility="collapsed",
                        index=(opciones_sym.index(st.session_state.get("mercado_simbolo","AAPL"))
                               if st.session_state.get("mercado_simbolo","AAPL") in opciones_sym else 0))
    if sel == "Escribir simbolo...":
        simbolo = st.text_input("Simbolo personalizado",
                                 value=st.session_state.get("mercado_simbolo","AAPL"),
                                 label_visibility="collapsed",
                                 placeholder="TSLA, NFLX, BNB-USD...").upper().strip()
    else:
        simbolo = sel
with c2:
    ejecutar = st.button("Ejecutar modelo", use_container_width=True, type="primary")

if not ejecutar:
    st.info("Selecciona un simbolo y presiona Ejecutar.")
    st.stop()

# ---------------------------------------------------------------------------
# Entrenamiento
# ---------------------------------------------------------------------------

with st.spinner(f"Entrenando con 5 anos de {simbolo}..."):
    try:
        modelo, scaler, accuracy, cm, retornos_df, ultimo = entrenar(simbolo)
    except Exception as exc:
        st.error(f"Error: {exc}")
        st.stop()

ultimo_sc  = scaler.transform(ultimo)
pred       = int(modelo.predict(ultimo_sc)[0])
proba      = modelo.predict_proba(ultimo_sc)[0]
confianza  = float(proba[pred]) * 100
tendencia  = "ALCISTA" if pred == 1 else "BAJISTA"
color      = "#26a69a" if pred == 1 else "#ef5350"

st.divider()

# ── Fila principal ────────────────────────────────────────────────────────────

col_gauge, col_pred, col_metricas = st.columns([1.2, 1, 1.2])

# Gauge
with col_gauge:
    fig_g = go.Figure(go.Indicator(
        mode  = "gauge+number+delta",
        value = confianza,
        delta = {"reference": 50, "valueformat": ".1f",
                 "increasing": {"color": "#26a69a"}, "decreasing": {"color": "#ef5350"}},
        gauge = {
            "axis":  {"range": [0, 100], "tickwidth": 1, "tickcolor": "#787b86",
                      "tickvals": [0,25,50,75,100]},
            "bar":   {"color": color, "thickness": 0.25},
            "bgcolor": "#1e222d",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  40], "color": "rgba(239,83,80,0.12)"},
                {"range": [40, 60], "color": "rgba(255,167,38,0.08)"},
                {"range": [60,100], "color": "rgba(38,166,154,0.12)"},
            ],
            "threshold": {"line": {"color": color, "width": 3}, "thickness": 0.85, "value": confianza},
        },
        title = {"text": "Confianza del modelo", "font": {"size": 13, "color": "#787b86"}},
        number = {"suffix": "%", "font": {"size": 28, "color": color}},
    ))
    fig_g.update_layout(
        height=220, margin=dict(l=20, r=20, t=30, b=10),
        paper_bgcolor="#131722", font_color="#d1d4dc",
    )
    st.plotly_chart(fig_g, use_container_width=True)

# Prediccion
with col_pred:
    st.markdown(f"""
    <div style="background:#1e222d;border:2px solid {color};border-radius:12px;
                padding:28px 16px;text-align:center;height:180px;
                display:flex;flex-direction:column;justify-content:center;">
        <div style="font-size:0.65rem;color:#787b86;letter-spacing:2px;
                    text-transform:uppercase;margin-bottom:10px;">Siguiente sesion</div>
        <div style="font-size:2.2rem;font-weight:800;color:{color};letter-spacing:3px;">{tendencia}</div>
        <div style="color:#787b86;font-size:0.8rem;margin-top:8px;">
            P(sube): <strong style="color:#26a69a;">{proba[1]*100:.1f}%</strong> &nbsp;
            P(baja): <strong style="color:#ef5350;">{proba[0]*100:.1f}%</strong>
        </div>
    </div>""", unsafe_allow_html=True)

# Metricas
with col_metricas:
    strat_final = float(retornos_df["Modelo"].iloc[-1])
    hold_final  = float(retornos_df["Buy & Hold"].iloc[-1])
    outperf     = (strat_final - hold_final) * 100

    st.metric("Precision (test 20%)", f"{accuracy*100:.1f}%",
               help="Porcentaje de dias correctamente clasificados en datos no vistos.")
    st.metric("Retorno modelo (acum.)",    f"{(strat_final-1)*100:+.1f}%")
    st.metric("Retorno buy & hold (acum.)",f"{(hold_final-1)*100:+.1f}%")
    st.metric("Diferencia vs B&H",         f"{outperf:+.1f}%",
               delta=f"{outperf:+.1f}%")

st.divider()

# ── Fila de graficos ──────────────────────────────────────────────────────────

col_ret, col_imp = st.columns([1.6, 1])

with col_ret:
    st.markdown("**Retornos acumulados — Modelo vs Buy & Hold (conjunto de prueba)**")
    fig_r = go.Figure()
    fig_r.add_trace(go.Scatter(
        x=retornos_df.index, y=retornos_df["Modelo"],
        name="Modelo RF", line=dict(color="#2962ff", width=2),
        fill="tozeroy", fillcolor="rgba(41,98,255,0.06)",
    ))
    fig_r.add_trace(go.Scatter(
        x=retornos_df.index, y=retornos_df["Buy & Hold"],
        name="Buy & Hold", line=dict(color="#787b86", width=1.5, dash="dot"),
    ))
    fig_r.update_layout(
        height=280, template="plotly_dark",
        paper_bgcolor="#131722", plot_bgcolor="#131722",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(gridcolor="#1e222d"),
        yaxis=dict(gridcolor="#1e222d", tickformat=".2f"),
    )
    st.plotly_chart(fig_r, use_container_width=True)

with col_imp:
    st.markdown("**Importancia de variables**")
    idx  = np.argsort(modelo.feature_importances_)
    fig_i = go.Figure(go.Bar(
        x=modelo.feature_importances_[idx],
        y=[NOMBRES_F[i] for i in idx],
        orientation="h",
        marker=dict(
            color=modelo.feature_importances_[idx],
            colorscale=[[0,"#1e222d"],[0.5,"#2962ff"],[1,"#26a69a"]],
            showscale=False,
        ),
    ))
    fig_i.update_layout(
        height=280, template="plotly_dark",
        paper_bgcolor="#131722", plot_bgcolor="#131722",
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(gridcolor="#1e222d", title="Importancia"),
        yaxis=dict(gridcolor="#1e222d"),
    )
    st.plotly_chart(fig_i, use_container_width=True)

# ── Matriz de confusion ───────────────────────────────────────────────────────

st.divider()
col_cm, col_info = st.columns([1, 2])

with col_cm:
    st.markdown("**Matriz de confusion (conjunto de prueba)**")
    tn, fp, fn, tp = cm.ravel() if cm.shape == (2,2) else (0,0,0,0)
    fig_cm = go.Figure(go.Heatmap(
        z=[[tp, fp],[fn, tn]],
        x=["Pred: Sube","Pred: Baja"],
        y=["Real: Sube","Real: Baja"],
        colorscale=[[0,"#1e222d"],[1,"#2962ff"]],
        showscale=False,
        text=[[tp, fp],[fn, tn]],
        texttemplate="%{text}",
        textfont=dict(size=18, color="#d1d4dc"),
    ))
    fig_cm.update_layout(
        height=220, template="plotly_dark",
        paper_bgcolor="#131722", plot_bgcolor="#131722",
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig_cm, use_container_width=True)

with col_info:
    st.markdown("**Como interpretar los resultados**")
    precision_alcista = tp / (tp + fp) * 100 if (tp + fp) > 0 else 0
    precision_bajista = tn / (tn + fn) * 100 if (tn + fn) > 0 else 0
    st.write(f"""
    - **Precision dias alcistas:** {precision_alcista:.1f}% — de cada 100 dias que el modelo predice subida, acierta en {precision_alcista:.0f}.
    - **Precision dias bajistas:** {precision_bajista:.1f}% — de cada 100 dias que predice caida, acierta en {precision_bajista:.0f}.
    - **Precision general:** {accuracy*100:.1f}% — porcentaje total de dias correctamente clasificados.
    - El modelo fue entrenado con el **80% de los datos** (4 anos) y evaluado en el **20% mas reciente** (1 ano).
    """)
    st.caption("Predicciones orientativas. No constituyen asesoramiento financiero.")
