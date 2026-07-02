
import numpy as np

from terrainslib.common import Terrain
from terrainslib.common import utils

from .registry import register_terrain

@register_terrain("stairs")
def stairs(
    width,
    length,
    horizontal_scale,
    vertical_scale,
    step_width,
    step_height,
    base_height=0.0,
    direction="y",
) -> Terrain:

    nx = utils.meters_to_pixels(width, horizontal_scale)
    ny = utils.meters_to_pixels(length, horizontal_scale)

    step_px = max(1, utils.meters_to_pixels(step_width, horizontal_scale))
    step_h = utils.meters_to_height(step_height, vertical_scale)
    base_h = utils.meters_to_height(base_height, vertical_scale)

    height = np.full((ny, nx), base_h, dtype=np.float32)

    if direction == "y":

        n_steps, offset_y, pitch = utils.compute_centered_tiling(
            ny, step_px, 0
        )

        for i in range(n_steps):
            y0 = offset_y + i * pitch
            y1 = y0 + step_px

            height[y0:y1, :] = base_h + i * step_h

    elif direction == "x":

        n_steps, offset_x, pitch = utils.compute_centered_tiling(
            nx, step_px, 0
        )

        for i in range(n_steps):
            x0 = offset_x + i * pitch
            x1 = x0 + step_px

            height[:, x0:x1] = base_h + i * step_h

    else:
        raise ValueError("direction must be 'x' or 'y'")

    return Terrain(
        height=height,
        horizontal_scale=horizontal_scale,
        vertical_scale=vertical_scale,
        metadata={
            "type": "stairs",
            "n_steps": int(n_steps),
            "direction": direction,
        },
    )