import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from config.clubs import get_club_logo_path, get_league_logo_path

LEAGUES = ["ligue1", "premier", "laliga", "bundesliga", "seriea"]
LEAGUE_LABELS = {
    "ligue1"     : "Ligue 1",
    "premier"    : "Premier League",
    "laliga"     : "La Liga",
    "bundesliga" : "Bundesliga",
    "seriea"     : "Serie A",
}

FOLDER = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")
IMAGES = os.path.join(os.path.dirname(__file__), "..", "..", "data", "images", "players")

RADAR_COLS = [
    "Performance_Gls", "Performance_Ast",
    "Per 90 Minutes_Gls", "Per 90 Minutes_Ast",
    "Playing Time_MP", "Performance_CrdY",
]

RADAR_LABELS = {
    "Performance_Gls"    : "Buts",
    "Performance_Ast"    : "Passes D",
    "Per 90 Minutes_Gls" : "Buts/90",
    "Per 90 Minutes_Ast" : "Ast/90",
    "Playing Time_MP"    : "Matchs",
    "Performance_CrdY"   : "Cartons J",
}

POS_HEATMAP = {
    "GK" : {"cx": 50, "cy": 95, "sx": 15, "sy": 8},
    "DF" : {"cx": 50, "cy": 80, "sx": 30, "sy": 12},
    "MF" : {"cx": 50, "cy": 50, "sx": 30, "sy": 20},
    "FW" : {"cx": 50, "cy": 22, "sx": 25, "sy": 15},
}


@st.cache_data
def load_players():
    dfs = {}
    for league in LEAGUES:
        path = os.path.join(FOLDER, f"{league}_players_standard_clean.csv")
        if os.path.exists(path):
            dfs[league] = pd.read_csv(path)
    return dfs


def normalize_series(s: pd.Series) -> pd.Series:
    mn, mx = s.min(), s.max()
    if mx == mn:
        return pd.Series([50.0] * len(s), index=s.index)
    return (s - mn) / (mx - mn) * 100


def get_pos_key(pos: str) -> str:
    pos = str(pos).upper()
    for key in ["GK", "DF", "MF", "FW"]:
        if key in pos:
            return key
    return "MF"


def get_player_image(player_id: str):
    if not player_id or str(player_id) == "nan":
        return None
    if not os.path.exists(IMAGES):
        return None
    for f in os.listdir(IMAGES):
        if f.startswith(str(player_id)):
            return os.path.join(IMAGES, f)
    return None


def draw_terrain_heatmap(pos: str):
    pos_key = get_pos_key(pos)
    zone    = POS_HEATMAP[pos_key]

    x  = np.linspace(0, 100, 200)
    y  = np.linspace(0, 100, 200)
    xx, yy = np.meshgrid(x, y)
    zz = np.exp(
        -((xx - zone["cx"])**2 / (2 * zone["sx"]**2) +
          (yy - zone["cy"])**2 / (2 * zone["sy"]**2))
    )

    fig = go.Figure()
    fig.add_trace(go.Heatmap(
        z=zz, x=x, y=y,
        colorscale=[[0, "rgba(0,0,0,0)"], [0.3, "rgba(0,212,255,0.1)"],
                    [0.7, "rgba(0,212,255,0.5)"], [1, "rgba(0,212,255,0.9)"]],
        showscale=False, zmin=0, zmax=1,
    ))

    shapes = [
        dict(type="rect",   x0=0,  y0=0,  x1=100, y1=100, line=dict(color="white", width=2)),
        dict(type="line",   x0=0,  y0=50, x1=100, y1=50,  line=dict(color="white", width=1)),
        dict(type="rect",   x0=20, y0=0,  x1=80,  y1=18,  line=dict(color="white", width=1)),
        dict(type="rect",   x0=20, y0=82, x1=80,  y1=100, line=dict(color="white", width=1)),
        dict(type="rect",   x0=35, y0=0,  x1=65,  y1=8,   line=dict(color="white", width=1)),
        dict(type="rect",   x0=35, y0=92, x1=65,  y1=100, line=dict(color="white", width=1)),
        dict(type="circle", x0=38, y0=38, x1=62,  y1=62,  line=dict(color="white", width=1)),
    ]
    fig.update_layout(
        shapes=shapes,
        plot_bgcolor="#2d5a27", paper_bgcolor="#0e1117",
        height=320,
        xaxis=dict(visible=False, range=[0, 100]),
        yaxis=dict(visible=False, range=[0, 100], scaleanchor="x", scaleratio=1.5),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    return fig


def kpi_card(label, value, color="#00d4ff"):
    st.markdown(f"""
    <div style='background:#1a1d27;border-radius:12px;padding:16px;
                border-left:4px solid {color};text-align:center'>
        <p style='color:#888;font-size:11px;margin:0;text-transform:uppercase;letter-spacing:1px'>{label}</p>
        <h3 style='color:{color};margin:6px 0;font-size:1.5rem'>{value}</h3>
    </div>
    """, unsafe_allow_html=True)


def player_card(row: pd.Series, league: str):
    player_id = str(row.get("player_id", ""))
    img_path  = get_player_image(player_id)
    club_name = row.get("Squad", "")
    logo_path = get_club_logo_path(club_name)
    league_logo = get_league_logo_path(league)

    col_img, col_info = st.columns([1, 3])

    with col_img:
        if img_path:
            st.image(img_path, width=150)
        else:
            st.markdown("""
            <div style='width:150px;height:150px;background:#1a1d27;border-radius:50%;
                        display:flex;align-items:center;justify-content:center;
                        border:3px solid #00d4ff;font-size:3rem;color:#00d4ff'>
                ?
            </div>
            """, unsafe_allow_html=True)

    with col_info:
        col_name, col_logo = st.columns([4, 1])
        with col_name:
            st.markdown(f"""
            <div style='background:#1a1d27;border-radius:12px;padding:16px;border-left:4px solid #00d4ff'>
                <h2 style='color:#ffffff;margin:0 0 8px'>{row.get("Player","")}</h2>
                <p style='color:#888;margin:2px 0;font-size:14px'>
                    {club_name} · {LEAGUE_LABELS.get(league, league)}
                </p>
                <p style='color:#888;margin:2px 0;font-size:14px'>
                    Poste : <span style='color:#00d4ff'>{row.get("Pos","")}</span> &nbsp;·&nbsp;
                    Age : <span style='color:#00d4ff'>{row.get("Age","")}</span> &nbsp;·&nbsp;
                    Nationalite : <span style='color:#00d4ff'>{row.get("Nation","")}</span>
                </p>
            </div>
            """, unsafe_allow_html=True)
        with col_logo:
            # afficher logo de club puis logo de ligue si disponible
            if logo_path:
                st.image(logo_path, width=70)
            if league_logo:
                st.image(league_logo, width=50)


def render():
    players = load_players()

    st.markdown("""
    <div style='padding:30px 0 10px'>
        <h1 style='font-size:2.5rem;color:#00d4ff;margin:0'>Analyse des Joueurs</h1>
        <p style='color:#888;font-size:1rem;margin:8px 0'>Saison 2024-2025</p>
        <hr style='border:1px solid #1a1d27;margin:20px 0'>
    </div>
    """, unsafe_allow_html=True)

    selected = st.selectbox(
        "Selectionner une ligue",
        options=list(players.keys()),
        format_func=lambda x: LEAGUE_LABELS.get(x, x),
    )

    # afficher le logo de la ligue sélectionnée dans la barre latérale
    logo_ligue = get_league_logo_path(selected)
    if logo_ligue:
        st.sidebar.image(logo_ligue, width=80)

    # ajouter le logo de la ligue au niveau de la vue générale (sous le titre)
    if logo_ligue:
        st.image(logo_ligue, width=100)

    df = players.get(selected, pd.DataFrame())

    if df.empty:
        st.warning("Donnees non disponibles.")
        return

    radar_cols = [c for c in RADAR_COLS if c in df.columns]

    df_norm = df.copy()
    for col in radar_cols:
        df_norm[col + "_norm"] = normalize_series(df[col].fillna(0))

    tabs = st.tabs(["Vue generale", "Fiche joueur", "Comparaison", "Inter-ligues"])

    # ── Tab 1 : Vue generale ──────────────────────────────────────────────────────
    with tabs[0]:
        total_players = len(df)
        total_goals   = int(df["Performance_Gls"].sum()) if "Performance_Gls" in df.columns else 0
        total_ast     = int(df["Performance_Ast"].sum()) if "Performance_Ast" in df.columns else 0
        top_scorer    = df.nlargest(1, "Performance_Gls").iloc[0]["Player"] if "Performance_Gls" in df.columns else "N/A"

        c1, c2, c3, c4 = st.columns(4)
        with c1: kpi_card("Joueurs",        str(total_players), color="#00d4ff")
        with c2: kpi_card("Buts",           str(total_goals),   color="#ffd700")
        with c3: kpi_card("Passes D",       str(total_ast),     color="#00ff87")
        with c4: kpi_card("Meilleur buteur",top_scorer,         color="#ff6b6b")

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Buts vs Passes decisives")
            if "Performance_Gls" in df.columns and "Performance_Ast" in df.columns:
                fig = px.scatter(
                    df.dropna(subset=["Performance_Gls", "Performance_Ast"]),
                    x="Performance_Gls", y="Performance_Ast",
                    hover_name="Player",
                    color="Pos" if "Pos" in df.columns else None,
                    hover_data=["Squad"],
                    color_discrete_sequence=px.colors.qualitative.Bold,
                )
                fig.update_layout(
                    plot_bgcolor="#0e1117", paper_bgcolor="#1a1d27",
                    font_color="#ffffff", height=400,
                    xaxis_title="Buts", yaxis_title="Passes decisives",
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Minutes jouees par poste")
            if "Playing Time_Min" in df.columns and "Pos" in df.columns:
                fig2 = px.violin(
                    df.dropna(subset=["Playing Time_Min", "Pos"]),
                    x="Pos", y="Playing Time_Min",
                    color="Pos", box=True,
                    color_discrete_sequence=px.colors.qualitative.Bold,
                )
                fig2.update_layout(
                    plot_bgcolor="#0e1117", paper_bgcolor="#1a1d27",
                    font_color="#ffffff", height=400,
                    xaxis_title="Poste", yaxis_title="Minutes",
                    showlegend=False,
                )
                st.plotly_chart(fig2, use_container_width=True)

        st.markdown("#### Top 15 scoreurs")
        if "Performance_Gls" in df.columns:
            top15 = df.nlargest(15, "Performance_Gls")[
                ["Player", "Squad", "Pos", "Performance_Gls", "Performance_Ast"]
            ].reset_index(drop=True)
            top15.index += 1
            fig3 = px.bar(
                top15.sort_values("Performance_Gls"),
                x="Performance_Gls", y="Player",
                orientation="h", color="Performance_Gls",
                color_continuous_scale="Blues", text="Performance_Gls",
                hover_data=["Squad", "Performance_Ast"],
            )
            fig3.update_layout(
                plot_bgcolor="#0e1117", paper_bgcolor="#1a1d27",
                font_color="#ffffff", height=500, showlegend=False,
            )
            fig3.update_traces(textposition="outside")
            st.plotly_chart(fig3, use_container_width=True)

        st.markdown("#### Carte des nationalites")
        if "Nation" in df.columns:
            nat_counts = df["Nation"].value_counts().reset_index()
            nat_counts.columns = ["Nation", "Count"]
            fig4 = px.choropleth(
                nat_counts, locations="Nation",
                locationmode="ISO-3", color="Count",
                color_continuous_scale="Blues",
            )
            fig4.update_layout(
                plot_bgcolor="#0e1117", paper_bgcolor="#1a1d27",
                font_color="#ffffff", height=400,
                geo=dict(bgcolor="#0e1117", showframe=False),
            )
            st.plotly_chart(fig4, use_container_width=True)

    # ── Tab 2 : Fiche joueur ──────────────────────────────────────────────────────
    with tabs[1]:
        players_list    = df["Player"].dropna().sort_values().tolist() if "Player" in df.columns else []
        selected_player = st.selectbox("Selectionner un joueur", players_list)

        if selected_player:
            row = df[df["Player"] == selected_player].iloc[0]
            player_card(row, selected)
            st.markdown("<br>", unsafe_allow_html=True)

            col_stats, col_terrain = st.columns([2, 1])

            with col_stats:
                st.markdown("#### Stats cles")
                s1, s2, s3 = st.columns(3)
                with s1: kpi_card("Buts",     str(int(row.get("Performance_Gls", 0) or 0)),           color="#ffd700")
                with s2: kpi_card("Passes D", str(int(row.get("Performance_Ast", 0) or 0)),           color="#00d4ff")
                with s3: kpi_card("Matchs",   str(int(row.get("Playing Time_MP", 0) or 0)),           color="#00ff87")

                s4, s5, s6 = st.columns(3)
                with s4: kpi_card("Buts/90",  str(round(row.get("Per 90 Minutes_Gls", 0) or 0, 2)), color="#ff6b6b")
                with s5: kpi_card("Ast/90",   str(round(row.get("Per 90 Minutes_Ast", 0) or 0, 2)), color="#a78bfa")
                with s6: kpi_card("Minutes",  str(int(row.get("Playing Time_Min", 0) or 0)),         color="#ffd700")

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### Profil radar")

                norm_cols = [c + "_norm" for c in radar_cols]
                if all(c in df_norm.columns for c in norm_cols):
                    row_norm = df_norm[df_norm["Player"] == selected_player][norm_cols].iloc[0]
                    labels   = [RADAR_LABELS.get(c, c) for c in radar_cols]
                    vals     = row_norm.values.tolist()

                    fig_r = go.Figure()
                    fig_r.add_trace(go.Scatterpolar(
                        r=vals + [vals[0]],
                        theta=labels + [labels[0]],
                        fill="toself", name=selected_player,
                        line_color="#00d4ff",
                        fillcolor="rgba(0,212,255,0.2)",
                    ))
                    fig_r.update_layout(
                        polar=dict(
                            bgcolor="#1a1d27",
                            radialaxis=dict(visible=True, range=[0, 100], color="#888"),
                        ),
                        paper_bgcolor="#0e1117", font_color="#ffffff",
                        height=400, showlegend=False,
                    )
                    st.plotly_chart(fig_r, use_container_width=True)

            with col_terrain:
                st.markdown("#### Zone d'action")
                pos   = str(row.get("Pos", "MF"))
                fig_t = draw_terrain_heatmap(pos)
                st.plotly_chart(fig_t, use_container_width=True)
                pos_key  = get_pos_key(pos)
                pos_desc = {"GK": "Gardien", "DF": "Defenseur", "MF": "Milieu", "FW": "Attaquant"}
                st.markdown(f"<p style='text-align:center;color:#888;font-size:13px'>{pos_desc.get(pos_key, pos)}</p>", unsafe_allow_html=True)

    # ── Tab 3 : Comparaison (meme ligue) ─────────────────────────────────────────
    with tabs[2]:
        st.markdown("### Comparaison face a face")
        players_list = df["Player"].dropna().sort_values().tolist() if "Player" in df.columns else []

        col_a, col_b = st.columns(2)
        with col_a:
            player_a = st.selectbox("Joueur A", players_list, index=0, key="cmp_a")
        with col_b:
            player_b = st.selectbox("Joueur B", players_list, index=min(1, len(players_list)-1), key="cmp_b")

        if player_a and player_b and radar_cols:
            norm_cols = [c + "_norm" for c in radar_cols]
            labels    = [RADAR_LABELS.get(c, c) for c in radar_cols]
            row_a     = df_norm[df_norm["Player"] == player_a].iloc[0]
            row_b     = df_norm[df_norm["Player"] == player_b].iloc[0]

            card_a, card_b = st.columns(2)
            with card_a: player_card(df[df["Player"] == player_a].iloc[0], selected)
            with card_b: player_card(df[df["Player"] == player_b].iloc[0], selected)

            st.markdown("<br>", unsafe_allow_html=True)

            vals_a = row_a[norm_cols].values.tolist()
            vals_b = row_b[norm_cols].values.tolist()

            fig_cmp = go.Figure()
            fig_cmp.add_trace(go.Scatterpolar(
                r=vals_a + [vals_a[0]], theta=labels + [labels[0]],
                fill="toself", name=player_a,
                line_color="#00d4ff", fillcolor="rgba(0,212,255,0.15)",
            ))
            fig_cmp.add_trace(go.Scatterpolar(
                r=vals_b + [vals_b[0]], theta=labels + [labels[0]],
                fill="toself", name=player_b,
                line_color="#ffd700", fillcolor="rgba(255,215,0,0.15)",
            ))
            fig_cmp.update_layout(
                polar=dict(bgcolor="#1a1d27",
                           radialaxis=dict(visible=True, range=[0, 100], color="#888")),
                paper_bgcolor="#0e1117", font_color="#ffffff",
                height=500, showlegend=True,
                legend=dict(orientation="h", y=-0.1),
            )
            st.plotly_chart(fig_cmp, use_container_width=True)

            st.markdown("#### Stats brutes")
            raw_cols = [c for c in [
                "Performance_Gls", "Performance_Ast", "Performance_G+A",
                "Per 90 Minutes_Gls", "Per 90 Minutes_Ast",
                "Playing Time_MP", "Playing Time_Min", "Performance_CrdY",
            ] if c in df.columns]

            raw_a   = df[df["Player"] == player_a][raw_cols].iloc[0]
            raw_b   = df[df["Player"] == player_b][raw_cols].iloc[0]
            comp_df = pd.DataFrame({
                "Stat"  : [RADAR_LABELS.get(c, c) for c in raw_cols],
                player_a: raw_a.values,
                player_b: raw_b.values,
            })
            st.dataframe(comp_df.set_index("Stat"), use_container_width=True)

    # ── Tab 4 : Comparaison inter-ligues ─────────────────────────────────────────
    with tabs[3]:
        st.markdown("### Comparaison inter-ligues")

        col_l1, col_l2 = st.columns(2)
        with col_l1:
            league_a = st.selectbox(
                "Ligue A", options=list(players.keys()),
                format_func=lambda x: LEAGUE_LABELS.get(x, x),
                key="inter_league_a",
            )
        with col_l2:
            league_b = st.selectbox(
                "Ligue B", options=list(players.keys()),
                format_func=lambda x: LEAGUE_LABELS.get(x, x),
                key="inter_league_b",
                index=min(1, len(players)-1),
            )

        df_a = players.get(league_a, pd.DataFrame())
        df_b = players.get(league_b, pd.DataFrame())

        if df_a.empty or df_b.empty:
            st.warning("Donnees non disponibles pour une des ligues.")
        else:
            radar_cols_a = [c for c in RADAR_COLS if c in df_a.columns]
            radar_cols_b = [c for c in RADAR_COLS if c in df_b.columns]
            common_cols  = [c for c in radar_cols_a if c in radar_cols_b]

            df_a_norm = df_a.copy()
            df_b_norm = df_b.copy()
            for col in common_cols:
                df_a_norm[col + "_norm"] = normalize_series(df_a_norm[col].fillna(0))
                df_b_norm[col + "_norm"] = normalize_series(df_b_norm[col].fillna(0))

            col_pa, col_pb = st.columns(2)
            with col_pa:
                inter_a = st.selectbox("Joueur A", df_a["Player"].dropna().sort_values().tolist(), key="inter_player_a")
            with col_pb:
                inter_b = st.selectbox("Joueur B", df_b["Player"].dropna().sort_values().tolist(), key="inter_player_b")

            if inter_a and inter_b:
                row_ia = df_a[df_a["Player"] == inter_a].iloc[0]
                row_ib = df_b[df_b["Player"] == inter_b].iloc[0]

                card_ia, card_ib = st.columns(2)
                with card_ia: player_card(row_ia, league_a)
                with card_ib: player_card(row_ib, league_b)

                st.markdown("<br>", unsafe_allow_html=True)

                norm_cols = [c + "_norm" for c in common_cols]
                labels    = [RADAR_LABELS.get(c, c) for c in common_cols]

                row_ia_norm = df_a_norm[df_a_norm["Player"] == inter_a]
                row_ib_norm = df_b_norm[df_b_norm["Player"] == inter_b]

                if not row_ia_norm.empty and not row_ib_norm.empty:
                    vals_ia = row_ia_norm[norm_cols].iloc[0].values.tolist()
                    vals_ib = row_ib_norm[norm_cols].iloc[0].values.tolist()

                    fig_inter = go.Figure()
                    fig_inter.add_trace(go.Scatterpolar(
                        r=vals_ia + [vals_ia[0]], theta=labels + [labels[0]],
                        fill="toself",
                        name=f"{inter_a} ({LEAGUE_LABELS.get(league_a, league_a)})",
                        line_color="#00d4ff", fillcolor="rgba(0,212,255,0.15)",
                    ))
                    fig_inter.add_trace(go.Scatterpolar(
                        r=vals_ib + [vals_ib[0]], theta=labels + [labels[0]],
                        fill="toself",
                        name=f"{inter_b} ({LEAGUE_LABELS.get(league_b, league_b)})",
                        line_color="#ffd700", fillcolor="rgba(255,215,0,0.15)",
                    ))
                    fig_inter.update_layout(
                        polar=dict(bgcolor="#1a1d27",
                                   radialaxis=dict(visible=True, range=[0, 100], color="#888")),
                        paper_bgcolor="#0e1117", font_color="#ffffff",
                        height=500, showlegend=True,
                        legend=dict(orientation="h", y=-0.1),
                    )
                    st.plotly_chart(fig_inter, use_container_width=True)

                st.markdown("#### Stats brutes comparees")
                raw_cols = [c for c in [
                    "Performance_Gls", "Performance_Ast", "Performance_G+A",
                    "Per 90 Minutes_Gls", "Per 90 Minutes_Ast",
                    "Playing Time_MP", "Playing Time_Min", "Performance_CrdY",
                ] if c in df_a.columns and c in df_b.columns]

                raw_ia  = df_a[df_a["Player"] == inter_a][raw_cols].iloc[0]
                raw_ib  = df_b[df_b["Player"] == inter_b][raw_cols].iloc[0]
                comp_df = pd.DataFrame({
                    "Stat"  : [RADAR_LABELS.get(c, c) for c in raw_cols],
                    inter_a : raw_ia.values,
                    inter_b : raw_ib.values,
                })
                st.dataframe(comp_df.set_index("Stat"), use_container_width=True)

    st.markdown("""
    <hr style='border:1px solid #1a1d27;margin-top:40px'>
    <p style='text-align:center;color:#444;font-size:12px'>
        Data source : FBref · Saison 2024-2025 · Built with Streamlit & Plotly
    </p>
    """, unsafe_allow_html=True)


render()