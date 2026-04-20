import cplex
import sys
import os
import time

# Format numbers with comma as decimal separator (European style)
def fmt(x, decimals=2):
    return f"{x:.{decimals}f}".replace(".", ",")

def export_row(instance_name, obj, elapsed, optimal, ttb, csv_file):
    row = "\t".join([
        instance_name,
        fmt(obj),
        fmt(elapsed, 2),
        "TRUE" if optimal else "FALSE",
        fmt(ttb, 2),
    ])
    write_header = not os.path.exists(csv_file)
    with open(csv_file, "a") as f:
        if write_header:
            f.write("Instance\tObjective\tTime\tOptimal\tTTB\n")
        f.write(row + "\n")

class IncumbentTracker(cplex.callbacks.IncumbentCallback):
    def __call__(self):
        self.ttb = time.time() - self.t0

class TimedExportCallback(cplex.callbacks.MIPInfoCallback):
    def __call__(self):
        if self.exported:
            return
        elapsed = time.time() - self.t0
        if elapsed >= 3600:
            self.exported = True
            try:
                obj = self.get_incumbent_objective_value()
            except cplex.exceptions.CplexError:
                obj = float("nan")
            export_row(self.instance_name, obj, elapsed, False,
                       self.incumbent_tracker.ttb, self.csv_file)
            print(f"[{self.instance_name}] 1-hour checkpoint exported to {self.csv_file}")

def solve(mps_file, csv_file="results.csv"):
    instance_name = os.path.splitext(os.path.basename(mps_file))[0]

    c = cplex.Cplex(mps_file)
    c.parameters.timelimit.set(3600.0*3)
    c.parameters.threads.set(64)

    t0 = time.time()

    inc_cb = c.register_callback(IncumbentTracker)
    inc_cb.t0 = t0
    inc_cb.ttb = float("nan")

    cb = c.register_callback(TimedExportCallback)
    cb.t0 = t0
    cb.exported = False
    cb.instance_name = instance_name
    cb.csv_file = csv_file
    cb.incumbent_tracker = inc_cb

    c.solve()
    elapsed = time.time() - t0

    status = c.solution.get_status_string()
    obj = c.solution.get_objective_value()
    optimal = c.solution.get_status() in (101, 102)  # MIPoptimal / MIPoptimalTol
    ttb = inc_cb.ttb

    print(f"[{instance_name}] Status: {status}, Objective: {obj}, TTB: {ttb:.2f}s")

    export_row(instance_name, obj, elapsed, optimal, ttb, csv_file)
    print(f"Results appended to {csv_file}")


arg = sys.argv[1] if len(sys.argv) > 1 else "complete_001_10x45_100_20.mps"

if os.path.isdir(arg):
    mps_files = sorted(f for f in os.listdir(arg) if f.endswith(".mps"))
    for fname in mps_files:
        solve(os.path.join(arg, fname))
else:
    solve(arg)
