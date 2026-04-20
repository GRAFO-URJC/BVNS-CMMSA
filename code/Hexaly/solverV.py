import datetime
import os

import hexaly.optimizer
from itertools import product

EXECUTION_TIME_IN_SECONDS = 600
HEXALY_VERBOSE = False

def solve_cyclic_min_max_sitting_arrangement(n, A):
    with hexaly.optimizer.HexalyOptimizer() as optimizer:

        print("Starting optimization...")

        # Verbosity
        optimizer.param.verbosity = 1 if HEXALY_VERBOSE else 0

        cb = LastBestCallback()
        # Add the callback
        optimizer.add_callback(hexaly.optimizer.HxCallbackType.TIME_TICKED, cb.callback)

        # Create the model
        model = optimizer.model

        is_odd = n % 2 == 1

        # Create a list of problematic vertex combinations
        W = set()
        V = range(0, n)
        for u, v, w in product(V, V, V):
            if u != v and v != w and w != u:
                if A.get((u, v), 0) < 0 and A.get((u, w), 0) > 0:
                    W.add((u, v, w))

        W = list(W)

        # List of order of vertices
        p = model.list(n)
        # Constraint 1: Each vertex should appear exactly once
        model.constraint(model.count(p) == n)

        # Distance matrix for cycle
        dist_matrix = [[min(abs(i - j), n - abs(i - j)) for j in range(n)] for i in range(n)]

        # Side relationship matrices
        right_matrix = [[False] * n for _ in range(n)]
        left_matrix = [[False] * n for _ in range(n)]

        # Compute side relationships
        for a in range(n):
            for b in range(n):
                if a == b:
                    continue
                diff = (b - a + n) % n
                if 1 <= diff < n / 2:
                    right_matrix[a][b] = True
                elif n / 2 < diff <= n - 1:
                    left_matrix[a][b] = True

        # Convert to model arrays
        dist_matrix = model.array(dist_matrix)
        right_matrix = model.array(right_matrix)
        left_matrix = model.array(left_matrix)

        # Error tracking with detailed logging
        errors = {a: [] for a in range(n)}
        error_details =  {}


        if not is_odd:
            num_obstacles_left = {}
            num_obstacles_right = {}
            opposites = {}
            for (u, v, w) in W:
                if (u,w) not in num_obstacles_left:
                    p_u = model.index(p, u)
                    p_w = model.index(p, w)
                    num_obstacles_left[(u,w)] = model.sum()
                    num_obstacles_right[(u,w)] = model.sum()
                    opposites[(u,w)] = model.and_(model.not_(model.at(left_matrix, p_u, p_w)), model.not_(model.at(right_matrix, p_u, p_w)))
                    errors[u].append(model.iif(opposites[(u,w)], model.min(num_obstacles_left[(u,w)], num_obstacles_right[(u,w)]), 0))

            for (u, v, w) in W:
                # Find positions in the permutation
                p_u = model.index(p, u)
                p_v = model.index(p, v)
                p_w = model.index(p, w)

                # Condition 1: The distance between u and v is less than the distance between u and w
                distance_condition = model.lt(model.at(dist_matrix, p_u, p_v), model.at(dist_matrix, p_u, p_w))

                # Condition 2: Vertices u, v and w are in the same side
                side_condition = model.or_(
                    model.and_(
                        model.at(right_matrix, p_u, p_w),
                        model.at(right_matrix, p_u, p_v)
                    ),
                    model.and_(
                        model.at(left_matrix, p_u, p_w),
                        model.at(left_matrix, p_u, p_v)
                    )
                )

                num_obstacles_left[(u,w)].add_operand(model.at(left_matrix, p_u, p_v))
                num_obstacles_right[(u,w)].add_operand(model.at(right_matrix, p_u, p_v))

                # Create an error if conditions are violated
                error = model.and_(distance_condition, side_condition)

                # Store error details
                error_details[(u, v, w)] = error
                errors[u].append(error)

        else:
            for (u, v, w) in W:
                # Find positions in the permutation
                p_u = model.index(p, u)
                p_v = model.index(p, v)
                p_w = model.index(p, w)

                # Condition 1: The distance between u and v is less than the distance between u and w
                distance_condition = model.lt(model.at(dist_matrix, p_u, p_v), model.at(dist_matrix, p_u, p_w))

                # Condition 2: Vertices u, v and w are in the same side
                side_condition = model.or_(
                    model.and_(
                        model.at(right_matrix, p_u, p_v),
                        model.at(right_matrix, p_u, p_w)
                    ),
                    model.and_(
                        model.at(left_matrix, p_u, p_v),
                        model.at(left_matrix, p_u, p_w)
                    )
                )

                # Create an error if conditions are violated
                error = model.and_(distance_condition, side_condition)

                # Store error details
                error_details[(u, v, w)] = error
                errors[u].append(error)

        # Create error count for each vertex
        num_errors = model.array([model.sum(errors[a]) for a in range(n)])
        max_errors = model.max(num_errors)

        # Objective: minimize maximum errors
        model.minimize(max_errors)

        model.close()

        # Set a time limit
        optimizer.param.time_limit = EXECUTION_TIME_IN_SECONDS
        optimizer.param.nb_threads = 1



        # Solve the model
        optimizer.solve()

        # Save environment for debugging
        #optimizer.save_environment("cyclic_min_max_sitting_arrangement.HXM")

        solution = optimizer.get_solution()

        # print("Optimization finished.")
        
        arrangement = []
        # Print results
        print("\nArrangement:")
        for r in p.value:
            # print(r, end=" ")
            arrangement.append(r+1)
        print(arrangement)
        print("\n\nError Counts:")
        for a in range(n):
            print(f"\tVertex {a+1}: {num_errors.value[a]} errors")
        
        # Print error details
        #print("\nError Details:")
        #for (u, v, w), error in error_details.items():
        #    if error.value:
        #        print(f"\tVertices {u}, {v}, {w}")



        time_to_best = cb.last_best_running_time

        return max_errors.value, arrangement, solution.get_objective_gap(0), time_to_best, optimizer.get_statistics().get_running_time(), solution.status





def sample_instance():
    NV = 6
    E_POS = [(0, 1), (0, 2), (2,1), (0, 3), (2, 3),(3,1),(2,5),(1,5)]
    E_NEG = [(0, 4), (4, 1), (4, 2), (4, 3),(5,4),(5,0)]
    return NV, E_POS, E_NEG


def generate_adjacency_matrix(V, E_POS, E_NEG):
    A = {(u, v): 0 for u, v in product(V, V)}
    for u, v in E_POS:
        A[(u, v)] = 1
        A[(v, u)] = 1
    for u, v in E_NEG:
        A[(u, v)] = -1
        A[(v, u)] = -1
    return A


def load_instance(path: str):
    print("Loading instance from file: {}".format(path))
    V = {}
    E_POS = []
    E_NEG = []
    with open(path, 'r') as f:
        line = f.readline()
        # if first line starts with '#', skip it and read the next line
        if line.startswith("#"):
            line = f.readline()
        #first line could have two formats:
        # 10 6
        if len(line.split()) == 2:
            NV, NE = map(int, line.split())
        # NV:10 NE:6
        else:
            NV, NE = map(int, line.split()[1::2])
        # each line has the format V1 V2 W
        for line in f:
            v1, v2, w = line.split()
            v1, v2, w = int(v1)-1, int(v2)-1, int(w)
            if w == 1:
                E_POS.append((v1, v2))
            elif w == -1:
                E_NEG.append((v1, v2))
            else:
                raise ValueError("w should be either 1 or -1")
            V[v1] = 1
            V[v2] = 1
        #print("Loaded instance with {} vertices and {} edges".format(len(V), len(E_POS) + len(E_NEG)))
    return NV, E_POS, E_NEG

def main():

    path = "instances"

    output_file = "output.csv"

    # if output file does not exist, create it and write the header
    if not os.path.exists(output_file):
        with open(output_file, 'w') as f:
            f.write("TimeStamp;Instance;OF;Gap;TimeToBest;TotalTime;Status\n")

    instances = os.listdir(path)

    # sort instances by name
    instances.sort()

    for instance in instances:
        n, e_pos, e_neg = load_instance(path + "/" + instance)
        A = generate_adjacency_matrix(range(0, n), e_pos, e_neg)
        of, arrangement, gap, TtB, time, status = solve_cyclic_min_max_sitting_arrangement(n, A)
        print("Instance: ", instance)
        with open(output_file, 'a') as f:
            f.write("{};{};{};{};{};{};{}\n".format(str(datetime.datetime.now()), instance, of, gap, TtB, time, status))
        out = """
            Result:
            \t OF: {}
            \t Gap: {}
            \t Time To Best: {}
            \t Time: {}
            \t Status: {}
        """.format(of, gap, TtB, time, status)
        print(out)
        print("\n\n\n")


class LastBestCallback:
    def __init__(self):
        self.last_best_value = float('inf')
        self.last_best_running_time = 0

    def callback(self, optimizer, cb_type):
        stats = optimizer.statistics
        obj = optimizer.model.objectives[0]
        # check that obj.value is a number
        try:
            if obj.value < self.last_best_value:
                self.last_best_running_time = stats.running_time
                self.last_best_value = obj.value
                print("New best value: ", self.last_best_value , " at time: ", self.last_best_running_time, "s.")
        except:
            pass


if __name__ == "__main__":
    main()



