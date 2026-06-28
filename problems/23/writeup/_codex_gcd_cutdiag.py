"""Cut-capacity diagnostic for GCD.

For H = L_omega + diag(N-T), indicator vectors give the necessary inequalities

    omega(delta A) + sum_{v in A} (N-T_v) >= 0.

Equivalently omega(delta A) >= sum_{v in A}(T_v-N).  This script checks how
sharp that subset condition is on named examples.  It is diagnostic only.
"""

from __future__ import annotations

import argparse
from fractions import Fraction as F

from _gcd import a_bar
from _h import dec, loads
from _superphi import blow


def omega_T(info):
    omega = {}
    for f in info["M"]:
        ae = a_bar(info["ell"][f])
        ps = info["cyc"][f]
        k = len(ps)
        ef = frozenset(f)
        omega[ef] = omega.get(ef, F(0)) + ae
        for p in ps:
            for i in range(len(p) - 1):
                e = frozenset((p[i], p[i + 1]))
                omega[e] = omega.get(e, F(0)) + ae * F(1, k)
    return omega, info["T"], info["n"]


def scan(info):
    omega, T, n = omega_T(info)
    best = None
    for mask in range(1, (1 << n) - 1):
        q = F(0)
        for e, w in omega.items():
            u, v = tuple(e)
            if ((mask >> u) & 1) != ((mask >> v) & 1):
                q += w
        for v in range(n):
            if (mask >> v) & 1:
                q += F(n) - T[v]
        if best is None or q < best[0]:
            best = (q, mask)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g6", default="I?BD@g]Qo")
    ap.add_argument("--blow", type=int, default=1)
    args = ap.parse_args()
    n, edges = dec(args.g6) if args.blow == 1 else blow(args.g6, args.blow)
    info = loads(n, edges)
    if info is None:
        raise SystemExit("loads() returned None")
    q, mask = scan(info)
    verts = [v for v in range(info["n"]) if (mask >> v) & 1]
    print(f"{args.g6}[{args.blow}] N={info['n']} min_indicator={q} = {float(q):+.9f} set={verts}")


if __name__ == "__main__":
    main()
