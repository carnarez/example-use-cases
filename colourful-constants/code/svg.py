"""Quick script thing to draw the random walk of an irrational number.

Run with:

```bash
$ python3 -m venv .venv
$ .venv/bin/pip install --no-cache-dir -r requirements.txt
$ .venv/bin/python svg.py pi_rainbow-gradient.json > output.svg
```

Expected options are:

```json
{
    "data": {
        "source": "str: path to the source filename including ALL the decimals",
        "first": "int: first decimal to consider",
        "until": "int: last decimal to consider"
    },
    "text": {
        "background": "str: large background filigrane text",
        "title": "str: title of the plot",
        "caption": "str: any subtitle to the plot"
    },
    "tone": {
        "gradient_start": "str: start color of the gradient (hexadecimal code)",
        "gradient_until": "str: end color of the gradient"
    }
}
```

Note that below is also valid (instead of the gradient syntax above):

```json
{
    ...
    "tone": {
        0: "str: color associated with a decimal digit equals to 0",
        1: "str: color associated with a decimal digit equals to 1",
        ...
        8: "str: color associated with a decimal digit equals to 8",
        9: "str: color associated with a decimal digit equals to 9"
    }
}
```

Attributes
----------
svg : string.Template
    Template to render the overall `SVG` file. Variables substituted (in the following
    order):
    - `width`: width of the `<svg>` element.
    - `height`: height of the `<svg>` element.
    - `text`: `<text>` elements acting as the legend of the plot.
    - `lines`: `<line>` elements defining the plot itself.
line_svg : string.Template
    Template to render a single `<line>` element. Variables substituted:
    - `x1`, `y1`, `x2`, `y2`: coordinates of the extremities of the `<line>` element
      (_better call it a segment then..._).
    - `color`: color of the `<line>` element.
text_svg : string.Template
    Template to render the textual content. Variables substituted:
    - `background`: large background filigrane text.
    - `backougrond_size`: font size of the background text.
    - `title`: title of the plot.
    - `title_size`: font size of the plot title.
    - `caption`: any subtitle to the plot.
    - `caption_size`: font size of the subtitle text.
"""

import math
import string
import sys
import typing

import colour
import numpy as np
import yaml

svg: string.Template = string.Template(
    '<?xml version="1.0" encoding="utf-8" ?>\n'
    '<svg '
    'width="$width" height="$height" '
    'version="1.2" '
    'xmlns="http://www.w3.org/2000/svg" '
    'xmlns:ev="http://www.w3.org/2001/xml-events" '
    'xmlns:xlink="http://www.w3.org/1999/xlink"'
    '>'
    '<defs />'
    '$text'
    '$plot'
    '$extras'
    '</svg>'
)

svg_line: string.Template = string.Template(
    '<line x1="$x1" y1="$y1" x2="$x2" y2="$y2" $style />'
)

svg_text: string.Template = string.Template('<text x="$x" y="$y" $style>$text</text>')


def fetch_config(source: str) -> typing.Dict[str, typing.Any]:
    """Read the configuration of the current plot.

    Parameters
    ----------
    source : str
        Filepath to the configuration `JSON` file to ingest.

    Returns
    -------
    : typing.Dict[str, typing.Any]
        Dictionary of the configuration options.
    """
    return yaml.load(open(source).read(), Loader=yaml.Loader)


def fetch_digits(source: str, first: int = 0, until: int = 100) -> np.array:
    """Extract the decimals from the source file.

    Parameters
    ----------
    source : str
        Filepath to the source file to ingest.
    first : int
        First decimal to consider.
    until : int
        Last decimal to consider.

    Returns
    -------
    : numpy.array
        `NumPy` array of the decimal digits.
    """
    digits: np.array = np.zeros(until - first, dtype=np.int8)

    # below gymnastics serves as a quick check to see if things fit in memory
    for n, d in enumerate(open(source).read().split(".")[1][first:until]):
        digits[n] += int(d)

    return digits


def color_scheme(
    gradient_steps: int = 0,
    gradient_start: str = None,
    gradient_until: str = None,
    color_codes_10: typing.Union[
        typing.Dict[typing.Union[int, str], str], typing.List[str]
    ] = None
) -> typing.List[colour.Color]:
    """Define the color scheme used to light up the path.

    Color management in `Python` can be cumbersome... but check the pretty nifty
    [`colour` package](https://github.com/vaab/colour), particularly useful to generate
    gradients of random sizes.

    Parameters
    ----------
    gradient_steps : int
        Number of colors to generate in the gradient. Defaults to `0`.
    gradient_start : str
        Initial color of the gradient. Defaults to `None`.
    gradient_until : str
        Last color of the gradient. Defaults to `None`.
    color_codes_10 : typing.Union[typing.Dict[typing.Union[int, str], str], typing.List[str]]
        One color for each digit. Defaults to `None`.

    Returns
    -------
    : typing.List[colour.Color]
        List of colors, one for each digit, or list of colors interpolated from the
        defined gradient.
    """
    colors: typing.List[colour.Color] = []

    if gradient_start is not None and gradient_until is not None:
        s = colour.Color(gradient_start)
        e = colour.Color(gradient_until)
        colors = list(s.range_to(e, gradient_steps))

    elif len(colour_array) == 10:
        if type(color_codes_10) == dict:
            colors = [colour.Color(color_codes_10[n]) for n in color_codes_10]
        else:
            colors = color_list

    return colors


def compute_coordinates(
    digits: np.array, angle_step: float = 36.0, recenter: bool = True
) -> np.array:
    """Generate the coordinates of each step of the path.

    Parameters
    ----------
    digits : numpy.array
        `NumPy` array of the decimal digits.
    angle_step : float
        Angle in between two digits. Defaults to `36.0`.
    recenter : bool
        Recenter the plot to avoid negative coordinates. Defaults to `True`.

    Returns
    -------
    : numpy.array
        `NumPy` array of the coordinates corresponding to each step.
    """
    points: np.array = np.zeros((digits.shape[0] + 1, 2), dtype=np.float32)

    for n, digit in enumerate(digits):
        angle = math.radians(digit*angle_step - 90.0)

        points[n + 1,0] += points[n,0] + math.cos(angle)
        points[n + 1,1] += points[n,1] + math.sin(angle)

    if recenter:
        xmin = np.min(points[:,0])
        ymin = np.min(points[:,1])
    
        points[:,0] -= xmin
        points[:,1] -= ymin

    return points


def rescale_coordinates(
    points: np.array,
    min_width: int = None,
    max_width: int = None,
    min_height: int = None,
    max_height: int = None,
    keep_ratio: bool = True
) -> np.array:
    """Rescale the whole plot to provided dimensions.

    Parameters
    ----------
    points : numpy.array
        `NumPy` array of the coordinates corresponding to each step.
    min_width : int
        Minimum width of the plot. Defaults to `None`.
    max_width : int
        Maximum width of the plot. Defaults to `None`.
    min_height : int
        Minimum height of the plot. Defaults to `None`.
    max_height : int
        Maximum height of the plot. Defaults to `None`.
    keep_ratio : bool
        Make sure not to deform the plot. Defaults to `True`.

    Returns
    -------
    : numpy.array
        `NumPy` array of the rescaled coordinates corresponding to each step.

    Raises
    ------
    : ValueError
        If none of `max_width` or `max_height` is defined.
    """
    factor: typing.Tuple[float, float] = ()

    xmax = np.max(points[:,0])
    ymax = np.max(points[:,1])

    if max_width is not None and max_height is not None:
        xf = max_width/xmax
        yf = max_height/ymax

        if keep_ratio:
            if ymax > xmax:
                xf = yf
            else:
                yf = xf

        factor = (xf, yf)

    elif max_width is not None and max_height is None:
        factor = (xmax, xmax)

    elif max_width is None and max_height is not None:
        factor = (ymax, ymax)

    else:
        raise ValueError('Provide at least one of "max_width" or "max_height".')

    points[:,0] *= factor[0]
    points[:,1] *= factor[1]

    xmax = np.max(points[:,0])
    ymax = np.max(points[:,1])

    if min_width is not None and xmax < min_width:
        points[:,0] += (min_width - xmax)/2

    if min_height is not None and ymax < min_height:
        points[:,1] += (min_height - ymax)/2

    return points


def render_plot(digits: np.array, points: np.array, colors: typing.List[str]) -> str:
    """Render the random walk plot using `SVG` `<line>`s.

    Parameters
    ----------
    digits : numpy.array
        `NumPy` array of the decimal digits.
    points : numpy.array
        `NumPy` array of the coordinates corresponding to each step.
    colors : typing.List[str]
        List of colors, one for each digit, or list of colors interpolated from the
        defined gradient.

    Returns
    -------
    : str
        Rendered and collated `<line>`s corresponding to each step.
    """
    lines: typing.List[str] = []

    for n, d in enumerate(digits):
        x1, y1 = points[n]
        x2, y2 = points[n + 1]

        try:
            color = colors[n]
        except KeyError:
            color = colors[d]

        lines.append(
            svg_line.substitute(
                color=color, x1=f"{x1:.4f}", x2=f"{x2:.4f}", y1=f"{y1:.4f}", y2=f"{y2:.4f}"
            )
        )

    return "".join(lines)


def render_text(points: np.array, **text: typing.Dict[str, str]) -> str:
    """Render a few `SVG` `<text>` elements.

    Parameters
    ----------
    points : numpy.array
        `NumPy` array of the coordinates corresponding to each step.
    text : typing.Dict[str, str]
        Dictionary of the various textual content.

    Returns
    -------
    : str
        Rendered `<text>` items.
    """
    ymax = np.max(points[:,1])

    return svg_text.substitute(
        background_size=f"{ymax:.0f}px",
        title_size=ymax*0.02,
        caption_size=ymax*0.015,
        **text,
    )


if __name__ == "__main__":
    config = fetch_config(sys.argv[1])

    digits = fetch_digits(**config["plot"]["data"])
    colors = color_scheme(**config["plot"]["color"], gradient_steps=digits.shape[0])
    
    points = compute_coordinates(digits)
    points = rescale_coordinates(points, **(config["plot"].gt("format", {})))
    
    sys.stdout.write(
        svg.substitute(
            width=f"{np.max(points[:,0]):.0f}px",
            height=f"{np.max(points[:,1]):.0f}px",
            plot=render_plot(digits, points, colors),
            text=render_text(points, **config["text"]),
        ).strip()
    )
