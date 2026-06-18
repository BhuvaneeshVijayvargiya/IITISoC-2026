"""
First Fit 3D Bin Packing Solver
IITISoC - Intelligent Cargo Packing & Spatial Neuro-Optimization

Usage:
  python first_fit_solver.py input.json [--runs N] [--seed S]
  python first_fit_solver.py ulds.csv packages.csv K [--runs N] [--seed S]

  --runs N   Generate N randomized solutions (default: 1)
  --seed S   Random seed for reproducibility

Input JSON format:
  {
    "K": 40,
    "ulds": [{"id": "ULD-1", "length": 100, "width": 80, "height": 80, "weight_limit": 250}, ...],
    "packages": [{"id": "P-1", "length": 70, "width": 40, "height": 50, "weight": 100, "type": "Priority", "delay_cost": 0}, ...]
  }

Input CSV format:
  ulds.csv   → columns: id, length, width, height, weight_limit
  packages.csv → columns: id, length, width, height, weight, type, delay_cost

Output (written to ./output/):
  solution.txt       — exact evaluator format (Line 1: cost/packed/priority-ULDs, then placements)
  solution_full.json — rich structured JSON for the AI team
  placements.csv     — flat CSV for AI feature extraction
"""

import json
import csv
import itertools
import sys
import os
import random
import copy
from dataclasses import dataclass, field
from typing import Optional


# ──────────────────────────────────────────────────────────────────────────────
# DATA MODELS
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ULD:
    id: str
    length: float   # X axis
    width: float    # Y axis
    height: float   # Z axis
    weight_limit: float
    current_weight: float = 0.0
    placed_packages: list = field(default_factory=list)

    @property
    def has_priority(self) -> bool:
        return any(p.package_type == "Priority" for p in self.placed_packages)

    def utilization(self) -> float:
        total = self.length * self.width * self.height
        used = sum((p.x1-p.x0)*(p.y1-p.y0)*(p.z1-p.z0) for p in self.placed_packages)
        return used / total if total > 0 else 0.0


@dataclass
class Package:
    id: str
    length: float
    width: float
    height: float
    weight: float
    package_type: str   # "Priority" or "Economy"
    delay_cost: float = 0.0


@dataclass
class PlacedPackage:
    package_id: str
    package_type: str
    uld_id: str
    x0: float; y0: float; z0: float
    x1: float; y1: float; z1: float
    orientation: tuple


@dataclass
class UnpackedPackage:
    package_id: str
    package_type: str
    delay_cost: float


# ──────────────────────────────────────────────────────────────────────────────
# GEOMETRY ENGINE
# ──────────────────────────────────────────────────────────────────────────────

def get_orientations(l, w, h, rng: random.Random = None) -> list[tuple]:
    """All unique axis-aligned orientations of a cuboid, optionally shuffled."""
    seen, result = set(), []
    for perm in itertools.permutations([l, w, h]):
        if perm not in seen:
            seen.add(perm)
            result.append(perm)
    if rng:
        rng.shuffle(result)
    return result


def overlaps(ax0,ay0,az0,ax1,ay1,az1, bx0,by0,bz0,bx1,by1,bz1) -> bool:
    return not (ax1<=bx0 or bx1<=ax0 or ay1<=by0 or by1<=ay0 or az1<=bz0 or bz1<=az0)


def is_valid(uld: ULD, pkg: Package, x0, y0, z0, l, w, h) -> bool:
    x1, y1, z1 = x0+l, y0+w, z0+h
    if x0<0 or y0<0 or z0<0: return False
    if x1>uld.length or y1>uld.width or z1>uld.height: return False
    if uld.current_weight + pkg.weight > uld.weight_limit: return False
    for p in uld.placed_packages:
        if overlaps(x0,y0,z0,x1,y1,z1, p.x0,p.y0,p.z0, p.x1,p.y1,p.z1):
            return False
    return True


def candidate_positions(uld: ULD) -> list[tuple]:
    """Extreme-point candidates: origin + all corners of placed packages."""
    xs, ys, zs = {0.0}, {0.0}, {0.0}
    for p in uld.placed_packages:
        xs.update([p.x0, p.x1]); ys.update([p.y0, p.y1]); zs.update([p.z0, p.z1])
    return [(x,y,z) for x in sorted(xs) for y in sorted(ys) for z in sorted(zs)]


# ──────────────────────────────────────────────────────────────────────────────
# FIRST FIT PLACEMENT
# ──────────────────────────────────────────────────────────────────────────────

def first_fit_place(uld: ULD, pkg: Package, rng: random.Random = None) -> Optional[PlacedPackage]:
    """Try all orientations × candidate positions; return first valid placement."""
    for orientation in get_orientations(pkg.length, pkg.width, pkg.height, rng):
        l, w, h = orientation
        for x0, y0, z0 in candidate_positions(uld):
            if is_valid(uld, pkg, x0, y0, z0, l, w, h):
                placed = PlacedPackage(
                    package_id=pkg.id, package_type=pkg.package_type, uld_id=uld.id,
                    x0=x0, y0=y0, z0=z0, x1=x0+l, y1=y0+w, z1=z0+h,
                    orientation=orientation
                )
                uld.placed_packages.append(placed)
                uld.current_weight += pkg.weight
                return placed
    return None


# ──────────────────────────────────────────────────────────────────────────────
# SOLVER
# ──────────────────────────────────────────────────────────────────────────────

def solve(ulds: list[ULD], packages: list[Package], K: float,
          rng: random.Random = None, run_id: int = 0) -> dict:
    """
    First Fit solver: Priority packages first, then Economy.
    If rng is provided, shuffles Economy package order and ULD order for diversity.
    Priority packages are always packed first (hard constraint) but their
    internal order is also shuffled when rng is provided.
    """
    # Fresh copies of ULD state so each run is independent
    fresh_ulds = [ULD(id=u.id, length=u.length, width=u.width,
                      height=u.height, weight_limit=u.weight_limit)
                  for u in ulds]

    priority_pkgs = [p for p in packages if p.package_type == "Priority"]
    economy_pkgs  = [p for p in packages if p.package_type == "Economy"]

    if rng:
        rng.shuffle(priority_pkgs)   # shuffle within priority group
        rng.shuffle(economy_pkgs)    # shuffle economy order
        rng.shuffle(fresh_ulds)      # shuffle which ULD is tried first

    ordered_pkgs = priority_pkgs + economy_pkgs
    placed, unpacked = [], []

    for pkg in ordered_pkgs:
        packed = False
        for uld in fresh_ulds:
            result = first_fit_place(uld, pkg, rng)
            if result:
                placed.append(result)
                packed = True
                break
        if not packed:
            unpacked.append(UnpackedPackage(
                package_id=pkg.id,
                package_type=pkg.package_type,
                delay_cost=pkg.delay_cost
            ))

    left_behind_cost = sum(u.delay_cost for u in unpacked if u.package_type == "Economy")
    priority_ulds    = sum(1 for u in fresh_ulds if u.has_priority)
    total_cost       = left_behind_cost + K * priority_ulds
    priority_failures = [u.package_id for u in unpacked if u.package_type == "Priority"]

    return {
        "run_id": run_id,
        "summary": {
            "total_cost": total_cost,
            "total_packed_packages": len(placed),
            "number_of_priority_ulds": priority_ulds,
            "left_behind_economy_cost": left_behind_cost,
            "K": K,
            "is_feasible": len(priority_failures) == 0,
            "priority_failures": priority_failures,
        },
        "uld_stats": [{
            "uld_id": u.id,
            "packages_packed": len(u.placed_packages),
            "weight_used": u.current_weight,
            "weight_limit": u.weight_limit,
            "weight_utilization_pct": round(u.current_weight / u.weight_limit * 100, 2),
            "volume_utilization_pct": round(u.utilization() * 100, 2),
            "has_priority": u.has_priority,
        } for u in fresh_ulds],
        "placements": [{
            "package_id": p.package_id, "package_type": p.package_type, "uld_id": p.uld_id,
            "x0": p.x0, "y0": p.y0, "z0": p.z0,
            "x1": p.x1, "y1": p.y1, "z1": p.z1,
            "orientation_used": list(p.orientation),
        } for p in placed],
        "unpacked": [{
            "package_id": u.package_id, "package_type": u.package_type, "delay_cost": u.delay_cost,
        } for u in unpacked],
    }


# ──────────────────────────────────────────────────────────────────────────────
# OUTPUT WRITERS
# ──────────────────────────────────────────────────────────────────────────────

def write_official_output(result: dict, filepath: str):
    """Exact evaluator format as per problem spec."""
    s = result["summary"]
    lines = [f"{s['total_cost']}, {s['total_packed_packages']}, {s['number_of_priority_ulds']}"]
    for p in result["placements"]:
        lines.append(f"{p['package_id']}, {p['uld_id']}, "
                     f"{int(p['x0'])}, {int(p['y0'])}, {int(p['z0'])}, "
                     f"{int(p['x1'])}, {int(p['y1'])}, {int(p['z1'])}")
    for u in result["unpacked"]:
        lines.append(f"{u['package_id']}, NONE, -1, -1, -1, -1, -1, -1")
    with open(filepath, "w") as f:
        f.write("\n".join(lines) + "\n")


def write_json_output(result: dict, filepath: str):
    with open(filepath, "w") as f:
        json.dump(result, f, indent=2)


def write_csv_placements(result: dict, filepath: str, mode: str = "w", write_header: bool = True):
    """Flat CSV for AI feature extraction. Supports append mode for multi-run."""
    fields = ["run_id","package_id","package_type","uld_id","x0","y0","z0","x1","y1","z1",
              "vol_l","vol_w","vol_h","volume","orientation_used"]
    with open(filepath, mode, newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if write_header:
            w.writeheader()
        for p in result["placements"]:
            l, w2, h = p["x1"]-p["x0"], p["y1"]-p["y0"], p["z1"]-p["z0"]
            w.writerow({"run_id": result["run_id"], **p,
                        "vol_l":l, "vol_w":w2, "vol_h":h, "volume":l*w2*h,
                        "orientation_used": str(p["orientation_used"])})


def print_summary(result: dict):
    s = result["summary"]
    run_tag = f" (run {result['run_id']})" if result.get("run_id", 0) > 0 else ""
    print(f"\n{'═'*55}")
    print(f"  FIRST FIT SOLVER — RESULTS{run_tag}")
    print(f"{'═'*55}")
    print(f"  Feasible : {'✅ YES' if s['is_feasible'] else '❌ NO — Priority packages left behind!'}")
    print(f"  Total Cost          : {s['total_cost']}")
    print(f"  Packed Packages     : {s['total_packed_packages']}")
    print(f"  Priority ULDs × K   : {s['number_of_priority_ulds']} × {s['K']} = {s['number_of_priority_ulds']*s['K']}")
    print(f"  Economy Left-Behind : {s['left_behind_economy_cost']}")
    if s["priority_failures"]:
        print(f"  ⚠ Priority Failures: {', '.join(s['priority_failures'])}")
    print()
    for u in result["uld_stats"]:
        tag = " [PRIORITY]" if u["has_priority"] else ""
        print(f"  {u['uld_id']}{tag}: {u['packages_packed']} pkgs | "
              f"{u['weight_used']}/{u['weight_limit']} kg ({u['weight_utilization_pct']}%) | "
              f"Vol {u['volume_utilization_pct']}%")
    print()
    for p in result["placements"]:
        print(f"  {p['package_id']} → {p['uld_id']}  "
              f"({p['x0']},{p['y0']},{p['z0']}) → ({p['x1']},{p['y1']},{p['z1']})")
    if result["unpacked"]:
        print()
        for u in result["unpacked"]:
            tag = f"delay_cost={u['delay_cost']}" if u["package_type"]=="Economy" else "PRIORITY VIOLATION"
            print(f"  {u['package_id']} → NONE  [{tag}]")
    print("═"*55 + "\n")


# ──────────────────────────────────────────────────────────────────────────────
# INPUT PARSERS
# ──────────────────────────────────────────────────────────────────────────────

def parse_json(filepath: str) -> tuple[list[ULD], list[Package], float]:
    with open(filepath) as f:
        data = json.load(f)
    ulds = [ULD(id=u["id"], length=u["length"], width=u["width"],
                height=u["height"], weight_limit=u["weight_limit"])
            for u in data["ulds"]]
    packages = [Package(id=p["id"], length=p["length"], width=p["width"],
                        height=p["height"], weight=p["weight"],
                        package_type=p["type"], delay_cost=p.get("delay_cost", 0.0))
                for p in data["packages"]]
    return ulds, packages, float(data.get("K", 0))


def parse_csv(ulds_file: str, pkgs_file: str, K: float) -> tuple[list[ULD], list[Package], float]:
    ulds = []
    with open(ulds_file, newline="") as f:
        for row in csv.DictReader(f):
            ulds.append(ULD(id=row["id"].strip(), length=float(row["length"]),
                            width=float(row["width"]), height=float(row["height"]),
                            weight_limit=float(row["weight_limit"])))
    packages = []
    with open(pkgs_file, newline="") as f:
        for row in csv.DictReader(f):
            packages.append(Package(id=row["id"].strip(), length=float(row["length"]),
                                    width=float(row["width"]), height=float(row["height"]),
                                    weight=float(row["weight"]), package_type=row["type"].strip(),
                                    delay_cost=float(row["delay_cost"]) if row.get("delay_cost","").strip() else 0.0))
    return ulds, packages, K


# ──────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]

    # Parse --runs and --seed flags
    num_runs = 1
    seed = None
    clean_args = []
    i = 0
    while i < len(args):
        if args[i] == "--runs" and i+1 < len(args):
            num_runs = int(args[i+1]); i += 2
        elif args[i] == "--seed" and i+1 < len(args):
            seed = int(args[i+1]); i += 2
        else:
            clean_args.append(args[i]); i += 1

    # Load input
    if len(clean_args) == 1 and clean_args[0].endswith(".json"):
        ulds, packages, K = parse_json(clean_args[0])
        print(f"[INFO] Loaded from JSON: {clean_args[0]}")
    elif len(clean_args) == 3:
        ulds, packages, K = parse_csv(clean_args[0], clean_args[1], float(clean_args[2]))
        print(f"[INFO] Loaded CSVs: {clean_args[0]}, {clean_args[1]}  K={clean_args[2]}")
    else:
        print("Usage:")
        print("  python first_fit_solver.py input.json [--runs N] [--seed S]")
        print("  python first_fit_solver.py ulds.csv packages.csv K [--runs N] [--seed S]")
        sys.exit(1)

    os.makedirs("output", exist_ok=True)

    # ── Single run ─────────────────────────────────────────────────────────────
    if num_runs == 1:
        result = solve(ulds, packages, K, rng=None, run_id=0)
        print_summary(result)
        write_official_output(result, "output/solution.txt")
        write_json_output(result, "output/solution_full.json")
        write_csv_placements(result, "output/placements.csv")
        print(f"[✓] Official output  → output/solution.txt")
        print(f"[✓] Full JSON output → output/solution_full.json")
        print(f"[✓] CSV placements   → output/placements.csv")

    # ── Multi-run (random restarts) ────────────────────────────────────────────
    else:
        base_seed = seed if seed is not None else 42
        print(f"[INFO] Running {num_runs} random restarts (base seed={base_seed})\n")

        all_results = []
        costs = []

        for run_id in range(num_runs):
            rng = random.Random(base_seed + run_id)
            # Run 0 is always deterministic (no shuffling) — gives the baseline
            result = solve(ulds, packages, K,
                           rng=(None if run_id == 0 else rng),
                           run_id=run_id)
            all_results.append(result)
            costs.append(result["summary"]["total_cost"])
            feasible = "✅" if result["summary"]["is_feasible"] else "❌"
            print(f"  Run {run_id:>3}: cost={result['summary']['total_cost']:>8}  "
                  f"packed={result['summary']['total_packed_packages']}  {feasible}")

        # ── Stats across all runs ──────────────────────────────────────────────
        feasible_results = [r for r in all_results if r["summary"]["is_feasible"]]
        feasible_costs   = [r["summary"]["total_cost"] for r in feasible_results]

        print(f"\n{'─'*55}")
        print(f"  RANDOM RESTART SUMMARY  ({num_runs} runs)")
        print(f"{'─'*55}")
        print(f"  Feasible solutions : {len(feasible_results)} / {num_runs}")
        if feasible_costs:
            best  = min(feasible_costs)
            worst = max(feasible_costs)
            avg   = sum(feasible_costs) / len(feasible_costs)
            print(f"  Best  cost (feasible) : {best}")
            print(f"  Worst cost (feasible) : {worst}")
            print(f"  Avg   cost (feasible) : {avg:.1f}")
        print(f"{'─'*55}\n")

        # ── Write outputs ──────────────────────────────────────────────────────

        # 1. Best feasible solution in official format
        if feasible_results:
            best_result = min(feasible_results, key=lambda r: r["summary"]["total_cost"])
            write_official_output(best_result, "output/solution_best.txt")
            write_json_output(best_result, "output/solution_best.json")
            print(f"[✓] Best solution (run {best_result['run_id']}, cost={best_result['summary']['total_cost']}) → output/solution_best.txt")

        # 2. All runs as a single JSON array (for AI team)
        with open("output/all_runs.json", "w") as f:
            json.dump(all_results, f, indent=2)
        print(f"[✓] All {num_runs} runs          → output/all_runs.json")

        # 3. Per-run official solution files
        runs_dir = "output/runs"
        os.makedirs(runs_dir, exist_ok=True)
        for r in all_results:
            write_official_output(r, f"{runs_dir}/solution_run{r['run_id']:04d}.txt")

        # 4. Combined placements CSV (all runs, with run_id column)
        csv_path = "output/all_placements.csv"
        for i, r in enumerate(all_results):
            write_csv_placements(r, csv_path, mode="w" if i==0 else "a", write_header=(i==0))
        print(f"[✓] All placements CSV  → {csv_path}")

        # 5. Run-level summary CSV (one row per run — useful for AI scoring)
        summary_path = "output/runs_summary.csv"
        with open(summary_path, "w", newline="") as f:
            fields = ["run_id","total_cost","total_packed","priority_ulds",
                      "economy_left_behind","is_feasible","priority_failures"]
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in all_results:
                s = r["summary"]
                w.writerow({
                    "run_id": r["run_id"],
                    "total_cost": s["total_cost"],
                    "total_packed": s["total_packed_packages"],
                    "priority_ulds": s["number_of_priority_ulds"],
                    "economy_left_behind": s["left_behind_economy_cost"],
                    "is_feasible": s["is_feasible"],
                    "priority_failures": ";".join(s["priority_failures"]),
                })
        print(f"[✓] Runs summary CSV    → {summary_path}")
        print(f"[✓] Per-run txt files   → {runs_dir}/solution_run*.txt")
