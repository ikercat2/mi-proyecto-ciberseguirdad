import streamlit as st

st.set_page_config(
    page_title="Nuu | Plataforma",
    page_icon="N",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Paginas
# ---------------------------------------------------------------------------

paginas_publicas = [
    st.Page("all_pages/1_landing_page.py", title="Inicio"),
    st.Page("all_pages/2_auth_page.py",    title="Acceso"),
]

paginas_privadas = [
    st.Page("all_pages/1_landing_page.py", title="Inicio"),
    st.Page("all_pages/6_mercado_page.py", title="Mercado"),
    st.Page("all_pages/7_grafico_page.py", title="Grafico"),
    st.Page("all_pages/8_modelo_page.py",  title="Modelo"),
    st.Page("all_pages/9_admin_page.py",   title="Administracion"),
]

# ---------------------------------------------------------------------------
# Sidebar con info de sesion
# ---------------------------------------------------------------------------

if st.session_state.get("usuario_autenticado"):
    usuario = st.session_state["usuario_autenticado"]

    with st.sidebar:
        st.markdown(f"**{usuario['nombre']}**")
        st.caption(usuario["email"])
        st.divider()
        if st.button("Cerrar sesion", use_container_width=True, type="primary"):
            del st.session_state["usuario_autenticado"]
            st.rerun()

    pg = st.navigation(paginas_privadas)
else:
    pg = st.navigation(paginas_publicas)

pg.run()
