import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from config.clubs import get_club_logo_path, get_league_logo_path

FOLDER = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")
PSG_ID = "Paris S-G"


@st.cache_data
def load_data():
    matches    = pd.DataFrame()
    classement = pd.DataFrame()
    teams      = pd.DataFrame()

    m = os.path.join(FOLDER, "ucl_matches_clean.csv")
    c = os.path.join(FOLDER, "ucl_classement_clean.csv")
    t = os.path.join(FOLDER, "ucl_teams_clean.csv")

    if os.path.exists(m): matches    = pd.read_csv(m, parse_dates=["Date"])
    if os.path.exists(c): classement = pd.read_csv(c)
    if os.path.exists(t): teams      = pd.read_csv(t)

    return matches, classement, teams


def kpi_card(label, value, color="#00d4ff"):
    st.markdown(f"""
    <div style='background:#1a1d27;border-radius:12px;padding:20px;
                border-left:4px solid {color};text-align:center'>
        <p style='color:#888;font-size:13px;margin:0;text-transform:uppercase;letter-spacing:1px'>{label}</p>
        <h2 style='color:{color};margin:8px 0;font-size:2rem'>{value}</h2>
    </div>
    """, unsafe_allow_html=True)


def render():
    matches, classement, teams = load_data()

    st.markdown("""
    <div style='padding:30px 0 10px'>
        <h1 style='font-size:2.5rem;color:#ffd700;margin:0'>UEFA Champions League 2024-2025</h1>
        <p style='color:#888;font-size:1rem;margin:8px 0'>Analyse complete · Focus PSG</p>
        <hr style='border:1px solid #1a1d27;margin:20px 0'>
    </div>
    """, unsafe_allow_html=True)

    # Afficher le logo de l'UCL
    logo_ucl = get_league_logo_path("ucl")
    if logo_ucl:
        st.image(logo_ucl, width=100)

    # KPIs UCL
    total_matchs = len(matches)
    total_goals  = int(matches["total_goals"].sum()) if "total_goals" in matches.columns else 0
    avg_goals    = round(matches["total_goals"].mean(), 2) if "total_goals" in matches.columns else 0
    nb_teams     = len(classement)

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Matchs joues",  f"{total_matchs}", color="#ffd700")
    with c2: kpi_card("Buts marques",  f"{total_goals}",  color="#00d4ff")
    with c3: kpi_card("Buts / match",  f"{avg_goals}",    color="#00ff87")
    with c4: kpi_card("Equipes",       f"{nb_teams}",     color="#ff6b6b")

    st.markdown("<br>", unsafe_allow_html=True)

    # Parcours PSG
    st.markdown("#### Parcours du PSG en UCL")
    psg_name = None
    if "Home" in matches.columns:
        for name in matches["Home"].dropna().unique():
            if "Paris" in str(name) or "PSG" in str(name):
                psg_name = name
                break
        if psg_name is None:
            for name in matches["Away"].dropna().unique():
                if "Paris" in str(name) or "PSG" in str(name):
                    psg_name = name
                    break

    if psg_name:
        psg_matches = matches[
            (matches["Home"] == psg_name) | (matches["Away"] == psg_name)
        ].sort_values("Date")

        psg_results = []
        for _, row in psg_matches.iterrows():
            if row["Home"] == psg_name:
                psg_results.append({
                    "Date"      : row["Date"],
                    "Round"     : row.get("Round", row.get("Wk", "")),
                    "Adversaire": row["Away"],
                    "Score"     : row["Score"],
                    "Buts PSG"  : row.get("home_score", 0),
                    "Buts Adv"  : row.get("away_score", 0),
                    "Domicile"  : "Domicile",
                })
            else:
                psg_results.append({
                    "Date"      : row["Date"],
                    "Round"     : row.get("Round", row.get("Wk", "")),
                    "Adversaire": row["Home"],
                    "Score"     : row["Score"],
                    "Buts PSG"  : row.get("away_score", 0),
                    "Buts Adv"  : row.get("home_score", 0),
                    "Domicile"  : "Exterieur",
                })

        psg_df = pd.DataFrame(psg_results)
        if not psg_df.empty:
            psg_df["Resultat"] = psg_df.apply(
                lambda r: "Victoire" if r["Buts PSG"] > r["Buts Adv"]
                else ("Defaite" if r["Buts PSG"] < r["Buts Adv"] else "Nul"), axis=1
            )

            # Stats PSG
            v = (psg_df["Resultat"] == "Victoire").sum()
            n = (psg_df["Resultat"] == "Nul").sum()
            d = (psg_df["Resultat"] == "Defaite").sum()
            gf = int(psg_df["Buts PSG"].sum())
            ga = int(psg_df["Buts Adv"].sum())

            c1, c2, c3, c4, c5 = st.columns(5)
            with c1: kpi_card("Victoires", str(v),       color="#00ff87")
            with c2: kpi_card("Nuls",      str(n),       color="#ffd700")
            with c3: kpi_card("Defaites",  str(d),       color="#ff6b6b")
            with c4: kpi_card("Buts",      str(gf),      color="#00d4ff")
            with c5: kpi_card("Encaisses", str(ga),      color="#a78bfa")

            st.markdown("<br>", unsafe_allow_html=True)

            # Timeline parcours PSG
            color_map = {"Victoire": "#00ff87", "Nul": "#ffd700", "Defaite": "#ff6b6b"}
            fig = px.scatter(
                psg_df, x="Date", y="Adversaire",
                color="Resultat", size="Buts PSG",
                color_discrete_map=color_map,
                hover_data=["Score", "Domicile", "Round"],
                text="Score",
            )
            fig.update_layout(
                plot_bgcolor="#0e1117", paper_bgcolor="#1a1d27",
                font_color="#ffffff", height=450,
                xaxis_title="", yaxis_title="",
            )
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(
                psg_df[["Date", "Round", "Adversaire", "Score", "Resultat", "Domicile"]].reset_index(drop=True),
                use_container_width=True,
            )
    else:
        st.info("Donnees PSG non trouvees dans les matchs UCL.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Classement UCL
    st.markdown("#### Classement phase de ligue")
    if not classement.empty:
        cols_show = [c for c in ["Rk", "Squad", "MP", "W", "D", "L", "GF", "GA", "GD", "Pts"] if c in classement.columns]
        st.dataframe(classement[cols_show].reset_index(drop=True), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # Top équipes en UCL
    with col1:
        st.markdown("#### Top equipes par points")
        if not classement.empty and "Pts" in classement.columns:
            top = classement.nlargest(10, "Pts").sort_values("Pts")
            fig2 = px.bar(
                top, x="Pts", y="Squad", orientation="h",
                color="Pts", color_continuous_scale="Oranges", text="Pts",
            )
            fig2.update_layout(
                plot_bgcolor="#0e1117", paper_bgcolor="#1a1d27",
                font_color="#ffffff", height=400, showlegend=False,
            )
            fig2.update_traces(textposition="outside")
            st.plotly_chart(fig2, use_container_width=True)

    # Distribution buts UCL
    with col2:
        st.markdown("#### Distribution des buts par match")
        if "total_goals" in matches.columns:
            fig3 = px.histogram(
                matches, x="total_goals", nbins=10,
                color_discrete_sequence=["#ffd700"],
            )
            fig3.update_layout(
                plot_bgcolor="#0e1117", paper_bgcolor="#1a1d27",
                font_color="#ffffff", height=400,
            )
            st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
    <hr style='border:1px solid #1a1d27;margin-top:40px'>
    <p style='text-align:center;color:#444;font-size:12px'>
        Data source : FBref · Saison 2024-2025 · Built with Streamlit & Plotly
    </p>
    """, unsafe_allow_html=True)


render()