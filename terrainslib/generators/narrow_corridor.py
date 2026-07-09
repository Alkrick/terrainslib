from __future__ import annotations

import numpy as np

from dataclasses import dataclass, field

from terrainslib.common import Terrain, TerrainCfg
from terrainslib.common import utils
from terrainslib.parameters import *

from .registry import register_terrain


def _narrow_corridor(cfg: "NarrowCorridorCfg", difficulty) -> Terrain:

    height, inner, nx, ny, base_h = utils.create_terrain_grid(cfg)

    corridor_px = utils.meters_to_pixels(
        cfg.corridor_width.resolve(difficulty),
        cfg.horizontal_scale,
    )

    wall_h = utils.meters_to_height(
        cfg.wall_height.resolve(difficulty),
        cfg.vertical_scale,
    )

    _build_narrow_corridor(
        inner,
        corridor_px,
        wall_h,
        base_h,
    )

    x = int(0.5 * nx)
    y = int(0.05 * ny)
    z = height[x, y]

    origin = np.array([x, y, z])

    return Terrain(
        height=height,
        origin=origin,
        cfg=cfg,
        metadata={"name": "narrow_corridor"},
    )


def _build_narrow_corridor(
    height,
    corridor_px,
    wall_h,
    base_h,
):
    nx, ny = height.shape

    height[:, :] = base_h

    wall_width = (nx - corridor_px) // 2

    height[:, :wall_width] = wall_h
    height[:, nx - wall_width :] = wall_h

    return height


@register_terrain("narrow_corridor")
@dataclass
class NarrowCorridorCfg(TerrainCfg):
    # Corridor
    corridor_width: tuple[float, float] = field(default=(0.5, 0.5), metadata={"class":Range})

    # Walls
    wall_height: tuple[float, float] = field(default=(0.5, 0.5), metadata={"class":Range})

    @property
    def func(self):
        return _narrow_corridor
