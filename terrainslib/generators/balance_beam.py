import numpy as np

from terrainslib.common import Terrain
from terrainslib.common import utils

from .registry import register_terrain


@register_terrain("balance_beam")
def balance_beam(
    width,
    length,
    horizontal_scale,
    vertical_scale,
    beam_width,
    pit_depth,
    beam_height=0.0,
) -> Terrain:

    nx = utils.meters_to_pixels(width, horizontal_scale)
    ny = utils.meters_to_pixels(length, horizontal_scale)

    beam_px = utils.meters_to_pixels(beam_width, horizontal_scale)

    beam_h = utils.meters_to_height(beam_height, vertical_scale)
    pit_h = utils.meters_to_height(pit_depth, vertical_scale)

    height = _build_balance_beam(
        nx,
        ny,
        beam_px,
        beam_h,
        pit_h,
    )

    return Terrain(
        height=height,
        horizontal_scale=horizontal_scale,
        vertical_scale=vertical_scale,
        metadata={"type": "balance_beam"},
    )


def _build_balance_beam(
    nx,
    ny,
    beam_px,
    beam_h,
    pit_h,
):

    height = np.full((ny, nx), pit_h, dtype=np.float32)

    x0 = (nx - beam_px) // 2
    x1 = x0 + beam_px

    height[:, x0:x1] = beam_h

    return height