import json
import csv
import os

# SINGLE RESULT WRITERS

def write_official_txt(result: dict, filepath: str):
    s = result["summary"]
    lines = [f"{s['total_cost']}, {s['total_packed_packages']}, {s['number_of_priority_ulds']}"]

    for p in result["placements"]:
        lines.append(
            f"{p['package_id']}, {p['uld_id']}, "
            f"{int(p['x0'])}, {int(p['y0'])}, {int(p['z0'])}, "
            f"{int(p['x1'])}, {int(p['y1'])}, {int(p['z1'])}"
        )

    for u in result["unpacked"]:
        lines.append(f"{u['package_id']}, NONE, -1, -1, -1, -1, -1, -1")

    with open(filepath, "w") as f:
        f.write("\n".join(lines) + "\n")


def write_json(result: dict, filepath: str):
    with open(filepath, "w") as f:
        json.dump(result, f, indent=2)


def write_placements_csv(result: dict, filepath: str, mode: str = "w", write_header: bool = True):
    fields = ["run_id", "package_id", "package_type", "uld_id",
              "x0", "y0", "z0", "x1", "y1", "z1",
              "vol_l", "vol_w", "vol_h", "volume", "orientation_used"]

    with open(filepath, mode, newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if write_header:
            w.writeheader()
        for p in result["placements"]:
            l = p["x1"] - p["x0"]
            wd = p["y1"] - p["y0"]
            h = p["z1"] - p["z0"]
            w.writerow({
                "run_id": result.get("run_id", 0),
                **p,
                "vol_l": l, "vol_w": wd, "vol_h": h, "volume": l * wd * h,
                "orientation_used": str(p["orientation_used"]),
            })


def write_single(result: dict, out_dir: str = "output"):
    os.makedirs(out_dir, exist_ok=True)
    write_official_txt(result, os.path.join(out_dir, "solution.txt"))
    write_json(result, os.path.join(out_dir, "solution.json"))
    write_placements_csv(result, os.path.join(out_dir, "placements.csv"))
    print(f"[OK] solution.txt   -> {out_dir}/solution.txt")
    print(f"[OK] solution.json  -> {out_dir}/solution.json")
    print(f"[OK] placements.csv -> {out_dir}/placements.csv")

# MULTI-RUN WRITERS 

def write_multi(all_results: list, out_dir: str = "output"):
    os.makedirs(out_dir, exist_ok=True)

    feasible = [r for r in all_results if r["summary"]["is_feasible"]]

    if feasible:
        best = min(feasible, key=lambda r: r["summary"]["total_cost"])
        write_official_txt(best, os.path.join(out_dir, "solution_best.txt"))
        write_json(best, os.path.join(out_dir, "solution_best.json"))
        print(f"[OK] solution_best.txt  -> {out_dir}/solution_best.txt  "
              f"(run {best['run_id']}, cost={best['summary']['total_cost']})")

    with open(os.path.join(out_dir, "all_runs.json"), "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"[OK] all_runs.json      -> {out_dir}/all_runs.json")

    runs_dir = os.path.join(out_dir, "runs")
    os.makedirs(runs_dir, exist_ok=True)
    for r in all_results:
        write_official_txt(r, os.path.join(runs_dir, f"solution_run{r['run_id']:04d}.txt"))
    print(f"[OK] per-run txt files  -> {runs_dir}/solution_run*.txt")

    csv_path = os.path.join(out_dir, "all_placements.csv")
    for i, r in enumerate(all_results):
        write_placements_csv(r, csv_path, mode="w" if i == 0 else "a", write_header=(i == 0))
    print(f"[OK] all_placements.csv -> {csv_path}")

    summary_path = os.path.join(out_dir, "runs_summary.csv")
    with open(summary_path, "w", newline="") as f:
        fields = ["run_id", "total_cost", "total_packed", "priority_ulds",
                  "economy_left_behind", "is_feasible", "priority_failures"]
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
    print(f"[OK] runs_summary.csv   -> {summary_path}")
