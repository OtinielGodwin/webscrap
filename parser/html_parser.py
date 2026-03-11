from bs4 import BeautifulSoup
from io import StringIO
import pandas as pd
from loguru import logger


def extract_table(html: str, table_id: str) -> pd.DataFrame:
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", {"id": table_id})

    if table is None:
        logger.warning(f"Table '{table_id}' introuvable")
        return pd.DataFrame()

    df = pd.read_html(StringIO(str(table)))[0]

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ["_".join(col).strip() for col in df.columns]

    logger.success(f"Table '{table_id}' → {df.shape[0]} lignes, {df.shape[1]} colonnes")
    return df


def extract_player_image(html: str, player_id: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    div  = soup.find("div", {"id": "meta"})

    if div is None:
        return None

    img = div.find("img")
    if img is None:
        return None

    return img.get("src")


def extract_all_tables(html: str) -> dict[str, pd.DataFrame]:
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find_all("table")
    result = {}

    for table in tables:
        table_id = table.get("id", "unknown")
        df = pd.read_html(StringIO(str(table)))[0]

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ["_".join(col).strip() for col in df.columns]

        result[table_id] = df

    logger.info(f"{len(result)} tables extraites")
    return result