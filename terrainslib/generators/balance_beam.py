from __future__ import annotations

import numpy as np

from dataclasses import dataclass, field

from terrainslib.common import Terrain, TerrainCfg
from terrainslib.common import utils
from terrainslib.parameters import *

from .registry import register_terrain


def _balance_beam(cfg: "BalanceBeamCfg", difficulty: float) -> Terrain:

    height, inner, nx, ny, base_h = utils.create_terrain_grid(cfg)

    beam_px = utils.meters_to_pixels(
        cfg.beam_width.resolve(difficulty), cfg.horizontal_scale
    )

    beam_h = utils.meters_to_height(cfg.beam_height.resolve(difficulty), cfg.vertical_scale)
    pit_h = utils.meters_to_height(cfg.pit_height.resolve(difficulty), cfg.vertical_scale)

    _build_balance_beam(
        inner,
        beam_px,
        beam_h,
        pit_h,
    )

    x = int(0.5 * nx)
    y = int(0.05 * ny)
    z = height[x, y]

    origin = np.array([x, y, z])

    return Terrain(
        height=height,
        origin=origin,
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

    height[:, :] = pit_h

    x0 = (nx - beam_px) // 2
    x1 = x0 + beam_px

    height[:, x0:x1] = beam_h

    return height


@register_terrain("balance_beam")
@dataclass
class BalanceBeamCfg(TerrainCfg):

    beam_width: tuple[float, float] = field(default=(0.3, 0.3), metadata={"class":Range})
    beam_height: tuple[float, float] = field(default=(0.3, 0.3), metadata={"class":Range})

    # Pit
    pit_height: float = field(default=(-0.4), metadata={"class":Constant})

    @property
    def func(self):
        return _balance_beam
