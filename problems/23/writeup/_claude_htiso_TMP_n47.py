import sys, time
from collections import Counter
from _bdef_construct import Cn, mycielski
from _codex_k2t_switch_probe import adj_from_edges
from _h import Bconn
from _codex_ht_isolation_gate import scan_selected_cut


def build47():
    E5 = Cn(5)
    n11, E11 = mycielski(5, E5)
    n23, E23 = mycielski(n11, E11)
    n47, E47 = mycielski(n23, E23)
    return n47, E47


def maxcut_ilp(n, edges):
    import pulp
    prob = pulp.LpProblem("maxcut", pulp.LpMaximize)
    x = [pulp.LpVariable("x%d" % i, cat="Binary") for i in range(n)]
    # y_e = 1 iff edge is cut; y_e <= x_u + x_v, y_e <= 2 - x_u - x_v
    ys = []
    for k, (u, v) in enumerate(edges):
        y = pulp.LpVariable("y%d" % k, lowBound=0, upBound=1)
        prob += y <= x[u] + x[v]
        prob += y <= 2 - x[u] - x[v]
        ys.append(y)
    prob += pulp.lpSum(ys)
    x[0].setInitialValue(0); x[0].fixValue()  # break symmetry
    solver = pulp.PULP_CBC_CMD(msg=1, threads=8, timeLimit=1200)
    prob.solve(solver)
    status = pulp.LpStatus[prob.status]
    side = [int(round(pulp.value(x[i]))) for i in range(n)]
    cutval = sum(1 for (u, v) in edges if side[u] != side[v])
    return status, side, cutval, int(round(pulp.value(prob.objective)))


if __name__ == "__main__":
    n, edges = build47()
    adj = adj_from_edges(n, edges)
    t0 = time.time()
    status, side, cutval, obj = maxcut_ilp(n, edges)
    print("ILP status:", status, "obj_bound:", obj, "cutval:", cutval,
          "time %.1fs" % (time.time() - t0))
    sys.stdout.flush()
    # Only proceed if solver proved optimality
    if status != "Optimal":
        print("NON-OPTIMAL — abort single-side run"); sys.exit(0)
    # verify Bconn
    print("Bconn on chosen side:", Bconn(n, adj, side))
    sys.stdout.flush()
    max_add = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    cap = int(sys.argv[2]) if len(sys.argv) > 2 else 3_000_000
    acc = {"tested": 0, "no_switch": 0, "bad_terminal": 0,
           "status": Counter(), "stats": Counter(), "first": None}
    scan_selected_cut("MycMycGrotzsch_N47_1side", n, adj, side, acc, max_add, True, cap)
    print("=== N47 one maxcut side  max_add=%d cap=%d ===" % (max_add, cap))
    print("TESTED", acc["tested"], "NO_SWITCH", acc["no_switch"], "BAD_TERMINAL", acc["bad_terminal"])
    print("STATUS", dict(acc["status"]))
    print("STATS", dict(acc["stats"]))
    print("FIRST", acc["first"])
