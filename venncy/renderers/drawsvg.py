"""drawsvg renderer for Venn diagrams."""

from __future__ import annotations

import numpy as np

from venncy import find_2venn_distance, find_3venn_distance

try:
    import drawsvg as draw
except ImportError as e:
    raise ImportError(
        "drawsvg is required for this renderer. "
        "Install it with:  pip install venncy[drawsvg]"
    ) from e


def _svg_dimensions(xmin, xmax, ymax, width, height):
    """Compute SVG pixel size and viewBox preserving aspect ratio."""
    data_w = xmax - xmin
    data_h = 2 * ymax
    pixel_aspect = width / height
    data_aspect = data_w / data_h

    if data_aspect > pixel_aspect:
        svg_px_w = width
        svg_px_h = width / data_aspect
    else:
        svg_px_h = height
        svg_px_w = height * data_aspect

    scale = svg_px_w / data_w
    return svg_px_w, svg_px_h, data_w, data_h, scale


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
) -> draw.Drawing:
    """
    Draw a 2-circle Venn diagram as an SVG using drawsvg.

    Args:
        area_a:   Area of circle A.
        area_b:   Area of circle B.
        area_ab:  Area of the intersection of A and B.
        labels:   Text labels placed at the centre of each circle.
        colors:   Fill colours for circles A and B.
        alpha:    Fill opacity (0–1).
        width:    SVG width in pixels.
        height:   SVG height in pixels.
        text_kwargs: Extra keyword arguments forwarded to ``drawsvg.Text``.
        **kwargs: Extra keyword arguments forwarded to ``drawsvg.Circle``
                  (e.g. *stroke*, *stroke_width*, *stroke_dasharray*, …).
                  These override the defaults built from *colors* and *alpha*.

    Returns:
        A drawsvg Drawing object. Call ``.save_svg(path)`` or
        ``.save_png(path)`` on it, or display it directly in a notebook.
    """
    result = find_2venn_distance(area_a, area_b, area_ab)
    r_a, r_b, d_ab = result

    centre_a_x = -d_ab / 2.0
    centre_b_x = d_ab / 2.0

    margin = 0.25 * max(r_a, r_b)
    xmin = min(centre_a_x - r_a, centre_b_x - r_b) - margin
    xmax = max(centre_a_x + r_a, centre_b_x + r_b) + margin
    ymax = max(r_a, r_b) + margin

    svg_px_w, svg_px_h, data_w, data_h, scale = _svg_dimensions(
        xmin, xmax, ymax, width, height,
    )

    drawing = draw.Drawing(
        f"{svg_px_w}px", f"{svg_px_h}px",
        viewBox=f"{xmin} {-ymax} {data_w} {data_h}",
    )

    for cx, radius, color in [(centre_a_x, r_a, colors[0]),
                               (centre_b_x, r_b, colors[1])]:
        base = {
            "fill": color,
            "fill_opacity": alpha,
            "stroke": color,
            "stroke_width": 2 / scale,
        }
        base.update(kwargs)
        drawing.append(draw.Circle(cx, 0, radius, **base))

    # Labels
    font_size = 14 / scale
    base_text = {
        "text_anchor": "middle",
        "dominant_baseline": "central",
        "font_weight": "bold",
    }
    base_text.update(text_kwargs or {})

    for cx, label in [(centre_a_x, labels[0]), (centre_b_x, labels[1])]:
        drawing.append(draw.Text(label, font_size, cx, 0, **base_text))

    return drawing


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
) -> draw.Drawing:
    """
    Draw a 3-circle Venn diagram as an SVG using drawsvg.

    Args:
        area_a:   Area of circle A.
        area_b:   Area of circle B.
        area_c:   Area of circle C.
        area_ab:  Area of the intersection of A and B.
        area_ac:  Area of the intersection of A and C.
        area_bc:  Area of the intersection of B and C.
        labels:   Text labels placed at the centre of each circle.
        colors:   Fill colours for circles A, B and C.
        alpha:    Fill opacity (0–1).
        width:    SVG width in pixels.
        height:   SVG height in pixels.
        text_kwargs: Extra keyword arguments forwarded to ``drawsvg.Text``.
        **kwargs: Extra keyword arguments forwarded to ``drawsvg.Circle``
                  (e.g. *stroke*, *stroke_width*, *stroke_dasharray*, …).
                  These override the defaults built from *colors* and *alpha*.

    Returns:
        A drawsvg Drawing object.
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

    mx = (ax_ + bx_ + cx_) / 3.0
    my = (ay_ + by_ + cy_) / 3.0
    centres = [(ax_ - mx, ay_ - my), (bx_ - mx, by_ - my), (cx_ - mx, cy_ - my)]
    radii = [r_a, r_b, r_c]

    margin = 0.25 * max(radii)
    xmin = min(c[0] - r for c, r in zip(centres, radii)) - margin
    xmax = max(c[0] + r for c, r in zip(centres, radii)) + margin
    ymax = max(c[1] + r for c, r in zip(centres, radii)) + margin
    ymin = min(c[1] - r for c, r in zip(centres, radii)) - margin
    ymax = max(ymax, -ymin)

    svg_px_w, svg_px_h, data_w, data_h, scale = _svg_dimensions(
        xmin, xmax, ymax, width, height,
    )

    drawing = draw.Drawing(
        f"{svg_px_w}px", f"{svg_px_h}px",
        viewBox=f"{xmin} {-ymax} {data_w} {data_h}",
    )

    for (cx, cy), radius, color in zip(centres, radii, colors):
        base = {
            "fill": color,
            "fill_opacity": alpha,
            "stroke": color,
            "stroke_width": 2 / scale,
        }
        base.update(kwargs)
        drawing.append(draw.Circle(cx, cy, radius, **base))

    # Labels
    font_size = 14 / scale
    base_text = {
        "text_anchor": "middle",
        "dominant_baseline": "central",
        "font_weight": "bold",
    }
    base_text.update(text_kwargs or {})

    for (cx, cy), label in zip(centres, labels):
        drawing.append(draw.Text(label, font_size, cx, cy, **base_text))

    return drawing
