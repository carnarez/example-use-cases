"""Scrape meridian data from Wikipedia and build the dataset."""

import random
import string
import sys
import time
import typing

import numpy as np
import requests

from bs4 import BeautifulSoup

size: int = 1

grid: typing.Tuple[int, int] = (45, 90)
land: np.array = np.zeros((180 * size, 360 * size), dtype=np.int8)
wiki: str = "https://en.wikipedia.org/wiki"

svg: string.Template = string.Template(
    '<?xml version="1.0" encoding="utf-8" ?>\n'
    "<svg "
    'width="$width" height="$height" '
    'version="1.2" '
    'xmlns="http://www.w3.org/2000/svg" '
    'xmlns:ev="http://www.w3.org/2001/xml-events" '
    'xmlns:xlink="http://www.w3.org/1999/xlink"'
    ">"
    "<defs />"
    "$plot"
    "</svg>"
)

svg_point: string.Template = string.Template(
    "<rect "
    'x="$x" y="$y" '
    'rx="$rx" ry="$ry" '
    'width="$width" height="$width" '
    'fill="$color" $style '
    "/>"
)


def _ith(i: int) -> str:
    """Guess the ordinal suffix of an integer.

    Parameters
    ----------
    i : int
        The integer to process.

    Returns
    -------
    : str
        Integer as a string include the ordinal suffix.
    """
    n = str(i)

    if n.endswith("1") and not n.endswith("11"):
        return f"{n}st"

    if n.endswith("2") and not n.endswith("12"):
        return f"{n}nd"

    if n.endswith("3") and not n.endswith("13"):
        return f"{n}rd"

    else:
        return f"{n}th"


def _nth(lat: float, lng: float) -> typing.List[int]:
    """Apply the resolution transformation to convert coordinates to integers.

    Parameters
    ----------
    lat : float
        Latitude to process.
    lat : float
        Latitude to process.

    Returns
    -------
    : typing.List[int]
        Latitude and longitude as integers, according to the chosen resolution and
        grid-step size.
    """
    return list(map(lambda x: int(round(x * size, 0)), (lat, lng)))


def fetch_content(url: str) -> str:
    """Fetch the content to be scraped.

    If the content is not found in the current folder, fetch it from Wikipedia and save
    it for later use, to avoid pinging the website constantly (and potentially get
    banned). Make sure the `.html` files are in the `.gitignore`!

    Parameters
    ----------
    url : str
        The URL of the page to fetch.

    Returns
    -------
    : str
        HTML content to be scraped.
    """
    filename = f'{url.replace(f"{wiki}/", "")}.html'

    try:
        with open(filename, "r") as f:
            html = f.read()
        sys.stderr.write(f'Reading local "{filename}"\n')

    except FileNotFoundError:
        html = requests.get(url).content.decode()

        with open(filename, "w") as f:
            f.write(html)

        time.sleep(random.uniform(2.0, 5.0))  # for good measure
        sys.stderr.write(f'Downloading "{url}"\n')

    return html


def scrape_all(arr: np.array) -> np.array:
    """Scrape all involved pages.

    Parameters
    ----------
    arr : numpy.array
        The array to fill up with data (forwarded to `scrape_one()`).

    Returns
    -------
    : numpy.array
        Filled array.
    """
    arr = scrape_one(f"{wiki}/IERS_Reference_Meridian", arr)
    arr = scrape_one(f"{wiki}/180th_meridian", arr)

    for i in range(1, 180):
        arr = scrape_one(f"{wiki}/{_ith(i)}_meridian_east", arr)
        arr = scrape_one(f"{wiki}/{_ith(i)}_meridian_west", arr)

    return arr


def scrape_one(url: str, arr: np.array) -> np.array:
    """Scrape a single page.

    Parameters
    ----------
    url : str
        The URL of the page to scrape.
    arr : numpy.array
        The array to fill up with data.

    Returns
    -------
    : numpy.array
        Filled array.
    """
    soup = BeautifulSoup(fetch_content(url), "html.parser")

    table = soup.select("table.wikitable")[0]
    for row in table.select("tr"):
        try:
            cell = row.select("td")[0]

            # fetch coordinates
            lat, lng = map(float, cell.select("span.geo")[0].text.split(";"))
            latth, lngth = _nth(np.abs(lat - 90.0), lng + 180.0)

            # land (1) or sea (2), depending on table cell background colour
            # sea will be swapped to 0 in the next step
            lnd = 2 if "style" in cell.attrs else 1
            arr[latth, lngth] = lnd

        except IndexError:
            pass

    return arr


def approximate_unknown(arr: np.array) -> np.array:
    """If the array resolution is higher than the data, fill up the missing values.

    Parameters
    ----------
    arr : numpy.array
        The array to fill up with data (forwarded to `scrape_one()`).

    Returns
    -------
    : numpy.array
        Filled array.

    Notes
    -----
    All this could be done neater (and faster) with
    [`numpy.convolve()`](https://numpy.org/doc/stable/reference/generated/numpy.convolve.html)
    but keeping things as loops for clarity.
    """
    if len(np.where(arr == 0)[0]):

        # only water up there
        arr[0, :] = 2

        # first pass: approximate unknown latitudes
        # applied only on the known longitudes
        for lng in range(0, 360 * size, size):
            for lat in range(1, 180 * size):
                if not arr[lat, lng]:
                    arr[lat, lng] = arr[lat - 1, lng]

    if len(np.where(arr == 0)[0]):

        # second pass: approximate unknown longitudes
        for lat in range(1, 180 * size):
            for lng in range(0, 360 * size, size):
                curr_value = arr[lat, lng]

                try:
                    next_value = arr[lat, lng + size]
                except IndexError:
                    next_value = arr[lat, 0]

                if curr_value == next_value:
                    arr[lat, lng : lng + size] = curr_value
                else:
                    arr[lat, lng : lng + size // 2] = curr_value
                    arr[lat, lng + size // 2 : lng + size] = next_value

    arr[np.where(arr == 2)] = 0  # sea is absence of land

    return arr


def average_grid(arr: np.array) -> np.array:
    """Average to the chosen [smaller] grid size.

    Parameters
    ----------
    arr : numpy.array
        The array to fill up with data (forwarded to `scrape_one()`).

    Returns
    -------
    : numpy.array
        Filled array.
    """
    avg: np.array = np.zeros(grid, dtype=np.int8)

    fx = 180 * size // grid[0]
    fy = 360 * size // grid[1]

    hfx = fx // 2
    hfy = fy // 2

    nlat, nlng = arr.shape

    # periodic boundary conditions
    arr_pbc = np.hstack((arr[:, nlng - hfy : nlng], arr))
    arr_pbc = np.hstack((arr_pbc, arr[:, 0:hfy]))

    # averages
    for lat in range(grid[0]):
        for lng in range(grid[1]):
            lat_min = 0 if lat * fx - hfx < 0 else lat * fx - hfx
            lat_max = nlat if lat * fx + hfx >= nlat else lat * fx + hfx
            lng_min = lng * fy
            lng_max = lng * fy + 2 * hfy
            avg[lat, lng] = int(
                round(np.mean(arr_pbc[lat_min:lat_max, lng_min:lng_max]), 0)
            )

    return avg


def render_plot(
    arr: np.array,
    radius: int,
    margin: int,
    colors: typing.Dict[int, str] = {0: "#0969da", 1: "#39d353"},
    styles: typing.Dict[str, str] = {},
) -> str:
    """Generate the SVG plot.

    Parameters
    ----------
    arr : numpy.array
        The array of data to process.
    radius : int
        Size of the points.
    margin: int
        Distance between ppints.
    colors : typing.Dict[int, str]
        Dictionary of colors for the two types of points. Defaults to
        `{0: "#0969da", 1: "#39d353"}`.
    styles : typing.Dict[str, str]
        Extra style to apply to the SVG points. Defaults to an empty dictionary.

    Returns
    -------
    : str
        All SVG objects concatenated as a string.
    """
    shape = styles.pop("shape", "square").lower()
    if shape in ["s", "square"]:
        rxy = f"{radius*0.25:.2f}"
    elif shape in ["c", "circle"]:
        rxy = f"{radius*0.5:.2f}"
    else:
        raise NotImplementedError(f'Shape "{shape}" is unknown.')

    points = ""
    nlat, nlng = arr.shape
    for lat in range(nlat):
        for lng in range(nlng):
            points += svg_point.substitute(
                x=lng * (radius + margin) + margin,
                y=lat * (radius + margin) + margin,
                rx=rxy,
                ry=rxy,
                width=radius,
                color=colors[arr[lat, lng]],
                style=" ".join([f'{k}="{v}"' for k, v in styles.items()]),
            )

    return points


if __name__ == "__main__":
    filename = f"dataset-{size}.npy"

    try:
        land = np.load(filename)
    except FileNotFoundError:
        land = scrape_all(land)
        land = approximate_unknown(land)
        np.save(filename, land)

    if grid != (180 * size, 360 * size):
        land = average_grid(land)

    radius = 8
    margin = 1
    nlat, nlng = land.shape

    sys.stdout.write(
        svg.substitute(
            width=f"{nlng*(radius + margin) + 2*margin}px",
            height=f"{nlat*(radius + margin) + 2*margin}px",
            plot=render_plot(land, radius, margin, styles={"shape": "circle"}),
        ).strip()
    )
