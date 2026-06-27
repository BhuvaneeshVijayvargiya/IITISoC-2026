from packages import Package
from ULDs import ULD
 
def load(filepath: str) -> tuple[list[Package], list[ULD], float]:
  
    with open(filepath) as f:
        lines = [line.strip() for line in f.readlines()]
 
    K = float(lines[0])
 
    sections = []
    current = []
    for line in lines[1:]:
        if line == "":
            if current:
                sections.append(current)
                current = []
        else:
            current.append(line)
    if current:
        sections.append(current)
 
    uld_lines     = sections[0]
    package_lines = sections[1]
 
    ulds = []
    for line in uld_lines:
        parts = line.split(",")
        ulds.append(ULD(
            id           = parts[0].strip(),
            length       = float(parts[1]),
            width        = float(parts[2]),
            height       = float(parts[3]),
            weight_limit = float(parts[4]),
        ))
 
    packages = []
    for line in package_lines:
        parts = line.split(",")
        delay = 0.0 if parts[6].strip() == "-" else float(parts[6].strip())
        packages.append(Package(
            id           = parts[0].strip(),
            length       = float(parts[1]),
            width        = float(parts[2]),
            height       = float(parts[3]),
            weight       = float(parts[4]),
            package_type = parts[5].strip(),
            delay_cost   = delay,
        ))
 
    return packages, ulds, K
