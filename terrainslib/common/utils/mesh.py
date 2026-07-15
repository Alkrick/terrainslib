"""
Utilities for converting heightmap terrains into triangle meshes.
"""

import numpy as np
from ..geometry import Geometry

def add_box(
    vertices,
    faces,
    x0,
    y0,
    z0,
    sx,
    sy,
    sz,
    resolution
):
    """
    Creates a subdivided box mesh.

    All six faces are subdivided uniformly so that:
    - roughness can be applied to any surface
    - topology remains consistent
    - adjacent geometry can share similar resolution

    subdivisions=1 gives a normal box.
    """
    
    subdivisions_x = max(1, int(np.ceil(sx / resolution)))
    subdivisions_y = max(1, int(np.ceil(sy / resolution)))

    vertex_map = {}

    def add_vertex(x, y, z):
        key = (x, y, z)

        if key not in vertex_map:
            vertex_map[key] = len(vertices)
            vertices.append([x, y, z])

        return vertex_map[key]

    def add_quad(v0, v1, v2, v3):
        faces.append([v0, v1, v2])
        faces.append([v0, v2, v3])

    # --------------------------------------------------
    # Bottom and top grids
    # --------------------------------------------------

    bottom = np.zeros(
        (subdivisions_y + 1, subdivisions_x + 1),
        dtype=int,
    )

    top = np.zeros(
        (subdivisions_y + 1, subdivisions_x + 1),
        dtype=int,
    )

    for iy in range(subdivisions_y + 1):

        for ix in range(subdivisions_x + 1):

            x = x0 + sx * ix / subdivisions_x
            y = y0 + sy * iy / subdivisions_y

            bottom[iy, ix] = add_vertex(
                x,
                y,
                z0,
            )

            top[iy, ix] = add_vertex(
                x,
                y,
                z0 + sz,
            )

    # --------------------------------------------------
    # Bottom face
    # --------------------------------------------------

    for iy in range(subdivisions_y):

        for ix in range(subdivisions_x):

            add_quad(
                bottom[iy, ix],
                bottom[iy, ix + 1],
                bottom[iy + 1, ix + 1],
                bottom[iy + 1, ix],
            )

    # --------------------------------------------------
    # Top face
    # --------------------------------------------------

    for iy in range(subdivisions_y):

        for ix in range(subdivisions_x):

            add_quad(
                top[iy, ix],
                top[iy, ix + 1],
                top[iy + 1, ix + 1],
                top[iy + 1, ix],
            )

    # --------------------------------------------------
    # Side faces
    # --------------------------------------------------

    # Front / back (y direction)
    for ix in range(subdivisions_x):

        # front
        add_quad(
            bottom[0, ix],
            bottom[0, ix + 1],
            top[0, ix + 1],
            top[0, ix],
        )

        # back
        add_quad(
            bottom[-1, ix + 1],
            bottom[-1, ix],
            top[-1, ix],
            top[-1, ix + 1],
        )

    # Left / right (x direction)
    for iy in range(subdivisions_y):

        # left
        add_quad(
            bottom[iy + 1, 0],
            bottom[iy, 0],
            top[iy, 0],
            top[iy + 1, 0],
        )

        # right
        add_quad(
            bottom[iy, -1],
            bottom[iy + 1, -1],
            top[iy + 1, -1],
            top[iy, -1],
        )



def grid_to_box_mesh(
    height: np.ndarray,
    horizontal_scale: float,
    vertical_scale: float,
    base_height: float = 0.0,
):
    """
    Convert a heightfield into independent box meshes.

    Each heightfield cell becomes an extruded box.
    """

    ny, nx = height.shape

    vertices = []
    triangles = []

    def add_box(x0, y0, x1, y1, z):

        index = len(vertices)

        z_top = z * vertical_scale
        z_bottom = base_height * vertical_scale

        vertices.extend(
            [
                # bottom
                [x0, y0, z_bottom],
                [x1, y0, z_bottom],
                [x1, y1, z_bottom],
                [x0, y1, z_bottom],

                # top
                [x0, y0, z_top],
                [x1, y0, z_top],
                [x1, y1, z_top],
                [x0, y1, z_top],
            ]
        )

        triangles.extend(
            [
                # bottom
                [index, index + 2, index + 1],
                [index, index + 3, index + 2],

                # top
                [index + 4, index + 5, index + 6],
                [index + 4, index + 6, index + 7],

                # sides
                [index, index + 1, index + 5],
                [index, index + 5, index + 4],

                [index + 1, index + 2, index + 6],
                [index + 1, index + 6, index + 5],

                [index + 2, index + 3, index + 7],
                [index + 2, index + 7, index + 6],

                [index + 3, index, index + 4],
                [index + 3, index + 4, index + 7],
            ]
        )


    for y in range(ny - 1):

        for x in range(nx - 1):

            z = height[y, x]

            x0 = x * horizontal_scale
            x1 = (x + 1) * horizontal_scale

            y0 = y * horizontal_scale
            y1 = (y + 1) * horizontal_scale

            add_box(
                x0,
                y0,
                x1,
                y1,
                z,
            )


    return (
        np.asarray(vertices, dtype=np.float32),
        np.asarray(triangles, dtype=np.int32),
    )



def height_field_to_mesh(
    height_field: np.ndarray,
    horizontal_scale: float,
    vertical_scale: float,
    slope_threshold: float | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Convert a height-field array to a triangle mesh represented by vertices and triangles.

    This function converts a height-field array to a triangle mesh represented by vertices and triangles.
    The height-field array is assumed to be a 2D array of floats, where each element represents the height
    of the terrain at that location. The height-field array is assumed to be in the form of a matrix, where
    the first dimension represents the x-axis and the second dimension represents the y-axis.

    The function can also correct vertical surfaces above the provide slope threshold. This is helpful to
    avoid having long vertical surfaces in the mesh. The correction is done by moving the vertices of the
    vertical surfaces to minimum of the two neighboring vertices.

    The correction is done in the following way:
    If :math:`\\frac{y_2 - y_1}{x_2 - x_1} > threshold`, then move A to A' (i.e., set :math:`x_1' = x_2`).
    This is repeated along all directions (rows, columns) as well as along both diagonals of each grid
    cell, so that box-like corners get a vertical post on all four sides instead of just two.

    .. code-block:: none

                B(x_2,y_2)
                    /|
                   / |
                  /  |
        (x_1,y_1)A---A'(x_1',y_1)

    Note on corners:
        Each interior vertex sits at the intersection of two diagonals of its neighboring grid cells:
        the "\\" diagonal (top-left / bottom-right) and the "/" diagonal (top-right / bottom-left).
        The original correction only ever checked the "\\" diagonal, so box corners oriented along "/"
        (e.g. the top-right and bottom-left corners of an axis-aligned raised platform) were left
        uncorrected and showed up as a diagonal ramp instead of a vertical wall. This version checks
        both diagonals.

    Args:
        height_field: The input height-field array.
        horizontal_scale: The discretization of the terrain along the x and y axis.
        vertical_scale: The discretization of the terrain along the z axis.
        slope_threshold: The slope threshold above which surfaces are made vertical.
            Defaults to None, in which case no correction is applied.

    Returns:
        The vertices and triangles of the mesh:
        - **vertices** (np.ndarray(float)): Array of shape (num_vertices, 3).
          Each row represents the location of each vertex (in m).
        - **triangles** (np.ndarray(int)): Array of shape (num_triangles, 3).
          Each row represents the indices of the 3 vertices connected by this triangle.
    """
    # read height field
    num_rows, num_cols = height_field.shape
    # create a mesh grid of the height field
    y = np.linspace(0, (num_cols - 1) * horizontal_scale, num_cols)
    x = np.linspace(0, (num_rows - 1) * horizontal_scale, num_rows)
    yy, xx = np.meshgrid(y, x)
    # copy height field to avoid modifying the original array
    hf = height_field.copy()

    # correct vertical surfaces above the slope threshold
    if slope_threshold is not None:
        # scale slope threshold based on the horizontal and vertical scale
        slope_threshold *= horizontal_scale / vertical_scale
        # allocate arrays to store the movement of the vertices
        move_x = np.zeros((num_rows, num_cols))
        move_y = np.zeros((num_rows, num_cols))
        move_corners = np.zeros((num_rows, num_cols))
        # NEW: separate x/y accumulators for the anti-diagonal ("/") correction.
        # Unlike the main diagonal, x and y move in OPPOSITE directions here, so they
        # can't be folded into a single "move_corners"-style scalar.
        move_x_anti = np.zeros((num_rows, num_cols))
        move_y_anti = np.zeros((num_rows, num_cols))

        # move vertices along the x-axis
        move_x[: num_rows - 1, :] += (
            hf[1:num_rows, :] - hf[: num_rows - 1, :] > slope_threshold
        )
        move_x[1:num_rows, :] -= (
            hf[: num_rows - 1, :] - hf[1:num_rows, :] > slope_threshold
        )
        # move vertices along the y-axis
        move_y[:, : num_cols - 1] += (
            hf[:, 1:num_cols] - hf[:, : num_cols - 1] > slope_threshold
        )
        move_y[:, 1:num_cols] -= (
            hf[:, : num_cols - 1] - hf[:, 1:num_cols] > slope_threshold
        )
        # move vertices along the main "\" diagonal: pair (i, j) -- (i+1, j+1)
        move_corners[: num_rows - 1, : num_cols - 1] += (
            hf[1:num_rows, 1:num_cols] - hf[: num_rows - 1, : num_cols - 1]
            > slope_threshold
        )
        move_corners[1:num_rows, 1:num_cols] -= (
            hf[: num_rows - 1, : num_cols - 1] - hf[1:num_rows, 1:num_cols]
            > slope_threshold
        )
        # NEW: move vertices along the anti "/" diagonal: pair (i, j+1) -- (i+1, j)
        # if the upper-right vertex is higher, pull the lower-left vertex in (both x and y)
        move_x_anti[1:num_rows, : num_cols - 1] -= (
            hf[: num_rows - 1, 1:num_cols] - hf[1:num_rows, : num_cols - 1]
            > slope_threshold
        )
        move_y_anti[1:num_rows, : num_cols - 1] += (
            hf[: num_rows - 1, 1:num_cols] - hf[1:num_rows, : num_cols - 1]
            > slope_threshold
        )
        # if the lower-left vertex is higher, pull the upper-right vertex in (both x and y)
        move_x_anti[: num_rows - 1, 1:num_cols] += (
            hf[1:num_rows, : num_cols - 1] - hf[: num_rows - 1, 1:num_cols]
            > slope_threshold
        )
        move_y_anti[: num_rows - 1, 1:num_cols] -= (
            hf[1:num_rows, : num_cols - 1] - hf[: num_rows - 1, 1:num_cols]
            > slope_threshold
        )

        xx += (
            move_x + (move_corners + move_x_anti) * (move_x == 0)
        ) * horizontal_scale
        yy += (
            move_y + (move_corners + move_y_anti) * (move_y == 0)
        ) * horizontal_scale

    # create vertices for the mesh
    vertices = np.zeros((num_rows * num_cols, 3), dtype=np.float32)
    vertices[:, 0] = xx.flatten()
    vertices[:, 1] = yy.flatten()
    vertices[:, 2] = hf.flatten() * vertical_scale
    # create triangles for the mesh
    triangles = -np.ones((2 * (num_rows - 1) * (num_cols - 1), 3), dtype=np.uint32)
    for i in range(num_rows - 1):
        ind0 = np.arange(0, num_cols - 1) + i * num_cols
        ind1 = ind0 + 1
        ind2 = ind0 + num_cols
        ind3 = ind2 + 1
        start = 2 * i * (num_cols - 1)
        stop = start + 2 * (num_cols - 1)
        triangles[start:stop:2, 0] = ind0
        triangles[start:stop:2, 1] = ind3
        triangles[start:stop:2, 2] = ind1
        triangles[start + 1 : stop : 2, 0] = ind0
        triangles[start + 1 : stop : 2, 1] = ind2
        triangles[start + 1 : stop : 2, 2] = ind3

    return Geometry(vertices, triangles, None)
