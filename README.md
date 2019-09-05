# fantasy_football_rank_aggregation

This repository contains the code I'm using to create fantasy football ranks. There's a
brief write-up about my methodology on Medium:
https://towardsdatascience.com/the-lazy-data-scientists-fantasy-football-rankings-76e941681a63

This is a work in progress right now. The process is very manual and I plan on automating
it more this season, so there will likely be major changes to the code and repo
structure.

## Rankings

For now, I'll be placing rankings in the following Dropbox folder. I'll try to keep them
up to date and I'll eventually find a better way to publish them.

Dropbox link: https://www.dropbox.com/sh/kgksdr8qjf19nx6/AACrO14benkYQdcMECagmGpxa?dl=0

## Code

I'm planning to make a lot of changes to the code this season, so more documentation to come.

The `scrapers/` directory contains code to scrape rankings from individual experts. It also has
a script to scrape the list of "checked" experts on FantasyPros (the experts that FantasyPros
considers worthy of inclusion in their composite ranks). For now I'm being lazy and using the
same list as them.

`update_draft_rankings.py` and `update_current_week.py` are wrappers around the code in 
`scrapers/` that I run manually to pull the rankings at the current point in time.

The `draft_2019.ipynb` notebook shows how I'm aggregating the rankings from individual experts.
Eventually I'll get that to run for weekly rankings and automate it.

## Dependencies

If you want to experiment with the code yourself, you'll need to install my rankaggregation
package, available on PyPI:
```
pip install rankaggregation
```

The source code for that package is on GitHub:
https://github.com/djcunningham0/rankaggregation
