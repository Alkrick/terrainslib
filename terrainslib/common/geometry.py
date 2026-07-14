from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field

@dataclass
class Geometry:
    
    vertices: np.ndarray
    faces: np.ndarray
    
    edges: np.ndarray | None
    
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
            edges=None,
            metadata=metadata,
        )
    
    @classmethod
    def _merge_vertices(cls, mesh: Geometry, tolerance=1e-5):
    
        vertices = mesh.vertices
        faces = mesh.faces

        rounded = np.round(
            vertices / tolerance
        ).astype(np.int64)

        _, unique_indices, inverse = np.unique(
            rounded,
            axis=0,
            return_index=True,
            return_inverse=True,
        )

        vertices_new = vertices[unique_indices]

        faces_new = inverse[faces]

        return cls(
            vertices=vertices_new,
            faces=faces_new,
            edges=None,
            metadata=mesh.metadata,
        )
