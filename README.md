# venncy

Area-proportional 2-circle Venn diagrams for Python — with your choice of renderer.

Unlike [matplotlib-venn](https://github.com/konstantint/matplotlib-venn) which is tied to matplotlib, **venncy** provides a common API across **six** rendering backends so you can pick the one that best fits your workflow.

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

Every renderer exposes the same `plot_venn2` function — just provide the three areas:

```python
from venncy.renderers.matplotlib import plot_venn2

fig, ax = plot_venn2(area_a=300, area_b=200, area_ab=80, labels=("Dogs", "Cats"))
```

Swap `matplotlib` for any other renderer name and the call is the same:

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

## How it works

venncy computes the exact circle radii and centre distance from the three input areas using the [lens geometry](https://en.wikipedia.org/wiki/Lens_(geometry)) formula, then delegates drawing to whichever backend you choose. This means the overlap region is **area-proportional** — not just a schematic.

## Examples

See the [notebooks/](notebooks/) folder for worked examples with each renderer.
