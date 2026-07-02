import numpy as np
from dataclasses import dataclass, field


@dataclass
class Terrain:
    height: np.ndarray
    
    horizontal_scale: float
    vertical_scale: float
    
    origin : np.ndarray | None = None
    
    metadata: dict = field(default_factory=dict)
    
    def meshgrid(self):
        ny, nx = self.height.shape

        x = np.arange(nx) * self.horizontal_scale
        y = np.arange(ny) * self.horizontal_scale

        return np.meshgrid(x, y), self.height * self.vertical_scale

