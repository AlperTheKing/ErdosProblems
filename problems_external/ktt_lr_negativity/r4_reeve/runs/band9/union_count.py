#!/usr/bin/env python3
"""Exact union count of the EXHAUSTIVE gap regions scanned by band9 (hunter 9).

Every region is a condition on (Aw,Bw,Cw) alone, and both the number of gap
classes N3(Aw)*N3(Bw)*N3(Cw) and the number of band triples realising a class
(band_multiplicity) depend only on (Aw,Bw,Cw).  So the union is computed exactly
by iterating over the 141^3 cells.  Pure integer arithmetic.
"""
import json
import sys

MAXW = 140


def N3(w):
    """#{(g0,g1,g2) >= 0 : g0 + 2 g1 + 3 g2 = w}."""
    n = 0
    g2 = 0
    while 3 * g2 <= w:
        r = w - 3 * g2
        n += r // 2 + 1
        g2 += 1
    return n


N = [N3(w) for w in range(MAXW + 1)]


def mult(Aw, Bw, Cw):
    """# band triples (|nu| in [91,140]) realising a gap class with these weights."""
    D = Cw - Aw - Bw
    if D % 4 != 0:
        return 0
    k = D // 4
    lo = max(0, -k)
    need = 91 - Cw
    if need > 0:
        lo = max(lo, -(-need // 4))
    hi = (140 - Cw) // 4 if Cw <= 140 else -1
    if lo > hi:
        return 0
    # sum_{n4=lo}^{hi} (k + n4 + 1)
    m = hi - lo + 1
    return m * (k + lo + 1) + m * (m - 1) // 2


REGIONS = {
    "wcone S=64": lambda A, B, C: A + B <= 64 and C <= 64,
    "wcone S=72": lambda A, B, C: A + B <= 72 and C <= 72,
    "wbox 44/44/44": lambda A, B, C: A <= 44 and B <= 44 and C <= 44,
    "wbox 140/8/8": lambda A, B, C: A <= 140 and B <= 8 and C <= 8,
    "wbox 8/8/140": lambda A, B, C: A <= 8 and B <= 8 and C <= 140,
    "wbox 8/140/8": lambda A, B, C: A <= 8 and B <= 140 and C <= 8,
    "wbox 20/20/140": lambda A, B, C: A <= 20 and B <= 20 and C <= 140,
    "wbox 32/32/140": lambda A, B, C: A <= 32 and B <= 32 and C <= 140,
}


def main():
    names = sys.argv[1:] or list(REGIONS)
    preds = [REGIONS[n] for n in names]
    tot_cls = tot_tri = 0
    uni_cls = uni_tri = 0
    per = {n: [0, 0] for n in names}
    for A in range(MAXW + 1):
        nA = N[A]
        for B in range(MAXW + 1 - A):
            nAB = nA * N[B]
            for C in range(MAXW + 1):
                if (C - A - B) % 4:
                    continue
                m = mult(A, B, C)
                if m == 0:
                    continue
                cls = nAB * N[C]
                tot_cls += cls
                tot_tri += cls * m
                inany = False
                for n, p in zip(names, preds):
                    if p(A, B, C):
                        per[n][0] += cls
                        per[n][1] += cls * m
                        inany = True
                if inany:
                    uni_cls += cls
                    uni_tri += cls * m
    out = {
        "band_total_gap_classes": tot_cls,
        "band_total_triples": tot_tri,
        "union_gap_classes": uni_cls,
        "union_band_triples": uni_tri,
        "union_fraction_gap_classes": "%.4f%%" % (100.0 * uni_cls / tot_cls),
        "union_fraction_band_triples": "%.4f%%" % (100.0 * uni_tri / tot_tri),
        "per_region": {n: {"gap_classes": v[0], "band_triples": v[1]} for n, v in per.items()},
    }
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    main()
