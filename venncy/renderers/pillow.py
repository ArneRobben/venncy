"""PIL / Pillow renderer for 2-circle Venn diagrams."""

from __future__ import annotations

from venncy import find_2venn_distance, VennResult

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as e:
    raise ImportError(
        "Pillow is required for this renderer. "
        "Install it with:  pip install venncy[pillow]"
    ) from e


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

    Returns:
        A PIL Image (RGBA). Call ``.save(path)`` to export it.
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

    scale = min(width / data_w, height / data_h)

    def to_px(x: float, y: float) -> tuple[float, float]:
        px = (x - xmin) * scale + (width - data_w * scale) / 2
        py = (y + ymax) * scale + (height - data_h * scale) / 2
        return px, py

    # Background
    img = Image.new("RGBA", (width, height), bg_color)

    # Draw each circle on a temporary layer for alpha blending
    for cx, radius, color in [
        (centre_a_x, R, colors[0]),
        (centre_b_x, r, colors[1]),
    ]:
        layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        layer_draw = ImageDraw.Draw(layer)
        px, py = to_px(cx, 0)
        r_px = radius * scale
        bbox = [px - r_px, py - r_px, px + r_px, py + r_px]

        # Convert named colour to RGBA with desired alpha
        from PIL import ImageColor
        rgb = ImageColor.getrgb(color)
        fill_rgba = rgb + (alpha,)
        outline_rgba = rgb + (255,)

        layer_draw.ellipse(bbox, fill=fill_rgba, outline=outline_rgba, width=2)
        img = Image.alpha_composite(img, layer)

    # Labels
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", size=max(14, int(14 * scale / 40)))
    except OSError:
        font = ImageFont.load_default()

    for cx, label in [(centre_a_x, labels[0]), (centre_b_x, labels[1])]:
        px, py = to_px(cx, 0)
        draw.text((px, py), label, fill="black", font=font, anchor="mm")

    return img
