"""CONFIRM the break with the ORIGINAL construction-gate code (no reimplementation).

Import lenbundle_switches, boundary_delta, flip, gamma_of DIRECTLY from _construction_gate and run its exact
covering logic on the second max cut 011111111111000000 of H?AFBo] blowup t=2. If it reports a failure there,
the (LB) lemma as currently stated (length-bundle half-switch covers every R<0 vertex) is FALSE on a genuine
maximum cut -- the residual gap is not 'which bundle' but 'the length-bundle family is insufficient for some
max cuts'. Also: is this cut GAMMA-MIN among all max cuts? (If it is gamma-min, that would be fatal to the whole
chain; if it is NOT gamma-min, the chain only needs gamma-min cuts and this break is irrelevant.)

Exact Fraction.
"""
from fractions import Fraction as F
from _h import dec, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _construction_gate import lenbundle_switches, boundary_delta, flip, gamma_of


def vertex_blowup(n, E, t):
    EE = []
    for (u, v) in E:
        for a in range(t):
            for b in range(t):
                EE.append((u * t + a, v * t + b))
    return n * t, EE


def cutval(n, adj, side):
    return sum(1 for v in range(n) for w in adj[v] if w > v and side[v] != side[w])


def gamma_min_among_maxcuts(n, adj):
    """min Gamma over all B-connected maximum cuts."""
    gmax = max(cutval(n, adj, s) for s in maxcut_all(n, adj))
    best = None
    for s in maxcut_all(n, adj):
        if cutval(n, adj, s) != gmax:
            continue
        g = gamma_of(n, adj, s)
        if g is None:
            continue
        if best is None or g < best:
            best = g
    return best, gmax


def run(side, adj, n, label):
    print("\n===", label, ''.join(map(str, side)))
    print("  cutval=", cutval(n, adj, side), " Bconn=", Bconn(n, adj, side))
    st = struct_for_side(n, adj, side)
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    N = F(n)
    K2 = build_K2(n, M, cyc)
    R = [N * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
    neg = [v for v in range(n) if R[v] < 0]
    gamma0 = sum(ell[f] ** 2 for f in M)
    print("  Gamma=", gamma0, " R<0:", neg)
    fails = []
    for v in neg:
        covered = False
        for Sset in lenbundle_switches(v, M, ell, cyc):
            if v not in Sset or len(Sset) == 0 or len(Sset) == n:
                continue
            if boundary_delta(n, adj, side, Sset) != 0:
                continue
            s2 = flip(side, Sset)
            g2 = gamma_of(n, adj, s2)
            if g2 is not None and g2 < gamma0:
                covered = True
                break
        if not covered:
            fails.append(v)
    print("  ORIGINAL construction-gate covering FAILURES at:", fails)
    return gamma0, fails


def main():
    hN, hE = dec("H?AFBo]")
    n, EE = vertex_blowup(hN, hE, 2)
    adj = [set() for _ in range(n)]
    for x, y in EE:
        adj[x].add(y); adj[y].add(x)
    gm, gmax = gamma_min_among_maxcuts(n, adj)
    print("graph H?AFBo] blowup t=2  N=%d  global-max-cut=%d  GAMMA-MIN over max cuts = %s" % (n, gmax, gm))
    # canonical cut
    base = [int(c) for c in "111110000"]
    sc = [base[v // 2] for v in range(n)]
    gc, fc = run(sc, adj, n, "canonical blowup cut")
    # break-hunt cut
    sb = [int(c) for c in "011111111111000000"]
    gb, fb = run(sb, adj, n, "break-hunt cut")
    print("\n--- SUMMARY ---")
    print("  canonical cut Gamma=%s  is-gamma-min=%s  construction-fails=%s" % (gc, gc == gm, fc))
    print("  break-hunt cut Gamma=%s  is-gamma-min=%s  construction-fails=%s" % (gb, gb == gm, fb))
    print("VERDICT:",
          "BREAK IS ON A NON-GAMMA-MIN MAX CUT -> harmless (chain only needs gamma-min)" if (fb and gb != gm) else
          ("BREAK IS ON A GAMMA-MIN CUT -> FATAL to length-bundle (LB)" if (fb and gb == gm) else
           "no construction failure on break-hunt cut (false alarm)"))


if __name__ == "__main__":
    main()
