import numpy as np

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..terrain_cfg import TerrainCfg

def meters_to_pixels(length, scale):
    return int(np.round(length / scale))

def meters_to_height(height, vertical_scale):
    return height / vertical_scale

def compute_centered_tiling(
    total_size_px: int,
    cell_size_px: int,
    spacing_px: int = 0,
):
    """
    Returns:
        n: number of full elements
        start_offset: centered starting index
        pitch: cell_size + spacing
    """

    pitch = cell_size_px + spacing_px

    if pitch <= 0:
        raise ValueError("Invalid pitch")

    # max number of full tiles that fit
    n = max(0, (total_size_px + spacing_px) // pitch)

    used = n * pitch - spacing_px  # last one has no trailing gap
    leftover = total_size_px - used

    start_offset = leftover // 2

    return n, start_offset, pitch

def create_terrain_grid(cfg: "TerrainCfg"):
    nx = meters_to_pixels(cfg.width, cfg.horizontal_scale)+1
    ny = meters_to_pixels(cfg.length, cfg.horizontal_scale)+1
    base_h = meters_to_height(cfg.base_height, cfg.vertical_scale)

    base = np.full((ny, nx), base_h, dtype=np.float32)

    border_w = meters_to_pixels(cfg.border_width, cfg.horizontal_scale)
    border_h = meters_to_height(cfg.border_height, cfg.vertical_scale)

    if border_w <= 0.0:
        pass
    else:
        base[:border_w, :] = border_h
        base[-border_w:, :] = border_h
        base[:, :border_w] = border_h
        base[:, -border_w:] = border_h

    inner = base[
        border_w:ny-border_w,
        border_w:nx-border_w,
    ]

    return base, inner, nx, ny, base_h
