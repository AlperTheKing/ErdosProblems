"""Exact replay of the R41 two-edge-detour support dichotomy."""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
R41 = ROOT / "tmp" / "fanout" / "r41_rotor_realization"
P5 = ROOT / "tmp" / "fanout" / "p5_n12_census"
for path in (R41, P5):
    sys.path.insert(0, str(path))

import p5_core as p5  # noqa: E402
import search_rotor_realization as rotor  # noqa: E402


def row_edges(row: tuple[int, ...]) -> set[tuple[int, int]]:
    return {rotor.edge(x, y) for x, y in zip(row, row[1:])}


def equality_fixture() -> dict:
    q = (0, 1, 2, 3, 4)
    qp = (0, 1, 5, 3, 4)
    selector = (6, 5, 7, 8, 9)
    blue = row_edges(q) | row_edges(qp) | row_edges(selector)
    bad = {rotor.edge(0, 4), rotor.edge(6, 9)}
    ctx = p5.make_graph_context(10, blue, bad)
    old = p5.reconstruct_state(ctx, (q, selector))
    new = p5.reconstruct_state(ctx, (qp, selector))
    entering = {rotor.edge(1, 5), rotor.edge(5, 3)}
    leaving = {rotor.edge(1, 2), rotor.edge(2, 3)}
    # The two edge-disjoint odd-cycle blocks give max-cut <= 6 + 4 = 10,
    # attained by the displayed bipartition.
    displayed_cut = len(blue)
    exact_maxcut = max(
        sum(((mask >> x) & 1) != ((mask >> y) & 1) for x, y in blue | bad)
        for mask in range(1 << 10)
    )
    complete_families = {
        "0-4": rotor.shortest_rows(10, blue, 0, 4),
        "6-9": rotor.shortest_rows(10, blue, 6, 9),
    }
    return {
        "order": 10,
        "triangleFree": rotor.triangle_free(10, blue | bad),
        "displayedCut": displayed_cut,
        "exactMaxcut": exact_maxcut,
        "completeFamilies": {
            key: [list(row) for row in family]
            for key, family in complete_families.items()
        },
        "enteringEdgesOldActive": entering <= old.active_edges,
        "oldPairCounts": [old.pair[2][1], old.pair[2][3]],
        "oldSupport": len(old.support),
        "newSupport": len(new.support),
        "newPairCounts": [new.pair[2][1], new.pair[2][3]],
        "createdOrderedZeroPairs": 4,
        "createdRawFreeHalfKeys": 8,
        "supportIdentity": new.support == (old.support - leaving) | entering,
        "pass": (
            rotor.triangle_free(10, blue | bad)
            and displayed_cut == exact_maxcut == 10
            and complete_families["0-4"] == (q, qp)
            and complete_families["6-9"] == (selector,)
            and entering <= old.active_edges
            and old.pair[2][1] == old.pair[2][3] == 1
            and len(new.support) == len(old.support)
            and new.pair[2][1] == new.pair[2][3] == 0
            and new.support == (old.support - leaving) | entering
        ),
    }


def main() -> int:
    cage = rotor.build_cage()
    bads = tuple(sorted(cage["bad"]))
    families = tuple(
        rotor.shortest_rows(cage["n"], cage["blue"], *bad) for bad in bads
    )
    ctx = p5.make_graph_context(cage["n"], cage["blue"], cage["bad"])

    checked = 0
    strict = 0
    equal = 0
    created_ordered_pairs = 0
    failures: list[dict] = []
    for choice in itertools.product(*(range(len(family)) for family in families)):
        rows = tuple(families[i][choice[i]] for i in range(len(bads)))
        old = p5.reconstruct_state(ctx, rows)
        for atom, family in enumerate(families):
            q = rows[atom]
            for replacement, qp in enumerate(family):
                if replacement == choice[atom]:
                    continue
                # Genuine two-edge middle replacement: outer four vertices fixed.
                if not (q[0:2] == qp[0:2] and q[3:5] == qp[3:5] and q[2] != qp[2]):
                    continue
                x, m, y, v = q[1], q[2], q[3], qp[2]
                new_edges = {rotor.edge(x, v), rotor.edge(v, y)}
                old_edges = {rotor.edge(x, m), rotor.edge(m, y)}
                # The support proof only uses the load-bearing part of
                # activeness: neither entering edge was already supported.
                if not new_edges.isdisjoint(old.support):
                    continue

                new_choice = list(choice)
                new_choice[atom] = replacement
                new_rows = tuple(
                    families[i][new_choice[i]] for i in range(len(bads))
                )
                new = p5.reconstruct_state(ctx, new_rows)
                disappearing = {e for e in old_edges if e not in new.support}
                expected = (old.support - disappearing) | new_edges
                unique = old.pair[m][x] == 1 and old.pair[m][y] == 1
                equality = len(new.support) == len(old.support)
                created = new.pair[m][x] == 0 and new.pair[m][y] == 0
                ok = (
                    new.support == expected
                    and len(new.support) >= len(old.support)
                    and equality == unique
                    and (not equality or created)
                )
                checked += 1
                strict += not equality
                equal += equality
                created_ordered_pairs += 4 if equality else 0
                if not ok:
                    failures.append({
                        "choice": list(choice),
                        "atom": atom,
                        "replacement": replacement,
                        "oldRow": list(q),
                        "newRow": list(qp),
                        "oldSupport": len(old.support),
                        "newSupport": len(new.support),
                        "unique": unique,
                        "created": created,
                    })

    fixture = equality_fixture()
    result = {
        "schema": "R41_SUPPORT_DICHOTOMY_V1",
        "cageOrder": cage["n"],
        "rowTuples": len(tuple(itertools.product(*(range(len(f)) for f in families)))),
        "checkedDirectedDetours": checked,
        "strictSupportGrowth": strict,
        "supportEquality": equal,
        "createdOrderedZeroPairsOnEquality": created_ordered_pairs,
        "equalityFixture": fixture,
        "failures": failures,
        "verdict": "PASS" if not failures and fixture["pass"] else "FAIL",
    }
    output = HERE / "support_dichotomy.json"
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, sort_keys=True))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
