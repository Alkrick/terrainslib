from __future__ import annotations

import numpy as np

from dataclasses import dataclass, field

from terrainslib.common import Terrain, TerrainCfg
from terrainslib.common import utils, build_centered_layout
from terrainslib.parameters import *

from .registry import register_terrain


def _discrete_boxes(
    cfg: "DiscreteBoxesCfg",
    difficulty,
) -> Terrain:

    height, inner, nx, ny, base_h = utils.create_terrain_grid(cfg)

    _build_discrete_boxes(inner, cfg, difficulty)

    x = nx // 2
    y = ny // 2
    z = height[y, x]

    origin = np.array([x, y, z])

    return Terrain(
        height=height,
        origin=origin,
        cfg=cfg,
        metadata={"name": "discrete_boxes"},
    )


def _build_discrete_boxes(
    height: np.ndarray,
    cfg: "DiscreteBoxesCfg",
    difficulty: float,
):

    ny, nx = height.shape

    # Resolve terrain-wide parameters
    box_size = cfg.m2p(cfg.box_size.resolve(difficulty))
    platform_size = cfg.m2p(cfg.platform_size.resolve(difficulty))

    layout = build_centered_layout(
        total_x=nx,
        total_y=ny,
        feature_x=box_size,
        feature_y=box_size,
    )

    # Central platform
    cx = nx // 2
    cy = ny // 2

    px0 = cx - platform_size // 2
    px1 = px0 + platform_size

    py0 = cy - platform_size // 2
    py1 = py0 + platform_size

    for x0, y0 in layout:

        x1 = x0 + box_size
        y1 = y0 + box_size

        # Skip cells overlapping the platform
        if x0 < px1 and x1 > px0 and y0 < py1 and y1 > py0:
            continue

        box_height = cfg.m2h(cfg.box_height.resolve(difficulty))

        height[y0:y1, x0:x1] = box_height

    # Platform
    platform_height = cfg.m2h(cfg.box_height.resolve(difficulty))
    height[py0-1:py1+1, px0-1:px1+1] = platform_height


@register_terrain("discrete_boxes")
@dataclass
class DiscreteBoxesCfg(TerrainCfg):

    box_size: Uniform = parameter(Uniform(
        Range(0.1, 0.2),
        Range(0.3, 0.4)
        ))
    
    box_height: Uniform = parameter(Uniform(
        Range(0.05, 0.10),
        Range(0.10, 0.15)
        ))

    platform_size: Constant = parameter(Constant(1.0))

    @property
    def func(self):
        return _discrete_boxes
