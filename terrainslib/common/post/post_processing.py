
from terrainslib.common import Terrain

from .roughness import apply_roughness


def post_processing(terrain: Terrain, cfg):
    
    if "roughness" in cfg:
        terrain = apply_roughness(terrain, cfg["roughness"])
    
    return terrain