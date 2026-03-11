from playwright.sync_api import sync_playwright
from loguru import logger
import time
import random
import os

from config.settings import DELAY_MIN, DELAY_MAX


def get_page_html(url: str, headless: bool = False) -> str:
    wait = random.uniform(DELAY_MIN, DELAY_MAX)
    logger.info(f"Attente de {wait:.1f}s avant {url}")
    time.sleep(wait)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--no-sandbox",
            ]
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="fr-FR",
            user_agent="Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36",
        )

        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        logger.info("Attente passage Cloudflare (30s)...")
        page.wait_for_timeout(30000)

        html = page.content()

        if len(html) < 100000:
            logger.warning("Page trop courte, Cloudflare non résolu. Attente 30s supplémentaires...")
            page.wait_for_timeout(30000)
            html = page.content()

        browser.close()

    logger.success(f"Page récupérée : {len(html)} caractères")
    return html


def save_raw_html(html: str, filename: str) -> None:
    path = os.path.join("data", "raw", filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    logger.info(f"HTML sauvegardé : {path}")