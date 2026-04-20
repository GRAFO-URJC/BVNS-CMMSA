# cplex


## Requirements

```bash
pip install gurobipy cplex matplotlib numpy
```

> Requires a valid Gurobi license (for MPS generation only — Gurobi does not solve here) and a valid CPLEX license (for solving).

---

## Step 1 — Generate MPS files

From inside `MPSgenerator/`:

```bash
cd MPSgenerator
python main.py
```

This reads all instances from `./instances/`, selects `Even` or `Odd` model class based on `NV`, builds the MIP formulation with Gurobi, and writes one `.mps` file per instance to the current directory. No solving happens.

---

## Step 2 — Solve with CPLEX

From the project root, pass either a single `.mps` file or a folder of `.mps` files:

```bash
# Single file
python run_cplex.py path/to/instance.mps

# Entire folder
python run_cplex.py path/to/mps_folder/
```

Results are appended to `results.csv` (tab-separated):

| Column | Description |
|---|---|
| `Instance` | MPS filename (no extension) |
| `Objective` | Best objective value found |
| `Time` | Total runtime (seconds) |
| `Optimal` | `TRUE` if proven optimal |
| `TTB` | Time to best incumbent (seconds) |

**CPLEX parameters in `run_cplex.py`:**

| Parameter | Default | Description |
|---|---|---|
| `timelimit` | `10800s` (3h) | Time limit per instance |
| `threads` | `64` | Number of solver threads |


---

## Input format

Same as the other solvers:

```
NV NE
v1 v2 w
...
```

Leading `#` comment lines are skipped. Vertices are **1-indexed**. Edge weights: `1` (positive) or `-1` (negative).

