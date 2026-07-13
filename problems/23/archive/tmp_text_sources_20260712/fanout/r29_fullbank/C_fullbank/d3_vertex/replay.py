from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
OUT = HERE / "result.json"
SHORE = (0, 1, 2)


def norm(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def frac(x: Fraction) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def main() -> None:
    spec = importlib.util.spec_from_file_location("r29_lead", LEAD)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    raw = mod.build()

    n = int(raw["n"])
    blue = set(raw["blue"])
    bad = set(raw["bad"])
    rows = list(raw["rows"])
    for j, meta in enumerate(raw["selectorMeta"]):
        rows[raw["selectorStart"] + j] = tuple(meta["anchorRow"])
    rows = tuple(rows)

    row_count = Counter(v for row in rows for v in row)
    T = {v: 5 * row_count[v] for v in range(n)}
    candidate_cap = {v: max(0, n - T[v]) for v in range(n)}
    support = {norm(u, v) for row in rows for u, v in zip(row, row[1:])}
    core = {v for row in rows for v in row}
    off = {e for e in blue if e not in support and (e[0] in core or e[1] in core)}
    internal = {e for e in off if e[0] in core and e[1] in core}
    boundary = off - internal

    blue_deg = Counter(v for e in blue for v in e)
    bad_deg = Counter(v for e in bad for v in e)
    off_deg = Counter(v for e in off for v in e)
    internal_deg = Counter(v for e in internal for v in e)

    def vertex(v: int) -> dict:
        dB, dM = blue_deg[v], bad_deg[v]
        return {
            "v": v,
            "inSelectedRowCore": v in core,
            "rowMultiplicity": row_count[v],
            "T_equals_5_times_rowMultiplicity": T[v],
            "candidateMax0NminusT": candidate_cap[v],
            "singletonDeltaBCard": dB,
            "singletonDeltaMCard": dM,
            "singletonDeltaBMinusDeltaM": dB - dM,
            "allOffSupportIncidentDegree": off_deg[v],
            "allOffSupportHalfLoad": frac(Fraction(off_deg[v], 2)),
            "internalOffSupportIncidentDegree": internal_deg[v],
            "internalEndpointHalfLoad": frac(Fraction(internal_deg[v], 2)),
            "candidateInternalMargin": frac(Fraction(candidate_cap[v]) - Fraction(internal_deg[v], 2)),
        }

    internal_pairs = sorted((e, v) for e in internal for v in e if v in core)
    shore_pairs = [(e, v) for e, v in internal_pairs if v in SHORE]
    margins = {v: Fraction(candidate_cap[v]) - Fraction(internal_deg[v], 2) for v in core}
    failing = sorted(v for v in core if margins[v] < 0)
    min_margin = min(margins.values())
    result = {
        "format": "r29-vertex-slack-audit-v1",
        "inputs": {
            "lead": str(LEAD.relative_to(ROOT)).replace("\\", "/"),
            "leadSha256": hashlib.sha256(LEAD.read_bytes()).hexdigest(),
            "N": n,
            "shore": list(SHORE),
            "tuple": "all-anchor",
        },
        "graph": {
            "blueEdges": len(blue), "badEdges": len(bad), "edges": len(blue | bad),
            "rows": len(rows), "selectedRowCoreVertices": len(core),
            "selectedSupportEdges": len(support),
            "offSupportBlueIncidentToCore": len(off),
            "internalOffSupportBlue": len(internal),
            "boundaryOffSupportBlue": len(boundary),
        },
        "candidateCapacity": {
            "definition": "max(0,N-T(v)), with T(v)=sum of selected row lengths through v=5*rowMultiplicity(v)",
            "sumAllVertices": sum(candidate_cap.values()),
            "sumSelectedRowCore": sum(candidate_cap[v] for v in core),
            "sumShore": sum(candidate_cap[v] for v in SHORE),
            "positiveVerticesAll": sum(candidate_cap[v] > 0 for v in range(n)),
            "positiveVerticesCore": sum(candidate_cap[v] > 0 for v in core),
        },
        "singletonCut": {
            "sumDeltaBAllVertices": sum(blue_deg.values()),
            "sumDeltaMAllVertices": sum(bad_deg.values()),
            "sumDeltaBMinusDeltaMAllVertices": sum(blue_deg.values()) - sum(bad_deg.values()),
        },
        "endpointRoutingCandidates": {
            "internalEdgeEndpointPairs": len(internal_pairs),
            "shoreInternalEdgeEndpointPairs": len(shore_pairs),
            "shorePairs": [[list(e), v] for e, v in shore_pairs],
            "totalInternalHalfLoad": frac(Fraction(len(internal_pairs), 2)),
            "shoreInternalHalfLoad": frac(Fraction(len(shore_pairs), 2)),
            "verticesFailingCandidateInternalCapacity": failing,
            "failingVertexCount": len(failing),
            "candidateInternalCapacityObligationPasses": not failing,
        },
        "shoreVertices": [vertex(v) for v in SHORE],
        "extremaOnCore": {
            "minCandidateInternalMargin": frac(min_margin),
            "verticesAtMinCandidateInternalMargin": sorted(v for v in core if margins[v] == min_margin),
            "maxT": max((T[v], v) for v in core),
            "maxInternalDegree": max((internal_deg[v], v) for v in core),
        },
        "compiledLegality": {
            "r29IncidenceProviderFound": False,
            "r29CapacityProviderFound": False,
            "actuallyCertifiedVertexSlackSinksForThisPayload": 0,
            "status": "candidate-only; constructors require explicit hendpointLegal/hincVertex and hslack/hvertex hypotheses",
        },
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
