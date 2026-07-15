from __future__ import annotations

import numpy as np

from dataclasses import dataclass

from terrainslib.common import Terrain, TerrainCfg, Geometry
from terrainslib.common import utils
from terrainslib.common.utils import mesh
from terrainslib.parameters import *

from ..registry import register_terrain


def _pyramid_stairs(
    cfg: "PyramidStairsCfg",
    difficulty,
):

    #
    # 1. Base terrain
    #
    base_height, _, _, _, _ = utils.create_terrain_grid(cfg)

    _build_base(
        base_height,
        cfg,
    )

    base_geometry = mesh.height_field_to_mesh(
            base_height,
            cfg.horizontal_scale,
            cfg.vertical_scale,
            cfg.slope_threshold,
        )
    

    #
    # 2. Stair geometry
    #
    if cfg.inverted.resolve(difficulty):
        geometry = _build_inverted_pyramid_stairs(
            cfg,
            difficulty,
        )
    else:
        stair_geometry = _build_pyramid_stairs(
            cfg,
            difficulty,
        )
        geometry = Geometry.merge(
            base_geometry,
            stair_geometry,
        )
    

    #
    # 3. Merge
    #

    origin = np.array(
        [
            cfg.width / 2,
            cfg.length / 2,
            cfg.step_height.resolve(difficulty),
        ]
    )

    name = (
        "pyramid_stairs_inv"
        if cfg.inverted.resolve(difficulty)
        else "pyramid_stairs"
    )

    return Terrain(
        mesh=geometry,
        height=None,
        origin=origin,
        cfg=cfg,
        metadata={"name": name},
    )


def _build_base(
    height,
    cfg,
):

    # Flat base at base_height.
    # The reserved border is therefore obstacle-free.
    height[:] = cfg.m2h(cfg.base_height)

def _build_inverted_pyramid_stairs(
    cfg: "PyramidStairsCfg",
    difficulty,
):

    vertices = []
    faces = []

    border = cfg.border_width

    step_width = cfg.step_width.resolve(difficulty)
    step_height = cfg.step_height.resolve(difficulty)
    platform_size = cfg.platform_size.resolve(difficulty)

    terrain_width = cfg.width - 2 * border
    terrain_length = cfg.length - 2 * border

    # Number of stair levels
    num_steps_x = int(
        (terrain_width - platform_size) // (2 * step_width)
    )

    num_steps_y = int(
        (terrain_length - platform_size) // (2 * step_width)
    )

    num_steps = min(num_steps_x, num_steps_y)

    total_height = (num_steps + 1) * step_height


    cx = cfg.width / 2
    cy = cfg.length / 2


    #
    # Generate stair walls
    #
    
    mesh.add_box(
        vertices,
        faces,
        x0=0,
        y0=cfg.length - border,
        z0=-step_height,
        sx=cfg.width,
        sy=border,
        sz=step_height,
        resolution=cfg.horizontal_scale,
    )


    # Bottom wall
    mesh.add_box(
        vertices,
        faces,
        x0=0,
        y0=0,
        z0=-step_height,
        sx=cfg.width,
        sy=border,
        sz=step_height,
        resolution=cfg.horizontal_scale,
    )


    # # Left wall
    mesh.add_box(
        vertices,
        faces,
        x0=0,
        y0=border,
        z0=-step_height,
        sx=border,
        sy=cfg.length - 2 * border,
        sz=step_height,
        resolution=cfg.horizontal_scale,
    )


    # # Right wall
    mesh.add_box(
        vertices,
        faces,
        x0=cfg.width - border,
        y0=border,
        z0=-step_height,
        sx=border,
        sy=cfg.length - 2 * border,
        sz=step_height,
        resolution=cfg.horizontal_scale,
    )

    for k in range(num_steps):

        current_width = terrain_width - 2 * k * step_width
        current_length = terrain_length - 2 * k * step_width

        wall_height = total_height - (k+1) * step_height

        z = -total_height + wall_height / 2

        offset = (k + 0.5) * step_width


        # Top wall
        mesh.add_box(
            vertices,
            faces,
            x0=cx - current_width / 2,
            y0=cy + current_length / 2 - step_width,
            z0=z - wall_height / 2,
            sx=current_width,
            sy=step_width,
            sz=wall_height,
            resolution=cfg.horizontal_scale,
        )


        # Bottom wall
        mesh.add_box(
            vertices,
            faces,
            x0=cx - current_width / 2,
            y0=cy - current_length / 2,
            z0=z - wall_height / 2,
            sx=current_width,
            sy=step_width,
            sz=wall_height,
            resolution=cfg.horizontal_scale,
        )


        # Left wall
        mesh.add_box(
            vertices,
            faces,
            x0=cx - current_width / 2,
            y0=cy - current_length / 2 + step_width,
            z0=z - wall_height / 2,
            sx=step_width,
            sy=current_length - 2 * step_width,
            sz=wall_height,
            resolution=cfg.horizontal_scale,
        )


        # Right wall
        mesh.add_box(
            vertices,
            faces,
            x0=cx + current_width / 2 - step_width,
            y0=cy - current_length / 2 + step_width,
            z0=z - wall_height / 2,
            sx=step_width,
            sy=current_length - 2 * step_width,
            sz=wall_height,
            resolution=cfg.horizontal_scale,
        )


    #
    # Bottom platform
    #
    bottom_size_x = terrain_width - 2 * num_steps * step_width
    bottom_size_y = terrain_length - 2 * num_steps * step_width

    mesh.add_box(
        vertices,
        faces,
        x0=cx - bottom_size_x / 2,
        y0=cy - bottom_size_y / 2,
        z0=-total_height - step_height,
        sx=bottom_size_x,
        sy=bottom_size_y,
        sz=step_height,
        resolution=cfg.horizontal_scale,
    )


    return Geometry(
        vertices=np.asarray(vertices, dtype=np.float32),
        faces=np.asarray(faces, dtype=np.int32),
        edges=None
    )

def _build_pyramid_stairs(
    cfg: "PyramidStairsCfg",
    difficulty,
):

    vertices = []
    faces = []

    border = cfg.border_width

    step_width = cfg.step_width.resolve(difficulty)
    step_height = cfg.step_height.resolve(difficulty)
    platform_size = cfg.platform_size.resolve(difficulty)

    inverted = cfg.inverted.resolve(difficulty)

    size_x = cfg.width - 2 * border
    size_y = cfg.length - 2 * border

    level = 0

    while (
        size_x >= platform_size
        and size_y >= platform_size
    ):

        h = (level + 1) * step_height

        if inverted:
            z0 = cfg.base_height - h
        else:
            z0 = cfg.base_height

        mesh.add_box(
            vertices,
            faces,
            x0=(cfg.width - size_x) * 0.5,
            y0=(cfg.length - size_y) * 0.5,
            z0=z0,
            sx=size_x,
            sy=size_y,
            sz=h,
            resolution=cfg.horizontal_scale,
        )

        size_x -= 2 * step_width
        size_y -= 2 * step_width

        level += 1

    return Geometry(
        vertices=np.asarray(vertices, dtype=np.float32),
        faces=np.asarray(faces, dtype=np.int32),
        edges=None
    )


@register_terrain("pyramid_stairs")
@dataclass
class PyramidStairsCfg(TerrainCfg):

    step_width: Range = parameter(
        Range(0.5, 0.3)
    )

    step_height: Range = parameter(
        Range(0.05, 0.15)
    )

    platform_size: Range = parameter(
        Range(2.0, 2.0)
    )

    inverted: Constant = parameter(
        Constant(False)
    )

    @property
    def generator(self):
        return _pyramid_stairs