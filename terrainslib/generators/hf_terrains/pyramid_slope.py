from __future__ import annotations

import numpy as np

from dataclasses import dataclass, field

from terrainslib.common import Terrain, TerrainCfg
from terrainslib.common import utils
from terrainslib.common.utils import mesh
from terrainslib.parameters import *

from ..registry import register_terrain


def _pyramid_slope(cfg: "PyramidSlopeCfg", difficulty) -> Terrain:

    height, inner, nx, ny, base_h = utils.create_terrain_grid(cfg)

    _build_pyramid_slope(inner, cfg, difficulty)

    x = int(0.5 * nx)
    y = int(0.5 * ny)
    z = height[y, x] * cfg.vertical_scale

    origin = np.array([x * cfg.horizontal_scale, y * cfg.horizontal_scale, z])

    name = "pyramid_slope_inv" if cfg.inverted.resolve(difficulty) else "pyramid_slope"

    geom = mesh.height_field_to_mesh(
        height, cfg.horizontal_scale, cfg.vertical_scale, cfg.slope_threshold
    )

    return Terrain(
        mesh=geom,
        height=height,
        origin=origin,
        cfg=cfg,
        metadata={"name": name},
    )


def _build_pyramid_slope(height: np.ndarray, cfg: "PyramidSlopeCfg", difficulty):

    slope = cfg.slope.resolve(difficulty)
    platform = cfg.m2p(
        cfg.platform_size.resolve(difficulty),
    )

    inverted = cfg.inverted.resolve(difficulty)

    ny, nx = height.shape

    cx = nx // 2
    cy = ny // 2

    dx = np.abs(np.arange(nx) - cx)
    dy = np.abs(np.arange(ny) - cy)

    dx = np.maximum(dx - platform // 2, 0)
    dy = np.maximum(dy - platform // 2, 0)

    dist = np.maximum.outer(dy, dx)

    height_per_pixel = slope * cfg.horizontal_scale / cfg.vertical_scale

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

    slope: Range = parameter(Range(0.2, 0.2))

    platform_size: Range = parameter(Range(2.0, 2.0))

    inverted: Constant = parameter(Constant(False))

    @property
    def generator(self):
        return _pyramid_slope
