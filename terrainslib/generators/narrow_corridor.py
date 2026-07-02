import numpy as np

from terrainslib.common import Terrain
from terrainslib.common import utils

from .registry import register_terrain


@register_terrain("narrow_corridor")
def narrow_corridor(
    width,
    length,
    horizontal_scale,
    vertical_scale,
    corridor_width,
    wall_height,
    floor_height=0.0,
) -> Terrain:

    nx = utils.meters_to_pixels(width, horizontal_scale)
    ny = utils.meters_to_pixels(length, horizontal_scale)

    corridor_px = utils.meters_to_pixels(
        corridor_width,
        horizontal_scale,
    )

    wall_h = utils.meters_to_height(
        wall_height,
        vertical_scale,
    )

    floor_h = utils.meters_to_height(
        floor_height,
        vertical_scale,
    )

    height = _build_narrow_corridor(
        nx,
        ny,
        corridor_px,
        wall_h,
        floor_h,
    )

    return Terrain(
        height=height,
        horizontal_scale=horizontal_scale,
        vertical_scale=vertical_scale,
        metadata={"type": "narrow_corridor"},
    )


def _build_narrow_corridor(
    nx,
    ny,
    corridor_px,
    wall_h,
    floor_h,
):

    height = np.full((ny, nx), floor_h, dtype=np.float32)

    wall_width = (nx - corridor_px) // 2

    height[:, :wall_width] = wall_h
    height[:, nx - wall_width :] = wall_h

    return height