"""PIL / Pillow renderer for Venn diagrams."""

from __future__ import annotations

import numpy as np

from venncy import find_2venn_distance, find_3venn_distance

try:
    from PIL import Image, ImageDraw, ImageFont, ImageColor
except ImportError as e:
    raise ImportError(
        "Pillow is required for this renderer. "
        "Install it with:  pip install venncy[pillow]"
    ) from e


def _compute_transform(centres, radii, width, height):
    """Return (xmin, ymax, scale, to_px) for mapping data coords to pixels."""
    margin = 0.25 * max(radii)
    xmin = min(c[0] - r for c, r in zip(centres, radii)) - margin
    xmax = max(c[0] + r for c, r in zip(centres, radii)) + margin
    ymax = max(c[1] + r for c, r in zip(centres, radii)) + margin
    ymin = min(c[1] - r for c, r in zip(centres, radii)) - margin
    ymax = max(ymax, -ymin)
    data_w = xmax - xmin
    data_h = 2 * ymax
    scale = min(width / data_w, height / data_h)

    def to_px(x: float, y: float) -> tuple[float, float]:
        px = (x - xmin) * scale + (width - data_w * scale) / 2
        py = (y + ymax) * scale + (height - data_h * scale) / 2
        return px, py

    return scale, to_px


def plot_venn2(
    area_a: float,
    area_b: float,
    area_ab: float,
    *,
    labels: tuple[str, str] = ("A", "B"),
    colors: tuple[str, str] = ("blue", "orange"),
    alpha: int = 90,
    width: int = 600,
    height: int = 600,
    bg_color: str = "white",
    text_kwargs: dict | None = None,
    **kwargs,
) -> Image.Image:
    """
    Draw a 2-circle Venn diagram as a PIL Image.

    Args:
        area_a:    Area of circle A.
        area_b:    Area of circle B.
        area_ab:   Area of the intersection of A and B.
        labels:    Text labels placed at the centre of each circle.
        colors:    Fill colours for circles A and B (any PIL colour string).
        alpha:     Fill opacity (0–255).
        width:     Image width in pixels.
        height:    Image height in pixels.
        bg_color:  Background colour.
        text_kwargs: Extra keyword arguments forwarded to ``ImageDraw.text()``.
        **kwargs: Extra keyword arguments forwarded to
                  ``ImageDraw.ellipse()`` (e.g. *width* for outline thickness).
                  These override the defaults built from *colors* and *alpha*.

    Returns:
        A PIL Image (RGBA). Call ``.save(path)`` to export it.
    """
    result = find_2venn_distance(area_a, area_b, area_ab)
    r_a, r_b, d_ab = result

    centres = [(-d_ab / 2.0, 0.0), (d_ab / 2.0, 0.0)]
    radii = [r_a, r_b]
    scale, to_px = _compute_transform(centres, radii, width, height)

    img = Image.new("RGBA", (width, height), bg_color)

    for (cx, cy), radius, color in zip(centres, radii, colors):
        layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        layer_draw = ImageDraw.Draw(layer)
        px, py = to_px(cx, cy)
        r_px = radius * scale
        bbox = [px - r_px, py - r_px, px + r_px, py + r_px]

        rgb = ImageColor.getrgb(color)
        base = {"fill": rgb + (alpha,), "outline": rgb + (255,), "width": 2}
        base.update(kwargs)

        layer_draw.ellipse(bbox, **base)
        img = Image.alpha_composite(img, layer)

    # Labels
    img_draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", size=max(14, int(14 * scale / 40)))
    except OSError:
        font = ImageFont.load_default()

    base_text = {"fill": "black", "font": font, "anchor": "mm"}
    base_text.update(text_kwargs or {})

    for (cx, cy), label in zip(centres, labels):
        px, py = to_px(cx, cy)
        img_draw.text((px, py), label, **base_text)

    return img


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
    alpha: int = 90,
    width: int = 600,
    height: int = 600,
    bg_color: str = "white",
    text_kwargs: dict | None = None,
    **kwargs,
) -> Image.Image:
    """
    Draw a 3-circle Venn diagram as a PIL Image.

    Args:
        area_a:    Area of circle A.
        area_b:    Area of circle B.
        area_c:    Area of circle C.
        area_ab:   Area of the intersection of A and B.
        area_ac:   Area of the intersection of A and C.
        area_bc:   Area of the intersection of B and C.
        labels:    Text labels placed at the centre of each circle.
        colors:    Fill colours for circles A, B and C (any PIL colour string).
        alpha:     Fill opacity (0–255).
        width:     Image width in pixels.
        height:    Image height in pixels.
        bg_color:  Background colour.
        text_kwargs: Extra keyword arguments forwarded to ``ImageDraw.text()``.
        **kwargs: Extra keyword arguments forwarded to
                  ``ImageDraw.ellipse()`` (e.g. *width* for outline thickness).
                  These override the defaults built from *colors* and *alpha*.

    Returns:
        A PIL Image (RGBA). Call ``.save(path)`` to export it.
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
    scale, to_px = _compute_transform(centres, radii, width, height)

    img = Image.new("RGBA", (width, height), bg_color)

    for (cx, cy), radius, color in zip(centres, radii, colors):
        layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        layer_draw = ImageDraw.Draw(layer)
        px, py = to_px(cx, cy)
        r_px = radius * scale
        bbox = [px - r_px, py - r_px, px + r_px, py + r_px]

        rgb = ImageColor.getrgb(color)
        base = {"fill": rgb + (alpha,), "outline": rgb + (255,), "width": 2}
        base.update(kwargs)

        layer_draw.ellipse(bbox, **base)
        img = Image.alpha_composite(img, layer)

    # Labels
    img_draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", size=max(14, int(14 * scale / 40)))
    except OSError:
        font = ImageFont.load_default()

    base_text = {"fill": "black", "font": font, "anchor": "mm"}
    base_text.update(text_kwargs or {})

    for (cx, cy), label in zip(centres, labels):
        px, py = to_px(cx, cy)
        img_draw.text((px, py), label, **base_text)

    return img
