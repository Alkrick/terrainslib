import numpy as np
from dataclasses import dataclass

from terrainslib.common import Terrain


@dataclass
class RoughnessConfig:
    enabled: bool = False

    # noise amplitude in meters
    amplitude: float = 0.02

    # spatial correlation (bigger = smoother noise)
    scale: float = 1.0

    seed: int | None = None


def apply_roughness(
    terrain: Terrain,
    cfg: RoughnessConfig,
) -> Terrain:

    if not cfg.enabled:
        return terrain

    rng = np.random.default_rng(cfg.seed)

    noise = rng.normal(
        loc=0.0,
        scale=cfg.amplitude,
        size=terrain.height.shape,
    )

    # simple smoothing (box filter approximation)
    noise = _box_blur(noise, k=3)

    new_height = terrain.height + noise

    return Terrain(
        height=new_height,
        horizontal_scale=terrain.horizontal_scale,
        vertical_scale=terrain.vertical_scale,
        origin=terrain.origin,
        metadata={
            **terrain.metadata,
            "roughness": cfg.__dict__,
        },
    )
    
def _box_blur(x: np.ndarray, k: int = 3) -> np.ndarray:
    pad = k // 2
    x_pad = np.pad(x, pad, mode="edge")

    out = np.zeros_like(x)

    for i in range(k):
        for j in range(k):
            out += x_pad[i:i + x.shape[0], j:j + x.shape[1]]

    return out / (k * k)