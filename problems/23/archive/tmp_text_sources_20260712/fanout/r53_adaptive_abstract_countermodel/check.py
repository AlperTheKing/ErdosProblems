"""Exact abstract countermodel for adaptive edge-capacity rotor bookkeeping.

This is deliberately graph-free.  It tests only the proposed soft flow and
the exact defect-transition identity.  Its purpose is to identify which part
of the R53 route must still come from graph geometry.
"""

from itertools import combinations, permutations


OBLIGATIONS = ("d0h0", "d0h1", "d1h0", "d1h1")


def keys(state: str) -> tuple[str, ...]:
    return tuple(f"{state}:e:{orientation}:h{half}"
                 for orientation in ("xy", "yx") for half in (0, 1))


def maximum_matching(state: str) -> tuple[int, dict[str, str]]:
    """All arcs are legal; keys have unit cap and their edge group has cap 2."""
    source_keys = keys(state)
    best: dict[str, str] = {}
    for size in range(1, len(OBLIGATIONS) + 1):
        for demand_subset in combinations(OBLIGATIONS, size):
            for key_subset in combinations(source_keys, size):
                # Every key belongs to the one active-edge node of capacity 2.
                if len(key_subset) > 2:
                    continue
                for ordered_keys in permutations(key_subset):
                    candidate = dict(zip(demand_subset, ordered_keys, strict=True))
                    if len(candidate) > len(best):
                        best = candidate
    return len(best), best


def transition(old: str, new: str) -> dict[str, int]:
    old_rank, old_matching = maximum_matching(old)
    new_rank, new_matching = maximum_matching(new)
    old_sources = set(old_matching.values())
    new_sources = set(new_matching.values())
    persistent_sources = set(keys(old)) & set(keys(new))

    carry = {
        d: s for d, s in old_matching.items()
        if s in persistent_sources and new_matching.get(d) == s
    }
    born = 0
    broken_live = old_rank - len(carry)
    dead_unmatched = 0
    reoptimized_gain = new_rank - len(carry)
    old_defect = len(OBLIGATIONS) - old_rank
    new_defect = len(OBLIGATIONS) - new_rank

    assert len(old_sources) == old_rank
    assert len(new_sources) == new_rank
    assert new_defect - old_defect == (
        born + broken_live - dead_unmatched - reoptimized_gain
    )
    return {
        "old_rank": old_rank,
        "new_rank": new_rank,
        "old_defect": old_defect,
        "new_defect": new_defect,
        "born": born,
        "broken_live": broken_live,
        "dead_unmatched": dead_unmatched,
        "reoptimized_gain": reoptimized_gain,
        "carry": len(carry),
    }


def main() -> None:
    rank_a, matching_a = maximum_matching("A")
    rank_b, matching_b = maximum_matching("B")
    assert rank_a == rank_b == 2
    assert len(OBLIGATIONS) - rank_a == len(OBLIGATIONS) - rank_b == 2
    ab = transition("A", "B")
    ba = transition("B", "A")
    assert ab == ba
    assert ab["born"] + ab["broken_live"] == (
        ab["dead_unmatched"] + ab["reoptimized_gain"]
    )
    print("PASS_ADAPTIVE_ABSTRACT_ROTOR")
    print({
        "obligations": len(OBLIGATIONS),
        "keys_per_state": len(keys("A")),
        "edge_group_capacity": 2,
        "rank": rank_a,
        "defect": len(OBLIGATIONS) - rank_a,
        "A_matching": matching_a,
        "B_matching": matching_b,
        "transition": ab,
    })


if __name__ == "__main__":
    main()
