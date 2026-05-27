"""
8_modelo_page.py — Modelo ML de prediccion de tendencia (Random Forest).
"""
import os
import sys

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from estilos import aplicar_estilos

if not st.session_state.get("usuario_autenticado"):
    st.warning("Debes iniciar sesion para acceder.")
    st.stop()

aplicar_estilos()

# ---------------------------------------------------------------------------
# Logica del modelo
# ---------------------------------------------------------------------------

FEATURES = [
    "sma_ratio20", "sma_ratio50", "rsi14",
    "macd", "vol_ratio", "ret_1d", "ret_5d", "ret_20d",
]

NOMBRES_FEATURES = [
    "Precio / SMA 20", "Precio / SMA 50", "RSI (14)",
    "MACD", "Volumen (ratio)", "Retorno 1d",
    "Retorno 5d", "Retorno 20d",
]


def _calcular_rsi(serie: pd.Series, n: int = 14) -> pd.Series:
    delta    = serie.diff()
    ganancia = delta.clip(lower=0).rolling(n).mean()
    perdida  = (-delta.clip(upper=0)).rolling(n).mean()
    return 100 - (100 / (1 + ganancia / perdida))


def _preparar_features(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["sma20"]       = d["Close"].rolling(20).mean()
    d["sma50"]       = d["Close"].rolling(50).mean()
    d["sma_ratio20"] = d["Close"] / d["sma20"]
    d["sma_ratio50"] = d["Close"] / d["sma50"]
    d["rsi14"]       = _calcular_rsi(d["Close"])
    e12              = d["Close"].ewm(span=12, adjust=False).mean()
    e26              = d["Close"].ewm(span=26, adjust=False).mean()
    d["macd"]        = e12 - e26
    d["vol_ratio"]   = d["Volume"] / d["Volume"].rolling(20).mean()
    d["ret_1d"]      = d["Close"].pct_change(1)
    d["ret_5d"]      = d["Close"].pct_change(5)
    d["ret_20d"]     = d["Close"].pct_change(20)
    return d


@st.cache_resource(ttl=3600, show_spinner=False)
def entrenar_modelo(simbolo: str):
    df = yf.download(simbolo, period="5y", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = _preparar_features(df)
    df["objetivo"] = (df["Close"].shift(-1) > df["Close"]).astype(int)
    df = df.dropna()

    if len(df) < 100:
        raise ValueError("Datos insuficientes para entrenar el modelo.")

    X = df[FEATURES].values
    y = df["objetivo"].values

    corte   = int(len(X) * 0.8)
    scaler  = StandardScaler()
    X_train = scaler.fit_transform(X[:corte])
    X_test  = scaler.transform(X[corte:])

    modelo = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    modelo.fit(X_train, y[:corte])
    accuracy = float(modelo.score(X_test, y[corte:]))

    ultimo = df[FEATURES].dropna().iloc[-1:].values
    return modelo, scaler, accuracy, ultimo


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

st.title("Modelo de Prediccion")
st.caption(
    "Clasificador Random Forest entrenado con 5 anos de datos historicos. "
    "Predice si el precio de cierre del siguiente dia sera mayor o menor al actual."
)

simbolo_def = st.session_state.get("mercado_simbolo", "AAPL")
c1, c2 = st.columns([3, 1])
with c1:
    simbolo = st.text_input(
        "Simbolo", value=simbolo_def,
        placeholder="AAPL, TSLA, BTC-USD...",
    ).upper().strip()
with c2:
    ejecutar = st.button("Ejecutar", use_container_width=True, type="primary")

if not ejecutar:
    st.info("Ingresa un simbolo y presiona Ejecutar para generar la prediccion.")
    st.stop()

if not simbolo:
    st.warning("Ingresa un simbolo valido.")
    st.stop()

# ---------------------------------------------------------------------------
# Entrenamiento y prediccion
# ---------------------------------------------------------------------------

with st.spinner(f"Entrenando modelo para {simbolo} con 5 anos de datos..."):
    try:
        modelo, scaler, accuracy, ultimo = entrenar_modelo(simbolo)
    except Exception as exc:
        st.error(f"Error al entrenar el modelo: {exc}")
        st.stop()

ultimo_sc = scaler.transform(ultimo)
pred      = int(modelo.predict(ultimo_sc)[0])
proba     = modelo.predict_proba(ultimo_sc)[0]
confianza = float(proba[pred]) * 100
tendencia = "ALCISTA" if pred == 1 else "BAJISTA"
color     = "#26a69a" if pred == 1 else "#ef5350"

st.divider()

# ── Resultado principal ───────────────────────────────────────────────────────

col_pred, col_metricas, col_importancia = st.columns([1, 1, 2])

with col_pred:
    st.markdown(
        f"""
        <div style="background:#1e222d; border:2px solid {color};
                    border-radius:10px; padding:28px 16px; text-align:center;">
            <div style="font-size:0.7rem; color:#787b86; letter-spacing:1.5px;
                        text-transform:uppercase; margin-bottom:10px;">
                Prediccion siguiente sesion
            </div>
            <div style="font-size:2rem; font-weight:700; color:{color};
                        letter-spacing:3px;">{tendencia}</div>
            <div style="color:#9598a1; font-size:0.85rem; margin-top:8px;">
                Confianza: <strong style="color:{color};">{confianza:.1f}%</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_metricas:
    st.metric(
        "Precision del modelo", f"{accuracy * 100:.1f}%",
        help="Calculada sobre el 20% de datos mas recientes no usados en entrenamiento.",
    )
    st.metric("Probabilidad alcista", f"{proba[1] * 100:.1f}%")
    st.metric("Probabilidad bajista", f"{proba[0] * 100:.1f}%")

with col_importancia:
    importancias = modelo.feature_importances_
    idx_ord = np.argsort(importancias)
    fig = go.Figure(go.Bar(
        x=importancias[idx_ord],
        y=[NOMBRES_FEATURES[i] for i in idx_ord],
        orientation="h",
        marker_color="#42a5f5",
    ))
    fig.update_layout(
        title="Importancia de variables",
        height=300,
        template="plotly_dark",
        paper_bgcolor="#131722",
        plot_bgcolor="#131722",
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis=dict(gridcolor="#1e222d", title="Importancia relativa"),
        yaxis=dict(gridcolor="#1e222d"),
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption(
    "Las predicciones son orientativas. No constituyen asesoramiento financiero. "
    "Rendimientos pasados no garantizan resultados futuros."
)
