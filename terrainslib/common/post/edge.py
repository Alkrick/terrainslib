import numpy as np
from collections import defaultdict

def compute_edges(
    mesh,
    angle_threshold: float = 90.0,
    resolution: float = 0.02,
    remove_boundary=True,
    remove_vertical=True,
):
    """
    Extract sharp geometric edges as sampled 3D points.

    Args:
        angle_threshold:
            Minimum dihedral angle (degrees) considered an edge.

        resolution:
            Distance between sampled points along edges.

    Returns:
        Nx3 array containing points lying on detected edges.
    """

    normals = _face_normals(mesh)

    edge_faces = _build_edge_map(mesh)

    threshold = np.cos(np.deg2rad(180.0 - angle_threshold))

    sharp_edges = []

    for edge, adjacent_faces in edge_faces.items():

        # Boundary edges
        if len(adjacent_faces) == 1:
            sharp_edges.append(edge)
            continue

        # Ignore non-manifold edges
        if len(adjacent_faces) != 2:
            continue

        n1 = normals[adjacent_faces[0]]
        n2 = normals[adjacent_faces[1]]

        if np.dot(n1, n2) < threshold:
            sharp_edges.append(edge)

    if remove_boundary:
        sharp_edges = _filter_boundary_edges(mesh.vertices, sharp_edges)

    if remove_vertical:
        sharp_edges = _filter_vertical_edges(mesh.vertices, sharp_edges)

    points = _sample_edges(
        mesh,
        sharp_edges,
        resolution,
    )

    # Remove duplicate points
    points = np.unique(
        np.round(points, decimals=5),
        axis=0,
    )

    edge_points = points.astype(np.float32)

    return edge_points

def _face_normals(mesh):
    """
    Compute normalized face normals.
    """

    v0 = mesh.vertices[mesh.faces[:, 0]]
    v1 = mesh.vertices[mesh.faces[:, 1]]
    v2 = mesh.vertices[mesh.faces[:, 2]]

    normals = np.cross(
        v1 - v0,
        v2 - v0,
    )

    norm = np.linalg.norm(
        normals,
        axis=1,
        keepdims=True,
    )

    normals /= norm + 1e-8

    return normals


def _build_edge_map(mesh):
    """
    Map each mesh edge to the faces sharing it.
    """

    edge_faces = defaultdict(list)

    for face_id, face in enumerate(mesh.faces):

        for i in range(3):

            a = face[i]
            b = face[(i + 1) % 3]

            edge = tuple(sorted((a, b)))

            edge_faces[edge].append(face_id)

    return edge_faces


def _filter_boundary_edges(vertices, edges):

    x_min = np.min(vertices[:, 0])
    x_max = np.max(vertices[:, 0])

    y_min = np.min(vertices[:, 1])
    y_max = np.max(vertices[:, 1])

    eps = 1e-5

    filtered = []

    for a, b in edges:

        p0 = vertices[a]
        p1 = vertices[b]

        on_x_boundary = (abs(p0[0] - x_min) < eps and abs(p1[0] - x_min) < eps) or (
            abs(p0[0] - x_max) < eps and abs(p1[0] - x_max) < eps
        )

        on_y_boundary = (abs(p0[1] - y_min) < eps and abs(p1[1] - y_min) < eps) or (
            abs(p0[1] - y_max) < eps and abs(p1[1] - y_max) < eps
        )

        if not (on_x_boundary or on_y_boundary):
            filtered.append((a, b))

    return filtered


def _filter_vertical_edges(vertices, edges):

    filtered = []

    for a, b in edges:

        p0 = vertices[a]
        p1 = vertices[b]

        delta = np.abs(p1 - p0)

        # vertical if z dominates xy displacement
        if delta[2] > max(delta[0], delta[1]):
            continue

        filtered.append((a, b))

    return filtered


def _sample_edges(
    mesh,
    edges,
    resolution,
):
    """
    Convert mesh edges into sampled 3D points.
    """

    points = []

    for a, b in edges:

        p0 = mesh.vertices[a]
        p1 = mesh.vertices[b]

        length = np.linalg.norm(p1 - p0)

        count = max(
            2,
            int(np.ceil(length / resolution)),
        )

        t = np.linspace(
            0,
            1,
            count,
        )

        edge_points = (1 - t[:, None]) * p0 + t[:, None] * p1

        points.append(edge_points)

    if len(points) == 0:
        return np.empty(
            (0, 3),
            dtype=np.float32,
        )

    return np.concatenate(
        points,
        axis=0,
    )
