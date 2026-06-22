"""
JSON format:
  {
    "K": 100,
    "ulds": [
      {"id": "ULD-1", "length": 240, "width": 180, "height": 160, "weight_limit": 1000}
    ],
    "packages": [
      {"id": "P-1", "length": 80, "width": 60, "height": 50, "weight": 120,
       "type": "Priority", "delay_cost": 0}
    ]
  }

CSV format:
  ulds.csv     -> columns: id, length, width, height, weight_limit
  packages.csv -> columns: id, length, width, height, weight, type, delay_cost
"""

import json
import csv
from packages import Package
from ULDs import ULD

def load_json(filepath: str) -> tuple[list[Package], list[ULD], float]:
    with open(filepath) as f:
        data = json.load(f)

    ulds = [
        ULD(
            id=u["id"],
            length=u["length"],
            width=u["width"],
            height=u["height"],
            weight_limit=u["weight_limit"],
        )
        for u in data["ulds"]
    ]

    packages = [
        Package(
            id=p["id"],
            length=p["length"],
            width=p["width"],
            height=p["height"],
            weight=p["weight"],
            package_type=p["type"],
            delay_cost=p.get("delay_cost", 0.0),
        )
        for p in data["packages"]
    ]

    K = float(data.get("K", 0))
    return packages, ulds, K


def load_csv(ulds_filepath: str, packages_filepath: str, K: float) -> tuple[list[Package], list[ULD], float]:
    ulds = []
    with open(ulds_filepath, newline="") as f:
        for row in csv.DictReader(f):
            ulds.append(ULD(
                id=row["id"].strip(),
                length=float(row["length"]),
                width=float(row["width"]),
                height=float(row["height"]),
                weight_limit=float(row["weight_limit"]),
            ))

    packages = []
    with open(packages_filepath, newline="") as f:
        for row in csv.DictReader(f):
            packages.append(Package(
                id=row["id"].strip(),
                length=float(row["length"]),
                width=float(row["width"]),
                height=float(row["height"]),
                weight=float(row["weight"]),
                package_type=row["type"].strip(),
                delay_cost=float(row["delay_cost"]) if row.get("delay_cost", "").strip() else 0.0,
            ))

    return packages, ulds, K


def load(filepath_or_ulds, packages_filepath: str = None, K: float = 0.0):
    if packages_filepath is None:
        if not filepath_or_ulds.endswith(".json"):
            raise ValueError("Single-argument load() expects a .json file")
        return load_json(filepath_or_ulds)
    return load_csv(filepath_or_ulds, packages_filepath, K)
