from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL  = os.getenv("FBREF_BASE_URL", "https://fbref.com/en")
DELAY_MIN = int(os.getenv("DELAY_MIN", 4))
DELAY_MAX = int(os.getenv("DELAY_MAX", 9))
SAISON    = "2024-2025"

HEADERS = {
    "User-Agent"      : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language" : "en-US,en;q=0.9",
    "Referer"         : "https://fbref.com",
}

URLS = {
    "ucl_classement"  : f"{BASE_URL}/comps/8/2024-2025/2024-2025-Champions-League-Stats",
    "ucl_stats"       : f"{BASE_URL}/comps/8/2024-2025/stats/2024-2025-Champions-League-Stats",
    "ucl_matches"     : f"{BASE_URL}/comps/8/2024-2025/schedule/2024-2025-Champions-League-Scores-and-Fixtures",

    "ligue1_classement" : f"{BASE_URL}/comps/13/2024-2025/2024-2025-Ligue-1-Stats",
    "ligue1_stats"      : f"{BASE_URL}/comps/13/2024-2025/stats/2024-2025-Ligue-1-Stats",
    "ligue1_matches"    : f"{BASE_URL}/comps/13/2024-2025/schedule/2024-2025-Ligue-1-Scores-and-Fixtures",

    "premier_classement" : f"{BASE_URL}/comps/9/2024-2025/2024-2025-Premier-League-Stats",
    "premier_stats"      : f"{BASE_URL}/comps/9/2024-2025/stats/2024-2025-Premier-League-Stats",
    "premier_matches"    : f"{BASE_URL}/comps/9/2024-2025/schedule/2024-2025-Premier-League-Scores-and-Fixtures",

    "laliga_classement" : f"{BASE_URL}/comps/12/2024-2025/2024-2025-La-Liga-Stats",
    "laliga_stats"      : f"{BASE_URL}/comps/12/2024-2025/stats/2024-2025-La-Liga-Stats",
    "laliga_matches"    : f"{BASE_URL}/comps/12/2024-2025/schedule/2024-2025-La-Liga-Scores-and-Fixtures",

    "bundesliga_classement" : f"{BASE_URL}/comps/20/2024-2025/2024-2025-Bundesliga-Stats",
    "bundesliga_stats"      : f"{BASE_URL}/comps/20/2024-2025/stats/2024-2025-Bundesliga-Stats",
    "bundesliga_matches"    : f"{BASE_URL}/comps/20/2024-2025/schedule/2024-2025-Bundesliga-Scores-and-Fixtures",

    "seriea_classement" : f"{BASE_URL}/comps/11/2024-2025/2024-2025-Serie-A-Stats",
    "seriea_stats"      : f"{BASE_URL}/comps/11/2024-2025/stats/2024-2025-Serie-A-Stats",
    "seriea_matches"    : f"{BASE_URL}/comps/11/2024-2025/schedule/2024-2025-Serie-A-Scores-and-Fixtures",

    "psg_squad" : f"{BASE_URL}/squads/e2d8892c/2024-2025/Paris-Saint-Germain-Stats",
}