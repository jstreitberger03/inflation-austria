"""
Style system for the inflation_report package.

Provides functions to apply a clean Matplotlib theme using Paul Tol colorblind-safe palettes,
with dotted y-major grid lines and sensible defaults for publication-quality plots.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Dict, Iterable, List, Optional

import matplotlib.pyplot as plt
from matplotlib import cycler

# Paul Tol's colorblind safe palettes (hex codes from Paul Tol's website)
PAUL_TOL_PALETTES: Dict[str, List[str]] = {
    "bright": [
        "#4477AA",
        "#EE6677",
        "#228833",
        "#CCBB44",
        "#66CCEE",
        "#AA3377",
        "#BBBBBB",
    ],
    "muted": [
        "#332288",
        "#88CCEE",
        "#44AA99",
        "#117733",
        "#999933",
        "#DDCC77",
        "#CC6677",
        "#882255",
        "#AA4499",
    ],
}


def apply_template(
    palette: str = "bright",
    font_size: int = 11,
    font_family: Optional[str] = None,
    mathtext_fontset: Optional[str] = "cm",
) -> None:
    """
    Configure Matplotlib with the minimal template style.
    """
    colors = PAUL_TOL_PALETTES.get(palette, PAUL_TOL_PALETTES["bright"])

    plt.style.use("default")
    plt.rcParams.update(
        {
            "axes.prop_cycle": cycler(color=colors),
            "axes.facecolor": "white",
            "figure.facecolor": "white",
            "axes.edgecolor": "#A0A0A0",
            "axes.linewidth": 0.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "axes.grid.axis": "y",
            "grid.alpha": 0.8,
            "grid.color": "#B0B0B0",
            "grid.linewidth": 0.8,
            "grid.linestyle": (0, (1, 3)),  # densely dotted
            "axes.titlesize": font_size + 1,
            "axes.labelsize": font_size,
            "xtick.labelsize": font_size - 1,
            "ytick.labelsize": font_size - 1,
            "font.size": font_size,
            "legend.frameon": False,
            "legend.fontsize": font_size - 1,
            "figure.autolayout": True,
        }
    )
    if font_family:
        plt.rcParams["font.family"] = [font_family, "DejaVu Sans", "sans-serif"]
    if mathtext_fontset:
        plt.rcParams["mathtext.fontset"] = mathtext_fontset


@contextmanager
def style_context(palette: str = "bright", font_size: int = 11):
    """
    Context manager to temporarily apply the template style.
    """
    with plt.rc_context():
        apply_template(palette=palette, font_size=font_size)
        yield


def palette_colors(name: str = "bright") -> Iterable[str]:
    """
    Return the list of hex colors for a given Tol palette.
    """
    return PAUL_TOL_PALETTES.get(name, PAUL_TOL_PALETTES["bright"])
