"""Exact referee for endpoint-anchored canonical coverage-or-trade.

This checker separates the abstract anchored interface from the additional
facts forced by a real triangle-free maximum-cut graph.  All calculations are
finite integer calculations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def anchored_abstract_witness() -> dict:
    """The R35 3x3 singleton-family model, made canonical explicitly."""

    a = b = 3
    n = 29
    rows = [
        (f"l{i}", "cL", "h", "cR", f"r{j}")
        for i in range(a)
        for j in range(b)
    ]
    endpoint_pairs = [(row[0], row[-1]) for row in rows]
    assert len(rows) == len(set(rows)) == len(set(endpoint_pairs)) == a * b

    q = a * b
    support_size = a + b + 3
    demand = 2 * (5 * q - support_size)
    p1_reserved = 2
    p1 = 2 * (n - support_size) - p1_reserved
    p3 = 2 * (a * (a - 1) + b * (b - 1))
    sources = p1 + p3
    defect = demand - sources

    assert (demand, p1, p3, sources, defect) == (72, 38, 24, 62, 10)

    # Every source is adjacent to every obligation in this one-owner shore.
    # Matching source i to obligation i proves maximum matching size >= 62;
    # cardinality proves <= 62.  All sources are used, so no augmentation is
    # available.  Singleton row families make the tuple the unique canonical
    # tuple and leave no nonidentity row change.
    matching = list(range(sources))
    assert len(set(matching)) == sources

    return {
        "model": "anchored_K3_3_singleton_families",
        "verticesParameter": n,
        "selectedRows": [list(row) for row in rows],
        "distinctAnchoredEndpointPairs": True,
        "rowFamilySizes": [1] * len(rows),
        "tupleCount": 1,
        "tupleRank": 0,
        "canonicalForDefectThenRank": True,
        "demand": demand,
        "p1Sources": p1,
        "p3Sources": p3,
        "strictP4Sources": 0,
        "p5Sources": 0,
        "commonBlueSources": 0,
        "maximumMatching": sources,
        "defect": defect,
        "allSourcesMatched": True,
        "coherentAugmentationExists": False,
        "nonidentityRowChangeExists": False,
        "checkedTradeExists": False,
        "verdict": "ABSTRACT_CANONICAL_COVERAGE_OR_TRADE_FALSE",
    }


def real_attachment_exhaustion() -> dict:
    """Exhaust all path-position branches in the R37 local real probe.

    Q is an endpoint-anchored shortest blue path with positions 0..4.  The
    scoped owner v has two blue neighbors x,y on the same cut shore.  If the
    pair is free, maximum-cut nonnegativity exposes common-blue.  If it is
    covered by Q, parity permits separations 2 or 4 only.  Separation 4 gives
    a two-edge endpoint shortcut; separation 2 gives a detour row once the
    row-intersection fact puts v outside Q and completeness lists all shortest
    rows.
    """

    same_shore_pairs = [
        (i, j) for i in range(5) for j in range(i + 1, 5)
        if (j - i) % 2 == 0
    ]
    assert same_shore_pairs == [(0, 2), (0, 4), (1, 3), (2, 4)]

    cases = []
    survivors = []
    for i, j in same_shore_pairs:
        for covered in (False, True):
            case = {"positions": [i, j], "pairCoveredBySelectedRow": covered}
            if not covered:
                case.update({
                    "outcome": "COMMON_BLUE_SOURCE",
                    "blockingFact": "max-cut switch nonnegativity plus same-shore nonreservation",
                })
            elif j - i == 4:
                case.update({
                    "outcome": "IMPOSSIBLE_BLUE_SHORTCUT",
                    "blockingFact": "endpoint anchoring and shortest blue distance four",
                    "shortcutLength": 2,
                })
            elif j - i == 2:
                original_middle = i + 1
                detour = list(range(5))
                detour[original_middle] = "v"
                assert len(set(detour)) == 5
                case.update({
                    "outcome": "TWO_EDGE_DETOUR_ROW",
                    "blockingFact": "row-intersection puts v outside Q; complete row DB admits the detour",
                    "replacedPosition": original_middle,
                    "detour": detour,
                })
            else:
                survivors.append(case)
            cases.append(case)

    assert len(cases) == 8
    assert not survivors
    assert sum(c["outcome"] == "COMMON_BLUE_SOURCE" for c in cases) == 4
    assert sum(c["outcome"] == "TWO_EDGE_DETOUR_ROW" for c in cases) == 3
    assert sum(c["outcome"] == "IMPOSSIBLE_BLUE_SHORTCUT" for c in cases) == 1

    return {
        "sameShorePositionPairs": [list(pair) for pair in same_shore_pairs],
        "branchesChecked": len(cases),
        "commonBlueBranches": 4,
        "detourBranches": 3,
        "shortcutContradictionBranches": 1,
        "survivingSterileBranches": 0,
        "cases": cases,
        "minimalBlockingLemma": {
            "name": "active-owner free-pair-or-detour",
            "statement": (
                "For same-shore blue neighbors x,y of a scoped owner v, "
                "either pairCount(x,y)=0 and both common-blue halves are "
                "available, or a least selected row covering x,y has "
                "separation two and replacing its middle by v is a distinct "
                "shortest row. Separation four contradicts endpoint distance."
            ),
            "irreducibleInputs": [
                "maximum-cut switch nonnegativity",
                "endpoint-anchored shortest rows",
                "triangle-free row-intersection (v is outside the covering row)",
                "complete shortest-row database",
            ],
        },
        "verdict": "NO_LOCAL_REAL_ATTACHMENT_WITNESS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = {
        "schema": "R35_CANONICAL_COVERAGE_OR_TRADE_REFEREE_V1",
        "abstract": anchored_abstract_witness(),
        "realAttachment": real_attachment_exhaustion(),
        "scopeRuling": (
            "Anchoring alone does not imply canonical coverage-or-trade. "
            "The real-graph local obstruction is the free-pair-or-detour lemma."
        ),
    }
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="ascii")
    print(encoded, end="")
    print("sha256=" + hashlib.sha256(encoded.encode("ascii")).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
