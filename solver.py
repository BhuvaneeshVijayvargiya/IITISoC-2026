"""
Priority packages are placed first, then Economy packages. For each package,
ULDs are tried in order and the package is placed in the first ULD where a
valid position is found. Within a ULD, all 6 orientations of the package are
tried against the set of the corners of already-placed packages, and the first
valid (orientation, position) combination is used.
"""

import random


def overlaps(ax0, ay0, az0, ax1, ay1, az1, bx0, by0, bz0, bx1, by1, bz1):
    if ax1 <= bx0:
        return False
    if bx1 <= ax0:
        return False
    if ay1 <= by0:
        return False
    if by1 <= ay0:
        return False
    if az1 <= bz0:
        return False
    if bz1 <= az0:
        return False
    return True


def is_valid(uld, pkg, x0, y0, z0, l, w, h):
    x1 = x0 + l
    y1 = y0 + w
    z1 = z0 + h

    if x0 < 0:
        return False
    if y0 < 0:
        return False
    if z0 < 0:
        return False
    if x1 > uld.length:
        return False
    if y1 > uld.width:
        return False
    if z1 > uld.height:
        return False
    if uld.current_weight + pkg.weight > uld.weight_limit:
        return False

    for placed in uld.placed_packages:
        px0 = placed.pos[0]
        py0 = placed.pos[1]
        pz0 = placed.pos[2]
        pl = placed.ori[0]
        pw = placed.ori[1]
        ph = placed.ori[2]
        px1 = px0 + pl
        py1 = py0 + pw
        pz1 = pz0 + ph
        if overlaps(x0, y0, z0, x1, y1, z1, px0, py0, pz0, px1, py1, pz1):
            return False

    return True


def candidate_positions(uld):
    xs = [0.0]
    ys = [0.0]
    zs = [0.0]

    for p in uld.placed_packages:
        x0 = p.pos[0]
        y0 = p.pos[1]
        z0 = p.pos[2]
        l = p.ori[0]
        w = p.ori[1]
        h = p.ori[2]

        if x0 not in xs:
            xs.append(x0)
        if x0 + l not in xs:
            xs.append(x0 + l)

        if y0 not in ys:
            ys.append(y0)
        if y0 + w not in ys:
            ys.append(y0 + w)

        if z0 not in zs:
            zs.append(z0)
        if z0 + h not in zs:
            zs.append(z0 + h)

    xs.sort()
    ys.sort()
    zs.sort()

    positions = []
    for x in xs:
        for y in ys:
            for z in zs:
                positions.append((x, y, z))

    return positions


def first_fit_place(uld, pkg, rng=None):
    orientations = pkg.orientations()

    if rng:
        rng.shuffle(orientations)

    for orientation in orientations:
        l = orientation[0]
        w = orientation[1]
        h = orientation[2]

        for position in candidate_positions(uld):
            x0 = position[0]
            y0 = position[1]
            z0 = position[2]

            if is_valid(uld, pkg, x0, y0, z0, l, w, h):
                pkg.uld_id = uld.id
                pkg.pos = (x0, y0, z0)
                pkg.ori = (l, w, h)
                uld.placed_packages.append(pkg)
                uld.current_weight = uld.current_weight + pkg.weight
                return True

    return False


def solve(packages, ulds, K, rng=None, run_id=0):
    fresh_ulds = []
    for u in ulds:
        new_uld = type(u)(id=u.id, length=u.length, width=u.width, height=u.height, weight_limit=u.weight_limit)
        fresh_ulds.append(new_uld)

    priority_pkgs = []
    economy_pkgs = []

    for p in packages:
        if p.package_type == "Priority":
            priority_pkgs.append(p)
        else:
            economy_pkgs.append(p)

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

    left_behind_cost = 0
    for p in unpacked:
        if p.package_type == "Economy":
            left_behind_cost = left_behind_cost + p.delay_cost

    priority_ulds = 0
    for u in fresh_ulds:
        if u.has_priority:
            priority_ulds = priority_ulds + 1

    total_cost = left_behind_cost + K * priority_ulds

    priority_failures = []
    for p in unpacked:
        if p.package_type == "Priority":
            priority_failures.append(p.id)

    uld_stats = []
    for u in fresh_ulds:
        if u.weight_limit != 0:
            weight_utilization_pct = round(u.current_weight / u.weight_limit * 100, 2)
        else:
            weight_utilization_pct = 0

        uld_info = {
            "uld_id": u.id,
            "packages_packed": len(u.placed_packages),
            "weight_used": u.current_weight,
            "weight_limit": u.weight_limit,
            "weight_utilization_pct": weight_utilization_pct,
            "volume_utilization_pct": round(u.utilization() * 100, 2),
            "has_priority": u.has_priority,
        }
        uld_stats.append(uld_info)

    placements = []
    for p in placed_packages:
        placement_info = {
            "package_id": p.id,
            "package_type": p.package_type,
            "uld_id": p.uld_id,
            "x0": p.pos[0],
            "y0": p.pos[1],
            "z0": p.pos[2],
            "x1": p.pos[0] + p.ori[0],
            "y1": p.pos[1] + p.ori[1],
            "z1": p.pos[2] + p.ori[2],
            "orientation_used": list(p.ori),
        }
        placements.append(placement_info)

    unpacked_list = []
    for p in unpacked:
        unpacked_info = {
            "package_id": p.id,
            "package_type": p.package_type,
            "delay_cost": p.delay_cost,
        }
        unpacked_list.append(unpacked_info)

    result = {
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
        "uld_stats": uld_stats,
        "placements": placements,
        "unpacked": unpacked_list,
    }

    return result
        
    
