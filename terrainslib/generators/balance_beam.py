from __future__ import annotations

import numpy as np

from dataclasses import dataclass, field
from typing import Callable

from terrainslib.common import Terrain, TerrainCfg
from terrainslib.common import utils

from .registry import register_terrain

def _balance_beam(cfg: 'BalanceBeamCfg') -> Terrain:

    height, inner, nx, ny, base_h = utils.create_terrain_grid(cfg)

    beam_px = utils.meters_to_pixels(cfg.beam_width, cfg.horizontal_scale)

    beam_h = utils.meters_to_height(cfg.beam_height, cfg.vertical_scale)
    pit_h = utils.meters_to_height(cfg.pit_depth, cfg.vertical_scale)

    _build_balance_beam(
        inner,
        beam_px,
        beam_h,
        pit_h,
    )

    return Terrain(
        height=height,
        cfg=cfg,
        metadata={"name": "balance_beam"},
    )


def _build_balance_beam(
    height,
    beam_px,
    beam_h,
    pit_h,
):
    nx, ny = height.shape

    height[:,:] = pit_h 

    x0 = (nx - beam_px) // 2
    x1 = x0 + beam_px

    height[:, x0:x1] = beam_h

    return height


@register_terrain("balance_beam")
@dataclass
class BalanceBeamCfg(TerrainCfg):
    
    beam_width: float = 0.30
    beam_height: float = 0.0

    # Pit
    pit_depth: float = -0.40
    
    @property
    def func(self):
        return _balance_beam
