import numpy as np
import open3d as o3d

# from terrainslib.common.utils.mesh import terrain_to_mesh

# ------------------------------------------------------------
# Core utility: height → color
# ------------------------------------------------------------


def _height_to_color(vertices: np.ndarray) -> np.ndarray:
    """
    Maps height to a perceptually useful color gradient.
    """

    z = vertices[:, 2]

    z_min = np.min(z)
    z_max = np.max(z)

    if z_max - z_min < 1e-8:
        t = np.zeros_like(z)
    else:
        t = (z - z_min) / (z_max - z_min)

    # Terrain-like colormap (simple but effective)
    colors = np.zeros((len(t), 3))

    # low → blue/green
    colors[:, 0] = 0.2 * (1 - t)
    colors[:, 1] = 0.4 + 0.4 * t
    colors[:, 2] = 0.6 * (1 - t)

    # high → brighter
    colors += 0.2 * t[:, None]

    return np.clip(colors, 0.0, 1.0)


# ------------------------------------------------------------
# Wireframe overlay
# ------------------------------------------------------------


def _create_wireframe(mesh: o3d.geometry.TriangleMesh):
    lines = o3d.geometry.LineSet.create_from_triangle_mesh(mesh)
    lines.paint_uniform_color([0, 0, 0])
    return lines


def _create_edge_points(points: np.ndarray, z_scale: float = 1.0):
    """
    Create Open3D point cloud from edge points.
    """

    points = points.copy()

    points[:, 2] *= z_scale

    cloud = o3d.geometry.PointCloud()

    cloud.points = o3d.utility.Vector3dVector(points)

    # Red color for visibility
    cloud.paint_uniform_color([1.0, 0.0, 0.0])

    return cloud

# ------------------------------------------------------------
# Main viewer
# ------------------------------------------------------------


def draw_mesh(
    terrain,
    *,
    z_scale: float = 2.0,
    show_wireframe: bool = True,
    show_edges=True,
    show_axes: bool = True,
    show_normals: bool = False,
):
    """
    Debug viewer for heightmap terrains.

    Features:
    - Height-based coloring
    - Optional wireframe overlay
    - Vertical exaggeration
    - Coordinate frame
    """

    mesh_data = terrain.mesh

    vertices = mesh_data.vertices.copy()
    faces = mesh_data.faces

    # --------------------------------------------------------
    # Vertical exaggeration (VERY important for RL terrains)
    # --------------------------------------------------------
    vertices[:, 2] *= z_scale

    # --------------------------------------------------------
    # Build Open3D mesh
    # --------------------------------------------------------
    mesh = o3d.geometry.TriangleMesh()

    mesh.vertices = o3d.utility.Vector3dVector(vertices)
    mesh.triangles = o3d.utility.Vector3iVector(faces)

    # --------------------------------------------------------
    # Normals (lighting quality)
    # --------------------------------------------------------
    mesh.compute_vertex_normals()

    # --------------------------------------------------------
    # Color by height
    # --------------------------------------------------------
    colors = _height_to_color(vertices)
    mesh.vertex_colors = o3d.utility.Vector3dVector(colors)

    # --------------------------------------------------------
    # Optional wireframe
    # --------------------------------------------------------
    geometries = [mesh]

    if show_wireframe:
        geometries.append(_create_wireframe(mesh))
        
     # --------------------------------------------------------
    # Edge points
    # --------------------------------------------------------
    if show_edges and terrain.mesh.edges is not None:

        edge_cloud = _create_edge_points(
            terrain.mesh.edges,
            z_scale,
        )

        geometries.append(edge_cloud)

    # --------------------------------------------------------
    # Coordinate frame
    # --------------------------------------------------------
    if show_axes:
        frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1.0)
        geometries.append(frame)

    # --------------------------------------------------------
    # Optional normals visualization
    # --------------------------------------------------------
    if show_normals:
        mesh.compute_vertex_normals()

    # --------------------------------------------------------
    # Render
    # --------------------------------------------------------
    
    vis = o3d.visualization.Visualizer()

    vis.create_window()

    for geom in geometries:
        vis.add_geometry(geom)

    opt = vis.get_render_option()
    opt.point_size = 10.0
    opt.mesh_show_back_face=True

    vis.run()
    vis.destroy_window()
