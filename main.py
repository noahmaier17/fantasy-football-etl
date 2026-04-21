"""
Automatically creates separate CSV spread sheets by position for post-season fantasy football.
"""
from colorama import Fore, init
from fractions import Fraction
from enum import Enum
import csv
import os
import ast
import random
import argparse
import requests
import pandas as pd
from pathlib import Path
import tabulate_playoff_teams
from helper_functions import (
    stats_directory_name, 
    add_duplicates, 
    Player, 
    write_to_csv, 
    duplicate_player, 
    print_top_k_players
)

init(autoreset=True)

class Positions(str, Enum):
    """List of all player positions using how they are written in the CSV."""
    QB = 'QB'
    RB = 'RB'
    WR = 'WR'
    K = 'K'
    TE = 'TE'
    DEF = 'DEF'

"""Contains the positions in the CSV we are concerned with."""
FIRST_NAME_COLUMN_NAME = "player.first_name"
LAST_NAME_COLUMN_NAME = "player.last_name"
FANTASY_POSITION_COLUMN_NAME = "player.fantasy_positions"
TEAM_COLUMN_NAME = "team"
PPR_COLUMN_NAME = "stats.pts_ppr"

"""Gets the API URL, where URL_PREFIX{$season_year}URL_SUFFIX can fetch PPR stats for the given season_year."""
PLAYERS_URL_PREFIX = "https://api.sleeper.com/stats/nfl/"
PLAYERS_URL_SUFFIX = "?season_type=regular&position[]=DEF&position[]=K&position[]=QB&position[]=RB&position[]=TE&position[]=WR&order_by=pts_ppr"

def main():
    # PART 1: Extract
    # First, we must parse all of our arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("year", help="year of the regular season", type=int)
    parser.add_argument("manager_count", help="number of managers", type=int)
    parser.add_argument("--duplication_odds", help="chance to duplicate a player; default is 2/9", default=2/9)
    parser.add_argument("--qb_count", help="number of QBs to include; default is (manager_count * 2 + 2)", type=int, default=None)
    parser.add_argument("--ignore_cache_csv", help="bypass cached CSV and fetch fresh data", action="store_true")
    parser.add_argument("--override_playoff_teams", help="overrides the playoff teams for the input year", action="store_true")
    args = parser.parse_args()

    season_year: int = args.year
    ignore_cache: bool = args.ignore_cache_csv
    manager_count: int = args.manager_count
    duplication_odds: float | Fraction = args.duplication_odds
    qb_count: int | None = args.qb_count
    override_playoff_teams: bool = args.override_playoff_teams

    # Converts the duplication odds value to a float
    try:
        duplication_odds = float(Fraction(duplication_odds))
    except Exception:
        assert False, "--duplication_odds must be a float value"

    # Resolves default qb count behavior
    if qb_count is None:
        qb_count = manager_count * 2 + 2

    number_of_duplicate_qbs = max(qb_count - 14, 0)

    print(Fore.GREEN + f" --- Running script for {season_year} season for {manager_count} managers ---")

    # Next, we will see if we already cached this data, downloading it if not.
    # Alternatively, if we are using --ignore_cache, will download the content irregardless.
    directory_name = stats_directory_name(season_year)
    directory_path = Path(directory_name)

    csv_file_name = directory_name + "/players.csv"
    csv_file_path = Path(csv_file_name)
    
    if directory_path.is_dir() and csv_file_path.is_file() and not ignore_cache:
        print(Fore.YELLOW + f"> {season_year} stats are already cached locally, so skipping API call...")
    else:
        print(Fore.CYAN + f"Fetching {season_year} Sleeper PPR statistics...")

        # Makes the request for player stats
        players_url = PLAYERS_URL_PREFIX + str(season_year) + PLAYERS_URL_SUFFIX
        response = requests.get(players_url)

        if response.status_code == 200:
            json_data = response.json()
        
            # First makes the directory (or does nothing if it already exists)
            directory_path.mkdir(exist_ok=True)

            # Next creates a file and writes to it
            with open(csv_file_name, "w",  newline="") as file:
                normalized_json: pd.DataFrame = pd.json_normalize(json_data)
                
                normalized_json.to_csv(file)

    # We also need all the playoff teams. We do this manually by running tabulate_playoff_teams.py
    playoff_teams_file_name = directory_name + "/playoff_teams.txt"
    playoff_teams_file_path = Path(playoff_teams_file_name)
    if not(directory_path.is_dir() and playoff_teams_file_path.is_file()) or override_playoff_teams:
        print(Fore.CYAN + "Tabulating playoff teams...")
        tabulate_playoff_teams.tabulate_playoff_teams(playoff_year=season_year)

    # Reads that text file
    print(Fore.CYAN + "Reading playoff teams...")
    post_season_team_acronyms: set[str] = set()
    with open(playoff_teams_file_path, "r") as f:
        for line in f:
            if line != "": # We _skip that last, pesky empty line
                post_season_team_acronyms.add(line.strip())

    # PART 2: Transform
    # First, we will read the CSV and convert all that data into class objects.
    print(Fore.CYAN + "Reading CSV...")
    players: list[Player] = []

    # Reads the CSV
    with open(csv_file_name, mode = 'r') as file:
        csv_file = csv.reader(file)

        # In case something is buggy with the CSV, we check which teams we see players from
        set_of_team_names: set[str] = set()

        # First, we need to calculate our column numbers of this CSV
        header: list[str] = next(csv_file)

        FIRST_NAME_POS: int = header.index(FIRST_NAME_COLUMN_NAME)
        LAST_NAME_POS: int = header.index(LAST_NAME_COLUMN_NAME)
        FANTASY_POSITION_POS: int = header.index(FANTASY_POSITION_COLUMN_NAME)
        TEAM_POS = header.index(TEAM_COLUMN_NAME)
        PPR_POS: int = header.index(PPR_COLUMN_NAME)

        for i, line in enumerate(csv_file):
            # We skip the first line that just contains CSV information
            if i == 0:
                continue
            # And we skip lines that are malformed (which seem to only be empty lines)
            if len(line) <= 1:
                continue

            # Creates a player object with this position
            # We must convert the player's points into a float
            points = line[PPR_POS]
            if points == "":
                # If we have no points value, we can skip this line
                continue
            points = float(line[PPR_POS])

            # We will iterate across all positions they count as playing for
            for position in ast.literal_eval(line[FANTASY_POSITION_POS]): # We convert a string-representation list into a Python list
                player = Player(
                    line[FIRST_NAME_POS] + " " + line[LAST_NAME_POS], # Some player names have asterisks
                    line[TEAM_POS],
                    position,
                    points
                )

                # If this player is on a team in the post season, we add them to the players list
                if player.team in post_season_team_acronyms:
                    players.append(player)

                    # To check for accuracy, we will add this team name to a set. 
                    # If that set is missing certain team names, we have an error in our program.
                    set_of_team_names.add(player.team)

        # Checks if our sets do not match
        set_difference = post_season_team_acronyms - set_of_team_names
        assert len(set_difference) == 0, (
            "Did not discover any teams by the name: " + str(set_difference) + ".\n" +
            "Most likely cause is having an incorrectly set team acronym name."
        )

        # Prints successful reading
        print(Fore.YELLOW + f"> Processed {i} players.")

    # Next, we will sort all these player objects.
    print(Fore.CYAN + "Sorting players by ppr...")
    players = sorted(players, key=lambda p: p.ppr, reverse=False)

    # Third, for each player, we add them to their corresponding CSV list
    print(Fore.CYAN + "Separating and filtering players by position...")
    QBs: list[str] = []
    RBs: list[str] = []
    WRs: list[str] = []
    TEs: list[str] = []
    Ks: list[str] = []
    DEFs: list[str] = []
    for player in players:
        match player.position:
            case Positions.QB.value:
                QBs.append(player.as_csv_return_string())
            case Positions.RB.value:
                RBs.append(player.as_csv_return_string())
            case Positions.WR.value:
                WRs.append(player.as_csv_return_string())
            case Positions.TE.value:
                TEs.append(player.as_csv_return_string())
            case Positions.K.value:
                Ks.append(player.as_csv_return_string())
            case Positions.DEF.value:
                DEFs.append(player.name) # We do not need the team name for defenses
            case _:
                print(Fore.RED + "Possible error: Player " + player.name + " has a malformed position value of " + player.position)

    # Fourth, duplicates players.
    # Duplicates QBs (of the top 14 QBs, we will duplicate `number_of_duplicate_qbs` of them)
    # I chose top 14 because that should be, roughly, the 14 starting post season QBs
    print(
        Fore.CYAN + f"Adding duplicates (duplication odds: " +
        Fore.LIGHTCYAN_EX + f"{round(duplication_odds, 4)}" + 
        Fore.CYAN + ")...")
    new_QBs: list[str] = []
    random_qb_indexes_do_duplicate = random.sample(range(0, 14), number_of_duplicate_qbs)

    for i, player_string in enumerate(QBs):
        new_QBs.append(player_string)
        if i in random_qb_indexes_do_duplicate:
            new_QBs.append(duplicate_player(player_string))
    QBs = new_QBs

    # Duplicates all other positions
    RBs: list[str] = add_duplicates(RBs, duplication_odds)
    WRs: list[str] = add_duplicates(WRs, duplication_odds)
    TEs: list[str] = add_duplicates(TEs, duplication_odds)

    # PART 3: Load
    # As our last and final step, adds those values to physical CSVs.
    print(Fore.CYAN + "Creating directory...")
    load_directory_name = "Post Season Positions"
    try:
        os.mkdir(directory_name + '/' + load_directory_name)
    except FileExistsError:
        pass
    except PermissionError:
        assert False, Fore.RED + "Directory Creation Permissions Denied!"
    except Exception as e:
        assert False, Fore.RED + "Exception: " + str(e)

    print(Fore.CYAN + "Writing CSV Data...")
    with open(directory_name + '/' + load_directory_name + '/QBs.csv', 'w', newline="") as file:
        write_to_csv(file, QBs)

    with open(directory_name + '/' + load_directory_name +'/RBs.csv', 'w', newline="") as file:
        write_to_csv(file, RBs)

    with open(directory_name + '/' + load_directory_name +'/WRs.csv', 'w', newline="") as file:
        write_to_csv(file, WRs)

    with open(directory_name + '/' + load_directory_name +'/DEFs.csv', 'w', newline="") as file:
        write_to_csv(file, DEFs)

    with open(directory_name + '/' + load_directory_name +'/Ks.csv', 'w', newline="") as file:
        write_to_csv(file, Ks)

    with open(directory_name + '/' + load_directory_name +'/TEs.csv', 'w', newline="") as file:
        write_to_csv(file, TEs)

    # Shows results to pass sniff test of data
    print(Fore.GREEN + " --- Successfully created Post Season Fantasy Football player CSVs --- ")
    print(Fore.CYAN + "Aggregating top 3 players by position, including possible duplicates, for verification...")

    print_top_k_players(3, "QB", QBs)
    print()

    print_top_k_players(3, "RB", RBs)
    print()

    print_top_k_players(3, "WR", WRs)
    print()

    print_top_k_players(3, "TE", TEs)
    print()

    print_top_k_players(3, "K", Ks)

    print(
        Fore.GREEN + "Aggregate stats: " + 
        f"QB Count: {len(QBs)} | " +   
        f"RB Count: {len(RBs)} | " +   
        f"WR Count: {len(WRs)} | " +   
        f"TE Count: {len(TEs)} | " +   
        f"K Count: {len(Ks)} | " +
        f"DEF Count: {len(DEFs)}"
    )

if __name__ == "__main__":
    main()