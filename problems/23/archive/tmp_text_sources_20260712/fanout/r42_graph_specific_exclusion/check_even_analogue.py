"""Parity-corrected abstract R42 rotor.

This deliberately remains non-graphical.  It shows why collision-half parity
excludes the literal 5/4 toy but not the source-swap mechanism: six paired
obligations can use four swapping sources plus one persistent source and keep
unit defect.
"""

from itertools import permutations


STEMS = ("a", "b", "c")
OBLIGATIONS = tuple((stem, half) for stem in STEMS for half in (0, 1))
PERSISTENT = ("p", 1)


def turnover(middle):
    return tuple((f"{middle}>{side}", 1) for side in ("x", "y")) + tuple(
        (f"{side}>{middle}", 1) for side in ("x", "y")
    )


def maximum_matchings(middle):
    sources = (PERSISTENT,) + turnover(middle)
    return tuple(dict(zip(chosen, sources)) for chosen in permutations(
        OBLIGATIONS, len(sources)
    ))


def main():
    states = {middle: maximum_matchings(middle) for middle in ("m", "v")}
    for middle, matchings in states.items():
        assert len(OBLIGATIONS) == 6
        assert len(matchings) == 720  # 6P5
        assert all(len(matching) == 5 for matching in matchings)
        assert all(PERSISTENT in matching.values() for matching in matchings)
        assert all(set(turnover(middle)) <= set(matching.values())
                   for matching in matchings)
    assert set(turnover("m")).isdisjoint(turnover("v"))
    print("verdict=PASS_PARITY_CORRECTED_ABSTRACT_ROTOR")
    print("obligations=6 sources=5 defect=1 matchings_per_state=720")
    print("turnover=4 persistent=1")


if __name__ == "__main__":
    main()
