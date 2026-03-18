"""Plotly renderer for Venn diagrams."""

from __future__ import annotations

import numpy as np

from venncy import find_2venn_distance, find_3venn_distance

try:
    import plotly.graph_objects as go
except ImportError as e:
    raise ImportError(
        "plotly is required for this renderer. "
        "Install it with:  pip install venncy[plotly]"
    ) from e


def plot_venn2(
    area_a: float,
    area_b: float,
    area_ab: float,
    *,
    labels: tuple[str, str] = ("A", "B"),
    colors: tuple[str, str] = ("rgba(66,135,245,0.35)", "rgba(255,159,64,0.35)"),
    line_colors: tuple[str, str] = ("blue", "orange"),
    width: int = 600,
    height: int = 600,
    text_kwargs: dict | None = None,
    **kwargs,
) -> go.Figure:
    """
    Draw a 2-circle Venn diagram using Plotly.

    Args:
        area_a:      Area of circle A.
        area_b:      Area of circle B.
        area_ab:     Area of the intersection of A and B.
        labels:      Text labels placed at the centre of each circle.
        colors:      Fill colours (with alpha) for circles A and B.
        line_colors: Outline colours for circles A and B.
        width:       Figure width in pixels.
        height:      Figure height in pixels.
        text_kwargs: Extra keyword arguments forwarded to ``textfont``
                     in the Plotly Scatter trace (e.g. *size*, *color*, *family*).
        **kwargs:    Extra keyword arguments forwarded to each
                     ``fig.add_shape()`` call (e.g. *line_width*, *line_dash*,
                     *opacity*, …). These override the defaults.

    Returns:
        A plotly Figure containing the Venn diagram.
    """
    result = find_2venn_distance(area_a, area_b, area_ab)
    r_a, r_b, d_ab = result

    centres = [(-d_ab / 2.0, 0.0), (d_ab / 2.0, 0.0)]
    radii = [r_a, r_b]

    fig = go.Figure()

    for (cx, cy), r, color, lc in zip(centres, radii, colors, line_colors):
        base = {
            "type": "circle",
            "xref": "x", "yref": "y",
            "x0": cx - r, "y0": cy - r,
            "x1": cx + r, "y1": cy + r,
            "line_color": lc,
            "fillcolor": color,
        }
        base.update(kwargs)
        fig.add_shape(**base)

    # Labels
    base_text = {"size": 16, "color": "black"}
    base_text.update(text_kwargs or {})

    fig.add_trace(go.Scatter(
        x=[c[0] for c in centres],
        y=[c[1] for c in centres],
        text=list(labels),
        mode="text",
        textfont=base_text,
    ))

    margin = 1.0
    fig.update_layout(
        width=width,
        height=height,
        xaxis=dict(
            range=[min(c[0] - r for c, r in zip(centres, radii)) - margin,
                   max(c[0] + r for c, r in zip(centres, radii)) + margin],
            zeroline=False,
            scaleanchor="y",
            scaleratio=1,
        ),
        yaxis=dict(
            range=[-max(radii) - margin, max(radii) + margin],
            zeroline=False,
        ),
        showlegend=False,
    )

    return fig


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
    line_colors: tuple[str, str, str] = ("blue", "orange", "green"),
    width: int = 600,
    height: int = 600,
    text_kwargs: dict | None = None,
    **kwargs,
) -> go.Figure:
    """
    Draw a 3-circle Venn diagram using Plotly.

    Args:
        area_a:      Area of circle A.
        area_b:      Area of circle B.
        area_c:      Area of circle C.
        area_ab:     Area of the intersection of A and B.
        area_ac:     Area of the intersection of A and C.
        area_bc:     Area of the intersection of B and C.
        labels:      Text labels placed at the centre of each circle.
        colors:      Fill colours (with alpha) for circles A, B and C.
        line_colors: Outline colours for circles A, B and C.
        width:       Figure width in pixels.
        height:      Figure height in pixels.
        text_kwargs: Extra keyword arguments forwarded to ``textfont``
                     in the Plotly Scatter trace (e.g. *size*, *color*, *family*).
        **kwargs:    Extra keyword arguments forwarded to each
                     ``fig.add_shape()`` call (e.g. *line_width*, *line_dash*,
                     *opacity*, …). These override the defaults.

    Returns:
        A plotly Figure containing the Venn diagram.
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

    fig = go.Figure()

    for (cx, cy), r, color, lc in zip(centres, radii, colors, line_colors):
        base = {
            "type": "circle",
            "xref": "x", "yref": "y",
            "x0": cx - r, "y0": cy - r,
            "x1": cx + r, "y1": cy + r,
            "line_color": lc,
            "fillcolor": color,
        }
        base.update(kwargs)
        fig.add_shape(**base)

    # Labels
    base_text = {"size": 16, "color": "black"}
    base_text.update(text_kwargs or {})

    fig.add_trace(go.Scatter(
        x=[c[0] for c in centres],
        y=[c[1] for c in centres],
        text=list(labels),
        mode="text",
        textfont=base_text,
    ))

    margin = 1.0
    xmin = min(c[0] - r for c, r in zip(centres, radii)) - margin
    xmax = max(c[0] + r for c, r in zip(centres, radii)) + margin
    ymax = max(c[1] + r for c, r in zip(centres, radii)) + margin
    ymin = min(c[1] - r for c, r in zip(centres, radii)) - margin

    fig.update_layout(
        width=width,
        height=height,
        xaxis=dict(
            range=[xmin, xmax],
            zeroline=False,
            scaleanchor="y",
            scaleratio=1,
        ),
        yaxis=dict(
            range=[ymin, ymax],
            zeroline=False,
        ),
        showlegend=False,
    )

    return fig
