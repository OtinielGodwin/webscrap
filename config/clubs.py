
import os

LEAGUES_LOGO_MAPPING = {
    "ucl"        : "8__logo.png",
    "premier"    : "9__logo.png",
    "seriea"     : "11__logo.png",
    "laliga"     : "12__logo.png",
    "ligue1"     : "13__logo.png",
    "bundesliga" : "20__logo.png",
}

def get_league_logo_path(league: str, base_dir: str = "data/images/clubs") -> str | None:
    filename = LEAGUES_LOGO_MAPPING.get(league)
    if not filename:
        return None
    path = os.path.join(base_dir, filename)
    if not os.path.exists(path):
        return None
    # retourner chemin absolu pour éviter les problèmes de cwd
    return os.path.abspath(path)



CLUB_LOGO_MAPPING = {
    "Alavés"               : "8d6fd021",
    "Angers"               : "69236f98",
    "Arsenal"              : "18bb7c10",
    "Aston Villa"          : "8602292d",
    "Atalanta"             : "922493f3",
    "Athletic Club"        : "2b390eca",
    "Atlético Madrid"      : "db3b9613",
    "Augsburg"             : "0cdc4311",
    "Auxerre"              : "5ae09109",
    "Barcelona"            : "206d90db",
    "Bayern Munich"        : "054efa67",
    "Benfica"              : "a77c513e",
    "Bochum"               : "b42c6323",
    "Bologna"              : "1d8099f8",
    "Bournemouth"          : "4ba7cbea",
    "Brentford"            : "cd051869",
    "Brest"                : "fb08dbb3",
    "Brighton"             : "d07537b9",
    "Cagliari"             : "c4260e09",
    "Celta Vigo"           : "f25da7fb",
    "Celtic"               : "b81aa4fa",
    "Chelsea"              : "cff3d9bb",
    "Club Brugge"          : "f1e6c5f1",
    "Como"                 : "28c9c3cd",
    "Crystal Palace"       : "47c64c55",
    "Dinamo Zagreb"        : "edd0d381",
    "Dortmund"             : "add600ae",
    "Eintracht Frankfurt"  : "f0ac8ee6",
    "Empoli"               : "a3d88bd8",
    "Espanyol"             : "a8661628",
    "Everton"              : "d3fd31cc",
    "Feyenoord"            : "fb4ca611",
    "Fiorentina"           : "421387cf",
    "Freiburg"             : "a486e511",
    "Fulham"               : "fd962109",
    "Genoa"                : "658bf2de",
    "Getafe"               : "7848bd64",
    "Girona"               : "9024a00a",
    "Gladbach"             : "32f3ee20",
    "Heidenheim"           : "18d9d2a7",
    "Hellas Verona"        : "0e72edf2",
    "Hoffenheim"           : "033ea6b8",
    "Holstein Kiel"        : "2ac661d9",
    "Inter"                : "d609edc0",
    "Ipswich Town"         : "b74092de",
    "Juventus"             : "e0652b02",
    "Las Palmas"           : "0049d422",
    "Lazio"                : "7213da33",
    "Le Havre"             : "5c2737db",
    "Lecce"                : "ffcbe334",
    "Leganés"              : "7c6f2c78",
    "Leicester City"       : "a2d435b3",
    "Lens"                 : "fd4e0f7d",
    "Leverkusen"           : "c7a9f859",
    "Lille"                : "cb188c0c",
    "Liverpool"            : "822bd0ba",
    "Lyon"                 : "d53c0b06",
    "Mainz 05"             : "a224b06a",
    "Mallorca"             : "2aa12281",
    "Manchester City"      : "b8fd03ef",
    "Manchester Utd"       : "19538871",
    "Marseille"            : "5725cc7b",
    "Milan"                : "dc56fe14",
    "Monaco"               : "fd6114db",
    "Montpellier"          : "281b0e73",
    "Monza"                : "21680aa4",
    "Nantes"               : "d7a486cd",
    "Napoli"               : "d48ad4ff",
    "Newcastle United"     : "b2b47a98",
    "Nice"                 : "132ebc33",
    "Nottingham Forest"    : "e4a775cb",
    "Osasuna"              : "03c57e2b",
    "PSV"                  : "e334d850",
    "Paris Saint-Germain"  : "e2d8892c",
    "Parma"                : "eab4234c",
    "RB Leipzig"           : "acbb6a5b",
    "RB Salzburg"          : "50f2a074",
    "Rayo Vallecano"       : "98e8af82",
    "Real Betis"           : "fc536746",
    "Real Madrid"          : "53a2f082",
    "Real Sociedad"        : "e31d1cd9",
    "Red Star"             : "099c6eb5",
    "Reims"                : "7fdd64e0",
    "Rennes"               : "b3072e00",
    "Roma"                 : "cf74a709",
    "Saint-Étienne"        : "d298ef2c",
    "Sevilla"              : "ad2be733",
    "Shakhtar Donetsk"     : "e89d5a28",
    "Slovan Bratislava"    : "ae7f2f70",
    "Southampton"          : "33c895d4",
    "Sparta Prague"        : "ecb862be",
    "Sporting CP"          : "13dc44fd",
    "St Pauli"             : "54864664",
    "Strasbourg"           : "c0d3eab4",
    "Sturm Graz"           : "3f4fe568",
    "Stuttgart"            : "598bc722",
    "Torino"               : "105360fe",
    "Tottenham Hotspur"    : "361ca564",
    "Toulouse"             : "3f8c4b5f",
    "Udinese"              : "04eea015",
    "Union Berlin"         : "7a41008f",
    "Valencia"             : "dcc91a7b",
    "Valladolid"           : "17859612",
    "Venezia"              : "af5d5982",
    "Villarreal"           : "2a8183b3",
    "Werder Bremen"        : "62add3bf",
    "West Ham United"      : "7c21e445",
    "Wolfsburg"            : "4eaa11d7",
    "Wolves"               : "8cec06e1",
    "Young Boys"           : "4b682260",
}


def get_club_logo_path(club_name: str, base_dir: str = "data/images/clubs") -> str | None:
    import os
    club_id = CLUB_LOGO_MAPPING.get(club_name)
    if not club_id:
        return None
    for f in os.listdir(base_dir):
        if f.startswith(club_id):
            return os.path.join(base_dir, f)
    return None