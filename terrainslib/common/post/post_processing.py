
from terrainslib.common import Terrain

from .roughness import apply_roughness
from .edge import compute_edge_map

def post_processing(terrain: Terrain, cfg):
    
    terrain.mesh = terrain.mesh._merge_vertices(terrain.mesh)
    
    post_cfg = cfg.post
    if "roughness" in post_cfg:
        terrain = apply_roughness(terrain, post_cfg["roughness"])
        
    terrain.mesh.edges = compute_edge_map(terrain.mesh, cfg=cfg, resolution=terrain.cfg.horizontal_scale)
    
    return terrain