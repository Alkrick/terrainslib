from __future__ import annotations

import numpy as np

from dataclasses import dataclass, field

from terrainslib.common import Terrain, TerrainCfg, build_centered_layout
from terrainslib.common import utils

from .registry import register_terrain


def _stepping_stones(cfg: "SteppingStonesCfg", difficulty) -> Terrain:
    height, inner, nx, ny, base_h = utils.create_terrain_grid(cfg)

    stone_w = utils.meters_to_pixels(cfg.stone_w.at(difficulty), cfg.horizontal_scale)
    stone_l = utils.meters_to_pixels(cfg.stone_l.at(difficulty), cfg.horizontal_scale)

    gap_w = utils.meters_to_pixels(cfg.spacing_w.at(difficulty), cfg.horizontal_scale)
    gap_l = utils.meters_to_pixels(cfg.spacing_l.at(difficulty), cfg.horizontal_scale)

    stone_h = utils.meters_to_height(cfg.stone_height, cfg.vertical_scale)
    pit_h = utils.meters_to_height(cfg.pit_height, cfg.vertical_scale)

    _build_stepping_stones(
        inner,
        stone_w,
        stone_l,
        gap_w,
        gap_l,
        stone_h,
        base_h,
        pit_h,
        cfg.randomize_pos
    )
    
    x = int(0.5*nx) 
    y = int(0.05*ny)
    z = height[x,y]
    
    origin = np.array([x,y,z])

    return Terrain(
        height=height,
        origin=origin,
        cfg=cfg,
        metadata={"name": "stepping_stones"},
    )


def _build_stepping_stones(
    height,
    stone_w,
    stone_l,
    gap_w,
    gap_l,
    stone_h,
    base_h,
    pit_h,
    randomize
):
    nx, ny = height.shape

    height[:, :] = pit_h

    layout = build_centered_layout(
        total_x=nx,
        total_y=ny,
        feature_x=stone_w,
        feature_y=stone_l,
        spacing_x=gap_w,
        spacing_y=gap_l,
    )
    
    for x0,y0 in layout:
        if randomize:
            y0 = int(y0 + np.random.uniform(0,5))
            x0 = int(x0 + np.random.uniform(0,5))
        
        y1 = y0 + stone_l
        x1 = x0 + stone_w
        
        height[y0:y1, x0:x1] = stone_h


@register_terrain("stepping_stones")
@dataclass
class SteppingStonesCfg(TerrainCfg):

    stone_w: tuple[float, float] = field(default=(0.3, 0.3), metadata={"range":True})
    stone_l: tuple[float, float] = field(default=(0.3, 0.3), metadata={"range":True})
    spacing_w : tuple[float, float] = field(default=(0.3, 0.3), metadata={"range":True})
    spacing_l : tuple[float, float] = field(default=(0.3, 0.3), metadata={"range":True})

    stone_height: float = 0.0
    base_height: float = 0.0
    
    pit_height: float = -0.25
    
    randomize_pos: bool = False

    @property
    def func(self):
        return _stepping_stones
