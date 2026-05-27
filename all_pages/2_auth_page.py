"""
2_auth_page.py  —  Página de registro e inicio de sesión con 2FA (TOTP).
"""

import io
import os
import sys

import pyotp
import qrcode
import streamlit as st

# Asegura que db.py sea importable desde all_pages/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import db

# ---------------------------------------------------------------------------
# Inicialización
# ---------------------------------------------------------------------------
db.init_db()


st.markdown(
    """
<style>
    .stTabs [data-baseweb="tab"] { font-size: 1rem; padding: 0.5rem 1.5rem; }
    .stTabs [aria-selected="true"] { font-weight: bold; }
    div[data-testid="stForm"] { border: 1px solid rgba(128,128,128,0.2); border-radius: 12px; padding: 1rem; }
</style>
""",
    unsafe_allow_html=True,
)

st.title("🔐 Acceso a la plataforma")

# ---------------------------------------------------------------------------
# Helpers de UI
# ---------------------------------------------------------------------------


def _qr_bytes(totp_secret: str, email: str) -> bytes:
    totp = pyotp.TOTP(totp_secret)
    uri = totp.provisioning_uri(name=email, issuer_name="SitioApp")
    qr = qrcode.QRCode(
        version=1,
        box_size=8,
        border=4,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Tabs — Iniciar sesión primero
# ---------------------------------------------------------------------------

tab_login, tab_registro = st.tabs(["🚪 Iniciar sesión", "📝 Registrarse"])


# ══════════════════════════════════════════════════════════════════════════
# TAB 1 — INICIO DE SESIÓN
# ══════════════════════════════════════════════════════════════════════════

with tab_login:
    # Si ya inició sesión mostrar estado activo
    if st.session_state.get("usuario_autenticado"):
        usuario = st.session_state.usuario_autenticado
        st.success(f"✅ Sesión activa: **{usuario['nombre']}** ({usuario['email']})")
        st.info("Puedes navegar por las secciones desde el menú lateral.")

    # Formulario de login
    else:
        st.subheader("Iniciar sesión")
        st.info("INGRESE CREDENCIALES")

        with st.form("form_login"):
            email_login = st.text_input(
                "Correo electrónico", placeholder="pepito@ejemplo.com"
            )
            pwd_login = st.text_input("Contraseña", type="password")
            otp_login = st.text_input(
                "Código OTP (6 dígitos)", max_chars=6, placeholder="123456"
            )
            ingresar = st.form_submit_button("🔓 Ingresar", use_container_width=True)

        if ingresar:
            if not email_login or not pwd_login or not otp_login:
                st.error("Completa los tres campos: correo, contraseña y OTP.")
            else:
                resultado, mensaje = db.autenticar(
                    email_login.strip(), pwd_login, otp_login.strip()
                )

                if resultado == db.ResultadoAuth.OK:
                    usuario_row = db.obtener_usuario(email_login.strip())
                    st.session_state.usuario_autenticado = {
                        "id": usuario_row["id"],
                        "nombre": usuario_row["nombre"],
                        "email": usuario_row["email"],
                        "telefono": usuario_row["telefono"],
                        "fecha_nacimiento": usuario_row["fecha_nacimiento"],
                        "tarjeta_enc": usuario_row["tarjeta_enc"],
                    }
                    st.success(mensaje)
                    st.rerun()

                elif resultado == db.ResultadoAuth.OTP_NO_CONFIG:
                    st.warning(f"⚠️ {mensaje}")
                    st.info("Ve a la pestaña **Registrarse** para configurar tu OTP.")

                elif resultado == db.ResultadoAuth.OTP_REPLAY:
                    st.warning(f"🔄 {mensaje}")

                elif resultado == db.ResultadoAuth.BLOQUEADO:
                    st.error(f"🔒 {mensaje}")

                else:
                    st.error(f"❌ {mensaje}")


# ══════════════════════════════════════════════════════════════════════════
# TAB 2 — REGISTRO
# ══════════════════════════════════════════════════════════════════════════

with tab_registro:
    st.subheader("Crear cuenta nueva")

    # Estado para el flujo post-registro (setup de OTP)
    if "reg_totp_secret" not in st.session_state:
        st.session_state.reg_totp_secret = None
    if "reg_email" not in st.session_state:
        st.session_state.reg_email = None

    # ── Si ya registró y falta configurar el OTP ──────────────────────────
    if st.session_state.reg_totp_secret:
        st.success("✅ Usuario creado. Ahora configura tu autenticador.")
        st.info(
            "**Paso 1:** Escanea el código QR en Google Authenticator "
            "o cualquier app TOTP compatible.\n\n"
            "**Paso 2:** Ingresa el código de 6 dígitos para confirmar."
        )

        st.image(
            _qr_bytes(st.session_state.reg_totp_secret, st.session_state.reg_email),
            caption="Escanea este QR con tu autenticador",
            width=240,
        )

        with st.form("form_otp_setup"):
            codigo = st.text_input(
                "Código OTP (6 dígitos)", max_chars=6, placeholder="123456"
            )
            confirmar = st.form_submit_button("✅ Confirmar OTP")

        if confirmar:
            totp = pyotp.TOTP(st.session_state.reg_totp_secret)
            if totp.verify(codigo, valid_window=1):
                db.activar_totp(st.session_state.reg_email)
                st.success("🎉 OTP activado. ¡Ya puedes iniciar sesión!")
                st.session_state.reg_totp_secret = None
                st.session_state.reg_email = None
                st.rerun()
            else:
                st.error("Código incorrecto. Verifica la hora de tu dispositivo.")

    # ── Formulario de registro ────────────────────────────────────────────
    else:
        with st.form("form_registro"):
            st.markdown("#### 👤 Datos personales")
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre completo *", placeholder="Ana García")
                email = st.text_input(
                    "Correo electrónico *", placeholder="ana@ejemplo.com"
                )
                telefono = st.text_input("Teléfono", placeholder="+57 300 000 0000")
            with col2:
                fecha_nac = st.date_input("Fecha de nacimiento", value=None)
                direccion = st.text_area(
                    "Dirección", placeholder="Calle 123 # 45-67", height=80
                )

            st.markdown("#### 🏥 Datos de salud")
            col3, col4 = st.columns(2)
            with col3:
                grupo = st.selectbox(
                    "Grupo sanguíneo",
                    ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                )
            with col4:
                alergias = st.text_input(
                    "Alergias conocidas", placeholder="Penicilina, mariscos…"
                )

            st.markdown("#### 💳 Datos crediticios")
            col5, col6 = st.columns(2)
            with col5:
                tarjeta_tipo = st.selectbox(
                    "Tipo de tarjeta", ["", "Visa", "Mastercard", "Amex", "Otro"]
                )
                tarjeta_num = st.text_input(
                    "Número de tarjeta",
                    max_chars=19,
                    placeholder="**** **** **** ****",
                    type="password",
                )
            with col6:
                tarjeta_venc = st.text_input(
                    "Vencimiento (MM/AA)", max_chars=5, placeholder="12/27"
                )

            st.markdown("#### 🔑 Credenciales")
            st.caption(f"Política: {db.POLITICA_CONTRASENA}")
            col7, col8 = st.columns(2)
            with col7:
                pwd = st.text_input("Contraseña *", type="password")
            with col8:
                pwd2 = st.text_input("Confirmar contraseña *", type="password")

            registrar = st.form_submit_button(
                "🚀 Crear cuenta", use_container_width=True
            )

        if registrar:
            errores = []
            if not nombre.strip():
                errores.append("El nombre es obligatorio.")
            if not email.strip():
                errores.append("El correo es obligatorio.")
            if not pwd:
                errores.append("La contraseña es obligatoria.")
            if pwd != pwd2:
                errores.append("Las contraseñas no coinciden.")

            if errores:
                for e in errores:
                    st.error(e)
            else:
                datos = {
                    "nombre": nombre.strip(),
                    "email": email.strip(),
                    "telefono": telefono.strip(),
                    "fecha_nacimiento": str(fecha_nac) if fecha_nac else "",
                    "direccion": direccion.strip(),
                    "grupo_sanguineo": grupo,
                    "alergias": alergias.strip(),
                    "tarjeta_tipo": tarjeta_tipo,
                    "tarjeta_numero": tarjeta_num.strip(),
                    "tarjeta_venc": tarjeta_venc.strip(),
                    "contrasena": pwd,
                }
                ok, resultado = db.registrar_usuario(datos)
                if ok:
                    st.session_state.reg_totp_secret = resultado
                    st.session_state.reg_email = email.strip()
                    st.rerun()
                else:
                    st.error(resultado)


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<p style='text-align:center;'>© 2025 Nuu | All rights reserved.</p>",
    unsafe_allow_html=True,
)
