# Venncy

Area-proportional Venn diagrams for Python — 2-circle and 3-circle — with your choice of renderer.

Unlike [matplotlib-venn](https://github.com/konstantint/matplotlib-venn) which is tied to matplotlib, **Venncy** provides a common interface across **six** rendering backends so you can pick the one that best fits your workflow.

| Renderer | Output | Interactive | Install extra |
|----------|--------|-------------|---------------|
| [matplotlib](notebooks/01_matplotlib.ipynb) | Static image (PNG, PDF, …) | No | `pip install venncy[matplotlib]` |
| [plotly](notebooks/02_plotly.ipynb) | Interactive HTML plot | Yes | `pip install venncy[plotly]` |
| [pyvis](notebooks/03_pyvis.ipynb) | Interactive vis.js HTML file | Yes | `pip install venncy[pyvis]` |
| [bokeh](notebooks/04_bokeh.ipynb) | Interactive HTML plot | Yes | `pip install venncy[bokeh]` |
| [drawsvg](notebooks/05_drawsvg.ipynb) | SVG (vector, lightweight) | No | `pip install venncy[drawsvg]` |
| [pillow](notebooks/06_pillow.ipynb) | Raster image (PNG) | No | `pip install venncy[pillow]` |

## Installation

Install the core library:

```bash
pip install venncy
```

Then install one or more rendering backends:

```bash
# Pick what you need
pip install venncy[matplotlib]
pip install venncy[plotly]
pip install venncy[bokeh]

# Or install everything at once
pip install venncy[all]
```

## Quick start

Every renderer exposes `plot_venn2` and `plot_venn3` — just provide the areas:

### 2-circle Venn diagram

```python
from venncy.renderers.matplotlib import plot_venn2

fig, ax = plot_venn2(area_a=300, area_b=200, area_ab=80, labels=("Dogs", "Cats"))
```

### 3-circle Venn diagram

```python
from venncy.renderers.matplotlib import plot_venn3

fig, ax = plot_venn3(
    area_a=300, area_b=200, area_c=150,
    area_ab=80, area_ac=60, area_bc=40,
    labels=("Dogs", "Cats", "Birds"),
)
```

### Swap renderers freely

The same `plot_venn2` / `plot_venn3` interface is available on every backend:

```python
from venncy.renderers.plotly import plot_venn2

fig = plot_venn2(area_a=300, area_b=200, area_ab=80, labels=("Dogs", "Cats"))
fig.show()
```

```python
from venncy.renderers.drawsvg import plot_venn2

drawing = plot_venn2(area_a=300, area_b=200, area_ab=80)
drawing.save_svg("venn.svg")
```

### Pass-through customisation

All renderers accept `**kwargs` forwarded to the underlying drawing primitive (e.g. `matplotlib.patches.Circle`, Bokeh's `ellipse` glyph, `drawsvg.Circle`, etc.) and a separate `text_kwargs` dict forwarded to the label/text API. This lets you customise any property without Venncy having to wrap it explicitly:

```python
fig, ax = plot_venn2(
    area_a=300, area_b=200, area_ab=80,
    edgecolor="black", linestyle="--", hatch="//",
    text_kwargs={"fontsize": 16, "color": "red"},
)
```

## How it works

Venncy computes the exact circle radii and centre distances from the input areas using the [lens (circle–circle intersection) geometry](https://en.wikipedia.org/wiki/Lens_(geometry)) formula, then delegates drawing to whichever backend you choose. Every overlap region is **area-proportional** — not just a schematic.

### Why area-proportional matters

Most Venn diagram libraries treat circles as fixed-size blobs and simply shift them to *suggest* overlap. That is fine for labelling set relationships, but it can be misleading when the relative sizes of groups matter.

Venncy solves for the geometry exactly:

| | 2-circle | 3-circle |
|---|---|---|
| **Radii** | Derived from `area_a`, `area_b` via $r = \sqrt{A/\pi}$ | Same per-circle derivation |
| **Distances** | Single distance `d_ab` solved from the lens-area equation so the intersection area equals `area_ab` | Three pairwise distances (`d_ab`, `d_ac`, `d_bc`) each solved independently, then placed via triangle geometry |

For three circles, each pairwise distance is the exact solution to the lens-area equation for that pair. The three circles are then positioned by placing A at the origin, B on the x-axis at distance `d_ab`, and solving for C's coordinates via the triangle formed by `d_ab`, `d_ac`, `d_bc`. This gives a geometrically faithful layout where every pairwise overlap is area-proportional.

### Comparison with matplotlib-venn

[matplotlib-venn](https://github.com/konstantint/matplotlib-venn) is the most popular Python Venn library. It does not guarantee geometric faithfulness for either two- or three-circle diagrams. For **two circles**, it will happily draw impossible inputs (e.g. `subsets=(1, 1, 3)` where the overlap exceeds both circles) without warning. For **three circles**, it uses a numerical optimisation routine that minimises a cost function over circle positions — a heuristic that does not guarantee exact pairwise overlaps. The result is an approximation where the actual intersection areas may deviate from the requested values.

Venncy takes a different approach: it solves each pairwise distance analytically (via root-finding on the closed-form lens-area equation) and positions the three circles using exact triangle geometry. The trade-off is that the triple-overlap region (`A ∩ B ∩ C`) is not independently controlled — it falls out of the pairwise geometry — but every pairwise overlap is exact by construction.

Because Venncy insists on geometric exactness, it will **refuse to draw impossible inputs**. For example, `area_a=1, area_b=1, area_ab=2` is not geometrically realisable — the overlap cannot be larger than either circle. matplotlib-venn will still produce *something* in cases like this (since it optimises a best-fit layout), but the result has no meaningful geometric interpretation. Venncy raises an error instead, so you know immediately that the input data is inconsistent.

## Examples

See the [notebooks/](notebooks/) folder for worked examples with each renderer.
