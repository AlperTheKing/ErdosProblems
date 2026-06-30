"""Exact gates for the seven-cut equality-atom PMS candidate.

The target implication is:

  seven quotient flip inequalities
      => 75*(I(P)-N) <= 2*(N^2 - 25*m)

for the N=10 equality atom row P=(7,5,8,6,9).  The margin is checked by an
integer numerator after multiplying by the positive denominator Z27*Z19*Z79.
"""

import argparse
import random
from itertools import product
from multiprocessing import Pool


def selected_ok(w):
    w0, w1, w2, w3, w4, w5, w6, w7, w8, w9 = w
    m = w1 * w9 + w2 * w7 + w7 * w9
    return (
        w5 >= w9
        and w6 >= w7
        and w3 + w5 >= w2 + w9
        and w4 + w6 >= w1 + w7
        and w0 * w6 + w3 * w8 + w5 * w8 >= m
        and w0 * w5 + w3 * w8 + w5 * w8 >= m
        and w0 * w6 + w4 * w8 + w6 * w8 >= m
    )


def margin_numer(w):
    w0, w1, w2, w3, w4, w5, w6, w7, w8, w9 = w
    z27 = w6 * (w0 * w5 + w3 * w8 + w5 * w8)
    i27 = w0 * w5 + w0 * w6 + w3 * w6 + w3 * w8 + w5 * w6 + w5 * w8 + w6 * w8

    z19 = w5 * (w0 * w6 + w4 * w8 + w6 * w8)
    i19 = w0 * w5 + w0 * w6 + w4 * w5 + w4 * w8 + w5 * w6 + w5 * w8 + w6 * w8

    z79 = (
        w0 * w5 * w6
        + w3 * w4 * w8
        + w3 * w6 * w8
        + w4 * w5 * w8
        + w5 * w6 * w8
    )
    i79 = (
        w0 * w5
        + w0 * w6
        + w3 * w4
        + w3 * w6
        + w3 * w8
        + w4 * w5
        + w4 * w8
        + w5 * w6
        + w5 * w8
        + w6 * w8
    )

    n = sum(w)
    m = w1 * w9 + w2 * w7 + w7 * w9
    endpoint = w1 + w2 + w7 + w9
    base = 2 * (n * n - 25 * m) - 75 * (endpoint - n)
    den = z27 * z19 * z79
    numer = base * den
    numer -= 75 * w2 * w7 * i27 * z19 * z79
    numer -= 75 * w1 * w9 * i19 * z27 * z79
    numer -= 75 * w7 * w9 * i79 * z27 * z19
    return numer


def random_worker(args):
    seed, samples, max_weight = args
    rng = random.Random(seed)
    selected = 0
    min_num = None
    min_w = None
    first_fail = None
    for _ in range(samples):
        w = tuple(rng.randint(1, max_weight) for _ in range(10))
        if not selected_ok(w):
            continue
        selected += 1
        num = margin_numer(w)
        if min_num is None or num < min_num:
            min_num = num
            min_w = w
        if num < 0 and first_fail is None:
            first_fail = (w, num)
            break
    return selected, min_num, min_w, first_fail


def run_random(samples, max_weight, workers, seed):
    workers = max(1, min(workers, samples))
    base = samples // workers
    rem = samples % workers
    jobs = [
        (seed + 1000003 * i, base + (1 if i < rem else 0), max_weight)
        for i in range(workers)
    ]
    if workers == 1:
        results = [random_worker(jobs[0])]
    else:
        with Pool(workers) as pool:
            results = pool.map(random_worker, jobs)
    selected = sum(r[0] for r in results)
    min_num = None
    min_w = None
    first_fail = None
    for _sel, num, w, fail in results:
        if fail is not None and first_fail is None:
            first_fail = fail
        if num is not None and (min_num is None or num < min_num):
            min_num = num
            min_w = w
    return selected, min_num, min_w, first_fail


def run_exhaustive(max_weight):
    total = 0
    selected = 0
    min_num = None
    min_w = None
    first_fail = None
    for w in product(range(1, max_weight + 1), repeat=10):
        total += 1
        if not selected_ok(w):
            continue
        selected += 1
        num = margin_numer(w)
        if min_num is None or num < min_num:
            min_num = num
            min_w = w
        if num < 0:
            first_fail = (w, num)
            break
    return total, selected, min_num, min_w, first_fail


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("random", "exhaustive"), default="random")
    parser.add_argument("--samples", type=int, default=1_000_000)
    parser.add_argument("--max-weight", type=int, default=50)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--seed", type=int, default=230623)
    args = parser.parse_args()

    if args.mode == "exhaustive":
        total, selected, min_num, min_w, first_fail = run_exhaustive(args.max_weight)
        print("mode exhaustive")
        print("max_weight", args.max_weight, "total", total, "selected", selected)
    else:
        selected, min_num, min_w, first_fail = run_random(
            args.samples, args.max_weight, args.workers, args.seed
        )
        print("mode random")
        print("samples", args.samples, "max_weight", args.max_weight, "workers", args.workers, "selected", selected)
    print("min_numer", min_num, "at", min_w)
    print("first_fail", first_fail or "")
    print("VERDICT", "PASS" if first_fail is None else "FAIL")


if __name__ == "__main__":
    main()
