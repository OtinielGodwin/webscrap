import os
import time
import random
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger
from playwright.sync_api import sync_playwright

from config.settings import DELAY_MIN, DELAY_MAX

HEADSHOT_URLS = [
    "https://fbref.com/req/202302030/images/headshots/{player_id}_2022.jpg",
    "https://fbref.com/req/202302030/images/headshots/{player_id}_2023.jpg",
]
CLUB_LOGO_URL = "https://cdn.ssref.net/req/202602162/tlogo/fb/{club_id}.png"
LEAGUES       = ["ucl", "ligue1", "premier", "laliga", "bundesliga", "seriea"]
NB_WORKERS    = 5
USER_AGENT    = (
    "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/145.0.0.0 Mobile Safari/537.36"
)


def _ensure_dirs() -> None:
    os.makedirs(os.path.join("data", "images", "players"), exist_ok=True)
    os.makedirs(os.path.join("data", "images", "clubs"),   exist_ok=True)


def recuperer_cookies() -> dict:
    logger.info("Récupération des cookies FBref via Playwright...")
    cookies_dict = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=USER_AGENT,
        )
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        page = context.new_page()
        page.goto("https://fbref.com/en/", wait_until="domcontentloaded", timeout=60000)
        logger.info("Attente passage Cloudflare (30s)...")
        page.wait_for_timeout(30000)

        for cookie in context.cookies():
            cookies_dict[cookie["name"]] = cookie["value"]

        browser.close()

    logger.success(f"{len(cookies_dict)} cookies récupérés")
    return cookies_dict


def telecharger_image(args: tuple) -> tuple:
    player_id, player_name, cookies = args

    if not player_id or player_id == "nan":
        return player_id, player_name, None

    _ensure_dirs()

    filename  = f"{player_id}_{player_name.replace(' ', '_').lower()}.jpg"
    save_path = os.path.join("data", "images", "players", filename)

    if os.path.exists(save_path):
        return player_id, player_name, save_path

    headers = {
        "User-Agent" : USER_AGENT,
        "Referer"    : "https://fbref.com/en/",
        "Accept"     : "image/webp,image/apng,image/*,*/*;q=0.8",
    }

    time.sleep(random.uniform(0.3, 0.8))

    for url_template in HEADSHOT_URLS:
        url = url_template.format(player_id=player_id)

        for attempt in range(3):
            try:
                response = requests.get(
                    url, headers=headers, cookies=cookies, timeout=15
                )

                if response.status_code == 200 and len(response.content) > 1000:
                    with open(save_path, "wb") as f:
                        f.write(response.content)
                    return player_id, player_name, save_path

                elif response.status_code == 404:
                    break

                else:
                    time.sleep(3)

            except Exception as e:
                logger.warning(f"Tentative {attempt + 1}/3 échouée pour {player_name} : {e}")
                time.sleep(5)

    return player_id, player_name, None


def scrape_images_from_csv(csv_path: str, cookies: dict, league: str = "") -> dict:
    if not os.path.exists(csv_path):
        logger.error(f"Fichier introuvable : {csv_path}")
        return {}

    df = pd.read_csv(csv_path)

    if "player_id" not in df.columns:
        logger.error("Colonne player_id introuvable")
        return {}

    player_col = next((c for c in df.columns if "Player" in c), None)
    if player_col is None:
        logger.error("Colonne Player introuvable")
        return {}

    joueurs = []
    for _, row in df.iterrows():
        player_id   = str(row.get("player_id", "")).strip()
        player_name = str(row.get(player_col, "")).strip()
        if player_id and player_name and player_id != "nan":
            filename  = f"{player_id}_{player_name.replace(' ', '_').lower()}.jpg"
            save_path = os.path.join("data", "images", "players", filename)
            if not os.path.exists(save_path):
                joueurs.append((player_id, player_name, cookies))

    total   = len(joueurs)
    logger.info(f"{total} images à télécharger pour {league}")

    if total == 0:
        logger.success(f"Toutes les images déjà téléchargées pour {league}")
        return {}

    resultats = {}

    with ThreadPoolExecutor(max_workers=NB_WORKERS) as executor:
        futures = {executor.submit(telecharger_image, args): args for args in joueurs}

        for i, future in enumerate(as_completed(futures), start=1):
            player_id, player_name, chemin = future.result()
            if chemin:
                resultats[player_id] = chemin
                logger.success(f"[{i}/{total}] {player_name}")
            else:
                logger.warning(f"[{i}/{total}] Pas de photo : {player_name}")

    logger.success(f"{len(resultats)}/{total} images téléchargées pour {league}")
    return resultats


def download_club_logo(club_id: str, club_name: str) -> str | None:
    if not club_id or club_id == "nan":
        return None

    _ensure_dirs()

    filename  = f"{club_id}_{club_name.replace(' ', '_').lower()}.png"
    save_path = os.path.join("data", "images", "clubs", filename)

    if os.path.exists(save_path):
        return save_path

    url = CLUB_LOGO_URL.format(club_id=club_id)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(response.content)
        logger.success(f"Logo club : {filename}")
        return save_path

    except Exception as e:
        logger.error(f"Erreur logo {club_name} : {e}")
        return None


def scrape_all_images() -> None:
    folder  = os.path.join("data", "processed")
    cookies = recuperer_cookies()

    for league in LEAGUES:
        csv_path = os.path.join(folder, f"{league}_players_standard.csv")
        if not os.path.exists(csv_path):
            logger.warning(f"Pas de fichier joueurs pour {league}")
            continue
        logger.info(f"Images joueurs {league}...")
        scrape_images_from_csv(csv_path, cookies, league)