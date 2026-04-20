import math
import os
from itertools import product

from gurobipy.gurobipy import Model, GRB, quicksum

class Odd:
    def __init__(self,path,cores,timelimit,memLimit) -> None:
        self.path = path

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
        M = 2 * NUM_VERTICES
        floor_half = NUM_VERTICES // 2
        ceil_half = math.ceil(NUM_VERTICES / 2)

        # GENERATE A LIST OF DISTANCES
        D = [d for d in range(1, math.floor(NUM_VERTICES / 2) + 1)]

        # GENERATE ADJACENCY MATRIX WITH WEIGHTS 0,+1,-1
        A = self.generate_adjacency_matrix(V, E_POS, E_NEG)

        # CREATE MODEL
        m = Model("MinSA")
        print("Generating model")

        print("Generating variables")
        error = {}
        for u, v, w in product(V, V, V):
            if u != v and v != w and w != u:
                if A[(u, v)] < 0 and A[(u, w)] > 0:
                    error[(u, v, w)] = m.addVar(vtype=GRB.BINARY, name="error(%s,%s,%s)" % (u, v, w))

        before = {}
        for u, v in product(V, V):
            if u != v:
                before[u, v] = m.addVar(vtype=GRB.BINARY, name=f"{u}_before_{v}")

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
        is_on_the_right = {}
        t_right = {}
        for u, v in product(V, V):
            if u != v:
                is_positive[u, v] = m.addVar(vtype=GRB.BINARY, name=f"is_positive{u}_{v}")
                is_lower_than_mid[u, v] = m.addVar(vtype=GRB.BINARY, name=f"is_lower_than_mid{u}_{v}")
                aux_is_on_the_right[u, v] = m.addVar(vtype=GRB.INTEGER, lb=-1, ub=1, name=f"aux_is_on_the_right{u}_{v}")
                is_on_the_right[u, v] = m.addVar(vtype=GRB.BINARY, name=f"is_on_the_right{u}_{v}")
                t_right[u, v] = m.addVar(vtype=GRB.BINARY, name=f"t_right{u}_{v}")

        distance_left = {}
        distance_right = {}
        for u, v, in product(V, V):
            if u != v:
                distance_left[u, v] = m.addVar(vtype=GRB.INTEGER, lb=0, name=f"distance_left{u}_{v}")
                distance_right[u, v] = m.addVar(vtype=GRB.INTEGER, lb=0, name=f"distance_right{u}_{v}")

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

        print("Generating constraints")

        # CONSTRAINT 1
        print("Constraint 1: Order")
        m.addConstrs(
            (before[u, v] + before[v, u] == 1 for u, v in product(V, V) if
            u != v), name="order")

        print("Constraint 2: Dicycle")
        m.addConstrs(
            (before[u, v] + before[v, w] + before[w, u] <= 2 for u, v, w in
            product(V, V, V) if
            u != v and v != w and w != u),
            name="order_dicycle")

        print("Constraint 3: Position calculation")
        m.addConstrs((position[u] == quicksum(before[v, u] for v in V if v != u) for u in V), name="position")

        print("Constraint 4: Distance calculation")
        m.addConstrs((distance[u, v] == position[v] - position[u] for u, v in product(V, V) if u != v), name="distance")

        print("Constraint 8: Is positive (big-M) - must come before constraint 5")
        m.addConstrs((distance[u, v] >= -M * (1 - is_positive[u, v])
                      for u, v in product(V, V) if u != v), name="is_pos_lb")
        m.addConstrs((distance[u, v] <= M * is_positive[u, v]
                      for u, v in product(V, V) if u != v), name="is_pos_ub")

        print("Constraint 5: Absolute distance calculation (big-M via is_positive)")
        m.addConstrs((abs_distance[u, v] >= distance[u, v]
                      for u, v in product(V, V) if u != v), name="abs_dist_ge_dist")
        m.addConstrs((abs_distance[u, v] >= -distance[u, v]
                      for u, v in product(V, V) if u != v), name="abs_dist_ge_neg_dist")
        m.addConstrs((abs_distance[u, v] <= distance[u, v] + M * (1 - is_positive[u, v])
                      for u, v in product(V, V) if u != v), name="abs_dist_le_dist_neg")
        m.addConstrs((abs_distance[u, v] <= -distance[u, v] + M * is_positive[u, v]
                      for u, v in product(V, V) if u != v), name="abs_dist_le_neg_dist_pos")

        print("Constraint 6: Other distance calculation")
        m.addConstrs((other_distance[u, v] == len(V) - abs_distance[u, v] for u, v in product(V, V) if u != v),
                    name="other_distance")

        print("Constraint 9: Is lower than mid (big-M) - must come before constraint 7")
        m.addConstrs((abs_distance[u, v] <= floor_half + M * (1 - is_lower_than_mid[u, v])
                      for u, v in product(V, V) if u != v), name="is_lt_mid_ub")
        m.addConstrs((abs_distance[u, v] >= ceil_half - M * is_lower_than_mid[u, v]
                      for u, v in product(V, V) if u != v), name="is_lt_mid_lb")

        print("Constraint 7: Cycle distance calculation (big-M via is_lower_than_mid)")
        m.addConstrs((cycle_distance[u, v] <= abs_distance[u, v]
                      for u, v in product(V, V) if u != v), name="cycle_dist_le_abs")
        m.addConstrs((cycle_distance[u, v] <= other_distance[u, v]
                      for u, v in product(V, V) if u != v), name="cycle_dist_le_other")
        m.addConstrs((cycle_distance[u, v] >= abs_distance[u, v] - M * (1 - is_lower_than_mid[u, v])
                      for u, v in product(V, V) if u != v), name="cycle_dist_ge_abs")
        m.addConstrs((cycle_distance[u, v] >= other_distance[u, v] - M * is_lower_than_mid[u, v]
                      for u, v in product(V, V) if u != v), name="cycle_dist_ge_other")

        print("Constraint 10: Is on the right (XOR linearization)")
        # aux_is_on_the_right = is_positive - is_lower_than_mid (in {-1,0,1})
        m.addConstrs((aux_is_on_the_right[u, v] == is_positive[u, v] - is_lower_than_mid[u, v]
                    for u, v in product(V, V) if u != v), name="aux_right")

        # t_right[u,v] = is_positive[u,v] AND is_lower_than_mid[u,v]
        m.addConstrs((t_right[u, v] >= is_positive[u, v] + is_lower_than_mid[u, v] - 1
                      for u, v in product(V, V) if u != v), name="t_right_lb")
        m.addConstrs((t_right[u, v] <= is_positive[u, v]
                      for u, v in product(V, V) if u != v), name="t_right_le_pos")
        m.addConstrs((t_right[u, v] <= is_lower_than_mid[u, v]
                      for u, v in product(V, V) if u != v), name="t_right_le_ltm")

        # is_on_the_right = |aux_is_on_the_right| = is_positive XOR is_lower_than_mid
        m.addConstrs((is_on_the_right[u, v] == is_positive[u, v] + is_lower_than_mid[u, v] - 2 * t_right[u, v]
                    for u, v in product(V, V) if u != v), name="is_right_xor")

        UB = floor_half  # cycle_distance in [0, floor_half]

        print("Constraint 11: Distance right (McCormick linearization of cycle_dist * is_right)")
        m.addConstrs((distance_right[u, v] >= cycle_distance[u, v] - UB * (1 - is_on_the_right[u, v])
                      for u, v in product(V, V) if u != v), name="dr_ge_cd")
        m.addConstrs((distance_right[u, v] <= cycle_distance[u, v]
                      for u, v in product(V, V) if u != v), name="dr_le_cd")
        m.addConstrs((distance_right[u, v] <= UB * is_on_the_right[u, v]
                      for u, v in product(V, V) if u != v), name="dr_le_UB_ir")

        print("Constraint 12: Distance left (McCormick linearization of cycle_dist * (1-is_right))")
        m.addConstrs((distance_left[u, v] >= cycle_distance[u, v] - UB * is_on_the_right[u, v]
                      for u, v in product(V, V) if u != v), name="dl_ge_cd")
        m.addConstrs((distance_left[u, v] <= cycle_distance[u, v]
                      for u, v in product(V, V) if u != v), name="dl_le_cd")
        m.addConstrs((distance_left[u, v] <= UB * (1 - is_on_the_right[u, v])
                      for u, v in product(V, V) if u != v), name="dl_le_UB_ir")

        print("Introducing auxiliary variables for products in constraints 13-14")
        # p13a[u,v,w] = distance_left[u,v] * (1 - is_right[u,w])
        # p13b[u,v,w] = distance_left[u,w] * (1 - is_right[u,v])
        # p14a[u,v,w] = distance_right[u,v] * is_right[u,w]
        # p14b[u,v,w] = distance_right[u,w] * is_right[u,v]
        p13a = {}; p13b = {}; p14a = {}; p14b = {}
        for u, v, w in product(V, V, V):
            if u != v and v != w and u != w and A[(u, v)] < 0 and A[(u, w)] > 0:
                p13a[u, v, w] = m.addVar(vtype=GRB.INTEGER, lb=0, name=f"p13a_{u}_{v}_{w}")
                p13b[u, v, w] = m.addVar(vtype=GRB.INTEGER, lb=0, name=f"p13b_{u}_{v}_{w}")
                p14a[u, v, w] = m.addVar(vtype=GRB.INTEGER, lb=0, name=f"p14a_{u}_{v}_{w}")
                p14b[u, v, w] = m.addVar(vtype=GRB.INTEGER, lb=0, name=f"p14b_{u}_{v}_{w}")

        valid = [(u, v, w) for u, v, w in product(V, V, V)
                 if u != v and v != w and u != w and A[(u, v)] < 0 and A[(u, w)] > 0]

        # Linearize p13a = dl[u,v] * (1 - is_right[u,w])
        m.addConstrs((p13a[u,v,w] >= distance_left[u,v] - UB * is_on_the_right[u,w]
                      for u,v,w in valid), name="p13a_lb")
        m.addConstrs((p13a[u,v,w] <= distance_left[u,v]
                      for u,v,w in valid), name="p13a_le_dl")
        m.addConstrs((p13a[u,v,w] <= UB * (1 - is_on_the_right[u,w])
                      for u,v,w in valid), name="p13a_le_UB")

        # Linearize p13b = dl[u,w] * (1 - is_right[u,v])
        m.addConstrs((p13b[u,v,w] >= distance_left[u,w] - UB * is_on_the_right[u,v]
                      for u,v,w in valid), name="p13b_lb")
        m.addConstrs((p13b[u,v,w] <= distance_left[u,w]
                      for u,v,w in valid), name="p13b_le_dl")
        m.addConstrs((p13b[u,v,w] <= UB * (1 - is_on_the_right[u,v])
                      for u,v,w in valid), name="p13b_le_UB")

        # Linearize p14a = dr[u,v] * is_right[u,w]
        m.addConstrs((p14a[u,v,w] >= distance_right[u,v] - UB * (1 - is_on_the_right[u,w])
                      for u,v,w in valid), name="p14a_lb")
        m.addConstrs((p14a[u,v,w] <= distance_right[u,v]
                      for u,v,w in valid), name="p14a_le_dr")
        m.addConstrs((p14a[u,v,w] <= UB * is_on_the_right[u,w]
                      for u,v,w in valid), name="p14a_le_UB")

        # Linearize p14b = dr[u,w] * is_right[u,v]
        m.addConstrs((p14b[u,v,w] >= distance_right[u,w] - UB * (1 - is_on_the_right[u,v])
                      for u,v,w in valid), name="p14b_lb")
        m.addConstrs((p14b[u,v,w] <= distance_right[u,w]
                      for u,v,w in valid), name="p14b_le_dr")
        m.addConstrs((p14b[u,v,w] <= UB * is_on_the_right[u,v]
                      for u,v,w in valid), name="p14b_le_UB")

        print("Constraint 13: Error left")
        m.addConstrs((p13a[u,v,w] - p13b[u,v,w] + error[u,v,w] * NUM_VERTICES >= 0
                      for u,v,w in valid), name="error_left")

        print("Constraint 14: Error right")
        m.addConstrs((p14a[u,v,w] - p14b[u,v,w] + error[u,v,w] * NUM_VERTICES >= 0
                      for u,v,w in valid), name="error_right")

        # write MPS for CPLEX (one file per instance)
        instance_name = os.path.splitext(os.path.basename(self.path))[0]
        m.write(f"{instance_name}.mps")
        print(f"Model written to {instance_name}.mps")
