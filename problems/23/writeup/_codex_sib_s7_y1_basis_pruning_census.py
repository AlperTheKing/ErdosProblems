"""Pruned combinatorial census for y=1 SIB-S7 rank-basis supports.

This is not an algebraic closure certificate.  It classifies the raw <=7
rank-basis search universe from `_codex_sib_s7_y1_basis_search_census.py` by
pure set relations to the observed support bases:

* contains an observed rank basis in the same branch/cap chart;
* is one insertion/deletion away from such a basis;
* is not adjacent to any observed rank basis.

The output quantifies how much of the raw 184,432-support universe remains for
true unobserved-support algebraic exclusion.
"""

from __future__ import annotations

from itertools import combinations


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
    ("s2", "s4", "ALL_TIGHT"): frozenset(("b1", "d1", "f1", "s1", "s3", "s5")),
    ("s2", "s5", "ALL_TIGHT"): frozenset(("b1", "d1", "f1", "s1", "s3", "s4")),
    ("s2", "s6", "ALL_TIGHT"): frozenset(("b1", "d1", "f1", "s1", "s3", "s4")),
    ("s3", "s4", "ALL_TIGHT"): frozenset(("b1", "d1", "f1", "s1", "s2", "s5")),
    ("s3", "s5", "ALL_TIGHT"): frozenset(("b1", "d1", "f1", "s1", "s2", "s4")),
    ("u1", "s4", "ALL_TIGHT"): frozenset(("b1", "d1", "f1", "s1", "s3", "s5")),
    ("u1", "s5", "ALL_TIGHT"): frozenset(("b1", "d1", "f1", "s1", "s3", "s4")),
    ("u1", "s6", "ALL_TIGHT"): frozenset(("b1", "d1", "f1", "s1", "s3", "s4")),
    ("u1", "s4", "HIGH_A"): frozenset(("a1", "b1", "d1", "s1", "s3", "s5")),
    ("u1", "s5", "HIGH_A"): frozenset(("a1", "b1", "d1", "s1", "s3", "s4")),
    ("s2", "s4", "S2_SURV"): frozenset(("b1", "f1", "s1", "s5")),
    ("s2", "s7", "S2_SURV"): frozenset(("b1", "f1", "s1", "s5")),
    ("s3", "s5", "S3_SURV"): frozenset(("b1", "f1", "u1", "v1")),
    ("xq", "s4", "XQ_A"): frozenset(("f1", "s3", "s5", "s6", "u1")),
    ("xq", "s5", "XQ_A"): frozenset(("f1", "s3", "s5", "s6", "u1")),
    ("xq", "s6", "XQ_B"): frozenset(("d1", "f1", "s1", "s2", "s3", "s7")),
    ("u1", "s7", "U1_S7_HIGH"): frozenset(("a1", "c1", "d1", "e1", "f1", "s1")),
    ("xq", "s5", "XQ_S5_HIGH"): frozenset(("a1", "s1", "s3", "s4", "s6", "u1")),
    ("u1", "s4", "ALL_ONES"): frozenset(("a1", "b1", "c1", "d1", "e1", "f1", "s1")),
}
def fixed_labels(branch: str, cap: str) -> set[str]:
    fixed = {cap}
    if branch in {"s2", "s3", "u1"}:
        fixed.add(branch)
    return fixed


def observed_for(branch: str, cap: str) -> list[tuple[str, frozenset[str]]]:
    return [(name, basis) for (br, ca, name), basis in OBSERVED_BASES.items() if br == branch and ca == cap]


def classify(S: frozenset[str], bases: list[tuple[str, frozenset[str]]]) -> str:
    if any(basis <= S for _name, basis in bases):
        return "contains_observed_basis"
    if any(len(S ^ basis) == 1 for _name, basis in bases):
        return "one_step_from_observed_basis"
    if any(len(S ^ basis) == 2 for _name, basis in bases):
        return "two_step_from_observed_basis"
    return "unobserved_far"


def main() -> None:
    total_counts: dict[str, int] = {}
    raw_total = 0
    for branch in BRANCHES:
        for cap in CAPS:
            movable = sorted(set(LABELS) - fixed_labels(branch, cap))
            bases = observed_for(branch, cap)
            counts: dict[str, int] = {}
            for r in range(8):
                for combo in combinations(movable, r):
                    raw_total += 1
                    cls = classify(frozenset(combo), bases)
                    counts[cls] = counts.get(cls, 0) + 1
                    total_counts[cls] = total_counts.get(cls, 0) + 1
            print(
                f"PRUNE-CHART branch={branch} cap={cap} observed_bases={len(bases)} "
                + " ".join(f"{key}={counts.get(key, 0)}" for key in sorted({*counts, 'contains_observed_basis', 'one_step_from_observed_basis', 'two_step_from_observed_basis', 'unobserved_far'}))
            )

    assert raw_total == 184432
    assert sum(total_counts.values()) == raw_total
    print("PRUNE-TOTAL " + " ".join(f"{key}={total_counts.get(key, 0)}" for key in sorted(total_counts)))
    print("PASS y=1 raw basis supports classified by observed-basis proximity")


if __name__ == "__main__":
    main()