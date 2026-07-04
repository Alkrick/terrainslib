from __future__ import annotations

import numpy as np

from dataclasses import dataclass, field
from typing import Callable

from terrainslib.common import Terrain, TerrainCfg, build_centered_layout
from terrainslib.common import utils

from .registry import register_terrain


def _narrow_corridor(
    cfg: 'NarrowCorridorCfg'
) -> Terrain:

    height, inner, nx, ny, base_h = utils.create_terrain_grid(cfg)

    corridor_px = utils.meters_to_pixels(
        cfg.corridor_width,
        cfg.horizontal_scale,
    )

    wall_h = utils.meters_to_height(
        cfg.wall_height,
        cfg.vertical_scale,
    )

    floor_h = utils.meters_to_height(
        cfg.floor_height,
        cfg.vertical_scale,
    )

    _build_narrow_corridor(
        inner,
        corridor_px,
        wall_h,
        floor_h,
    )

    return Terrain(
        height=height,
        cfg=cfg,
        metadata={"name": "narrow_corridor"},
    )


def _build_narrow_corridor(
    height,
    corridor_px,
    wall_h,
    floor_h,
):
    nx, ny = height.shape

    height[:,:] = floor_h

    wall_width = (nx - corridor_px) // 2

    height[:, :wall_width] = wall_h
    height[:, nx - wall_width :] = wall_h

    return height


@register_terrain("narrow_corridor")
@dataclass
class NarrowCorridorCfg(TerrainCfg):
    # Corridor
    corridor_width:float = 0.50

    # Walls
    wall_height:float = 0.50

    # Floor
    floor_height:float = 0.0
    
    @property
    def func(self):
        return _narrow_corridor
