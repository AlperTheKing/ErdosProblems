#!/usr/bin/env python3
"""Exact: for h*_0=1, h*_1=0, which (d, V=Sum h*) admit a negative Ehrhart
coefficient, and with which h*?  Pure exact arithmetic.

[n^k] P = (1/d!) * sum_j h*_j * e_{d-k}(d-j, d-j-1, ..., 1-j)
"""
from fractions import Fraction
from itertools import product
import sys, json


def esym(vals):
    """all elementary symmetric polys e_0..e_m of vals (list)."""
    e = [1] + [0] * len(vals)
    for v in vals:
        for i in range(len(vals), 0, -1):
            e[i] = e[i] + v * e[i - 1]
    return e


def coeff_vectors(d):
    """rows[k][j] = e_{d-k}(d-j,...,1-j) / d!  -> [n^k]P = sum_j rows[k][j]*h_j"""
    fac = 1
    for i in range(2, d + 1):
        fac *= i
    cols = []
    for j in range(d + 1):
        vals = [d - j - i for i in range(d)]
        cols.append(esym(vals))
    rows = []
    for k in range(d + 1):
        rows.append([Fraction(cols[j][d - k], fac) for j in range(d + 1)])
    return rows


def min_volume(d, smax=None):
    """min V=sum h* over nonneg integer h* with h_0=1,h_1=0, deg<=smax,
    such that some coefficient < 0.  Returns (V, h*) or None."""
    if smax is None:
        smax = d - 1
    rows = coeff_vectors(d)
    for V in range(2, 60):
        extra = V - 1
        # distribute `extra` among j = 2..smax
        best = None
        idxs = list(range(2, smax + 1))
        if not idxs:
            continue
        def rec(pos, rem, cur):
            nonlocal best
            if best is not None:
                return
            if pos == len(idxs):
                if rem != 0:
                    return
                h = [0] * (d + 1)
                h[0] = 1
                for i, jj in enumerate(idxs):
                    h[jj] = cur[i]
                if h[smax] == 0 and smax > 1:
                    return   # require deg exactly smax for this shape class
                for k in range(1, d):
                    s = sum(rows[k][j] * h[j] for j in range(d + 1))
                    if s < 0:
                        best = (h, k, s)
                        return
                return
            for v in range(rem + 1):
                rec(pos + 1, rem - v, cur + [v])
        rec(0, extra, [])
        if best:
            return V, best[0], best[1], str(best[2])
    return None


if __name__ == "__main__":
    out = {}
    for d in range(3, 15):
        row = {}
        for smax in range(2, d):
            r = min_volume(d, smax)
            if r:
                row["s=%d" % smax] = {"V": r[0], "hstar": r[1], "negk": r[2],
                                      "coeff": r[3]}
        # overall best over all smax <= d-1
        allr = [(v["V"], k, v) for k, v in row.items()]
        best = min(allr) if allr else None
        out[str(d)] = {"per_s": row,
                       "min_V_overall": best[0] if best else None,
                       "witness": best[2] if best else None}
    print(json.dumps(out, indent=1))
