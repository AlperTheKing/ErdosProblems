"""CEGIS-style search for a small maxcut-constraint subset for weighted PMS.

This is exploratory.  It searches integer quotient weights that satisfy the
currently selected flip inequalities but violate the PMS margin, then adds a
violated flip inequality.  A successful small subset is a proof target, not a
proof by itself.
"""

from fractions import Fraction as F
import random

import _codex_ocpms_weight_formula as wf


def canonical_constraints():
    b_edges = {tuple(sorted(e)) for e in wf.b_edges()}
    out = []
    for mask in range(1, (1 << wf.base_n) - 1):
        if not (mask & 1):
            continue
        coeff = []
        has_bad = False
        for a, b in sorted(wf.base_E):
            if ((mask >> a) & 1) ^ ((mask >> b) & 1):
                sign = 1 if (a, b) in b_edges else -1
                coeff.append((sign, a, b))
                has_bad |= sign < 0
        if has_bad:
            out.append((mask, tuple(coeff)))
    return out


def slack(constraint, w):
    return sum(sign * w[a] * w[b] for sign, a, b in constraint)


def fmt_mask(mask):
    return tuple(i for i in range(wf.base_n) if (mask >> i) & 1)


def margin(w):
    i_val = wf.weighted_I_for_row(w)
    n_val = sum(w)
    m_val = sum(w[a] * w[b] for a, b in wf.m_edges())
    return 2 * (n_val * n_val - 25 * m_val) - 75 * (i_val - n_val)


def random_weight(rng, max_w):
    return tuple(rng.randint(1, max_w) for _ in range(wf.base_n))


def main():
    rng = random.Random(20260630)
    constraints = canonical_constraints()

    selected = set()
    for idx, (mask, _c) in enumerate(constraints):
        size = bin(mask).count("1")
        if size in (1, wf.base_n - 1):
            selected.add(idx)

    print("constraints", len(constraints), "initial", len(selected))

    for round_no in range(30):
        bad = None
        checked = 0
        for _ in range(20000):
            w = random_weight(rng, 12)
            if all(slack(constraints[i][1], w) >= 0 for i in selected):
                checked += 1
                mar = margin(w)
                if mar < 0:
                    bad = (w, mar)
                    break
        if bad is None:
            print("round", round_no, "no sampled bad", "selected", len(selected), "checked", checked)
            continue

        w, mar = bad
        violated = [
            (slack(c, w), idx, mask)
            for idx, (mask, c) in enumerate(constraints)
            if slack(c, w) < 0
        ]
        violated.sort()
        print("round", round_no, "bad", w, "margin", mar, "violated", len(violated))
        if not violated:
            print("ALL-CONSTRAINT PMS FAILURE", w, mar)
            return
        _s, idx, mask = violated[0]
        selected.add(idx)
        print("  add", fmt_mask(mask), "slack", _s)

    print("selected masks:")
    for idx in sorted(selected):
        mask, c = constraints[idx]
        print(fmt_mask(mask), c)


if __name__ == "__main__":
    main()
