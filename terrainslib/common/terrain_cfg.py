from __future__ import annotations

import numpy as np

from dataclasses import dataclass, field, fields
from abc import abstractmethod
from terrainslib.parameters import ParameterSpec

from .post import post_processing


@dataclass
class TerrainCfg:

    name: str = ""

    width: float = 8.0
    length: float = 8.0

    base_height: float = 0.0

    border_width: float = 1.0
    border_height: float = 0.0

    horizontal_scale: float = 0.1
    vertical_scale: float = 0.005

    slope_threshold: float = 0.75
    
    seed: int = 0

    post: dict = field(default_factory=dict)
    
    def m2p(self, value):
        return int(np.round(value/self.horizontal_scale))
    
    def m2h(self, value):
        return (value/self.vertical_scale)

    @property
    @abstractmethod
    def generator(self):
        ...
    
    def generate(self, difficulty=1.0):
        terrain = self.generator(self, difficulty) # Returns Terrain object
        terrain = post_processing(terrain, self.post)
        return terrain