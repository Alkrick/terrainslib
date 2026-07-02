import numpy as np
import matplotlib.pyplot as plt
from terrainslib.common import Terrain

def plot_heightmap(
    terrain: Terrain,
    cmap: str = "terrain",
    show_colorbar: bool = True,
    title: str | None = None,
):
    h = terrain.height

    plt.figure(figsize=(8, 6))
    im = plt.imshow(h, cmap=cmap, origin="lower")

    if show_colorbar:
        plt.colorbar(im, label="Height (grid units)")

    if title:
        plt.title(title)

    plt.xlabel("X")
    plt.ylabel("Y")
    plt.tight_layout()
    plt.show()


def plot_heightmap_meters(
    terrain: Terrain,
    cmap: str = "terrain",
):
    h_m = terrain.height * terrain.vertical_scale

    plt.figure(figsize=(8, 6))
    im = plt.imshow(h_m, cmap=cmap, origin="lower")

    plt.colorbar(im, label="Height (m)")
    plt.title("Terrain Height (meters)")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.tight_layout()
    plt.show()


def plot_contours(
    terrain: Terrain,
    levels: int = 20,
):
    h = terrain.height

    plt.figure(figsize=(8, 6))
    plt.contour(h, levels=levels, colors="black", linewidths=0.5)

    plt.title("Terrain Contours")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.axis("equal")
    plt.tight_layout()
    plt.show()


