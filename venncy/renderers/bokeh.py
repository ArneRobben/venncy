"""Bokeh renderer for Venn diagrams."""

from __future__ import annotations

import numpy as np

from venncy import find_2venn_distance, find_3venn_distance

try:
    from bokeh.plotting import figure
    from bokeh.models import Label
except ImportError as e:
    raise ImportError(
        "bokeh is required for this renderer. "
        "Install it with:  pip install venncy[bokeh]"
    ) from e


def _pad_ranges(xmin, xmax, ymax, width, height):
    """Pad x/y ranges so the data aspect ratio matches the pixel aspect ratio."""
    data_w = xmax - xmin
    data_h = 2 * ymax
    pixel_aspect = width / height
    data_aspect = data_w / data_h

    if data_aspect > pixel_aspect:
        new_data_h = data_w / pixel_aspect
        ymax = new_data_h / 2
    else:
        new_data_w = data_h * pixel_aspect
        xmid = (xmin + xmax) / 2
        xmin = xmid - new_data_w / 2
        xmax = xmid + new_data_w / 2

    return xmin, xmax, ymax


def plot_venn2(
    area_a: float,
    area_b: float,
    area_ab: float,
    *,
    labels: tuple[str, str] = ("A", "B"),
    colors: tuple[str, str] = ("blue", "orange"),
    alpha: float = 0.35,
    width: int = 600,
    height: int = 600,
    text_kwargs: dict | None = None,
    **kwargs,
) -> figure:
    """
    Draw a 2-circle Venn diagram using Bokeh.

    Args:
        area_a:   Area of circle A.
        area_b:   Area of circle B.
        area_ab:  Area of the intersection of A and B.
        labels:   Text labels placed at the centre of each circle.
        colors:   Fill colours for circles A and B.
        alpha:    Fill opacity.
        width:    Figure width in pixels.
        height:   Figure height in pixels.
        text_kwargs: Extra keyword arguments forwarded to ``bokeh.models.Label``.
        **kwargs: Extra keyword arguments forwarded to the Bokeh ``ellipse``
                  glyph (e.g. *line_width*, *line_dash*, *line_color*, …).
                  These override the defaults built from *colors* and *alpha*.

    Returns:
        A Bokeh Figure containing the Venn diagram.
    """
    result = find_2venn_distance(area_a, area_b, area_ab)
    r_a, r_b, d_ab = result

    centre_a = (-d_ab / 2.0, 0.0)
    centre_b = (d_ab / 2.0, 0.0)

    margin = 0.25 * max(r_a, r_b)
    xmin = min(centre_a[0] - r_a, centre_b[0] - r_b) - margin
    xmax = max(centre_a[0] + r_a, centre_b[0] + r_b) + margin
    ymax = max(r_a, r_b) + margin

    xmin, xmax, ymax = _pad_ranges(xmin, xmax, ymax, width, height)

    p = figure(
        width=width,
        height=height,
        x_range=(xmin, xmax),
        y_range=(-ymax, ymax),
    )

    # Build defaults, then let **kwargs override
    base = {
        "fill_color": list(colors),
        "fill_alpha": alpha,
        "line_color": list(colors),
        "line_width": 2,
    }
    base.update(kwargs)

    p.ellipse(
        x=[centre_a[0], centre_b[0]],
        y=[centre_a[1], centre_b[1]],
        width=[2 * r_a, 2 * r_b],
        height=[2 * r_a, 2 * r_b],
        **base,
    )

    # Labels
    base_text = {
        "text_align": "center",
        "text_baseline": "middle",
        "text_font_size": "14pt",
        "text_font_style": "bold",
    }
    base_text.update(text_kwargs or {})

    for centre, label in zip([centre_a, centre_b], labels):
        lbl = Label(x=centre[0], y=centre[1], text=label, **base_text)
        p.add_layout(lbl)

    p.axis.visible = False
    p.grid.visible = False
    p.toolbar_location = None

    return p


def plot_venn3(
    area_a: float,
    area_b: float,
    area_c: float,
    area_ab: float,
    area_ac: float,
    area_bc: float,
    *,
    labels: tuple[str, str, str] = ("A", "B", "C"),
    colors: tuple[str, str, str] = ("blue", "orange", "green"),
    alpha: float = 0.35,
    width: int = 600,
    height: int = 600,
    text_kwargs: dict | None = None,
    **kwargs,
) -> figure:
    """
    Draw a 3-circle Venn diagram using Bokeh.

    Args:
        area_a:   Area of circle A.
        area_b:   Area of circle B.
        area_c:   Area of circle C.
        area_ab:  Area of the intersection of A and B.
        area_ac:  Area of the intersection of A and C.
        area_bc:  Area of the intersection of B and C.
        labels:   Text labels placed at the centre of each circle.
        colors:   Fill colours for circles A, B and C.
        alpha:    Fill opacity.
        width:    Figure width in pixels.
        height:   Figure height in pixels.
        text_kwargs: Extra keyword arguments forwarded to ``bokeh.models.Label``.
        **kwargs: Extra keyword arguments forwarded to the Bokeh ``ellipse``
                  glyph (e.g. *line_width*, *line_dash*, *line_color*, …).
                  These override the defaults built from *colors* and *alpha*.

    Returns:
        A Bokeh Figure containing the Venn diagram.
    """
    result = find_3venn_distance(area_a, area_b, area_c, area_ab, area_ac, area_bc)
    r_a, r_b, r_c, d_ab, d_ac, d_bc = result

    # Place A at origin, B on x-axis, solve for C via triangle geometry
    ax_ = 0.0
    ay_ = 0.0
    bx_ = d_ab
    by_ = 0.0

    if d_ab > 0:
        cx_ = (d_ac**2 + d_ab**2 - d_bc**2) / (2.0 * d_ab)
        cy_sq = d_ac**2 - cx_**2
        cy_ = np.sqrt(max(cy_sq, 0.0))
    else:
        cx_, cy_ = 0.0, d_ac

    # Centre the diagram around the centroid
    mx = (ax_ + bx_ + cx_) / 3.0
    my = (ay_ + by_ + cy_) / 3.0
    centre_a = (ax_ - mx, ay_ - my)
    centre_b = (bx_ - mx, by_ - my)
    centre_c = (cx_ - mx, cy_ - my)

    centres = [centre_a, centre_b, centre_c]
    radii = [r_a, r_b, r_c]

    margin = 0.25 * max(radii)
    xmin = min(c[0] - r for c, r in zip(centres, radii)) - margin
    xmax = max(c[0] + r for c, r in zip(centres, radii)) + margin
    ymax = max(c[1] + r for c, r in zip(centres, radii)) + margin
    ymin = min(c[1] - r for c, r in zip(centres, radii)) - margin
    ymax = max(ymax, -ymin)

    xmin, xmax, ymax = _pad_ranges(xmin, xmax, ymax, width, height)

    p = figure(
        width=width,
        height=height,
        x_range=(xmin, xmax),
        y_range=(-ymax, ymax),
    )

    base = {
        "fill_color": list(colors),
        "fill_alpha": alpha,
        "line_color": list(colors),
        "line_width": 2,
    }
    base.update(kwargs)

    p.ellipse(
        x=[c[0] for c in centres],
        y=[c[1] for c in centres],
        width=[2 * r for r in radii],
        height=[2 * r for r in radii],
        **base,
    )

    # Labels
    base_text = {
        "text_align": "center",
        "text_baseline": "middle",
        "text_font_size": "14pt",
        "text_font_style": "bold",
    }
    base_text.update(text_kwargs or {})

    for centre, label in zip(centres, labels):
        lbl = Label(x=centre[0], y=centre[1], text=label, **base_text)
        p.add_layout(lbl)

    p.axis.visible = False
    p.grid.visible = False
    p.toolbar_location = None

    return p
