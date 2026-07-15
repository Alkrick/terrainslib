from __future__ import annotations

import numpy as np

from dataclasses import dataclass

from terrainslib.common import Terrain, TerrainCfg, Geometry
from terrainslib.common import build_centered_layout, utils
from terrainslib.common.utils import mesh
from terrainslib.parameters import *

from ..registry import register_terrain


def _stepping_stones(cfg: "SteppingStonesCfg", difficulty):

    # 1. Create base terrain
    base_height, _, _, _, _ = utils.create_terrain_grid(cfg)

    _build_base(
        base_height,
        cfg,
        difficulty,
    )

    # 2. Convert base heightfield to mesh
    base_geometry = mesh.height_field_to_mesh(
        base_height, cfg.horizontal_scale, cfg.vertical_scale, cfg.slope_threshold
    )


    # 3. Generate stone meshes
    stone_geometry = _build_stones(
        cfg,
        difficulty,
    )

    # 4. Merge
    geometry = Geometry.merge(
        base_geometry,
        stone_geometry,
    )

    origin = np.array(
        [
            cfg.width / 2,
            cfg.length * 0.05,
            cfg.stone_height.resolve(difficulty),
        ]
    )

    return Terrain(
        mesh=geometry,
        height=None,
        origin=origin,
        cfg=cfg,
        metadata={"name": "stepping_stones"},
    )


def _build_base(height, cfg, difficulty):

    border = cfg.border_width

    pit_h = cfg.m2h(cfg.pit_height.resolve(difficulty))

    height[:, :] = pit_h

    # restore border
    bw = int(border / cfg.horizontal_scale)

    height[:bw, :] = cfg.base_height
    height[-bw:, :] = cfg.base_height

    height[:, :bw] = cfg.base_height
    height[:, -bw:] = cfg.base_height


def _build_stones(
    cfg: "SteppingStonesCfg",
    difficulty,
):

    vertices = []
    faces = []

    width = cfg.width
    length = cfg.length

    border = cfg.border_width

    pit_h = cfg.pit_height.resolve(difficulty)

    stone_h = cfg.stone_height.resolve(difficulty)

    stone_w = cfg.stone_width.resolve(difficulty)
    stone_l = cfg.stone_length.resolve(difficulty)

    gap_w = cfg.spacing_width.resolve(difficulty)
    gap_l = cfg.spacing_length.resolve(difficulty)

    randomize = cfg.randomize_pos.resolve(difficulty)

    #
    # Layout only inside border
    #
    inner_width = width - 2 * border
    inner_length = length - 2 * border

    layout = build_centered_layout(
        total_x=inner_width,
        total_y=inner_length,
        feature_x=stone_w,
        feature_y=stone_l,
        spacing_x=gap_w,
        spacing_y=gap_l,
    )

    #
    # Generate stones
    #
    for x, y in layout:

        if randomize:
            x += np.random.uniform(0, gap_w)
            y += np.random.uniform(0, gap_l)

        mesh.add_box(
            vertices,
            faces,
            x0=x + border,
            y0=y + border,
            z0=pit_h,
            sx=stone_w,
            sy=stone_l,
            sz=stone_h - pit_h,
            resolution=cfg.horizontal_scale,
        )

    return Geometry(
        vertices=np.asarray(vertices, dtype=np.float32),
        faces=np.asarray(faces, dtype=np.int32),
        edges=None
    )



@register_terrain("stepping_stones")
@dataclass
class SteppingStonesCfg(TerrainCfg):

    stone_width: Range = parameter(Range(0.8, 0.3))

    stone_length: Range = parameter(Range(0.8, 0.3))

    spacing_width: Range = parameter(Range(0.05, 0.15))

    spacing_length: Range = parameter(Range(0.05, 0.15))

    stone_height: Constant = parameter(Constant(0.0))

    pit_height: Constant = parameter(Constant(-0.4))

    randomize_pos: Constant = parameter(Constant(False))

    @property
    def generator(self):
        return _stepping_stones
