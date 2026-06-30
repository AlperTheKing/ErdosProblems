"""Finisher: C5[5],C5[6] tightness via a directly-constructed gamma-min side (no 2^(n-1) brute force),
plus C5[t] x two-lane hybrid with the side taken from the components' own gamma-min sides (bridge = 1 cut edge).
For C5[t], the gamma-min connected-B max cut is the standard near-balanced cut realized by splitting each
blow-up class; we instead let CP-SAT FIND a max cut and use the parity-consistent class assignment that the
two-lane / C5 already give. We verify GLOBAL-max with CP-SAT and require the supplied side == an optimum.
"""
from fractions import Fraction as F
from _wf_lrsbreak_3 import evaluate, trifree, cpmax, cutsize, build_two_lane
from _h import Bconn
from ortools.sat.python import cp_model


def c5_blowup(t):
    n = 5 * t; E = []
    for i in range(5):
        for a in range(t):
            for b in range(t):
                E.append((i * t + a, ((i + 1) % 5) * t + b))
    return n, sorted(set((min(a, b), max(a, b)) for a, b in E))


def cpmax_side(n, edges, tlimit=120):
    """Return (opt, bound, optimal, side) where side is an actual MAX-cut 2-coloring."""
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
    side = [int(s.Value(x[i])) for i in range(n)]
    return int(round(s.ObjectiveValue())), int(round(s.BestObjectiveBound())), optimal, side


if __name__ == "__main__":
    print("=== 3c: C5[5..6] + hybrids using a CP-SAT-found max-cut SIDE (then re-gate) ===", flush=True)
    results = []
    # C5[5], C5[6]
    for t in (5, 6):
        n, E = c5_blowup(t)
        edges = sorted(set((min(a, b), max(a, b)) for a, b in E))
        opt, bnd, isopt, side = cpmax_side(n, edges, tlimit=120)
        # Need a CONNECTED-B max cut. Try the CP side; if not Bconn, the gate rejects (reported).
        adj = [set() for _ in range(n)]
        for a, b in edges:
            adj[a].add(b); adj[b].add(a)
        bc = Bconn(n, adj, side)
        print(f"[C5[{t}]] N={n} CPmax={opt} bound={bnd} optimal={isopt} Bconn(cpside)={bc}", flush=True)
        if not bc:
            print(f"    CP max-cut side not B-connected; C5[t] tightness already shown for t<=4 (margin 0).", flush=True)
            continue
        r = evaluate(f"C5[{t}]", n, edges, side, tlimit=120)
        if r:
            results.append(r)

    # C5[t] x two-lane hybrid: build combined, let CP-SAT find the global max-cut side, then gate.
    print("\n--- C5[t] x two-lane bridged hybrid (CP-SAT side) ---", flush=True)
    for t in (2, 3):
        for L in (8,):
            n1, E1 = c5_blowup(t)
            n2, E2, s2, _ = build_two_lane(L)
            E2s = [(a + n1, b + n1) for a, b in E2]
            E = list(E1) + E2s + [(0, n1)]   # bridge C5 vtx0 to two-lane vtx0
            n = n1 + n2
            edges = sorted(set((min(a, b), max(a, b)) for a, b in E))
            if n > 55:
                print(f"[C5[{t}]+TL{L}] N={n} skipped (>55, CP-SAT side search slow)", flush=True)
                continue
            opt, bnd, isopt, side = cpmax_side(n, edges, tlimit=180)
            r = evaluate(f"C5[{t}]+TL{L}", n, edges, side, tlimit=180)
            if r:
                results.append(r)

    print("\n=== SUMMARY 3c ===", flush=True)
    valid = [r for r in results if r['global_max'] and r['tf'] and r['bc']]
    print(f"configs={len(results)} GLOBAL-max-valid={len(valid)}", flush=True)
    for form, key in (('B2', 'b2'), ('PATH-LRS', 'path'), ('ROW-LRS', 'row'), ('LRS', 'lrs')):
        if valid:
            worst = min(valid, key=lambda r: r[key])
            brk = [r for r in valid if form in r['breaks']]
            print(f"  {form:9s}: min margin = {float(worst[key]):+.6f} at {worst['name']} breakers={len(brk)}", flush=True)
