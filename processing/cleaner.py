import os
import pandas as pd
from loguru import logger


LEAGUES = ["ucl", "ligue1", "premier", "laliga", "bundesliga", "seriea"]

PLAYERS_RENAME = {
    "Unnamed: 0_level_0_Rk"      : "Rk",
    "Unnamed: 1_level_0_Player"  : "Player",
    "Unnamed: 2_level_0_Nation"  : "Nation",
    "Unnamed: 3_level_0_Pos"     : "Pos",
    "Unnamed: 4_level_0_Squad"   : "Squad",
    "Unnamed: 5_level_0_Age"     : "Age",
    "Unnamed: 6_level_0_Born"    : "Born",
    "Unnamed: 24_level_0_Matches": "Matches",
}

TEAMS_RENAME = {
    "Unnamed: 0_level_0_Squad" : "Squad",
    "Unnamed: 1_level_0_# Pl"  : "Nb_Players",
    "Unnamed: 2_level_0_Age"   : "Age",
    "Unnamed: 3_level_0_Poss"  : "Poss",
}


def clean_classement(df: pd.DataFrame, league: str) -> pd.DataFrame:
    df = df.dropna(subset=["Squad"])
    df = df[df["Squad"] != "Squad"]

    numeric_cols = ["MP", "W", "D", "L", "GF", "GA", "GD", "Pts", "Pts/MP", "Attendance"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if league == "ucl":
        df["Squad"] = df["Squad"].str.replace(r"^[a-z]{2,3}\s", "", regex=True)

    df["win_rate"]  = (df["W"] / df["MP"]).round(3)
    df["goal_diff"] = df["GF"] - df["GA"]

    return df.reset_index(drop=True)


def clean_matches(df: pd.DataFrame) -> pd.DataFrame:
    if "Score" not in df.columns:
        return df

    df = df.dropna(subset=["Score"])
    df = df[df["Score"].str.contains(r"\d", na=False)]
    df = df[df["Score"] != "Score"]

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    scores = df["Score"].str.split("–", expand=True)
    if scores.shape[1] == 2:
        df["home_score"]  = pd.to_numeric(scores[0], errors="coerce")
        df["away_score"]  = pd.to_numeric(scores[1], errors="coerce")
        df["total_goals"] = df["home_score"] + df["away_score"]
        df["result"]      = df.apply(
            lambda r: "home" if r["home_score"] > r["away_score"]
            else ("away" if r["home_score"] < r["away_score"] else "draw"), axis=1
        )

    if "Attendance" in df.columns:
        df["Attendance"] = pd.to_numeric(df["Attendance"], errors="coerce")

    return df.reset_index(drop=True)


def clean_teams(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=TEAMS_RENAME)
    df = df.dropna(subset=["Squad"])
    df = df[df["Squad"] != "Squad"]

    numeric_cols = [
        "Nb_Players", "Poss", "Playing Time_MP", "Playing Time_Min",
        "Performance_Gls", "Performance_Ast", "Performance_G+A",
        "Performance_CrdY", "Performance_CrdR",
        "Per 90 Minutes_Gls", "Per 90 Minutes_Ast",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.reset_index(drop=True)


def clean_players(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=PLAYERS_RENAME)

    if "Player" not in df.columns:
        return df

    df = df[df["Player"] != "Player"]
    df = df.dropna(subset=["Player"])

    if "Nation" in df.columns:
        df["Nation"] = df["Nation"].str.split(" ").str[-1]

    numeric_cols = [
        "Playing Time_MP", "Playing Time_Starts", "Playing Time_Min",
        "Playing Time_90s", "Performance_Gls", "Performance_Ast",
        "Performance_G+A", "Performance_G-PK", "Performance_PK",
        "Performance_PKatt", "Performance_CrdY", "Performance_CrdR",
        "Per 90 Minutes_Gls", "Per 90 Minutes_Ast", "Per 90 Minutes_G+A",
        "Per 90 Minutes_G-PK", "Per 90 Minutes_G+A-PK", "Age", "Born",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.reset_index(drop=True)


def process_all() -> None:
    folder = os.path.join("data", "processed")

    for league in LEAGUES:
        for ftype, fn in [
            ("classement",       lambda df, l=league: clean_classement(df, l)),
            ("matches",          lambda df: clean_matches(df)),
            ("teams",            lambda df: clean_teams(df)),
            ("players_standard", lambda df: clean_players(df)),
        ]:
            path = os.path.join(folder, f"{league}_{ftype}.csv")
            if not os.path.exists(path):
                logger.warning(f"Manquant : {league}_{ftype}.csv")
                continue

            df     = pd.read_csv(path)
            df     = fn(df)
            output = os.path.join(folder, f"{league}_{ftype}_clean.csv")
            df.to_csv(output, index=False)
            logger.success(f"{league}_{ftype}_clean.csv → {df.shape[0]} lignes x {df.shape[1]} colonnes")


if __name__ == "__main__":
    process_all()