"""H2_perturb.py -- exact perturbation attack at the EQUALITY points.

Both conjectures are homogeneous of degree 4 in the weight vector:
    ARC :  S^2 - 25*ARCBOUND >= 0
    WSQ :  W^2 - ARCBOUND*S^2 >= 0

Let w0 be an equality point (integer).  Put w = t*w0 + h, t a positive integer,
h an integer vector.  Write for an arc A
    mono(A, w) = t^2 mono(A,w0) + t L_A(h) + mono(A,h),
    L_A(h)     = sum over edges uv monochromatic for A of (w0_u h_v + w0_v h_u)
               = sum_v h_v * (w0-weighted number of neighbours of v on v's side).

EXACT ASYMPTOTIC CRITERIA (derived in H2.md, verified below by finite-t evaluation).

ARC, with sum(h)=0, A* ranging over the arcs attaining ARCBOUND(w0):
    S^2 - 25*ARCBOUND(t w0 + h) < 0 for all large t
      <=>  for every optimal arc A*:  L_{A*}(h) > 0, or
           ( L_{A*}(h) = 0 and mono(A*,h) > 0 ).

WSQ, with sum(h)=0 and sum_v h_v * deg_{w0}(v) = 0:
    W^2 - ARCBOUND*S^2 < 0 for all large t
      <=>  for every optimal arc A*:  L_{A*}(h) > 0, or
           ( L_{A*}(h) = 0 and  S0^2 * mono(A*,h) > 2 * W0 * W(h) ).

This file searches integer h exhaustively over small support / small entries.
"""
import sys, itertools
from fractions import Fraction
from H2_core import adj_matrix, edges, total_W, arcbound_fast


def arc_data(m, w0):
    """Return (E, nbr, list of (mask, mono) for every cyclic interval)."""
    E = edges(m)
    nbr = [[] for _ in range(m)]
    for (i, j) in E:
        nbr[i].append(j); nbr[j].append(i)
    arcs = []
    for s in range(m):
        inA = [False] * m
        for L in range(0, m + 1):
            if L > 0:
                inA[(s + L - 1) % m] = True
            if L == 0 or L == m:
                if L == 0:
                    arcs.append(tuple(inA))
                continue
            arcs.append(tuple(inA))
    # dedupe
    arcs = sorted(set(arcs))
    out = []
    for inA in arcs:
        mo = sum(w0[i] * w0[j] for (i, j) in E if inA[i] == inA[j])
        out.append((inA, mo))
    return E, nbr, out


def L_of(inA, E, w0, h):
    return sum(w0[i] * h[j] + w0[j] * h[i] for (i, j) in E if inA[i] == inA[j])


def mono_of(inA, E, h):
    return sum(h[i] * h[j] for (i, j) in E if inA[i] == inA[j])


def analyse(m, w0, mode, hgen, verbose=True):
    """mode in {'ARC','WSQ'}.  hgen yields integer vectors h (len m)."""
    E, nbr, arcs = arc_data(m, w0)
    W0 = total_W(w0, E)
    S0 = sum(w0)
    AB0 = min(mo for _, mo in arcs)
    # equality check
    if mode == 'ARC':
        assert 25 * AB0 == S0 * S0, f"not an ARC equality point: 25*{AB0} vs {S0*S0}"
    else:
        assert AB0 * S0 * S0 == W0 * W0, f"not a WSQ equality point"
    opt = [inA for inA, mo in arcs if mo == AB0]
    degw = [sum(w0[u] for u in nbr[v]) for v in range(m)]
    hits = []
    for h in hgen:
        if sum(h) != 0:
            continue
        if mode == 'WSQ' and sum(h[v] * degw[v] for v in range(m)) != 0:
            continue
        ok = True
        for inA in opt:
            La = L_of(inA, E, w0, h)
            if La > 0:
                continue
            if La < 0:
                ok = False; break
            if mode == 'ARC':
                if mono_of(inA, E, h) <= 0:
                    ok = False; break
            else:
                if S0 * S0 * mono_of(inA, E, h) <= 2 * W0 * total_W(h, E):
                    ok = False; break
        if ok:
            hits.append(tuple(h))
            if verbose:
                print(f"  CANDIDATE m={m} mode={mode} h={tuple(h)}")
    return hits, (E, W0, S0, AB0, len(opt))


def finite_t_check(m, w0, h, tmax=200, mode='both'):
    """Exact finite-t evaluation.  Returns list of (t, ARCslack, WSQslack)."""
    E = edges(m)
    res = []
    for t in range(1, tmax + 1):
        w = [t * w0[i] + h[i] for i in range(m)]
        if min(w) < 0:
            continue
        S = sum(w); W = total_W(w, E)
        AB = arcbound_fast(w, E, m)
        res.append((t, S * S - 25 * AB, W * W - AB * S * S))
    return res


def gen_support(m, maxsupp, vals):
    """All integer h with |support| <= maxsupp, entries in vals, first nonzero at 0
    (rotation-canonical), sum 0."""
    seen = set()
    for k in range(2, maxsupp + 1):
        for rest in itertools.combinations(range(1, m), k - 1):
            pos = (0,) + rest
            for entries in itertools.product(vals, repeat=k):
                if entries[0] == 0:
                    continue
                if sum(entries) != 0:
                    continue
                if any(e == 0 for e in entries):
                    continue
                h = [0] * m
                for p, e in zip(pos, entries):
                    h[p] = e
                key = tuple(h)
                if key in seen:
                    continue
                seen.add(key)
                yield h


if __name__ == "__main__":
    modd = [int(x) for x in sys.argv[1:]] or [5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25]
    for m in modd:
        w0 = [1] * m
        E = edges(m)
        W0 = total_W(w0, E); S0 = m; AB0 = arcbound_fast(w0, E, m)
        eqW = (AB0 * S0 * S0 == W0 * W0)
        eqA = (25 * AB0 == S0 * S0)
        print(f"=== m={m} deg={2*len(E)//m} AB0={AB0} W0={W0} "
              f"WSQ-equality={eqW} ARC-equality={eqA}")
        if not eqW:
            print("   (skip: not a WSQ equality point)")
            continue
        maxs = 4 if m <= 21 else 3
        hits, info = analyse(m, w0, 'WSQ', gen_support(m, maxs, [-2, -1, 1, 2]))
        print(f"   optimal arcs: {info[4]}   candidates found: {len(hits)}")
        for h in hits[:20]:
            chk = finite_t_check(m, w0, list(h), tmax=60)
            bad = [(t, a, b) for (t, a, b) in chk if b < 0]
            print(f"     h={h}  finite-t WSQ violations: {bad[:5]}")
