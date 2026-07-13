"""Build the proposed A389182 b-file extension through n=100.

The prefix n=1..69 is the currently published OEIS data. The extension is
deduced from exact branch-and-bound certificates at the six endpoints below
and monotonicity of F(n).
"""

from pathlib import Path


KNOWN_1_TO_69 = [
    1, 2, 3, 3, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 7,
    8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 10, 10, 10, 10, 10,
    10, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 12, 12, 12,
    12, 12, 12, 12, 12, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14,
]

# Exact proof-complete BnB values. If F(a)=F(b)=c and a<=n<=b, then
# monotonicity gives c=F(a)<=F(n)<=F(b)=c.
CERTIFIED_INTERVALS = [
    (70, 80, 14),
    (81, 85, 15),
    (86, 100, 16),
]


def build_terms() -> list[int]:
    assert len(KNOWN_1_TO_69) == 69
    terms = list(KNOWN_1_TO_69)
    for lo, hi, value in CERTIFIED_INTERVALS:
        assert lo == len(terms) + 1
        terms.extend([value] * (hi - lo + 1))
    assert len(terms) == 100
    assert all(x <= y for x, y in zip(terms, terms[1:]))
    return terms


def main() -> None:
    terms = build_terms()
    target = Path(__file__).with_name("b389182_1_100.txt")
    target.write_text(
        "".join(f"{n} {value}\n" for n, value in enumerate(terms, 1)),
        encoding="ascii",
    )
    print(f"wrote {target} with {len(terms)} terms")


if __name__ == "__main__":
    main()
