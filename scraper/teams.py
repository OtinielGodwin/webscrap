import os
import pandas as pd
from loguru import logger

from config.settings import URLS, SAISON
from scraper.browser import get_page_html, save_raw_html
from parser.html_parser import extract_table


TEAMS_CONFIG = {
    "ucl"        : {"url_key": "ucl_stats",        "table_id": "stats_squads_standard_for"},
    "ligue1"     : {"url_key": "ligue1_stats",     "table_id": "stats_squads_standard_for"},
    "premier"    : {"url_key": "premier_stats",    "table_id": "stats_squads_standard_for"},
    "laliga"     : {"url_key": "laliga_stats",     "table_id": "stats_squads_standard_for"},
    "bundesliga" : {"url_key": "bundesliga_stats", "table_id": "stats_squads_standard_for"},
    "seriea"     : {"url_key": "seriea_stats",     "table_id": "stats_squads_standard_for"},
}


def scrape_teams(league_key: str) -> pd.DataFrame:
    config   = TEAMS_CONFIG[league_key]
    url      = URLS[config["url_key"]]
    table_id = config["table_id"]

    html = get_page_html(url)
    save_raw_html(html, f"{league_key}_teams_raw.html")

    df = extract_table(html, table_id)

    if df.empty:
        logger.warning(f"Aucune équipe trouvée pour {league_key}")
        return df

    df["league"] = league_key
    df["saison"] = SAISON

    output_path = os.path.join("data", "processed", f"{league_key}_teams.csv")
    df.to_csv(output_path, index=False)
    logger.success(f"Equipes {league_key} sauvegardées → {output_path}")

    return df


def scrape_psg() -> dict[str, pd.DataFrame]:
    url = URLS["psg_squad"]
    html = get_page_html(url)
    save_raw_html(html, "psg_raw.html")

    tables = {
        "stats"    : "stats_standard_8",
        "shooting" : "stats_shooting_8",
        "passing"  : "stats_passing_8",
        "defense"  : "stats_defense_8",
    }

    dfs = {}
    for name, table_id in tables.items():
        df = extract_table(html, table_id)
        if not df.empty:
            df["saison"] = SAISON
            output_path = os.path.join("data", "processed", f"psg_{name}.csv")
            df.to_csv(output_path, index=False)
            logger.success(f"PSG {name} sauvegardé → {output_path}")
            dfs[name] = df

    return dfs


def scrape_all_teams() -> dict[str, pd.DataFrame]:
    results = {}
    for league_key in TEAMS_CONFIG:
        logger.info(f"Scraping équipes {league_key}...")
        results[league_key] = scrape_teams(league_key)
    return results