from __future__ import annotations

import numpy as np

from dataclasses import dataclass, field

from terrainslib.common import Terrain, TerrainCfg
from terrainslib.common import utils
from terrainslib.parameters import *

from .registry import register_terrain


def _discrete_boxes(
    cfg: "DiscreteBoxesCfg",
    difficulty,
) -> Terrain:

    height, inner, nx, ny, base_h = utils.create_terrain_grid(cfg)

    print(cfg.box_size)
    print(cfg.box_height)

    box_size = utils.meters_to_pixels(
        cfg.box_size.resolve(difficulty),
        cfg.horizontal_scale,
    )

    platform_size = utils.meters_to_pixels(
        cfg.platform_size.resolve(difficulty),
        cfg.horizontal_scale,
    )

    rng = np.random.default_rng(cfg.seed)

    _build_discrete_boxes(inner, box_size, platform_size, base_h, rng, cfg)

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


def _build_discrete_boxes(height, box_size, platform_size, base_h, rng, cfg):

    ny, nx = height.shape

    # initialize ground
    height[:] = base_h

    cx = nx // 2
    cy = ny // 2

    # central platform
    px0 = cx - platform_size // 2
    px1 = cx + platform_size // 2

    py0 = cy - platform_size // 2
    py1 = cy + platform_size // 2

    box_height = utils.meters_to_height(
        cfg.box_height.resolve(),
        cfg.vertical_scale,
    )

    height[py0:py1, px0:px1] = box_height

    # grid around the platform
    for y in range(0, ny, box_size):

        for x in range(0, nx, box_size):

            box_height = utils.meters_to_height(
                cfg.box_height.resolve(),
                cfg.vertical_scale,
            )

            # skip platform
            if x < px1 and x + box_size > px0 and y < py1 and y + box_size > py0:
                continue

            # random box height
            h = rng.choice([0, box_height])

            if h > 0:
                height[y : y + box_size, x : x + box_size] = h


@register_terrain("discrete_boxes")
@dataclass
class DiscreteBoxesCfg(TerrainCfg):

    box_size: Uniform = parameter(Uniform(0.2, 0.4))
    box_height: Uniform = parameter(Uniform(0.15, 0.15))

    platform_size: Constant = parameter(Constant(1.0))

    @property
    def func(self):
        return _discrete_boxes
