import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
import base64
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from config.clubs import get_league_logo_path
from app.utils import plotly_color

LEAGUES = ["ligue1", "premier", "laliga", "bundesliga", "seriea"]
LEAGUE_LABELS = {
    "ligue1"     : "Ligue 1",
    "premier"    : "Premier League",
    "laliga"     : "La Liga",
    "bundesliga" : "Bundesliga",
    "seriea"     : "Serie A",
}
LEAGUE_COLORS = {
    "ligue1"     : "#00d4ff",
    "premier"    : "#ff6b35",
    "laliga"     : "#ff3b5c",
    "bundesliga" : "#e8002d",
    "seriea"     : "#0066cc",
}
FOLDER = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")


@st.cache_data
def load_data():
    players, matches = {}, {}
    for league in LEAGUES:
        p = os.path.join(FOLDER, f"{league}_players_standard_clean.csv")
        m = os.path.join(FOLDER, f"{league}_matches_clean.csv")
        if os.path.exists(p): players[league] = pd.read_csv(p)
        if os.path.exists(m): matches[league] = pd.read_csv(m)
    return players, matches


def get_logo_b64(league):
    path = get_league_logo_path(league)
    if path and os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def kpi_card(label, value, color="#00ff87"):
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


def section_title(title, color="#00ff87"):
    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:12px;margin:28px 0 16px'>
        <div style='width:4px;height:24px;background:linear-gradient({color},transparent);border-radius:2px'></div>
        <span style='font-family:"Bebas Neue",sans-serif;font-size:1.4rem;letter-spacing:2px;color:{color}'>{title}</span>
        <div style='flex:1;height:1px;background:linear-gradient(90deg,rgba(255,255,255,0.05),transparent)'></div>
    </div>
    """, unsafe_allow_html=True)


def render():
    players, matches = load_data()

    # ── HEADER ───────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style='display:flex;align-items:center;gap:20px;padding:28px 32px;
                background:linear-gradient(135deg,rgba(0,255,135,0.06),rgba(0,0,0,0.4));
                border-radius:16px;border:1px solid rgba(0,255,135,0.1);
                border-left:4px solid #00ff87;margin-bottom:28px;position:relative;overflow:hidden'>
        <div style='position:absolute;top:0;left:0;right:0;bottom:0;
                    background:linear-gradient(135deg,rgba(0,255,135,0.03),transparent 60%);pointer-events:none'></div>
        <div style='font-size:3rem;line-height:1'>🤖</div>
        <div>
            <div style='font-family:"Bebas Neue",sans-serif;font-size:2.4rem;letter-spacing:3px;line-height:1;
                        background:linear-gradient(135deg,#00ff87,#ffffff);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text'>
                ML ANALYTICS
            </div>
            <div style='font-family:"Inter",sans-serif;font-size:13px;color:#555;margin-top:4px;letter-spacing:1px'>
                CLUSTERING · PRÉDICTION · ANALYSE AVANCÉE
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Clustering joueurs", "Prédiction de matchs"])

    # ── TAB 1 : CLUSTERING ────────────────────────────────────────────────────────
    with tab1:
        section_title("CLUSTERING PAR PROFIL (K-MEANS)", color="#00ff87")

        selected = st.selectbox(
            "Ligue",
            options=list(players.keys()),
            format_func=lambda x: LEAGUE_LABELS.get(x, x),
        )

        color    = LEAGUE_COLORS.get(selected, "#00d4ff")
        logo_b64 = get_logo_b64(selected)
        if logo_b64:
            st.image(f"data:image/png;base64,{logo_b64}", width=50)

        df = players.get(selected, pd.DataFrame())
        feature_cols = [c for c in [
            "Performance_Gls", "Performance_Ast", "Performance_G+A",
            "Per 90 Minutes_Gls", "Per 90 Minutes_Ast",
            "Playing Time_MP", "Playing Time_Min", "Performance_CrdY",
        ] if c in df.columns]

        if len(feature_cols) < 3:
            st.warning("Pas assez de colonnes pour le clustering.")
        else:
            df_ml      = df.dropna(subset=feature_cols).copy()
            n_clusters = st.slider("Nombre de clusters", 2, 8, 4)

            scaler           = StandardScaler()
            X_scaled         = scaler.fit_transform(df_ml[feature_cols])
            kmeans           = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            df_ml["Cluster"] = kmeans.fit_predict(X_scaled).astype(str)

            pca          = PCA(n_components=2)
            coords       = pca.fit_transform(X_scaled)
            df_ml["PCA_1"] = coords[:, 0]
            df_ml["PCA_2"] = coords[:, 1]

            col1, col2 = st.columns(2)
            with col1:
                fig = px.scatter(
                    df_ml, x="PCA_1", y="PCA_2",
                    color="Cluster",
                    hover_name="Player" if "Player" in df_ml.columns else None,
                    hover_data=["Squad", "Performance_Gls"] if "Squad" in df_ml.columns else None,
                    color_discrete_sequence=px.colors.qualitative.Bold,
                )
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(15,20,32,0.8)",
                    font_color="#ffffff", height=440,
                    margin=dict(l=0, r=0, t=30, b=0),
                    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#555"),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#555"),
                    font=dict(family="Rajdhani"),
                    title=dict(text="Visualisation PCA", font=dict(family="Bebas Neue", size=18, color="#00ff87")),
                    legend=dict(font=dict(family="Rajdhani")),
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                cluster_means = df_ml.groupby("Cluster")[feature_cols].mean().round(2)
                labels_short  = {
                    "Performance_Gls"    : "Buts",
                    "Performance_Ast"    : "Passes D",
                    "Performance_G+A"    : "G+A",
                    "Per 90 Minutes_Gls" : "Buts/90",
                    "Per 90 Minutes_Ast" : "Ast/90",
                    "Playing Time_MP"    : "Matchs",
                    "Playing Time_Min"   : "Minutes",
                    "Performance_CrdY"   : "Cartons J",
                }
                cluster_means.columns = [labels_short.get(c, c) for c in cluster_means.columns]
                fig2 = px.imshow(
                    cluster_means, text_auto=True, aspect="auto",
                    color_continuous_scale=[
                        [0,   plotly_color("#0f1420")],
                        [0.5, plotly_color("#1a3a2a")],
                        [1,   plotly_color("#00ff87")],
                    ],
                )
                fig2.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(15,20,32,0.8)",
                    font_color="#ffffff", height=440,
                    margin=dict(l=0, r=0, t=30, b=0),
                    font=dict(family="Rajdhani"),
                    title=dict(text="Profil moyen par cluster", font=dict(family="Bebas Neue", size=18, color="#00ff87")),
                )
                st.plotly_chart(fig2, use_container_width=True)

            section_title("TOP JOUEURS PAR CLUSTER", color="#00ff87")
            for cluster_id in sorted(df_ml["Cluster"].unique()):
                with st.expander(f"Cluster {cluster_id}"):
                    cluster_df = df_ml[df_ml["Cluster"] == cluster_id]
                    show_cols  = [c for c in ["Player", "Squad", "Pos", "Performance_Gls", "Performance_Ast", "Playing Time_MP"] if c in cluster_df.columns]
                    st.dataframe(
                        cluster_df[show_cols].sort_values("Performance_Gls", ascending=False).head(10).reset_index(drop=True),
                        use_container_width=True,
                    )

    # ── TAB 2 : PREDICTION ────────────────────────────────────────────────────────
    with tab2:
        section_title("PRÉDICTION DE RÉSULTAT (RANDOM FOREST)", color="#00ff87")

        selected_m = st.selectbox(
            "Ligue",
            options=list(matches.keys()),
            format_func=lambda x: LEAGUE_LABELS.get(x, x),
            key="ml_league",
        )

        df_m      = matches.get(selected_m, pd.DataFrame())
        feature_m = [c for c in ["home_score", "away_score", "total_goals", "Attendance"] if c in df_m.columns]

        if "result" not in df_m.columns or len(feature_m) < 2:
            st.warning("Données insuffisantes pour la prédiction.")
        else:
            df_m = df_m.dropna(subset=feature_m + ["result"]).copy()
            X    = df_m[feature_m]
            y    = df_m["result"]

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            model    = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            y_pred   = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)

            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#0f1420,#131825);border-radius:12px;
                        padding:20px 24px;border:1px solid rgba(255,255,255,0.04);
                        border-left:4px solid #00ff87;margin-bottom:24px;display:flex;align-items:center;gap:20px'>
                <div>
                    <p style='color:#555;font-size:10px;margin:0;text-transform:uppercase;
                              letter-spacing:2px;font-family:"Inter"'>Accuracy du modèle</p>
                    <h1 style='color:#00ff87;margin:4px 0 0;font-family:"Bebas Neue";
                               font-size:3rem;letter-spacing:3px;line-height:1'>
                        {round(accuracy * 100, 1)}%
                    </h1>
                </div>
                <div style='color:#555;font-size:13px;font-family:"Inter"'>
                    Entraîné sur {len(X_train)} matchs<br>
                    Testé sur {len(X_test)} matchs
                </div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                importance_df = pd.DataFrame({
                    "Feature"    : feature_m,
                    "Importance" : model.feature_importances_,
                }).sort_values("Importance", ascending=True)
                fig3 = px.bar(
                    importance_df, x="Importance", y="Feature", orientation="h",
                    color="Importance",
                    color_continuous_scale=[
                        [0, plotly_color("#0f1420")],
                        [1, plotly_color("#00ff87")],
                    ],
                    text=importance_df["Importance"].round(3),
                )
                fig3.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(15,20,32,0.8)",
                    font_color="#ffffff", height=320, showlegend=False,
                    margin=dict(l=0, r=20, t=30, b=0),
                    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#555"),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#888"),
                    font=dict(family="Rajdhani"),
                    title=dict(text="Importance des features", font=dict(family="Bebas Neue", size=18, color="#00ff87")),
                )
                fig3.update_traces(textposition="outside", textfont_size=12)
                st.plotly_chart(fig3, use_container_width=True)

            with col2:
                pred_counts = pd.Series(y_pred).value_counts().reset_index()
                pred_counts.columns = ["Resultat", "Count"]
                pred_counts["Resultat"] = pred_counts["Resultat"].map({
                    "home": "Domicile", "away": "Extérieur", "draw": "Nul"
                })
                fig4 = px.pie(
                    pred_counts, values="Count", names="Resultat",
                    color_discrete_sequence=["#00ff87", "#ffd700", "#ff6b6b"],
                    hole=0.5,
                )
                fig4.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(15,20,32,0.8)",
                    font_color="#ffffff", height=320,
                    margin=dict(l=0, r=0, t=30, b=0),
                    legend=dict(font=dict(family="Rajdhani", size=13)),
                    font=dict(family="Rajdhani"),
                    title=dict(text="Distribution des prédictions", font=dict(family="Bebas Neue", size=18, color="#00ff87")),
                )
                st.plotly_chart(fig4, use_container_width=True)

            # ── SIMULATEUR ────────────────────────────────────────────────────────
            section_title("SIMULATEUR DE MATCH", color="#00ff87")

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                sim_home = st.number_input("Buts domicile attendus", 0, 10, 1)
                sim_att  = st.number_input("Affluence estimée", 0, 100000, 30000)
            with col_s2:
                sim_away = st.number_input("Buts extérieur attendus", 0, 10, 1)

            if st.button("PRÉDIRE LE RÉSULTAT"):
                sim_data     = pd.DataFrame([[sim_home, sim_away, sim_home + sim_away, sim_att]], columns=feature_m)
                pred         = model.predict(sim_data)[0]
                proba        = model.predict_proba(sim_data)[0]
                labels_pred  = model.classes_
                result_label = {"home": "Victoire domicile", "away": "Victoire extérieur", "draw": "Match nul"}.get(pred, pred)
                result_color = {"home": "#00ff87", "away": "#ff6b6b", "draw": "#ffd700"}.get(pred, "#00ff87")

                st.markdown(f"""
                <div style='background:linear-gradient(135deg,rgba(0,255,135,0.08),#0f1420);
                            border-radius:12px;padding:20px 24px;
                            border:1px solid {result_color}44;
                            border-left:4px solid {result_color};margin:16px 0;text-align:center'>
                    <p style='color:#555;font-size:11px;font-family:"Inter";margin:0;
                               text-transform:uppercase;letter-spacing:2px'>Résultat prédit</p>
                    <h2 style='color:{result_color};font-family:"Bebas Neue";font-size:2rem;
                               letter-spacing:3px;margin:8px 0 0'>{result_label}</h2>
                </div>
                """, unsafe_allow_html=True)

                proba_df = pd.DataFrame({"Resultat": labels_pred, "Probabilite": proba})
                proba_df["Resultat"] = proba_df["Resultat"].map({
                    "home": "Domicile", "away": "Extérieur", "draw": "Nul"
                })
                fig5 = px.bar(
                    proba_df, x="Resultat", y="Probabilite",
                    color="Probabilite",
                    color_continuous_scale=[
                        [0, plotly_color("#0f1420")],
                        [1, plotly_color("#00ff87")],
                    ],
                    text=proba_df["Probabilite"].apply(lambda x: f"{x:.1%}"),
                )
                fig5.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(15,20,32,0.8)",
                    font_color="#ffffff", height=300, showlegend=False,
                    margin=dict(l=0, r=0, t=20, b=0),
                    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#555"),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", color="#555", tickformat=".0%"),
                    font=dict(family="Rajdhani"),
                )
                fig5.update_traces(textposition="outside", textfont_size=14)
                st.plotly_chart(fig5, use_container_width=True)

    st.markdown("""
    <div style='margin-top:60px;padding:20px;border-top:1px solid rgba(255,255,255,0.04);text-align:center'>
        <span style='font-family:"Inter",sans-serif;font-size:11px;color:#333;
                     letter-spacing:2px;text-transform:uppercase'>
            Data source : FBref &nbsp;·&nbsp; Saison 2024-2025 &nbsp;·&nbsp; Built with Streamlit & Plotly
        </span>
    </div>
    """, unsafe_allow_html=True)


render()