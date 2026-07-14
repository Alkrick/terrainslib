from __future__ import annotations

import numpy as np

from dataclasses import dataclass

from terrainslib.common import Terrain, TerrainCfg, Geometry
from terrainslib.common import utils, build_centered_layout
from terrainslib.common.utils import mesh
from terrainslib.parameters import *

from ..registry import register_terrain


def _discrete_boxes(
    cfg: "DiscreteBoxesCfg",
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

    # 2. Generate box geometry
    box_geometry = _build_box_mesh(
        cfg,
        difficulty,
    )

    # 3. Merge geometry
    geometry = Geometry.merge(
        base_geometry,
        box_geometry,
    )

    origin = _get_origin(
        cfg,
        difficulty,
    )

    return Terrain(
        mesh=geometry,
        height=None,
        origin=origin,
        cfg=cfg,
        metadata={"name": "discrete_boxes"},
    )


def _build_box_mesh(
    cfg: "DiscreteBoxesCfg",
    difficulty: float,
):

    vertices = []
    faces = []

    rng = np.random.default_rng(cfg.seed)
    
    border = cfg.border_width

    # Resolve parameters
    box_size = cfg.box_size.resolve(difficulty)
    platform_size = cfg.platform_size.resolve(difficulty)

    width = cfg.width
    length = cfg.length
    
    inner_w = width - 2*border
    inner_l = length - 2*border

    layout = build_centered_layout(
        total_x=inner_w,
        total_y=inner_l,
        feature_x=box_size,
        feature_y=box_size,
    )

    # Center platform
    cx = inner_w / 2
    cy = inner_l / 2

    px0 = cx - platform_size / 2 
    px1 = cx + platform_size / 2

    py0 = cy - platform_size / 2
    py1 = cy + platform_size / 2

    # Ground height
    base_height = cfg.base_height

    # Generate random boxes
    for x, y in layout:
        x1 = x + box_size
        y1 = y + box_size

        h = cfg.box_height.resolve(difficulty)
        # Sample every box independently
        if x < px1 and x1 > px0 and y < py1 and y1 > py0:
            h = 1.5 * cfg.box_height.mid(difficulty)

        mesh.add_box(
            vertices,
            faces,
            x0=x+border,
            y0=y+border,
            z0=base_height,
            sx=box_size,
            sy=box_size,
            sz=h,
            resolution=cfg.horizontal_scale,
        )

    return Geometry(
        vertices=np.asarray(vertices, dtype=np.float32),
        faces=np.asarray(faces, dtype=np.int32),
        edges=None
    )


def _get_origin(
    cfg,
    difficulty,
):

    return np.array(
        [
            cfg.width / 2,
            cfg.length / 2,
            cfg.box_height.resolve(difficulty),
        ]
    )


@register_terrain("discrete_boxes")
@dataclass
class DiscreteBoxesCfg(TerrainCfg):

    box_size: Uniform = parameter(
        Uniform(
            Range(0.1, 0.2),
            Range(0.3, 0.4),
        )
    )

    box_height: Uniform = parameter(
        Uniform(
            Range(0.05, 0.10),
            Range(0.10, 0.15),
        )
    )

    platform_size: Constant = parameter(Constant(1.0))

    @property
    def generator(self):
        return _discrete_boxes
