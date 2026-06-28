"""Check GPT-Pro's tight-cap descent condition on SPLIT-bad L=5 rows.

For a unique L=5 bad row f=v0v4 with path v0-v1-v2-v3-v4, compute the
central-overload defect D and the four cap rotations:

  W0={v0}, W4={v4}, W01={v0,v1}, W34={v3,v4}.

Report whether any defect-lowering cap is max-cut tight:

  lambda(W) = delta_B(W) - delta_M(W) = 0.

This is a necessary local gate for the proposed tight-cap descent lemma.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F

from _h import dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins


def split_rows(n, adj, side):
    st = struct_for_side(n, adj, list(side))
    if st is None:
        return []
    M, ell, _T, _mu, cyc = st
    S = [F(0) for _ in range(n)]
    pf = {}
    for g in M:
        paths = cyc[g]
        d = {}
        for path in paths:
            for v in path:
                d[v] = d.get(v, F(0)) + F(1, len(paths))
        pf[g] = d
        for v, x in d.items():
            S[v] += x

    rows = []
    for f in sorted(M):
        if ell[f] != 5 or len(cyc[f]) != 1:
            continue
        path = tuple(cyc[f][0])
        A = tuple(S[v] for v in path)
        D = central_defect(A, n)
        if D > 0 and sum(A) <= n:
            rows.append((f, path, A, D))
    return rows


def central_defect(A, n):
    return max(F(0), min(A[2] - F(n, 5), A[1] + A[2] + A[3] - F(3 * n, 5)))


def rotated_A(A, cap_name):
    a0, a1, a2, a3, a4 = A
    if cap_name == "W0":
        return (a0, a4, a3, a2, a1)
    if cap_name == "W4":
        return (a4, a0, a1, a2, a3)
    if cap_name == "W01":
        return (a1, a0, a4, a3, a2)
    if cap_name == "W34":
        return (a3, a4, a0, a1, a2)
    raise ValueError(cap_name)


def lambda_cap(adj, side, W):
    W = set(W)
    delta_b = 0
    delta_m = 0
    for u in W:
        for v in adj[u]:
            if u < v and v not in W or v < u and v not in W:
                if side[u] != side[v]:
                    delta_b += 1
                else:
                    delta_m += 1
    return delta_b - delta_m, delta_b, delta_m


def cap_vertices(path, cap_name):
    v0, v1, _v2, v3, v4 = path
    if cap_name == "W0":
        return (v0,)
    if cap_name == "W4":
        return (v4,)
    if cap_name == "W01":
        return (v0, v1)
    if cap_name == "W34":
        return (v3, v4)
    raise ValueError(cap_name)


def analyze_cut(n, adj, side):
    out = []
    for f, path, A, D in split_rows(n, adj, side):
        caps = []
        for name in ("W0", "W4", "W01", "W34"):
            Ap = rotated_A(A, name)
            Dp = central_defect(Ap, n)
            lam, db, dm = lambda_cap(adj, side, cap_vertices(path, name))
            caps.append(
                {
                    "name": name,
                    "vertices": cap_vertices(path, name),
                    "Dprime": Dp,
                    "lowers": Dp < D,
                    "lambda": lam,
                    "delta_B": db,
                    "delta_M": dm,
                }
            )
        out.append({"f": f, "path": path, "A": A, "D": D, "caps": caps})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("g6")
    ap.add_argument("--side-index", type=int, default=None)
    ap.add_argument("--all-cuts", action="store_true")
    args = ap.parse_args()

    n, edges = dec(args.g6)
    adj, cuts = gmins(n, edges)
    targets = range(len(cuts)) if args.all_cuts else [args.side_index or 0]
    print(f"g6={args.g6} n={n} gamma_min_cuts={len(cuts)}")
    for idx in targets:
        side = tuple(int(x) for x in cuts[idx])
        rows = analyze_cut(n, adj, side)
        print(f"cut={idx} side={cuts[idx]} rows={len(rows)}")
        for row in rows:
            print(
                " row",
                row["f"],
                "path",
                row["path"],
                "A",
                tuple(str(x) for x in row["A"]),
                "D",
                row["D"],
            )
            tight_lower = [c for c in row["caps"] if c["lowers"] and c["lambda"] == 0]
            print("  tight_lower_count", len(tight_lower))
            for cap in row["caps"]:
                print(
                    "  cap",
                    cap["name"],
                    cap["vertices"],
                    "D'",
                    cap["Dprime"],
                    "lowers",
                    cap["lowers"],
                    "lambda",
                    cap["lambda"],
                    "dB",
                    cap["delta_B"],
                    "dM",
                    cap["delta_M"],
                )


if __name__ == "__main__":
    main()
