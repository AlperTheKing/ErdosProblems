"""Shape profile for still-unobserved SIB-S7 y=1,u=1 terminal supports.

This is a targeting artifact, not a proof gate.  It reuses the exact terminal
support generator from the monomial-hit filter and summarizes the u1 branch by
active label frequencies and slack-pattern classes.
"""

from __future__ import annotations

from collections import Counter

import _codex_sib_s7_y1_basis_pruning_census as census
import _codex_sib_s7_y1_terminal_rank_profile as rankprof


LOWER_LABELS = ("a1", "b1", "c1", "d1", "e1", "f1", "x1", "v1", "u1")
SLACK_LABELS = ("s1", "s2", "s3", "s4", "s5", "s6", "s7")


def main() -> None:
    states = sorted(rankprof.collect_unique_still("u1", None))
    assert len(states) == 20152

    label_freq: Counter[str] = Counter()
    lower_count: Counter[int] = Counter()
    slack_count: Counter[int] = Counter()
    cap_count: Counter[str] = Counter()
    rank_count: Counter[int] = Counter()
    slack_pattern_count: Counter[tuple[str, ...]] = Counter()
    lower_pattern_count: Counter[tuple[str, ...]] = Counter()
    cap_slack_count: Counter[tuple[str, tuple[str, ...]]] = Counter()
    examples: dict[tuple[str, ...], tuple[str, str, tuple[str, ...], int]] = {}

    for branch, cap, support_tuple in states:
        assert branch == "u1"
        support = set(support_tuple)
        for label in support:
            label_freq[label] += 1

        lower_pattern = tuple(label for label in LOWER_LABELS if label in support)
        slack_pattern = tuple(label for label in SLACK_LABELS if label in support)
        lower_count[len(lower_pattern)] += 1
        slack_count[len(slack_pattern)] += 1
        cap_count[cap] += 1
        slack_pattern_count[slack_pattern] += 1
        lower_pattern_count[lower_pattern] += 1
        cap_slack_count[(cap, slack_pattern)] += 1

        rank, _eq_count, _labels = rankprof.rank_for_key(branch, cap, support_tuple)
        rank_count[rank] += 1
        examples.setdefault(slack_pattern, (branch, cap, support_tuple, rank))

    print(f"U1-TERMINAL-SHAPES total={len(states)}")
    print("U1-CAPS " + " ".join(f"{cap}:{cap_count[cap]}" for cap in census.CAPS))
    print("U1-RANKS " + " ".join(f"{rank}:{rank_count[rank]}" for rank in sorted(rank_count)))
    print("U1-LOWER-COUNT " + " ".join(f"{count}:{lower_count[count]}" for count in sorted(lower_count)))
    print("U1-SLACK-COUNT " + " ".join(f"{count}:{slack_count[count]}" for count in sorted(slack_count)))
    print("U1-LABEL-FREQ " + " ".join(f"{label}:{label_freq[label]}" for label in (*LOWER_LABELS, *SLACK_LABELS)))

    print("U1-TOP-SLACK-PATTERNS")
    for pattern, count in slack_pattern_count.most_common(20):
        branch, cap, support, rank = examples[pattern]
        print(
            f"  count={count} pattern={','.join(pattern) or '-'} "
            f"example_cap={cap} example_rank={rank} example_support={','.join(support)}"
        )

    print("U1-TOP-LOWER-PATTERNS")
    for pattern, count in lower_pattern_count.most_common(20):
        print(f"  count={count} pattern={','.join(pattern) or '-'}")

    print("U1-TOP-CAP-SLACK-PATTERNS")
    for (cap, pattern), count in cap_slack_count.most_common(24):
        print(f"  count={count} cap={cap} pattern={','.join(pattern) or '-'}")

    print("PASS u1 still-unobserved terminal support shapes profiled")


if __name__ == "__main__":
    main()
