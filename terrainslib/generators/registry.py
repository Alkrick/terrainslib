from typing import Type

from terrainslib.common import TerrainCfg

REGISTRY: dict[str, Type[TerrainCfg]] = {}


def register_terrain(name: str):
    def decorator(cls: Type[TerrainCfg]):
        if name in REGISTRY:
            raise ValueError(f"Terrain '{name}' already registered")

        cls.name = name
        REGISTRY[name] = cls
        return cls

    return decorator