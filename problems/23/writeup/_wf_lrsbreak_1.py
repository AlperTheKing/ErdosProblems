"""ADVERSARIAL BREAKER #1 for the LRS certificate family (Erdos #23).

Family: DENSE-CHORD long paths. Take a path 0..L; add MANY even-gap bad chords
(monochromatic under the parity 2-coloring => even-distance endpoints), as many as
triangle-free allows; optionally add 'detour ballast' (extra parallel B-edges) to make
the parity coloring a GLOBAL-max cut. Push |M| up. CP-SAT max-verify each candidate.
For every candidate that is a CP-SAT-verified triangle-free connected-B GLOBAL-max cut,
compute (exact Fraction):
  T(v)=load, Gamma=sum ell^2, |M|=beta, N=n.
Test ALL FOUR forms:
  B2:       max_v T(v) <= 2N
  PATH-LRS: for every bad f and every shortest geodesic P: (1/ell_f) sum_{v in P} T(v) + |M| <= N + N^2/25
  ROW-LRS:  for every bad f: A_f + |M| <= N + N^2/25, A_f = sum_v p_f(v) T(v)/ell_f
  LRS:      sum_v T^2 <= Gamma*(N + N^2/25 - |M|)
A breaker counts ONLY when CP-SAT proves the parity cut is THE global max (cut==bound).

Run from E:/Projects/ErdosProblems/problems/23/writeup.
"""
from fractions import Fraction as F
from collections import deque
import itertools
from _satzmu_conn import struct_for_side
from _h import Bconn
from ortools.sat.python import cp_model


# ---------------- graph utils ----------------
def adjof(n, E):
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b); adj[b].add(a)
    return adj

def trifree(n, adj):
    for u in range(n):
        for v in adj[u]:
            if v > u and (adj[u] & adj[v]):
                return False
    return True

def cutsize(n, adj, s):
    return sum(1 for u in range(n) for v in adj[u] if v > u and s[u] != s[v])

def cpmax(n, edges, tlimit=120):
    m = cp_model.CpModel()
    x = [m.NewBoolVar("x%d" % i) for i in range(n)]
    t = []
    for a, b in edges:
        z = m.NewBoolVar("e%d_%d" % (a, b))
        m.AddBoolXOr([x[a], x[b], z.Not()])
        t.append(z)
    m.Maximize(sum(t))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = tlimit
    s.parameters.num_search_workers = 16
    st = s.Solve(m)
    return int(round(s.ObjectiveValue())), int(round(s.BestObjectiveBound())), st


# ---------------- LRS family tester ----------------
def test_forms(n, adj, side):
    """Return dict of all four forms' exact slacks, or None if struct fails."""
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    N = F(n)
    beta = F(len(M))
    Gamma = sum(F(ell[f]) ** 2 for f in M)
    RHS = N + N * N / 25  # N + N^2/25

    # B2
    maxT = max(T) if T else F(0)
    b2_slack = 2 * N - maxT  # >=0 means holds

    # PATH-LRS: per f, per geodesic path P
    path_worst = None  # smallest slack
    for f in M:
        lf = F(ell[f])
        for P in cyc[f]:
            A = sum(T[v] for v in P) / lf
            slack = RHS - (A + beta)
            if path_worst is None or slack < path_worst[0]:
                path_worst = (slack, f, tuple(P), A)

    # ROW-LRS: per f, A_f = sum_v p_f(v) T(v)/ell_f
    # p_f(v) = (#geos of f through v)/(#geos of f).  sum over geos counts incidence.
    row_worst = None
    for f in M:
        lf = F(ell[f])
        k = len(cyc[f])
        # p_f(v) accumulated
        pf = {}
        for P in cyc[f]:
            for v in P:
                pf[v] = pf.get(v, F(0)) + F(1, k)
        A = sum(pf[v] * T[v] for v in pf) / lf
        slack = RHS - (A + beta)
        if row_worst is None or slack < row_worst[0]:
            row_worst = (slack, f, A)

    # LRS: sum T^2 <= Gamma*(N + N^2/25 - |M|)
    sumT2 = sum(t * t for t in T)
    lrs_rhs = Gamma * (N + N * N / 25 - beta)
    lrs_slack = lrs_rhs - sumT2

    return dict(N=int(n), beta=int(len(M)), Gamma=Gamma, RHS=RHS,
                maxT=maxT, b2_slack=b2_slack,
                path_worst=path_worst, row_worst=row_worst,
                sumT2=sumT2, lrs_rhs=lrs_rhs, lrs_slack=lrs_slack,
                M=M, ell={f: ell[f] for f in M}, T=T)


# ---------------- DENSE-CHORD constructor ----------------
def build_dense_chord(L, chords, ballast=None):
    """Path 0..L (vertices 0..L). 'chords' = list of even-gap (u,v) bad edges (u<v, v-u even).
    'ballast' = extra edges to add (used to force parity = global max). Returns (n,E,side).
    side = parity coloring i%2 on the path; ballast endpoints must be colored to be cut/bad
    as intended -- here ballast only added among path vertices so side is i%2 throughout."""
    n = L + 1
    E = set()
    for i in range(L):
        E.add((i, i + 1))
    for (u, v) in chords:
        E.add((min(u, v), max(u, v)))
    if ballast:
        for (u, v) in ballast:
            E.add((min(u, v), max(u, v)))
    side = [i % 2 for i in range(n)]
    return n, sorted(E), side


def greedy_max_even_chords(L, max_gap=None):
    """Add as many even-gap chords (u,v), v-u even, to path 0..L as triangle-free allows.
    Greedy by increasing gap then position. Returns chord list."""
    n = L + 1
    adj = [set() for _ in range(n)]
    for i in range(L):
        adj[i].add(i + 1); adj[i + 1].add(i)
    chords = []
    gaps = range(2, L + 1, 2)
    cand = []
    for g in gaps:
        if max_gap and g > max_gap:
            continue
        for u in range(0, n - g):
            cand.append((u, u + g))
    # try each; keep if no triangle created
    for (u, v) in cand:
        if v in adj[u]:
            continue
        if adj[u] & adj[v]:  # common neighbor => triangle
            continue
        adj[u].add(v); adj[v].add(u)
        chords.append((u, v))
    return chords


# ---------------- driver ----------------
def evaluate(name, n, E, side, tlimit=120):
    adj = adjof(n, E)
    tf = trifree(n, adj)
    bc = Bconn(n, adj, side)
    pc = cutsize(n, adj, side)
    if not tf:
        print(f"[{name}] N={n} NOT triangle-free -> skip")
        return None
    opt, bound, status = cpmax(n, E, tlimit)
    is_global = (pc == opt == bound)
    print(f"[{name}] N={n} edges={len(E)} tri-free={tf} Bconn={bc} "
          f"parity-cut={pc} CPSAT-max={opt} bound={bound} GLOBAL-MAX={is_global}")
    if not bc:
        print("    -> B not connected on parity cut; skip cert test")
        return None
    if not is_global:
        print("    -> parity cut is NOT the CP-SAT global max; cannot count as breaker")
        # still report cert on parity cut for info (heuristic only)
    r = test_forms(n, adj, side)
    if r is None:
        print("    -> struct_for_side None (no bad edge / no geodesic)")
        return None
    print(f"    |M|={r['beta']} Gamma={r['Gamma']} N+N^2/25={r['RHS']} "
          f"(={float(r['RHS']):.3f})")
    print(f"    B2:       maxT={float(r['maxT']):.4f} 2N={2*n} slack={float(r['b2_slack']):.4f} "
          f"{'HOLDS' if r['b2_slack']>=0 else '*** BREAK ***'}")
    pw = r['path_worst']
    print(f"    PATH-LRS: worst slack={float(pw[0]):.4f} at f={pw[1]} "
          f"{'HOLDS' if pw[0]>=0 else '*** BREAK ***'}")
    rw = r['row_worst']
    print(f"    ROW-LRS:  worst slack={float(rw[0]):.4f} at f={rw[1]} "
          f"{'HOLDS' if rw[0]>=0 else '*** BREAK ***'}")
    print(f"    LRS:      sumT2={r['sumT2']} rhs={r['lrs_rhs']} slack={float(r['lrs_slack']):.4f} "
          f"{'HOLDS' if r['lrs_slack']>=0 else '*** BREAK ***'}")
    r['name'] = name
    r['is_global'] = is_global
    r['Bconn'] = bc
    r['trifree'] = tf
    return r


if __name__ == "__main__":
    print("=== LRS BREAKER #1: DENSE-CHORD long paths ===\n")
    results = []
    # Family A: pure path + greedy max even chords, no ballast.
    for L in range(6, 17):
        chords = greedy_max_even_chords(L)
        n, E, side = build_dense_chord(L, chords)
        r = evaluate(f"path-densechord L={L} ({len(chords)} chords)", n, E, side)
        if r:
            results.append(r)
        print()
    # Family B: limit gap to keep parity cut closer to global max
    for L in range(8, 18):
        for mg in (2, 4):
            chords = greedy_max_even_chords(L, max_gap=mg)
            n, E, side = build_dense_chord(L, chords)
            r = evaluate(f"path-densechord L={L} maxgap={mg} ({len(chords)} chords)", n, E, side)
            if r:
                results.append(r)
            print()

    # Summary: weakest surviving form among GLOBAL-MAX cases
    print("\n=== SUMMARY (GLOBAL-MAX-verified candidates only) ===")
    gm = [r for r in results if r['is_global'] and r['Bconn']]
    print(f"global-max+Bconn candidates: {len(gm)}")
    forms = {'B2': 'b2_slack', 'PATH-LRS': None, 'ROW-LRS': None, 'LRS': 'lrs_slack'}
    minslack = {'B2': None, 'PATH-LRS': None, 'ROW-LRS': None, 'LRS': None}
    breaks = {'B2': [], 'PATH-LRS': [], 'ROW-LRS': [], 'LRS': []}
    for r in gm:
        sl = {'B2': r['b2_slack'], 'PATH-LRS': r['path_worst'][0],
              'ROW-LRS': r['row_worst'][0], 'LRS': r['lrs_slack']}
        for k, v in sl.items():
            if minslack[k] is None or v < minslack[k]:
                minslack[k] = v
            if v < 0:
                breaks[k].append((r['name'], float(v)))
    for k in ['B2', 'PATH-LRS', 'ROW-LRS', 'LRS']:
        ms = minslack[k]
        print(f"  {k}: min slack over global-max cands = "
              f"{float(ms) if ms is not None else 'na'}  breaks={breaks[k]}")
