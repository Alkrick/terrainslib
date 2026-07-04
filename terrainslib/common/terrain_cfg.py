from __future__ import annotations

from dataclasses import dataclass, field
from abc import abstractmethod
from .post import post_processing
from . import utils

@dataclass
class TerrainCfg:
    
    name:str = ''
    
    width: float = 5.0
    length: float = 5.0
    
    base_height: float = 0.0
    
    border_width: float = 0.0
    border_height: float = 0.0
    
    horizontal_scale: float = 0.05
    vertical_scale: float = 0.02
    
    slope_threshold: float = 0.0
    
    post: dict = field(default_factory=dict)
    
    @property
    @abstractmethod
    def func(self):
        ...
    
    def generate(self):
        terrain = self.func(self) # Returns Terrain object
        terrain = post_processing(terrain, self.post)
        
        return terrain
    
    
        
        
    
    