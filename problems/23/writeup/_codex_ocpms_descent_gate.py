"""Gate a one-coordinate descent certificate for the seven-cut PMS lemma."""

from fractions import Fraction as F
from itertools import product
import random

import _codex_ocpms_weight_formula as wf
import _codex_ocpms_selected_exhaust_v2 as seven


def feasible(w):
    if not seven.selected_ok(w):
        return False
    w0, w1, w2, w3, w4, w5, w6, w7, w8, w9 = w
    m = w1 * w9 + w2 * w7 + w7 * w9
    return w0 * w6 + w4 * w8 + w6 * w8 >= m


def margin(w):
    n = sum(w)
    m = sum(w[a] * w[b] for a, b in wf.m_edges())
    return F(2 * (n * n - 25 * m), 1) - 75 * (wf.weighted_I_for_row(w) - n)


def descent_options(w):
    base = margin(w)
    out = []
    for i, val in enumerate(w):
        if val <= 1:
            continue
        ww = list(w)
        ww[i] -= 1
        ww = tuple(ww)
        if feasible(ww):
            mm = margin(ww)
            if mm <= base:
                out.append((i, mm - base))
    return out


def scan_box(max_w):
    total = feasible_count = fail = 0
    hist = {}
    for w in product(range(1, max_w + 1), repeat=10):
        total += 1
        if not feasible(w):
            continue
        feasible_count += 1
        if all(v == 1 for v in w):
            continue
        opts = descent_options(w)
        if not opts:
            fail += 1
            print("FAIL", w, "margin", margin(w))
            return False
        hist[opts[0][0]] = hist.get(opts[0][0], 0) + 1
    print("box", max_w, "total", total, "feasible", feasible_count, "fail", fail, "hist", hist)
    return True


def scan_random(trials, max_w):
    rng = random.Random(20260630)
    feasible_count = fail = 0
    hist = {}
    for _ in range(trials):
        w = tuple(rng.randint(1, max_w) for _ in range(10))
        if not feasible(w):
            continue
        feasible_count += 1
        if all(v == 1 for v in w):
            continue
        opts = descent_options(w)
        if not opts:
            fail += 1
            print("RFAIL", w, "margin", margin(w))
            return False
        hist[opts[0][0]] = hist.get(opts[0][0], 0) + 1
    print("random", trials, max_w, "feasible", feasible_count, "fail", fail, "hist", hist)
    return True


if __name__ == "__main__":
    scan_box(4)
    scan_random(10000, 30)
