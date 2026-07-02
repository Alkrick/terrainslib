import numpy as np

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