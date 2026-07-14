from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field

@dataclass
class Geometry:
    
    vertices: np.ndarray
    faces: np.ndarray
    
    metadata: dict = field(default_factory=dict)
    
    @classmethod
    def merge(
        cls,
        *geometries: Geometry,
    ) -> Geometry:

        vertices = []
        faces = []

        vertex_offset = 0

        metadata = {}


        for geometry in geometries:

            if geometry is None:
                continue

            v = geometry.vertices
            f = geometry.faces


            vertices.append(v)

            # shift face indices
            faces.append(
                f + vertex_offset
            )


            vertex_offset += len(v)


            metadata.update(
                geometry.metadata
            )


        return cls(
            vertices=np.concatenate(vertices, axis=0),
            faces=np.concatenate(faces, axis=0),
            metadata=metadata,
        )
