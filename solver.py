from pct import PCT
from pct_store import add_round


def check_collision(x, y, z, l, w, h, placed):
    px, py, pz = placed.pos
    pl, pw, ph = placed.ori

    x_no_overlap = (x + l <= px) or (px + pl <= x)
    y_no_overlap = (y + w <= py) or (py + pw <= y)
    z_no_overlap = (z + h <= pz) or (pz + ph <= z)

    if x_no_overlap or y_no_overlap or z_no_overlap:
        return False

    return True
    

def generate_pct(package, ulds_list):
    possible_placements = []

    for uld in ulds_list:

        too_heavy = uld.current_weight + package.weight > uld.weight_limit
        if too_heavy:
            continue

        for ep in uld.extr:
            ax, ay, az, sx, sy, sz = ep

            for ori in package.orientations():
                l, w, h = ori
                x = ax if sx > 0 else ax - l
                y = ay if sy > 0 else ay - w
                z = az if sz > 0 else az - h

                out_of_bounds = (x < 0) or (y < 0) or (z < 0)
                sticks_out = (x + l > uld.length) or (y + w > uld.width) or (z + h > uld.height)
                if sticks_out or out_of_bounds:
                    continue

                has_collision = False
                for placed in uld.placed_packages:
                    if check_collision(x, y, z, l, w, h, placed):
                        has_collision = True
                        break

                if not has_collision:
                    node = PCT(package, uld, ep, ori)
                    possible_placements.append(node)

    return possible_placements


def score_node(node):
    score = 0

    already_has_priority = node.uld.has_priority
    this_is_priority = node.package.package_type == "Priority"

    if already_has_priority and this_is_priority:
        score += 150

    uld = node.uld
    target_x, target_y, target_z = uld.center()

    weighted_x = node.package.weight * node.cx
    weighted_y = node.package.weight * node.cy
    weighted_z = node.package.weight * node.cz
    total_weight = node.package.weight
 
    for placed in uld.placed_packages:
        px, py, pz = placed.pos
        pl, pw, ph = placed.ori
        pcx = px + pl / 2
        pcy = py + pw / 2
        pcz = pz + ph / 2
 
        weighted_x += placed.weight * pcx
        weighted_y += placed.weight * pcy
        weighted_z += placed.weight * pcz
        total_weight += placed.weight
 
    com_x = weighted_x / total_weight
    com_y = weighted_y / total_weight
    com_z = weighted_z / total_weight
 
    com_offset = abs(com_x - target_x) + abs(com_y - target_y) + abs(com_z - target_z)
    score -= 2 * com_offset

    box_offset = abs(node.cx - target_x) + abs(node.cy - target_y) + abs(node.cz - target_z)
    score -= 0.01 * box_offset

    return score


def place(package, node):
    uld = node.uld
    x, y, z = node.ep
    l, w, h = node.ori

    package.uld_id = uld.id
    package.pos = (x, y, z)
    package.ori = (l, w, h)
    sx, sy, sz = node.direction

    uld.placed_packages.append(package)
    uld.current_weight += package.weight

    far_x = x + l if sx > 0 else x
    far_y = y + w if sy > 0 else y
    far_z = z + h if sz > 0 else z
 
    near_x = x if sx > 0 else x + l
    near_y = y if sy > 0 else y + w
    near_z = z if sz > 0 else z + h
 
    new_point_1 = (far_x, near_y, near_z, sx, sy, sz)
    new_point_2 = (near_x, far_y, near_z, sx, sy, sz)
    new_point_3 = (near_x, near_y, far_z, sx, sy, sz)

    for pt in [new_point_1, new_point_2, new_point_3]:
        if pt not in uld.extr:
            uld.extr.append(pt)


def solve(packages, ulds, K):
    priority_pkgs = []
    economy_pkgs = []

    for p in packages:
        if p.package_type == "Priority":
            priority_pkgs.append(p)
        else:
            economy_pkgs.append(p)

    ordered = priority_pkgs + economy_pkgs
    unpacked = []
    pct_log = []

    for round_number, package in enumerate(ordered, start=1):
        possible_placements = generate_pct(package, ulds)

        if len(possible_placements) == 0:
            unpacked.append(package)
            add_round(pct_log ,[], None, round_number)
            continue

        for node in possible_placements:
            node.score = score_node(node)

        best = possible_placements[0]
        for node in possible_placements:
            if node.score > best.score:
                best = node

        add_round(pct_log, possible_placements, best, round_number)
        place(package, best)

    left_behind_cost = 0
    for p in unpacked:
        if p.package_type == "Economy":
            left_behind_cost += p.delay_cost

    priority_ulds = 0
    for u in ulds:
        if u.has_priority:
            priority_ulds += 1

    total_cost = left_behind_cost + K * priority_ulds

    priority_failures = []
    for p in unpacked:
        if p.package_type == "Priority":
            priority_failures.append(p.id)

    placements = []
    for p in ordered:
        if p.uld_id is not None:
            placements.append({
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
            })

    unpacked_list = []
    for p in unpacked:
        unpacked_list.append({
            "package_id": p.id,
            "package_type": p.package_type,
            "delay_cost": p.delay_cost,
        })

    uld_stats = []
    for u in ulds:
        uld_stats.append({
            "uld_id": u.id,
            "packages_packed": len(u.placed_packages),
            "weight_used": u.current_weight,
            "weight_limit": u.weight_limit,
            "has_priority": u.has_priority,
        })

    result = {
        "summary": {
            "total_cost": total_cost,
            "total_packed_packages": len(ordered) - len(unpacked),
            "number_of_priority_ulds": priority_ulds,
            "left_behind_economy_cost": left_behind_cost,
            "K": K,
            "is_feasible": len(priority_failures) == 0,
            "priority_failures": priority_failures,
        },
        "placements": placements,
        "unpacked": unpacked_list,
        "uld_stats": uld_stats,
    }

    return result, pct_log
