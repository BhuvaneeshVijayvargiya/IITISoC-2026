import csv
import json
import os


def pct_node_to_dict(node, was_chosen: bool, round_number: int) -> dict:
    x, y, z = node.ep
    l, w, h = node.ori

    return {
        "round":            round_number,
        "package_id":       node.package.id,
        "package_type":     node.package.package_type,
        "pkg_length":       node.package.length,
        "pkg_width":        node.package.width,
        "pkg_height":       node.package.height,
        "pkg_weight":       node.package.weight,
        "delay_cost":       node.package.delay_cost,
        "uld_id":           node.uld.id,
        "uld_weight_now":   node.uld.current_weight,
        "uld_weight_max":   node.uld.weight_limit,
        "uld_has_priority": node.uld.has_priority,
        "ep_x":             x,
        "ep_y":             y,
        "ep_z":             z,
        "ori_l":            l,
        "ori_w":            w,
        "ori_h":            h,
        "end_x":            x + l,
        "end_y":            y + w,
        "end_z":            z + h,
        "volume":           l * w * h,
        "score":            node.score,
        "was_chosen":       was_chosen,
    }


class PCTStore:
    def __init__(self):
        self.records = []

    def add_round(self, all_nodes: list, best_node, round_number: int):
        for node in all_nodes:
            chosen = (node is best_node)
            row = pct_node_to_dict(node, chosen, round_number)
            self.records.append(row)

    def save(self, out_dir: str = "output"):
        os.makedirs(out_dir, exist_ok=True)

        csv_path = os.path.join(out_dir, "pct_log.csv")
        if self.records:
            fieldnames = list(self.records[0].keys())
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.records)
            print(f"[PCT] pct_log.csv   -> {csv_path}  ({len(self.records)} rows)")
        else:
            print("[PCT] No PCT nodes were recorded.")

        json_path = os.path.join(out_dir, "pct_log.json")
        with open(json_path, "w") as f:
            json.dump(self.records, f, indent=2)
        print(f"[PCT] pct_log.json  -> {json_path}")

    def summary(self) -> dict:
        total          = len(self.records)
        chosen         = sum(1 for r in self.records if r["was_chosen"])
        rounds_covered = len(set(r["round"] for r in self.records))
        return {
            "total_pct_nodes_seen": total,
            "nodes_chosen":         chosen,
            "rounds_processed":     rounds_covered,
        }
