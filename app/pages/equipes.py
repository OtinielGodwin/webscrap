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
def load_data():
    teams, classements = {}, {}
    for league in LEAGUES:
        t = os.path.join(FOLDER, f"{league}_teams_clean.csv")
        c = os.path.join(FOLDER, f"{league}_classement_clean.csv")
        if os.path.exists(t):
            teams[league]       = pd.read_csv(t)
        if os.path.exists(c):
            classements[league] = pd.read_csv(c)
    return teams, classements


def kpi_card(label, value, color="#00d4ff"):
    st.markdown(f"""
    <div style='background:#1a1d27;border-radius:12px;padding:20px;
                border-left:4px solid {color};text-align:center'>
        <p style='color:#888;font-size:13px;margin:0;text-transform:uppercase;letter-spacing:1px'>{label}</p>
        <h2 style='color:{color};margin:8px 0;font-size:2rem'>{value}</h2>
    </div>
    """, unsafe_allow_html=True)


def render():
    teams, classements = load_data()

    st.markdown("""
    <div style='padding:30px 0 10px'>
        <h1 style='font-size:2.5rem;color:#00d4ff;margin:0'>Analyse des Equipes</h1>
        <p style='color:#888;font-size:1rem;margin:8px 0'>Saison 2024-2025</p>
        <hr style='border:1px solid #1a1d27;margin:20px 0'>
    </div>
    """, unsafe_allow_html=True)

    selected = st.selectbox(
        "Selectionner une competition",
        options=[l for l in LEAGUES if l in teams],
        format_func=lambda x: LEAGUE_LABELS[x],
    )

    df  = teams.get(selected, pd.DataFrame())
    dfc = classements.get(selected, pd.DataFrame())

    if df.empty:
        st.warning("Donnees non disponibles.")
        return

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Equipes",         f"{len(df)}",                                                          color="#00d4ff")
    with c2: kpi_card("Total buts",      f"{int(df['Performance_Gls'].sum()) if 'Performance_Gls' in df.columns else 'N/A'}", color="#ffd700")
    with c3: kpi_card("Moy buts/equipe", f"{round(df['Performance_Gls'].mean(), 1) if 'Performance_Gls' in df.columns else 'N/A'}", color="#00ff87")
    with c4: kpi_card("Moy possession",  f"{round(df['Poss'].mean(), 1)}%" if 'Poss' in df.columns else "N/A",  color="#ff6b6b")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # Buts marqués vs encaissés
    with col1:
        st.markdown("#### Buts marques vs encaisses")
        if not dfc.empty and "GF" in dfc.columns and "GA" in dfc.columns:
            fig = px.scatter(
                dfc, x="GF", y="GA", text="Squad",
                color="Pts", color_continuous_scale="Blues",
                hover_data=["W", "D", "L", "Pts"],
            )
            fig.add_shape(type="line", x0=dfc["GF"].min(), y0=dfc["GF"].min(),
                          x1=dfc["GF"].max(), y1=dfc["GF"].max(),
                          line=dict(color="gray", dash="dash"))
            fig.update_traces(textposition="top center", marker_size=10)
            fig.update_layout(
                plot_bgcolor="#0e1117", paper_bgcolor="#1a1d27",
                font_color="#ffffff", height=400,
                xaxis_title="Buts marques", yaxis_title="Buts encaisses",
            )
            st.plotly_chart(fig, use_container_width=True)

    # Possession moyenne
    with col2:
        st.markdown("#### Possession par equipe")
        if "Poss" in df.columns and "Squad" in df.columns:
            df_poss = df[["Squad", "Poss"]].dropna().sort_values("Poss", ascending=True)
            fig2 = px.bar(
                df_poss, x="Poss", y="Squad", orientation="h",
                color="Poss", color_continuous_scale="Blues",
                text="Poss",
            )
            fig2.update_layout(
                plot_bgcolor="#0e1117", paper_bgcolor="#1a1d27",
                font_color="#ffffff", height=400,
            )
            fig2.update_traces(textposition="outside")
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Heatmap correlations
    st.markdown("#### Heatmap des correlations")
    num_cols = [c for c in ["Performance_Gls", "Performance_Ast", "Performance_G+A",
                             "Performance_CrdY", "Performance_CrdR",
                             "Per 90 Minutes_Gls", "Per 90 Minutes_Ast", "Poss"] if c in df.columns]
    if len(num_cols) >= 3:
        corr = df[num_cols].corr().round(2)
        fig3 = px.imshow(
            corr, text_auto=True, aspect="auto",
            color_continuous_scale="RdBu_r",
        )
        fig3.update_layout(
            plot_bgcolor="#0e1117", paper_bgcolor="#1a1d27",
            font_color="#ffffff", height=450,
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Radar chart comparaison équipes
    st.markdown("#### Comparaison radar — deux equipes")
    st.markdown("Comparaison entre équipes de ligues différentes")
    
    # Comparaison entre ligues
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        league_a = st.selectbox("Ligue A", options=list(teams.keys()),
                               format_func=lambda x: LEAGUE_LABELS.get(x, x),
                               key="comp_league_a")
    with col_l2:
        league_b = st.selectbox("Ligue B", options=list(teams.keys()),
                               format_func=lambda x: LEAGUE_LABELS.get(x, x),
                               key="comp_league_b",
                               index=min(1, len(teams)-1))
    
    df_a = teams.get(league_a, pd.DataFrame())
    df_b = teams.get(league_b, pd.DataFrame())
    
    if not df_a.empty and not df_b.empty and "Squad" in df_a.columns and "Squad" in df_b.columns:
        squads_a = df_a["Squad"].dropna().tolist()
        squads_b = df_b["Squad"].dropna().tolist()
        
        col_ta, col_tb = st.columns(2)
        with col_ta:
            team_a = st.selectbox("Équipe A", squads_a, key="team_inter_a")
        with col_tb:
            team_b = st.selectbox("Équipe B", squads_b, key="team_inter_b")
        
        radar_cols = [c for c in ["Performance_Gls", "Performance_Ast",
                                   "Per 90 Minutes_Gls", "Per 90 Minutes_Ast",
                                   "Poss", "Performance_CrdY"] if c in df_a.columns and c in df_b.columns]
        radar_labels = {
            "Performance_Gls"     : "Buts",
            "Performance_Ast"     : "Passes D",
            "Per 90 Minutes_Gls"  : "Buts/90",
            "Per 90 Minutes_Ast"  : "Ast/90",
            "Poss"                : "Possession",
            "Performance_CrdY"    : "Cartons J",
        }
        
        if radar_cols:
            row_a = df_a[df_a["Squad"] == team_a][radar_cols].iloc[0] if team_a in df_a["Squad"].values else None
            row_b = df_b[df_b["Squad"] == team_b][radar_cols].iloc[0] if team_b in df_b["Squad"].values else None
            
            if row_a is not None and row_b is not None:
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Afficher les logos des clubs et ligues
                logo_col_a, radar_col, logo_col_b = st.columns([1, 3, 1])
                with logo_col_a:
                    st.markdown(f"<div style='text-align:center'><h5 style='color:#00d4ff'>{team_a}</h5></div>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align:center;color:#888;font-size:12px'>{LEAGUE_LABELS.get(league_a, league_a)}</p>", unsafe_allow_html=True)
                    logo_a = get_club_logo_path(team_a)
                    if logo_a:
                        st.image(logo_a, width=120)
                    else:
                        st.markdown("<div style='text-align:center;color:#888'>Pas de logo</div>", unsafe_allow_html=True)
                
                with radar_col:
                    labels = [radar_labels.get(c, c) for c in radar_cols]
                    fig4 = go.Figure()
                    fig4.add_trace(go.Scatterpolar(
                        r=row_a.values.tolist() + [row_a.values[0]],
                        theta=labels + [labels[0]],
                        fill="toself", name=team_a,
                        line_color="#00d4ff", fillcolor="rgba(0,212,255,0.2)",
                    ))
                    fig4.add_trace(go.Scatterpolar(
                        r=row_b.values.tolist() + [row_b.values[0]],
                        theta=labels + [labels[0]],
                        fill="toself", name=team_b,
                        line_color="#ffd700", fillcolor="rgba(255,215,0,0.2)",
                    ))
                    fig4.update_layout(
                        polar=dict(bgcolor="#1a1d27",
                                   radialaxis=dict(visible=True, color="#888")),
                        paper_bgcolor="#0e1117", font_color="#ffffff",
                        height=500, showlegend=True,
                        legend=dict(orientation="v", x=1.05)
                    )
                    st.plotly_chart(fig4, use_container_width=True)
                
                with logo_col_b:
                    st.markdown(f"<div style='text-align:center'><h5 style='color:#ffd700'>{team_b}</h5></div>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align:center;color:#888;font-size:12px'>{LEAGUE_LABELS.get(league_b, league_b)}</p>", unsafe_allow_html=True)
                    logo_b = get_club_logo_path(team_b)
                    if logo_b:
                        st.image(logo_b, width=120)
                    else:
                        st.markdown("<div style='text-align:center;color:#888'>Pas de logo</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Classement complet
    if not dfc.empty:
        st.markdown("#### Classement complet")
        cols_show = [c for c in ["Rk", "Squad", "MP", "W", "D", "L", "GF", "GA", "GD", "Pts", "win_rate"] if c in dfc.columns]
        st.dataframe(dfc[cols_show].reset_index(drop=True), use_container_width=True)

    st.markdown("""
    <hr style='border:1px solid #1a1d27;margin-top:40px'>
    <p style='text-align:center;color:#444;font-size:12px'>
        Data source : FBref · Saison 2024-2025 · Built with Streamlit & Plotly
    </p>
    """, unsafe_allow_html=True)


render()