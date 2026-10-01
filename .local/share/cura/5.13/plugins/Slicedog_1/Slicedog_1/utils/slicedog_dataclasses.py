from UM.Math.Vector import Vector

from dataclasses import dataclass, field, asdict
import numpy as np

# TODO used also for anchors...
@dataclass
class CurrentForce:
    id: str = ''
    faces: list[list[int]] = field(default_factory=lambda: [[]])
    center: Vector = field(default_factory=lambda: Vector(np.nan, np.nan, np.nan))
    direction: Vector = field(default_factory=lambda: Vector(np.nan, np.nan, np.nan))
    push: bool = field(default=True)
    magnitude: float = field(default=-1)
    unit: str = ''
    confirmed: bool = field(default=False)

    @property
    def facesFlat(self):
        return list({item for sublist in self.faces for item in sublist})

    def to_dict(self):
        return asdict(self)