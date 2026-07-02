"""Combinatorial census for the y=1 SIB-S7 branch/cap rank-basis search.

This is not the unobserved-support exclusion.  It records the finite search
universe suggested by the seven-variable branch/cap charts and the observed
rank-basis artifact: if a chart face is covered by a rank-basis argument, it is
natural to enumerate active bases of size at most seven.

There are 16 branch/cap charts: branches s2, s3, u1, xq crossed with capacity
faces s4..s7.  In s2/s3/u1 charts, the branch label and capacity label are fixed,
leaving 14 movable labels.  In xq charts only the capacity label is fixed,
leaving 15 movable labels.  Thus the raw basis-search universe is

  12 * sum_{k=0}^7 C(14,k) + 4 * sum_{k=0}^7 C(15,k) = 184432.

The script also checks that every observed rank basis is compatible with its
claimed branch/cap chart and has size at most seven.
"""

from __future__ import annotations

from math import comb


CAPS = ("s4", "s5", "s6", "s7")
BRANCHES = ("s2", "s3", "u1", "xq")
LABELS = (
    "a1",
    "b1",
    "c1",
    "d1",
    "e1",
    "f1",
    "x1",
    "v1",
    "u1",
    "s1",
    "s2",
    "s3",
    "s4",
    "s5",
    "s6",
    "s7",
)

OBSERVED_BASES = {
    ("u1", "s4", "ALL_TIGHT"): ("b1", "d1", "f1", "s1", "s3", "s5"),
    ("u1", "s4", "HIGH_A"): ("a1", "b1", "d1", "s1", "s3", "s5"),
    ("xq", "s4", "XQ_A"): ("f1", "s3", "s5", "s6", "u1"),
    ("xq", "s6", "XQ_B"): ("d1", "f1", "s1", "s2", "s3", "s7"),
    ("u1", "s7", "U1_S7_HIGH"): ("a1", "c1", "d1", "e1", "f1", "s1"),
    ("xq", "s5", "XQ_S5_HIGH"): ("a1", "s1", "s3", "s4", "s6", "u1"),
    ("u1", "s4", "ALL_ONES"): ("a1", "b1", "c1", "d1", "e1", "f1", "s1"),
}


def fixed_labels(branch: str, cap: str) -> set[str]:
    fixed = {cap}
    if branch in {"s2", "s3", "u1"}:
        fixed.add(branch)
    return fixed


def basis_count(movable_count: int, max_size: int = 7) -> int:
    return sum(comb(movable_count, k) for k in range(max_size + 1))


def main() -> None:
    total = 0
    rows: list[tuple[str, str, int, int]] = []
    for branch in BRANCHES:
        for cap in CAPS:
            movable = sorted(set(LABELS) - fixed_labels(branch, cap))
            count = basis_count(len(movable))
            rows.append((branch, cap, len(movable), count))
            total += count

    for branch, cap, movable_count, count in rows:
        print(f"BASIS-CHART branch={branch} cap={cap} movable={movable_count} count_le7={count}")

    assert basis_count(14) == 9908
    assert basis_count(15) == 16384
    assert total == 184432

    for (branch, cap, name), basis in OBSERVED_BASES.items():
        fixed = fixed_labels(branch, cap)
        assert len(basis) <= 7, name
        assert not (set(basis) & fixed), (name, basis, fixed)
        assert set(basis) <= set(LABELS), name
        print(f"OBSERVED-BASIS {name} branch={branch} cap={cap} size={len(basis)}")

    print("PASS y=1 branch/cap raw rank-basis search universe has 184432 supports of size <=7")


if __name__ == "__main__":
    main()