from typing import TypeVar, Callable, cast


T = TypeVar("T")

REGISTRY: dict[str, T] = {}


def register_terrain(name: str) -> Callable[[T], T]:
    def decorator(cls: T) -> T:
        if name in REGISTRY:
            raise ValueError(f"Terrain '{name}' already registered")
        cls.name = name
        REGISTRY[name] = cls
        return cls

    return decorator