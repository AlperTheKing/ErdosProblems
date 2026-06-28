"""Dump full-set ROWSUM compensation terms.

For fixed overloaded row o, define s_v=sum_{op in O}K[op,v].
The full-set ROWSUM demand is

    D_o = s_o + sum_{q in Q} K[o,q] s_q/(R_q+s_q).

The raw capped-support upper proxy is

    U_o = s_o + sum_{q in Q} min(1,s_q),

which is false as a bound by N.  This script dumps the exact surplus

    L_o = sum_Q (min(1,s_q) - K[o,q]s_q/(R_q+s_q))

that must pay the raw deficit U_o-N.
"""
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction as F
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

from _angleD_O1 import gmin_sides
from _h import GENG, dec
from _test_fullg import build_K


def frac(x):
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def check_g6(g6):
    n, E = dec(g6)
    adj, sides = gmin_sides(n, E)
    rows = []
    for side in sides:
        r = build_K(adj, side, n)
        if r is None:
            continue
        K, T = r
        O = [v for v in range(n) if T[v] > n]
        Q = [v for v in range(n) if T[v] <= n]
        if not O:
            continue
        s = [sum(K[op][v] for op in O) for v in range(n)]
        qcap = sum(min(F(1), s[q]) for q in Q)
        support = [v for v in range(n) if s[v] > 0]
        idle = [v for v in range(n) if s[v] == 0]
        for o in O:
            qterms = []
            weighted = F(0)
            surplus = F(0)
            for q in Q:
                R = F(n) - T[q]
                den = R + s[q]
                if den <= 0:
                    continue
                w = K[o][q] * s[q] / den
                c = min(F(1), s[q])
                weighted += w
                surplus += c - w
                if s[q] or K[o][q]:
                    qterms.append((q, s[q], T[q], K[o][q], R, den, c, w, c - w))
            demand = s[o] + weighted
            raw = s[o] + qcap
            rec = {
                "rowslack": F(n) - demand,
                "rawdef": raw - F(n),
                "surplus": surplus,
                "g6": g6,
                "side": "".join(map(str, side)),
                "o": o,
                "N": n,
                "O": tuple(O),
                "T_O": tuple((v, T[v]) for v in O),
                "s_o": s[o],
                "qcap": qcap,
                "weighted": weighted,
                "demand": demand,
                "raw": raw,
                "support_size": len(support),
                "idle": tuple(idle),
                "qterms": tuple(qterms),
            }
            rows.append(rec)
    return rows


def fmt(rec):
    keys = [
        "rowslack",
        "rawdef",
        "surplus",
        "g6",
        "side",
        "o",
        "N",
        "O",
        "s_o",
        "qcap",
        "weighted",
        "demand",
        "raw",
        "support_size",
        "idle",
    ]
    out = {}
    for k in keys:
        v = rec[k]
        if isinstance(v, F):
            out[k] = frac(v)
        elif isinstance(v, tuple):
            out[k] = tuple((a, frac(b)) if isinstance(b, F) else (a, b) for a, b in v) if k == "T_O" else v
        else:
            out[k] = v
    out["T_O"] = tuple((v, frac(t)) for v, t in rec["T_O"])
    out["qterms"] = tuple(
        (q, frac(s), frac(T), frac(a), frac(R), frac(den), frac(cap), frac(w), frac(slack))
        for q, s, T, a, R, den, cap, w, slack in rec["qterms"]
    )
    return out


def main():
    workers = min(61, os.cpu_count() or 1)
    graphs = subprocess.run([GENG, "-tc", "11"], capture_output=True, text=True, check=True).stdout.split()
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(check_g6, g6) for g6 in graphs]
        for fut in as_completed(futures):
            rows.extend(fut.result())
    rows.sort(key=lambda r: (r["rowslack"], -r["rawdef"], r["g6"], r["side"], r["o"]))
    print("workers", workers)
    print("rows", len(rows))
    print("hardest_rowsum")
    for rec in rows[:12]:
        print(fmt(rec))
    rows_by_raw = sorted(rows, key=lambda r: (-r["rawdef"], r["rowslack"], r["g6"], r["side"], r["o"]))
    print("largest_rawdef")
    for rec in rows_by_raw[:12]:
        print(fmt(rec))


if __name__ == "__main__":
    main()
