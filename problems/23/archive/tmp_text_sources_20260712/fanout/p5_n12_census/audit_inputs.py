"""Audit that an N=12 Pattern-5 fixture is reconstructible without guesses."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WRITEUP = ROOT / "problems" / "23" / "writeup"
PHT = ROOT / "tmp" / "fanout" / "pht_n12_direct"
FIXTURE = ROOT / "tmp" / "fanout" / "r29_fullbank_local" / "n12_first_micro_fixture.json"
sys.path.insert(0, str(WRITEUP))
sys.path.insert(0, str(PHT))

import n12_pht as n12  # noqa: E402
from p5_core import analyze_rows, make_graph_context  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    g6 = fixture["g6"]
    choice = tuple(fixture["choice"])
    n, edges = n12.dec(g6)
    info = n12.loads(n, edges)
    assert info is not None
    assert all(length == 5 for length in info["ell"].values())
    families = n12.shortest_row_families(info)
    rows = n12.rows_for_choice(families, choice)
    ctx = make_graph_context(n, info["Bset"], info["Mset"])
    analysis = analyze_rows(ctx, rows, details=True)
    state = analysis["state"]

    comparisons = {
        "edges": [list(e) for e in sorted(edges)] == fixture["edges"],
        "blue": state["blue"] == fixture["blue"],
        "bad": state["bad"] == fixture["bad"],
        "rows": state["rows"] == fixture["rows"],
        "selected": state["selected"] == fixture["selected"],
        "support": state["support"] == fixture["support"],
        "activeEdges": state["activeEdges"] == fixture["activeEdges"],
        "demandedActiveEdges": (
            state["demandedActiveEdges"] == fixture["demandedActiveEdges"]
        ),
        # The fixture generator labels every selected off-support component
        # ``activeComponents``.  Compare its actual serialized semantics, then
        # derive the true bad-pair-containing active subset independently.
        "fixtureActiveComponentsField": (
            state["selectedComponents"] == fixture["activeComponents"]
        ),
    }
    assert all(comparisons.values()), comparisons

    derivation = {
        "graph": "graph6 decoded by pinned dec",
        "cut": "loads selects an exact connected Gamma-minimum maximum cut",
        "rows": "complete shortest-row families from info['cyc'] plus explicit choice",
        "pairCount": "recomputed by integer row co-occurrence",
        "activeScope": "recomputed from selected off-support B-components containing a bad pair",
        "fixtureFieldNote": (
            "fixture['activeComponents'] serializes all selected off-support "
            "components; true active components are re-filtered by bad-pair containment"
        ),
        "quiescentComponents": "recomputed as components of B[V minus activeScope]",
        "activeBoundaries": "recomputed from literal B edges crossing each quiescent component",
        "componentEquality": "recomputed in the selected off-support graph",
        "reservations": "literal half=0 demanded-active-edge predicate",
        "switchLoss": "exact dB(S)-dM(S) from edge crossings",
        "guessedFields": [],
    }
    result = {
        "schema": "P5_N12_INPUT_AUDIT_V1",
        "verdict": "RECONSTRUCTIBLE_WITHOUT_GUESSED_FIELDS",
        "fixture": {"g6": g6, "choice": list(choice), "familySizes": list(map(len, families))},
        "comparisons": comparisons,
        "derivation": derivation,
        "pattern5": {
            "keys": analysis["p5Stats"]["keys"],
            "ownerArcs": analysis["p5Stats"]["ownerArcs"],
            "newOwnerArcsVsP1P4": analysis["p5Stats"]["newOwnerArcsVsP1P4"],
            "components": analysis["p5Audit"]["components"],
            "checkedSwitches": analysis["p5Audit"]["checkedSwitches"],
            "negativeSwitches": analysis["p5Audit"]["negativeSwitches"],
            "reservedCandidates": analysis["p5Audit"]["reservedCandidates"],
        },
        "checks": {
            "oneClaudeBefore": analysis["oneClaudeBefore"],
            "oneClaudeAfter": analysis["oneClaudeAfter"],
            "oneFive": analysis["oneFive"],
            "microBeforeP5": analysis["microBeforeP5"],
            "microFive": analysis["microFive"],
        },
        "sha256": {
            "fixture": sha256(FIXTURE),
            "n12Pht": sha256(PHT / "n12_pht.py"),
            "claudePattern5": sha256(WRITEUP / "_claude_r29_pattern5_gate.py"),
            "p5Core": sha256(HERE / "p5_core.py"),
        },
    }
    result["canonicalPayloadSha256"] = canonical_hash(result)
    output = HERE / "input_audit.json"
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
