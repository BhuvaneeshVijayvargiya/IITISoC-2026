# First Fit Solver — IITISoC 2026
### Intelligent Cargo Packing & Spatial Neuro-Optimization

This folder contains the **First Fit baseline solver** built by the packing team.
It takes a flight manifest (ULDs + packages) and produces valid 3D packing solutions
using a brute-force First Fit algorithm with random restarts.

The outputs of this solver feed directly into the AI team's model as training data.

---

## Folder Structure

```
first-fit-solver/
├── first_fit_solver.py       ← main solver (run this)
├── README.md                 ← this file
├── sample_data/
│   ├── sample_input.json     ← sample manifest (JSON format)
│   ├── sample_ulds.csv       ← sample ULDs (CSV format)
│   └── sample_packages.csv   ← sample packages (CSV format)
└── sample_output/
    ├── solution_best.txt     ← best solution in evaluator format
    ├── solution_best.json    ← best solution full details
    ├── all_runs.json         ← all 200 solutions (AI training data)
    ├── runs_summary.csv      ← cost per run (AI labels)
    └── all_placements.csv    ← all placements across all runs
```

---

## Prerequisites

Python 3.8 or higher. No external libraries needed — only built-ins are used.

```bash
python --version
# should show Python 3.8 or higher
```

---

## How to Run

### Step 1 — Place files in the same folder

```
my_folder/
├── first_fit_solver.py
└── your_input.json
```

### Step 2 — Open a terminal in that folder

- **Windows** — right click the folder → "Open in Terminal"
- **Mac** — right click the folder → "New Terminal at Folder"
- **Linux** — `cd` into the folder

### Step 3 — Run

**Single run** — one deterministic solution:
```bash
python first_fit_solver.py your_input.json
```

**Multiple randomized runs** — recommended for training data:
```bash
python first_fit_solver.py your_input.json --runs 500
```

**With fixed seed** — same results every time:
```bash
python first_fit_solver.py your_input.json --runs 500 --seed 42
```

**Using CSV input:**
```bash
python first_fit_solver.py ulds.csv packages.csv 100
#                          ^^^^^^^^  ^^^^^^^^^^^^  ^
#                          ULDs file  Packages     K value
```

**Using the provided sample input:**
```bash
python first_fit_solver.py sample_data/sample_input.json --runs 200
```

### Step 4 — Check results

An `output/` folder is created automatically:

```
output/
├── solution.txt              ← single run: evaluator-format result
├── solution_full.json        ← single run: full details
├── placements.csv            ← single run: flat CSV
├── solution_best.txt         ← multi-run: best solution found
├── solution_best.json        ← multi-run: best solution full details
├── all_runs.json             ← multi-run: all solutions (AI training data)
├── runs_summary.csv          ← multi-run: cost per run (labels for AI)
├── all_placements.csv        ← multi-run: all placements across all runs
└── runs/
    ├── solution_run0000.txt
    ├── solution_run0001.txt
    └── ...
```

---

## Input Format

### JSON (recommended)

```json
{
  "K": 100,
  "ulds": [
    {
      "id": "ULD-1",
      "length": 240,
      "width": 180,
      "height": 160,
      "weight_limit": 1000
    }
  ],
  "packages": [
    {
      "id": "P-001",
      "length": 80,
      "width": 60,
      "height": 50,
      "weight": 120,
      "type": "Priority",
      "delay_cost": 0
    },
    {
      "id": "E-001",
      "length": 80,
      "width": 60,
      "height": 50,
      "weight": 130,
      "type": "Economy",
      "delay_cost": 50
    }
  ]
}
```

### CSV

`ulds.csv` — columns: `id, length, width, height, weight_limit`

`packages.csv` — columns: `id, length, width, height, weight, type, delay_cost`

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

## Cost Function

```
Total Cost = Σ(delay_cost of left-behind Economy packages) + K × N_priority_ulds
```

`N_priority_ulds` = number of ULDs that contain at least one Priority package.

### Hard Constraints (always enforced)
1. Every Priority package must be packed — no exceptions
2. No two packages may overlap inside a ULD
3. Every package must lie fully within its ULD bounds
4. Total weight in a ULD must not exceed its weight limit

Feasibility is primary — a valid solution with higher cost beats an invalid one.

---

## Evaluator Output Format

```
Total-Cost, Total-Packed-Packages, Number-of-Priority-ULDs
Package-ID, ULD-ID, x0, y0, z0, x1, y1, z1
...
Package-ID, NONE, -1, -1, -1, -1, -1, -1    ← unpacked
```

---

## Coordinate Convention

```
Z (Height)
│
│
└────── Y (Width)
 \
  X (Length)

Origin (0,0,0) = front-left-bottom corner of ULD
```

Each package is defined by two corners `(x0,y0,z0)` → `(x1,y1,z1)`.

---

## How the Algorithm Works

1. Sort packages — Priority first, then Economy
2. For each package, try ULDs one by one
3. In each ULD, try all 6 axis-aligned orientations of the package
4. For each orientation, try candidate positions (corners of already-placed packages)
5. First valid placement found → commit it, move to next package
6. If no ULD fits → package is left behind (Economy) or flagged as violation (Priority)

In **multi-run mode**, package order, ULD order, and orientation order are randomly
shuffled each run to produce diverse solutions. Run 0 is always the deterministic baseline.

---

## For the AI Team

The key files to consume:

| File | Use |
|---|---|
| `sample_output/all_runs.json` | Training data — 200 solutions on the sample manifest |
| `sample_output/runs_summary.csv` | Labels — cost per run for scoring/ranking |
| `sample_output/all_placements.csv` | Feature table — placement details across all runs |

The geometry functions in `first_fit_solver.py` (`is_valid`, `overlaps`, `candidate_positions`)
can be imported and reused directly in your AI placement loop to validate placements before committing.

```python
from first_fit_solver import is_valid, overlaps, candidate_positions, ULD, Package
```
