#!/usr/bin/env python3
"""Realized-vertex-denominator scan over genuine r=5 hive polytopes."""

import json
import random
import sys

from vertices5 import analyze


def rand_triple(rng, maxpart):
    lam = sorted((rng.randint(0, maxpart) for _ in range(5)), reverse=True)
    mu = sorted((rng.randint(0, maxpart) for _ in range(5)), reverse=True)
    tot = sum(lam) + sum(mu)
    if tot == 0:
        return None
    # random weakly decreasing nu with 5 parts summing to tot
    cuts = sorted(rng.randint(0, tot) for _ in range(4))
    comp = [cuts[0]] + [cuts[i] - cuts[i - 1] for i in range(1, 4)] + [tot - cuts[3]]
    nu = sorted(comp, reverse=True)
    return lam, mu, nu


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 11
    rng = random.Random(seed)
    counts, best, wit = {}, 1, None
    nonempty = 0
    tried = 0
    while tried < n:
        tried += 1
        t = rand_triple(rng, rng.choice([3, 4, 5, 6, 8, 10, 14]))
        if t is None:
            continue
        a = analyze(*t)
        if a is None:
            continue
        nonempty += 1
        for d in a["denoms"]:
            counts[d] = counts.get(d, 0) + 1
        if a["q"] > best:
            best = a["q"]
            wit = {k: a[k] for k in ("lam", "mu", "nu", "denoms", "q", "dim", "n_vertices")}
            print("new max q=%d  %s" % (best, wit), flush=True)
        if tried % 250 == 0:
            print("  tried=%d nonempty=%d max_q=%d denoms=%s"
                  % (tried, nonempty, best, sorted(counts)), flush=True)
    res = {"tried": tried, "nonempty": nonempty,
           "denominator_occurrence_counts": {str(k): v for k, v in sorted(counts.items())},
           "max_lcm_denominator_realized": best, "witness": wit, "seed": seed}
    print(json.dumps(res, indent=1))
    with open("scan_denoms_seed%d.json" % seed, "w") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
