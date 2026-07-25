#!/usr/bin/env python3
"""
Classify every verified atlas triple by PRIMITIVITY (all essential-Horn slacks
strict) and by its closest-to-negative Ehrhart coefficient ratio maxR
(a_k < 0  <=>  R_k > 1).  All arithmetic exact.

Route A reduced the full KTT conjecture to: every PRIMITIVE hive polytope has
no negative Ehrhart coefficient.  This script measures whether primitivity
pushes the h*-vector toward the negativity threshold (danger) or keeps it
bounded away (safety), using the already-verified h* atlas.
"""
import csv, json, os, sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "hstar_spread"))
from crit import wrow, coeffs_from_hstar, moments  # noqa

HORN = {int(k): v for k, v in json.load(
    open(os.path.join(ROOT, "general_proof_horn_cache.json"))).items()}


def parse_part(s):
    s = (s or "").strip()
    if not s:
        return []
    return [int(x) for x in s.replace(";", ",").split(",") if x.strip() != ""]


def psum(part, idx):
    return sum(part[i - 1] for i in idx)


def is_primitive(lam, mu, nu):
    """True iff every essential-Horn inequality is STRICT.  Returns
    (primitive_bool, min_slack, num_saturated)."""
    r = len(nu)
    lam = list(lam) + [0] * (r - len(lam))
    mu = list(mu) + [0] * (r - len(mu))
    if r not in HORN:
        return None, None, None
    msl = None
    nsat = 0
    for I, J, K in HORN[r]:
        sl = psum(lam, I) + psum(mu, J) - psum(nu, K)
        if sl < 0:
            # weight-matched positive triples should satisfy all Horn ineqs;
            # a negative slack means data problem -> report
            return None, sl, None
        if sl == 0:
            nsat += 1
        msl = sl if msl is None else min(msl, sl)
    return (nsat == 0), msl, nsat


def maxR(h):
    """closest-to-negative ratio over interior coefficients k=1..d-1."""
    d = len(h) - 1
    best = Fraction(0)
    bk = -1
    for k in range(1, d):
        W = wrow(d, k)
        pos = sum(h[j] * W[j] for j in range(d + 1) if W[j] > 0)
        neg = sum(-h[j] * W[j] for j in range(d + 1) if W[j] < 0)
        if pos == 0:
            continue
        R = Fraction(neg, pos)
        if R > best:
            best = R
            bk = k
    return best, bk


def main():
    atlas = os.path.join(ROOT, "hstar_spread", "hstar_atlas2.tsv")
    rows = list(csv.DictReader(open(atlas), delimiter="\t"))
    out = []
    n_prim = n_nonprim = n_bad = 0
    any_neg = []
    for row in rows:
        h = [int(x) for x in row["hstar"].split(",")]
        lam = parse_part(row["lam"])
        mu = parse_part(row["mu"])
        nu = parse_part(row["nu"])
        if not nu:
            n_bad += 1
            continue
        prim, msl, nsat = is_primitive(lam, mu, nu)
        if prim is None:
            n_bad += 1
            continue
        R, bk = maxR(h)
        if R > 1:
            any_neg.append((lam, mu, nu, h, str(R)))
        d = len(h) - 1
        M = sum(h)
        rec = dict(d=d, r=len(nu), c=h[1] + (d + 1) if False else None,
                   M=M, prim=prim, min_slack=msl, nsat=nsat,
                   R_num=R.numerator, R_den=R.denominator, bk=bk,
                   hstar=h, lam=lam, mu=mu, nu=nu)
        out.append(rec)
        if prim:
            n_prim += 1
        else:
            n_nonprim += 1
    json.dump(out, open(os.path.join(HERE, "classified.json"), "w"))
    print("rows classified:", len(out), " primitive:", n_prim,
          " nonprimitive:", n_nonprim, " skipped:", n_bad)
    print("triples with a NEGATIVE coefficient (R>1):", len(any_neg))
    for x in any_neg[:10]:
        print("  NEG", x)

    # summary: distribution of R by primitivity and by d
    def summ(recs, label):
        if not recs:
            print(f"  [{label}] none")
            return
        Rs = sorted((Fraction(r["R_num"], r["R_den"]) for r in recs))
        mx = Rs[-1]
        near = sum(1 for R in Rs if R > Fraction(9, 10))
        near95 = sum(1 for R in Rs if R > Fraction(95, 100))
        near99 = sum(1 for R in Rs if R > Fraction(99, 100))
        print(f"  [{label}] n={len(recs):5d}  maxR={float(mx):.5f}  "
              f"#R>.90={near:4d}  #R>.95={near95:4d}  #R>.99={near99:4d}")

    print("\n=== closest-to-negative ratio maxR, split by primitivity ===")
    summ([r for r in out if r["prim"]], "PRIMITIVE   ")
    summ([r for r in out if not r["prim"]], "NONPRIMITIVE")

    print("\n=== by dimension d (primitive only) ===")
    for d in sorted(set(r["d"] for r in out if r["prim"])):
        summ([r for r in out if r["prim"] and r["d"] == d], f"prim d={d}")
    print("\n=== by dimension d (nonprimitive only) ===")
    for d in sorted(set(r["d"] for r in out if not r["prim"])):
        summ([r for r in out if not r["prim"] and r["d"] == d], f"nonp d={d}")

    # top-10 nearest-to-negative overall, with primitivity flag
    print("\n=== top 15 nearest-to-negative triples overall ===")
    allr = sorted(out, key=lambda r: -Fraction(r["R_num"], r["R_den"]))
    for r in allr[:15]:
        R = Fraction(r["R_num"], r["R_den"])
        print(f"  R={float(R):.5f} d={r['d']} r={r['r']} M={r['M']:6d} "
              f"prim={int(r['prim'])} k={r['bk']} minslack={r['min_slack']} "
              f"nu={r['nu']} lam={r['lam']} mu={r['mu']}")


if __name__ == "__main__":
    main()
