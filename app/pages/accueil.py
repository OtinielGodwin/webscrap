import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from config.clubs import get_club_logo_path, get_league_logo_path

LEAGUES = ["ucl", "ligue1", "premier", "laliga", "bundesliga", "seriea"]
LEAGUE_LABELS = {
    "ucl"        : "Champions League",
    "ligue1"     : "Ligue 1",
    "premier"    : "Premier League",
    "laliga"     : "La Liga",
    "bundesliga" : "Bundesliga",
    "seriea"     : "Serie A",
}

FOLDER = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")


@st.cache_data
def load_data():
    matches, classements, players = {}, {}, {}

    for league in LEAGUES:
        m = os.path.join(FOLDER, f"{league}_matches_clean.csv")
        c = os.path.join(FOLDER, f"{league}_classement_clean.csv")
        p = os.path.join(FOLDER, f"{league}_players_standard_clean.csv")

        if os.path.exists(m):
            matches[league]     = pd.read_csv(m, parse_dates=["Date"])
        if os.path.exists(c):
            classements[league] = pd.read_csv(c)
        if os.path.exists(p):
            players[league]     = pd.read_csv(p)

    return matches, classements, players


def kpi_card(label, value, color="#00d4ff"):
    st.markdown(f"""
    <div style='background:#1a1d27;border-radius:12px;padding:20px;
                border-left:4px solid {color};text-align:center'>
        <p style='color:#888;font-size:13px;margin:0;text-transform:uppercase;letter-spacing:1px'>{label}</p>
        <h2 style='color:{color};margin:8px 0;font-size:2rem'>{value}</h2>
    </div>
    """, unsafe_allow_html=True)


def render():
    matches, classements, players = load_data()

    st.markdown("""
    <div style='text-align:center;padding:40px 0 20px'>
        <h1 style='font-size:3rem;color:#00d4ff;margin:0'>Football Analytics</h1>
        <p style='color:#888;font-size:1.1rem;margin:8px 0'>Saison 2024-2025 · Champions League · Ligue 1 · Premier League · La Liga · Bundesliga · Serie A</p>
        <hr style='border:1px solid #1a1d27;margin:20px 0'>
    </div>
    """, unsafe_allow_html=True)

    # KPIs
    total_matches = sum(len(df) for df in matches.values())
    total_goals   = sum(
        df["total_goals"].sum() for df in matches.values()
        if "total_goals" in df.columns
    )
    total_players = sum(len(df) for df in players.values())
    avg_goals     = round(total_goals / total_matches, 2) if total_matches > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Matchs joues",   f"{total_matches:,}",    color="#00d4ff")
    with c2: kpi_card("Buts marques",   f"{int(total_goals):,}", color="#ffd700")
    with c3: kpi_card("Joueurs suivis", f"{total_players:,}",    color="#00ff87")
    with c4: kpi_card("Buts / match",   f"{avg_goals}",          color="#ff6b6b")

    st.markdown("<br>", unsafe_allow_html=True)

    # Classements rapides
    st.markdown("### Top 5 par ligue")
    cols       = st.columns(3)
    league_list = [l for l in LEAGUES if l in classements]

    for i, league in enumerate(league_list):
        df  = classements[league]
        top = df.nlargest(5, "Pts")[["Squad", "MP", "W", "D", "L", "Pts"]].reset_index(drop=True)
        top.index += 1
        with cols[i % 3]:
            st.markdown(f"**{LEAGUE_LABELS[league]}**")
            st.dataframe(top, use_container_width=True, height=210)

    st.markdown("<br>", unsafe_allow_html=True)

    # Buts par ligue
    st.markdown("### Buts marques par competition")
    goals_data = []
    for league, df in matches.items():
        if "total_goals" in df.columns:
            goals_data.append({
                "Ligue"     : LEAGUE_LABELS[league],
                "Total buts": int(df["total_goals"].sum()),
                "Moy/match" : round(df["total_goals"].mean(), 2),
            })

    if goals_data:
        gdf = pd.DataFrame(goals_data).sort_values("Total buts", ascending=True)
        fig = px.bar(
            gdf, x="Total buts", y="Ligue", orientation="h",
            color="Moy/match", color_continuous_scale="Blues",
            text="Total buts",
        )
        fig.update_layout(
            plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
            font_color="#ffffff", height=350,
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Top scorers
    st.markdown("### Top 15 scoreurs — toutes ligues")
    all_players = []
    for league, df in players.items():
        if "Player" in df.columns and "Performance_Gls" in df.columns:
            tmp = df[["player_id", "Player", "Squad", "Performance_Gls", "Performance_Ast"]].copy()
            tmp.columns = ["player_id", "Player", "Squad", "Gls", "Ast"]
            tmp["League"] = LEAGUE_LABELS[league]
            all_players.append(tmp)

    if all_players:
        adf   = pd.concat(all_players, ignore_index=True).dropna(subset=["Gls"])
        top15 = adf.nlargest(15, "Gls").reset_index(drop=True)

        fig2 = px.bar(
            top15.sort_values("Gls"), x="Gls", y="Player",
            orientation="h", color="League",
            text="Gls", hover_data=["Squad", "Ast"],
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig2.update_layout(
            plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
            font_color="#ffffff", height=500,
        )
        fig2.update_traces(textposition="outside")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Carte nationalites
    st.markdown("### Carte des nationalites des joueurs")
    nat_dfs = [df[["Nation"]] for df in players.values() if "Nation" in df.columns]
    if nat_dfs:
        nat_counts = pd.concat(nat_dfs, ignore_index=True)["Nation"].value_counts().reset_index()
        nat_counts.columns = ["Nation", "Count"]

        fig3 = px.choropleth(
            nat_counts, locations="Nation",
            locationmode="ISO-3", color="Count",
            color_continuous_scale="Blues",
        )
        fig3.update_layout(
            plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
            font_color="#ffffff", height=450,
            geo=dict(bgcolor="#0e1117", showframe=False),
        )
        st.plotly_chart(fig3, use_container_width=True)

    # Derniers resultats UCL
    if "ucl" in matches:
        st.markdown("### Derniers resultats UCL")
        ucl    = matches["ucl"].dropna(subset=["Score"])
        ucl    = ucl.sort_values("Date", ascending=False)
        last10 = ucl[["Date", "Home", "Score", "Away"]].head(10).reset_index(drop=True)
        st.dataframe(last10, use_container_width=True)

    st.markdown("""
    <hr style='border:1px solid #1a1d27;margin-top:40px'>
    <p style='text-align:center;color:#444;font-size:12px'>
        Data source : FBref · Saison 2024-2025 · Built with Streamlit & Plotly
    </p>
    """, unsafe_allow_html=True)


render()