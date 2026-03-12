import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
import base64

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from config.clubs import get_league_logo_path
from app.utils import plotly_color

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
def load_data():
    matches, classements, players = {}, {}, {}
    for league in LEAGUES:
        m = os.path.join(FOLDER, f"{league}_matches_clean.csv")
        c = os.path.join(FOLDER, f"{league}_classement_clean.csv")
        p = os.path.join(FOLDER, f"{league}_players_standard_clean.csv")
        if os.path.exists(m): matches[league]     = pd.read_csv(m, parse_dates=["Date"])
        if os.path.exists(c): classements[league] = pd.read_csv(c)
        if os.path.exists(p): players[league]     = pd.read_csv(p)
    return matches, classements, players


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
                border-top:2px solid {color};text-align:center;position:relative;overflow:hidden;'>
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
    matches, classements, players = load_data()

    # ── HERO HEADER : texte + fond (sans logos pour éviter le bug base64 inline) ─
    st.markdown("""
    <div style='background:linear-gradient(135deg,rgba(0,212,255,0.06) 0%,rgba(255,215,0,0.03) 50%,rgba(0,0,0,0) 100%);
        border:1px solid rgba(0,212,255,0.08);border-radius:20px;
        padding:40px 40px 32px;margin-bottom:12px;position:relative;overflow:hidden;'>
        <div style='position:absolute;top:-60px;right:-60px;width:300px;height:300px;
            background:radial-gradient(circle,rgba(0,212,255,0.06),transparent 70%);border-radius:50%;'></div>
        <div style='position:absolute;bottom:-40px;left:10%;width:200px;height:200px;
            background:radial-gradient(circle,rgba(255,215,0,0.04),transparent 70%);border-radius:50%;'></div>
        <div style='font-family:"Bebas Neue",sans-serif;font-size:3.6rem;letter-spacing:6px;line-height:1;
            background:linear-gradient(135deg,#00d4ff,#ffffff,#ffd700);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text'>
            FOOTBALL ANALYTICS
        </div>
        <div style='font-family:"Inter",sans-serif;font-size:14px;color:#555;
            letter-spacing:3px;margin:8px 0 0;text-transform:uppercase'>
            SAISON 2024 · 2025 · 6 COMPÉTITIONS
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── LOGOS LIGUES : markdown séparé court pour éviter le bug d'affichage HTML ─
    logos_html = "<div style='display:flex;align-items:center;gap:20px;flex-wrap:wrap;padding:0 8px;margin-bottom:24px'>"
    for league in LEAGUES:
        b64 = get_logo_b64(league)
        if b64:
            logos_html += (
                f'<img src="data:image/png;base64,{b64}" '
                f'style="height:40px;width:auto;opacity:0.75;'
                f'filter:grayscale(20%);object-fit:contain">'
            )
    logos_html += "</div>"
    st.markdown(logos_html, unsafe_allow_html=True)

    # ── KPIs ─────────────────────────────────────────────────────────────────────
    total_matches = sum(len(df) for df in matches.values())
    total_goals   = int(sum(df["total_goals"].sum() for df in matches.values() if "total_goals" in df.columns))
    total_players = sum(len(df) for df in players.values())
    avg_goals     = round(total_goals / total_matches, 2) if total_matches > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Matchs joues",   f"{total_matches:,}", color="#00d4ff", icon="⚽")
    with c2: kpi_card("Buts marques",   f"{total_goals:,}",   color="#ffd700", icon="🥅")
    with c3: kpi_card("Joueurs suivis", f"{total_players:,}", color="#00ff87", icon="👤")
    with c4: kpi_card("Buts / match",   f"{avg_goals}",       color="#ff6b6b", icon="📊")

    # ── TOP 5 PAR LIGUE ───────────────────────────────────────────────────────────
    section_title("TOP 5 PAR COMPÉTITION")

    cols        = st.columns(3)
    league_list = [l for l in LEAGUES if l in classements]

    for i, league in enumerate(league_list):
        df    = classements[league]
        color = LEAGUE_COLORS.get(league, "#00d4ff")
        b64   = get_logo_b64(league)
        top   = df.nlargest(5, "Pts")[["Squad", "W", "D", "L", "Pts"]].reset_index(drop=True)
        top.index += 1

        with cols[i % 3]:
            # Header de la carte : logo séparé du bloc principal
            h_col, l_col = st.columns([4, 1])
            with h_col:
                st.markdown(f"""
                <div style='background:#0f1420;border-radius:10px 10px 0 0;
                            border-top:2px solid {color};border-left:1px solid rgba(255,255,255,0.04);
                            border-right:1px solid rgba(255,255,255,0.04);padding:10px 14px'>
                    <span style='font-family:"Bebas Neue",sans-serif;font-size:1rem;
                                 letter-spacing:2px;color:{color}'>{LEAGUE_LABELS[league]}</span>
                </div>
                """, unsafe_allow_html=True)
            with l_col:
                if b64:
                    st.image(f"data:image/png;base64,{b64}", width=36)
            st.dataframe(top, use_container_width=True, height=200, hide_index=False)

    # ── BUTS PAR COMPETITION ──────────────────────────────────────────────────────
    section_title("BUTS PAR COMPÉTITION")

    goals_data = []
    for league, df in matches.items():
        if "total_goals" in df.columns:
            goals_data.append({
                "Ligue"     : LEAGUE_LABELS[league],
                "Total buts": int(df["total_goals"].sum()),
                "Moy/match" : round(df["total_goals"].mean(), 2),
            })

    if goals_data:
        gdf       = pd.DataFrame(goals_data).sort_values("Total buts", ascending=True)
        color_seq = [LEAGUE_COLORS.get(k, "#00d4ff") for k in LEAGUE_LABELS if k in matches]
        fig = px.bar(
            gdf, x="Total buts", y="Ligue", orientation="h",
            color="Ligue", color_discrete_sequence=color_seq,
            text="Total buts", hover_data=["Moy/match"],
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(15,20,32,0.8)",
            font_color="#ffffff", height=320,
            margin=dict(l=0, r=20, t=20, b=0), showlegend=False,
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#555"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#888"),
            font=dict(family="Rajdhani, sans-serif"),
        )
        fig.update_traces(textposition="outside", textfont_size=14)
        st.plotly_chart(fig, use_container_width=True)

    # ── TOP SCOREURS ──────────────────────────────────────────────────────────────
    section_title("TOP 15 SCOREURS — TOUTES LIGUES")

    all_players = []
    for league, df in players.items():
        if "Player" in df.columns and "Performance_Gls" in df.columns:
            tmp = df[["Player", "Squad", "Performance_Gls", "Performance_Ast"]].copy()
            tmp.columns = ["Player", "Squad", "Gls", "Ast"]
            tmp["League"] = LEAGUE_LABELS[league]
            all_players.append(tmp)

    if all_players:
        adf       = pd.concat(all_players, ignore_index=True).dropna(subset=["Gls"])
        top15     = adf.nlargest(15, "Gls").reset_index(drop=True)
        color_map = {v: LEAGUE_COLORS.get(k, "#00d4ff") for k, v in LEAGUE_LABELS.items()}
        fig2 = px.bar(
            top15.sort_values("Gls"), x="Gls", y="Player",
            orientation="h", color="League",
            color_discrete_map=color_map,
            text="Gls", hover_data=["Squad", "Ast"],
        )
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(15,20,32,0.8)",
            font_color="#ffffff", height=500,
            margin=dict(l=0, r=20, t=20, b=0),
            legend=dict(orientation="h", y=1.05, font=dict(size=12, family="Rajdhani")),
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#555"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#888"),
            font=dict(family="Rajdhani, sans-serif"),
        )
        fig2.update_traces(textposition="outside", textfont_size=13)
        st.plotly_chart(fig2, use_container_width=True)

    # ── CARTE NATIONALITES ────────────────────────────────────────────────────────
    section_title("CARTE DES NATIONALITÉS")

    nat_dfs = [df[["Nation"]] for df in players.values() if "Nation" in df.columns]
    if nat_dfs:
        nat_counts = pd.concat(nat_dfs, ignore_index=True)["Nation"].value_counts().reset_index()
        nat_counts.columns = ["Nation", "Count"]
        fig3 = px.choropleth(
            nat_counts, locations="Nation", locationmode="ISO-3", color="Count",
            color_continuous_scale=[
                [0,   plotly_color("#0f1420")],
                [0.3, plotly_color("#00416a")],
                [1,   plotly_color("#00d4ff")],
            ],
        )
        fig3.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(15,20,32,0.8)",
            font_color="#ffffff", height=400,
            margin=dict(l=0, r=0, t=0, b=0),
            geo=dict(bgcolor="rgba(0,0,0,0)", showframe=False,
                     showcoastlines=True, coastlinecolor="rgba(255,255,255,0.1)",
                     showland=True, landcolor="#111827",
                     showocean=True, oceancolor="#070b12"),
            coloraxis_colorbar=dict(
                tickfont=dict(color="#888"),
                title=dict(text="Joueurs", font=dict(color="#888")),
            ),
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ── DERNIERS RESULTATS UCL ────────────────────────────────────────────────────
    if "ucl" in matches:
        section_title("DERNIERS RÉSULTATS UCL", color="#ffd700")
        ucl    = matches["ucl"].dropna(subset=["Score"]).sort_values("Date", ascending=False)
        last10 = ucl[["Date", "Home", "Score", "Away"]].head(10).reset_index(drop=True)
        st.dataframe(last10, use_container_width=True)

    # ── FOOTER ────────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style='margin-top:60px;padding:20px;border-top:1px solid rgba(255,255,255,0.04);text-align:center'>
        <span style='font-family:"Inter",sans-serif;font-size:11px;color:#333;
                     letter-spacing:2px;text-transform:uppercase'>
            Data source : FBref &nbsp;·&nbsp; Saison 2024-2025 &nbsp;·&nbsp; Built with Streamlit & Plotly
        </span>
    </div>
    """, unsafe_allow_html=True)


render()