from __future__ import annotations

import numpy as np

from dataclasses import dataclass, field

from terrainslib.common import Terrain, TerrainCfg
from terrainslib.common import utils
from terrainslib.parameters import *

from .registry import register_terrain


def _stairs(cfg: "StairsCfg", difficulty) -> Terrain:

    height, inner, nx, ny, base_h = utils.create_terrain_grid(cfg)

    step_px = max(
        1, utils.meters_to_pixels(cfg.step_width.resolve(difficulty), cfg.horizontal_scale)
    )
    step_h = utils.meters_to_height(cfg.step_height.resolve(difficulty), cfg.vertical_scale)

    n_steps = _build_stairs(inner, cfg.direction.resolve(difficulty), step_px, step_h, base_h)

    x = int(0.5 * nx)
    y = int(0.05 * ny)
    z = height[x, y]

    origin = np.array([x, y, z])

    return Terrain(
        height=height,
        origin=origin,
        cfg=cfg,
        metadata={
            "name": "stairs",
            "n_steps": int(n_steps),
            "direction": cfg.direction,
        },
    )


def _build_stairs(height, direction, step_px, step_h, base_h):
    nx, ny = height.shape

    if direction == "y":

        n_steps, offset_y, pitch = utils.compute_centered_tiling(ny, step_px, 0)

        for i in range(n_steps):
            y0 = offset_y + i * pitch
            y1 = y0 + step_px

            height[y0:y1, :] = base_h + i * step_h

    elif direction == "x":

        n_steps, offset_x, pitch = utils.compute_centered_tiling(nx, step_px, 0)

        for i in range(n_steps):
            x0 = offset_x + i * pitch
            x1 = x0 + step_px

            height[:, x0:x1] = base_h + i * step_h

    else:
        raise ValueError("direction must be 'x' or 'y'")

    return n_steps


@register_terrain("stairs")
@dataclass
class StairsCfg(TerrainCfg):

    step_width: Range = parameter(Range(0.5, 0.5))
    step_height: Range = parameter(Range(0.2, 0.2))

    direction: Choice = parameter(Choice(["x", "y"], [0.5, 0.5]))

    @property
    def func(self):
        return _stairs
