import streamlit as st

all_pages = [
    st.Page("all_pages/1_landing_page.py", title="Home"),
    st.Page("all_pages/2_auth_page.py", title="Sign Up/Sign In"),
    st.Page("all_pages/3_A_page.py", title="Equipo A"),
    st.Page("all_pages/4_B_page.py", title="Equipo B"),
    st.Page("all_pages/5_C_page.py", title="Equipo Chat"),
]

pg = st.navigation(all_pages)
pg.run()
