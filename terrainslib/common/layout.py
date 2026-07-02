from dataclasses import dataclass


@dataclass(frozen=True)
class Layout:
    """
    Describes a centered tiling layout in grid space.
    """

    n_x: int
    n_y: int

    offset_x: int
    offset_y: int

    pitch_x: int
    pitch_y: int


def build_centered_layout(
    total_x: int,
    total_y: int,
    cell_x: int,
    cell_y: int,
    spacing_x: int = 0,
    spacing_y: int = 0,
) -> Layout:

    pitch_x = cell_x + spacing_x
    pitch_y = cell_y + spacing_y

    if pitch_x <= 0 or pitch_y <= 0:
        raise ValueError("Invalid pitch")

    n_x = max(0, (total_x + spacing_x) // pitch_x)
    n_y = max(0, (total_y + spacing_y) // pitch_y)

    used_x = n_x * pitch_x - spacing_x
    used_y = n_y * pitch_y - spacing_y

    offset_x = (total_x - used_x) // 2
    offset_y = (total_y - used_y) // 2

    return Layout(
        n_x=n_x,
        n_y=n_y,
        offset_x=offset_x,
        offset_y=offset_y,
        pitch_x=pitch_x,
        pitch_y=pitch_y,
    )