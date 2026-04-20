# GurobiModel — Cyclic Min-Max Sitting Arrangement (MIP)


## Requirements

```bash
pip install gurobipy matplotlib numpy
```

> Requires a valid Gurobi license (`gurobi.lic`).

## Running

Set the parameters at the top of `main.py`:

| Parameter | Default | Description |
|---|---|---|
| `p` | `"../Instances/test"` | Path to folder containing instance files |
| `cores` | `8` | Number of solver threads |
| `timelimit` | `300` | Time limit per instance (seconds) |
| `memLimit` | `110` | Memory limit (GB) |

Then run:

```bash
python main.py
```

Instances are processed in ascending order of vertex count. The correct model class is selected automatically: `Even` for even `NV`, `Odd` for odd `NV`.

## Input format

Same format as the Hexaly solver:

```
NV NE
v1 v2 w
v1 v2 w
...
```

- Leading `#` comment lines are skipped.
- First data line: `NV NE` (e.g., `10 6`) or `NV:10 NE:6`.
- Each edge line: `v1 v2 w` where `w` is `1` (positive) or `-1` (negative). Vertices are **1-indexed**.

## Output

Results are appended to `output.csv`:

```
instance;objective;ttb;time;gap;optimal
```

| Column | Description |
|---|---|
| `instance` | File path |
| `objective` | Best objective value (max errors) |
| `ttb` | Time to best incumbent (seconds) |
| `time` | Total solver runtime (seconds) |
| `gap` | Final MIP gap |
| `optimal` | `True` if proven optimal |

A `model.lp` file is also written to disk after each solve for debugging.

