"""Scan the seven-cut PMS margin as crude endpoint part plus core reservoir."""

from fractions import Fraction as F
from itertools import product

import _codex_ocpms_descent_gate as d
import _codex_ocpms_endpoint_real_opt as er


def parts(w):
    w0, w1, w2, w3, w4, w5, w6, w7, w8, w9 = w
    core = (w0, w3, w4, w5, w6, w8)
    K, c19, c27, c79, _A, _B, _C = er.constants(core)
    # Convert float constants from er.constants back to exact formulas.
    z27 = w6 * (w0 * w5 + w3 * w8 + w5 * w8)
    a27 = w0 * w5 + w0 * w6 + w3 * w6 + w3 * w8 + w5 * w6 + w5 * w8 + w6 * w8
    z19 = w5 * (w0 * w6 + w4 * w8 + w6 * w8)
    a19 = w0 * w5 + w0 * w6 + w4 * w5 + w4 * w8 + w5 * w6 + w5 * w8 + w6 * w8
    z79 = w0 * w5 * w6 + w3 * w4 * w8 + w3 * w6 * w8 + w4 * w5 * w8 + w5 * w6 * w8
    a79 = (
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
    c19 = F(a19, z19)
    c27 = F(a27, z27)
    c79 = F(a79, z79)

    x, y, u, v = w1, w2, w7, w9
    s = x + y + u + v
    K = sum(core)
    f0 = 2 * (K + s) ** 2 + 75 * K - 225 * x * v - 225 * y * u - 200 * u * v
    reservoir = 75 * ((F(7, 3) - c19) * x * v + (F(7, 3) - c27) * y * u + (F(2, 1) - c79) * u * v)
    return F(f0, 1), reservoir, F(f0, 1) + reservoir


def main():
    max_w = 5
    count = 0
    crude_neg = 0
    min_margin = None
    min_ratio = None
    min_ratio_w = None
    worst_def = None
    for w in product(range(1, max_w + 1), repeat=10):
        if not d.feasible(w):
            continue
        count += 1
        f0, res, margin = parts(w)
        if min_margin is None or margin < min_margin[0]:
            min_margin = (margin, w, f0, res)
        if f0 < 0:
            crude_neg += 1
            ratio = res / (-f0)
            if min_ratio is None or ratio < min_ratio:
                min_ratio = ratio
                min_ratio_w = (w, f0, res, margin)
            if worst_def is None or f0 < worst_def[0]:
                worst_def = (f0, w, res, margin)
            if res + f0 < 0:
                print("FAIL", w, f0, res, margin)
                return
    print("max_w", max_w, "count", count, "crude_neg", crude_neg)
    print("min_margin", min_margin)
    print("min_ratio", min_ratio, "at", min_ratio_w)
    print("worst_crude", worst_def)


if __name__ == "__main__":
    main()
