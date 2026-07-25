#saves every box-packing decision made by PCT into a spreadsheet

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


def add_round(records: list, all_nodes: list, best_node, round_number: int):
    for node in all_nodes:
        chosen = (node is best_node)
        records.append(pct_node_to_dict(node, chosen, round_number))

def save_pct(records : list, out_dir: str = "output"):
    os.makedirs(out_dir, exist_ok=True)

    csv_path = os.path.join(out_dir, "pct_log.csv")
    if records:
        fieldnames = list(records[0].keys())
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
        

def summary(records:  list) -> dict:
    total          = len(records)
    chosen         = sum(1 for r in records if r["was_chosen"])
    rounds_covered = len(set(r["round"] for r in records))
    return {
        "total_pct_nodes_seen": total,
        "nodes_chosen":         chosen,
        "rounds_processed":     rounds_covered,
    }
