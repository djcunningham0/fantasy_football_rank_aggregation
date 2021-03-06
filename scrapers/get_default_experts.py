import pandas as pd
from datetime import datetime as dt
import os
from scrapers.utils import *  # TODO: don't import *


# Note: these are being scraped from FantasyPros, so we can't get data for past weeks

def get_draft_experts(directory=None, verbose=False):
    year = get_current_season()

    if directory is None:
        directory = "./experts/" + str(year)

    std_df = get_expert_list("https://www.fantasypros.com/nfl/rankings/consensus-cheatsheets.php")
    half_df = get_expert_list("https://www.fantasypros.com/nfl/rankings/half-point-ppr-cheatsheets.php")
    ppr_df = get_expert_list("https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php")

    std_file = f'{str(year)}_expert_list_draft_STD.csv'
    half_file = f'{str(year)}_expert_list_draft_HALF.csv'
    ppr_file = f'{str(year)}_expert_list_draft_PPR.csv'

    write_expert_list(std_df, filename=std_file, directory=directory, verbose=verbose)
    write_expert_list(half_df, filename=half_file, directory=directory, verbose=verbose)
    write_expert_list(ppr_df, filename=ppr_file, directory=directory, verbose=verbose)


def get_weekly_experts(directory=None, verbose=False):
    year = get_current_season()
    week = get_latest_week()

    if directory is None:
        directory = "./experts/" + str(year)

    # I'm making the lazy assumption that the default FantasyPros experts are the same for each position
    # TODO: don't make this lazy assumption
    url_dict = {
        'STD': 'https://www.fantasypros.com/nfl/rankings/',
        'HALF': 'https://www.fantasypros.com/nfl/rankings/half-point-ppr-',
        'PPR': 'https://www.fantasypros.com/nfl/rankings/ppr-'
    }
    for pos in ['qb', 'rb', 'wr', 'te', 'flex', 'qb-flex', 'dst', 'k']:
        # scoring options depend on whether position is affected by PPR
        if pos in ['qb', 'dst', 'k']:
            scoring_opts = ['STD']
        else:
            scoring_opts = ['STD', 'PPR', 'HALF']

        for scoring in scoring_opts:
            url = f'{url_dict[scoring]}{pos}.php'  # e.g., https://www.fantasypros.com/nfl/rankings/ppr-rb.php
            df = get_expert_list(url)

            filename = f'{str(year)}_expert_list_week{str(week)}_{pos.upper()}_{scoring}.csv'
            write_expert_list(df, filename=filename, directory=directory, verbose=verbose)


def get_expert_list(url):

    expert_list = []
    soup = get_soup(url)
    tr = soup.find_all("tr")

    for row in tr:
        if row.find("input", class_="expert") is not None:
            info = row.find_all("a")
            # print(row)
            name = info[0].text
            site = info[1].text

            attrs = row.find("input").attrs
            if 'checked' in attrs and attrs['checked'] == 'checked':
                checked = True
            else:
                checked = False

            expert_list.append([name, site, checked, dt.today().strftime("%Y%m%d")])

    df = pd.DataFrame(expert_list)
    df.columns = ["Expert", "Site", "checked", "scraped_date"]

    return df


def write_expert_list(df, filename, directory, verbose=False):

    if filename[-4:] != ".csv":
        filename += ".csv"

    directory = fix_directory_name(directory)
    filename = directory + filename
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    if verbose:
        print("Writing " + filename)

    df.to_csv(filename, index=False)
