# Module `dataset`

Scrape meridian data from Wikipedia and build the dataset.

**Functions:**

* [`fetch_content()`](#datasetfetch_content): Fetch the content to be scraped.
* [`scrape_all()`](#datasetscrape_all): Scrape all involved pages.
* [`scrape_one()`](#datasetscrape_one): Scrape a single page.
* [`approximate_unknown()`](#datasetapproximate_unknown): If the array resolution is higher than the data, fill up the missing values.
* [`average_grid()`](#datasetaverage_grid): Average to the chosen [smaller] grid size.
* [`render_plot()`](#datasetrender_plot): Generate the SVG plot.

## Functions

### `dataset.fetch_content`

```python
fetch_content(url: str) -> str:
```

Fetch the content to be scraped.

If the content is not found in the current folder, fetch it from Wikipedia and save
it for later use, to avoid pinging the website constantly (and potentially get
banned). Make sure the `.html` files are in the `.gitignore`!

**Parameters:**

* `url` [`str`]: The URL of the page to fetch.

**Returns:**

* [`str`]: HTML content to be scraped.

### `dataset.scrape_all`

```python
scrape_all(arr: np.array) -> np.array:
```

Scrape all involved pages.

**Parameters:**

* `arr` [`numpy.array`]: The array to fill up with data (forwarded to `scrape_one()`).

**Returns:**

* [`numpy.array`]: Filled array.

### `dataset.scrape_one`

```python
scrape_one(url: str, arr: np.array) -> np.array:
```

Scrape a single page.

**Parameters:**

* `url` [`str`]: The URL of the page to scrape.
* `arr` [`numpy.array`]: The array to fill up with data.

**Returns:**

* [`numpy.array`]: Filled array.

### `dataset.approximate_unknown`

```python
approximate_unknown(arr: np.array) -> np.array:
```

If the array resolution is higher than the data, fill up the missing values.

**Parameters:**

* `arr` [`numpy.array`]: The array to fill up with data (forwarded to `scrape_one()`).

**Returns:**

* [`numpy.array`]: Filled array.

**Notes:**

All this could be done neater (and faster) with
[`numpy.convolve()`](https://numpy.org/doc/stable/reference/generated/numpy.convolve.html)
but keeping things as loops for clarity.

### `dataset.average_grid`

```python
average_grid(arr: np.array) -> np.array:
```

Average to the chosen [smaller] grid size.

**Parameters:**

* `arr` [`numpy.array`]: The array to fill up with data (forwarded to `scrape_one()`).

**Returns:**

* [`numpy.array`]: Filled array.

### `dataset.render_plot`

```python
render_plot(
    arr: np.array, 
    radius: int, 
    margin: int, 
    colors: typing.Dict[int, str], 
    styles: typing.Dict[str, str],
) -> str:
```

Generate the SVG plot.

**Parameters:**

* `arr` [`numpy.array`]: The array of data to process.
* `radius` [`int`]: Size of the points.
margin: int
    Distance between ppints.
* `colors` [`typing.Dict[int, str]`]: Dictionary of colors for the two types of points. Defaults to
    `{0: "#0969da", 1: "#39d353"}`.
* `styles` [`typing.Dict[str, str]`]: Extra style to apply to the SVG points. Defaults to an empty dictionary.

**Returns:**

* [`str`]: All SVG objects concatenated as a string.
