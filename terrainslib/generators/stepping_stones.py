from __future__ import annotations

import numpy as np

from dataclasses import dataclass, field
from typing import Callable

from terrainslib.common import Terrain, TerrainCfg, build_centered_layout
from terrainslib.common import utils

from .registry import register_terrain


def _stepping_stones(
    cfg :'SteppingStonesCfg'
) -> Terrain:

    nx = utils.meters_to_pixels(cfg.width, cfg.horizontal_scale)
    ny = utils.meters_to_pixels(cfg.length, cfg.horizontal_scale)

    stone_w = utils.meters_to_pixels(cfg.stone_size[0], cfg.horizontal_scale)
    stone_l = utils.meters_to_pixels(cfg.stone_size[1], cfg.horizontal_scale)

    gap_w = utils.meters_to_pixels(cfg.spacing[0], cfg.horizontal_scale)
    gap_l = utils.meters_to_pixels(cfg.spacing[1], cfg.horizontal_scale)

    stone_h = utils.meters_to_height(cfg.stone_height, cfg.vertical_scale)
    base_h = utils.meters_to_height(cfg.base_height, cfg.vertical_scale)

    height = _build_stepping_stones(
        nx,
        ny,
        stone_w,
        stone_l,
        gap_w,
        gap_l,
        stone_h,
        base_h,
    )

    return Terrain(
        height=height,
        cfg=cfg,
        metadata={"name": "stepping_stones"},
    )


def _build_stepping_stones(
    nx,
    ny,
    stone_w,
    stone_l,
    gap_w,
    gap_l,
    stone_h,
    base_h,
):
    layout = build_centered_layout(
        total_x=nx,
        total_y=ny,
        cell_x=stone_w,
        cell_y=stone_l,
        spacing_x=gap_w,
        spacing_y=gap_l,
    )

    height = np.full((ny, nx), base_h, dtype=np.float32)

    for iy in range(layout.n_y):
        y0 = layout.offset_y + iy * layout.pitch_y
        y1 = y0 + stone_l

        for ix in range(layout.n_x):
            x0 = layout.offset_x + ix * layout.pitch_x
            x1 = x0 + stone_w

            height[y0:y1, x0:x1] = stone_h

    return height


@register_terrain("stepping_stones")
@dataclass
class SteppingStonesCfg(TerrainCfg):

    stone_size = [0.4, 0.4]
    spacing = [0.3, 0.3]

    stone_height:float = 0.0
    base_height:float = -0.25
    
    @property
    def func(self):
        return _stepping_stones