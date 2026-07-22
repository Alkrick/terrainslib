import numpy as np
from collections import defaultdict
from terrainslib.common.utils import create_terrain_grid

import matplotlib.pylab as plt

def compute_edge_map(
    mesh,
    cfg,
    angle_threshold: float = 90.0,
    resolution: float = 0.02,
    remove_boundary=True,
    remove_vertical=True,
):
    
    edge_segments = compute_edges(mesh, angle_threshold, resolution, remove_boundary, remove_vertical)
    
    # base_grid, _, nx, ny, _ = create_terrain_grid(cfg)
    
    # H, W = base_grid.shape
    # edge_mask = np.zeros_like(base_grid, dtype=np.bool)
    
    # ix = np.round((edge_segments[:, 0])/ cfg.horizontal_scale).astype(int)
    # iy = np.round((edge_segments[:, 1])/ cfg.horizontal_scale).astype(int)
    
    # valid = (
    #     (ix>=0) & (ix < W) & 
    #     (iy>=0) & (iy < H)
    # )
    
    # edge_mask[iy[valid], ix[valid]] = True
    
    # plt.imshow(edge_mask)
    # plt.show()
    
    return edge_segments

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
    
    # sharp_edges = list(set(
    #     tuple(sorted(e))
    #     for e in sharp_edges
    # ))
    
    # print(f"Edges len: {len(sharp_edges)}")
    # print(f"Filtered vertices shape: {mesh.vertices[np.asarray(sharp_edges)].shape}")
    # print(f"Mesh vertices shape: {mesh.vertices.shape}")
    # print(f"Mesh faces shape: {mesh.faces.shape}")

    # lengths = np.linalg.norm(
    #     mesh.vertices[np.asarray(sharp_edges)][:,1] -
    #     mesh.vertices[np.asarray(sharp_edges)][:,0],
    #     axis=1
    # )

    # print(f"Lengths - Min: {lengths.min()}, Max: {lengths.max()}, Mean: {lengths.mean()}")
        
    edge_segments = np.empty(0)
    if len(sharp_edges) != 0:
        edge_segments = np.stack(
            [
                mesh.vertices[[a for a, _ in sharp_edges]],
                mesh.vertices[[b for _, b in sharp_edges]],
            ],
            axis=1,
        ).astype(np.float32)
        
    # print("Before:", len(edge_segments))

    merged_segments = _merge_collinear_segments(
        edge_segments
    )

    # print("After:", len(merged_segments))

    return merged_segments

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

def _merge_collinear_segments(
    segments,
    angle_threshold=1e-5,
    position_threshold=1e-5,
):
    """
    Merge connected collinear line segments.

    Args:
        segments:
            [N,2,3] array

    Returns:
        [M,2,3] merged segments
    """

    # Use tuples as vertex keys
    vertices = {}

    def vertex_id(p):
        key = tuple(np.round(p, 5))
        if key not in vertices:
            vertices[key] = len(vertices)
        return vertices[key]

    edges = []

    for s in segments:
        a = vertex_id(s[0])
        b = vertex_id(s[1])
        edges.append((a, b))

    points = np.array(list(vertices.keys()))

    # adjacency
    adjacency = defaultdict(list)

    for i, (a, b) in enumerate(edges):
        adjacency[a].append((i, b))
        adjacency[b].append((i, a))


    visited = np.zeros(len(edges), dtype=bool)

    merged = []


    def is_collinear(p0, p1, p2):
        """
        Check if p0->p1 and p1->p2 are same line.
        """

        v1 = p1 - p0
        v2 = p2 - p1

        n1 = np.linalg.norm(v1)
        n2 = np.linalg.norm(v2)

        if n1 < 1e-8 or n2 < 1e-8:
            return False

        v1 /= n1
        v2 /= n2

        return np.linalg.norm(v1 - v2) < angle_threshold or \
               np.linalg.norm(v1 + v2) < angle_threshold


    for edge_id in range(len(edges)):

        if visited[edge_id]:
            continue

        # start segment
        a, b = edges[edge_id]

        start = a
        end = b

        visited[edge_id] = True


        # extend forward
        changed = True

        while changed:

            changed = False

            for eid, nxt in adjacency[end]:

                if visited[eid]:
                    continue

                if is_collinear(
                    points[start],
                    points[end],
                    points[nxt],
                ):
                    visited[eid] = True
                    end = nxt
                    changed = True
                    break


        # extend backwards
        changed = True

        while changed:

            changed = False

            for eid, nxt in adjacency[start]:

                if visited[eid]:
                    continue

                if is_collinear(
                    points[nxt],
                    points[start],
                    points[end],
                ):
                    visited[eid] = True
                    start = nxt
                    changed = True
                    break


        merged.append(
            [
                points[start],
                points[end],
            ]
        )


    return np.asarray(merged, dtype=np.float32)

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
