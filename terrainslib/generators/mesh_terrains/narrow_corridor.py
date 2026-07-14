from __future__ import annotations

import numpy as np

from dataclasses import dataclass

from terrainslib.common import Terrain, TerrainCfg, Geometry
from terrainslib.common.utils import mesh
from terrainslib.parameters import *

from ..registry import register_terrain


def _narrow_corridor(cfg: "NarrowCorridorCfg", difficulty):

    geometry = _build_narrow_corridor(
        cfg,
        difficulty,
    )

    origin = np.array(
        [
            cfg.width / 2,
            cfg.length * 0.05,
            cfg.base_height,
        ]
    )

    return Terrain(
        mesh=geometry,
        height=None,
        origin=origin,
        cfg=cfg,
        metadata={"name": "narrow_corridor"},
    )


def _build_narrow_corridor(
    cfg: "NarrowCorridorCfg",
    difficulty,
):

    vertices = []
    faces = []

    corridor_width = cfg.corridor_width.resolve(difficulty)
    wall_height = cfg.wall_height.resolve(difficulty)

    border = cfg.border_width

    wall_width = (cfg.width - corridor_width - 2 * border) / 2


    #
    # Border ring
    #

    # Bottom border
    mesh.add_box(
        vertices,
        faces,
        x0=0,
        y0=0,
        z0=cfg.base_height,
        sx=cfg.width,
        sy=border,
        sz=0.01,
        resolution=cfg.horizontal_scale,
    )

    # Top border
    mesh.add_box(
        vertices,
        faces,
        x0=0,
        y0=cfg.length - border,
        z0=cfg.base_height,
        sx=cfg.width,
        sy=border,
        sz=0.01,
        resolution=cfg.horizontal_scale,
    )

    # Left border
    mesh.add_box(
        vertices,
        faces,
        x0=0,
        y0=border,
        z0=cfg.base_height,
        sx=border,
        sy=cfg.length - 2 * border,
        sz=0.01,
        resolution=cfg.horizontal_scale,
    )

    # Right border
    mesh.add_box(
        vertices,
        faces,
        x0=cfg.width - border,
        y0=border,
        z0=cfg.base_height,
        sx=border,
        sy=cfg.length - 2 * border,
        sz=0.01,
        resolution=cfg.horizontal_scale,
    )


    #
    # Corridor walls
    #

    # Left wall
    mesh.add_box(
        vertices,
        faces,
        x0=border,
        y0=border,
        z0=cfg.base_height,
        sx=wall_width,
        sy=cfg.length - 2 * border,
        sz=wall_height,
        resolution=cfg.horizontal_scale,
    )


    # Right wall
    mesh.add_box(
        vertices,
        faces,
        x0=cfg.width - border - wall_width,
        y0=border,
        z0=cfg.base_height,
        sx=wall_width,
        sy=cfg.length - 2 * border,
        sz=wall_height,
        resolution=cfg.horizontal_scale,
    )


    #
    # Corridor floor
    #
    mesh.add_box(
        vertices,
        faces,
        x0=border + wall_width,
        y0=border,
        z0=cfg.base_height,
        sx=corridor_width,
        sy=cfg.length - 2 * border,
        sz=0.01,
        resolution=cfg.horizontal_scale,
    )


    return Geometry(
        vertices=np.asarray(vertices, dtype=np.float32),
        faces=np.asarray(faces, dtype=np.int32),
        edges=None
    )


@register_terrain("narrow_corridor")
@dataclass
class NarrowCorridorCfg(TerrainCfg):

    corridor_width: Range = parameter(
        Range(0.3, 0.3)
    )

    wall_height: Range = parameter(
        Range(0.3, 0.3)
    )

    @property
    def generator(self):
        return _narrow_corridor