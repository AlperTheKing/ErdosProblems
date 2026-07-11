"""Exact real-graph falsifier to the scaled collision-residual token route.

The underlying 167-vertex graph is independently locked by
_codex_pro_active_cycle_counterexample_verify.py as triangle-free, max-cut,
Gamma-minimal, and all-ell5. Its positive shortest-row component has 27
vertices and 28 bad rows, hence component residual 29.
"""

from fractions import Fraction
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _codex_collision_reserve_locked_gate import active_cycle_lock  # noqa: E402


def main() -> None:
    lock = active_cycle_lock()
    assert lock["N"] == 167
    assert lock["badEdges"] == 28

    component_n = 27
    component_bad = 28
    component_residual = component_n * component_n - 25 * component_bad
    assert component_residual == 29

    # Common row-choice denominator K=1: all selected shortest rows are unique.
    need_by_vertex = []
    for row in lock["records"]:
        vertex_slack_units = max(0, component_n - row["T"])
        need_units = max(0, row["degree"] - vertex_slack_units)
        need_by_vertex.append((row["v"], need_units))

    need = sum(value for _, value in need_by_vertex)
    assert need == 7

    endpoint_hall_need = Fraction(need, 2)
    official_residual_hall_budget = Fraction(component_residual, 25)
    scaled_lhs = 25 * need
    scaled_rhs = 2 * component_residual

    assert scaled_lhs == 175
    assert scaled_rhs == 58
    assert endpoint_hall_need > official_residual_hall_budget

    print(json.dumps({
        "graph": "locked-N167-active-cycle",
        "triangleFreeMaxCutGammaMin": True,
        "componentN": component_n,
        "componentBadRows": component_bad,
        "componentResidual": component_residual,
        "needByVertex": need_by_vertex,
        "needSlots": need,
        "endpointHallNeed": str(endpoint_hall_need),
        "officialResidualHallBudget": str(official_residual_hall_budget),
        "scaledCondition": {
            "lhs25Need": scaled_lhs,
            "rhs2Residual": scaled_rhs,
            "holds": False,
        },
        "deficit": str(endpoint_hall_need - official_residual_hall_budget),
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
