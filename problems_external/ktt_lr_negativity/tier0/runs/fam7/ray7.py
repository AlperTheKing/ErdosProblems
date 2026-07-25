#!/usr/bin/env python3
"""Family-7 dilation-ray analyzer.

For a screened seed record we have the EXACT Ehrhart polynomial P of
Q = Q(lam,mu,nu) (deg d).  The triple (n*lam, n*mu, n*nu) is itself a member
of the family and its hive polytope is n*Q, so exactly:

    c(nQ)        = P(n)
    interior(nQ) = (-1)^d P(-n)          (Ehrhart-Macdonald, period 1)
    h*_1(nQ)     = P(n) - (d+1)
    h*_d(nQ)     = (-1)^d P(-n)
    margin(nQ)   = h*_1 - h*_d = B(nQ) - (d+1),  B = boundary lattice points

so a whole dilation ray is decided by exact rational arithmetic on the seed
polynomial.  All arithmetic is Fraction/int; no float decides anything.
Candidates found here are re-verified against engines A and B.
"""
import json, sys, glob
from fractions import Fraction


def poly_eval(coeffs, n):
    v = Fraction(0)
    for c in reversed(coeffs):
        v = v * n + c
    return v


def main():
    NMAX = int(sys.argv[1])
    files = []
    for pat in sys.argv[2:]:
        files.extend(glob.glob(pat))
    best_hd = (-1, None)
    min_margin = (None, None)
    min_margin_int = (None, None)      # restricted to interior-positive
    min_c_int = {}       # d -> (c, info)
    min_margin_by_d = {}  # d -> (margin, info) over interior-positive
    hits = []
    nseed = 0
    nray = 0
    n_int_pos = 0
    seen_seeds = set()
    dcount = {}
    for fn in files:
        with open(fn) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                if rec.get("status") != "OK":
                    continue
                d = rec["d"]
                if d is None or d < 2:
                    continue
                key = (tuple(rec["lam"]), tuple(rec["mu"]), tuple(rec["nu"]))
                if key in seen_seeds:
                    continue
                seen_seeds.add(key)
                nseed += 1
                dcount[d] = dcount.get(d, 0) + 1
                coeffs = [Fraction(x) for x in rec["coeffs_low_to_high"]]
                for n in range(1, NMAX + 1):
                    c = poly_eval(coeffs, n)
                    inte = poly_eval(coeffs, -n) * ((-1) ** d)
                    if c.denominator != 1 or inte.denominator != 1:
                        raise AssertionError("non-integer Ehrhart value %s %s" % (key, n))
                    c = int(c); inte = int(inte)
                    nray += 1
                    h1 = c - (d + 1)
                    marg = h1 - inte
                    info = {"seed": {"lam": rec["lam"], "mu": rec["mu"], "nu": rec["nu"]},
                            "n": n, "d": d, "c": c, "hstar_1": h1, "hstar_d": inte,
                            "margin": marg, "B": inte and (c - inte) or (c - inte),
                            "triple": {"lam": [n * x for x in rec["lam"]],
                                       "mu": [n * x for x in rec["mu"]],
                                       "nu": [n * x for x in rec["nu"]]}}
                    if inte > best_hd[0]:
                        best_hd = (inte, info)
                    if min_margin[0] is None or marg < min_margin[0]:
                        min_margin = (marg, info)
                    if inte > 0:
                        n_int_pos += 1
                        if min_margin_int[0] is None or marg < min_margin_int[0]:
                            min_margin_int = (marg, info)
                        cur = min_c_int.get(str(d))
                        if cur is None or c < cur[0]:
                            min_c_int[str(d)] = (c, info)
                        cur2 = min_margin_by_d.get(str(d))
                        if cur2 is None or marg < cur2[0]:
                            min_margin_by_d[str(d)] = (marg, info)
                    if marg < 0 or (h1 == 0 and inte > 0):
                        hits.append(info)
    print(json.dumps({"n_seeds": nseed, "seeds_by_d": dcount, "n_ray_points": nray,
                      "n_interior_positive": n_int_pos,
                      "best_hstar_d": best_hd,
                      "min_margin_overall": min_margin,
                      "min_margin_interior_positive": min_margin_int,
                      "min_c_with_interior": min_c_int,
                      "min_margin_by_d_interior_positive": min_margin_by_d,
                      "hits": hits[:50], "n_hits": len(hits)}, indent=1))


if __name__ == "__main__":
    main()
