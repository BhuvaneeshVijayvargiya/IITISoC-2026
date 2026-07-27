#this is to read the input cargo data and make it into a readable format for the rest of the program.

import pandas as pd
from packages import Package
from ULDs import ULD
 
def load(filepath: str) -> tuple[list[Package], list[ULD], float]:
  
    with open(filepath) as f:
        lines = [line.strip() for line in f.readlines()]
 
    K = float(lines[0])

    blank_rows = [i for i, line in enumerate(lines) if line.strip() == ""]

    if blank_rows and blank_rows[0] == 1:
        uld_start = 2
        boundary_idx = 1
    else:
        uld_start = 1
        boundary_idx = 0

    uld_end = blank_rows[boundary_idx]

    pkg_start = blank_rows[boundary_idx] + 1
    pkg_end = blank_rows[boundary_idx + 1] if len(blank_rows) > boundary_idx + 1 else len(lines)

 
    uld_df = pd.read_csv(
        filepath,
        skiprows=uld_start,
        nrows=uld_end - uld_start,
        header=None,
        names=["id", "length", "width", "height", "weight_limit"],
        dtype={"id": str},
        skipinitialspace=True,
    )
 
 
    pkg_df = pd.read_csv(
        filepath,
        skiprows=pkg_start,
        nrows=pkg_end - pkg_start,
        header=None,
        names=["id", "length", "width", "height", "weight", "package_type", "delay_cost"],
        dtype={"id": str, "package_type": str},
        skipinitialspace=True,
        na_values="-",
    )
    pkg_df["delay_cost"] = pkg_df["delay_cost"].fillna(0.0)

 
    ulds = [ULD(**row) for row in uld_df.to_dict("records")]
    packages = [Package(**row) for row in pkg_df.to_dict("records")]
    
 
    return packages, ulds, K
