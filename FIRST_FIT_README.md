# First Fit Solver — README

This document covers the First Fit packing module: `packages.py`, `ULDs.py`,
`input.py`, `solver.py`, `output.py`. For overall project info see `README.md`.

---

## What It Does

Packs a list of packages into a list of ULDs (cargo containers) using a
**First Fit** strategy, with optional **random restarts** to generate many
diverse solutions:

1. Priority packages are placed first, then Economy packages
2. For each package, ULDs are tried in order — it's placed in the **first**
   ULD where a valid position is found
3. Within a ULD, all 6 orientations of the package are tried, and candidate
   positions come from the corners of already-placed packages (extreme points)
4. The first valid (orientation, position) combination is used

In **multi-run mode**, package order, ULD order, and orientation order are
randomly shuffled each run — useful for generating diverse training data.

---

## File Roles

| File | Role |
|---|---|
| `packages.py` | `Package` class — id, dimensions, weight, type, delay cost, plus orientation generation |
| `ULDs.py` | `ULD` class — id, dimensions, weight limit, tracks placed packages and utilization |
| `input.py` | Reads a manifest (JSON or CSV) and builds `Package`/`ULD` object lists |
| `solver.py` | The First Fit algorithm — geometry checks, placement, and the `solve()` orchestrator |
| `output.py` | Writes results to `solution.txt` / `.json` / `.csv` (single-run and multi-run) |

---

## How to Run

### Prerequisites

No external libraries needed — only Python's built-ins (`json`, `csv`, `random`).

```bash
python --version
# 3.8 or higher
```

### Single run — from JSON

```python
from input import load
from solver import solve
from output import write_single

packages, ulds, K = load("sample_input/manifest.json")
result = solve(packages, ulds, K)
write_single(result, out_dir="output")
```

### Single run — from CSV

```python
from input import load
from solver import solve
from output import write_single

packages, ulds, K = load("sample_input/ulds.csv", "sample_input/packages.csv", K=100)
result = solve(packages, ulds, K)
write_single(result, out_dir="output")
```

### Multi-run — random restarts

```python
import random
from input import load
from solver import solve
from output import write_multi

packages, ulds, K = load("sample_input/manifest.json")

all_results = []
for run_id in range(200):
    rng = random.Random(42 + run_id)
    # run 0 is always deterministic (no shuffling) — the baseline
    result = solve(packages, ulds, K, rng=(None if run_id == 0 else rng), run_id=run_id)
    all_results.append(result)

write_multi(all_results, out_dir="output")
```

Save any of the above as a script (e.g. `run.py`) and execute with:

```bash
python run.py
```

---

## Input Format

### JSON (single file)

```json
{
  "K": 100,
  "ulds": [
    {"id": "ULD-1", "length": 240, "width": 180, "height": 160, "weight_limit": 1000}
  ],
  "packages": [
    {"id": "P-001", "length": 80, "width": 60, "height": 50, "weight": 120,
     "type": "Priority", "delay_cost": 0}
  ]
}
```

### CSV (two files)

`ulds.csv` — columns: `id, length, width, height, weight_limit`

`packages.csv` — columns: `id, length, width, height, weight, type, delay_cost`

See `sample_input/` for working examples of all three formats.

### Field Reference

| Field | Description |
|---|---|
| `K` | Penalty per ULD that contains any Priority package |
| `ulds[].id` | Unique container identifier |
| `ulds[].length/width/height` | ULD dimensions in cm |
| `ulds[].weight_limit` | Max weight the ULD can carry (kg) |
| `packages[].id` | Unique package identifier |
| `packages[].length/width/height` | Package dimensions in cm |
| `packages[].weight` | Package weight in kg |
| `packages[].type` | `"Priority"` or `"Economy"` |
| `packages[].delay_cost` | Cost if left behind (Economy only; 0 for Priority) |

---

## Output Format

### Single run — `write_single()`

| File | Description |
|---|---|
| `solution.txt` | Evaluator format (see below) |
| `solution.json` | Full structured result — summary, per-ULD stats, placements, unpacked |
| `placements.csv` | Flat CSV, one row per placed package |

### Multi-run — `write_multi()`

| File | Description |
|---|---|
| `solution_best.txt` / `.json` | Best feasible solution across all runs |
| `all_runs.json` | Every run's full result — primary AI training data |
| `runs_summary.csv` | One row per run: cost, packed count, feasibility — AI labels |
| `all_placements.csv` | Every placement across all runs, tagged with `run_id` |
| `runs/solution_run0000.txt` ... | Per-run evaluator-format files |

### Evaluator format (`solution.txt`)

```
Total-Cost, Total-Packed-Packages, Number-of-Priority-ULDs
Package-ID, ULD-ID, x0, y0, z0, x1, y1, z1
...
Package-ID, NONE, -1, -1, -1, -1, -1, -1     ← unpacked packages
```

---

## Cost Function

```
Total Cost = Σ(delay_cost of left-behind Economy packages) + K × N_priority_ulds
```

`N_priority_ulds` = number of ULDs containing at least one Priority package.

### Hard Constraints (always enforced)
1. Every Priority package must be packed
2. No two packages may overlap inside a ULD
3. Every package must lie fully within its ULD's bounds
4. Total weight in a ULD must not exceed its weight limit

---

## Sample Data

`sample_input/` — a manifest with 3 Priority + 5 Economy packages and 2 ULDs,
provided in both JSON (`manifest.json`) and CSV (`packages.csv` + `ulds.csv`) form.

`sample_output/` — the actual result of running `write_single()` on the sample
manifest with `K=100`:
- Total cost: 100
- All 8 packages packed (feasible)
- 1 ULD used for Priority packages

Reproduce it yourself:

```bash
python -c "
from input import load
from solver import solve
from output import write_single

packages, ulds, K = load('sample_input/manifest.json')
result = solve(packages, ulds, K)
write_single(result, out_dir='output')
"
```
