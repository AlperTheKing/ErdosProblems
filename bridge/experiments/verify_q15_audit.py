#!/usr/bin/env python3
"""
AUDIT + EXECUTE GPT Q15 route (max-cut-colored switching + C5-defect cleanup).
(A) SW1: for a MAX cut A⊔B and every root v in A, with P=N(v)∩A, Q=N(v)∩B, R=A∖(P∪{v}), T=B∖Q:
        |P| + e(P,R) + e(Q,T) <= e(R,T)    (must hold; triangle-free => e(P,Q)=0).
(B) C5-cleanup: beta(G) <= (e + 4 d_5)/5, where d_5 = min over psi:V->Z5 of #{uv in E: psi(u)-psi(v) != +-1 mod5}.
(C) C5-target feasibility: is d_5(G) <= (N^2/5 - e)/4 on band triangle-free graphs?  (=> beta<=n^2)
beta = e - MaxCut (exact via CP-SAT). d_5 exact via CP-SAT. All small/medium graphs.
"""
import itertools, random
from ortools.sat.python import cp_model
random.seed(15)

def adj(N, E):
    A = [set() for _ in range(N)]
    for u, v in E: A[u].add(v); A[v].add(u)
    return A
def edges(N, A): return [(u, v) for u in range(N) for v in A[u] if v > u]

def maxcut(N, A, tl=30):
    E = edges(N, A); m = cp_model.CpModel()
    x = [m.NewBoolVar(f"x{v}") for v in range(N)]
    cut = []
    for (u, v) in E:
        d = m.NewBoolVar(f"c{u}_{v}"); m.Add(d <= x[u] + x[v]); m.Add(d <= 2 - x[u] - x[v])
        cut.append(d)
    m.Maximize(sum(cut))
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = tl; s.parameters.num_search_workers = 8
    s.Solve(m)
    col = [int(s.Value(x[v])) for v in range(N)]
    return len(E) - int(s.ObjectiveValue()), col   # beta, coloring

def d5(N, A, tl=30):
    E = edges(N, A); m = cp_model.CpModel()
    c = [m.NewIntVar(0, 4, f"p{v}") for v in range(N)]
    bad = []
    # edge good iff (c_u - c_v) mod 5 in {1,4}; bad otherwise
    good_pairs = [(a, b) for a in range(5) for b in range(5) if (a - b) % 5 in (1, 4)]
    for (u, v) in E:
        g = m.NewBoolVar(f"g{u}_{v}")
        m.AddAllowedAssignments([c[u], c[v]], good_pairs).OnlyEnforceIf(g)
        m.AddForbiddenAssignments([c[u], c[v]], good_pairs).OnlyEnforceIf(g.Not())
        bad.append(g.Not())
    m.Minimize(sum(bad))
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = tl; s.parameters.num_search_workers = 8
    s.Solve(m)
    return int(s.ObjectiveValue())

def check_SW1(N, A, col):
    E = edges(N, A)
    def e_between(X, Y): return sum(1 for u in X for w in A[u] if w in Y)
    viol = 0; worst = None
    side = [set(v for v in range(N) if col[v] == c) for c in (0, 1)]
    for v in range(N):
        Av = side[col[v]]; Bv = side[1 - col[v]]
        P = (A[v] & Av); Q = (A[v] & Bv)
        R = Av - P - {v}; T = Bv - Q
        lhs = len(P) + e_between(P, R) + e_between(Q, T)
        rhs = e_between(R, T)
        if lhs > rhs: viol += 1; worst = (v, lhs, rhs)
    return viol, worst

def report(tag, N, A):
    E = edges(N, A); e = len(E); x = e/(N*N)
    beta, col = maxcut(N, A)
    dd = d5(N, A)
    bound = (e + 4*dd)/5.0
    target = (N*N/5.0 - e)/4.0
    sw_viol, worst = check_SW1(N, A, col)
    inband = 0.1243 <= x <= 0.16
    print(f"  {tag:14s} N={N:3d} e={e:4d} x={x:.4f} band={int(inband)} | beta={beta:4d} "
          f"(e+4d5)/5={bound:7.1f} beta<=bnd={int(beta<=bound+1e-9)} | d5={dd:3d} target={target:6.1f} "
          f"d5<=target={int(dd<=target+1e-9)} | SW1 viol={sw_viol}")
    return beta <= bound+1e-9, (dd <= target+1e-9), sw_viol == 0

def C5n(n):
    parts = [list(range(i*n, i*n+n)) for i in range(5)]
    E = [(u, v) for p in range(5) for u in parts[p] for v in parts[(p+1) % 5]]
    return 5*n, adj(5*n, E)
def myc(N, A):
    E = edges(N, A); z = 2*N; E2 = list(E)
    for u, v in E: E2.append((u+N, v)); E2.append((u, v+N))
    for v in range(N): E2.append((z, v+N))
    return 2*N+1, adj(2*N+1, E2)
def kbip(a, b): return a+b, adj(a+b, [(u, a+w) for u in range(a) for w in range(b)])
def rand_band(N, lo, hi):
    for _ in range(300):
        A = [set() for _ in range(N)]; ps = [(u, v) for u in range(N) for v in range(u+1, N)]
        random.shuffle(ps); cnt = 0
        tgt = random.randint(lo, hi)
        for u, v in ps:
            if cnt >= tgt: break
            if A[u] & A[v]: continue
            A[u].add(v); A[v].add(u); cnt += 1
        if lo <= cnt <= hi: return N, A
    return None

if __name__ == "__main__":
    print("Q15 AUDIT: (A) SW1 holds; (B) beta<=(e+4d5)/5; (C) d5<=(N^2/5-e)/4 on band graphs?")
    b_ok = t_ok = s_ok = True
    for n in (2, 3):
        N, A = C5n(n); r = report(f"C5[{n}]", N, A); b_ok &= r[0]; s_ok &= r[2]
    N, A = C5n(2); N2, A2 = myc(N, A); N3, A3 = myc(N2, A2)
    r = report("M(M(C5))", N3, A3); b_ok &= r[0]; s_ok &= r[2]
    for (a, b) in [(8, 32), (16, 64)]:
        N, A = kbip(a, b); r = report(f"K_{a},{b}", N, A); b_ok &= r[0]; s_ok &= r[2]
    print("  -- random in-band --")
    for N in (12, 15, 18):
        lo, hi = int(0.1243*N*N)+1, int(0.16*N*N)
        for _ in range(3):
            rr = rand_band(N, lo, hi)
            if rr:
                r = report(f"rand{N}", rr[0], rr[1]); b_ok &= r[0]; t_ok &= r[1]; s_ok &= r[2]
    print(f"\n  (B) beta<=(e+4d5)/5 on ALL: {b_ok}")
    print(f"  (C) d5<=(N^2/5-e)/4 on ALL band: {t_ok}  <-- if True, C5-cleanup is a viable route")
    print(f"  (A) SW1 holds (0 viol) on ALL: {s_ok}")
    print("DONE")
