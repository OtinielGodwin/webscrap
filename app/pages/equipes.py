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
    teams, classements = {}, {}
    for league in LEAGUES:
        t = os.path.join(FOLDER, f"{league}_teams_clean.csv")
        c = os.path.join(FOLDER, f"{league}_classement_clean.csv")
        if os.path.exists(t): teams[league]       = pd.read_csv(t)
        if os.path.exists(c): classements[league] = pd.read_csv(c)
    return teams, classements


def get_logo_b64(path):
    if path and os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def kpi_card(label, value, color="#00d4ff"):
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


def section_title(title, color="#00d4ff"):
    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:12px;margin:28px 0 16px'>
        <div style='width:4px;height:24px;background:linear-gradient({color},transparent);border-radius:2px'></div>
        <span style='font-family:"Bebas Neue",sans-serif;font-size:1.4rem;letter-spacing:2px;color:{color}'>{title}</span>
        <div style='flex:1;height:1px;background:linear-gradient(90deg,rgba(255,255,255,0.05),transparent)'></div>
    </div>
    """, unsafe_allow_html=True)


def render():
    teams, classements = load_data()

    selected = st.selectbox(
        "Compétition",
        options=[l for l in LEAGUES if l in teams or l in classements],
        format_func=lambda x: LEAGUE_LABELS[x],
    )

    color    = LEAGUE_COLORS.get(selected, "#00d4ff")
    logo_b64 = get_logo_b64(get_league_logo_path(selected))
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:64px;width:auto;filter:drop-shadow(0 0 12px {color}66)">' if logo_b64 else ""

    # ── HEADER ────────────────────────────────────────────────────────────────────
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
                ANALYSE DES ÉQUIPES
            </div>
            <div style='font-family:"Inter",sans-serif;font-size:13px;color:#555;margin-top:4px;letter-spacing:1px'>
                {LEAGUE_LABELS[selected]} · SAISON 2024-2025
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    df  = teams.get(selected, pd.DataFrame())
    dfc = classements.get(selected, pd.DataFrame())

    if df.empty and dfc.empty:
        st.warning("Donnees non disponibles.")
        return

    # ── KPIs ─────────────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Équipes",        f"{len(dfc) if not dfc.empty else len(df)}",  color=color)
    with c2: kpi_card("Total buts",     f"{int(df['Performance_Gls'].sum()) if not df.empty and 'Performance_Gls' in df.columns else 'N/A'}", color="#ffd700")
    with c3: kpi_card("Moy buts/éq.",   f"{round(df['Performance_Gls'].mean(),1) if not df.empty and 'Performance_Gls' in df.columns else 'N/A'}", color="#00ff87")
    with c4: kpi_card("Moy possession", f"{round(df['Poss'].mean(),1)}%" if not df.empty and 'Poss' in df.columns else "N/A", color="#ff6b6b")

    # ── SCATTER & POSSESSION ──────────────────────────────────────────────────────
    section_title("ATTAQUE VS DÉFENSE", color=color)

    col1, col2 = st.columns(2)
    with col1:
        if not dfc.empty and "GF" in dfc.columns and "GA" in dfc.columns:
            fig = px.scatter(
                dfc, x="GF", y="GA", text="Squad",
                color="Pts",
                color_continuous_scale=[
                    [0, plotly_color("#0f1420")],
                    [0.5, plotly_color(color, "88")],
                    [1, plotly_color(color)],
                ],
                hover_data=["W","D","L","Pts"],
                size_max=15,
            )
            fig.add_shape(type="line",
                          x0=dfc["GF"].min(), y0=dfc["GF"].min(),
                          x1=dfc["GF"].max(), y1=dfc["GF"].max(),
                          line=dict(color="rgba(255,255,255,0.1)", dash="dash"))
            fig.update_traces(textposition="top center", marker_size=10,
                              textfont=dict(family="Rajdhani", size=11))
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(15,20,32,0.8)",
                font_color="#ffffff", height=420,
                margin=dict(l=0,r=0,t=30,b=0),
                xaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#555", title="Buts marqués"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#555", title="Buts encaissés"),
                font=dict(family="Rajdhani"),
                title=dict(text="Buts marqués vs encaissés", font=dict(family="Bebas Neue",size=18,color=color)),
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if not df.empty and "Poss" in df.columns and "Squad" in df.columns:
            df_poss = df[["Squad","Poss"]].dropna().sort_values("Poss", ascending=True)
            fig2 = px.bar(
                df_poss, x="Poss", y="Squad", orientation="h",
                color="Poss", color_continuous_scale=[[0, plotly_color("#0f1420")],[1, plotly_color(color)]],
                text="Poss",
            )
            fig2.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(15,20,32,0.8)",
                font_color="#ffffff", height=420,
                margin=dict(l=0,r=20,t=30,b=0),
                xaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#555"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#888"),
                font=dict(family="Rajdhani"),
                title=dict(text="Possession par équipe", font=dict(family="Bebas Neue",size=18,color=color)),
            )
            fig2.update_traces(textposition="outside", textfont_size=12)
            st.plotly_chart(fig2, use_container_width=True)

    # ── HEATMAP CORRELATIONS ──────────────────────────────────────────────────────
    if not df.empty:
        num_cols = [c for c in ["Performance_Gls","Performance_Ast","Performance_G+A",
                                 "Performance_CrdY","Performance_CrdR",
                                 "Per 90 Minutes_Gls","Per 90 Minutes_Ast","Poss"] if c in df.columns]
        if len(num_cols) >= 3:
            section_title("CORRÉLATIONS", color=color)
            corr = df[num_cols].corr().round(2)
            corr.columns = [c.replace("Performance_","").replace("Per 90 Minutes_","p90_") for c in corr.columns]
            corr.index   = corr.columns
            fig3 = px.imshow(corr, text_auto=True, aspect="auto",
                             color_continuous_scale=[
                                 [0, plotly_color("#0f1420")],
                                 [0.5, plotly_color("#1a2a3a")],
                                 [1, plotly_color(color)],
                             ])
            fig3.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(15,20,32,0.8)",
                font_color="#ffffff", height=420,
                margin=dict(l=0,r=0,t=20,b=0),
                font=dict(family="Rajdhani"),
            )
            st.plotly_chart(fig3, use_container_width=True)

    # ── COMPARAISON RADAR ─────────────────────────────────────────────────────────
    section_title("COMPARAISON FACE À FACE", color=color)

    col_l1, col_l2 = st.columns(2)
    with col_l1:
        league_a = st.selectbox("Ligue A", options=list(teams.keys()),
                                format_func=lambda x: LEAGUE_LABELS.get(x,x), key="comp_league_a")
    with col_l2:
        league_b = st.selectbox("Ligue B", options=list(teams.keys()),
                                format_func=lambda x: LEAGUE_LABELS.get(x,x), key="comp_league_b",
                                index=min(1, len(teams)-1))

    df_a = teams.get(league_a, pd.DataFrame())
    df_b = teams.get(league_b, pd.DataFrame())

    if not df_a.empty and not df_b.empty:
        col_ta, col_tb = st.columns(2)
        with col_ta:
            team_a = st.selectbox("Équipe A", df_a["Squad"].dropna().tolist(), key="team_inter_a")
        with col_tb:
            team_b = st.selectbox("Équipe B", df_b["Squad"].dropna().tolist(), key="team_inter_b")

        radar_cols = [c for c in ["Performance_Gls","Performance_Ast",
                                   "Per 90 Minutes_Gls","Per 90 Minutes_Ast",
                                   "Poss","Performance_CrdY"] if c in df_a.columns and c in df_b.columns]
        radar_labels = {
            "Performance_Gls"    : "Buts",
            "Performance_Ast"    : "Passes D",
            "Per 90 Minutes_Gls" : "Buts/90",
            "Per 90 Minutes_Ast" : "Ast/90",
            "Poss"               : "Possession",
            "Performance_CrdY"   : "Cartons J",
        }
        color_a = LEAGUE_COLORS.get(league_a, "#00d4ff")
        color_b = LEAGUE_COLORS.get(league_b, "#ffd700")

        if radar_cols and team_a in df_a["Squad"].values and team_b in df_b["Squad"].values:
            row_a = df_a[df_a["Squad"] == team_a][radar_cols].iloc[0]
            row_b = df_b[df_b["Squad"] == team_b][radar_cols].iloc[0]

            logo_col_a, radar_col, logo_col_b = st.columns([1, 3, 1])

            with logo_col_a:
                st.markdown(f"<div style='text-align:center'><h4 style='color:{color_a};font-family:Bebas Neue;letter-spacing:2px'>{team_a}</h4></div>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align:center;color:#555;font-size:12px;font-family:Inter'>{LEAGUE_LABELS.get(league_a,'')}</p>", unsafe_allow_html=True)
                logo_a_b64 = get_logo_b64(get_club_logo_path(team_a))
                if logo_a_b64:
                    st.markdown(f"<div style='text-align:center'><img src='data:image/png;base64,{logo_a_b64}' style='width:100px'></div>", unsafe_allow_html=True)

            with radar_col:
                labels = [radar_labels.get(c,c) for c in radar_cols]
                fig4 = go.Figure()
                fig4.add_trace(go.Scatterpolar(
                    r=row_a.values.tolist() + [row_a.values[0]],
                    theta=labels + [labels[0]], fill="toself", name=team_a,
                    line_color=color_a, fillcolor=plotly_color(color_a, "30"),
                ))
                fig4.add_trace(go.Scatterpolar(
                    r=row_b.values.tolist() + [row_b.values[0]],
                    theta=labels + [labels[0]], fill="toself", name=team_b,
                    line_color=color_b, fillcolor=plotly_color(color_b, "30"),
                ))
                fig4.update_layout(
                    polar=dict(bgcolor="#0f1420",
                               radialaxis=dict(visible=True, color="#555", gridcolor="rgba(255,255,255,0.08)"),
                               angularaxis=dict(color="#888")),
                    paper_bgcolor="rgba(15,20,32,0.8)", font_color="#ffffff",
                    height=460, showlegend=True,
                    legend=dict(orientation="h", y=-0.08, font=dict(family="Rajdhani", size=13)),
                    font=dict(family="Rajdhani"),
                )
                st.plotly_chart(fig4, use_container_width=True)

            with logo_col_b:
                st.markdown(f"<div style='text-align:center'><h4 style='color:{color_b};font-family:Bebas Neue;letter-spacing:2px'>{team_b}</h4></div>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align:center;color:#555;font-size:12px;font-family:Inter'>{LEAGUE_LABELS.get(league_b,'')}</p>", unsafe_allow_html=True)
                logo_b_b64 = get_logo_b64(get_club_logo_path(team_b))
                if logo_b_b64:
                    st.markdown(f"<div style='text-align:center'><img src='data:image/png;base64,{logo_b_b64}' style='width:100px'></div>", unsafe_allow_html=True)

    # ── CLASSEMENT ────────────────────────────────────────────────────────────────
    if not dfc.empty:
        section_title("CLASSEMENT COMPLET", color=color)
        cols_show = [c for c in ["Rk","Squad","MP","W","D","L","GF","GA","GD","Pts","win_rate"] if c in dfc.columns]
        st.dataframe(dfc[cols_show].reset_index(drop=True), use_container_width=True)

    st.markdown("""
    <div style='margin-top:60px;padding:20px;border-top:1px solid rgba(255,255,255,0.04);text-align:center'>
        <span style='font-family:"Inter",sans-serif;font-size:11px;color:#333;
                     letter-spacing:2px;text-transform:uppercase'>
            Data source : FBref &nbsp;·&nbsp; Saison 2024-2025 &nbsp;·&nbsp; Built with Streamlit & Plotly
        </span>
    </div>
    """, unsafe_allow_html=True)


render()
