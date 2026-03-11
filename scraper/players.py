import os
import pandas as pd
from bs4 import BeautifulSoup
from loguru import logger

from config.settings import URLS, SAISON
from scraper.browser import get_page_html, save_raw_html
from parser.html_parser import extract_all_tables


PLAYERS_CONFIG = {
    "ucl"        : {"url_key": "ucl_stats"},
    "ligue1"     : {"url_key": "ligue1_stats"},
    "premier"    : {"url_key": "premier_stats"},
    "laliga"     : {"url_key": "laliga_stats"},
    "bundesliga" : {"url_key": "bundesliga_stats"},
    "seriea"     : {"url_key": "seriea_stats"},
}

STAT_TYPES = [
    "stats_standard",
    "stats_shooting",
    "stats_passing",
    "stats_defense",
    "stats_gca",
    "stats_possession",
]


def extract_player_ids(html: str, table_id: str) -> dict[str, str]:
    soup  = BeautifulSoup(html, "lxml")
    table = soup.find("table", {"id": table_id})

    if table is None:
        return {}

    ids  = {}
    rows = table.find_all("tr")

    for row in rows:
        td = row.find("td", {"data-stat": "player"})
        if td is None:
            continue
        a = td.find("a", href=True)
        if a and "/players/" in a["href"]:
            parts     = a["href"].strip("/").split("/")
            player_id = parts[2] if len(parts) >= 3 else ""
            name      = a.text.strip()
            if player_id and name:
                ids[name] = player_id

    return ids


def scrape_players(league_key: str) -> dict[str, pd.DataFrame]:
    config = PLAYERS_CONFIG[league_key]
    url    = URLS[config["url_key"]]

    html = get_page_html(url)
    save_raw_html(html, f"{league_key}_players_raw.html")

    all_tables = extract_all_tables(html)
    logger.info(f"Tables disponibles : {list(all_tables.keys())}")

    dfs = {}
    for stat_type in STAT_TYPES:
        if stat_type not in all_tables:
            logger.warning(f"Table {stat_type} introuvable pour {league_key}")
            continue

        df = all_tables[stat_type]

        if df.empty:
            continue

        player_col = next((c for c in df.columns if "Player" in c), None)
        if player_col:
            df = df[df[player_col] != player_col]

        df = df.dropna(how="all").reset_index(drop=True)

        player_ids = extract_player_ids(html, stat_type)
        if player_ids and player_col:
            df.insert(0, "player_id", df[player_col].map(player_ids).fillna(""))

        df["league"] = league_key
        df["saison"] = SAISON

        output_path = os.path.join("data", "processed", f"{league_key}_players_{stat_type.replace('stats_', '')}.csv")
        df.to_csv(output_path, index=False)
        logger.success(f"{league_key} {stat_type} → {df.shape[0]} joueurs → {output_path}")
        dfs[stat_type] = df

    return dfs


def scrape_all_players() -> dict[str, dict[str, pd.DataFrame]]:
    results = {}
    for league_key in PLAYERS_CONFIG:
        logger.info(f"Scraping joueurs {league_key}...")
        results[league_key] = scrape_players(league_key)
    return results