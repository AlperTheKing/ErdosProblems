"""Exact targeted probe for active-scope-first P5 row selection.

This enumerates only pinned fixtures already present in the P5 census.  It
uses integer tuple state and Hall checks from p5_core; no floating point.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PHT = ROOT / "tmp/fanout/pht_n12_direct"
P5 = ROOT / "tmp/fanout/p5_n12_census"
sys.path.insert(0, str(PHT))
sys.path.insert(0, str(P5))

import n12_pht as n12
from p5_core import analyze_rows, make_graph_context


FIXTURES = (
    "J?BEFboL`{?",  # first pinned P1--P5 micro falsifier
    "K??E@cyjFgWk",  # pinned common-blue defect-13 fixture
)


def analyze_fixture(g6: str) -> dict:
    n, edges = n12.dec(g6)
    info = n12.loads(n, edges)
    assert info is not None and all(length == 5 for length in info["ell"].values())
    families = n12.shortest_row_families(info)
    sizes = tuple(map(len, families))
    ctx = make_graph_context(n, info["Bset"], info["Mset"])
    records = []
    for index, choice in enumerate(itertools.product(*(range(size) for size in sizes))):
        rows = n12.rows_for_choice(families, choice)
        a = analyze_rows(ctx, rows)
        records.append({
            "index": index,
            "choice": list(choice),
            "active": a["activeVertices"],
            "demand": a["microDemand"],
            "p5Keys": a["p5Stats"]["keys"],
            "p5OwnerArcs": a["p5Stats"]["ownerArcs"],
            "p5NewArcs": a["p5Stats"]["newOwnerArcsVsP1P4"],
            "margin": a["microFive"]["minimumMargin"],
            "full": a["microFive"]["full"],
        })

    first_two = min((r["active"], r["demand"]) for r in records)
    tied = [r for r in records if (r["active"], r["demand"]) == first_two]
    selectors = {}
    for metric in ("p5Keys", "p5OwnerArcs", "p5NewArcs"):
        best_reach = max(r[metric] for r in tied)
        winners = [r for r in tied if r[metric] == best_reach]
        selectors[metric] = {
            "bestReach": best_reach,
            "winnerCount": len(winners),
            "failureCount": sum(not r["full"] for r in winners),
            "firstWinner": winners[0],
            "firstFailure": next((r for r in winners if not r["full"]), None),
        }

    return {
        "g6": g6,
        "familySizes": list(sizes),
        "tuples": len(records),
        "minimumActiveThenDemand": list(first_two),
        "firstTwoTieCount": len(tied),
        "firstTwoFailureCount": sum(not r["full"] for r in tied),
        "selectors": selectors,
    }


def main() -> None:
    result = {
        "schema": "P5_SELECTION_ADVERSARY_LEX_PROBE_V1",
        "fixtures": [analyze_fixture(g6) for g6 in FIXTURES],
    }
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
