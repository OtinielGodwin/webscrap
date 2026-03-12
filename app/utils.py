"""
Utility helpers shared across the Streamlit application.
Currently includes helpers for handling colors in a way that is
compatible with Plotly (which only accepts rgba() strings or 8-digit
hex codes when transparency is required).
"""

import re


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert a 6‑ or 8‑digit hex color (#rrggbb or #rrggbbaa) to an (r,g,b)
    tuple. The alpha component (if present) is ignored here.

    The input may start with or without ``#``.
    """

    hex_color = hex_color.lstrip("#")
    if len(hex_color) not in (6, 8):
        raise ValueError(f"Invalid hex color length: '{hex_color}'")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return r, g, b


def _hex_alpha_to_float(alpha: str) -> float:
    """Convert a 2‑digit hex alpha component (e.g. "22") to a float
    in the range [0,1].
    """

    try:
        iv = int(alpha, 16)
    except ValueError as ve:
        raise ValueError(f"Alpha must be a hex pair, got '{alpha}'") from ve
    return round(iv / 255, 3)


def plotly_color(color: str, opacity: str | float | None = None) -> str:
    """Return a colour string that Plotly accepts.

    ``color`` may be any valid CSS colour string (hex, rgb/rgba, named
    colour, etc.).  ``opacity`` can be provided either as a two‑digit hex
    string (``"22"``) or as a float between 0 and 1.  When ``opacity`` is
    given the result is always an ``rgba(r,g,b,a)`` string; if it is omitted
    the original colour is returned unchanged unless the input was a 6‑digit
    hex colour and the caller requested an alpha via the ``opacity``
    argument, in which case the alpha is appended.

    This helper is primarily intended to sanitize the common pattern
    ``f"{base_color}22"`` which is not accepted by Plotly.
    """

    # if we already have an rgba() string or a 8‑digit hex code, leave it as‑is
    if isinstance(color, str) and (color.startswith("rgba") or
                                 (color.startswith("#") and len(color) == 9)):
        if opacity is None:
            return color
        # otherwise we'll rebuild below using the provided opacity

    # try to interpret a hex color so we can convert
    hex_match = re.fullmatch(r"#?([0-9a-fA-F]{6})([0-9a-fA-F]{2})?", color)
    if hex_match:
        base = hex_match.group(1)
        supplied_alpha = hex_match.group(2)
        r, g, b = [int(base[i : i + 2], 16) for i in (0, 2, 4)]
        if opacity is not None:
            if isinstance(opacity, float):
                a = opacity
            else:
                # treat opacity as hex string
                a = _hex_alpha_to_float(str(opacity))
        elif supplied_alpha:
            a = _hex_alpha_to_float(supplied_alpha)
        else:
            # no alpha required
            return f"#{base}"
        return f"rgba({r},{g},{b},{a})"

    # opacity provided but colour is not a simple hex: fall back to rgba
    if opacity is not None:
        # attempt to parse rgb from the string
        rgb_match = re.search(r"(\d{1,3}),\s*(\d{1,3}),\s*(\d{1,3})", color)
        if rgb_match:
            r, g, b = map(int, rgb_match.groups())
            a = float(opacity) if isinstance(opacity, (int, float)) else _hex_alpha_to_float(str(opacity))
            return f"rgba({r},{g},{b},{a})"

    # nothing fancy, just return as‑is
    return color
