"""Independent re-verification of a candidate hit.

* full profile P(0..D+2) recomputed with ENGINE B (LR rule, not hives)
* INDEPENDENT interpolation: Lagrange (not Newton), exact Fractions
* INDEPENDENT h*: from the power series identity
      sum_n P(n) t^n  =  (sum_j h*_j t^j) / (1-t)^{d+1}
  i.e. h*_j = sum_{i} (-1)^i C(d+1,i) P(j-i)   recomputed from scratch here
* interior count h*_d cross-checked by Ehrhart-Macdonald reciprocity
  (-1)^d P(-1)
Usage: python fam2_verify_hit.py hits.jsonl out.json
"""
import sys, os, json
from fractions import Fraction
from math import comb
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, r"E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/tier0")
import tier0_screen as T


def lagrange(nodes):
    """nodes: list of (x, y).  Returns coefficient list low->high (Fractions)."""
    n = len(nodes)
    coeffs = [Fraction(0)] * n
    for i, (xi, yi) in enumerate(nodes):
        # basis poly prod_{j!=i} (x - xj)/(xi - xj)
        num = [Fraction(1)]
        den = Fraction(1)
        for j, (xj, _) in enumerate(nodes):
            if j == i:
                continue
            new = [Fraction(0)] * (len(num) + 1)
            for k, c in enumerate(num):
                new[k + 1] += c
                new[k] += c * (-xj)
            num = new
            den *= (xi - xj)
        f = Fraction(yi) / den
        for k, c in enumerate(num):
            coeffs[k] += c * f
    return coeffs


def pev(co, x):
    s = Fraction(0)
    for c in reversed(co):
        s = s * x + c
    return s


def hstar_indep(profile, d):
    return [sum((-1) ** i * comb(d + 1, i) * profile[j - i]
                for i in range(0, j + 1)) for j in range(0, d + 1)]


def verify(rec):
    lam, mu, nu = rec["lam"], rec["mu"], rec["nu"]
    D = (len(nu) - 1) * (len(nu) - 2) // 2
    jobs = [(tuple(n * x for x in lam), tuple(n * x for x in mu),
             tuple(n * x for x in nu)) for n in range(D + 3)]
    valsB = T.engineB_batch(jobs)
    valsA = T.engineA_batch(jobs)
    out = {"lam": lam, "mu": mu, "nu": nu, "D": D,
           "engineB_profile": [str(v) for v in valsB],
           "engineA_profile": [str(v) for v in valsA],
           "screen_profile": rec["profile"]}
    okAB = (valsA == valsB)
    out["engineA_equals_engineB"] = okAB
    out["engineB_equals_screen"] = ([str(v) for v in valsB] ==
                                    [str(v) for v in rec["profile"]])
    if not all(isinstance(v, int) for v in valsB):
        out["verdict"] = "ENGINE_B_INCOMPLETE"
        return out
    co = lagrange([(n, valsB[n]) for n in range(D + 1)])
    while co and co[-1] == 0:
        co.pop()
    d = len(co) - 1
    out["lagrange_coeffs"] = [str(c) for c in co]
    out["d_independent"] = d
    out["heldout_independent"] = [
        {"n": n, "engineB": valsB[n], "poly": str(pev(co, n)),
         "match": pev(co, n) == valsB[n]} for n in (D + 1, D + 2)]
    h = hstar_indep({n: valsB[n] for n in range(D + 3)}, d)
    out["hstar_independent"] = h
    out["hstar_matches_screen"] = (h == rec["hstar"])
    out["hstar_d_independent"] = h[d] if d >= 0 else None
    out["hstar_1_independent"] = h[1] if d >= 1 else None
    out["reciprocity_interior"] = str((-1) ** d * pev(co, -1))
    out["reciprocity_ok"] = ((-1) ** d * pev(co, -1) == h[d])
    out["TIER0_independent"] = bool(d >= 1 and h[1] == 0 and h[d] > 0)
    out["JACKPOT_independent"] = bool(d >= 1 and h[d] > h[1])
    out["NEG_independent"] = any(c < 0 for c in co)
    out["verdict"] = ("CONFIRMED" if (okAB and out["engineB_equals_screen"]
                                      and out["hstar_matches_screen"]
                                      and all(x["match"] for x in out["heldout_independent"])
                                      and out["reciprocity_ok"])
                      else "DISCREPANCY")
    return out


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    recs = [json.loads(l) for l in open(src) if l.strip()]
    res = [verify(r) for r in recs]
    json.dump(res, open(dst, "w"), indent=1)
    for r in res:
        print(r["verdict"], r["lam"], r["mu"], r["nu"],
              "TIER0=%s JACKPOT=%s NEG=%s" % (r.get("TIER0_independent"),
                                              r.get("JACKPOT_independent"),
                                              r.get("NEG_independent")))
