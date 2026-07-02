"""
Utilities for converting heightmap terrains into triangle meshes.
"""

from dataclasses import dataclass

import numpy as np

from terrainslib.common import Terrain


@dataclass
class Mesh:
    """
    Generic triangle mesh representation.

    Attributes
    ----------
    vertices : (N, 3) float array
        XYZ coordinates of every vertex.
    faces : (M, 3) int array
        Triangle indices into vertices.
    """

    vertices: np.ndarray
    faces: np.ndarray


def terrain_to_mesh(terrain: Terrain) -> Mesh:
    """
    Convert a Terrain heightmap into a triangle mesh.

    Parameters
    ----------
    terrain
        Input terrain.

    Returns
    -------
    Mesh
        Triangle mesh.
    """

    height = terrain.height.astype(np.float32)

    ny, nx = height.shape

    # ------------------------------------------------------------------
    # Vertices
    # ------------------------------------------------------------------

    xs = np.arange(nx, dtype=np.float32) * terrain.horizontal_scale
    ys = np.arange(ny, dtype=np.float32) * terrain.horizontal_scale

    X, Y = np.meshgrid(xs, ys)

    Z = height * terrain.vertical_scale

    vertices = np.column_stack(
        (
            X.ravel(),
            Y.ravel(),
            Z.ravel(),
        )
    )

    # ------------------------------------------------------------------
    # Faces
    # ------------------------------------------------------------------

    faces = []

    for y in range(ny - 1):
        for x in range(nx - 1):

            v00 = y * nx + x
            v10 = v00 + 1
            v01 = v00 + nx
            v11 = v01 + 1

            # Triangle 1
            faces.append((v00, v01, v10))

            # Triangle 2
            faces.append((v10, v01, v11))

    faces = np.asarray(faces, dtype=np.int32)

    return Mesh(vertices, faces)