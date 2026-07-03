
from __future__ import annotations

import numpy as np

from dataclasses import dataclass, field
from typing import Callable

from terrainslib.common import Terrain, TerrainCfg, build_centered_layout
from terrainslib.common import utils

from .registry import register_terrain

def _stairs(
    cfg: 'StairsCfg'
) -> Terrain:

    nx = utils.meters_to_pixels(cfg.width, cfg.horizontal_scale)
    ny = utils.meters_to_pixels(cfg.length, cfg.horizontal_scale)

    step_px = max(1, utils.meters_to_pixels(cfg.step_width, cfg.horizontal_scale))
    step_h = utils.meters_to_height(cfg.step_height, cfg.vertical_scale)
    base_h = utils.meters_to_height(cfg.base_height, cfg.vertical_scale)

    height = np.full((ny, nx), base_h, dtype=np.float32)

    if cfg.direction == "y":

        n_steps, offset_y, pitch = utils.compute_centered_tiling(
            ny, step_px, 0
        )

        for i in range(n_steps):
            y0 = offset_y + i * pitch
            y1 = y0 + step_px

            height[y0:y1, :] = base_h + i * step_h

    elif cfg.direction == "x":

        n_steps, offset_x, pitch = utils.compute_centered_tiling(
            nx, step_px, 0
        )

        for i in range(n_steps):
            x0 = offset_x + i * pitch
            x1 = x0 + step_px

            height[:, x0:x1] = base_h + i * step_h

    else:
        raise ValueError("direction must be 'x' or 'y'")

    return Terrain(
        height=height,
        cfg=cfg,
        metadata={
            "name": "stairs",
            "n_steps": int(n_steps),
            "direction": cfg.direction,
        },
    )


@register_terrain("stairs")
@dataclass
class StairsCfg(TerrainCfg):
    
    step_width:float = 0.5
    step_height:float = 0.2

    base_height:float = 0.0
    direction:str = "y"
    
    @property
    def func(self):
        return _stairs