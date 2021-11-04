# Scraping meridians

In this little exercise to discover scraping processes we propose to scrape _Wikipedia_
content: the
[list of meridians](https://en.wikipedia.org/w/index.php?title=Category:Meridians_(geography))
(decide for yourself following which of east of west direction is more enticing) as a
dataset to plot in a fancy 3D representatino (bonus point for the fanciness).

As the resolution of such a description is not as fine as we would like, wrap an API
around your scraped dataset to serve averaged situation (_e.g._, land or water) for any
queried coordinates.

One could also decide to plot instant plane positions extracted from the
[OpenSky Network](https://opensky-network.org/) (check out the
[documentation of the associated API](https://opensky-network.org/apidoc/))...
