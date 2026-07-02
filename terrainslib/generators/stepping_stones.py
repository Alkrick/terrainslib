import numpy as np

from terrainslib.common import Terrain, build_centered_layout
from terrainslib.common import utils


from .registry import register_terrain


@register_terrain("stepping_stones")
def stepping_stones(
    width,
    length,
    horizontal_scale,
    vertical_scale,
    stone_size,
    spacing,
    stone_height,
    base_height=0.0,
) -> Terrain:

    nx = utils.meters_to_pixels(width, horizontal_scale)
    ny = utils.meters_to_pixels(length, horizontal_scale)

    stone_w = utils.meters_to_pixels(stone_size[0], horizontal_scale)
    stone_l = utils.meters_to_pixels(stone_size[1], horizontal_scale)

    gap_w = utils.meters_to_pixels(spacing[0], horizontal_scale)
    gap_l = utils.meters_to_pixels(spacing[1], horizontal_scale)

    stone_h = utils.meters_to_height(stone_height, vertical_scale)
    base_h = utils.meters_to_height(base_height, vertical_scale)

    height = _build_stepping_stones(
        nx,
        ny,
        stone_w,
        stone_l,
        gap_w,
        gap_l,
        stone_h,
        base_h,
    )

    return Terrain(
        height=height,
        horizontal_scale=horizontal_scale,
        vertical_scale=vertical_scale,
        origin=None,
        metadata={"type": "stepping_stones"},
    )


def _build_stepping_stones(
    nx,
    ny,
    stone_w,
    stone_l,
    gap_w,
    gap_l,
    stone_h,
    base_h,
):
    layout = build_centered_layout(
        total_x=nx,
        total_y=ny,
        cell_x=stone_w,
        cell_y=stone_l,
        spacing_x=gap_w,
        spacing_y=gap_l,
    )

    height = np.full((ny, nx), base_h, dtype=np.float32)

    for iy in range(layout.n_y):
        y0 = layout.offset_y + iy * layout.pitch_y
        y1 = y0 + stone_l

        for ix in range(layout.n_x):
            x0 = layout.offset_x + ix * layout.pitch_x
            x1 = x0 + stone_w

            height[y0:y1, x0:x1] = stone_h

    return height
