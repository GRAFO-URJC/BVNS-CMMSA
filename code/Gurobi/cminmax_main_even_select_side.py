import datetime
import errno
import math
import multiprocessing
import os
from itertools import product

from gurobipy.gurobipy import Model, quicksum, GRB, min_, abs_

from drawer import drawer

class Even():
    def __init__(self,path,cores,timelimit,memLimit) -> None:
        self.path = path
        self.cores = cores
        self.timelimit = timelimit
        self.memLimit = memLimit
        self.best_obj = None
        self.best_time = 0

    def callback_function(self,model, where):
        if where == GRB.Callback.MIPSOL:
            # New incumbent solution found
            current_obj = model.cbGet(GRB.Callback.MIPSOL_OBJ)
            current_time = model.cbGet(GRB.Callback.RUNTIME)

            # Update if this is the best solution so far
            if (self.best_obj is None) or (current_obj < self.best_obj):  # For minimization
                self.best_obj = current_obj
                self.best_time = current_time
    def load_instance(self):
        print("Loading instance from file: {}".format(self.path))
        V = {}
        E_POS = []
        E_NEG = []
        with open(self.path, 'r') as f:
            line = f.readline()
            while "#" in line:
                line = f.readline()

            # first line could have two formats:
            # 10 6
            if len(line.split()) == 2:
                NV, NE = map(int, line.split())
            # NV:10 NE:6
            else:
                NV, NE = map(int, line.split()[1::2])
            # each line has the format V1 V2 W
            for line in f:
                v1, v2, w = line.split()
                v1, v2, w = int(v1), int(v2), int(w)
                if w == 1:
                    E_POS.append((v1, v2))
                elif w == -1:
                    E_NEG.append((v1, v2))
                else:
                    raise ValueError("w should be either 1 or -1")
                V[v1] = 1
                V[v2] = 1
            #print("Loaded instance with {} vertices and {} edges".format(len(V), len(E_POS) + len(E_NEG)))
        v = [i for i in range(1, NV + 1)]
        return v, E_POS, E_NEG


    def generate_adjacency_matrix(self,V, E_POS, E_NEG):
        A = {(u, v): 0 for u, v in product(V, V)}
        for u, v in E_POS:
            A[(u, v)] = 1
            A[(v, u)] = 1
        for u, v in E_NEG:
            A[(u, v)] = -1
            A[(v, u)] = -1
        return A



    def run(self):
        V, E_POS, E_NEG = self.load_instance()
        NUM_VERTICES = len(V)
        A = self.generate_adjacency_matrix(V, E_POS, E_NEG)
        m = Model("MinSA")
        #print("Generating model")

        #print("Generating variables")
        error = {}
        for u, v, w in product(V, V, V):
            if u != v and v != w and w != u:
                if A[(u, v)] < 0 and A[(u, w)] > 0:
                    error[(u, v, w)] = m.addVar(vtype=GRB.BINARY, name="error(%s,%s,%s)" % (u, v, w))

        before = {}
        for u, v in product(V, V):
            if u != v:
                before[u, v] = m.addVar(vtype=GRB.BINARY, name=f"{u}_before_{v}")
                # if u == 1 is the first vertex, then before[1,v] = 1
                if u == 1:
                    before[u, v].lb = 1
                    before[u, v].ub = 1

        position = {}
        for u in V:
            position[u] = m.addVar(vtype=GRB.INTEGER, name=f"pos{u}")

        distance = {}
        abs_distance = {}
        other_distance = {}
        cycle_distance = {}
        for u, v in product(V, V):
            if u != v:
                distance[u, v] = m.addVar(vtype=GRB.INTEGER, lb=-1 * GRB.INFINITY, name=f"distance{u}_{v}")
                abs_distance[u, v] = m.addVar(vtype=GRB.INTEGER, lb=0, name=f"abs_distance{u}_{v}")
                other_distance[u, v] = m.addVar(vtype=GRB.INTEGER, lb=0, name=f"other_distance{u}_{v}")
                cycle_distance[u, v] = m.addVar(vtype=GRB.INTEGER, name=f"cycle_distance_{u}_{v}")

        is_positive = {}
        is_lower_than_mid = {}
        aux_is_on_the_right = {}
        abs_aux_is_on_the_right = {}
        is_on_the_right = {}
        is_on_the_left = {}
        is_on_the_middle = {}
        for u, v in product(V, V):
            if u != v:
                is_positive[u, v] = m.addVar(vtype=GRB.BINARY, name=f"is_positive{u}_{v}")
                is_lower_than_mid[u, v] = m.addVar(vtype=GRB.BINARY, name=f"is_lower_than_mid{u}_{v}")
                aux_is_on_the_right[u, v] = m.addVar(vtype=GRB.INTEGER, lb=-1, ub=1, name=f"aux_is_on_the_right{u}_{v}")
                abs_aux_is_on_the_right[u, v] = m.addVar(vtype=GRB.INTEGER, lb=-1, ub=1, name=f"abs_aux_is_on_the_right{u}_{v}")
                is_on_the_right[u, v] = m.addVar(vtype=GRB.BINARY, name=f"is_on_the_right{u}_{v}")
                is_on_the_left[u, v] = m.addVar(vtype=GRB.BINARY, name=f"is_on_the_left{u}_{v}")
                is_on_the_middle[u, v] = m.addVar(vtype=GRB.BINARY, name=f"is_on_the_middle{u}_{v}")

        distance_left = {}
        distance_right = {}
        for u, v, in product(V, V):
            if u != v:
                distance_left[u, v] = m.addVar(vtype=GRB.INTEGER, name=f"distance_left{u}_{v}")
                distance_right[u, v] = m.addVar(vtype=GRB.INTEGER, name=f"distance_right{u}_{v}")

        # Calculate the objective function


        # Calculate the objective function which is going to be the maximum error
        # auxiliar variable to calculate the maximum error
        z = m.addVar(vtype=GRB.CONTINUOUS, name="Z")

        # Calculate the maximum error for each vertex. First we sum the errors for each vertex
        # and then we calculate the maximum
        m.addConstrs((z >= quicksum(error[u, v, w] for v, w in product(V, V) if A[(u, v)] < 0 and A[(u, w)] > 0)
                    for u in V), name="max_error")

        total_error = z

        # Set the objective function
        m.setObjective(total_error, GRB.MINIMIZE)

        #print("Generating constraints")

        # CONSTRAINT 1
        #print("Constraint 1: Order")
        m.addConstrs(
            (before[u, v] + before[v, u] == 1 for u, v in product(V, V) if
            u != v), name="order")

        #print("Constraint 2: Dicycle")
        m.addConstrs(
            (before[u, v] + before[v, w] + before[w, u] <= 2 for u, v, w in
            product(V, V, V) if
            u != v and v != w and w != u),
            name="order_dicycle")

        #print("Constraint 3: Position calculation")
        m.addConstrs((position[u] == quicksum(before[v, u] for v in V if v != u) for u in V), name="position")

        #print("Constraint 4: Distance calculation")
        m.addConstrs((distance[u, v] == position[v] - position[u] for u, v in product(V, V) if u != v), name="distance")

        #print("Constraint 5: Absolute distance calculation")
        m.addConstrs((abs_distance[u, v] == abs_(distance[u, v]) for u, v in product(V, V) if u != v), name="abs_distance")

        #print("Constraint 6: Other distance calculation")
        m.addConstrs((other_distance[u, v] == len(V) - abs_distance[u, v] for u, v in product(V, V) if u != v),
                    name="other_distance")

        #print("Constraint 7: Cycle distance calculation")
        m.addConstrs(
            (cycle_distance[u, v] == min_(abs_distance[u, v], other_distance[u, v]) for u, v in product(V, V) if u != v),
            name="cycle_distance")

        #print("Constraint 8: Is on the middle")
        m.addConstrs(
            (is_on_the_middle[u, v] == 1) >> (cycle_distance[u, v] >= (len(V) / 2)) for u, v in product(V, V) if u != v)

        m.addConstrs(
            (is_on_the_middle[u, v] == 0) >> (cycle_distance[u, v] <= (len(V) / 2 - 1)) for u, v in product(V, V) if u != v)

        #print("Constraint 8: Is negative")
        m.addConstrs((is_positive[u, v] == 1) >> (distance[u, v] >= 0) for u, v in product(V, V) if u != v)
        m.addConstrs((is_positive[u, v] == 0) >> (distance[u, v] <= 0) for u, v in product(V, V) if u != v)

        #print("Constraint 9: Is lower than mid")
        m.addConstrs((is_lower_than_mid[u, v] == 1) >> (abs_distance[u, v] <= len(V) / 2) for u, v in product(V, V) if u != v)
        m.addConstrs((is_lower_than_mid[u, v] == 0) >> (abs_distance[u, v] >= len(V) / 2) for u, v in product(V, V) if u != v)
        #
        #print("Constraint 10: Is on the right")
        # if is positive and is lower than the mid, is on the right
        # if is negative and is greater than the mid, is on the right
        # in other case, is on the left

        m.addConstrs(aux_is_on_the_right[u, v] == (is_positive[u, v] - is_lower_than_mid[u, v])
                    for u, v in product(V, V) if u != v)

        m.addConstrs((abs_aux_is_on_the_right[u, v] == abs_(aux_is_on_the_right[u, v])) for u, v in product(V, V) if u != v)

        m.addConstrs(
            (is_on_the_right[u, v] >= abs_aux_is_on_the_right[u, v] * (1 - is_on_the_middle[u, v]))
            for u, v in product(V, V) if u != v)

        m.addConstrs(
            (is_on_the_left[u, v] >= (1 - abs_aux_is_on_the_right[u, v]) * (1 - is_on_the_middle[u, v]))
            for u, v in product(V, V) if u != v)

        m.addConstrs(is_on_the_right[u, v] + is_on_the_left[u, v] >= is_on_the_middle[u,v] for u, v in product(V, V) if u != v)

        #print("Constraint 11: Is on the left")

        #print("Constraint 11: Distance right")
        m.addConstrs((distance_right[u, v] == cycle_distance[u, v] * is_on_the_right[u, v]) for u, v in product(V, V) if u != v)

        #print("Constraint 12: Distance left")
        m.addConstrs(
            (distance_left[u, v] == cycle_distance[u, v] * is_on_the_left[u, v]) for u, v in product(V, V) if u != v)

        #print("Constraint 13: Error left")
        m.addConstrs(((distance_left[u, v] * is_on_the_left[u, w]
                    - distance_left[u, w] * is_on_the_left[u, v]
                    + error[u, v, w] * NUM_VERTICES >= 0)
                    for u, v, w in product(V, V, V) if A[(u, v)] < 0 and A[(u, w)] > 0), name="error_left")

        #print("Constraint 14: Error right")
        m.addConstrs(((distance_right[u, v] * is_on_the_right[u, w]
                    - distance_right[u, w] * is_on_the_right[u, v]
                    + error[u, v, w] * NUM_VERTICES >= 0)
                    for u, v, w in product(V, V, V) if A[(u, v)] < 0 and A[(u, w)] > 0), name="error_right")

        #print("Solving model")

        # number of threads (half of the cores)
        cores = multiprocessing.cpu_count()
        m.setParam("Threads", self.cores)

        # set the time limit
        m.setParam("TimeLimit", self.timelimit)

        # set the gap limit
        m.setParam("MIPGap", 0.001)

        # set the log level
        m.setParam("OutputFlag",1)
        m.setParam("memLimit",self.memLimit)

        def callback(model, where):
            if where == GRB.Callback.MIPSOL:
                pos = {}
                for u in V:
                    pos[u] = model.cbGetSolution(position[u])
                score = model.cbGet(GRB.Callback.MIPSOL_OBJ)
                drawer(E_POS, E_NEG, [u for u in sorted(V, key=lambda x: pos[x])], score)


        m.optimize(self.callback_function)
        # write the model
        m.write("model.lp")

        solution = {}

        solution["instance"] =self.path 

        if m.status == GRB.Status.OPTIMAL or (m.status == GRB.Status.TIME_LIMIT and m.objVal < float("inf")):

            print("Optimal solution found with objective: %g" % m.objVal)
            solution["objective"] = str(m.objVal)
            print("Time: %g" % m.Runtime)
            solution["time"] = str(int(m.Runtime))
            solution["ttb"] = f"{self.best_time:.2f}"
            print("TTB: "+ str(solution["ttb"]))
            print("Gap: %g" % m.MIPGap)
            solution["gap"] = str(m.MIPGap)
            solution["optimal"] = str(m.status==GRB.Status.OPTIMAL)
            # #print variables
            # for v in m.getVars():
                # print('%s %g' % (v.varName, v.x))

            # calculate the position of each vertex
            pos = {}
            for u in V:
                pos[u] = len(V) - 1
                for v in V:
                    if u != v:
                        pos[u] -= before[u, v].X
            # #printed sorted by position
            # for u in sorted(V, key=lambda x: pos[x]):
            #     #print(u, end=" ")

            # save the solution ordered by position as a string
            solution["order"] = " ".join([str(u) for u in sorted(V, key=lambda x: pos[x])])

            #drawer(E_POS, E_NEG, [u for u in sorted(V, key=lambda x: pos[x])], m.objVal, self.path)
            self.solution = solution
            with open("salida.csv","a") as f:
                f.write(solution["instance"]+";"+solution["objective"]+";"+solution["ttb"]+";"+solution["time"]+";"+solution["gap"]+";"+solution["optimal"]+"\n")

        else:
            #print("No solution found")
            solution["objective"] = -1









