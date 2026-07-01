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
            x, y, z = ep

            for ori in package.orientations():
                l, w, h = ori

                sticks_out = (x + l > uld.length) or (y + w > uld.width) or (z + h > uld.height)
                if sticks_out:
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
        score += 100

    distance_from_origin = node.x + node.y + node.z
    score -= distance_from_origin

    return score


def place(package, node):
    uld = node.uld
    x, y, z = node.ep
    l, w, h = node.ori

    package.uld_id = uld.id
    package.pos = (x, y, z)
    package.ori = (l, w, h)

    uld.placed_packages.append(package)
    uld.current_weight += package.weight

    new_point_1 = (x + l, y, z)
    new_point_2 = (x, y + w, z)
    new_point_3 = (x, y, z + h)

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
