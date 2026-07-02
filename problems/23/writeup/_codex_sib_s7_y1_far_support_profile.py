"""Profile the unobserved-far y=1 SIB-S7 rank-basis supports.

This is a targeting artifact, not a closure certificate.  It reuses the
observed-basis proximity classification and records how the remaining far
support universe is distributed by support size and active labels.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations

import _codex_sib_s7_y1_basis_pruning_census as census


def main() -> None:
    total_far = 0
    size_hist: Counter[int] = Counter()
    label_hist: Counter[str] = Counter()
    chart_far: Counter[tuple[str, str]] = Counter()
    chart_size_hist: dict[tuple[str, str], Counter[int]] = {}

    for branch in census.BRANCHES:
        for cap in census.CAPS:
            key = (branch, cap)
            movable = sorted(set(census.LABELS) - census.fixed_labels(branch, cap))
            bases = census.observed_for(branch, cap)
            local_size_hist: Counter[int] = Counter()
            local_label_hist: Counter[str] = Counter()
            for r in range(8):
                for combo in combinations(movable, r):
                    support = frozenset(combo)
                    if census.classify(support, bases) != "unobserved_far":
                        continue
                    total_far += 1
                    chart_far[key] += 1
                    size_hist[r] += 1
                    local_size_hist[r] += 1
                    for label in support:
                        label_hist[label] += 1
                        local_label_hist[label] += 1
            chart_size_hist[key] = local_size_hist
            most = ",".join(f"{name}:{count}" for name, count in local_label_hist.most_common(3))
            print(
                f"FAR-CHART branch={branch} cap={cap} far={chart_far[key]} "
                f"sizes={dict(sorted(local_size_hist.items()))} top3={most}"
            )

    assert total_far == 182589
    assert sum(chart_far.values()) == total_far
    assert sum(size_hist.values()) == total_far

    print("FAR-SIZE-HIST " + " ".join(f"{size}:{size_hist[size]}" for size in sorted(size_hist)))
    print("FAR-LABEL-HIST " + " ".join(f"{label}:{label_hist[label]}" for label in census.LABELS))
    print("PASS y=1 unobserved-far support profile recorded")


if __name__ == "__main__":
    main()
