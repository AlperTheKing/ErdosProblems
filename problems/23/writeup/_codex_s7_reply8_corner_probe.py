"""Exact bounded probes for S7 Reply 8 YCOR/YXCOR corner gates.

This is a formula-stabilization gate, not a final proof certificate.  It uses
integer arithmetic on the cleared numerator e*Y*Z*Phi and searches bounded
positive integer structural variables.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def invariants(a, b, c, d, e, f):
    Y = a * c + b * f + c * f
    R = b + c
    D = d + e
    Z = e * Y + d * f * R
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    S = a + b + c + d + e + f
    Ms = {
        4: Y,
        5: a * e + b * f + c * f,
        6: a * c + d * f + e * f,
        7: a * e + d * f + e * f,
    }
    return Y, R, D, Z, A, B, S, Ms


def cleared_phi(Y, Z, A, B, S, M, N, x, q, v, e):
    # e*Y*Z * [2(N^2-25M) - 75(x*q*A/Z + v*B/(eY) - S)]
    eY = e * Y
    eYZ = eY * Z
    return 2 * eYZ * (N * N - 25 * M) - 75 * (eY * x * q * A + Z * v * B - eYZ * S)


def feasible_other_slacks(Ms, j):
    Mj = Ms[j]
    return all(Mk >= Mj for Mk in Ms.values())


def search(bound):
    out = {
        "bound": bound,
        "YCOR": {str(j): {"checked": 0, "violations": [], "min_pi": None, "min_point": None} for j in range(4, 8)},
        "YXCOR": {str(j): {"checked": 0, "violations": [], "min_pi": None, "min_point": None} for j in range(4, 8)},
    }
    for a in range(1, bound + 1):
      for b in range(1, bound + 1):
       for c in range(1, bound + 1):
        for d in range(1, bound + 1):
         for e in range(1, bound + 1):
          for f in range(1, bound + 1):
            Y, R, D, Z, A, B, S, Ms = invariants(a, b, c, d, e, f)
            if R < 2:
                continue
            for q in range(1, D + 1):
                for j, M in Ms.items():
                    if not feasible_other_slacks(Ms, j):
                        continue
                    # YCOR: y=1, s3=0, x=R-1, M=x*q+v.
                    x = R - 1
                    v = M - x * q
                    u = q - v
                    if v >= 1 and u >= 1 and v <= e:
                        N = S + R + q
                        pi = cleared_phi(Y, Z, A, B, S, M, N, x, q, v, e)
                        rec = out["YCOR"][str(j)]
                        rec["checked"] += 1
                        if rec["min_pi"] is None or pi < rec["min_pi"]:
                            rec["min_pi"] = pi
                            rec["min_point"] = [a, b, c, d, e, f, q, x, u, v]
                        if pi < 0 and len(rec["violations"]) < 5:
                            rec["violations"].append({"pi": pi, "point": [a, b, c, d, e, f, q, x, u, v]})
                    # YXCOR: x=y=1, M=q+v.
                    x = 1
                    v = M - q
                    u = q - v
                    if v >= 1 and u >= 1 and v <= e:
                        N = S + 2 + q
                        pi = cleared_phi(Y, Z, A, B, S, M, N, x, q, v, e)
                        rec = out["YXCOR"][str(j)]
                        rec["checked"] += 1
                        if rec["min_pi"] is None or pi < rec["min_pi"]:
                            rec["min_pi"] = pi
                            rec["min_point"] = [a, b, c, d, e, f, q, x, u, v]
                        if pi < 0 and len(rec["violations"]) < 5:
                            rec["violations"].append({"pi": pi, "point": [a, b, c, d, e, f, q, x, u, v]})
    verdict = "PASS" if all(not rec["violations"] for fam in ("YCOR", "YXCOR") for rec in out[fam].values()) else "FAIL"
    out["verdict"] = verdict
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bound", type=int, default=6)
    ap.add_argument("--summary", default="")
    args = ap.parse_args()
    out = search(args.bound)
    print("VERDICT", out["verdict"], "bound", args.bound)
    for fam in ("YCOR", "YXCOR"):
        for j in range(4, 8):
            rec = out[fam][str(j)]
            print(fam, j, "checked", rec["checked"], "min_pi", rec["min_pi"], "viol", len(rec["violations"]), "min_point", rec["min_point"])
    if args.summary:
        Path(args.summary).write_text(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
