import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
def load_matches():
    dfs = {}
    for league in LEAGUES:
        path = os.path.join(FOLDER, f"{league}_matches_clean.csv")
        if os.path.exists(path):
            dfs[league] = pd.read_csv(path, parse_dates=["Date"])
    return dfs


def kpi_card(label, value, color="#00d4ff"):
    st.markdown(f"""
    <div style='background:#1a1d27;border-radius:12px;padding:20px;
                border-left:4px solid {color};text-align:center'>
        <p style='color:#888;font-size:13px;margin:0;text-transform:uppercase;letter-spacing:1px'>{label}</p>
        <h2 style='color:{color};margin:8px 0;font-size:2rem'>{value}</h2>
    </div>
    """, unsafe_allow_html=True)


def render():
    matches = load_matches()

    st.markdown("""
    <div style='padding:30px 0 10px'>
        <h1 style='font-size:2.5rem;color:#00d4ff;margin:0'>Analyse des Matchs</h1>
        <p style='color:#888;font-size:1rem;margin:8px 0'>Saison 2024-2025</p>
        <hr style='border:1px solid #1a1d27;margin:20px 0'>
    </div>
    """, unsafe_allow_html=True)

    # Filtre ligue
    selected = st.selectbox(
        "Selectionner une competition",
        options=LEAGUES,
        format_func=lambda x: LEAGUE_LABELS[x],
    )

    # Afficher le logo de la ligue sélectionnée
    logo_ligue = get_league_logo_path(selected)
    if logo_ligue:
        st.image(logo_ligue, width=100)

    df = matches.get(selected, pd.DataFrame())

    if df.empty:
        st.warning("Donnees non disponibles pour cette competition.")
        return

    # KPIs
    total_matchs  = len(df)
    total_goals   = int(df["total_goals"].sum()) if "total_goals" in df.columns else 0
    avg_goals     = round(df["total_goals"].mean(), 2) if "total_goals" in df.columns else 0
    total_home    = int((df["result"] == "home").sum()) if "result" in df.columns else 0
    total_away    = int((df["result"] == "away").sum()) if "result" in df.columns else 0
    total_draw    = int((df["result"] == "draw").sum()) if "result" in df.columns else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi_card("Matchs joues",  f"{total_matchs:,}",  color="#00d4ff")
    with c2: kpi_card("Buts marques",  f"{total_goals:,}",   color="#ffd700")
    with c3: kpi_card("Buts / match",  f"{avg_goals}",       color="#00ff87")
    with c4: kpi_card("Victoires dom", f"{total_home:,}",    color="#ff6b6b")
    with c5: kpi_card("Victoires ext", f"{total_away:,}",    color="#a78bfa")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # Distribution buts par match
    with col1:
        st.markdown("#### Distribution des buts par match")
        if "total_goals" in df.columns:
            fig = px.histogram(
                df, x="total_goals", nbins=10,
                color_discrete_sequence=["#00d4ff"],
                labels={"total_goals": "Buts par match", "count": "Nombre de matchs"},
            )
            fig.update_layout(
                plot_bgcolor="#0e1117", paper_bgcolor="#1a1d27",
                font_color="#ffffff", height=350,
                bargap=0.1,
            )
            st.plotly_chart(fig, use_container_width=True)

    # Repartition resultats
    with col2:
        st.markdown("#### Repartition des resultats")
        if "result" in df.columns:
            result_counts = df["result"].value_counts().reset_index()
            result_counts.columns = ["Resultat", "Count"]
            result_counts["Resultat"] = result_counts["Resultat"].map({
                "home" : "Victoire domicile",
                "away" : "Victoire exterieur",
                "draw" : "Match nul",
            })
            fig2 = px.pie(
                result_counts, values="Count", names="Resultat",
                color_discrete_sequence=["#00d4ff", "#ffd700", "#00ff87"],
                hole=0.4,
            )
            fig2.update_layout(
                plot_bgcolor="#0e1117", paper_bgcolor="#1a1d27",
                font_color="#ffffff", height=350,
            )
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Evolution buts dans le temps
    st.markdown("#### Evolution des buts dans le temps")
    if "Date" in df.columns and "total_goals" in df.columns:
        df_time = df.dropna(subset=["Date"]).sort_values("Date")
        df_time["cumul_goals"] = df_time["total_goals"].cumsum()

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=df_time["Date"], y=df_time["cumul_goals"],
            mode="lines", name="Buts cumulés",
            line=dict(color="#00d4ff", width=2),
            fill="tozeroy", fillcolor="rgba(0,212,255,0.1)",
        ))
        fig3.add_trace(go.Bar(
            x=df_time["Date"], y=df_time["total_goals"],
            name="Buts par match",
            marker_color="#ffd700", opacity=0.4,
        ))
        fig3.update_layout(
            plot_bgcolor="#0e1117", paper_bgcolor="#1a1d27",
            font_color="#ffffff", height=400,
            xaxis_title="Date", yaxis_title="Buts",
            legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    # Top équipes qui marquent
    with col3:
        st.markdown("#### Top 10 équipes les plus prolifiques")
        if "Home" in df.columns and "home_score" in df.columns:
            home = df.groupby("Home")["home_score"].sum().reset_index()
            home.columns = ["Squad", "Goals"]
            away = df.groupby("Away")["away_score"].sum().reset_index()
            away.columns = ["Squad", "Goals"]
            total = pd.concat([home, away]).groupby("Squad")["Goals"].sum().reset_index()
            total = total.nlargest(10, "Goals").sort_values("Goals")

            fig4 = px.bar(
                total, x="Goals", y="Squad", orientation="h",
                color="Goals", color_continuous_scale="Blues",
                text="Goals",
            )
            fig4.update_layout(
                plot_bgcolor="#0e1117", paper_bgcolor="#1a1d27",
                font_color="#ffffff", height=400,
                showlegend=False,
            )
            fig4.update_traces(textposition="outside")
            st.plotly_chart(fig4, use_container_width=True)

    # Top équipes qui encaissent le moins
    with col4:
        st.markdown("#### Top 10 meilleures défenses")
        if "Home" in df.columns and "away_score" in df.columns:
            home_conc = df.groupby("Home")["away_score"].sum().reset_index()
            home_conc.columns = ["Squad", "Conceded"]
            away_conc = df.groupby("Away")["home_score"].sum().reset_index()
            away_conc.columns = ["Squad", "Conceded"]
            total_conc = pd.concat([home_conc, away_conc]).groupby("Squad")["Conceded"].sum().reset_index()
            total_conc = total_conc.nsmallest(10, "Conceded").sort_values("Conceded", ascending=False)

            fig5 = px.bar(
                total_conc, x="Conceded", y="Squad", orientation="h",
                color="Conceded", color_continuous_scale="Reds",
                text="Conceded",
            )
            fig5.update_layout(
                plot_bgcolor="#0e1117", paper_bgcolor="#1a1d27",
                font_color="#ffffff", height=400,
                showlegend=False,
            )
            fig5.update_traces(textposition="outside")
            st.plotly_chart(fig5, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tableau des matchs
    st.markdown("#### Calendrier des matchs")
    cols_show = [c for c in ["Date", "Round", "Wk", "Home", "Score", "Away", "Attendance", "Venue"] if c in df.columns]

    search = st.text_input("Rechercher une equipe...")
    df_show = df[cols_show].sort_values("Date", ascending=False) if "Date" in df.columns else df[cols_show]

    if search:
        mask    = df_show.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
        df_show = df_show[mask]

    st.dataframe(df_show.reset_index(drop=True), use_container_width=True, height=400)

    st.markdown("""
    <hr style='border:1px solid #1a1d27;margin-top:40px'>
    <p style='text-align:center;color:#444;font-size:12px'>
        Data source : FBref · Saison 2024-2025 · Built with Streamlit & Plotly
    </p>
    """, unsafe_allow_html=True)


render()