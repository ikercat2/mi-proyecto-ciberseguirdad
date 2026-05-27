"""
2_auth_page.py — Pagina de registro e inicio de sesion con 2FA (TOTP).
"""
import io
import os
import sys

import pyotp
import qrcode
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import db
from estilos import aplicar_estilos

db.init_db()
aplicar_estilos()

# CSS especifico del auth
try:
    st.html("""
    <style>
      .block-container { max-width: 520px !important; padding-top: 3rem !important; }

      .auth-logo {
        text-align: center;
        margin-bottom: 28px;
      }
      .auth-logo-text {
        font-size: 1.6rem;
        font-weight: 800;
        color: #d1d4dc;
        letter-spacing: -1px;
      }
      .auth-logo-dot { color: #2962ff; }
      .auth-title {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: #d1d4dc !important;
        text-align: center;
        margin-bottom: 6px !important;
      }
      .auth-sub {
        font-size: 0.82rem !important;
        color: #5d6168 !important;
        text-align: center;
        margin-bottom: 24px !important;
      }

      div[data-testid="stForm"] {
        background: #1a1e2c;
        border: 1px solid #2a2e39;
        border-radius: 12px;
        padding: 28px 28px 20px !important;
      }

      [data-testid="stTabs"] [data-baseweb="tab"] {
        padding: 10px 0 !important;
        flex: 1 !important;
        justify-content: center !important;
      }
    </style>
    """)
except AttributeError:
    pass

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _qr_bytes(totp_secret: str, email: str) -> bytes:
    totp = pyotp.TOTP(totp_secret)
    uri  = totp.provisioning_uri(name=email, issuer_name="NuuApp")
    qr   = qrcode.QRCode(version=1, box_size=8, border=4,
                          error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Logo
# ---------------------------------------------------------------------------

try:
    st.html("""
    <div class="auth-logo">
        <div class="auth-logo-text">nuu<span class="auth-logo-dot">.</span></div>
    </div>
    """)
except AttributeError:
    st.title("nuu.")

# ---------------------------------------------------------------------------
# Si ya inicio sesion
# ---------------------------------------------------------------------------

if st.session_state.get("usuario_autenticado"):
    usuario = st.session_state.usuario_autenticado
    st.success(f"Sesion activa: **{usuario['nombre']}**")
    if st.button("Ir al mercado", use_container_width=True, type="primary"):
        st.switch_page("all_pages/6_mercado_page.py")
    st.stop()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_login, tab_reg = st.tabs(["Iniciar sesion", "Crear cuenta"])

# ══════════════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════════════

with tab_login:
    try:
        st.html('<div class="auth-title">Bienvenido de vuelta</div><div class="auth-sub">Ingresa tus credenciales para continuar</div>')
    except AttributeError:
        st.subheader("Iniciar sesion")

    with st.form("form_login"):
        email_l = st.text_input("Correo electronico", placeholder="ejemplo@correo.com")
        pwd_l   = st.text_input("Contrasena", type="password", placeholder="Tu contrasena")
        otp_l   = st.text_input("Codigo OTP", max_chars=6, placeholder="6 digitos de tu autenticador")
        entrar  = st.form_submit_button("Iniciar sesion", use_container_width=True, type="primary")

    if entrar:
        if not email_l or not pwd_l or not otp_l:
            st.error("Completa todos los campos.")
        else:
            resultado, mensaje = db.autenticar(email_l.strip(), pwd_l, otp_l.strip())
            if resultado == db.ResultadoAuth.OK:
                row = db.obtener_usuario(email_l.strip())
                st.session_state.usuario_autenticado = {
                    "id":              row["id"],
                    "nombre":          row["nombre"],
                    "email":           row["email"],
                    "telefono":        row["telefono"],
                    "fecha_nacimiento": row["fecha_nacimiento"],
                    "tarjeta_enc":     row["tarjeta_enc"],
                }
                st.rerun()
            elif resultado == db.ResultadoAuth.OTP_NO_CONFIG:
                st.warning(f"{mensaje} — Ve a la pestana Crear cuenta para configurar tu OTP.")
            elif resultado == db.ResultadoAuth.OTP_REPLAY:
                st.warning(mensaje)
            elif resultado == db.ResultadoAuth.BLOQUEADO:
                st.error(mensaje)
            else:
                st.error(mensaje)

# ══════════════════════════════════════════════════════════════════
# REGISTRO
# ══════════════════════════════════════════════════════════════════

with tab_reg:
    if "reg_totp_secret" not in st.session_state:
        st.session_state.reg_totp_secret = None
    if "reg_email" not in st.session_state:
        st.session_state.reg_email = None

    # ── Setup OTP post-registro ───────────────────────────────────
    if st.session_state.reg_totp_secret:
        st.success("Cuenta creada. Configura tu autenticador.")
        st.info("**Paso 1** — Escanea el QR en Google Authenticator.\n\n**Paso 2** — Ingresa el codigo de 6 digitos.")
        st.image(_qr_bytes(st.session_state.reg_totp_secret,
                           st.session_state.reg_email), width=220)

        with st.form("form_otp_setup"):
            codigo  = st.text_input("Codigo OTP", max_chars=6, placeholder="123456")
            confirmar = st.form_submit_button("Confirmar y activar", use_container_width=True, type="primary")

        if confirmar:
            totp = pyotp.TOTP(st.session_state.reg_totp_secret)
            if totp.verify(codigo, valid_window=1):
                db.activar_totp(st.session_state.reg_email)
                st.success("OTP activado. Ya puedes iniciar sesion.")
                st.session_state.reg_totp_secret = None
                st.session_state.reg_email       = None
                st.rerun()
            else:
                st.error("Codigo incorrecto.")

    # ── Formulario de registro ────────────────────────────────────
    else:
        try:
            st.html('<div class="auth-title">Crea tu cuenta</div><div class="auth-sub">Rellena tus datos para registrarte</div>')
        except AttributeError:
            st.subheader("Crear cuenta")

        with st.form("form_registro"):
            st.markdown("**Datos personales**")
            col1, col2 = st.columns(2)
            with col1:
                nombre   = st.text_input("Nombre completo *", placeholder="Ana Garcia")
                email    = st.text_input("Correo electronico *", placeholder="ana@ejemplo.com")
                telefono = st.text_input("Telefono", placeholder="+57 300 000 0000")
            with col2:
                fecha_nac = st.date_input("Fecha de nacimiento", value=None)
                direccion = st.text_area("Direccion", placeholder="Calle 123 # 45-67", height=80)

            st.markdown("**Datos de salud**")
            col3, col4 = st.columns(2)
            with col3:
                grupo = st.selectbox("Grupo sanguineo",
                                      ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            with col4:
                alergias = st.text_input("Alergias conocidas", placeholder="Penicilina...")

            st.markdown("**Datos crediticios**")
            col5, col6 = st.columns(2)
            with col5:
                tarjeta_tipo = st.selectbox("Tipo de tarjeta", ["", "Visa", "Mastercard", "Amex", "Otro"])
                tarjeta_num  = st.text_input("Numero de tarjeta", max_chars=19,
                                              placeholder="**** **** **** ****", type="password")
            with col6:
                tarjeta_venc = st.text_input("Vencimiento (MM/AA)", max_chars=5, placeholder="12/27")

            st.markdown("**Contrasena**")
            st.caption(db.POLITICA_CONTRASENA)
            col7, col8 = st.columns(2)
            with col7:
                pwd  = st.text_input("Contrasena *", type="password")
            with col8:
                pwd2 = st.text_input("Confirmar contrasena *", type="password")

            registrar = st.form_submit_button("Crear cuenta", use_container_width=True, type="primary")

        if registrar:
            errores = []
            if not nombre.strip():  errores.append("El nombre es obligatorio.")
            if not email.strip():   errores.append("El correo es obligatorio.")
            if not pwd:             errores.append("La contrasena es obligatoria.")
            if pwd != pwd2:         errores.append("Las contrasenas no coinciden.")

            for e in errores:
                st.error(e)

            if not errores:
                datos = {
                    "nombre":          nombre.strip(),
                    "email":           email.strip(),
                    "telefono":        telefono.strip(),
                    "fecha_nacimiento": str(fecha_nac) if fecha_nac else "",
                    "direccion":       direccion.strip(),
                    "grupo_sanguineo": grupo,
                    "alergias":        alergias.strip(),
                    "tarjeta_tipo":    tarjeta_tipo,
                    "tarjeta_numero":  tarjeta_num.strip(),
                    "tarjeta_venc":    tarjeta_venc.strip(),
                    "contrasena":      pwd,
                }
                ok, resultado = db.registrar_usuario(datos)
                if ok:
                    st.session_state.reg_totp_secret = resultado
                    st.session_state.reg_email       = email.strip()
                    st.rerun()
                else:
                    st.error(resultado)
