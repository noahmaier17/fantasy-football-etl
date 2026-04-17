# Fantasy Football ETL Pipeline

## Project Description

Replaced a manual system of fetching NFL player statistics for the purpose of drafting a post-season fantasy football team (a format not supported by the variety of fantasy football apps) with an automated pipeline. Filters players based on team, sorts the players by regular season total PPR, and groups the players by position. Saved 3+ hours of manual work per draft, and has been used for a league of 10-12 players. 

## Tech Stack

Python - Main programming language.

InquirerPy - Used for handling user input.

requests - Fetches the API JSON data.

pandas - Used to flatten the fetched API data. 

colorama - Creates nice-looking command line text colors.

Sleeper API - the API for fetching the player statistics. See [https://docs.sleeper.com/](https://docs.sleeper.com/).

## How to Run

### Installation
```
pip install -e .
```

### Running Script: ETL Pipeline
```
run-fetch-post-season-players year manager_count [options]
```
**Required arguments:**
- `year` - year of the regular season.
- `manager_count` - the number of managers.

**Optional arguments:**
- `--duplication_odds` - chance to duplicate a player to add more positional depth. Default is 2/9.
- `--qb_count` — number of QBs to include. Default is (manager_count * 2 + 2).
- `--ignore_cache_csv` — bypass cached CSV and fetch fresh data.
- `--override_playoff_teams` — overrides the playoff teams for the input year.

**Example:**
```
run-fetch-post-season-players 2024 12 --duplication_odds 0.33
```

### Running Script: Setting Playoff NFL Teams
```
run-tabulate-playoff-teams year
```
**Required arguments:**
- `year` - what year's season to add playoff team information to.

**Example:**
```
run-tabulate-playoff-teams 2024
```

## Project File Structure

- `main.py` - Runs the ETL pipeline.
- `tabulate_playoff_teams.py` - Asks the user to manually input what teams are in the playoffs for the given year (any API I could find that could fetch this data was expensive). Can be run on its own.
- `helper_functions.py` - For this small project, all helper functions are simply grouped in the same file. 

## Current Design Limitations

- The Google Auth service used to automate other aspects of this project (live scoring, sending the final CSVs to Google Drive) currently is not working. The majority of the most impactful aspects of this script are still functional however, and the non-functional parts have been moved to a git-ignored folder.
- It was difficult to find public-facing APIs for this project. [Sleeper](sleeper.com) was the only site I could find where this data was available without having to spend unreasonable amounts of money. As a result, to figure out what teams are in the post season, the user must input that information manually. That information is cached, so it only needs to be input once, but ideally the user inputs nothing. I considered using some sort of web scraping tool to get this information, but that seemed to be beyond the scope and needs of the project.
- I could implement more rigorous type checking on the input arguments and unit testing with something like `PyTest`, but given the small scope of this project neither are a big priority. 