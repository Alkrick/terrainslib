from __future__ import annotations

import numpy as np

from dataclasses import dataclass, field

from terrainslib.common import Terrain, TerrainCfg
from terrainslib.common import utils
from terrainslib.parameters import *

from .registry import register_terrain


def _pyramid_slope(cfg: "PyramidSlopeCfg", difficulty) -> Terrain:

    height, inner, nx, ny, base_h = utils.create_terrain_grid(cfg)

    slope = cfg.slope.resolve(difficulty)
    platform = utils.meters_to_pixels(
        cfg.platform_size.resolve(difficulty),
        cfg.horizontal_scale,
    )

    inverted = cfg.inverted.resolve(difficulty)

    _build_pyramid_slope(
        inner,
        slope,
        platform,
        cfg.horizontal_scale,
        cfg.vertical_scale,
        inverted,
    )

    x = nx // 2
    y = ny // 2
    z = height[y, x]

    origin = np.array([x, y, z])

    name = "pyramid_slope_inv" if inverted else "pyramid_slope"

    return Terrain(
        height=height,
        origin=origin,
        cfg=cfg,
        metadata={"name": name},
    )


def _build_pyramid_slope(
    height: np.ndarray,
    slope: float,
    platform: int,
    horizontal_scale: float,
    vertical_scale: float,
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

    height_per_pixel = slope * horizontal_scale / vertical_scale

    pyramid = dist * height_per_pixel

    pyramid -= pyramid.max()

    if inverted:
        height[:] += pyramid
    else:
        height[:] -= pyramid

    np.rint(height, out=height)


@register_terrain("pyramid_slope")
@dataclass
class PyramidSlopeCfg(TerrainCfg):

    slope: Range = parameter(Range(0.2, 0.6))

    platform_size: Range = parameter(Range(1.0, 1.0))

    inverted: Constant = parameter(Constant(False))

    @property
    def func(self):
        return _pyramid_slope