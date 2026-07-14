
from terrainslib.common import Terrain

from .roughness import apply_roughness
from .edge import compute_edges

def post_processing(terrain: Terrain, cfg):
    
    terrain.mesh = terrain.mesh._merge_vertices(terrain.mesh)
    
    if "roughness" in cfg:
        terrain = apply_roughness(terrain, cfg["roughness"])
        
    terrain.mesh.edges = compute_edges(terrain.mesh, resolution=terrain.cfg.horizontal_scale)
    
    return terrain