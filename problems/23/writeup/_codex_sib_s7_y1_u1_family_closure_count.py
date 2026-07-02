"""Count u1 terminal supports covered by newly certified custom families."""

from __future__ import annotations

from collections import Counter

import _codex_sib_s7_y1_far_support_linear_filter as lin
import _codex_sib_s7_y1_terminal_rank_profile as rankprof
import _codex_sib_s7_y1_u1_inactive_ineq_closure as inactive


ABDF_BASIS = frozenset(("a1", "b1", "d1", "f1"))


def custom_family(branch: str, cap: str, closure: frozenset[str]) -> str | None:
    if branch != "u1":
        return None
    if cap in {"s4", "s5", "s6", "s7"} and ABDF_BASIS <= closure:
        return "U1_ABDF_CAP"
    if cap == "s4" and frozenset(("a1", "b1", "d1")) <= closure:
        return "U1_ABD_S4"
    return None


def main() -> None:
    starts = sorted(rankprof.collect_unique_still("u1", None))
    assert len(starts) == 20152

    status_counts: Counter[str] = Counter()
    custom_counts: Counter[str] = Counter()
    by_cap: Counter[tuple[str, str]] = Counter()
    still_unique: set[tuple[str, str, tuple[str, ...]]] = set()

    for branch, cap, support_tuple in starts:
        status, closure = inactive.close_support(branch, cap, support_tuple)
        if status == "contradiction":
            cls = "contradiction"
        elif lin.observed_closure_class(branch, cap, closure) == "closes_to_observed_basis":
            cls = "closes_to_observed_basis"
        else:
            family = custom_family(branch, cap, closure)
            if family is not None:
                cls = "closes_to_custom_family"
                custom_counts[family] += 1
            else:
                cls = "still_unobserved"
                still_unique.add((branch, cap, tuple(sorted(closure))))
        status_counts[cls] += 1
        by_cap[(cap, cls)] += 1

    print("U1-FAMILY-CLOSURE " + " ".join(f"{key}={status_counts[key]}" for key in sorted(status_counts)))
    print("U1-FAMILY-CLOSURE-CUSTOM " + " ".join(f"{key}={custom_counts[key]}" for key in sorted(custom_counts)))
    print(f"U1-FAMILY-CLOSURE-STILL-UNIQUE={len(still_unique)}")
    for cap in ("s4", "s5", "s6", "s7"):
        pieces = []
        for cls in ("contradiction", "closes_to_observed_basis", "closes_to_custom_family", "still_unobserved"):
            pieces.append(f"{cls}={by_cap[(cap, cls)]}")
        print(f"U1-FAMILY-CLOSURE-CAP cap={cap} " + " ".join(pieces))
    print("PASS u1 terminal supports counted against custom certified families")


if __name__ == "__main__":
    main()

