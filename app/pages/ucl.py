import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
import base64

from app.utils import plotly_color

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from config.clubs import get_club_logo_path, get_league_logo_path

FOLDER = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")


@st.cache_data
def load_data():
    matches = classement = teams = pd.DataFrame()
    m = os.path.join(FOLDER, "ucl_matches_clean.csv")
    c = os.path.join(FOLDER, "ucl_classement_clean.csv")
    t = os.path.join(FOLDER, "ucl_teams_clean.csv")
    if os.path.exists(m): matches    = pd.read_csv(m, parse_dates=["Date"])
    if os.path.exists(c): classement = pd.read_csv(c)
    if os.path.exists(t): teams      = pd.read_csv(t)
    return matches, classement, teams


def get_logo_b64(path):
    if path and os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def kpi_card(label, value, color="#ffd700"):
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#0f1420,#131825);border-radius:12px;
                padding:20px 16px;border:1px solid rgba(255,255,255,0.04);
                border-top:2px solid {color};text-align:center'>
        <p style='color:#555;font-size:10px;margin:0;text-transform:uppercase;
                  letter-spacing:2px;font-family:"Inter",sans-serif'>{label}</p>
        <h2 style='color:{color};margin:8px 0 0;font-family:"Bebas Neue",sans-serif;
                   font-size:2.2rem;letter-spacing:2px;line-height:1'>{value}</h2>
    </div>
    """, unsafe_allow_html=True)


def section_title(title, color="#ffd700"):
    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:12px;margin:28px 0 16px'>
        <div style='width:4px;height:24px;background:linear-gradient({color},transparent);border-radius:2px'></div>
        <span style='font-family:"Bebas Neue",sans-serif;font-size:1.4rem;letter-spacing:2px;color:{color}'>{title}</span>
        <div style='flex:1;height:1px;background:linear-gradient(90deg,rgba(255,255,255,0.05),transparent)'></div>
    </div>
    """, unsafe_allow_html=True)


def render():
    matches, classement, teams = load_data()

    # ── HEADER UCL ────────────────────────────────────────────────────────────────
    ucl_b64 = get_logo_b64(get_league_logo_path("ucl"))
    psg_b64 = get_logo_b64(get_club_logo_path("Paris Saint-Germain"))
    ucl_logo = f'<img src="data:image/png;base64,{ucl_b64}" style="height:72px;width:auto;filter:drop-shadow(0 0 16px #ffd70066)">' if ucl_b64 else ""
    psg_logo = f'<img src="data:image/png;base64,{psg_b64}" style="height:60px;width:auto;filter:drop-shadow(0 0 12px #00d4ff44)">' if psg_b64 else ""

    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:24px;padding:32px 36px;
                background:linear-gradient(135deg,rgba(255,215,0,0.06),rgba(0,0,0,0.4),rgba(0,212,255,0.03));
                border-radius:16px;border:1px solid rgba(255,215,0,0.12);
                border-left:4px solid #ffd700;margin-bottom:28px;position:relative;overflow:hidden'>
        <div style='position:absolute;top:-80px;right:-80px;width:350px;height:350px;
                    background:radial-gradient(circle,rgba(255,215,0,0.05),transparent 70%);border-radius:50%'></div>
        {ucl_logo}
        <div style='flex:1'>
            <div style='font-family:"Bebas Neue",sans-serif;font-size:2.6rem;letter-spacing:4px;line-height:1;
                        background:linear-gradient(135deg,#ffd700,#ffffff,#ffd700);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text'>
                UEFA CHAMPIONS LEAGUE 2024-2025
            </div>
            <div style='font-family:"Inter",sans-serif;font-size:13px;color:#555;margin-top:6px;letter-spacing:2px'>
                ANALYSE COMPLÈTE · FOCUS PSG
            </div>
        </div>
        {psg_logo}
    </div>
    """, unsafe_allow_html=True)

    # ── KPIs UCL ─────────────────────────────────────────────────────────────────
    total_matchs = len(matches)
    total_goals  = int(matches["total_goals"].sum()) if "total_goals" in matches.columns else 0
    avg_goals    = round(matches["total_goals"].mean(), 2) if "total_goals" in matches.columns else 0
    nb_teams     = len(classement)

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Matchs",      f"{total_matchs}", color="#ffd700")
    with c2: kpi_card("Buts",        f"{total_goals}",  color="#00d4ff")
    with c3: kpi_card("Buts/match",  f"{avg_goals}",    color="#00ff87")
    with c4: kpi_card("Équipes",     f"{nb_teams}",     color="#ff6b6b")

    # ── PARCOURS PSG ─────────────────────────────────────────────────────────────
    section_title("PARCOURS DU PSG", color="#00d4ff")

    psg_name = None
    if "Home" in matches.columns:
        for name in list(matches["Home"].dropna().unique()) + list(matches["Away"].dropna().unique()):
            if "Paris" in str(name) or "PSG" in str(name):
                psg_name = name
                break

    if psg_name:
        psg_matches = matches[(matches["Home"] == psg_name) | (matches["Away"] == psg_name)].sort_values("Date")

        psg_results = []
        for _, row in psg_matches.iterrows():
            is_home = row["Home"] == psg_name
            psg_results.append({
                "Date"      : row["Date"],
                "Round"     : row.get("Round", row.get("Wk","")),
                "Adversaire": row["Away"] if is_home else row["Home"],
                "Score"     : row["Score"],
                "Buts PSG"  : row.get("home_score",0) if is_home else row.get("away_score",0),
                "Buts Adv"  : row.get("away_score",0) if is_home else row.get("home_score",0),
                "Lieu"      : "Dom." if is_home else "Ext.",
            })

        psg_df = pd.DataFrame(psg_results)
        if not psg_df.empty:
            psg_df["Resultat"] = psg_df.apply(
                lambda r: "Victoire" if r["Buts PSG"] > r["Buts Adv"]
                else ("Défaite" if r["Buts PSG"] < r["Buts Adv"] else "Nul"), axis=1
            )

            v  = (psg_df["Resultat"] == "Victoire").sum()
            n  = (psg_df["Resultat"] == "Nul").sum()
            d  = (psg_df["Resultat"] == "Défaite").sum()
            gf = int(psg_df["Buts PSG"].sum())
            ga = int(psg_df["Buts Adv"].sum())

            c1, c2, c3, c4, c5 = st.columns(5)
            with c1: kpi_card("Victoires", str(v),  color="#00ff87")
            with c2: kpi_card("Nuls",      str(n),  color="#ffd700")
            with c3: kpi_card("Défaites",  str(d),  color="#ff6b6b")
            with c4: kpi_card("Buts",      str(gf), color="#00d4ff")
            with c5: kpi_card("Encaissés", str(ga), color="#a78bfa")

            st.markdown("<br>", unsafe_allow_html=True)

            color_map = {"Victoire": "#00ff87", "Nul": "#ffd700", "Défaite": "#ff6b6b"}
            fig = px.scatter(
                psg_df, x="Date", y="Adversaire",
                color="Resultat", size="Buts PSG",
                color_discrete_map=color_map,
                hover_data=["Score","Lieu","Round"],
                text="Score",
                size_max=25,
            )
            fig.update_traces(textfont=dict(family="Rajdhani", size=11, color="white"))
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(15,20,32,0.8)",
                font_color="#ffffff", height=480,
                margin=dict(l=0,r=0,t=20,b=0),
                legend=dict(orientation="h", y=1.06, font=dict(family="Rajdhani", size=13)),
                xaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#555"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#888"),
                font=dict(family="Rajdhani"),
            )
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(
                psg_df[["Date","Round","Adversaire","Score","Resultat","Lieu"]].reset_index(drop=True),
                use_container_width=True,
            )
    else:
        st.info("Données PSG non trouvées dans les matchs UCL.")

    # ── CLASSEMENT ────────────────────────────────────────────────────────────────
    if not classement.empty:
        section_title("CLASSEMENT PHASE DE LIGUE", color="#ffd700")
        cols_show = [c for c in ["Rk","Squad","MP","W","D","L","GF","GA","GD","Pts"] if c in classement.columns]
        st.dataframe(classement[cols_show].reset_index(drop=True), use_container_width=True)

    # ── TOP ÉQUIPES ───────────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        if not classement.empty and "Pts" in classement.columns:
            section_title("TOP ÉQUIPES", color="#ffd700")
            top = classement.nlargest(10, "Pts").sort_values("Pts")
            fig2 = px.bar(
                top, x="Pts", y="Squad", orientation="h",
                color="Pts", color_continuous_scale=[[0, plotly_color("#0f1420")],[1, plotly_color("#ffd700")]],
                text="Pts",
            )
            fig2.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(15,20,32,0.8)",
                font_color="#ffffff", height=400, showlegend=False,
                margin=dict(l=0,r=20,t=20,b=0),
                xaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#555"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#888"),
                font=dict(family="Rajdhani"),
            )
            fig2.update_traces(textposition="outside", textfont_size=13)
            st.plotly_chart(fig2, use_container_width=True)

    with col2:
        if "total_goals" in matches.columns:
            section_title("DISTRIBUTION DES BUTS", color="#00d4ff")
            fig3 = px.histogram(
                matches, x="total_goals", nbins=10,
                color_discrete_sequence=["#ffd700"],
            )
            fig3.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(15,20,32,0.8)",
                font_color="#ffffff", height=400,
                margin=dict(l=0,r=0,t=20,b=0),
                xaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#555", title="Buts par match"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#555", title="Fréquence"),
                font=dict(family="Rajdhani"),
                bargap=0.1,
                showlegend=False,
            )
            st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
    <div style='margin-top:60px;padding:20px;border-top:1px solid rgba(255,255,255,0.04);text-align:center'>
        <span style='font-family:"Inter",sans-serif;font-size:11px;color:#333;
                     letter-spacing:2px;text-transform:uppercase'>
            Data source : FBref &nbsp;·&nbsp; Saison 2024-2025 &nbsp;·&nbsp; Built with Streamlit & Plotly
        </span>
    </div>
    """, unsafe_allow_html=True)


render()
