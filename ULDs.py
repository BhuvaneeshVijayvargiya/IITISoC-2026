from dataclasses import dataclass, field

@dataclass
class ULD:
    id: str
    length: float     
    width: float       
    height: float      
    weight_limit: float

    current_weight: float = 0.0
    placed_packages: list = field(default_factory=list)   
    extr: list = field(default_factory=lambda: [(0, 0, 0)])

    @property
    def has_priority(self) -> bool:
        return any(p.package_type == "Priority" for p in self.placed_packages)

    def volume(self) -> float:
        return self.length * self.width * self.height

    def used_volume(self) -> float:
        total = 0.0
        for p in self.placed_packages:
            x0, y0, z0 = p.pos
            l, w, h = p.ori
            total += l * w * h
        return total

    def utilization(self) -> float:
        total = self.volume()
        return self.used_volume() / total if total > 0 else 0.0
