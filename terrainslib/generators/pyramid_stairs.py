from __future__ import annotations

import numpy as np

from dataclasses import dataclass, field


from terrainslib.common import Terrain, TerrainCfg
from terrainslib.common import utils
from terrainslib.parameters import *

from .registry import register_terrain


def _pyramid_stairs(cfg: "PyramidStairsCfg", difficulty) -> Terrain:

    height, inner, nx, ny, base_h = utils.create_terrain_grid(cfg)

    step_w = utils.meters_to_pixels(
        cfg.step_width.resolve(difficulty), cfg.horizontal_scale
    )
    platform_size = utils.meters_to_height(
        cfg.platform_size.resolve(difficulty), cfg.horizontal_scale
    )
    step_h = utils.meters_to_pixels(
        cfg.step_height.resolve(difficulty), cfg.vertical_scale
    )
    
    inverted = cfg.inverted.resolve(difficulty)

    _build_pyramid_stairs(
        inner,
        step_w,
        step_h,
        platform_size,
        inverted
    )

    x = int(0.5 * nx)
    y = int(0.5 * ny)
    z = height[x, y]

    origin = np.array([x, y, z])
    
    name = "pyramid_stairs"
    if inverted:
        name = "pyramid_stairs_inv"

    return Terrain(
        height=height,
        origin=origin,
        cfg=cfg,
        metadata={"name": name},
    )


def _build_pyramid_stairs(
    height: np.ndarray,
    step_width: int,
    step_height: int,
    platform: int,
    inverted: bool,
):

    ny, nx = height.shape

    cx = nx // 2
    cy = ny // 2

    dx = np.abs(np.arange(nx) - cx)
    dy = np.abs(np.arange(ny) - cy)

    dx = np.maximum(dx - platform // 2, 0)
    dy = np.maximum(dy - platform // 2, 0)

    dist = np.maximum.outer(dy, dx)

    level = dist // step_width

    if inverted:
        height[:] -= (level.max() - level) * step_height
    else:
        height[:] += (level.max() - level) * step_height



@register_terrain("pyramid_stairs")
@dataclass
class PyramidStairsCfg(TerrainCfg):

    step_width: Range = parameter(Range(0.5, 0.5))
    step_height:Range = parameter(Range(0.5, 0.5))
    platform_size: Range = parameter(Range(0.5, 0.5))
    inverted: Constant = parameter(Constant(False))

    @property
    def func(self):
        return _pyramid_stairs
