"""."""

import json
import math
import string
import sys
import typing

import colour
import numpy as np

svg: string.Template = string.Template(
    '<?xml version="1.0" encoding="utf-8" ?>\n'
    '<svg '
    f'width="$width" '
    f'height="$height" '
    'version="1.2" '
    'xmlns="http://www.w3.org/2000/svg" '
    'xmlns:ev="http://www.w3.org/2001/xml-events" '
    'xmlns:xlink="http://www.w3.org/1999/xlink"'
    '>'
    '<defs />'
    '$text'
    '$plot'
    '</svg>'
)

svg_line: string.Template = string.Template(
    '<line '
    'x1="$x1" y1="$y1" '
    'x2="$x2" y2="$y2" '
    'stroke="$color" '
    'stroke-linecap="round" '
    'stroke-width="4" '
    '/>'
)

svg_text: string.Template = string.Template(
    '<text '
    'x="50%" y="50%" '
    'fill="#f7f7f7" '
    'font-family="Arial, Helvetica, sans-serif" '
    'font-size="$background_size" '
    'dominant-baseline="middle" '
    'text-anchor="middle"'
    '>'
    '$background'
    '</text>'
    '<text '
    'x="3%" y="96.5%" '
    'fill="#aaaaaa" '
    'font-family="Arial, Helvetica, sans-serif" '
    'font-size="$title_size" '
    '>'
    '$title'
    '</text>'
    '<text '
    'x="3%" y="99%" '
    'fill="#aaaaaa" '
    'font-family="Arial, Helvetica, sans-serif" '
    'font-size="$caption_size" '
    '>'
    '$caption'
    '</text>'
)


def fetch_config(source: str) -> typing.Dict[str, typing.Any]:
    """.
    """
    return json.load(open(source))


def fetch_digits(source: str, first: int = 0, until: int = 100) -> np.array:
    """.
    """
    digits: np.array = np.zeros(until - first, dtype=np.int8)

    for n, d in enumerate(open(source).read().split(".")[1][first:until]):
        digits[n] += int(d)

    return digits


def color_scheme(
    gradient_steps: int = 0,
    gradient_start: str = None,
    gradient_until: str = None,
    color_array: typing.Union[
        typing.Dict[typing.Union[int, str], str], typing.List[str]
    ] = []
) -> typing.List[colour.Color]:
    """.
    """
    colors: typing.List[colour.Color] = []

    if gradient_start is not None and gradient_until is not None:
        s = colour.Color(gradient_start)
        e = colour.Color(gradient_until)
        colors = list(s.range_to(e, gradient_steps))

    elif len(colour_array) == 10:
        if type(color_array) == dict:
            colors = [colour.Color(color_array[n]) for n in color_array]
        else:
            colors = color_list

    return colors


def compute_coordinates(digits: np.array, angle_step: float = 36.0, recenter: bool = True):
    """.
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
        min_height: int = None,
        max_width: int = None,
        max_height: int = None,
        keep_ratio: bool = True
) -> np.array:
    """.
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
    """.
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
    """.
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

    digits = fetch_digits(**config["data"])
    colors = color_scheme(**config["tone"], gradient_steps=digits.shape[0])
    
    points = compute_coordinates(digits)
    points = rescale_coordinates(points, min_width=2500, max_width=2000, max_height=3000)
    
    sys.stdout.write(
        svg.substitute(
            width=f"{np.max(points[:,0]):.0f}px",
            height=f"{np.max(points[:,1]):.0f}px",
            plot=render_plot(digits, points, colors),
            text=render_text(points, **config["text"]),
        ).strip()
    )
