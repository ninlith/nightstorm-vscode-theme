"""Plotting."""

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from nightstorm.generate import base_chromatic_palette

hue_names = [
    "red",
    "vermilion/orange",
    "amber",
    "gold/yellow",
    "chartreuse/lime",
    "green",
    "aquamarine",
    "turquoise",
    "cyan",
    "azure",
    "blue/indigo",
    "violet",
    "purple",
    "magenta",
    "cerise/rose",
]
data = [
    ("Base Chromatic Palette", base_chromatic_palette, hue_names),
]

def plot(ax, title, palette, labels=None):
    """Plot a color palette."""
    n = len(palette)
    ax.imshow(
        [range(n)],
        cmap=mpl.colors.ListedColormap(list(palette)),
        interpolation="nearest",
        aspect="auto",
    )
    ax.set_xticks(range(n) if labels else [])
    ax.set_xticklabels(labels if labels else [], rotation=45, ha="right", fontsize=8)
    ax.set_yticks([])
    ax.set_title(title)

_, axes = plt.subplots(nrows=len(data), ncols=1, figsize=(8, len(data)*2))
axes = np.ravel(axes)  # ensure iterability
for axis, (palette_name, palette_colors, hue_names) in zip(axes, data):
    plot(ax=axis, title=palette_name, palette=palette_colors, labels=hue_names)
plt.xlabel("hue names")
plt.tight_layout()
plt.show()
