#in this we defined packages class
import itertools
from dataclasses import dataclass, field

@dataclass
class Package:
    id: str
    length: float
    width: float
    height: float
    weight: float
    package_type: str          
    delay_cost: float = 0.0    

    uld_id: str = None
    pos: tuple = None          
    ori: tuple = None          

    def volume(self) -> float:
        return self.length * self.width * self.height

    def orientations(self) -> list[tuple]:
        seen, result = set(), []
        for perm in itertools.permutations([self.length, self.width, self.height]):
            if perm not in seen:
                seen.add(perm)
                result.append(perm)
        return result

    def __str__(self):
        return f"{self.id}:({self.length},{self.width},{self.height})"
