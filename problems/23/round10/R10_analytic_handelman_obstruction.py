"""Exact Farkas gate for the coarse max-coordinate Handelman ansatz."""
from fractions import Fraction
from itertools import combinations_with_replacement

from R10_analytic_handelman import MONOMIALS, MONO_INDEX
from R10_analytic_probe import EDGES, N

SPECIAL = {(1, 6), (1, 8), (2, 6), (2, 9), (3, 7), (3, 10),
           (4, 8), (5, 9), (6, 10)}


def ell(coefficients):
    moments = []
    for i, j in MONOMIALS:
        moments.append(2 if (i, j) == (0, 0) else
                       1 if (i == 0 and j > 0) or (i, j) in SPECIAL else 0)
    return sum(a * b for a, b in zip(coefficients, moments))


def product(a, b):
    out = [0] * len(MONOMIALS)
    for i in range(N):
        out[MONO_INDEX[i, i]] = a[i] * b[i]
        for j in range(i + 1, N):
            out[MONO_INDEX[i, j]] = a[i] * b[j] + a[j] * b[i]
    return out


def cut(start, length):
    inside = {(start + j) % N for j in range(length)}
    out = [0] * len(MONOMIALS)
    for u, v in EDGES:
        if (u in inside) == (v in inside):
            out[MONO_INDEX[u, v]] = 1
    return out


def main():
    # Pair identity: q_(i,4)-q_(i,5)=x_(i+4)(p_i-x_i).
    for i in range(N):
        lhs = [a - b for a, b in zip(cut(i, 4), cut(i, 5))]
        unit = [0] * N
        unit[(i + 4) % N] = 1
        sign = [0] * N
        for offset in (-3, -2, -1):
            sign[(i + offset) % N] += 1
        sign[i] -= 1
        assert lhs == product(unit, sign)
    # Exact equality witness for the 22-cut inequality.
    witness = [Fraction(1, 5) if i in {0, 1, 4, 5, 8} else Fraction(0) for i in range(N)]
    witness_values = [sum(witness[u] * witness[v] for u, v in EDGES
                          if (((u - start) % N < length) == ((v - start) % N < length)))
                      for length in (4, 5) for start in range(N)]
    assert min(witness_values) == Fraction(1, 25)
    assert set(witness_values) == {Fraction(1, 25), Fraction(3, 25)}


    # Cone generators for C_0={x>=0, x_0>=x_i}.
    generators = []
    for i in range(N):
        form = [0] * N
        form[i] = 1
        generators.append(form)
    for i in range(1, N):
        form = [0] * N
        form[0], form[i] = 1, -1
        generators.append(form)

    # Separator includes coefficient -3 on sum(lambda_A)=1.
    cut_slacks = {(start, length): ell(cut(start, length)) - 3
                  for length in (4, 5) for start in range(N)}
    assert min(cut_slacks.values()) >= 0
    product_slacks = [ell(product(generators[r], generators[s]))
                      for r, s in combinations_with_replacement(range(len(generators)), 2)]
    assert min(product_slacks) >= 0
    ell_l2 = ell(product([1] * N, [1] * N))
    separator_target = Fraction(ell_l2, 25) - 3
    assert ell_l2 == 40 and separator_target == Fraction(-7, 5)

    print("EXACT FARKAS GATE PASSED")
    print("pair identities: 11/11")
    print("exact witness min over 22 cuts:", min(witness_values))
    print("cut slacks ell(q_A)-3:", cut_slacks)
    print("minimum generator-product slack:", min(product_slacks))
    print("separator on target plus normalization:", separator_target)


if __name__ == "__main__":
    main()
