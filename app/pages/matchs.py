import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
import base64

from app.utils import plotly_color

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from config.clubs import get_league_logo_path, get_club_logo_path

LEAGUES = ["ucl", "ligue1", "premier", "laliga", "bundesliga", "seriea"]
LEAGUE_LABELS = {
    "ucl"        : "Champions League",
    "ligue1"     : "Ligue 1",
    "premier"    : "Premier League",
    "laliga"     : "La Liga",
    "bundesliga" : "Bundesliga",
    "seriea"     : "Serie A",
}
LEAGUE_COLORS = {
    "ucl"        : "#ffd700",
    "ligue1"     : "#00d4ff",
    "premier"    : "#ff6b35",
    "laliga"     : "#ff3b5c",
    "bundesliga" : "#e8002d",
    "seriea"     : "#0066cc",
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


def get_logo_b64(league):
    path = get_league_logo_path(league)
    if path and os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def kpi_card(label, value, color="#00d4ff", icon=""):
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#0f1420,#131825);border-radius:12px;
                padding:20px 16px;border:1px solid rgba(255,255,255,0.04);
                border-top:2px solid {color};text-align:center;position:relative;overflow:hidden'>
        <div style='position:absolute;top:-20px;right:-10px;font-size:4rem;
                    opacity:0.04;font-family:"Bebas Neue",sans-serif;color:{color}'>{icon}</div>
        <p style='color:#555;font-size:10px;margin:0;text-transform:uppercase;
                  letter-spacing:2px;font-family:"Inter",sans-serif;font-weight:500'>{label}</p>
        <h2 style='color:{color};margin:8px 0 0;font-family:"Bebas Neue",sans-serif;
                   font-size:2.2rem;letter-spacing:2px;line-height:1'>{value}</h2>
    </div>
    """, unsafe_allow_html=True)


def section_title(title, color="#00d4ff"):
    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:12px;margin:28px 0 16px'>
        <div style='width:4px;height:24px;background:linear-gradient({color},transparent);border-radius:2px'></div>
        <span style='font-family:"Bebas Neue",sans-serif;font-size:1.4rem;letter-spacing:2px;color:{color}'>{title}</span>
        <div style='flex:1;height:1px;background:linear-gradient(90deg,rgba(255,255,255,0.05),transparent)'></div>
    </div>
    """, unsafe_allow_html=True)


def render():
    matches = load_matches()

    # ── HEADER ───────────────────────────────────────────────────────────────────
    selected = st.selectbox(
        "Compétition",
        options=LEAGUES,
        format_func=lambda x: LEAGUE_LABELS[x],
    )

    color = LEAGUE_COLORS.get(selected, "#00d4ff")
    b64   = get_logo_b64(selected)
    logo_html = f'<img src="data:image/png;base64,{b64}" style="height:64px;width:auto;filter:drop-shadow(0 0 12px {color}66)">' if b64 else ""

    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:20px;padding:28px 32px;
                background:linear-gradient(135deg,rgba(0,0,0,0.4),rgba(15,20,32,0.6));
                border-radius:16px;border:1px solid rgba(255,255,255,0.05);
                border-left:4px solid {color};margin-bottom:28px;position:relative;overflow:hidden'>
        <div style='position:absolute;top:0;left:0;right:0;bottom:0;
                    background:linear-gradient(135deg,{color}08,transparent 60%);pointer-events:none'></div>
        {logo_html}
        <div>
            <div style='font-family:"Bebas Neue",sans-serif;font-size:2.4rem;letter-spacing:3px;line-height:1;
                        background:linear-gradient(135deg,{color},#ffffff);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text'>
                ANALYSE DES MATCHS
            </div>
            <div style='font-family:"Inter",sans-serif;font-size:13px;color:#555;margin-top:4px;letter-spacing:1px'>
                {LEAGUE_LABELS[selected]} · SAISON 2024-2025
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    df = matches.get(selected, pd.DataFrame())
    if df.empty:
        st.warning("Donnees non disponibles.")
        return

    # ── KPIs ─────────────────────────────────────────────────────────────────────
    total_matchs = len(df)
    total_goals  = int(df["total_goals"].sum()) if "total_goals" in df.columns else 0
    avg_goals    = round(df["total_goals"].mean(), 2) if "total_goals" in df.columns else 0
    total_home   = int((df["result"] == "home").sum()) if "result" in df.columns else 0
    total_away   = int((df["result"] == "away").sum()) if "result" in df.columns else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi_card("Matchs",       f"{total_matchs:,}", color=color)
    with c2: kpi_card("Buts",         f"{total_goals:,}",  color="#ffd700")
    with c3: kpi_card("Buts/match",   f"{avg_goals}",      color="#00ff87")
    with c4: kpi_card("Victoires dom",f"{total_home:,}",   color="#ff6b6b")
    with c5: kpi_card("Victoires ext",f"{total_away:,}",   color="#a78bfa")

    # ── GRAPHIQUES ────────────────────────────────────────────────────────────────
    section_title("DISTRIBUTION & RÉSULTATS", color=color)

    col1, col2 = st.columns(2)
    with col1:
        if "total_goals" in df.columns:
            fig = px.histogram(
                df, x="total_goals", nbins=10,
                color_discrete_sequence=[color],
                labels={"total_goals": "Buts par match"},
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(15,20,32,0.8)",
                font_color="#ffffff", height=340, margin=dict(l=0,r=0,t=20,b=0),
                xaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#555"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#555"),
                font=dict(family="Rajdhani"),
                title=dict(text="Distribution des buts", font=dict(family="Bebas Neue", size=18, color=color)),
                bargap=0.1,
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "result" in df.columns:
            result_counts = df["result"].value_counts().reset_index()
            result_counts.columns = ["Resultat", "Count"]
            result_counts["Resultat"] = result_counts["Resultat"].map({
                "home" : "Domicile", "away" : "Extérieur", "draw" : "Nul",
            })
            fig2 = px.pie(
                result_counts, values="Count", names="Resultat",
                color_discrete_sequence=[color, "#ffd700", "#00ff87"],
                hole=0.5,
            )
            fig2.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(15,20,32,0.8)",
                font_color="#ffffff", height=340, margin=dict(l=0,r=0,t=20,b=0),
                legend=dict(font=dict(family="Rajdhani", size=13)),
                font=dict(family="Rajdhani"),
                title=dict(text="Répartition des résultats", font=dict(family="Bebas Neue", size=18, color=color)),
            )
            fig2.update_traces(textfont_size=14)
            st.plotly_chart(fig2, use_container_width=True)

    # ── ÉVOLUTION TEMPORELLE ──────────────────────────────────────────────────────
    section_title("ÉVOLUTION DANS LE TEMPS", color=color)

    if "Date" in df.columns and "total_goals" in df.columns:
        df_time = df.dropna(subset=["Date"]).sort_values("Date")
        df_time["cumul_goals"] = df_time["total_goals"].cumsum()

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=df_time["Date"], y=df_time["cumul_goals"],
            mode="lines", name="Buts cumulés",
            line=dict(color=color, width=2),
            fill="tozeroy", fillcolor=plotly_color(color, "18"),
        ))
        fig3.add_trace(go.Bar(
            x=df_time["Date"], y=df_time["total_goals"],
            name="Buts par match",
            marker_color="#ffd700", opacity=0.35,
        ))
        fig3.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(15,20,32,0.8)",
            font_color="#ffffff", height=380,
            margin=dict(l=0,r=0,t=20,b=0),
            legend=dict(orientation="h", y=1.08, font=dict(family="Rajdhani")),
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#555"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#555"),
            font=dict(family="Rajdhani"),
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ── TOP ÉQUIPES ───────────────────────────────────────────────────────────────
    section_title("MEILLEURES ÉQUIPES", color=color)

    col3, col4 = st.columns(2)
    with col3:
        if "Home" in df.columns and "home_score" in df.columns:
            home  = df.groupby("Home")["home_score"].sum().reset_index()
            home.columns = ["Squad", "Goals"]
            away  = df.groupby("Away")["away_score"].sum().reset_index()
            away.columns = ["Squad", "Goals"]
            total = pd.concat([home, away]).groupby("Squad")["Goals"].sum().reset_index()
            total = total.nlargest(10, "Goals").sort_values("Goals")

            fig4 = px.bar(
                total, x="Goals", y="Squad", orientation="h",
                color="Goals", color_continuous_scale=[[0, plotly_color("#0f1420")],[1, plotly_color(color)]],
                text="Goals",
            )
            fig4.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(15,20,32,0.8)",
                font_color="#ffffff", height=380, showlegend=False,
                margin=dict(l=0,r=20,t=20,b=0),
                xaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#555"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#888"),
                font=dict(family="Rajdhani"),
                title=dict(text="Top 10 attaques", font=dict(family="Bebas Neue", size=18, color=color)),
            )
            fig4.update_traces(textposition="outside", textfont_size=13)
            st.plotly_chart(fig4, use_container_width=True)

    with col4:
        if "Home" in df.columns and "away_score" in df.columns:
            home_c = df.groupby("Home")["away_score"].sum().reset_index()
            home_c.columns = ["Squad", "Conceded"]
            away_c = df.groupby("Away")["home_score"].sum().reset_index()
            away_c.columns = ["Squad", "Conceded"]
            total_c = pd.concat([home_c, away_c]).groupby("Squad")["Conceded"].sum().reset_index()
            total_c = total_c.nsmallest(10, "Conceded").sort_values("Conceded", ascending=False)

            fig5 = px.bar(
                total_c, x="Conceded", y="Squad", orientation="h",
                color="Conceded", color_continuous_scale=[[0, plotly_color("#0f1420")],[1, plotly_color("#00ff87")]],
                text="Conceded",
            )
            fig5.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(15,20,32,0.8)",
                font_color="#ffffff", height=380, showlegend=False,
                margin=dict(l=0,r=20,t=20,b=0),
                xaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#555"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#888"),
                font=dict(family="Rajdhani"),
                title=dict(text="Top 10 défenses", font=dict(family="Bebas Neue", size=18, color="#00ff87")),
            )
            fig5.update_traces(textposition="outside", textfont_size=13)
            st.plotly_chart(fig5, use_container_width=True)

    # ── CALENDRIER ───────────────────────────────────────────────────────────────
    section_title("CALENDRIER DES MATCHS", color=color)

    cols_show = [c for c in ["Date","Round","Wk","Home","Score","Away","Attendance","Venue"] if c in df.columns]
    search    = st.text_input("🔍  Rechercher une équipe...")
    df_show   = df[cols_show].sort_values("Date", ascending=False) if "Date" in df.columns else df[cols_show]
    if search:
        mask    = df_show.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
        df_show = df_show[mask]

    st.dataframe(df_show.reset_index(drop=True), use_container_width=True, height=400)

    st.markdown("""
    <div style='margin-top:60px;padding:20px;border-top:1px solid rgba(255,255,255,0.04);text-align:center'>
        <span style='font-family:"Inter",sans-serif;font-size:11px;color:#333;
                     letter-spacing:2px;text-transform:uppercase'>
            Data source : FBref &nbsp;·&nbsp; Saison 2024-2025 &nbsp;·&nbsp; Built with Streamlit & Plotly
        </span>
    </div>
    """, unsafe_allow_html=True)


render()
