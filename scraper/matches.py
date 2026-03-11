import os
import pandas as pd
from loguru import logger

from config.settings import URLS, SAISON
from scraper.browser import get_page_html, save_raw_html
from parser.html_parser import extract_table


MATCHES_CONFIG = {
    "ucl" : {
        "url_key"  : "ucl_matches",
        "table_ids": ["sched_2024-2025_8_1", "sched_2024-2025_8_2", "sched_2024-2025_8_3"],
    },
    "ligue1" : {
        "url_key"  : "ligue1_matches",
        "table_ids": ["sched_2024-2025_13_1"],
    },
    "premier" : {
        "url_key"  : "premier_matches",
        "table_ids": ["sched_2024-2025_9_1"],
    },
    "laliga" : {
        "url_key"  : "laliga_matches",
        "table_ids": ["sched_2024-2025_12_1"],
    },
    "bundesliga" : {
        "url_key"  : "bundesliga_matches",
        "table_ids": ["sched_2024-2025_20_1"],
    },
    "seriea" : {
        "url_key"  : "seriea_matches",
        "table_ids": ["sched_2024-2025_11_1"],
    },
}


def scrape_matches(league_key: str) -> pd.DataFrame:
    config = MATCHES_CONFIG[league_key]
    url    = URLS[config["url_key"]]

    html = get_page_html(url)
    save_raw_html(html, f"{league_key}_matches_raw.html")

    dfs = []
    for table_id in config["table_ids"]:
        df = extract_table(html, table_id)
        if not df.empty:
            dfs.append(df)

    if not dfs:
        logger.warning(f"Aucun match trouvé pour {league_key}")
        return pd.DataFrame()

    combined = pd.concat(dfs, ignore_index=True)
    combined = combined.dropna(subset=["Score"] if "Score" in combined.columns else combined.columns[:1])
    combined = combined[combined["Score"].str.contains(r"\d", na=False)] if "Score" in combined.columns else combined
    combined["league"] = league_key
    combined["saison"] = SAISON

    output_path = os.path.join("data", "processed", f"{league_key}_matches.csv")
    combined.to_csv(output_path, index=False)
    logger.success(f"{league_key} → {combined.shape[0]} matchs → {output_path}")
    return combined


def scrape_all_matches() -> None:
    for league_key in MATCHES_CONFIG:
        logger.info(f"Scraping matchs {league_key}...")
        scrape_matches(league_key)