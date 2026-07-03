from __future__ import annotations

import numpy as np

from dataclasses import dataclass, field
from typing import Callable


from terrainslib.common import Terrain, TerrainCfg, build_centered_layout
from terrainslib.common import utils

from .registry import register_terrain

def _hurdles(
    cfg: 'HurdlesCfg'
) -> Terrain:

    nx = utils.meters_to_pixels(cfg.width, cfg.horizontal_scale)
    ny = utils.meters_to_pixels(cfg.length, cfg.horizontal_scale)

    hurdle_px = utils.meters_to_pixels(cfg.hurdle_width, cfg.horizontal_scale)
    spacing_px = utils.meters_to_pixels(cfg.spacing, cfg.horizontal_scale)

    hurdle_h = utils.meters_to_height(cfg.hurdle_height, cfg.vertical_scale)
    base_h = utils.meters_to_height(cfg.base_height, cfg.vertical_scale)

    height = _build_hurdle_course(
        nx,
        ny,
        hurdle_px,
        spacing_px,
        hurdle_h,
        base_h,
    )

    return Terrain(
        height=height,
        cfg=cfg,
        metadata={"name": "hurdles"},
    )


def _build_hurdle_course(
    nx,
    ny,
    hurdle_px,
    spacing_px,
    hurdle_h,
    base_h,
):

    layout = build_centered_layout(
        total_x=1,
        total_y=ny,
        cell_x=1,
        cell_y=hurdle_px,
        spacing_y=spacing_px,
    )

    height = np.full((ny, nx), base_h, dtype=np.float32)

    for iy in range(layout.n_y):

        y0 = layout.offset_y + iy * layout.pitch_y
        y1 = y0 + hurdle_px

        height[y0:y1, :] = hurdle_h

    return height


@register_terrain("hurdles")
@dataclass
class HurdlesCfg(TerrainCfg):

    hurdle_width: float = 0.3
    hurdle_height: float = 0.2
    spacing: float = 3.0
    base_height: float = 0.0
    
    @property
    def func(self):
        return _hurdles
