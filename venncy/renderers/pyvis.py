"""pyvis / vis.js renderer for 2-circle Venn diagrams."""

from __future__ import annotations

from math import pi as PI

from venncy import find_2venn_distance, VennResult

try:
    import networkx as nx
    from pyvis.network import Network
except ImportError as e:
    raise ImportError(
        "pyvis and networkx are required for this renderer. "
        "Install them with:  pip install venncy[pyvis]"
    ) from e


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

    Returns:
        The pyvis Network object (the HTML file has already been written).
    """
    result = find_2venn_distance(area_a, area_b, area_ab)
    R, r, d = result

    # --- Build networkx graph ---
    G = nx.Graph()
    G.add_nodes_from(list(labels))

    pos = {labels[0]: (-d / 2.0, 0.0), labels[1]: (d / 2.0, 0.0)}
    radii = {labels[0]: R, labels[1]: r}

    # --- Map data-space to pixel canvas ---
    margin_px = 60
    usable_w = canvas_width - 2 * margin_px
    usable_h = canvas_height - 2 * margin_px

    xmin = min(pos[labels[0]][0] - R, pos[labels[1]][0] - r)
    xmax = max(pos[labels[0]][0] + R, pos[labels[1]][0] + r)
    ymin = min(-R, -r)
    ymax = max(R, r)

    data_w = xmax - xmin
    data_h = ymax - ymin

    scale = min(
        usable_w / data_w if data_w > 0 else usable_w,
        usable_h / data_h if data_h > 0 else usable_h,
    )

    def data_to_px(x: float, y: float) -> tuple[float, float]:
        return margin_px + (x - xmin) * scale, margin_px + (y - ymin) * scale

    # Stamp vis.js attributes onto the graph nodes
    for i, n in enumerate(labels):
        px_x, px_y = data_to_px(*pos[n])
        G.nodes[n].update(
            x=float(px_x),
            y=float(px_y),
            fixed=True,
            physics=False,
            shape="dot",
            size=float(radii[n] * scale),
            label=n,
            borderWidth=2,
            color=colors[i],
        )

    # --- Build pyvis network ---
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
