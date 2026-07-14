from __future__ import annotations

import numpy as np

from dataclasses import dataclass, field

from terrainslib.common import Terrain, TerrainCfg
from terrainslib.common import utils
from terrainslib.common.utils import mesh
from terrainslib.parameters import *

from ..registry import register_terrain


def _balance_beam(cfg: "BalanceBeamCfg", difficulty: float) -> Terrain:

    height, inner, nx, ny, base_h = utils.create_terrain_grid(cfg)

    _build_balance_beam(
        inner,
        cfg,
        difficulty
    )

    x = int(0.5 * nx)
    y = int(0.05 * ny)
    z = height[x, y]

    origin = np.array([x, y, z])
    
    geom = mesh.height_field_to_mesh(height, cfg.horizontal_scale, cfg.vertical_scale, cfg.slope_threshold)

    return Terrain(
        mesh=geom,
        height=height,
        origin=origin,
        cfg=cfg,
        metadata={"name": "balance_beam"},
    )


def _build_balance_beam(
    height,
    cfg: "BalanceBeamCfg",
    difficulty
):
    nx, ny = height.shape
    
    pit_h = cfg.m2h(cfg.pit_height.resolve(difficulty))
    beam_h = cfg.m2h(cfg.beam_height.resolve(difficulty))
    beam_px = cfg.m2p(cfg.beam_width.resolve(difficulty))

    height[:, :] = pit_h

    y0 = (nx - beam_px) // 2
    y1 = y0 + beam_px

    height[y0:y1, :] = beam_h

    return height


@register_terrain("balance_beam")
@dataclass
class BalanceBeamCfg(TerrainCfg):

    beam_width: Range = parameter(Range(0.3, 0.3))
    beam_height: Range = parameter(Range(0.3, 0.3))

    # Pit
    pit_height: Constant = parameter(Constant(-0.3))

    @property
    def generator(self):
        return _balance_beam
