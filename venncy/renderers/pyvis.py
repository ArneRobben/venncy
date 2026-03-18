"""pyvis / vis.js renderer for Venn diagrams."""

from __future__ import annotations

import numpy as np
from math import pi as PI

from venncy import find_2venn_distance, find_3venn_distance

try:
    import networkx as nx
    from pyvis.network import Network
except ImportError as e:
    raise ImportError(
        "pyvis and networkx are required for this renderer. "
        "Install them with:  pip install venncy[pyvis]"
    ) from e


def _build_network(centres, radii, labels, colors, canvas_width, canvas_height,
                   output_path, text_kwargs, kwargs):
    """Shared logic for building and writing a pyvis Network."""
    margin_px = 60
    usable_w = canvas_width - 2 * margin_px
    usable_h = canvas_height - 2 * margin_px

    xmin = min(c[0] - r for c, r in zip(centres, radii))
    xmax = max(c[0] + r for c, r in zip(centres, radii))
    ymin = min(c[1] - r for c, r in zip(centres, radii))
    ymax = max(c[1] + r for c, r in zip(centres, radii))

    data_w = xmax - xmin
    data_h = ymax - ymin

    scale = min(
        usable_w / data_w if data_w > 0 else usable_w,
        usable_h / data_h if data_h > 0 else usable_h,
    )

    def data_to_px(x: float, y: float) -> tuple[float, float]:
        return margin_px + (x - xmin) * scale, margin_px + (y - ymin) * scale

    G = nx.Graph()
    G.add_nodes_from(list(labels))

    # Build default font settings, let text_kwargs override
    base_font = {"size": 16}
    base_font.update(text_kwargs or {})

    for i, n in enumerate(labels):
        cx, cy = centres[i]
        px_x, px_y = data_to_px(cx, cy)
        node_attrs = {
            "x": float(px_x),
            "y": float(px_y),
            "fixed": True,
            "physics": False,
            "shape": "dot",
            "size": float(radii[i] * scale),
            "label": n,
            "borderWidth": 2,
            "color": colors[i],
            "font": base_font,
        }
        node_attrs.update(kwargs)
        G.nodes[n].update(node_attrs)

    net = Network(
        directed=False,
        select_menu=False,
        filter_menu=False,
        height=f"{canvas_height}px",
        width=f"{canvas_width}px",
    )

    net.set_options(
        '{"physics":{"enabled":false},'
        '"interaction":{"dragNodes":false},'
        '"nodes":{"font":{"size":16}}}'
    )

    net.from_nx(G)
    net.write_html(output_path, notebook=False)

    return net


def plot_venn2(
    area_a: float,
    area_b: float,
    area_ab: float,
    *,
    labels: tuple[str, str] = ("A", "B"),
    colors: tuple[str, str] = ("rgba(66,135,245,0.35)", "rgba(255,159,64,0.35)"),
    canvas_width: int = 800,
    canvas_height: int = 800,
    output_path: str = "venn.html",
    text_kwargs: dict | None = None,
    **kwargs,
) -> Network:
    """
    Draw a 2-circle Venn diagram as an interactive vis.js network and
    write it to an HTML file.

    Args:
        area_a:        Area of circle A.
        area_b:        Area of circle B.
        area_ab:       Area of the intersection of A and B.
        labels:        Text labels for each circle.
        colors:        Fill colours (with alpha) for circles A and B.
        canvas_width:  Canvas width in pixels.
        canvas_height: Canvas height in pixels.
        output_path:   File path for the generated HTML.
        text_kwargs:   Extra keyword arguments forwarded to the vis.js
                       node ``font`` settings (e.g. *size*, *color*, *face*).
        **kwargs:      Extra keyword arguments forwarded to each vis.js
                       node (e.g. *borderWidth*, *borderWidthSelected*, …).
                       These override the defaults.

    Returns:
        The pyvis Network object (the HTML file has already been written).
    """
    result = find_2venn_distance(area_a, area_b, area_ab)
    r_a, r_b, d_ab = result

    centres = [(-d_ab / 2.0, 0.0), (d_ab / 2.0, 0.0)]
    radii = [r_a, r_b]

    return _build_network(
        centres, radii, labels, colors,
        canvas_width, canvas_height, output_path,
        text_kwargs, kwargs,
    )


def plot_venn3(
    area_a: float,
    area_b: float,
    area_c: float,
    area_ab: float,
    area_ac: float,
    area_bc: float,
    *,
    labels: tuple[str, str, str] = ("A", "B", "C"),
    colors: tuple[str, str, str] = (
        "rgba(66,135,245,0.35)",
        "rgba(255,159,64,0.35)",
        "rgba(76,175,80,0.35)",
    ),
    canvas_width: int = 800,
    canvas_height: int = 800,
    output_path: str = "venn.html",
    text_kwargs: dict | None = None,
    **kwargs,
) -> Network:
    """
    Draw a 3-circle Venn diagram as an interactive vis.js network and
    write it to an HTML file.

    Args:
        area_a:        Area of circle A.
        area_b:        Area of circle B.
        area_c:        Area of circle C.
        area_ab:       Area of the intersection of A and B.
        area_ac:       Area of the intersection of A and C.
        area_bc:       Area of the intersection of B and C.
        labels:        Text labels for each circle.
        colors:        Fill colours (with alpha) for circles A, B and C.
        canvas_width:  Canvas width in pixels.
        canvas_height: Canvas height in pixels.
        output_path:   File path for the generated HTML.
        text_kwargs:   Extra keyword arguments forwarded to the vis.js
                       node ``font`` settings (e.g. *size*, *color*, *face*).
        **kwargs:      Extra keyword arguments forwarded to each vis.js
                       node (e.g. *borderWidth*, *borderWidthSelected*, …).
                       These override the defaults.

    Returns:
        The pyvis Network object (the HTML file has already been written).
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

    return _build_network(
        centres, radii, labels, colors,
        canvas_width, canvas_height, output_path,
        text_kwargs, kwargs,
    )
