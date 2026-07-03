from dataclasses import dataclass, field
from abc import abstractmethod
from .post import post_processing

@dataclass
class TerrainCfg:
    
    name:str = ''
    
    width: float = 5.0
    length: float = 5.0
    
    horizontal_scale: float = 0.05
    vertical_scale: float = 0.02
    
    post: dict = field(default_factory=dict)
    
    @property
    @abstractmethod
    def func(self):
        ...
    
    def generate(self):
        terrain = self.func(self)
        terrain = post_processing(terrain, self.post)
        
        return terrain
        
        
    
    