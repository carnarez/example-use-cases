# Module `svg`

Quick script thing to draw the random walk of an irrational number.

Run with:

```bash
$ python3 -m venv .venv
$ .venv/bin/pip install --no-cache-dir -r requirements.txt
$ .venv/bin/python svg.py pi_rainbow-gradient.json > output.svg
```

Expected options are:

```yaml
plot:
  data:
    source: "constants/pi.dat"  # str: path to the source file including the decimals
    first: 0                    # int: first decimal to consider
    until: 1000                 # int: last decimal to consider
  color:
    gradient_start: "violet"    # str: start color of the gradient (hexadecimal code)
    gradient_until: "red"       # str: end color of the gradient
  format:
    min_width: 2480             # int: minimum width of the final plot
    max_width: 2480             # int: maximum width of the final plot
    min_height: 3508            # int: minimum height of the final plot
    max_height: 3508            # int: maximum height of the final plot
  style:
    ...                         # extra styling options for the SVG lines
```

Note that below is also valid (instead of the gradient syntax above):

```yaml
  ...
  color:
    0: "#00000f"                # str: color associated with a decimal digit equals to 0
    1: "#0000ff"                # str: color associated with a decimal digit equals to 1
    ...                        
    8: "#000fff"                # str: color associated with a decimal digit equals to 8
    9: "#00ffff"                # str: color associated with a decimal digit equals to 9
```

**Attributes:**

* `svg` [`string.Template`]: Template to render the overall `SVG` file. Variables substituted (in the following
    order):
    - `width`: width of the `<svg>` element.
    - `height`: height of the `<svg>` element.
    - `plot`: `<line>` elements defining the plot itself.
* `line_svg` [`string.Template`]: Template to render a single `<line>` element. Variables substituted:
    - `x1`, `y1`, `x2`, `y2`: coordinates of the extremities of the `<line>` element
      (_better call it a segment then..._).
    - `color`: color of the `<line>` element.
    - `style`: extra styling options for the `<line>` element.

**Functions:**

* [`fetch_config()`](#svgfetch_config): Read the configuration of the current plot.
* [`fetch_digits()`](#svgfetch_digits): Extract the decimals from the source file.
* [`color_scheme()`](#svgcolor_scheme): Define the color scheme used to light up the path.
* [`compute_coordinates()`](#svgcompute_coordinates): Generate the coordinates of each step of the path.
* [`rescale_coordinates()`](#svgrescale_coordinates): Rescale the whole plot to provided dimensions.
* [`render_plot()`](#svgrender_plot): Render the random walk plot using `SVG` `<line>`s.

## Functions

### `svg.fetch_config`

```python
fetch_config(source: str) -> typing.Dict[str, typing.Any]:
```

Read the configuration of the current plot.

**Parameters:**

* `source` [`str`]: Filepath to the configuration `JSON` file to ingest.

**Returns:**

* [`typing.Dict[str, typing.Any]`]: Dictionary of the configuration options.

### `svg.fetch_digits`

```python
fetch_digits(source: str, first: int, until: int) -> np.array:
```

Extract the decimals from the source file.

**Parameters:**

* `source` [`str`]: Filepath to the source file to ingest.
* `first` [`int`]: First decimal to consider.
* `until` [`int`]: Last decimal to consider.

**Returns:**

* [`numpy.array`]: `NumPy` array of the decimal digits.

### `svg.color_scheme`

```python
color_scheme(
    gradient_steps: int, 
    gradient_start: str, 
    gradient_until: str, 
    color_codes_10: typing.Union[typing.Dict[typing.Union[int, str], str], typing.List[str]],
) -> typing.List[colour.Color]:
```

Define the color scheme used to light up the path.

Color management in `Python` can be cumbersome... but check the pretty nifty
[`colour` package](https://github.com/vaab/colour), particularly useful to generate
gradients of random sizes.

**Parameters:**

* `gradient_steps` [`int`]: Number of colors to generate in the gradient. Defaults to `0`.
* `gradient_start` [`str`]: Initial color of the gradient. Defaults to `None`.
* `gradient_until` [`str`]: Last color of the gradient. Defaults to `None`.
* `color_codes_10` [`typing.Union[typing.Dict[typing.Union[int, str], str], typing.List[str]]`]: One color for each digit. Defaults to `None`.

**Returns:**

* [`typing.List[colour.Color]`]: List of colors, one for each digit, or list of colors interpolated from the
    defined gradient.

### `svg.compute_coordinates`

```python
compute_coordinates(digits: np.array, angle_step: float, recenter: bool) -> np.array:
```

Generate the coordinates of each step of the path.

**Parameters:**

* `digits` [`numpy.array`]: `NumPy` array of the decimal digits.
* `angle_step` [`float`]: Angle in between two digits. Defaults to `36.0`.
* `recenter` [`bool`]: Recenter the plot to avoid negative coordinates. Defaults to `True`.

**Returns:**

* [`numpy.array`]: `NumPy` array of the coordinates corresponding to each step.

### `svg.rescale_coordinates`

```python
rescale_coordinates(
    points: np.array, 
    min_width: int, 
    max_width: int, 
    min_height: int, 
    max_height: int, 
    keep_ratio: bool,
) -> np.array:
```

Rescale the whole plot to provided dimensions.

**Parameters:**

* `points` [`numpy.array`]: `NumPy` array of the coordinates corresponding to each step.
* `min_width` [`int`]: Minimum width of the plot. Defaults to `None`.
* `max_width` [`int`]: Maximum width of the plot. Defaults to `None`.
* `min_height` [`int`]: Minimum height of the plot. Defaults to `None`.
* `max_height` [`int`]: Maximum height of the plot. Defaults to `None`.
* `keep_ratio` [`bool`]: Make sure not to deform the plot. Defaults to `True`.

**Returns:**

* [`numpy.array`]: `NumPy` array of the rescaled coordinates corresponding to each step.

**Raises:**

* [`ValueError`]: If none of `max_width` or `max_height` is defined.

### `svg.render_plot`

```python
render_plot(
    digits: np.array, 
    points: np.array, 
    colors: typing.List[str], 
    styles: typing.Dict[str, str],
) -> str:
```

Render the random walk plot using `SVG` `<line>`s.

**Parameters:**

* `digits` [`numpy.array`]: `NumPy` array of the decimal digits.
* `points` [`numpy.array`]: `NumPy` array of the coordinates corresponding to each step.
* `colors` [`typing.List[str]`]: List of colors, one for each digit, or list of colors interpolated from the
    defined gradient.
* `styles` [`typing.Dict[str, str]`]: Extra styling options for the lines.

**Returns:**

* [`str`]: Rendered and collated `<line>`s corresponding to each step.
