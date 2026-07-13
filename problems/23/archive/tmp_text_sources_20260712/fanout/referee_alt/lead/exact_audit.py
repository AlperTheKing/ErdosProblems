from fractions import Fraction
from itertools import product


def r29_arithmetic():
    assert 4110 + 2704 + 12 + 207 + 6 == 7039
    assert 707 + 676 == 1383
    assert Fraction(34575, 25) == 1383
    assert 19953 - (17325 + 2600) == 28
    assert 19953 + 52 * 200 + 458 == 30811
    assert 676 * (680 - 1) == 459004
    assert 30813 - 30811 == 2


def finite_descent_equivalence():
    # For every finite two-state score/Hall model:
    # no Hall-failing global minimum iff every failing state has a lower state.
    for scores in product(range(3), repeat=2):
        for hall in product((False, True), repeat=2):
            minimum = min(scores)
            no_failing_min = all(hall[i] or scores[i] != minimum for i in range(2))
            descent = all(
                hall[i] or any(scores[j] < scores[i] for j in range(2))
                for i in range(2)
            )
            assert no_failing_min == descent


def canonical_quantifier_falsifier():
    # Both states minimize.  The designated canonical state is Hall-good,
    # while another global minimizer is Hall-bad.
    scores = (0, 0)
    hall = (True, False)
    canonical = 0
    minimum = min(scores)
    assert scores[canonical] == minimum and hall[canonical]
    assert any(scores[i] == minimum and not hall[i] for i in range(2))


if __name__ == "__main__":
    r29_arithmetic()
    finite_descent_equivalence()
    canonical_quantifier_falsifier()
    print("PASS r29_arithmetic=7 descent_models=36 canonical_falsifier=1")
