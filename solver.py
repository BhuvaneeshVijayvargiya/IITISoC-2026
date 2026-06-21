"""
Priority packages are placed first, then Economy packages. For each package,
ULDs are tried in order and the package is placed in the first ULD where a
valid position is found. Within a ULD, all 6 orientations of the package are
tried against a set of candidate positions (the corners of already-placed
packages), and the first valid (orientation, position) combination is used.
"""

import random


# ──────────────────────────────────────────────────────────────────────────
# GEOMETRY ENGINE
# ──────────────────────────────────────────────────────────────────────────

def overlaps(ax0, ay0, az0, ax1, ay1, az1, bx0, by0, bz0, bx1, by1, bz1) -> bool:
    return not (ax1 <= bx0 or bx1 <= ax0 or
                ay1 <= by0 or by1 <= ay0 or
                az1 <= bz0 or bz1 <= az0)


def is_valid(uld, pkg, x0, y0, z0, l, w, h) -> bool:
    x1, y1, z1 = x0 + l, y0 + w, z0 + h

    if x0 < 0 or y0 < 0 or z0 < 0:
        return False
    if x1 > uld.length or y1 > uld.width or z1 > uld.height:
        return False
    if uld.current_weight + pkg.weight > uld.weight_limit:
        return False

    for placed in uld.placed_packages:
        px0, py0, pz0 = placed.pos
        pl, pw, ph = placed.ori
        px1, py1, pz1 = px0 + pl, py0 + pw, pz0 + ph
        if overlaps(x0, y0, z0, x1, y1, z1, px0, py0, pz0, px1, py1, pz1):
            return False

    return True


def candidate_positions(uld) -> list[tuple]:
    xs, ys, zs = {0.0}, {0.0}, {0.0}
    for p in uld.placed_packages:
        x0, y0, z0 = p.pos
        l, w, h = p.ori
        xs.update([x0, x0 + l])
        ys.update([y0, y0 + w])
        zs.update([z0, z0 + h])
    return [(x, y, z) for x in sorted(xs) for y in sorted(ys) for z in sorted(zs)]


# ──────────────────────────────────────────────────────────────────────────
# FIRST FIT PLACEMENT
# ──────────────────────────────────────────────────────────────────────────

def first_fit_place(uld, pkg, rng: random.Random = None) -> bool:
    orientations = pkg.orientations()
    if rng:
        rng.shuffle(orientations)

    for l, w, h in orientations:
        for x0, y0, z0 in candidate_positions(uld):
            if is_valid(uld, pkg, x0, y0, z0, l, w, h):
                pkg.uld_id = uld.id
                pkg.pos = (x0, y0, z0)
                pkg.ori = (l, w, h)
                uld.placed_packages.append(pkg)
                uld.current_weight += pkg.weight
                return True
    return False


# ──────────────────────────────────────────────────────────────────────────
# SOLVER
# ──────────────────────────────────────────────────────────────────────────

def solve(packages, ulds, K: float, rng: random.Random = None, run_id: int = 0) -> dict:
    fresh_ulds = [
        type(u)(id=u.id, length=u.length, width=u.width, height=u.height, weight_limit=u.weight_limit)
        for u in ulds
    ]

    priority_pkgs = [p for p in packages if p.package_type == "Priority"]
    economy_pkgs = [p for p in packages if p.package_type == "Economy"]

    if rng:
        rng.shuffle(priority_pkgs)
        rng.shuffle(economy_pkgs)
        rng.shuffle(fresh_ulds)

    ordered_pkgs = priority_pkgs + economy_pkgs

    placed_packages = []
    unpacked = []

    for pkg in ordered_pkgs:
        packed = False
        for uld in fresh_ulds:
            if first_fit_place(uld, pkg, rng):
                placed_packages.append(pkg)
                packed = True
                break
        if not packed:
            unpacked.append(pkg)

    left_behind_cost = sum(p.delay_cost for p in unpacked if p.package_type == "Economy")
    priority_ulds = sum(1 for u in fresh_ulds if u.has_priority)
    total_cost = left_behind_cost + K * priority_ulds
    priority_failures = [p.id for p in unpacked if p.package_type == "Priority"]

    return {
        "run_id": run_id,
        "summary": {
            "total_cost": total_cost,
            "total_packed_packages": len(placed_packages),
            "number_of_priority_ulds": priority_ulds,
            "left_behind_economy_cost": left_behind_cost,
            "K": K,
            "is_feasible": len(priority_failures) == 0,
            "priority_failures": priority_failures,
        },
        "uld_stats": [
            {
                "uld_id": u.id,
                "packages_packed": len(u.placed_packages),
                "weight_used": u.current_weight,
                "weight_limit": u.weight_limit,
                "weight_utilization_pct": round(u.current_weight / u.weight_limit * 100, 2) if u.weight_limit else 0,
                "volume_utilization_pct": round(u.utilization() * 100, 2),
                "has_priority": u.has_priority,
            }
            for u in fresh_ulds
        ],
        "placements": [
            {
                "package_id": p.id,
                "package_type": p.package_type,
                "uld_id": p.uld_id,
                "x0": p.pos[0], "y0": p.pos[1], "z0": p.pos[2],
                "x1": p.pos[0] + p.ori[0], "y1": p.pos[1] + p.ori[1], "z1": p.pos[2] + p.ori[2],
                "orientation_used": list(p.ori),
            }
            for p in placed_packages
        ],
        "unpacked": [
            {
                "package_id": p.id,
                "package_type": p.package_type,
                "delay_cost": p.delay_cost,
            }
            for p in unpacked
        ],
    }
