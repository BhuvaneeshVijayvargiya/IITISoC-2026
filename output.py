import os
#temporary file, just used for checking purposes

def write_official_txt(result: dict, filepath: str):
    s = result["summary"]

    lines = [
        f"{s['total_cost']}, {s['total_packed_packages']}, {s['number_of_priority_ulds']}"
    ]

    for p in result["placements"]:
        lines.append(
            f"{p['package_id']}, {p['uld_id']}, "
            f"{int(p['x0'])}, {int(p['y0'])}, {int(p['z0'])}, "
            f"{int(p['x1'])}, {int(p['y1'])}, {int(p['z1'])}"
        )

    for u in result["unpacked"]:
        lines.append(
            f"{u['package_id']}, NONE, -1, -1, -1, -1, -1, -1"
        )

    with open(filepath, "w") as f:
        f.write("\n".join(lines) + "\n")


def write_single(result: dict, out_dir: str = "output"):

    os.makedirs(out_dir, exist_ok=True)

    write_official_txt(
        result,
        os.path.join(out_dir, "solution.txt")
    )
