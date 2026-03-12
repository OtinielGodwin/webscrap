"""
app/styles.py
CSS global et composants visuels partagés.
"""
import streamlit as st


def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600&family=Rajdhani:wght@500;600;700&display=swap');

    * { box-sizing: border-box; }

    html, body, [data-testid="stAppViewContainer"] {
        background: #07090f !important;
        color: #e0e0e0 !important;
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(ellipse at 20% 20%, rgba(0,212,255,0.04) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, rgba(255,215,0,0.03) 0%, transparent 50%),
            #07090f !important;
    }

    /* Hide keyboard shortcuts labels - target the specific text elements */
    [data-testid="stAppHeader"] {
        display: none !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #0b0e18 !important;
        border-right: 1px solid rgba(0,212,255,0.1) !important;
    }
    [data-testid="stSidebar"] * {
        font-family: 'Rajdhani', sans-serif !important;
    }

    /* Sidebar toggle button - cibler le vrai élément */
    button[aria-label*="toggle"] {
        color: #00d4ff !important;
        font-size: 0 !important;
    }
    button[aria-label*="toggle"]::before {
        content: "☰" !important;
        font-size: 20px !important;
        display: inline-block !important;
    }
    button[aria-label*="toggle"] svg {
        display: none !important;
    }
    button[aria-label*="toggle"] span {
        display: none !important;
    }

    /* Nav sidebar */
    [data-testid="stSidebarNav"] a {
        border-radius: 8px !important;
        margin: 2px 8px !important;
        padding: 10px 16px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        color: #888 !important;
        transition: all 0.2s ease !important;
        border-left: 3px solid transparent !important;
    }
    [data-testid="stSidebarNav"] a:hover {
        background: rgba(0,212,255,0.08) !important;
        color: #00d4ff !important;
        border-left-color: #00d4ff !important;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: rgba(0,212,255,0.12) !important;
        color: #00d4ff !important;
        border-left-color: #00d4ff !important;
    }

    /* Typographie */
    h1, h2, h3, h4, h5 {
        font-family: 'Bebas Neue', sans-serif !important;
        letter-spacing: 2px !important;
    }
    p, span, div, label, .stMarkdown {
        font-family: 'Inter', sans-serif !important;
    }

    /* Selectbox */
    [data-testid="stSelectbox"] > div > div {
        background: #0f1420 !important;
        border: 1px solid rgba(0,212,255,0.2) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600 !important;
    }
    [data-testid="stSelectbox"] > div > div:hover {
        border-color: #00d4ff !important;
    }

    /* Tabs */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        background: #0b0e18 !important;
        border-radius: 10px !important;
        padding: 4px !important;
        gap: 4px !important;
        border-bottom: none !important;
    }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 8px !important;
        color: #666 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        letter-spacing: 0.5px !important;
        padding: 8px 20px !important;
        border: none !important;
        transition: all 0.2s !important;
    }
    [data-testid="stTabs"] [data-baseweb="tab"]:hover {
        color: #00d4ff !important;
        background: rgba(0,212,255,0.08) !important;
    }
    [data-testid="stTabs"] [aria-selected="true"] {
        background: rgba(0,212,255,0.15) !important;
        color: #00d4ff !important;
        box-shadow: 0 0 20px rgba(0,212,255,0.2) !important;
    }
    [data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(0,212,255,0.1) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    /* Boutons */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff, #0099cc) !important;
        color: #000 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        letter-spacing: 1px !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 28px !important;
        transition: all 0.2s !important;
        text-transform: uppercase !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(0,212,255,0.3) !important;
    }

    /* Inputs */
    [data-testid="stNumberInput"] input,
    [data-testid="stTextInput"] input {
        background: #0f1420 !important;
        border: 1px solid rgba(0,212,255,0.2) !important;
        border-radius: 8px !important;
        color: #fff !important;
        font-family: 'Rajdhani', sans-serif !important;
    }

    /* Slider */
    [data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
        background: #00d4ff !important;
        border-color: #00d4ff !important;
    }

    /* Expander */
    [data-testid="stExpander"] {
        background: #0f1420 !important;
        border: 1px solid rgba(0,212,255,0.1) !important;
        border-radius: 10px !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0b0e18; }
    ::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.3); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #00d4ff; }

    /* Padding global */
    .block-container {
        padding-top: 1.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* Alerts */
    [data-testid="stAlert"] {
        background: rgba(0,212,255,0.05) !important;
        border: 1px solid rgba(0,212,255,0.2) !important;
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)


def sidebar_brand():
    with st.sidebar:
        st.markdown("""
        <div style='padding:20px 16px 24px;border-bottom:1px solid rgba(0,212,255,0.1);margin-bottom:8px'>
            <div style='font-family:"Bebas Neue",sans-serif;font-size:1.6rem;
                        color:#00d4ff;letter-spacing:4px;line-height:1'>FOOTBALL</div>
            <div style='font-family:"Bebas Neue",sans-serif;font-size:1.1rem;
                        color:#ffd700;letter-spacing:6px;line-height:1.2'>ANALYTICS</div>
            <div style='font-family:"Inter",sans-serif;font-size:11px;
                        color:#333;margin-top:6px;letter-spacing:1px'>SAISON 2024 · 2025</div>
        </div>
        """, unsafe_allow_html=True)
