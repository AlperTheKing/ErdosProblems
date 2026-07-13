"""Exact checks for the R35 collision source-floor identities.

This is not a proof of collision feasibility.  It checks the exact arithmetic
decomposition used in REPORT.md on:

* every owner shore of the first pinned N=10 deficient tuple;
* the anchored K3,3 double-star arithmetic from R35; and
* the two-owner/two-half example showing why base-component coherence is an
  additional loss term rather than an ordinary source-count correction.

All quantities are integers.  No floating point solver or approximation is
used.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WRITEUP = ROOT / "problems" / "23" / "writeup"
PHT = ROOT / "tmp" / "fanout" / "pht_n12_direct"
P5_DIR = ROOT / "tmp" / "fanout" / "p5_n12_census"
R32_DIR = ROOT / "tmp" / "fanout" / "r32_n12_fullbank"
for path in (WRITEUP, PHT, P5_DIR, R32_DIR):
    sys.path.insert(0, str(path))

from _codex_r19_global_base_census import dec, loads  # noqa: E402
from _codex_r20_two_row_exchange_gate import shortest_row_families  # noqa: E402
from _codex_r23_heavy_alltuple_descent_gate import rows_for_choice  # noqa: E402
from fullbank_core import collision_owners, decode_source  # noqa: E402
import p5_core as p5  # noqa: E402


def merge_masks(*relations: dict[int, int]) -> dict[int, int]:
    out: dict[int, int] = {}
    for relation in relations:
        for source, mask in relation.items():
            out[source] = out.get(source, 0) | mask
    return out


def shore_arithmetic(ctx: p5.GraphContext, state: p5.TupleState,
                     shore: frozenset[int]) -> dict:
    """Compute the exact P1/P3/strict-P4 shore decomposition."""

    n = ctx.n
    masks = p5.relation_masks(ctx, state)
    owner_index = {owner: index for index, owner in enumerate(state.owners)}
    shore_mask = sum(1 << owner_index[v] for v in shore)

    own: set[int] = set()
    p3_by_owner: dict[int, set[int]] = {v: set() for v in shore}
    p4: set[int] = {
        source for source, mask in masks["p4"].items() if mask & shore_mask
    }

    for source, mask in masks["p13"].items():
        x, y, _half = decode_source(n, source)
        if x in shore and mask & (1 << owner_index[x]):
            own.add(source)
        for v in shore:
            bit = 1 << owner_index[v]
            if not (mask & bit):
                continue
            if (
                x not in shore
                and state.pair[v][x] > 0
                and state.pair[v][y] > 0
                and ctx.sigma_pair[x][y] >= 0
            ):
                p3_by_owner[v].add(source)

    p3_extra = set().union(*p3_by_owner.values()) if p3_by_owner else set()
    assert not (p3_extra & own)
    p4_extra = p4 - own - p3_extra
    raw_reach = own | p3_extra | p4_extra

    demand = sum(state.collision[v] for v in shore)
    row_total = 0
    support_total = 0
    own_formula = 0
    p3_sum_formula = 0
    per_owner = {}
    for v in sorted(shore):
        q_v = state.pair[v][v]
        support = {x for x in range(n) if state.pair[v][x] > 0}
        s_v = len(support)
        row_total += q_v
        support_total += s_v

        reserved_p1 = sum(
            1
            for y in range(n)
            if y not in support
            and p5.edge(v, y) in state.demanded_active_edges
            and v in state.active_vertices
        )
        own_v = 2 * (n - s_v) - reserved_p1
        own_formula += own_v
        assert own_v == sum(
            1 for source in own if decode_source(n, source)[0] == v
        )

        x_choices = support - shore
        candidates = len(x_choices) * (s_v - 1)
        blocked = sum(
            1
            for x in x_choices
            for y in support
            if x != y and state.pair[x][y] > 0
        )
        free_bases = candidates - blocked
        reserved_p3 = sum(
            1
            for x in x_choices
            for y in support
            if x != y
            and state.pair[x][y] == 0
            and p5.edge(x, y) in state.demanded_active_edges
            and x in state.active_vertices
        )
        p3_v_formula = 2 * free_bases - reserved_p3
        p3_sum_formula += p3_v_formula
        assert p3_v_formula == len(p3_by_owner[v])
        assert state.collision[v] == 2 * (5 * q_v - s_v)
        per_owner[v] = {
            "q": q_v,
            "s": s_v,
            "collisionDemand": state.collision[v],
            "p1": own_v,
            "p1Reserved": reserved_p1,
            "quadraticCandidates": candidates,
            "cooccurrenceBlocked": blocked,
            "freeOrderedBases": free_bases,
            "p3Reserved": reserved_p3,
            "p3HalfIncidences": p3_v_formula,
        }

    p3_overlap = p3_sum_formula - len(p3_extra)
    assert p3_overlap >= 0
    press = 2 * (5 * row_total - n * len(shore)) + (
        2 * (n * len(shore) - support_total) - len(own)
    )
    assert demand - len(own) == press
    assert len(p3_extra) == p3_sum_formula - p3_overlap
    assert demand - len(raw_reach) == press - len(p3_extra) - len(p4_extra)

    component_sets: dict[int, set[int]] = {}
    raw = merge_masks(masks["p13"], masks["p4"])
    for source, mask in raw.items():
        if not (mask & shore_mask):
            continue
        base = source >> 1
        for v in shore:
            if mask & (1 << owner_index[v]):
                component_sets.setdefault(base, set()).add(state.selected_comp[v])
    coherence_automatic = all(len(comps) <= 1 for comps in component_sets.values())

    return {
        "shore": sorted(shore),
        "demand": demand,
        "p1": len(own),
        "press": press,
        "p3Extra": len(p3_extra),
        "p3OwnerIncidences": p3_sum_formula,
        "p3OverlapLoss": p3_overlap,
        "p4Extra": len(p4_extra),
        "rawReach": len(raw_reach),
        "rawDefect": demand - len(raw_reach),
        "coherenceAutomatic": coherence_automatic,
        "perOwner": per_owner,
    }


def pinned_n10() -> dict:
    g6 = "I?rFf_{N?"
    choice = (0, 0, 0, 7)
    n, edges = dec(g6)
    info = loads(n, edges)
    assert info is not None
    families = shortest_row_families(info)
    rows = rows_for_choice(families, choice)
    ctx = p5.make_graph_context(n, info["Bset"], info["Mset"])
    state = p5.reconstruct_state(ctx, rows)
    owners = collision_owners(state)
    shores = []
    for width in range(1, len(owners) + 1):
        for values in itertools.combinations(owners, width):
            shores.append(shore_arithmetic(ctx, state, frozenset(values)))
    worst = max(shores, key=lambda row: (row["rawDefect"], -len(row["shore"])))
    assert worst["shore"] == [4, 6, 8]
    # This lane excludes P5, so the exact P1/P3/P4 reach is 22 here.
    assert worst["demand"] == 32 and worst["rawReach"] == 22
    assert all(row["coherenceAutomatic"] for row in shores)
    return {
        "g6": g6,
        "choice": list(choice),
        "ownerShoresChecked": len(shores),
        "worstP1P3P4Shore": worst,
    }


def anchored_double_star(a: int, b: int, n: int, p1_reserved: int) -> dict:
    """The one-hub equality model used by the R35 anchored K3,3 core."""

    q = a * b
    s = a + b + 3
    demand = 2 * (5 * q - s)
    p1 = 2 * (n - s) - p1_reserved
    p3_free_bases = a * (a - 1) + b * (b - 1)
    p3 = 2 * p3_free_bases
    d = s - 1
    candidates = d * d
    blockers = candidates - p3_free_bases
    press = 2 * (5 * q - n) + p1_reserved
    required_p4 = demand - p1 - p3
    assert demand - p1 == press
    assert 2 * (candidates - blockers) == p3
    assert required_p4 == press - p3
    return {
        "a": a,
        "b": b,
        "n": n,
        "q": q,
        "s": s,
        "demand": demand,
        "p1": p1,
        "p1Reserved": p1_reserved,
        "quadraticCandidates": candidates,
        "cooccurrenceBlocked": blockers,
        "p3FreeOrderedBases": p3_free_bases,
        "p3": p3,
        "press": press,
        "coherenceTax": 0,
        "strictP4Required": required_p4,
        "endpointOnlyGap": demand - p3,
    }


def coherence_toy() -> dict:
    """Two halves of one base cannot be split across two components."""

    demand = (1, 1)
    raw_eligible = ({0, 1}, {0, 1})
    raw_checks = {}
    for mask in (1, 2, 3):
        shore = {i for i in range(2) if mask & (1 << i)}
        reach = sum(bool(eligible & shore) for eligible in raw_eligible)
        raw_checks[mask] = (sum(demand[i] for i in shore), reach)
        assert raw_checks[mask][0] <= raw_checks[mask][1]

    label_checks = {}
    for label in (0, 1):
        failures = []
        for mask in (1, 2, 3):
            shore = {i for i in range(2) if mask & (1 << i)}
            raw_reach = sum(bool(eligible & shore) for eligible in raw_eligible)
            filtered_reach = sum(
                label in eligible and label in shore for eligible in raw_eligible
            )
            tax = raw_reach - filtered_reach
            assert filtered_reach + tax == raw_reach
            shore_demand = sum(demand[i] for i in shore)
            if shore_demand > filtered_reach:
                failures.append({
                    "shore": sorted(shore),
                    "demand": shore_demand,
                    "rawReach": raw_reach,
                    "coherenceTax": tax,
                    "filteredReach": filtered_reach,
                })
        assert failures
        label_checks[label] = failures
    return {
        "rawHallPasses": True,
        "coherentAssignmentExists": False,
        "fixedLabelFailures": label_checks,
    }


def main() -> int:
    result = {
        "schema": "R35_SOURCE_FLOOR_EXACT_V1",
        "pinnedN10": pinned_n10(),
        "r35K33": anchored_double_star(3, 3, 29, 2),
        "coherenceToy": coherence_toy(),
    }
    k33 = result["r35K33"]
    assert k33["demand"] == 72
    assert k33["p1"] == 38
    assert k33["p3"] == 24
    assert k33["strictP4Required"] == 10
    assert k33["endpointOnlyGap"] == 48
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    print("PASS exact source-floor identities and coherence-tax obstruction")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
