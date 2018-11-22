import os
from io import StringIO
import pandas as pd
from scrapers.utils import *


def update_draft_and_current_week(year=None, week=None, verbose=False):
    """
    Scrape pre-draft and weekly rankings (current week) and write the results to CSV files.
    Write to default directories.
    """
    scrape_draft_rankings(verbose=verbose, year=year)
    scrape_weekly_rankings(verbose=verbose, year=year, week=week)

    if verbose:
        print("Done.")


def scrape_draft_rankings(year=None, directory=None, verbose=False):
    """
    Scrape pre-draft rankings from all FantasyPros sources and write the results to CSV files.

    :param year: year of the season to scrape rankings for (defaults to current season)
    :param directory: directory to write CSV files to (will be created if it doesn't exist)
    :param verbose: True to print messages when writing files
    """
    if year is None:
        year = get_current_season()

    if directory is None:
        directory = "./rankings/" + str(year) + "/draft/"

    directory = fix_directory_name(directory)

    for scoring in ['STD', 'PPR', 'HALF']:
        for source in range(700):  # TODO: refine this range
            df = do_scrape(source=source, year=year, week=0, pos="ALL", scoring=scoring)

            # only continue if this source actually has rankings (and get the fantasypros consensus once)
            if df is not None and (('Unnamed: 4' not in df.columns) or (source == 0)):
                write_df(df, directory, verbose=verbose)


def scrape_weekly_rankings(year=None, week=None, directory=None, verbose=False):
    """
    Scrape weekly rankings from all FantasyPros sources and write the results to CSV files.

    :param year: year of the season to scrape rankings for (defaults to current season)
    :param week: week to scrape weekly rankings for (defaults to latest week with rankings)
    :param directory: directory to write CSV files to (will be created if it doesn't exist)
    """

    if year is None:
        year = get_current_season()

    if week is None:
        week = get_latest_week(year=year)

    if directory is None:
        directory = "./rankings/" + str(year) + "/weekly/"

    if week < 1:
        if verbose:
            print("Use scrape_draft_rankings for pre-draft rankings.")
        return None

    directory = fix_directory_name(directory)

    for source in range(700):  # TODO: refine this range
        # start with QB to see if weekly ranks exist for this source
        df = do_scrape(source=source, year=year, week=week, pos="QB", scoring="STD")

        # if only three columns (Staff Composite, Player, Team), there are no expert ranks from this source
        if df is None or (len(df.columns) == 3 and source != 0):
            continue

        # if we made it this far, write the QB ranks to a file
        write_df(df, directory, verbose=verbose)

        # then continue with the other positions
        for pos in ['RB', 'WR', 'TE', 'FLX', 'DST', 'K']:
            # scoring options depend on whether position is affected by PPR
            if pos in ['DST', 'K']:
                scoring_opts = ['STD']
            else:
                scoring_opts = ['STD', 'PPR', 'HALF']

            for scoring in scoring_opts:
                df = do_scrape(source=source, year=year, week=week, pos=pos, scoring=scoring)
                if df is not None:
                    write_df(df, directory, verbose=verbose)


def do_scrape(source, year, week, pos, scoring):
    """
    Do the actual web scraping of the FantasyPros sources and return a Pandas DataFrame with the scraped rankings.

    :param source: a number representing the source ID
    :param year: the year of the season to scrape data for
    :param week: the week to scrape data for (0 for pre-draft rankings)
    :param pos: the position to scrape data for ("ALL" for all positions)
    :param scoring: the scoring format to scrape rankings for ("STD", "PPR", or "HALF")
    :return: a Pandas DataFrame
    """
    url = "https://partners.fantasypros.com/external/widget/nfl-staff-rankings.php?source=" \
          + str(source) \
          + "&year=" \
          + str(year) \
          + "&week=" \
          + str(week) \
          + "&position=" \
          + str(pos) \
          + "&scoring=" \
          + str(scoring) \
          + "&ajax=true&export=xls"

    soup = get_soup(url)
    if soup is None:
        return None

    # get the source name
    if source == 0:
        source_name = "FantasyPros consensus"
    else:
        source_name = soup.text.split('\t')[0].strip()

    # [2:-1] strips some empty and unneeded lines
    table = soup.text.replace('\t\n', '\n').replace(' \t', '\t').replace('\t ', '\t').split('\n')[2:-1]

    # this puts it in a format that Pandas can read into a DataFrame
    data = StringIO('\n'.join(table))

    # read into a DataFrame
    df = pd.read_table(data)

    # set some attributes on the DataFrame
    df.__setattr__("source", source)
    df.__setattr__("source_name", source_name)
    df.__setattr__("year", year)
    df.__setattr__("week", week)
    df.__setattr__("pos", pos)
    df.__setattr__("scoring", scoring)

    return df


def write_df(df, directory, verbose=False):
    """
    Write the scraped rankings (in a Pandas DataFrame) to a CSV file.

    :param df: dataframe containing scraped rankings
    :param directory: directory to write CSV files to (will be created if it doesn't exist)
    """
    directory = fix_directory_name(directory)

    source = df.source
    source_name = df.source_name
    year = df.year
    week = df.week
    pos = df.pos
    scoring = df.scoring

    if week == 0:
        week_str = "draft"
    else:
        # add week to the directory path
        week_str = "week" + str(week)
        directory += week_str + "/"

    filename = directory + "_".join([str(year), str(source), source_name, pos, scoring, week_str]) + ".csv"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    if verbose:
        print("writing " + filename)

    df.to_csv(filename, index=False)
