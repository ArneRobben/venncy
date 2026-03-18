"""Plotly renderer for 2-circle Venn diagrams."""

from __future__ import annotations

from venncy import find_2venn_distance, VennResult_2_2

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

    Returns:
        A plotly Figure containing the Venn diagram.
    """
    result = find_2venn_distance(area_a, area_b, area_ab)
    r_a, r_b, d_ab = result

    centre_a = (-d_ab / 2.0, 0.0)
    centre_b = (d_ab / 2.0, 0.0)

    fig = go.Figure()

    # Circle A
    fig.add_shape(
        type="circle",
        xref="x", yref="y",
        x0=centre_a[0] - r_a, y0=centre_a[1] - r_a,
        x1=centre_a[0] + r_a, y1=centre_a[1] + r_a,
        line_color=line_colors[0],
        fillcolor=colors[0],
    )

    # Circle B
    fig.add_shape(
        type="circle",
        xref="x", yref="y",
        x0=centre_b[0] - r_b, y0=centre_b[1] - r_b,
        x1=centre_b[0] + r_b, y1=centre_b[1] + r_b,
        line_color=line_colors[1],
        fillcolor=colors[1],
    )

    # Labels
    fig.add_trace(go.Scatter(
        x=[centre_a[0], centre_b[0]],
        y=[centre_a[1], centre_b[1]],
        text=list(labels),
        mode="text",
        textfont=dict(size=16, color="black"),
    ))

    margin = 1.0
    fig.update_layout(
        width=width,
        height=height,
        xaxis=dict(
            range=[min(centre_a[0] - r_a, centre_b[0] - r_b) - margin,
                   max(centre_a[0] + r_a, centre_b[0] + r_b) + margin],
            zeroline=False,
            scaleanchor="y",
            scaleratio=1,
        ),
        yaxis=dict(
            range=[-max(r_a, r_b) - margin, max(r_a, r_b) + margin],
            zeroline=False,
        ),
        showlegend=False,
    )

    return fig
