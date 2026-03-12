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

# keyboard navigation: left/right arrows toggle the sidebar visibility
# we inject a small JS script that listens for arrow keys and clicks the
# built-in sidebar toggle button. this keeps everything in Python/HTML,
# avoiding external dependencies.

st.markdown("""
<script>
document.addEventListener('keydown', function(event) {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
        // find the Streamlit sidebar toggle button (aria-label may vary)
        var btn = document.querySelector('button[aria-label*="toggle"]');
        if (!btn) {
            // fallback: look for first button with svg hamburger
            btn = document.querySelector('button > svg');
            if (btn) btn = btn.closest('button');
        }
        if (btn) btn.click();
    }
});
</script>
""", unsafe_allow_html=True)

pg = st.navigation([
    st.Page("pages/accueil.py",  title="Accueil",       url_path="accueil"),
    st.Page("pages/matchs.py",   title="Matchs",        url_path="matchs"),
    st.Page("pages/equipes.py",  title="Equipes",       url_path="equipes"),
    st.Page("pages/joueurs.py",  title="Joueurs",       url_path="joueurs"),
    st.Page("pages/ucl.py",      title="UCL / PSG",     url_path="ucl"),
    st.Page("pages/ml.py",       title="ML Analytics",  url_path="ml"),
])

pg.run()
