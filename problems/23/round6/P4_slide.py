"""Where exactly does W8 kill the hierarchy, and what survives?

(1) min over b in the SUPPORT of m(b)          - what bound_k averages; W8 makes it > 1/25.
(2) min over b in the WHOLE CIRCLE of m(b)     - the neighbourhood cuts of non-atoms;
                                                 this is the cheapest possible repair.
(3) min over ALL 1/3-arcs                      - same family, stated arc-wise.
(4) min over half-arcs                         - the A-family's minimum (A is only its average).
(5) ARCBOUND                                   - the full two-parameter arc family.
"""
from fractions import Fraction as F
from P4_core import (from_gamma, sort_cyclic, adjacency, W_of, mono, m_at, arcbound, psi,
                     m_values, A_of, TARGET, far)

CASES = [
    ("W8 (the new falsifier)", 20, [0, 3, 4, 0, 1, 0, 0, 2, 4, 4, 0, 0, 0, 0, 4, 4, 3, 1, 0, 0]),
    ("W2 C5 extremal", 5, [1, 1, 1, 1, 1]),
    ("W3 uniform Gamma_18", 18, [1] * 18),
    ("W6 uniform Gamma_7", 7, [1] * 7),
    ("W1 Gamma_8 half-arc killer", 8, [0, 1, 0, 1, 2, 0, 2, 1]),
]


def breakpoints(pos):
    """b-values where N(b) can change: b = p -+ 1/3 (mod 1); return midpoints of the cells"""
    bps = sorted(set([(p - F(1, 3)) % 1 for p in pos] + [(p + F(1, 3)) % 1 for p in pos] + list(pos)))
    mids = []
    for i in range(len(bps)):
        a, c = bps[i], bps[(i + 1) % len(bps)]
        mids.append(((a + c) / 2) % 1 if c > a else ((a + c + 1) / 2) % 1)
    return bps + mids


def min_m_circle(pos, wt, adj):
    cand = breakpoints(pos)
    return min(m_at(pos, wt, b, adj) for b in cand), cand


def min_third_arcs(pos, wt, adj):
    """min over ALL arcs of length exactly 1/3 (open), i.e. all N(b)"""
    v, _ = min_m_circle(pos, wt, adj)
    return v


def min_half_arcs(pos, wt, adj):
    """min over all arcs of length exactly 1/2"""
    best = None
    cand = sorted(set([p % 1 for p in pos] + [(p + F(1, 2)) % 1 for p in pos]))
    ext = []
    for i in range(len(cand)):
        a, c = cand[i], cand[(i + 1) % len(cand)]
        ext.append(a)
        ext.append(((a + c) / 2) % 1 if c > a else ((a + c + 1) / 2) % 1)
    for a in ext:
        inS = [((p - a) % 1) < F(1, 2) for p in pos]
        v = mono(pos, wt, inS, adj)
        if best is None or v < best:
            best = v
    return best


if __name__ == '__main__':
    print(f"{'measure':28s} {'A':>10s} {'min_supp m':>11s} {'min_circle m':>13s} "
          f"{'min half-arc':>13s} {'ARCBOUND':>10s} {'psi':>10s}")
    for nm, m, w in CASES:
        pos, wt = sort_cyclic(*from_gamma(m, w))
        adj = adjacency(pos)
        A = A_of(pos, wt, adj)
        ms = min(m_values(pos, wt, adj))
        mc, _ = min_m_circle(pos, wt, adj)
        mh = min_half_arcs(pos, wt, adj)
        ab = arcbound(pos, wt, adj)
        ps = psi(pos, wt, adj) if len(pos) <= 20 else None
        f = lambda v: f"{float(v):10.6f}" + ("*" if v > TARGET else " ")
        print(f"{nm:28s} {f(A)} {f(ms)} {f(mc)}  {f(mh)} {f(ab)} "
              f"{f(ps) if ps is not None else '   n/a':>10s}")
    print("\n  ( * = exceeds 1/25 = 0.04 )")
    print("\n  W8 detail: the value of m(b) as b sweeps the circle")
    pos, wt = sort_cyclic(*from_gamma(20, CASES[0][2]))
    adj = adjacency(pos)
    seen = {}
    for b in sorted(set(breakpoints(pos))):
        v = m_at(pos, wt, b, adj)
        seen.setdefault(v, []).append(b)
    for v in sorted(seen):
        print(f"    m = {str(v):>10s} = {float(v):.6f} {'<= 1/25' if v <= TARGET else '> 1/25'} "
              f"at b in {[str(t) for t in seen[v][:6]]}{' ...' if len(seen[v])>6 else ''}")
