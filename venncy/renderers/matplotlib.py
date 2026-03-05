"""Matplotlib renderer for 2-circle Venn diagrams."""

from __future__ import annotations

from venncy import find_2venn_distance, VennResult

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

    Returns:
        (fig, ax) — the matplotlib Figure and Axes containing the diagram.
    """
    result = find_2venn_distance(area_a, area_b, area_ab)
    R, r, d = result

    # Place circles symmetrically about the origin
    centre_a = (-d / 2.0, 0.0)
    centre_b = (d / 2.0, 0.0)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    else:
        fig = ax.get_figure()

    circle_a = Circle(centre_a, R, facecolor=colors[0], alpha=alpha, edgecolor=colors[0], lw=2)
    circle_b = Circle(centre_b, r, facecolor=colors[1], alpha=alpha, edgecolor=colors[1], lw=2)
    ax.add_patch(circle_a)
    ax.add_patch(circle_b)

    # Labels
    ax.text(*centre_a, labels[0], ha="center", va="center", fontsize=12, weight="bold")
    ax.text(*centre_b, labels[1], ha="center", va="center", fontsize=12, weight="bold")

    # Keep 1:1 aspect ratio so radii are visually correct
    ax.set_aspect("equal", adjustable="datalim")

    margin = 0.25 * max(R, r)
    xmin = min(centre_a[0] - R, centre_b[0] - r) - margin
    xmax = max(centre_a[0] + R, centre_b[0] + r) + margin
    ymax = max(R, r) + margin
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-ymax, ymax)
    ax.axis("off")

    return fig, ax
