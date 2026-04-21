import csv
import random
from io import TextIOWrapper

"""All the special delimiters to prepend to duplicated player names."""
DELIMITERS_2024 = [
    "Evil",
    "Clone",
    "Bad-Ending",
    "Good-Ending",
    "Creepypasta",
    "Skinwalker",
    "Bargain Bin",
    # "Dollar-Store",
    "Alternate",
    "Toy",
    "Lil'",
    "Punished",
    # "Chimera",
    "Phantom",
    "Withered",
    "Tainted",
    # "THE",
    "Full-Art"
]
DELIMITERS_2025 = [
    "Funtime",
    "Doppelganger",
    "Corrupted",
    "Twisted",
    "Altered",
    "True-Ending",
    "Glitched",
    "Bootleg",
    "Uncanny",
    "Long",
    "Isekai'd"
]
ALL_DELIMITERS = DELIMITERS_2024 + DELIMITERS_2025

"""List of all AFC teams."""
AFC_EAST_TEAMS_TO_ACRONYM = {
    "New England Patriots": "NE",
    "Buffalo Bills": "BUF",
    "Miami Dolphins": "MIA",
    "New York Jets": "NYJ"
}
AFC_NORTH_TEAMS_TO_ACRONYM = {
    "Pittsburgh Steelers": "PIT",
    "Baltimore Ravens": "BAL",
    "Cincinnati Bengals": "CIN",
    "Cleveland Browns": "CLE"
}
AFC_SOUTH_TEAMS_TO_ACRONYM = {
    "Jacksonville Jaguars": "JAX",
    "Houston Texans": "HOU",
    "Indianapolis Colts": "IND",
    "Tennessee Titans": "TEN"
}
AFC_WEST_TEAMS_TO_ACRONYM = {
    "Denver Broncos": "DEN",
    "Los Angeles Chargers": "LAC",
    "Kansas City Chiefs": "KC",
    "Las Vegas Raiders": "LV"
}
AFC_TEAMS_TO_ACRONYM = (
    AFC_EAST_TEAMS_TO_ACRONYM | AFC_NORTH_TEAMS_TO_ACRONYM | AFC_SOUTH_TEAMS_TO_ACRONYM | AFC_WEST_TEAMS_TO_ACRONYM
)

NFC_EAST_TEAMS_TO_ACRONYM = {
    "Philadelphia Eagles": "PHI",
    "Dallas Cowboys": "DAL",
    "Washington Commanders": "WAS",
    "New York Giants": "NYG"
}
NFC_NORTH_TEAMS_TO_ACRONYM = {
    "Chicago Bears": "CHI",
    "Green Bay Packers": "GB",
    "Minnesota Vikings": "MIN",
    "Detroit Lions": "DET"
}
NFC_SOUTH_TEAMS_TO_ACRONYM = {
    "Carolina Panthers": "CAR",
    "Tampa Bay Buccaneers": "TB",
    "Atlanta Falcons": "ATL",
    "New Orleans Saints": "NO"
}
NFC_WEST_TEAMS_TO_ACRONYM = {
    "Seattle Seahawks": "SEA",
    "Los Angeles Rams": "LAR",
    "San Francisco 49ers": "SF",
    "Arizona Cardinals": "ARI"
}
NFC_TEAMS_TO_ACRONYM = (
    NFC_EAST_TEAMS_TO_ACRONYM | NFC_NORTH_TEAMS_TO_ACRONYM | NFC_SOUTH_TEAMS_TO_ACRONYM | NFC_WEST_TEAMS_TO_ACRONYM
)

class Player():
    def __init__(self, name: str, team: str, position: str, ppr: float):
        self.name: str = name
        self.team: str = team
        self.position: str = position
        self.ppr: float = ppr
    
    def as_csv_return_string(self) -> str:
        """Returns a string that will be printed to our position CSV."""
        return self.name + ";" + self.team.upper()

def duplicate_player(player_name: str) -> str:
    """Duplicates the player, returning a new string object with a delimiter."""
    return "* " + ALL_DELIMITERS[random.randint(0, len(ALL_DELIMITERS) - 1)] + " " + player_name

def add_duplicates(players: list[str], chance: float) -> list[str]:
    """Adds random-chance duplicates to a list, returning said object."""
    return_list: list[str] = []
    for player_name in players:
        return_list.append(player_name)
        if random.random() <= chance:
            return_list.append(duplicate_player(player_name))
            if random.random() <= 0.01:
                return_list.append("* Ultra-Rare " + player_name)

    return return_list

def write_to_csv(file: TextIOWrapper, list_of_players: list[str]) -> None:
    """Writes the list of players to the csv."""
    writer = csv.writer(file)
    for player in list_of_players:
        writer.writerow([player])

def stats_directory_name(season_year: int) -> str:
    """Creates the name of the directories to hold PPR stats."""
    return str(season_year) + " Season"

def print_top_k_players(k: int, position: str, players: list[str]) -> list[str]:
    """Prints top min(k, len(players)) players for a position."""
    k = min(k, len(players))

    for i, player_line in enumerate(players[len(players) - k:len(players)]):
        player, team = player_line.split(";")
        duplicated_text: str = ""

        # If 0th character is an asterisk, it means the player was duplicated
        if len(player) > 0 and player[0] == "*":
            duplicated_text = "[duplicated player]"

        print(f"{position} {i + 1}: {player} ({team}) {duplicated_text}")