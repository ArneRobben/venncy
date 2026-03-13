"""drawsvg renderer for 2-circle Venn diagrams."""

from __future__ import annotations

from venncy import find_2venn_distance, VennResult

try:
    import drawsvg as draw
except ImportError as e:
    raise ImportError(
        "drawsvg is required for this renderer. "
        "Install it with:  pip install venncy[drawsvg]"
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

    Returns:
        A drawsvg Drawing object. Call ``.save_svg(path)`` or
        ``.save_png(path)`` on it, or display it directly in a notebook.
    """
    result = find_2venn_distance(area_a, area_b, area_ab)
    R, r, d = result

    centre_a_x = -d / 2.0
    centre_b_x = d / 2.0

    margin = 0.25 * max(R, r)
    xmin = min(centre_a_x - R, centre_b_x - r) - margin
    xmax = max(centre_a_x + R, centre_b_x + r) + margin
    ymax = max(R, r) + margin
    data_w = xmax - xmin
    data_h = 2 * ymax

    # Maintain aspect ratio: adjust pixel dimensions to match data proportions
    pixel_aspect = width / height
    data_aspect = data_w / data_h
    if data_aspect > pixel_aspect:
        # data is wider — shrink pixel height
        svg_px_w = width
        svg_px_h = width / data_aspect
    else:
        # data is taller — shrink pixel width
        svg_px_h = height
        svg_px_w = height * data_aspect

    scale = svg_px_w / data_w

    # Use data coordinates for viewBox; set pixel size via width/height strings
    drawing = draw.Drawing(
        f"{svg_px_w}px", f"{svg_px_h}px",
        viewBox=f"{xmin} {-ymax} {data_w} {data_h}",
    )

    # Circle A
    drawing.append(draw.Circle(
        centre_a_x, 0, R,
        fill=colors[0],
        fill_opacity=alpha,
        stroke=colors[0],
        stroke_width=2 / scale,
    ))

    # Circle B
    drawing.append(draw.Circle(
        centre_b_x, 0, r,
        fill=colors[1],
        fill_opacity=alpha,
        stroke=colors[1],
        stroke_width=2 / scale,
    ))

    # Labels
    font_size = 14 / scale
    for cx, label in [(centre_a_x, labels[0]), (centre_b_x, labels[1])]:
        drawing.append(draw.Text(
            label,
            font_size,
            cx, 0,
            text_anchor="middle",
            dominant_baseline="central",
            font_weight="bold",
        ))

    return drawing
