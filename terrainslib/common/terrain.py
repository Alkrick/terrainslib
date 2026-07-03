from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .terrain_cfg import TerrainCfg
@dataclass
class Terrain:
    height: np.ndarray
    
    cfg: TerrainCfg
    
    origin : np.ndarray | None = None
    
    metadata: dict = field(default_factory=dict)
    
    def meshgrid(self):
        ny, nx = self.height.shape

        x = np.arange(nx) * self.cfg.horizontal_scale
        y = np.arange(ny) * self.cfg.horizontal_scale

        return np.meshgrid(x, y), self.height * self.cfg.vertical_scale
        
        

