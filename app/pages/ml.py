import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from config.clubs import get_league_logo_path

from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

LEAGUES = ["ligue1", "premier", "laliga", "bundesliga", "seriea"]
LEAGUE_LABELS = {
    "ligue1"     : "Ligue 1",
    "premier"    : "Premier League",
    "laliga"     : "La Liga",
    "bundesliga" : "Bundesliga",
    "seriea"     : "Serie A",
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


def render():
    players, matches = load_data()

    st.markdown("""
    <div style='padding:30px 0 10px'>
        <h1 style='font-size:2.5rem;color:#00ff87;margin:0'>ML / Analytics</h1>
        <p style='color:#888;font-size:1rem;margin:8px 0'>Clustering · Prediction · Analyse avancee</p>
        <hr style='border:1px solid #1a1d27;margin:20px 0'>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Clustering joueurs", "Prediction de matchs"])

    # ── Tab 1 : Clustering ────────────────────────────────────────────────────────
    with tab1:
        st.markdown("### Clustering des joueurs par profil")
        st.markdown("Regroupement automatique des joueurs selon leurs statistiques (K-Means)")

        selected = st.selectbox(
            "Ligue",
            options=list(players.keys()),
            format_func=lambda x: LEAGUE_LABELS.get(x, x),
        )

        # Afficher le logo de la ligue sélectionnée
        logo_ligue = get_league_logo_path(selected)
        if logo_ligue:
            st.image(logo_ligue, width=100)

        df = players.get(selected, pd.DataFrame())

        feature_cols = [c for c in [
            "Performance_Gls", "Performance_Ast", "Performance_G+A",
            "Per 90 Minutes_Gls", "Per 90 Minutes_Ast",
            "Playing Time_MP", "Playing Time_Min",
            "Performance_CrdY",
        ] if c in df.columns]

        if len(feature_cols) < 3:
            st.warning("Pas assez de colonnes pour le clustering.")
        else:
            df_ml = df.dropna(subset=feature_cols).copy()
            n_clusters = st.slider("Nombre de clusters", 2, 8, 4)

            scaler   = StandardScaler()
            X_scaled = scaler.fit_transform(df_ml[feature_cols])

            kmeans        = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            df_ml["Cluster"] = kmeans.fit_predict(X_scaled).astype(str)

            # PCA 2D
            pca    = PCA(n_components=2)
            coords = pca.fit_transform(X_scaled)
            df_ml["PCA_1"] = coords[:, 0]
            df_ml["PCA_2"] = coords[:, 1]

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Visualisation PCA des clusters")
                fig = px.scatter(
                    df_ml, x="PCA_1", y="PCA_2",
                    color="Cluster", hover_name="Player" if "Player" in df_ml.columns else None,
                    hover_data=["Squad", "Performance_Gls"] if "Squad" in df_ml.columns else None,
                    color_discrete_sequence=px.colors.qualitative.Bold,
                )
                fig.update_layout(
                    plot_bgcolor="#0e1117", paper_bgcolor="#1a1d27",
                    font_color="#ffffff", height=450,
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("#### Profil moyen par cluster")
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
                    color_continuous_scale="Blues",
                )
                fig2.update_layout(
                    plot_bgcolor="#0e1117", paper_bgcolor="#1a1d27",
                    font_color="#ffffff", height=450,
                )
                st.plotly_chart(fig2, use_container_width=True)

            # Top joueurs par cluster
            st.markdown("#### Top joueurs par cluster")
            for cluster_id in sorted(df_ml["Cluster"].unique()):
                with st.expander(f"Cluster {cluster_id}"):
                    cluster_df = df_ml[df_ml["Cluster"] == cluster_id]
                    show_cols  = [c for c in ["Player", "Squad", "Pos", "Performance_Gls", "Performance_Ast", "Playing Time_MP"] if c in cluster_df.columns]
                    st.dataframe(
                        cluster_df[show_cols].sort_values("Performance_Gls", ascending=False).head(10).reset_index(drop=True),
                        use_container_width=True,
                    )

    # ── Tab 2 : Prediction ────────────────────────────────────────────────────────
    with tab2:
        st.markdown("### Prediction de resultat de match")
        st.markdown("Modele Random Forest entraine sur les statistiques des matchs")

        selected_m = st.selectbox(
            "Ligue",
            options=list(matches.keys()),
            format_func=lambda x: LEAGUE_LABELS.get(x, x),
            key="ml_league",
        )

        df_m = matches.get(selected_m, pd.DataFrame())

        feature_m = [c for c in ["home_score", "away_score", "total_goals", "Attendance"] if c in df_m.columns]

        if "result" not in df_m.columns or len(feature_m) < 2:
            st.warning("Donnees insuffisantes pour la prediction.")
        else:
            df_m = df_m.dropna(subset=feature_m + ["result"]).copy()

            X = df_m[feature_m]
            y = df_m["result"]

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            y_pred   = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)

            st.markdown(f"""
            <div style='background:#1a1d27;border-radius:12px;padding:20px;border-left:4px solid #00ff87;margin-bottom:20px'>
                <p style='color:#888;font-size:13px;margin:0;text-transform:uppercase'>Accuracy du modele</p>
                <h2 style='color:#00ff87;margin:8px 0'>{round(accuracy * 100, 1)}%</h2>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Importance des features")
                importance_df = pd.DataFrame({
                    "Feature"   : feature_m,
                    "Importance": model.feature_importances_,
                }).sort_values("Importance", ascending=True)

                fig3 = px.bar(
                    importance_df, x="Importance", y="Feature",
                    orientation="h", color="Importance",
                    color_continuous_scale="Greens", text=importance_df["Importance"].round(3),
                )
                fig3.update_layout(
                    plot_bgcolor="#0e1117", paper_bgcolor="#1a1d27",
                    font_color="#ffffff", height=300, showlegend=False,
                )
                st.plotly_chart(fig3, use_container_width=True)

            with col2:
                st.markdown("#### Distribution des predictions")
                pred_counts = pd.Series(y_pred).value_counts().reset_index()
                pred_counts.columns = ["Resultat", "Count"]
                pred_counts["Resultat"] = pred_counts["Resultat"].map({
                    "home" : "Victoire domicile",
                    "away" : "Victoire exterieur",
                    "draw" : "Match nul",
                })
                fig4 = px.pie(
                    pred_counts, values="Count", names="Resultat",
                    color_discrete_sequence=["#00ff87", "#ffd700", "#ff6b6b"],
                    hole=0.4,
                )
                fig4.update_layout(
                    plot_bgcolor="#0e1117", paper_bgcolor="#1a1d27",
                    font_color="#ffffff", height=300,
                )
                st.plotly_chart(fig4, use_container_width=True)

            # Simulation
            st.markdown("#### Simuler un match")
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                sim_home = st.number_input("Buts domicile attendus", 0, 10, 1)
                sim_att  = st.number_input("Affluence estimee", 0, 100000, 30000)
            with col_s2:
                sim_away = st.number_input("Buts exterieur attendus", 0, 10, 1)

            if st.button("Predire le resultat"):
                sim_data = pd.DataFrame([[sim_home, sim_away, sim_home + sim_away, sim_att]], columns=feature_m)
                pred     = model.predict(sim_data)[0]
                proba    = model.predict_proba(sim_data)[0]
                labels   = model.classes_

                result_label = {"home": "Victoire domicile", "away": "Victoire exterieur", "draw": "Match nul"}.get(pred, pred)
                st.success(f"Resultat predit : **{result_label}**")

                proba_df = pd.DataFrame({"Resultat": labels, "Probabilite": proba})
                proba_df["Resultat"] = proba_df["Resultat"].map({
                    "home": "Victoire domicile", "away": "Victoire exterieur", "draw": "Match nul"
                })
                fig5 = px.bar(
                    proba_df, x="Resultat", y="Probabilite",
                    color="Probabilite", color_continuous_scale="Greens",
                    text=proba_df["Probabilite"].apply(lambda x: f"{x:.1%}"),
                )
                fig5.update_layout(
                    plot_bgcolor="#0e1117", paper_bgcolor="#1a1d27",
                    font_color="#ffffff", height=300, showlegend=False,
                )
                st.plotly_chart(fig5, use_container_width=True)

    st.markdown("""
    <hr style='border:1px solid #1a1d27;margin-top:40px'>
    <p style='text-align:center;color:#444;font-size:12px'>
        Data source : FBref · Saison 2024-2025 · Built with Streamlit & Plotly
    </p>
    """, unsafe_allow_html=True)


render()