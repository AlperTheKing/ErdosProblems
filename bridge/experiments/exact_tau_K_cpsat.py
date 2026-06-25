#!/usr/bin/env python3
"""
RUNG 1: EXACT tau_K via CP-SAT (Codex-style, with optimality proof), to validate local-search and
pin the exact extremal of R(F)=tau_K(F)/RHS(F).

tau_K(G) = min over phi:V->{0..15} (Clebsch vertices = even subsets of [5]) of sum over edges of
cost(phi(u),phi(v)), cost(i,j)=(4-popcount(L_i ^ L_j))/2 in {0,1,2}. Symmetry-broken by fixing phi(v0)=0.
"""
import sys
from ortools.sat.python import cp_model

labels = [m for m in range(32) if bin(m).count('1') % 2 == 0]   # 16 Clebsch vertices
def cost(i, j): return (4 - bin(labels[i] ^ labels[j]).count('1')) // 2

def exact_tau_K(N, E, time_limit=60.0, workers=8):
    m = cp_model.CpModel()
    c = [m.NewIntVar(0, 15, f"c{v}") for v in range(N)]
    if N: m.Add(c[0] == 0)                                       # symmetry break (vertex-transitive)
    # cost table per (i,j)
    tuples = [(i, j, cost(i, j)) for i in range(16) for j in range(16)]
    tcost = []
    for (u, v) in E:
        t = m.NewIntVar(0, 2, f"t_{u}_{v}")
        m.AddAllowedAssignments([c[u], c[v], t], tuples)
        tcost.append(t)
    m.Minimize(sum(tcost))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = time_limit
    s.parameters.num_search_workers = workers
    st = s.Solve(m)
    status = {cp_model.OPTIMAL: "OPTIMAL", cp_model.FEASIBLE: "FEASIBLE"}.get(st, str(st))
    return int(s.ObjectiveValue()), status, s.BestObjectiveBound

def adj(N, E):
    A = [set() for _ in range(N)]
    for u, v in E: A[u].add(v); A[v].add(u)
    return A
def C5(): return 5, [(i, (i+1) % 5) for i in range(5)]
def mycielskian(N, E):
    z = 2*N; E2 = list(E)
    for u, v in E: E2.append((u+N, v)); E2.append((u, v+N))
    for v in range(N): E2.append((z, v+N))
    return 2*N+1, E2
def dedup(E): return sorted({(min(u,v),max(u,v)) for u,v in E})

def report(tag, N, E):
    E = dedup(E); e = len(E); rhs = (N*N/5.0 - e)/2.0; x = e/(N*N)
    tk, st, bnd = exact_tau_K(N, E)
    ratio = tk/rhs if rhs > 0 else float('inf')
    band = 0.1243 <= x <= 0.16
    flag = "  <<< CF COUNTEREXAMPLE!!" if (tk > rhs + 1e-9 and band) else ""
    print(f"  {tag:20s} N={N:3d} e={e:4d} x={x:.4f} band={int(band)} EXACT tau_K={tk:3d} ({st}) "
          f"RHS={rhs:6.1f} R={ratio:.4f}{flag}", flush=True)
    return tk, st, ratio

if __name__ == "__main__":
    print("RUNG 1 — EXACT tau_K (CP-SAT) on Mycielskian extremals:")
    n, e = C5(); report("C5", n, e)
    n2, e2 = mycielskian(n, e); report("M(C5)=Grötzsch", n2, e2)
    n3, e3 = mycielskian(n2, e2); report("M(M(C5)) 23v χ5", n3, e3)
    # blow-up invariance of EXACT tau_K
    def blow(N, E, k): return N*k, [(a*k+x, b*k+y) for (a,b) in dedup(E) for x in range(k) for y in range(k)]
    nb, eb = blow(n3, e3, 2); report("M(M(C5))[2]", nb, eb)
    print("DONE")
