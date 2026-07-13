"""Exact R29 prune/slot-transport audit; integer arithmetic only."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
HALL = ROOT / "tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py"
HALL_CERT = ROOT / "tmp/fanout/r29_gate/d05/retry2/cut_certificate.json"
BEST_TUPLE = ROOT / "tmp/fanout/r29_gate/d09/retry2/best_tuple.json"
OWNERS = (0, 1, 2)
FILES = (
    "problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean",
    "problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean",
    "problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean",
    "problems/23/lean/Erdos23Delta0/Gamma/CheckedC5BaseTransfer.lean",
    "problems/23/lean/Erdos23Delta0/Gamma/CheckedRowCompanionBaseTransfer.lean",
    "problems/23/lean/Erdos23Delta0/Ell5/ConcreteCage/Bank.lean",
    "problems/23/lean/Erdos23Delta0/Ell5DistancePrune.lean",
    "problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean",
    "problems/23/lean/Erdos23Delta0/AggregateLedgerNoIncidenceCounterexample.lean",
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    out = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(out)
    return out


def grep(pattern):
    command = ["git", "grep", "-n", "-I", "-E", pattern, "--",
               "problems/23/lean/Erdos23Delta0"]
    run = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    assert run.returncode in (0, 1), run.stderr
    return {"command": " ".join(command), "returncode": run.returncode,
            "matches": [x for x in run.stdout.splitlines() if x]}


def cited_lines(relative):
    needles = ("prune", "Prune", "no_double_spend", "source_injective",
               "legal edge-to-token incidence", "remaining open theorem",
               "does not determine port incidence", "dist_eq_of_le_of_geodesic_sub")
    lines = (ROOT / relative).read_text(encoding="utf-8").splitlines()
    return [{"line": i, "text": line.strip()}
            for i, line in enumerate(lines, 1)
            if any(n in line for n in needles)]


def main():
    lead = module("r29_lead_prune_audit", LEAD)
    hall = module("r29_hall_prune_audit", HALL)
    data = lead.build()
    assert (data["n"], len(data["blue"]), len(data["bad"]), len(data["graph"])) == (2943, 7039, 1383, 8422)
    assert sum(data["classMax"]) == 7039
    assert len(data["atoms"]) == len(data["rows"]) == 1383

    adj = lead.adjacency(data["n"], data["blue"])
    path_hist = Counter()
    gamma = 0
    for u, v in data["atoms"]:
        dist, count = lead.bfs(adj, u)
        assert dist[v] == 4
        path_hist[count[v]] += 1
        gamma += (dist[v] + 1) ** 2
    assert path_hist == Counter({1: 707, 680: 676}) and gamma == 34575

    selector_hist = Counter()
    atoms = data["atoms"][data["selectorStart"]:data["selectorStop"]]
    for atom, meta in zip(atoms, data["selectorMeta"]):
        dist, count = lead.bfs(adj, atom[0])
        row = tuple(meta["anchorRow"])
        assert lead.edge(row[0], row[-1]) == atom
        assert len(row) == 5 and dist[row[-1]] == 4
        assert all(lead.edge(x, y) in data["blue"] for x, y in zip(row, row[1:]))
        selector_hist[count[atom[1]]] += 1
    assert selector_hist == Counter({680: 676})

    incidence = hall.load_untrusted_incidence()
    rebuilt = hall.rebuild_scope(incidence)
    rows, pair, load, support, active_edges, active_vertices, demanded, collision, hit = rebuilt
    masks, reasons, companions = hall.owner_sources(incidence, pair, active_edges, active_vertices)
    demand_by_owner = {o: collision.get(o, 0) + hit.get(o, 0) for o in OWNERS}
    reason_hist = Counter(reasons.values())
    assert sum(demand_by_owner.values()) == 19953
    assert len(masks) == 19925
    assert reason_hist == Counter({1: 17325, 2: 2600})

    provider_scan = grep("CheckedPruneStep|localRankDecrease|moveSound|slotTransport|SlotTransport|pruneTransport|PruneTransport")
    abstract_scan = grep("PruneKey|CapKind\\.prune|LocalBankKind")
    existence_scan = grep("Ell5FullBankRelaxedCover_exists|Ell5FullBankRelaxedCover_globalPackage_exists")
    assert provider_scan["matches"] == [] and abstract_scan["matches"]

    # There is no operational predicate with which to classify a row rewrite.
    # This is the set of instantiated production prune sources, not an assertion
    # about what a future provider could construct.
    prune_sources = set()
    overlap = prune_sources.intersection(masks)
    incremental = prune_sources.difference(masks)
    assert not overlap and not incremental
    defect = sum(demand_by_owner.values()) - len(masks)
    after = defect - len(incremental)
    assert defect == after == 28

    result = {
        "schema": "R29 prune/slot-transport exact audit v1",
        "status": "UNDEFINED",
        "status_reason": "Abstract prune labels and consumer checks exist, but no graph-derived prune-step, local-rank, injective slot-move, reachability, or real-graph package provider is implemented.",
        "reconstruction": {
            "n": data["n"], "edges": len(data["graph"]), "blue": len(data["blue"]),
            "bad": len(data["bad"]), "max_cut": sum(data["classMax"]),
            "rows": len(data["rows"]), "gamma": gamma,
            "row_shortest_path_count_histogram": {str(k): v for k, v in sorted(path_hist.items())},
            "selector_families": len(data["selectorMeta"]), "selector_rows_per_family": 680,
            "verified_anchor_rows": sum(selector_hist.values()),
            "canonical_incidence_sha256": hashlib.sha256(lead.canonical_bytes(data)).hexdigest(),
            "hall_incidence_sha256": hall.incidence_sha(incidence),
            "all_anchor_tuple_external_file_sha256": sha(BEST_TUPLE) if BEST_TUPLE.exists() else None,
        },
        "hub_shore": {
            "owners": list(OWNERS), "demand_by_owner": {str(k): v for k, v in sorted(demand_by_owner.items())},
            "demand": sum(demand_by_owner.values()), "implemented_base_freehalf_sources": len(masks),
            "base_source_reason_histogram": {"same_first_only": reason_hist[1], "row_companion_only": reason_hist[2], "both": reason_hist[3]},
            "auxiliary_defect": defect,
        },
        "prune_operational_audit": {
            "alternative_shortest_rows_exist": True,
            "alternative_rows_are_not_prune_steps_without_provider": True,
            "implemented_graph_derived_prune_source_records": len(prune_sources),
            "implemented_prune_transport_maps": 0, "local_rank_decrease_checks": 0,
            "prune_sources_reachable_from_hub_shore": 0,
            "injective": True, "injectivity_is_vacuous": True,
            "overlap_with_existing_base_sources": len(overlap),
            "new_distinct_sources_after_overlap_removal": len(incremental),
            "incremental_exact_capacity_units": len(incremental),
            "defect_after_all_enumerable_implemented_prune_sources": after,
            "no_double_spend": True, "no_double_spend_is_vacuous": True,
            "interpretation": "Zero is attributable enumerable implemented prune capacity, not an upper bound on an unimplemented future provider.",
        },
        "provider_boundary": {
            "prose_contract": ["problems/23/writeup/WALL_ATTACK_R19_GPTPRO56.md:19-25", "problems/23/writeup/WALL_ATTACK_R19_GPTPRO56.md:36-40", "problems/23/writeup/WALL_ATTACK_R20_GPTPRO56.md:39-50"],
            "unproved_provider": "A real-graph CheckedPruneStep/CheckedTransferMatching constructor with old/new shortest rows, same cut bad set, strict local rank decrease, injective move/moveSound on affected half-slot keys, and component preservation; ultimately Ell5FullBankRelaxedCover_exists/globalPackage_exists.",
            "concrete_provider_symbol_matches": provider_scan,
            "abstract_label_matches": abstract_scan,
            "existence_name_matches_are_comments_only": existence_scan,
        },
        "source_manifest": {f: {"sha256": sha(ROOT / f), "lines": cited_lines(f)} for f in FILES},
        "input_hashes": {"lead_python": sha(LEAD), "hall_rebuilder": sha(HALL), "hall_cut_certificate": sha(HALL_CERT)},
        "assertions": {
            "canonical_counts": True, "all_anchor_hub_demand_19953": sum(demand_by_owner.values()) == 19953,
            "implemented_base_reach_19925": len(masks) == 19925, "auxiliary_defect_28": defect == 28,
            "no_compiled_prune_provider_symbol": not provider_scan["matches"],
            "enumerable_incremental_prune_capacity_zero": len(incremental) == 0,
            "final_status_undefined": True,
        },
    }
    out = HERE / "audit.json"
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "demand": 19953, "base_reach": 19925,
                      "defect": defect, "prune_sources": 0, "incremental_prune_capacity": 0,
                      "audit_sha256": sha(out)}, sort_keys=True))


if __name__ == "__main__":
    main()
