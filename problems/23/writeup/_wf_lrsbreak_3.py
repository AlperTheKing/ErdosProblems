"""ADVERSARIAL BREAKER family #3: STACKED/BRIDGED two-lanes + two-lane x blow-up hybrids.

Goal: combine the high local rho(O) of the two-lane (which already kills the universal
rho(O)<=N / ROWSUM-O route) with HIGHER |M| (=beta) to crush the +N^2/25-|M| slack that
saves the LRS family on the sparse (|M|=4) two-lane.

For each candidate graph + the supplied side:
  STEP A (HARD GATE): triangle-free + Bconn + CP-SAT GLOBAL-max verified (parity cut == true max,
                      cut_value == best_objective_bound). A breaker counts ONLY here.
  STEP B: compute T,ell,Gamma,p_f exactly (struct_for_side). Then all four forms (exact Fraction):
     B2:       max_v T(v) <= 2N
     PATH-LRS: (sum_{v in P} T(v))/ell(f) + |M| <= N + N^2/25   for every f, every shortest geodesic P
     ROW-LRS:  (O ell)_f / ell(f) + |M| <= N + N^2/25           for every f      [(O ell)_f = sum_g O_fg ell_g]
     LRS:      sum_v T^2 <= Gamma*(N + N^2/25 - |M|)
  PATH-LRS => ROW-LRS => LRS; B2 is the separate Rayleigh-floor leg.

Report the smallest margin per form, any GLOBAL-max-verified violation with full exact data,
and the weakest form that survived everything.

Run from E:/Projects/ErdosProblems/problems/23/writeup.
"""
import sys
from fractions import Fraction as F
from _satzmu_conn import struct_for_side
from _h import Bconn
from _verify_two_lane import build_two_lane
from ortools.sat.python import cp_model


# ---------------- exact certificate forms ----------------
def cert_forms(n, adj, side):
    """Return dict of all four exact margins (min over the per-edge/per-path forms) or None."""
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    m = len(M)
    if m == 0:
        return None
    N = n
    Gamma = sum(ell[f] ** 2 for f in M)
    rhs = F(N) + F(N * N, 25) - F(m)   # N + N^2/25 - |M|

    # p_f(v) exact
    pf = {}
    for f in M:
        Ps = cyc[f]; k = len(Ps); d = {}
        for P in Ps:
            for v in P:
                d[v] = d.get(v, F(0)) + F(1, k)
        pf[f] = d

    # B2
    maxT = max(T)
    b2_margin = F(2 * N) - maxT

    # PATH-LRS: min over f,P of  rhs - (sum_{v in P} T(v))/ell(f)
    path_min = None; path_arg = None
    for f in M:
        ef = ell[f]
        for P in cyc[f]:
            avg = sum(T[v] for v in P) / ef
            marg = rhs - avg
            if path_min is None or marg < path_min:
                path_min = marg; path_arg = (f, ef, tuple(P), avg)

    # ROW-LRS: (O ell)_f / ell(f) ; O_fg = <p_f,p_g>
    row_min = None; row_arg = None
    for f in M:
        val = F(0)
        for g in M:
            dot = sum(pf[f].get(v, F(0)) * pf[g].get(v, F(0)) for v in pf[f])
            val += dot * ell[g]
        avg = val / ell[f]
        marg = rhs - avg
        if row_min is None or marg < row_min:
            row_min = marg; row_arg = (f, ell[f], avg)

    # LRS (scalar)
    sumT2 = sum(t * t for t in T)
    lrs_margin = Gamma * rhs - sumT2   # >=0 wanted (=Gamma*(N+N^2/25-m)-sumT2)

    # rho(O) lower bound info (for context): sumT^2/Gamma
    sumT = sum(T)
    rayleigh = (sumT * sumT) / Gamma   # <= rho(O); also Gamma/N <= rayleigh

    return dict(
        N=N, m=m, Gamma=Gamma, sumT2=sumT2, maxT=maxT, sumT=sumT,
        b2=(b2_margin, maxT),
        path=(path_min, path_arg),
        row=(row_min, row_arg),
        lrs=(lrs_margin, sumT2, Gamma * rhs),
        rayleigh=rayleigh,
    )


# ---------------- HARD gate: CP-SAT global max ----------------
def trifree(n, adj):
    for u in range(n):
        for v in adj[u]:
            if v > u and (adj[u] & adj[v]):
                return False
    return True


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
    optimal = (st == cp_model.OPTIMAL)
    return int(round(s.ObjectiveValue())), int(round(s.BestObjectiveBound())), optimal


def cutsize(n, adj, side):
    return sum(1 for u in range(n) for v in adj[u] if v > u and side[u] != side[v])


def evaluate(name, n, E, side, tlimit=120):
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b); adj[b].add(a)
    N = n
    tf = trifree(n, adj)
    bc = Bconn(n, adj, side)
    pc = cutsize(n, adj, side)
    opt, bnd, isopt = cpmax(n, sorted(set((min(a, b), max(a, b)) for a, b in E)), tlimit)
    global_max = (pc == opt == bnd) and isopt
    cf = cert_forms(n, adj, side)
    print(f"[{name}] N={N} |E|={len(set((min(a,b),max(a,b)) for a,b in E))} trifree={tf} Bconn={bc} "
          f"paritycut={pc} CPmax={opt} bound={bnd} optimal={isopt} GLOBAL-MAX={global_max}", flush=True)
    if cf is None:
        print("    struct_for_side None (no bad edges / no geodesic)", flush=True)
        return None
    m = cf['m']; Gamma = cf['Gamma']
    print(f"    |M|={m} Gamma={Gamma} N^2={N*N} Gamma<=N^2:{Gamma<=N*N} "
          f"N^2/25={N*N/25:.2f} slack(N^2/25-m)={float(F(N*N,25)-m):.2f}  rayleigh(sumT^2/Gamma)={float(cf['rayleigh']):.3f} (>=Gamma/N={float(F(Gamma,N)):.3f})", flush=True)
    b2m, maxT = cf['b2']
    pm, parg = cf['path']
    rm, rarg = cf['row']
    lm, sT2, grhs = cf['lrs']
    print(f"    B2      margin={float(b2m):+.4f} (2N-maxT, maxT={float(maxT)})  {'HOLDS' if b2m>=0 else 'VIOLATED'}", flush=True)
    print(f"    PATH-LRS margin={float(pm):+.4f}  {'HOLDS' if pm>=0 else 'VIOLATED'}   arg f={parg[0]} ell={parg[1]} avg={float(parg[3]):.3f}", flush=True)
    print(f"    ROW-LRS  margin={float(rm):+.4f}  {'HOLDS' if rm>=0 else 'VIOLATED'}   arg f={rarg[0]} ell={rarg[1]} avg={float(rarg[2]):.3f}", flush=True)
    print(f"    LRS      margin={float(lm):+.4f}  {'HOLDS' if lm>=0 else 'VIOLATED'}   (Gamma*rhs={float(grhs):.2f} sumT^2={float(sT2):.2f})", flush=True)
    breaks = []
    if global_max and tf and bc:
        if b2m < 0: breaks.append('B2')
        if pm < 0: breaks.append('PATH-LRS')
        if rm < 0: breaks.append('ROW-LRS')
        if lm < 0: breaks.append('LRS')
        if breaks:
            print(f"    *** GLOBAL-MAX-VERIFIED BREAKER of {breaks} ***", flush=True)
    elif (b2m < 0 or pm < 0 or rm < 0 or lm < 0):
        why = []
        if not global_max: why.append('NOT-global-max')
        if not tf: why.append('not-trifree')
        if not bc: why.append('not-Bconn')
        print(f"    (negative margin but NOT a valid breaker: {why})", flush=True)
    return dict(name=name, N=N, m=m, global_max=global_max, tf=tf, bc=bc,
                b2=b2m, path=pm, row=rm, lrs=lm, breaks=breaks)


# ---------------- constructors: stacked / bridged two-lanes ----------------
def relabel(n, E, side, off):
    return [(a + off, b + off) for a, b in E], side[:]


def stack_two_lanes(L1, L2, bridge='cut'):
    """Disjoint union of two two-lanes; add ONE bridge x0(block1)-x?(block2).
    bridge='cut'  -> connect to a vertex on the OPPOSITE side (keeps cut edge, B stays connected)
    bridge='none' -> no bridge (B will NOT be connected across blocks; gate will reject)
    """
    n1, E1, s1, bad1 = build_two_lane(L1)
    n2, E2, s2, bad2 = build_two_lane(L2)
    E2s = [(a + n1, b + n1) for a, b in E2]
    s = s1 + s2
    E = list(E1) + E2s
    if bridge == 'cut':
        # x0 of block1 has side s1[0]; pick a block2 vertex with opposite side that won't make a triangle.
        # use x-vertex of block2 with opposite parity, far from block1 attachments to avoid triangles.
        target = None
        for cand in range(n2):
            if s2[cand] != s1[0]:
                target = cand + n1; break
        if target is not None:
            E.append((0, target))
    n = n1 + n2
    return n, sorted(set((min(a, b), max(a, b)) for a, b in E)), s


def chain_two_lanes(Ls, bridge='cut'):
    """Chain k two-lanes block_0 - block_1 - ... each linked by a single cut bridge."""
    n = 0; E = []; s = []
    prev_x0 = None; prev_side0 = None
    for L in Ls:
        nL, EL, sL, _ = build_two_lane(L)
        EL = [(a + n, b + n) for a, b in EL]
        E += EL
        x0 = n  # vertex 0 of this block
        if prev_x0 is not None:
            # bridge prev block's x0 to this block's first opposite-side vertex
            tgt = None
            for cand in range(nL):
                if sL[cand] != prev_side0:
                    tgt = cand + n; break
            if tgt is not None:
                E.append((prev_x0, tgt))
        prev_x0 = x0; prev_side0 = sL[0]
        s += sL
        n += nL
    return n, sorted(set((min(a, b), max(a, b)) for a, b in E)), s


def blowup_two_lane(L, t):
    """t-fold i.i.d. blow-up of the two-lane graph, with the inherited side (blow-up preserves bipartition).
    Blow-up of a triangle-free graph need NOT be triangle-free (independent set blown to independent set keeps
    no edges inside a class, so it IS triangle-free iff original is). Vertices in one original vertex form an
    independent set; triangle would need 3 mutually adjacent originals = triangle in original. So blow-up of a
    triangle-free graph is triangle-free. Good."""
    n0, E0, s0, _ = build_two_lane(L)
    n = n0 * t; E = []
    for a, b in E0:
        for i in range(t):
            for j in range(t):
                E.append((a * t + i, b * t + j))
    side = [0] * n
    for v in range(n0):
        for i in range(t):
            side[v * t + i] = s0[v]
    return n, sorted(set((min(a, b), max(a, b)) for a, b in E)), side


if __name__ == "__main__":
    print("=== LRS BREAKER family #3: stacked/bridged two-lanes + two-lane x blow-up ===", flush=True)
    print("    HARD gate: a breaker requires triangle-free + Bconn + CP-SAT GLOBAL-max (cut==opt==bound, optimal).", flush=True)
    results = []

    # baseline: single two-lanes (should survive via slack); confirm the harness reproduces known numbers
    print("\n--- baseline single two-lanes ---", flush=True)
    for L in (8, 10, 12):
        n, E, s, _ = build_two_lane(L)
        r = evaluate(f"two-lane-L{L}", n, E, s)
        if r: results.append(r)

    # stacked two pairs (raise |M| to 8 while each block keeps its local rho)
    print("\n--- stacked (2 blocks) bridged two-lanes ---", flush=True)
    for L1, L2 in ((8, 8), (8, 10), (10, 10), (8, 12)):
        n, E, s = stack_two_lanes(L1, L2)
        r = evaluate(f"stack2-L{L1}+L{L2}", n, E, s)
        if r: results.append(r)

    # chained 3 and 4 blocks (|M| up to 12,16)
    print("\n--- chained (3-4 blocks) bridged two-lanes ---", flush=True)
    for Ls in ([8, 8, 8], [8, 8, 8, 8], [8, 10, 8]):
        n, E, s = chain_two_lanes(Ls)
        r = evaluate(f"chain-{Ls}", n, E, s)
        if r: results.append(r)

    # two-lane x blow-up hybrids
    print("\n--- two-lane x blow-up (t=2,3) ---", flush=True)
    for L in (8, 10):
        for t in (2, 3):
            n, E, s = blowup_two_lane(L, t)
            if n > 90:
                print(f"[blow-L{L}-t{t}] skipped N={n} (>90, CP-SAT too slow)", flush=True)
                continue
            r = evaluate(f"blow-L{L}-t{t}", n, E, s, tlimit=180)
            if r: results.append(r)

    # ---------------- summary ----------------
    print("\n=== SUMMARY ===", flush=True)
    valid = [r for r in results if r['global_max'] and r['tf'] and r['bc']]
    print(f"configs evaluated={len(results)}  GLOBAL-max-valid={len(valid)}", flush=True)
    any_break = {}
    for form in ('B2', 'PATH-LRS', 'ROW-LRS', 'LRS'):
        brk = [r for r in valid if form in r['breaks']]
        any_break[form] = brk
    # weakest surviving form among valid configs (most negative -> closest to break, but we report survivors)
    for form, key in (('B2', 'b2'), ('PATH-LRS', 'path'), ('ROW-LRS', 'row'), ('LRS', 'lrs')):
        if valid:
            worst = min(valid, key=lambda r: r[key])
            print(f"  {form:9s}: min margin over GLOBAL-max configs = {float(worst[key]):+.4f} at {worst['name']} "
                  f"(N={worst['N']},|M|={worst['m']})  breakers={len(any_break[form])}", flush=True)
    broke = [f for f in ('B2', 'PATH-LRS', 'ROW-LRS', 'LRS') if any_break[f]]
    if broke:
        print(f"  *** GLOBAL-MAX-VERIFIED BREAKERS FOUND for: {broke} ***", flush=True)
        for f in broke:
            for r in any_break[f]:
                print(f"     {f} broken by {r['name']} N={r['N']} |M|={r['m']} margin={float(r[{'B2':'b2','PATH-LRS':'path','ROW-LRS':'row','LRS':'lrs'}[f]]):+.4f}", flush=True)
    else:
        print("  NO GLOBAL-max-verified breaker found in family #3.", flush=True)
