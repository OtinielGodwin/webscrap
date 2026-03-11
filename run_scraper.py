from loguru import logger
from scraper.leagues import scrape_all_leagues
from scraper.matches import scrape_all_matches
from scraper.teams import scrape_all_teams, scrape_psg
from scraper.players import scrape_all_players
from scraper.images import scrape_all_images
from processing.cleaner import process_all

logger.add("logs/scraper.log", rotation="10 MB")


def run():
    logger.info("=== DEBUT DU SCRAPING 2024-2025 ===")

    logger.info("--- Classements ---")
    scrape_all_leagues()

    logger.info("--- Matchs ---")
    scrape_all_matches()

    logger.info("--- Stats equipes ---")
    scrape_all_teams()
    scrape_psg()

    logger.info("--- Stats joueurs ---")
    scrape_all_players()

    logger.info("--- Nettoyage données ---")
    process_all()

    logger.info("--- Images joueurs ---")
    scrape_all_images()

    logger.info("=== SCRAPING TERMINE ===")


if __name__ == "__main__":
    run()