from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from .geometry import Geometry

if TYPE_CHECKING:
    from .terrain_cfg import TerrainCfg
@dataclass
class Terrain:
    
    height: np.ndarray | None
    
    mesh: Geometry
    
    cfg: TerrainCfg
    
    origin : np.ndarray | None = None
    
    metadata: dict = field(default_factory=dict)
    
        
        

