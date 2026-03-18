"""Matplotlib renderer for Venn diagrams."""

from __future__ import annotations

import numpy as np
from venncy import find_2venn_distance, find_3venn_distance

try:
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle
    from matplotlib.figure import Figure
    from matplotlib.axes import Axes
except ImportError as e:
    raise ImportError(
        "matplotlib is required for this renderer. "
        "Install it with:  pip install venncy[matplotlib]"
    ) from e


def plot_venn2(
    area_a: float,
    area_b: float,
    area_ab: float,
    *,
    labels: tuple[str, str] = ("A", "B"),
    colors: tuple[str, str] = ("tab:blue", "tab:orange"),
    alpha: float = 0.35,
    ax: Axes | None = None,
    figsize: tuple[float, float] = (6, 6),
    dpi: int = 150,
    text_kwargs: dict | None = None,
    **kwargs,
) -> tuple[Figure, Axes]:
    """
    Draw a 2-circle Venn diagram using matplotlib.

    Args:
        area_a:   Area of circle A.
        area_b:   Area of circle B.
        area_ab:  Area of the intersection of A and B.
        labels:   Text labels placed at the centre of each circle.
        colors:   Face / edge colours for circle A and B.
        alpha:    Fill opacity.
        ax:       An existing Axes to draw on. If *None* a new Figure is created.
        figsize:  Figure size (only used when *ax* is None).
        dpi:      Figure DPI (only used when *ax* is None).
        text_kwargs: Extra keyword arguments forwarded to ``ax.text()``.
        **kwargs: Extra keyword arguments forwarded to
                  ``matplotlib.patches.Circle`` (e.g. *edgecolor*,
                  *linestyle*, *linewidth*, *hatch*, *zorder*, …).
                  These override the defaults built from *colors* and *alpha*.

    Returns:
        (fig, ax) — the matplotlib Figure and Axes containing the diagram.
    """
    result = find_2venn_distance(area_a, area_b, area_ab)
    r_a, r_b, d_ab = result

    # Place circles symmetrically about the origin
    centre_a = (-d_ab / 2.0, 0.0)
    centre_b = (d_ab / 2.0, 0.0)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    else:
        fig = ax.get_figure()

    # Build per-circle defaults, then let **kwargs override any of them
    base_a = {"facecolor": colors[0], "alpha": alpha, "edgecolor": colors[0], "lw": 2}
    base_b = {"facecolor": colors[1], "alpha": alpha, "edgecolor": colors[1], "lw": 2}
    base_a.update(kwargs)
    base_b.update(kwargs)

    circle_a = Circle(centre_a, r_a, **base_a)
    circle_b = Circle(centre_b, r_b, **base_b)
    ax.add_patch(circle_a)
    ax.add_patch(circle_b)

    # Labels
    base_text = {"ha": "center", "va": "center", "fontsize": 12, "weight": "bold"}
    base_text.update(text_kwargs or {})
    ax.text(*centre_a, labels[0], **base_text)
    ax.text(*centre_b, labels[1], **base_text)

    # Keep 1:1 aspect ratio so radii are visually correct
    ax.set_aspect("equal", adjustable="box")

    margin = 0.25 * max(r_a, r_b)
    xmin = min(centre_a[0] - r_a, centre_b[0] - r_b) - margin
    xmax = max(centre_a[0] + r_a, centre_b[0] + r_b) + margin
    ymax = max(r_a, r_b) + margin
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-ymax, ymax)
    ax.axis("off")

    return fig, ax

def plot_venn3(
    area_a: float,
    area_b: float,
    area_c: float,
    area_ab: float,
    area_ac: float,
    area_bc: float,
    *,
    labels: tuple[str, str, str] = ("A", "B", "C"),
    colors: tuple[str, str, str] = ("tab:blue", "tab:orange", "tab:green"),
    alpha: float = 0.35,
    ax: Axes | None = None,
    figsize: tuple[float, float] = (6, 6),
    dpi: int = 150,
    text_kwargs: dict | None = None,
    **kwargs,
) -> tuple[Figure, Axes]:
    """
    Draw a 3-circle Venn diagram using matplotlib.

    Args:
        area_a:   Area of circle A.
        area_b:   Area of circle B.
        area_c:   Area of circle C.
        area_ab:  Area of the intersection of A and B.
        area_ac:  Area of the intersection of A and C.
        area_bc:  Area of the intersection of B and C.
        labels:   Text labels placed at the centre of each circle.
        colors:   Face / edge colours for circles A, B and C.
        alpha:    Fill opacity.
        ax:       An existing Axes to draw on. If *None* a new Figure is created.
        figsize:  Figure size (only used when *ax* is None).
        dpi:      Figure DPI (only used when *ax* is None).
        text_kwargs: Extra keyword arguments forwarded to ``ax.text()``.
        **kwargs: Extra keyword arguments forwarded to
                  ``matplotlib.patches.Circle`` (e.g. *edgecolor*,
                  *linestyle*, *linewidth*, *hatch*, *zorder*, …).
                  These override the defaults built from *colors* and *alpha*.

    Returns:
        (fig, ax) — the matplotlib Figure and Axes containing the diagram.
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

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    else:
        fig = ax.get_figure()

    # Build per-circle defaults, then let **kwargs override any of them
    base_a = {"facecolor": colors[0], "alpha": alpha, "edgecolor": colors[0], "lw": 2}
    base_b = {"facecolor": colors[1], "alpha": alpha, "edgecolor": colors[1], "lw": 2}
    base_c = {"facecolor": colors[2], "alpha": alpha, "edgecolor": colors[2], "lw": 2}
    base_a.update(kwargs)
    base_b.update(kwargs)
    base_c.update(kwargs)

    circle_a = Circle(centre_a, r_a, **base_a)
    circle_b = Circle(centre_b, r_b, **base_b)
    circle_c = Circle(centre_c, r_c, **base_c)
    ax.add_patch(circle_a)
    ax.add_patch(circle_b)
    ax.add_patch(circle_c)

    # Labels
    base_text = {"ha": "center", "va": "center", "fontsize": 12, "weight": "bold"}
    base_text.update(text_kwargs or {})
    ax.text(*centre_a, labels[0], **base_text)
    ax.text(*centre_b, labels[1], **base_text)
    ax.text(*centre_c, labels[2], **base_text)

    # Keep 1:1 aspect ratio so radii are visually correct
    ax.set_aspect("equal", adjustable="box")

    margin = 0.25 * max(r_a, r_b, r_c)
    xmin = min(centre_a[0] - r_a, centre_b[0] - r_b, centre_c[0] - r_c) - margin
    xmax = max(centre_a[0] + r_a, centre_b[0] + r_b, centre_c[0] + r_c) + margin
    ymax = max(centre_a[1] + r_a, centre_b[1] + r_b, centre_c[1] + r_c) + margin
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-ymax, ymax)
    ax.axis("off")

    return fig, ax