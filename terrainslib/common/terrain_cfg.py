from __future__ import annotations

from dataclasses import dataclass, field, fields
from abc import abstractmethod
from terrainslib.parameters import ParameterSpec

from .post import post_processing


@dataclass
class TerrainCfg:

    name: str = ""

    width: float = 5.0
    length: float = 5.0

    base_height: float = 0.0

    border_width: float = 0.0
    border_height: float = 0.0

    horizontal_scale: float = 0.05
    vertical_scale: float = 0.02

    slope_threshold: float = 0.0

    post: dict = field(default_factory=dict)

    def convert(self):
        # for f in fields(self):
        #     if not f.metadata.get("range", False):
        #         continue

        #     value = getattr(self, f.name)

        #     if isinstance(value, (list, tuple)) and len(value) == 2:
        #         setattr(self, f.name, Range(value[0], value[1]))
        for f in fields(self):
            param_cls = f.metadata.get("class")
            if param_cls is None:
                continue

            value = getattr(self, f.name)

            if not isinstance(value, ParameterSpec):
                setattr(self, f.name, param_cls.from_config(value))

    @property
    @abstractmethod
    def func(self):
        ...
    
    def generate(self, difficulty=1.0):
        terrain = self.func(self, difficulty) # Returns Terrain object
        terrain = post_processing(terrain, self.post)
        return terrain