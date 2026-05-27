import streamlit as st

# ---------------------------------------------------------------------------
# Páginas públicas (sin autenticación)
# ---------------------------------------------------------------------------
paginas_publicas = [
    st.Page("all_pages/1_landing_page.py", title="Home"),
    st.Page("all_pages/2_auth_page.py",    title="Iniciar sesión"),
]

# ---------------------------------------------------------------------------
# Páginas privadas (requieren login)
# ---------------------------------------------------------------------------
paginas_privadas = [
    st.Page("all_pages/1_landing_page.py", title="Home"),
    st.Page("all_pages/3_A_page.py",       title="Equipo A"),
    st.Page("all_pages/4_B_page.py",       title="Equipo B"),
    st.Page("all_pages/5_C_page.py",       title="Equipo Chat"),
]

# ---------------------------------------------------------------------------
# Sidebar con info de usuario y botón de cerrar sesión
# ---------------------------------------------------------------------------
if st.session_state.get("usuario_autenticado"):
    usuario = st.session_state["usuario_autenticado"]

    with st.sidebar:
        st.markdown(f"### 👤 {usuario['nombre']}")
        st.caption(f"📧 {usuario['email']}")
        st.divider()
        if st.button("🚪 Cerrar sesión", use_container_width=True, type="primary"):
            del st.session_state["usuario_autenticado"]
            st.rerun()

    pg = st.navigation(paginas_privadas)
else:
    pg = st.navigation(paginas_publicas)

pg.run()
