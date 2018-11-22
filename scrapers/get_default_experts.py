import pandas as pd
from datetime import datetime as dt
import os
from scrapers.utils import *


# Note: these are being scraped from FantasyPros, so we can't get data for past weeks

def get_draft_experts(directory=None, verbose=False):
    year = get_current_season()

    if directory is None:
        directory = "./experts/" + str(year)

    url = "https://www.fantasypros.com/nfl/rankings/consensus-cheatsheets.php"
    df = get_expert_list(url)

    filename = str(year) + "_expert_list_draft.csv"
    write_expert_list(df, filename=filename, directory=directory, verbose=verbose)


def get_weekly_experts(directory=None, verbose=False):
    year = get_current_season()
    week = get_latest_week()

    if directory is None:
        directory = "./experts/" + str(year)

    # I'm making the lazy assumption that the default FantasyPros experts are the same for each position
    url = "https://www.fantasypros.com/nfl/rankings/qb.php"
    df = get_expert_list(url)

    filename = str(year) + "_expert_list_week" + str(week) + ".csv"
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
