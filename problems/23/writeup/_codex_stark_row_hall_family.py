"""Test restricted subset families for STAR-K-multi row-Hall.

For each row-Hall configuration, compare the exact minimum Hall slack
over all nonempty bad-edge subsets against the minimum over the proposed
restricted family:

  singleton subsets, pair subsets, the full set, and 3-of-4 subsets.

If these minima are equal, checking only the restricted family proves
the full Hall condition for that configuration.
"""
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction as F
import argparse
import itertools
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

from _angleD_O1 import gmin_sides
from _codex_stark_row_hall_masks import row_demands
from _h import GENG, dec


def subset_slack(mask, demands, supports):
    d = sum((demands[i] for i in range(len(demands)) if (mask >> i) & 1), F(0))
    U = set()
    for i in range(len(demands)):
        if (mask >> i) & 1:
            U |= supports[i]
    return F(len(U)) - d, mask, len(U), d


def allowed_masks(m):
    out = set()
    for i in range(m):
        out.add(1 << i)
    for i in range(m):
        for j in range(i + 1, m):
            out.add((1 << i) | (1 << j))
    out.add((1 << m) - 1)
    if m == 4:
        for miss in range(4):
            out.add(((1 << 4) - 1) ^ (1 << miss))
    return out


def check_config(demands, supports):
    m = len(demands)
    if m == 0:
        return None
    best_all = min((subset_slack(mask, demands, supports) for mask in range(1, 1 << m)), key=lambda r: (r[0], r[1]))
    fam = allowed_masks(m)
    best_fam = min((subset_slack(mask, demands, supports) for mask in fam), key=lambda r: (r[0], r[1]))
    return best_all, best_fam


def check_g6(g6):
    n, E = dec(g6)
    adj, sides = gmin_sides(n, E)
    total = fail = 0
    first = None
    hist = {}
    for side in sides:
        for o, M, demands, supports in row_demands(n, adj, side):
            total += 1
            r = check_config(demands, supports)
            if r is None:
                continue
            best_all, best_fam = r
            m = len(M)
            key = "full" if best_all[1].bit_count() == m else best_all[1].bit_count()
            hist[key] = hist.get(key, 0) + 1
            if best_all[0] != best_fam[0]:
                fail += 1
                if first is None:
                    first = {
                        "g6": g6,
                        "side": "".join(map(str, side)),
                        "o": o,
                        "M_size": m,
                        "best_all": best_all,
                        "best_fam": best_fam,
                        "best_edges": [M[i] for i in range(m) if (best_all[1] >> i) & 1],
                        "fam_edges": [M[i] for i in range(m) if (best_fam[1] >> i) & 1],
                    }
    return total, fail, first, hist


def merge_hist(a, b):
    for k, v in b.items():
        a[k] = a.get(k, 0) + v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", type=int, default=11)
    ap.add_argument("--workers", type=int, default=min(61, os.cpu_count() or 1))
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()

    total = fail = 0
    first = None
    hist = {}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(check_g6, g6) for g6 in graphs]
        for fut in as_completed(futures):
            t, f, ex, h = fut.result()
            total += t
            fail += f
            merge_hist(hist, h)
            if ex is not None and first is None:
                first = ex
    print("workers", args.workers)
    print("N", args.n)
    print("configs", total)
    print("restricted_family_fail", fail)
    print("best_size_hist", hist)
    print("first", first)


if __name__ == "__main__":
    main()
