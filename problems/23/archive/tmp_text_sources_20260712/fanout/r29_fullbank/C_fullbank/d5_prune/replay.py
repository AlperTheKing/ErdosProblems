"""Exact replay of the R29 N=2943 prune-provider audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]

FILES = {
    "typed_sources": ROOT / "problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean",
    "fullbank": ROOT / "problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean",
    "proper": ROOT / "problems/23/lean/Erdos23Delta0/Ell5/ConcreteCage/Proper.lean",
    "balance": ROOT / "problems/23/lean/Erdos23Delta0/Ell5/ConcreteCage/BalanceTriviality.lean",
    "ledger_sep": ROOT / "problems/23/lean/Erdos23Delta0/NeutralLensLedger.lean",
    "global_cert": ROOT / "tmp/fanout/r29_gate/d09/retry2/certificate.json",
    "hall_cert": ROOT / "tmp/fanout/r29_gate/d05/retry2/cut_certificate.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(text: str, fragment: str) -> None:
    assert fragment in text, fragment


def main() -> None:
    src = {key: path.read_text(encoding="utf-8") for key, path in FILES.items() if path.suffix == ".lean"}
    require(src["typed_sources"], "| prune (prune : PruneKey)")
    require(src["fullbank"], "pruneCapQ : ℚ")
    require(src["fullbank"], "prune_nonneg : 0 ≤ V.pruneCapQ")
    require(src["fullbank"], "view.pruneCapQ = P.ledger.spendOfKindLocal l CapKind.prune")
    require(src["proper"], "structure AmbientProperSubcage")
    require(src["ledger_sep"], "pruneIdentity : Balance C = Balance C' + Balance W + rem")
    require(src["balance"], "theorem balance_nonneg")
    require(src["balance"], "theorem no_negative_balance_cage")

    # There is no graph-to-prune constructor in any of the audited production APIs.
    forbidden_provider_fragments = (
        "pruneTokenOfAmbientProperSubcage",
        "pruneSourceOfLedgerSep",
        "pruneCapQ_of_graph",
        "pruneLegal_of_graph",
    )
    joined = "\n".join(src.values())
    assert not any(name in joined for name in forbidden_provider_fragments)

    global_cert = json.loads(FILES["global_cert"].read_text(encoding="utf-8"))
    hall_cert = json.loads(FILES["hall_cert"].read_text(encoding="utf-8"))
    assert global_cert["exact_state"]["score"] == 23115
    assert global_cert["lower_bound"]["minimum"] == 23115
    assert global_cert["lower_bound"]["unique_argmin_local_counts"] == [0, 0]
    witness = hall_cert["maximum_deficiency_cut"]
    assert witness["shore"] == [0, 1, 2]
    assert (witness["demand"], witness["neighborhood"], witness["gap"]) == (19953, 19925, 28)

    result = {
        "status": "NO_GRAPH_DERIVED_PRUNE_TOKEN",
        "fixture": {"N": 2943, "selector": "all-anchor", "shore": [0, 1, 2]},
        "exact": {
            "global_scoped_score": 23115,
            "global_minimum": 23115,
            "unique_minimizing_local_counts": [0, 0],
            "hall_demand": 19953,
            "hall_neighborhood": 19925,
            "hall_defect": 28,
            "justified_prune_token_count": 0,
            "justified_prune_capacity_hall_units": "0",
            "justified_prune_capacity_capQ": "0",
            "source_ids": [],
        },
        "selector_rewrite_test": {
            "can_count_as_prune": False,
            "reason": "row selection changes, but no strict vertex-set descendant or graph-to-token provider is constructed; all-anchor is already a global scoped-score minimum",
        },
        "missing_provider": {
            "name": "graph-derived prune-token provider",
            "must_construct": [
                "proper descendant/prunable block and complement",
                "ledger prune identity with nonnegative remainder",
                "typed PruneKey/sourceId and owning active component",
                "nonnegative capQ and legal port incidence",
                "injectivity/no-double-spend evidence",
                "semantic bridge from cage balance/remainder to port-Hall capacity",
            ],
        },
        "hashes": {key: sha256(path) for key, path in FILES.items()},
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
