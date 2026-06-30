"""Gate arbitrary subset-decrement descent for the seven-cut PMS lemma."""

from itertools import combinations, product
import random

import _codex_ocpms_descent_gate as d


def subset_descent_options(w):
    base = d.margin(w)
    positive = [i for i, v in enumerate(w) if v > 1]
    out = []
    for r in range(1, len(positive) + 1):
        for subset in combinations(positive, r):
            ww = list(w)
            for i in subset:
                ww[i] -= 1
            ww = tuple(ww)
            if d.feasible(ww) and d.margin(ww) <= base:
                out.append((subset, d.margin(ww) - base, ww))
                return out
    return out


def scan_box(max_w):
    feasible = fail = 0
    hist = {}
    for w in product(range(1, max_w + 1), repeat=10):
        if not d.feasible(w):
            continue
        feasible += 1
        if all(v == 1 for v in w):
            continue
        opts = subset_descent_options(w)
        if not opts:
            fail += 1
            print("FAIL", w, "margin", d.margin(w))
            return False
        size = len(opts[0][0])
        hist[size] = hist.get(size, 0) + 1
    print("box", max_w, "feasible", feasible, "fail", fail, "hist", hist)
    return True


def scan_random(trials, max_w):
    rng = random.Random(20260630)
    feasible = fail = 0
    hist = {}
    for _ in range(trials):
        w = tuple(rng.randint(1, max_w) for _ in range(10))
        if not d.feasible(w):
            continue
        feasible += 1
        if all(v == 1 for v in w):
            continue
        opts = subset_descent_options(w)
        if not opts:
            fail += 1
            print("RFAIL", w, "margin", d.margin(w))
            return False
        size = len(opts[0][0])
        hist[size] = hist.get(size, 0) + 1
    print("random", trials, max_w, "feasible", feasible, "fail", fail, "hist", hist)
    return True


if __name__ == "__main__":
    scan_box(4)
    scan_random(5000, 30)
