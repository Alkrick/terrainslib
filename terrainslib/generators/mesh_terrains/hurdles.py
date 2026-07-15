from __future__ import annotations

import numpy as np

from dataclasses import dataclass

from terrainslib.common import Terrain, TerrainCfg, Geometry
from terrainslib.common import utils, build_centered_layout
from terrainslib.common.utils import mesh
from terrainslib.parameters import *

from ..registry import register_terrain


def _hurdles(
    cfg: "HurdlesCfg",
    difficulty,
) -> Terrain:


    # 1. Create base terrain
    base_height, _, _, _, _ = utils.create_terrain_grid(cfg)

    base_geometry = mesh.height_field_to_mesh(
        base_height,
        cfg.horizontal_scale,
        cfg.vertical_scale,
        cfg.slope_threshold,
    )


    # 2. Generate hurdle meshes
    hurdle_geometry = _build_hurdle_mesh(
        cfg,
        difficulty,
    )


    # 3. Merge
    geometry = Geometry.merge(
        base_geometry,
        hurdle_geometry,
    )


    origin = np.array(
        [
            cfg.width / 2,
            cfg.length * 0.05,
            cfg.hurdle_height.resolve(difficulty),
        ]
    )


    return Terrain(
        mesh=geometry,
        height=None,
        origin=origin,
        cfg=cfg,
        metadata={"name": "hurdles"},
    )



def _build_hurdle_mesh(
    cfg: "HurdlesCfg",
    difficulty,
):

    vertices = []
    faces = []

    border = cfg.border_width

    hurdle_depth = cfg.hurdle_depth.resolve(difficulty)
    hurdle_width = cfg.hurdle_width.resolve(difficulty)
    hurdle_height = cfg.hurdle_height.resolve(difficulty)
    spacing = cfg.spacing.resolve(difficulty)

    # Generate hurdles only inside the border
    layout = build_centered_layout(
        total_x=1,
        total_y=cfg.length - 2 * border,
        feature_x=1,
        feature_y=hurdle_depth,
        spacing_x=0,
        spacing_y=spacing,
    )

    x0 = cfg.width / 2 - hurdle_width / 2

    for _, y in layout:

        mesh.add_box(
            vertices,
            faces,
            x0=x0,
            y0=y + border,
            z0=cfg.base_height,
            sx=hurdle_width,
            sy=hurdle_depth,
            sz=hurdle_height,
            resolution=cfg.horizontal_scale,
        )

    return Geometry(
        vertices=np.asarray(vertices, dtype=np.float32),
        faces=np.asarray(faces, dtype=np.int32),
        edges=None,
    )


@register_terrain("hurdles")
@dataclass
class HurdlesCfg(TerrainCfg):

    hurdle_depth: Range = parameter(
        Range(1.2, 0.3)
    )
    
    hurdle_width: Constant = parameter(
        Constant(5.0)
    )

    hurdle_height: Range = parameter(
        Range(0.1, 0.2)
    )

    spacing: Range = parameter(
        Range(2.0, 0.5)
    )


    @property
    def generator(self):
        return _hurdles