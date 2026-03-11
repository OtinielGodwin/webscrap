import streamlit as st

st.set_page_config(
    page_title            = "Football Analytics 2024-2025",
    layout                = "wide",
    initial_sidebar_state = "expanded",
)

pg = st.navigation([
    st.Page("pages/accueil.py",  title="Accueil"),
    st.Page("pages/matchs.py",   title="Matchs"),
    st.Page("pages/equipes.py",  title="Equipes"),
    st.Page("pages/joueurs.py",  title="Joueurs"),
    st.Page("pages/ucl.py",      title="UCL / PSG"),
    st.Page("pages/ml.py",       title="ML Analytics"),
])

pg.run()