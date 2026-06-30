"""List quotient flip constraints for the N=10 OC-PMS equality atom."""

from itertools import combinations

import _codex_ocpms_weight_formula as wf


def coeffs(subset):
    s = set(subset)
    b_edges = {tuple(sorted(e)) for e in wf.b_edges()}
    out = {}
    for a, b in sorted(wf.base_E):
        if (a in s) ^ (b in s):
            out[(a, b)] = 1 if (a, b) in b_edges else -1
    return out


def fmt(c):
    plus = []
    minus = []
    for edge, sign in sorted(c.items()):
        term = f"w{edge[0]}w{edge[1]}"
        if sign > 0:
            plus.append(term)
        else:
            minus.append(term)
    lhs = " + ".join(plus) if plus else "0"
    rhs = " + ".join(minus) if minus else "0"
    return f"{lhs} >= {rhs}"


def delta_value(c, weights):
    return sum(sign * weights[a] * weights[b] for (a, b), sign in c.items())


def main():
    weights = (3, 3, 3, 3, 3, 2, 2, 2, 2, 2)
    rows = []
    for size in range(1, wf.base_n + 1):
        for subset in combinations(range(wf.base_n), size):
            # Identify complements to avoid printing both S and V-S.
            if 0 not in subset:
                continue
            c = coeffs(subset)
            if any(sign < 0 for sign in c.values()):
                rows.append((delta_value(c, weights), subset, c))
    rows.sort(key=lambda item: (item[0], len(item[1]), item[1]))

    print("weights", weights)
    print("row", wf.BASE_ROW)
    print("nontrivial canonical constraints", len(rows))
    print("first 80 by slack:")
    for slack, subset, c in rows[:80]:
        print(f"slack={slack:4d} S={subset}: {fmt(c)}")


if __name__ == "__main__":
    main()
