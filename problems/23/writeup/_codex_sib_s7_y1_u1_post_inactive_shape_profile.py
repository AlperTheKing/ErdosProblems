"""Shape profile after inactive-inequality closure for y=1,u=1 supports."""

from __future__ import annotations

from collections import Counter

import _codex_sib_s7_y1_basis_pruning_census as census
import _codex_sib_s7_y1_far_support_linear_filter as lin
import _codex_sib_s7_y1_terminal_rank_profile as rankprof
import _codex_sib_s7_y1_u1_inactive_ineq_closure as inactive


LOWER_LABELS = ("a1", "b1", "c1", "d1", "e1", "f1", "x1", "v1", "u1")
SLACK_LABELS = ("s1", "s2", "s3", "s4", "s5", "s6", "s7")


def main() -> None:
    states = sorted(rankprof.collect_unique_still("u1", None))
    assert len(states) == 20152

    still_unique: set[tuple[str, str, tuple[str, ...]]] = set()
    slack_pattern_count: Counter[tuple[str, ...]] = Counter()
    lower_pattern_count: Counter[tuple[str, ...]] = Counter()
    cap_slack_count: Counter[tuple[str, tuple[str, ...]]] = Counter()
    examples: dict[tuple[str, ...], tuple[str, tuple[str, ...]]] = {}
    label_freq: Counter[str] = Counter()

    for branch, cap, support_tuple in states:
        status, closure = inactive.close_support(branch, cap, support_tuple)
        if status == "contradiction":
            continue
        if lin.observed_closure_class(branch, cap, closure) == "closes_to_observed_basis":
            continue
        closure_tuple = tuple(sorted(closure))
        key = (branch, cap, closure_tuple)
        if key in still_unique:
            continue
        still_unique.add(key)
        support = set(closure_tuple)
        for label in support:
            label_freq[label] += 1
        slack_pattern = tuple(label for label in SLACK_LABELS if label in support)
        lower_pattern = tuple(label for label in LOWER_LABELS if label in support)
        slack_pattern_count[slack_pattern] += 1
        lower_pattern_count[lower_pattern] += 1
        cap_slack_count[(cap, slack_pattern)] += 1
        examples.setdefault(slack_pattern, (cap, closure_tuple))

    assert len(still_unique) == 11995
    print(f"U1-POST-INACTIVE-SHAPES unique_still={len(still_unique)}")
    print("U1-POST-INACTIVE-LABEL-FREQ " + " ".join(f"{label}:{label_freq[label]}" for label in (*LOWER_LABELS, *SLACK_LABELS)))
    print("U1-POST-INACTIVE-TOP-SLACK-PATTERNS")
    for pattern, count in slack_pattern_count.most_common(20):
        cap, support = examples[pattern]
        print(f"  count={count} pattern={','.join(pattern) or '-'} example_cap={cap} example_support={','.join(support)}")
    print("U1-POST-INACTIVE-TOP-LOWER-PATTERNS")
    for pattern, count in lower_pattern_count.most_common(20):
        print(f"  count={count} pattern={','.join(pattern) or '-'}")
    print("U1-POST-INACTIVE-TOP-CAP-SLACK-PATTERNS")
    for (cap, pattern), count in cap_slack_count.most_common(24):
        print(f"  count={count} cap={cap} pattern={','.join(pattern) or '-'}")
    print("PASS u1 post-inactive-closure remaining support shapes profiled")


if __name__ == "__main__":
    main()
