"""Exact row-support derivation of the R29 hub-shore demand.

This intentionally does not generate any of the 680 rows in a selector family.
It checks only the structural support identities used in the proof.
"""

import hashlib
import json
from pathlib import Path

N = 2943
HUBS = (0, 1, 2)
LEFT_SIZE = 26
RIGHT_SIZE = 26
TRAFFIC_ROWS = LEFT_SIZE * RIGHT_SIZE
SELECTOR_FAMILIES = 676


def main() -> None:
    # Every traffic row is (left,1,0,2,right).  For a fixed hub v:
    # v itself and the other two hubs occur with it in all 676 rows;
    # each of the 52 leaves occurs with it in exactly 26 rows.
    self_and_hub_excess = len(HUBS) * (TRAFFIC_ROWS - 1)
    leaf_excess = (LEFT_SIZE + RIGHT_SIZE) * (LEFT_SIZE - 1)
    collision_half_per_hub = 2 * (self_and_hub_excess + leaf_excess)

    # Selectors lie in vertices 3..2761 and so add no hub row occurrence or
    # hub pair occurrence.  Fixed non-traffic rows also avoid the hubs.
    selector_hub_occurrences = 0
    row_count_per_hub = TRAFFIC_ROWS

    # All non-cable blue edges at a hub occur in traffic-row support.  The
    # one cable edge at each hub has selected endpoints, is outside row
    # support, and belongs to a component activated by a fixed seed bad atom.
    demanded_active_degree_per_hub = 1
    residual_capacity = max(0, N - 5 * row_count_per_hub)
    hit_need_per_hub = max(
        0, demanded_active_degree_per_hub - residual_capacity
    )

    collision_half = len(HUBS) * collision_half_per_hub
    hit_need = len(HUBS) * hit_need_per_hub
    demand = collision_half + hit_need

    result = {
        "arbitrary_selector_choices": f"680^{SELECTOR_FAMILIES}",
        "selector_rows_enumerated": 0,
        "selector_hub_occurrences": selector_hub_occurrences,
        "traffic_rows": TRAFFIC_ROWS,
        "row_count_per_hub": row_count_per_hub,
        "pair_excess_per_hub": {
            "self_and_other_hubs": self_and_hub_excess,
            "52_leaves": leaf_excess,
            "total": self_and_hub_excess + leaf_excess,
        },
        "collision_half_per_hub": collision_half_per_hub,
        "residual_capacity_per_hub": residual_capacity,
        "demanded_active_degree_per_hub": demanded_active_degree_per_hub,
        "hit_need_per_hub": hit_need_per_hub,
        "shore_collision_half": collision_half,
        "shore_hit_need": hit_need,
        "shore_demand": demand,
        "identity": "3 * (2 * (3 * 675 + 52 * 25) + 1) = 19953",
    }
    assert collision_half_per_hub == 6650
    assert (collision_half, hit_need, demand) == (19950, 3, 19953)
    out = json.dumps(result, indent=2, sort_keys=True) + "\n"
    Path("result.json").write_text(out, encoding="utf-8", newline="\n")
    print(out, end="")
    print("result_sha256", hashlib.sha256(out.encode()).hexdigest())


if __name__ == "__main__":
    main()
