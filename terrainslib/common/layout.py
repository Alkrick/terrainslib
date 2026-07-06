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

    stride_x: int
    stride_y: int
    
    def __iter__(self):
        for iy in range(self.n_y):
            y = self.offset_y + iy * self.stride_y
            for ix in range(self.n_x):
                x = self.offset_x + ix * self.stride_x
                
                yield x,y
            


def build_centered_layout(
    total_x: int,
    total_y: int,
    feature_x: int,
    feature_y: int,
    spacing_x: int = 0,
    spacing_y: int = 0,
) -> Layout:

    stride_x = feature_x + spacing_x
    stride_y = feature_y + spacing_y

    if stride_x <= 0 or stride_y <= 0:
        raise ValueError("Invalid cell")

    n_x = max(0, (total_x + spacing_x) // stride_x)
    n_y = max(0, (total_y + spacing_y) // stride_y)

    used_x = n_x * stride_x - spacing_x
    used_y = n_y * stride_y - spacing_y

    offset_x = (total_x - used_x) // 2
    offset_y = (total_y - used_y) // 2

    return Layout(
        n_x=n_x,
        n_y=n_y,
        offset_x=offset_x,
        offset_y=offset_y,
        stride_x=stride_x,
        stride_y=stride_y,
    )