"""Exact boundary and fixture checks for the R39 weak-free question."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
for relative in (
    "tmp/fanout/r36_freepair_search",
    "tmp/fanout/r36_freepair_proof",
    "tmp/fanout/r35_endpoint_diversity",
    "tmp/fanout/r32_n12_fullbank",
    "tmp/fanout/p5_n12_census",
    "tmp/fanout/pht_n12_direct",
    "problems/23/writeup",
):
    sys.path.insert(0, str(ROOT / relative))

import check_real_endpoint_floor_obstruction as cage24  # noqa: E402
import p5_core as p5  # noqa: E402
import r37_weakfree_deadend_gate as gate  # noqa: E402
import verify_counterexample as cage20  # noqa: E402
from collision_only_core import analyze_collision_only  # noqa: E402


def verify_edge_identity() -> None:
    # Check all endpoint membership patterns for A and B and both edge signs.
    for au in (0, 1):
        for av in (0, 1):
            for bu in (0, 1):
                for bv in (0, 1):
                    for sign in (-1, 1):
                        cross_a = au != av
                        cross_b = bu != bv
                        cross_xor = (au ^ bu) != (av ^ bv)
                        both = cross_a and cross_b
                        assert sign * (cross_a + cross_b) == (
                            sign * cross_xor + 2 * sign * both
                        )


def analyze20() -> dict:
    ctx = p5.make_graph_context(cage20.N, cage20.EDGES - cage20.BAD, cage20.BAD)
    families = [cage20.ROW_DB[e] for e in sorted(cage20.BAD)]
    choice = tuple(
        family.index(tuple(row))
        for family, row in zip(families, cage20.SELECTED)
    )
    state = p5.reconstruct_state(ctx, cage20.SELECTED)
    result = analyze_collision_only(ctx, cage20.SELECTED)
    probes, weak, detours, invalid = gate.classify_probes(
        ctx, state, families, choice
    )
    owner_arcs, source_keys = gate.raw_other_source_arcs(ctx, state)
    assert not invalid and not detours
    assert result["collisionDefect"] == result["collisionDemand"] == 0
    assert probes["sigma1"] == 1 and len(weak) == 1
    assert weak[0]["sigma"] == 1
    assert source_keys == 0 and not owner_arcs
    return {
        "defect": result["collisionDefect"],
        "demand": result["collisionDemand"],
        "weak": len(weak),
        "sigma1": probes["sigma1"],
        "otherSources": source_keys,
        "detours": len(detours),
    }


def analyze24() -> dict:
    ctx = p5.make_graph_context(cage24.N, cage24.BLUE, cage24.BAD)
    families = [cage24.shortest_rows(*e) for e in cage24.INTENDED_BAD]
    choice = tuple(
        family.index(tuple(row))
        for family, row in zip(families, cage24.SELECTED_ROWS)
    )
    state = p5.reconstruct_state(ctx, cage24.SELECTED_ROWS)
    result = analyze_collision_only(ctx, cage24.SELECTED_ROWS)
    probes, weak, detours, invalid = gate.classify_probes(
        ctx, state, families, choice
    )
    trade = gate.strict_one_row_trade(
        ctx, families, choice, result["collisionDefect"]
    )
    assert not invalid and not weak and not detours
    assert result["collisionDefect"] == 68
    assert trade is not None and trade["newDefect"] == 51
    return {
        "defect": result["collisionDefect"],
        "demand": result["collisionDemand"],
        "matched": result["collisionMatched"],
        "weak": len(weak),
        "sigmaGe2": probes["sigmaGe2"],
        "trade": [trade["oldDefect"], trade["newDefect"]],
    }


def main() -> None:
    verify_edge_identity()
    print("BOUNDARY_IDENTITY=PASS patterns=32")
    print("CAGE20=" + repr(analyze20()))
    print("CAGE24=" + repr(analyze24()))


if __name__ == "__main__":
    main()
