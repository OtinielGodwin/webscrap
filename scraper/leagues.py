import os
import pandas as pd
from loguru import logger

from config.settings import URLS, SAISON
from scraper.browser import get_page_html, save_raw_html
from parser.html_parser import extract_table


LEAGUE_TABLE_IDS = {
    "ucl"        : "results2024-202582_overall",
    "ligue1"     : "results2024-2025131_overall",
    "premier"    : "results2024-202591_overall",
    "laliga"     : "results2024-2025121_overall",
    "bundesliga" : "results2024-2025201_overall",
    "seriea"     : "results2024-2025111_overall",
}

LEAGUE_URL_KEYS = {
    "ucl"        : "ucl_classement",
    "ligue1"     : "ligue1_classement",
    "premier"    : "premier_classement",
    "laliga"     : "laliga_classement",
    "bundesliga" : "bundesliga_classement",
    "seriea"     : "seriea_classement",
}


def scrape_league(league_key: str) -> pd.DataFrame:
    url      = URLS[LEAGUE_URL_KEYS[league_key]]
    table_id = LEAGUE_TABLE_IDS[league_key]

    html = get_page_html(url)
    save_raw_html(html, f"{league_key}_raw.html")

    df = extract_table(html, table_id)

    if df.empty:
        logger.warning(f"Aucune donnée pour {league_key}")
        return df

    df["league"] = league_key
    df["saison"] = SAISON

    output_path = os.path.join("data", "processed", f"{league_key}_classement.csv")
    df.to_csv(output_path, index=False)
    logger.success(f"Classement {league_key} sauvegardé → {output_path}")

    return df


def scrape_league_from_html(league_key: str) -> pd.DataFrame:
    table_id  = LEAGUE_TABLE_IDS[league_key]
    html_path = os.path.join("data", "raw", f"{league_key}_raw.html")

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    df = extract_table(html, table_id)

    if df.empty:
        logger.warning(f"Aucune donnée pour {league_key}")
        return df

    df["league"] = league_key
    df["saison"] = SAISON

    output_path = os.path.join("data", "processed", f"{league_key}_classement.csv")
    df.to_csv(output_path, index=False)
    logger.success(f"Classement {league_key} sauvegardé → {output_path}")

    return df


def scrape_all_leagues() -> dict[str, pd.DataFrame]:
    results = {}
    for league_key in LEAGUE_TABLE_IDS:
        logger.info(f"Scraping {league_key}...")
        results[league_key] = scrape_league(league_key)
    return results


def scrape_all_leagues_from_html() -> dict[str, pd.DataFrame]:
    results = {}
    for league_key in LEAGUE_TABLE_IDS:
        logger.info(f"Parsing {league_key}...")
        results[league_key] = scrape_league_from_html(league_key)
    return results