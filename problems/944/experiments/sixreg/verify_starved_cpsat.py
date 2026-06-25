# Independent CP-SAT cross-check of robust_fk2 verdicts on H* (2026-06-12).
# - re-verify a sample of STARVED pairs (expect INFEASIBLE)
# - re-verify a served control (expect FEASIBLE)
# - DECIDE the 26 capped (gamma, 11) pairs
from ortools.sat.python import cp_model

reps = []
for a in range(5):
    for b in range(5):
        for c in range(5):
            if a == b == c == 0:
                continue
            if (a and a != 1) or (not a and b and b != 1) or (not a and not b and c != 1):
                continue
            reps.append((a, b, c))
adj = {x: set() for x in range(62)}
for i in range(31):
    for j in range(31):
        if sum(reps[i][t] * reps[j][t] for t in range(3)) % 5 == 0:
            adj[i].add(31 + j)
            adj[31 + j].add(i)
for a, b in [(0, 32), (7, 41), (15, 33)]:
    adj[a].discard(b)
    adj[b].discard(a)
ANCH = sorted(x for x in range(62) if len(adj[x]) == 5)
assert ANCH == [0, 7, 15, 32, 33, 41]


def decide(gamma, v):
    """exists proper 3-col of H*-v, exactly (2,2,2) on N(v), anchor s != gamma_s?"""
    m = cp_model.CpModel()
    x = {u: m.NewIntVar(0, 2, f"x{u}") for u in range(62) if u != v}
    for u in range(62):
        if u == v:
            continue
        for w in adj[u]:
            if w != v and w > u:
                m.Add(x[u] != x[w])
    g = gamma
    for s in range(6):
        if ANCH[s] != v:
            m.Add(x[ANCH[s]] != g % 3)
        g //= 3
    for c in range(3):
        bs = []
        for w in adj[v]:
            b = m.NewBoolVar(f"b{w}_{c}")
            m.Add(x[w] == c).OnlyEnforceIf(b)
            m.Add(x[w] != c).OnlyEnforceIf(b.Not())
            bs.append(b)
        m.Add(sum(bs) == 2)
    sol = cp_model.CpSolver()
    sol.parameters.max_time_in_seconds = 120
    sol.parameters.num_search_workers = 8
    r = sol.Solve(m)
    return {cp_model.OPTIMAL: "FEASIBLE", cp_model.FEASIBLE: "FEASIBLE",
            cp_model.INFEASIBLE: "INFEASIBLE"}.get(r, "UNKNOWN")


print("== starved sample (expect INFEASIBLE) ==")
for g, v in [(5, 31), (5, 60), (15, 43), (135, 2), (161, 21), (140, 11)]:
    print(f"  gamma={g} v={v}: {decide(g, v)}")

print("== served control (expect FEASIBLE) ==")
for g, v in [(0, 1), (1, 31), (5, 1), (135, 31)]:
    print(f"  gamma={g} v={v}: {decide(g, v)}")

print("== capped (gamma,11) decisions ==")
capped = [14, 40, 50, 49, 13, 43, 52, 16, 17, 41, 44, 53, 95, 94, 103, 97, 98,
          104, 107, 106, 135, 137, 148, 153, 155, 161]
res = {}
for g in capped:
    res[g] = decide(g, 11)
    print(f"  gamma={g} v=11: {res[g]}")
from collections import Counter
print("capped summary:", dict(Counter(res.values())))
