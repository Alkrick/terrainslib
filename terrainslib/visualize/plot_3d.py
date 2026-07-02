import numpy as np
import matplotlib.pyplot as plt
from terrainslib.common import Terrain


def plot_3d_surface(
    terrain: Terrain,
    stride: int = 1,
    title: str | None = None,
):
    h = terrain.height

    ny, nx = h.shape

    x = np.arange(nx) * terrain.horizontal_scale
    y = np.arange(ny) * terrain.horizontal_scale

    X, Y = np.meshgrid(x, y)
    Z = h * terrain.vertical_scale

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")

    ax.plot_surface(
        X[::stride, ::stride],
        Y[::stride, ::stride],
        Z[::stride, ::stride],
        cmap="terrain",
        linewidth=0,
        antialiased=True,
    )

    if title:
        ax.set_title(title)

    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Z (m)")

    plt.tight_layout()
    plt.show()