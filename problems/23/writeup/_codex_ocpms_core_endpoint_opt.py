"""Enumerate endpoint optima for fixed core weights in the seven-cut PMS lemma."""

from itertools import product

import _codex_ocpms_descent_gate as d


CORE_IDX = (0, 3, 4, 5, 6, 8)
END_IDX = (1, 2, 7, 9)


def assemble(core, end):
    w = [None] * 10
    for i, v in zip(CORE_IDX, core):
        w[i] = v
    for i, v in zip(END_IDX, end):
        w[i] = v
    return tuple(w)


def active_constraints(w):
    w0, w1, w2, w3, w4, w5, w6, w7, w8, w9 = w
    m = w1 * w9 + w2 * w7 + w7 * w9
    vals = [
        ("w5=w9", w5 - w9),
        ("w6=w7", w6 - w7),
        ("w3+w5=w2+w9", w3 + w5 - w2 - w9),
        ("w4+w6=w1+w7", w4 + w6 - w1 - w7),
        ("A=w0w6+w3w8+w5w8", w0 * w6 + w3 * w8 + w5 * w8 - m),
        ("B=w0w5+w3w8+w5w8", w0 * w5 + w3 * w8 + w5 * w8 - m),
        ("C=w0w6+w4w8+w6w8", w0 * w6 + w4 * w8 + w6 * w8 - m),
    ]
    return tuple(name for name, val in vals if val == 0)


def main():
    max_core = 4
    worst = None
    hist = {}
    for core in product(range(1, max_core + 1), repeat=len(CORE_IDX)):
        # endpoint variables are bounded by w7<=w6, w9<=w5 and two sum constraints.
        w0, w3, w4, w5, w6, w8 = core
        best = None
        best_w = None
        for w1 in range(1, w4 + w6):
            for w2 in range(1, w3 + w5):
                for w7 in range(1, w6 + 1):
                    for w9 in range(1, w5 + 1):
                        w = assemble(core, (w1, w2, w7, w9))
                        if not d.feasible(w):
                            continue
                        mar = d.margin(w)
                        if best is None or mar < best:
                            best = mar
                            best_w = w
        if best_w is None:
            continue
        act = active_constraints(best_w)
        hist[act] = hist.get(act, 0) + 1
        if worst is None or best < worst[0]:
            worst = (best, best_w, act)
    print("worst", worst)
    print("active pattern histogram")
    for act, count in sorted(hist.items(), key=lambda kv: (-kv[1], kv[0]))[:80]:
        print(count, act)


if __name__ == "__main__":
    main()
