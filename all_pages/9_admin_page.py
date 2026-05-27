"""
9_admin_page.py — Administracion: gestion y descarga de usuarios registrados.
"""
import io
import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import db
from estilos import aplicar_estilos

if not st.session_state.get("usuario_autenticado"):
    st.warning("Debes iniciar sesion para acceder.")
    st.stop()

aplicar_estilos()

try:
    db.init_db()
    usuarios = db.obtener_usuarios_para_excel()
except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")
    st.stop()

# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

st.title("Administracion")
st.caption("Gestion de usuarios registrados en la plataforma.")

if not usuarios:
    st.info("No hay usuarios registrados.")
    st.stop()

df = pd.DataFrame(usuarios)
df.columns = [
    "Nombre", "Email", "Telefono",
    "Fecha de nacimiento", "Grupo sanguineo", "Alergias", "Registrado en",
]

# ── Metricas ──────────────────────────────────────────────────────────────────

c1, c2, c3 = st.columns(3)
c1.metric("Total de usuarios",  len(df))
c2.metric("Con telefono",       int(df["Telefono"].astype(bool).sum()))
c3.metric("Con alergias",       int(df["Alergias"].astype(bool).sum()))

st.divider()

# ── Tabla ─────────────────────────────────────────────────────────────────────

st.subheader("Listado de usuarios")
st.dataframe(
    df[["Nombre", "Email", "Telefono", "Fecha de nacimiento", "Registrado en"]],
    use_container_width=True,
    hide_index=True,
)

st.divider()

# ── Descarga Excel ────────────────────────────────────────────────────────────

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Usuarios")
buffer.seek(0)

st.download_button(
    label=f"Descargar Excel  ({len(df)} usuarios)",
    data=buffer,
    file_name="usuarios_registrados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    type="primary",
)
