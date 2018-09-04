from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
from io import StringIO
from datetime import datetime


def get_soup(url, headers=None, verbose=True):
    result = requests.get(url, headers=headers)
    if result.status_code != 200:
        if verbose:
            print("Failed to connect to {} with error code: {}".format(url, result.status_code))
        return None
    else:
        soup = bs(result.content, 'html5lib')
        return soup


def scrape_draft_rankings(year=None, directory="rankings/draft/"):
    if year is None:
        now = datetime.now()
        if now.month > 2:
            year = now.year
        else:
            year = now.year - 1

    if directory[-1] != "/":
        directory += "/"

    for scoring in ['STD', 'PPR', 'HALF']:
        for source in range(700):
            url = "https://partners.fantasypros.com/external/widget/nfl-staff-rankings.php?source=" \
                  + str(source) \
                  + "&year=2018&week=0&position=ALL&scoring=" \
                  + str(scoring) \
                  + "&ajax=true&width=640&export=xls"

            soup = get_soup(url)

            # [2:-1] strips some empty and unneeded lines
            table = soup.text.replace('\t\n', '\n').replace(' \t', '\t').replace('\t ', '\t').split('\n')[2:-1]

            # this puts it in a format that Pandas can read into a DataFrame
            data = StringIO('\n'.join(table))

            # read into a DataFrame
            df = pd.read_table(data)

            # only continue if this source actually has rankings (and get the fantasypros consensus once)
            if ('Unnamed: 4' not in df.columns) or (source == 0):
                print(str(source) + "_" + scoring)

                if source == 0:
                    source = "fantasypros_consensus"

                filename = "_".join([str(year), str(source), str(scoring)]) + ".csv"
                df.to_csv(directory + filename)
