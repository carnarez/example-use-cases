# Scraping meridians

In this little exercise to discover scraping processes we propose to
[scrape](https://www.crummy.com/software/BeautifulSoup/) _Wikipedia_ content: the
[list of meridians](https://en.wikipedia.org/w/index.php?title=Category:Meridians_(geography))
as a dataset to plot in a fancy 3D representation (bonus point for the fanciness).

As the resolution of such a description is not as fine as we would like, wrap an
[API](https://fastapi.tiangolo.com/) around your scraped dataset to serve averaged
situation (_e.g._, land or water) for any queried pair of coordinates.

One could also decide to plot instant plane positions extracted from the
[OpenSky Network](https://opensky-network.org/) (check out the
[documentation of the associated API](https://opensky-network.org/apidoc/))... how do
flight trajectories translate in various
[map projections](https://en.wikipedia.org/wiki/Map_projection)?
