import os
import sys
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from estilos import aplicar_estilos

aplicar_estilos()

# ---------------------------------------------------------------------------
# CSS especifico de la landing
# ---------------------------------------------------------------------------

try:
    st.html("""
    <style>
      .block-container { padding-top: 0 !important; max-width: 100% !important; }

      .hero {
        background: linear-gradient(135deg, #0f1117 0%, #131722 50%, #0d1426 100%);
        padding: 80px 60px 70px;
        text-align: center;
        border-bottom: 1px solid #1e222d;
        position: relative;
        overflow: hidden;
      }
      .hero::before {
        content: '';
        position: absolute;
        top: -40%;
        left: 50%;
        transform: translateX(-50%);
        width: 700px;
        height: 700px;
        background: radial-gradient(circle, rgba(41,98,255,0.08) 0%, transparent 70%);
        pointer-events: none;
      }
      .hero-tag {
        display: inline-block;
        background: rgba(41,98,255,0.12);
        color: #2962ff;
        border: 1px solid rgba(41,98,255,0.25);
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 24px;
      }
      .hero-title {
        font-size: 3.2rem !important;
        font-weight: 800 !important;
        line-height: 1.15 !important;
        color: #d1d4dc !important;
        letter-spacing: -1.5px !important;
        margin: 0 0 20px !important;
      }
      .hero-title span { color: #2962ff; }
      .hero-sub {
        font-size: 1.1rem !important;
        color: #787b86 !important;
        max-width: 540px;
        margin: 0 auto 36px !important;
        line-height: 1.7 !important;
        font-weight: 400 !important;
      }

      .stats-bar {
        display: flex;
        justify-content: center;
        gap: 48px;
        padding: 28px 0;
        border-bottom: 1px solid #1e222d;
        background: #0f1117;
      }
      .stat-item { text-align: center; }
      .stat-num {
        font-size: 1.6rem;
        font-weight: 700;
        color: #d1d4dc;
        display: block;
      }
      .stat-lbl {
        font-size: 0.72rem;
        color: #5d6168;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
      }

      .features {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        padding: 50px 60px;
        background: #0f1117;
      }
      .feat-card {
        background: #131722;
        border: 1px solid #1e222d;
        border-radius: 12px;
        padding: 28px 24px;
        transition: border-color 0.2s, transform 0.2s;
      }
      .feat-card:hover { border-color: #2a2e39; transform: translateY(-2px); }
      .feat-icon {
        width: 40px;
        height: 40px;
        background: rgba(41,98,255,0.1);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        margin-bottom: 16px;
      }
      .feat-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #d1d4dc;
        margin-bottom: 8px;
      }
      .feat-desc {
        font-size: 0.82rem;
        color: #5d6168;
        line-height: 1.6;
      }

      .lp-footer {
        text-align: center;
        padding: 24px;
        background: #0f1117;
        border-top: 1px solid #1e222d;
        font-size: 0.78rem;
        color: #4c525e;
      }
    </style>
    """)
except AttributeError:
    pass

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------

usuario = st.session_state.get("usuario_autenticado")

bienvenida = (
    f'<div class="hero-tag">Bienvenido de vuelta, {usuario["nombre"]}</div>'
    if usuario
    else '<div class="hero-tag">Plataforma de analisis financiero</div>'
)

try:
    st.html(f"""
    <div class="hero">
        {bienvenida}
        <div class="hero-title">Analiza mercados.<br><span>Toma mejores decisiones.</span></div>
        <div class="hero-sub">
            Graficos en tiempo real, indicadores tecnicos avanzados
            y modelos de tendencias con Machine Learning — todo en un solo lugar.
        </div>
    </div>

    <div class="stats-bar">
        <div class="stat-item">
            <span class="stat-num">50+</span>
            <span class="stat-lbl">Mercados</span>
        </div>
        <div class="stat-item">
            <span class="stat-num">3</span>
            <span class="stat-lbl">Indicadores tecnicos</span>
        </div>
        <div class="stat-item">
            <span class="stat-num">5 anos</span>
            <span class="stat-lbl">Datos historicos</span>
        </div>
        <div class="stat-item">
            <span class="stat-num">ML</span>
            <span class="stat-lbl">Modelo de tendencias</span>
        </div>
    </div>
    """)
except AttributeError:
    st.title("Analiza mercados. Toma mejores decisiones.")

# ---------------------------------------------------------------------------
# CTA
# ---------------------------------------------------------------------------

st.write("")
col_l, col_c, col_r = st.columns([2, 1, 2])
with col_c:
    if usuario:
        if st.button("Ir al mercado", use_container_width=True, type="primary"):
            st.switch_page("all_pages/6_mercado_page.py")
    else:
        if st.button("Comenzar ahora", use_container_width=True, type="primary"):
            st.switch_page("all_pages/2_auth_page.py")

st.write("")

# ---------------------------------------------------------------------------
# Features
# ---------------------------------------------------------------------------

try:
    st.html("""
    <div class="features">
        <div class="feat-card">
            <div class="feat-icon">&#9700;</div>
            <div class="feat-title">Graficos interactivos</div>
            <div class="feat-desc">
                Velas japonesas con SMA, Bandas de Bollinger, RSI y MACD
                en tiempo real sobre cualquier activo.
            </div>
        </div>
        <div class="feat-card">
            <div class="feat-icon">&#9670;</div>
            <div class="feat-title">Modelo de tendencias</div>
            <div class="feat-desc">
                Random Forest entrenado con 5 anos de datos historicos
                que clasifica la direccion del siguiente cierre segun indicadores tecnicos.
            </div>
        </div>
        <div class="feat-card">
            <div class="feat-icon">&#9632;</div>
            <div class="feat-title">Mercados globales</div>
            <div class="feat-desc">
                Acciones US, criptomonedas, bolsas europeas e indices
                mundiales en una sola pantalla.
            </div>
        </div>
    </div>
    """)
except AttributeError:
    pass

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

try:
    st.html('<div class="lp-footer">© 2025 Nuu · Plataforma de analisis financiero · Datos provistos por Yahoo Finance</div>')
except AttributeError:
    st.caption("© 2025 Nuu · Datos provistos por Yahoo Finance")
