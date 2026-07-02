from typing import Callable

REGISTRY: dict[str, Callable] = {}

def register_terrain(name: str):
    def decorator(func: Callable):
        if name in REGISTRY:
            raise ValueError(f"Terrain '{name}' already registered")
        
        REGISTRY[name]=func
        return func
    return decorator