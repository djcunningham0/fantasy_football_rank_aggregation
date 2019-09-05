from bs4 import BeautifulSoup as bs
import requests
from datetime import datetime


def get_soup(url, headers=None, verbose=True):
    """
    Get the HTML for a given URL using the BeautifulSoup library.

    :return: a BeautifulSoup object
    """
    result = requests.get(url, headers=headers)
    if result.status_code != 200:
        if verbose:
            print(f'Failed to connect to {url} with error code: {result.status_code}')
        return None
    else:
        soup = bs(result.content, 'html5lib')
        return soup


def get_current_season():
    """
    Gets the year of the current fantasy football season. If March or later, return this calendar year. Otherwise,
    return last year.

    :return: the year of the current fantasy football season
    """
    now = datetime.now()
    if now.month > 2:
        year = now.year
    else:
        year = now.year - 1

    return year


def get_latest_week(year=None, max_week=17):
    """
    Gets the latest week of a given season with weekly rankings.

    :param year: the season to pull rankings for (defaults to current season year)
    :param max_week: the latest week to begin looking for ranks (defaults to last week of regular season)
    :return: the latest week with rankings
    """
    if year is None:
        year = get_current_season()

    week = max_week
    found = False

    while not found and week > 0:
        url = "https://partners.fantasypros.com/external/widget/nfl-staff-rankings.php?source=0&year=" \
              + str(year) \
              + "&week=" \
              + str(week) \
              + "&position=QB&scoring=STD&ajax=true&export=xls"
        soup = get_soup(url)

        if soup.text != "no data available":
            found = True
        else:
            week -= 1

    return week


def fix_directory_name(directory):  # TODO: replace occurences of this with os.path.join
    """
    Add a backslash the end of the directory name if it doesn't already have one.
    """
    if directory[-1] != "/":
        directory += "/"

    return directory
