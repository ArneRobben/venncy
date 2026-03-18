"""Bokeh renderer for 2-circle Venn diagrams."""

from __future__ import annotations

import numpy as np

from venncy import find_2venn_distance, VennResult_2_2

try:
    from bokeh.plotting import figure
    from bokeh.models import Label
except ImportError as e:
    raise ImportError(
        "bokeh is required for this renderer. "
        "Install it with:  pip install venncy[bokeh]"
    ) from e


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

    # Pad ranges so data aspect ratio matches pixel aspect ratio,
    # ensuring circles are not rendered as ellipses.
    data_w = xmax - xmin
    data_h = 2 * ymax
    pixel_aspect = width / height
    data_aspect = data_w / data_h

    if data_aspect > pixel_aspect:
        # data is wider — expand y range
        new_data_h = data_w / pixel_aspect
        ymax = new_data_h / 2
    else:
        # data is taller — expand x range
        new_data_w = data_h * pixel_aspect
        xmid = (xmin + xmax) / 2
        xmin = xmid - new_data_w / 2
        xmax = xmid + new_data_w / 2

    p = figure(
        width=width,
        height=height,
        x_range=(xmin, xmax),
        y_range=(-ymax, ymax),
    )

    # Draw circles via ellipse (circle is an ellipse with equal width/height)
    # Bokeh ellipse uses full width/height, so diameter = 2*radius
    p.ellipse(
        x=[centre_a[0], centre_b[0]],
        y=[centre_a[1], centre_b[1]],
        width=[2 * r_a, 2 * r_b],
        height=[2 * r_a, 2 * r_b],
        fill_color=list(colors),
        fill_alpha=alpha,
        line_color=list(colors),
        line_width=2,
    )

    # Labels
    for centre, label in zip([centre_a, centre_b], labels):
        lbl = Label(
            x=centre[0],
            y=centre[1],
            text=label,
            text_align="center",
            text_baseline="middle",
            text_font_size="14pt",
            text_font_style="bold",
        )
        p.add_layout(lbl)

    p.axis.visible = False
    p.grid.visible = False
    p.toolbar_location = None

    return p
