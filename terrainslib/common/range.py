from dataclasses import dataclass


@dataclass(frozen=True)
class Range:
    min: float
    max: float
    
    def at(self, scale):
        return self.min + scale * (self.max - self.min)