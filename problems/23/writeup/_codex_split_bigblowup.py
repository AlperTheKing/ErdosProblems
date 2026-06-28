"""Odd-cycle blow-up quotient stress test for the symmetric split certificate.

For C_m[x_0,...,x_{m-1}] with a minimum-product bad adjacent class
V_a V_b, b=a+1 mod m, a fixed bad edge has layer contributions along the
complementary B-path:

    A_0 = x_b,
    A_i = x_a*x_b / x_{a-i mod m},  1 <= i <= m-2,
    A_{m-1} = x_a.

The split certificate asks for t with 1 <= t <= (m-1)/2 such that the
endpoint shells and complementary center interval obey proportional N/m
budgets.  This script tests that exact quotient condition with Fractions.
"""
from __future__ import annotations

import argparse
import random
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F


def contributions(parts, bad):
    m = len(parts)
    a = bad
    b = (bad + 1) % m
    nbad = parts[a] * parts[b]
    vals = [F(parts[b])]
    for step in range(1, m - 1):
        vals.append(F(nbad, parts[(a - step) % m]))
    vals.append(F(parts[a]))
    return vals


def split_ok(parts, bad, support12=False):
    m = len(parts)
    n = sum(parts)
    vals = contributions(parts, bad)
    half = m // 2
    best = None
    best_data = None
    max_t = min(2, half) if support12 else half
    for t in range(1, max_t + 1):
        outer = sum(vals[:t]) + sum(vals[m - t :])
        center = sum(vals[t : m - t])
        ogap = outer - F(2 * t * n, m)
        cgap = center - F((m - 2 * t) * n, m)
        margin = max(ogap, cgap)
        if best is None or margin < best:
            best = margin
            best_data = (t, outer, center, ogap, cgap, tuple(vals), sum(vals))
        if ogap <= 0 and cgap <= 0:
            return True, best_data, t
    return False, best_data, None


def random_parts(m, total, rng):
    parts = [1] * m
    for _ in range(total - m):
        if rng.random() < 0.75:
            idx = rng.randrange(m)
        else:
            idx = int(rng.random() ** 3 * m) % m
        parts[idx] += 1
    rng.shuffle(parts)
    return parts


def worker(args):
    m, total_min, total_max, count, seed, targeted, support12 = args
    rng = random.Random(seed)
    seen = 0
    fails = 0
    first_fail = None
    worst = None
    hist = {}
    for _ in range(count):
        if targeted and m == 7:
            x = rng.randint(1, 12)
            y = rng.randint(1, 12)
            A = rng.randint(max(10, total_min // 5), max(20, total_max // 2))
            B = rng.randint(max(2, total_min // 20), max(5, total_max // 4))
            C = rng.randint(max(2, total_min // 20), max(5, total_max // 4))
            parts = [x, A, B, y, C, y, A]
        else:
            total = rng.randint(total_min, total_max)
            parts = random_parts(m, total, rng)
        products = [parts[i] * parts[(i + 1) % m] for i in range(m)]
        minprod = min(products)
        for bad, prod in enumerate(products):
            if prod != minprod:
                continue
            ok, data, first_t = split_ok(parts, bad, support12=support12)
            seen += 1
            if ok:
                hist[(m, first_t)] = hist.get((m, first_t), 0) + 1
            if not ok:
                fails += 1
                if first_fail is None:
                    first_fail = (tuple(parts), bad, data)
            if worst is None or data[3] > worst[2][3] or data[4] > worst[2][4]:
                # Keep the largest individual gap among best splits.
                worst = (tuple(parts), bad, data)
    return seen, fails, first_fail, worst, hist


def fmt(x):
    return f"{x} ({float(x):+.6g})"


def check_named(support12=False):
    named = [
        ((3, 423, 173, 7, 176, 7, 423), 2),
        ((5, 715, 303, 12, 304, 12, 715), 0),
        ((5, 715, 303, 12, 304, 12, 715), 6),
    ]
    for parts, bad in named:
        ok, data, first_t = split_ok(list(parts), bad, support12=support12)
        print(f"named parts={parts} bad={bad} ok={ok} first_t={first_t} data={data}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m", type=int, default=7)
    ap.add_argument("--samples", type=int, default=100000)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--min-n", type=int, default=20)
    ap.add_argument("--max-n", type=int, default=4000)
    ap.add_argument("--seed", type=int, default=2806)
    ap.add_argument("--target-c7", action="store_true")
    ap.add_argument("--named", action="store_true")
    ap.add_argument("--support12", action="store_true")
    args = ap.parse_args()
    if args.named:
        check_named(support12=args.support12)

    per = (args.samples + args.workers - 1) // args.workers
    jobs = []
    for w in range(args.workers):
        c = min(per, max(0, args.samples - w * per))
        if c:
            jobs.append((args.m, args.min_n, args.max_n, c, args.seed + 1009 * w, args.target_c7, args.support12))

    total_seen = total_fails = 0
    first_fail = None
    worst = None
    hist = {}
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for seen, fails, ff, ww, hh in ex.map(worker, jobs):
            total_seen += seen
            total_fails += fails
            for key, val in hh.items():
                hist[key] = hist.get(key, 0) + val
            if first_fail is None and ff is not None:
                first_fail = ff
            if ww is not None:
                if worst is None:
                    worst = ww
                else:
                    old_gap = max(worst[2][3], worst[2][4])
                    new_gap = max(ww[2][3], ww[2][4])
                    if new_gap > old_gap:
                        worst = ww

    print(f"m={args.m} samples={args.samples} quotient_rows={total_seen} split_fails={total_fails}")
    print(f"first_fail={first_fail}")
    print(f"hist={sorted(hist.items())}")
    if worst:
        parts, bad, data = worst
        print(f"worst_best_split parts={parts} bad={bad}")
        print(f"  t={data[0]} outer={data[1]} center={data[2]}")
        print(f"  outer_gap={fmt(data[3])} center_gap={fmt(data[4])}")
        print(f"  vals={data[5]} rowsum={data[6]} N={sum(parts)}")


if __name__ == "__main__":
    main()
