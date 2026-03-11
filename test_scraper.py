import pandas as pd
from bs4 import BeautifulSoup

FILES = {
    "ligue1"     : "data/raw/ligue1_classement_raw.html",
    "premier"    : "data/raw/premier_classement_raw.html",
    "laliga"     : "data/raw/laliga_classement_raw.html",
    "bundesliga" : "data/raw/bundesliga_classement_raw.html",
    "seriea"     : "data/raw/seriea_classement_raw.html",
    "ucl"        : "data/raw/ucl_classement_raw.html",
}

mapping = {}

for league, filepath in FILES.items():
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "lxml")
    rows = soup.find_all("tr")

    for row in rows:
        td = row.find("td", {"data-stat": "team"})
        if td is None:
            continue
        a = td.find("a", href=True)
        img = td.find("img")
        if a and img:
            src      = img.get("src", "")
            club_name = a.text.strip()
            if "tlogo" in src:
                club_id = src.split("/")[-1].replace(".png", "")
                mapping[club_name] = club_id

for name, cid in sorted(mapping.items()):
    print(f'"{name}" : "{cid}",')