import numpy as np

from terrainslib.common import Terrain, build_centered_layout
from terrainslib.common import utils

from .registry import register_terrain


@register_terrain("hurdles")
def hurdles(
    width,
    length,
    horizontal_scale,
    vertical_scale,
    hurdle_width,
    hurdle_height,
    spacing,
    base_height=0.0,
) -> Terrain:

    nx = utils.meters_to_pixels(width, horizontal_scale)
    ny = utils.meters_to_pixels(length, horizontal_scale)

    hurdle_px = utils.meters_to_pixels(hurdle_width, horizontal_scale)
    spacing_px = utils.meters_to_pixels(spacing, horizontal_scale)

    hurdle_h = utils.meters_to_height(hurdle_height, vertical_scale)
    base_h = utils.meters_to_height(base_height, vertical_scale)

    height = _build_hurdle_course(
        nx,
        ny,
        hurdle_px,
        spacing_px,
        hurdle_h,
        base_h,
    )

    return Terrain(
        height=height,
        horizontal_scale=horizontal_scale,
        vertical_scale=vertical_scale,
        metadata={"type": "hurdles"},
    )


def _build_hurdle_course(
    nx,
    ny,
    hurdle_px,
    spacing_px,
    hurdle_h,
    base_h,
):

    layout = build_centered_layout(
        total_x=1,
        total_y=ny,
        cell_x=1,
        cell_y=hurdle_px,
        spacing_y=spacing_px,
    )

    height = np.full((ny, nx), base_h, dtype=np.float32)

    for iy in range(layout.n_y):

        y0 = layout.offset_y + iy * layout.pitch_y
        y1 = y0 + hurdle_px

        height[y0:y1, :] = hurdle_h

    return height