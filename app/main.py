import streamlit as st
from styles import inject_css, sidebar_brand

st.set_page_config(
    page_title            = "Football Analytics 2024-2025",
    page_icon             = "⚽",
    layout                = "wide",
    initial_sidebar_state = "expanded",
)

inject_css()
sidebar_brand()

pg = st.navigation([
    st.Page("pages/accueil.py",  title="Accueil",       url_path="accueil"),
    st.Page("pages/matchs.py",   title="Matchs",        url_path="matchs"),
    st.Page("pages/equipes.py",  title="Equipes",       url_path="equipes"),
    st.Page("pages/joueurs.py",  title="Joueurs",       url_path="joueurs"),
    st.Page("pages/ucl.py",      title="UCL / PSG",     url_path="ucl"),
    st.Page("pages/ml.py",       title="ML Analytics",  url_path="ml"),
])

pg.run()
