#!/usr/bin/env python3
"""Independent replay of IRREGULAR19_INCIDENCE_SEED.json.

This verifier uses only Python's standard library and reconstructs every
claimed graph, incidence, block, and literal two-step quantity from raw JSON.
A zero exit certifies the coarse seed and its recorded semantic failure; it
does not certify an SSNC counterexample.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical_missing_edges() -> list[list[int]]:
    edges = [sorted((i, (i + 1) % 9)) for i in range(9)]
    edges += [[0, 9], [0, 10]]
    edges += [[i, 10 + i] for i in range(1, 9)]
    return sorted(edges)


def main() -> int:
    default = Path(__file__).with_name("IRREGULAR19_INCIDENCE_SEED.json")
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    raw = path.read_bytes()
    seed = json.loads(raw)

    require(seed["schema"] == "ssnc-irregular19-incidence-seed-v1", "schema")
    require(seed["status"] == "COARSE_SEED_ONLY_NOT_AN_SSNC_COUNTEREXAMPLE", "status")
    n = seed["n"]
    require(n == 19, "n")
    require(seed["vertices"] == list(range(n)), "canonical vertices")

    expected_missing = canonical_missing_edges()
    missing_json = seed["missing_graph"]["edges"]
    require(missing_json == expected_missing, "canonical missing graph")
    missing = {tuple(edge) for edge in missing_json}
    require(len(missing) == 19, "missing edge count")
    require(all(0 <= a < b < n for a, b in missing), "missing edge endpoints")

    missing_degree = [0] * n
    for a, b in missing:
        missing_degree[a] += 1
        missing_degree[b] += 1
    require(missing_degree == [4] + [3] * 8 + [1] * 10, "missing degrees by vertex")
    require(Counter(missing_degree) == Counter({1: 10, 3: 8, 4: 1}), "missing degree multiset")
    require(seed["missing_graph"]["expected_degree_by_vertex"] == missing_degree, "stored missing degrees")
    require(seed["missing_graph"]["expected_degree_multiset"] == {"1": 10, "3": 8, "4": 1}, "stored degree multiset")

    outs = seed["orientation"]["out_neighbors"]
    require(len(outs) == n, "orientation row count")
    outsets: list[set[int]] = []
    for v, row in enumerate(outs):
        require(row == sorted(row), f"out row {v} not sorted")
        require(len(row) == len(set(row)), f"out row {v} duplicate")
        require(all(isinstance(w, int) and 0 <= w < n for w in row), f"out row {v} range")
        require(v not in row, f"loop at {v}")
        require(len(row) == 8, f"outdegree at {v}")
        outsets.append(set(row))

    missing_arc_count = 0
    digon_count = 0
    unoriented_present_count = 0
    for a, b in combinations(range(n), 2):
        ab = b in outsets[a]
        ba = a in outsets[b]
        if (a, b) in missing:
            missing_arc_count += int(ab) + int(ba)
        else:
            digon_count += int(ab and ba)
            unoriented_present_count += int(not ab and not ba)
            require(ab ^ ba, f"present pair {a},{b} is not oriented exactly once")
    require(missing_arc_count == 0, "arcs on missing edges")
    require(digon_count == 0, "digons")
    require(unoriented_present_count == 0, "unoriented present pairs")
    require(sum(map(len, outs)) == 152, "arc count")

    blocks = seed["incidence"]["root_blocks_by_target"]
    require(len(blocks) == n, "target block count")
    expected_target_sizes = [2 * d - 1 for d in missing_degree]
    require(expected_target_sizes == [7] + [5] * 8 + [1] * 10, "target size formula")
    require(seed["incidence"]["expected_target_sizes"] == expected_target_sizes, "stored target sizes")

    block_missing_pairs = 0
    block_degree_rows = 0
    for target, block in enumerate(blocks):
        require(block == sorted(block), f"block {target} not sorted")
        require(len(block) == len(set(block)), f"block {target} duplicate")
        require(target not in block, f"diagonal incidence at target {target}")
        require(len(block) == expected_target_sizes[target], f"block size at target {target}")
        for a, b in combinations(block, 2):
            block_missing_pairs += int(tuple(sorted((a, b))) in missing)
        require(block_missing_pairs == 0, f"missing pair in block through target {target}")
        required = (len(block) - 1) // 2
        require(2 * required == len(block) - 1, f"block {target} even size")
        for v in block:
            induced_out = sum(w in outsets[v] for w in block if w != v)
            require(induced_out == required, f"block {target}, root {v} not regular")
            block_degree_rows += 1
    require(block_missing_pairs == 0, "block missing-edge avoidance")

    sources = [[u for u, block in enumerate(blocks) if v in block] for v in range(n)]
    stored_sources = seed["incidence"]["declared_unreachable_targets_by_source"]
    require(stored_sources == sources, "source fibres are not transpose of target blocks")
    require(all(row == sorted(row) and len(row) == 3 for row in sources), "source fibre size")
    require(seed["incidence"]["expected_source_size"] == 3, "stored source size")
    require(sum(map(len, sources)) == sum(map(len, blocks)) == 57, "incidence count")

    ledger = []
    literal_incidence_count = 0
    row_matches = 0
    strict_rows = 0
    false_declared = 0
    for v in range(n):
        direct = outsets[v]
        two_step_reach: set[int] = set()
        for middle in direct:
            two_step_reach.update(outsets[middle])
        new_second = sorted(two_step_reach - {v} - direct)
        literal_unreachable = sorted(set(range(n)) - {v} - direct - set(new_second))
        declared = sources[v]
        declared_only = sorted(set(declared) - set(literal_unreachable))
        literal_only = sorted(set(literal_unreachable) - set(declared))
        row_match = declared == literal_unreachable
        strict = len(new_second) < len(direct)
        ledger.append({
            "vertex": v,
            "out_degree": len(direct),
            "new_second_degree": len(new_second),
            "declared_unreachable": declared,
            "literal_unreachable": literal_unreachable,
            "declared_only": declared_only,
            "literal_only": literal_only,
            "biconditional_row_match": row_match,
            "strict_counterexample_inequality": strict,
        })
        literal_incidence_count += len(literal_unreachable)
        row_matches += int(row_match)
        strict_rows += int(strict)
        false_declared += len(declared_only)

    stored_snapshot = seed["literal_semantics_snapshot"]
    require(stored_snapshot["per_vertex"] == ledger, "stored semantic ledger")
    expected_summary = {
        "declared_incidence_count": 57,
        "literal_unreachable_incidence_count": literal_incidence_count,
        "biconditional_matching_rows": row_matches,
        "strict_rows": strict_rows,
    }
    require(stored_snapshot["summary"] == expected_summary, "stored semantic summary")

    # This exact seed is deliberately frozen as a coarse starting point.
    require(all(row["new_second_degree"] == 10 for row in ledger), "expected N2 failure ledger")
    require(literal_incidence_count == 0, "expected literal W count")
    require(row_matches == 0, "expected biconditional mismatch count")
    require(strict_rows == 0, "must not pass strict SSNC predicate")
    require(false_declared == 57, "declared-only incidence count")

    digest = hashlib.sha256(raw).hexdigest().upper()
    result = {
        "status": "PASS_COARSE_SEED_ONLY",
        "seed_sha256": digest,
        "vertices": n,
        "missing_edges": len(missing),
        "missing_degree_multiset": {"1": 10, "3": 8, "4": 1},
        "arcs": sum(map(len, outs)),
        "outdegree": 8,
        "target_block_sizes": {"1": 10, "5": 8, "7": 1},
        "incidences": 57,
        "regular_block_root_rows": block_degree_rows,
        "block_missing_pairs": block_missing_pairs,
        "literal_unreachable_incidences": literal_incidence_count,
        "biconditional_matching_rows": row_matches,
        "strict_rows": strict_rows,
        "declared_only_incidences": false_declared,
        "ssnc_counterexample": False,
    }
    print(json.dumps(result, sort_keys=True))
    for row in ledger:
        print(
            f"v={row['vertex']:02d} d+={row['out_degree']} "
            f"N2+={row['new_second_degree']} declaredW={row['declared_unreachable']} "
            f"literalW={row['literal_unreachable']} match={row['biconditional_row_match']} "
            f"strict={row['strict_counterexample_inequality']}"
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"AUDIT_FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)