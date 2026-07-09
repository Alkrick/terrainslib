from __future__ import annotations

import numpy as np

from dataclasses import dataclass, field


from terrainslib.common import Terrain, TerrainCfg, build_centered_layout
from terrainslib.common import utils
from terrainslib.parameters import *

from .registry import register_terrain


def _hurdles(cfg: "HurdlesCfg", difficulty) -> Terrain:

    height, inner, nx, ny, base_h = utils.create_terrain_grid(cfg)

    hurdle_px = utils.meters_to_pixels(
        cfg.hurdle_width.resolve(difficulty), cfg.horizontal_scale
    )
    spacing_px = utils.meters_to_pixels(
        cfg.spacing.resolve(difficulty), cfg.horizontal_scale
    )
    hurdle_h = utils.meters_to_height(
        cfg.hurdle_height.resolve(difficulty), cfg.vertical_scale
    )

    _build_hurdle_course(
        inner,
        hurdle_px,
        spacing_px,
        hurdle_h,
        base_h,
    )

    x = int(0.5 * nx)
    y = int(0.05 * ny)
    z = height[x, y]

    origin = np.array([x, y, z])

    return Terrain(
        height=height,
        origin=origin,
        cfg=cfg,
        metadata={"name": "hurdles"},
    )


def _build_hurdle_course(
    height,
    hurdle_px,
    spacing_px,
    hurdle_h,
    base_h,
):

    nx, ny = height.shape

    height[:, :] = base_h

    layout = build_centered_layout(
        total_x=1,
        total_y=ny,
        feature_x=1,
        feature_y=hurdle_px,
        spacing_y=spacing_px,
    )

    for _, y0 in layout:
        y1 = y0 + hurdle_px

        height[y0:y1, :] = hurdle_h


@register_terrain("hurdles")
@dataclass
class HurdlesCfg(TerrainCfg):

    hurdle_width: tuple[float, float] = field(default=(0.5, 0.5), metadata={"class":Range})
    hurdle_height: tuple[float, float] = field(default=(0.5, 0.5), metadata={"class":Range})
    spacing: tuple[float, float] = field(default=(0.5, 0.5), metadata={"class":Range})

    @property
    def func(self):
        return _hurdles
