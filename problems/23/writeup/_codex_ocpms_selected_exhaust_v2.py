"""Corrected exhaustive gate for the six-inequality PMS candidate.

This supersedes `_codex_ocpms_selected_exhaust.py`, whose numerator omitted
the endpoint contribution `w1+w2+w7+w9` in I(P).
"""

from itertools import product


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


def run(max_w):
    total = 0
    selected = 0
    neg = 0
    min_num = None
    min_w = None
    for w in product(range(1, max_w + 1), repeat=10):
        total += 1
        if not selected_ok(w):
            continue
        selected += 1
        num = margin_numer(w)
        if min_num is None or num < min_num:
            min_num = num
            min_w = w
        if num < 0:
            neg += 1
            print("FAIL", w, "numer", num)
            break
    print("max_w", max_w, "total", total, "selected", selected, "neg", neg)
    print("min_numer", min_num, "at", min_w)


if __name__ == "__main__":
    run(4)
