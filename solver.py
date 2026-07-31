#solver to arrange in such a way which minimizes penalty cost in a physically possible way.

import copy
from pct import PCT
from pct_store import add_round
from stability import calculate_overlap_area
from feature import compute_cog_deviation
import torch
from feature import extracter
from model import AI

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
                supported_area=0

                if not has_collision:
                    is_stable = False


                    if z == 0:
                        is_stable = True
                    else:
                        supported_area = 0
                        for placed in uld.placed_packages:
                            px, py, pz = placed.pos
                            pl, pw, ph = placed.ori

                            if pz + ph == z:
                                supported_area += calculate_overlap_area(x, y, l, w, px, py, pl, pw)

                        if supported_area >= (l * w) * 0.5:
                            is_stable = True

                    if is_stable:
                        node = PCT(package, uld, ep, ori,supported_area)
                        possible_placements.append(node)

    return possible_placements

def score_node(node):
    uld=node.uld
    pkg=node.package
    score=0.0
    if uld.has_priority and pkg.package_type=="Priority":
        score+=1000
    elif pkg.package_type=="Priority":
        score+=250
    cog=compute_cog_deviation(node)
    score-=45*cog
    vol= uld.used_volume()+(node.l * node.w * node.h)
    util=vol/uld.volume() if uld.volume()>0 else 0.0
    score+=100*util
    score+=pkg.delay_cost if pkg.package_type=="Economy" else 10
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


def build_result(ordered, unpacked, ulds, K):
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

    return result


def solve(packages, ulds, K,model):
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
            add_round(pct_log, [], None, round_number)
            continue

        features = []
        for node in possible_placements:
            features.append(extracter(node, node.support))
        candidates = torch.tensor(features, dtype=torch.float32)

        best_idx = model.rank(candidates)
        best = possible_placements[best_idx]

        add_round(pct_log, possible_placements, best, round_number)
        place(package, best)


    result = build_result(ordered, unpacked, ulds, K)

    return result, pct_log


def copy_branch(branch):
    new_branch = {}
    new_branch["ulds"] = copy.deepcopy(branch["ulds"])
    new_branch["packages"] = copy.deepcopy(branch["packages"])
    new_branch["unpacked"] = copy.deepcopy(branch["unpacked"])
    new_branch["total_score"] = branch["total_score"]
    new_branch["pct_log"] = copy.deepcopy(branch["pct_log"])
    return new_branch


def find_uld_by_id(ulds, uld_id):
    for u in ulds:
        if u.id == uld_id:
            return u
    return None


LOOKAHEAD_WEIGHT = 0.5  # for one step ahead in beam search


def score_with_model(possible_placements, model): 
    features = []
    for node in possible_placements:
        features.append(extracter(node, node.support))
    candidates = torch.tensor(features, dtype=torch.float32)

    with torch.no_grad():
        scores = model(candidates)

    for node, s in zip(possible_placements, scores):
        node.score = float(s)


def lookahead_score(branch, node, round_number, model):
    
    if round_number >= len(branch["packages"]):
        return 0.0  

    sim_ulds = copy.deepcopy(branch["ulds"])
    sim_uld = find_uld_by_id(sim_ulds, node.uld.id)
    sim_package = copy.deepcopy(node.package)

    child_node = PCT(sim_package, sim_uld, node.ep, node.ori, node.support)
    place(sim_package, child_node)

    next_package = branch["packages"][round_number]
    child_candidates = generate_pct(next_package, sim_ulds)
    if len(child_candidates) == 0:
        return 0.0

    features = [extracter(c, c.support) for c in child_candidates]
    candidates = torch.tensor(features, dtype=torch.float32)

    best_idx = model.rank(candidates)
    with torch.no_grad():
        child_scores = model(candidates)

    return float(child_scores[best_idx])


def solve_beam(packages, ulds, K, model, beam_width=3):
    print(type(beam_width), beam_width)
    priority_pkgs = []
    economy_pkgs = []

    for p in packages:
        if p.package_type == "Priority":
            priority_pkgs.append(p)
        else:
            economy_pkgs.append(p)

    ordered = priority_pkgs + economy_pkgs

    first_branch = {}
    first_branch["ulds"] = copy.deepcopy(ulds)
    first_branch["packages"] = copy.deepcopy(ordered)
    first_branch["unpacked"] = []
    first_branch["total_score"] = 0
    first_branch["pct_log"] = []

    branches = [first_branch]

    for round_number, package in enumerate(ordered, start=1):
        print(f"Round {round_number}, branches={len(branches)}")
        all_candidates = []

        for branch in branches:
            branch_package = branch["packages"][round_number - 1]
            possible_placements = generate_pct(branch_package, branch["ulds"])

            if len(possible_placements) == 0:
                new_branch = copy_branch(branch)
                new_branch["unpacked"].append(new_branch["packages"][round_number - 1])
                add_round(new_branch["pct_log"], [], None, round_number)
                all_candidates.append(new_branch)
                continue

            score_with_model(possible_placements, model)

            print("beam_width =", beam_width, type(beam_width))
            print("possible_placements =", type(possible_placements), len(possible_placements))

            possible_placements.sort(key=lambda n: n.score, reverse=True)

            print("About to slice...")

            shortlist = possible_placements[: int(beam_width) * 2]

            print("Shortlist length =", len(shortlist))

            for node in shortlist:
                node.score += LOOKAHEAD_WEIGHT * lookahead_score(branch, node, round_number, model)

            shortlist.sort(key=lambda n: n.score, reverse=True)
            top_nodes = shortlist[:beam_width]

            for node in top_nodes:
                new_branch = copy_branch(branch)
                new_package = new_branch["packages"][round_number - 1]
                new_uld = find_uld_by_id(new_branch["ulds"], node.uld.id)

                new_node = PCT(new_package, new_uld, node.ep, node.ori, node.support)
                new_node.score = node.score
                place(new_package, new_node)

                new_branch["total_score"] = new_branch["total_score"] + node.score
                add_round(new_branch["pct_log"], possible_placements, node, round_number)

                all_candidates.append(new_branch)

        all_candidates.sort(key=lambda b: b["total_score"], reverse=True)
        branches = all_candidates[:beam_width]

    final_results = []
    for branch in branches:
        result = build_result(branch["packages"], branch["unpacked"], branch["ulds"], K)
        final_results.append({
            "result": result,
            "pct_log": branch["pct_log"],
            "total_score": branch["total_score"],
            "ulds": branch["ulds"],
            "packages": branch["packages"],
        })

    best_branch = final_results[0]
    for f in final_results:
        if f["result"]["summary"]["total_cost"] < best_branch["result"]["summary"]["total_cost"]:
            best_branch = f

    return final_results, best_branch
