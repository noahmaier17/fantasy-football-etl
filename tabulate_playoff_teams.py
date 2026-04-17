"""
For every team, we determine if they are a playoff team for the given year.

Note: InquirerPy has very lousy typing, so utilized `Any` frequently.
"""

from InquirerPy import separator
from InquirerPy.resolver import prompt
from pathlib import Path
from typing import Any, Optional
import argparse

import helper_functions

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("year", help="what year's season to add playoff team information to", type=int)
    args = parser.parse_args()

    tabulate_playoff_teams(args.year)

def tabulate_playoff_teams(playoff_year: Optional[int]=None):
    # Asks the year we are focused on
    if playoff_year == None:
        season_year: int = int(input("Playoff year: "))
    else:
        season_year: int = playoff_year

    # We need to have this directory and corresponding text document created if it does not exist
    new_directory_name = helper_functions.stats_directory_name(season_year)
    directory_path = Path(new_directory_name)

    file_name = new_directory_name + "/playoff_teams.txt"

    # Creates this directory based on the season name if it does not exist
    if not directory_path.is_dir():
        directory_path.mkdir()

    AFC_questions: list[dict[str, Any]] = [
        {
            'type': 'checkbox',
            'message': 'Which AFC teams are in the playoffs?',
            'choices': (
                [separator.Separator("AFC EAST")] +
                list(helper_functions.AFC_EAST_TEAMS_TO_ACRONYM.keys()) +
                [separator.Separator("AFC NORTH")] +
                list(helper_functions.AFC_NORTH_TEAMS_TO_ACRONYM.keys()) +
                [separator.Separator("AFC SOUTH")] +
                list(helper_functions.AFC_SOUTH_TEAMS_TO_ACRONYM.keys()) +
                [separator.Separator("AFC WEST")] +
                list(helper_functions.AFC_WEST_TEAMS_TO_ACRONYM.keys())
            )
        }
    ]
    
    selected_AFC_teams: Any = prompt(AFC_questions)[0]
    assert len(selected_AFC_teams) == 7, "Number of selected AFC teams is not 7"

    NFC_questions: list[dict[str, Any]] = [
        {
            'type': 'checkbox',
            'message': 'Which NCF teams are in the playoffs?',
            'choices': (
                [separator.Separator("NFC EAST")] +
                list(helper_functions.NFC_EAST_TEAMS_TO_ACRONYM.keys()) +
                [separator.Separator("NFC NORTH")] +
                list(helper_functions.NFC_NORTH_TEAMS_TO_ACRONYM.keys()) +
                [separator.Separator("NFC SOUTH")] +
                list(helper_functions.NFC_SOUTH_TEAMS_TO_ACRONYM.keys()) +
                [separator.Separator("NFC WEST")] +
                list(helper_functions.NFC_WEST_TEAMS_TO_ACRONYM.keys())
            )
        }
    ]
    
    selected_NFC_teams: Any = prompt(NFC_questions)[0]
    assert len(selected_NFC_teams) == 7, "Number of selected NFC teams is not 7"

    with open(file_name, "w") as f:
        for team in selected_AFC_teams:
            f.write(helper_functions.AFC_TEAMS_TO_ACRONYM[team] + "\n")
        for team in selected_NFC_teams:
            f.write(helper_functions.NFC_TEAMS_TO_ACRONYM[team] + "\n")

if __name__ == "__main__":
    main()