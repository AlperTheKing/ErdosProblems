#!/usr/bin/env python3
"""Build proof-producing CNFs for the accepted live-x t=5 projection.

The projection keeps the 18 support vertices and adds seven isolated vertices,
so N=25.  It is intentionally not called a production extension: the exact
displayed switch in the source violates IsMaxCut.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "tmp/fanout/r42_graph_specific_exclusion/t5_live_x_classifier_v_l9_r9_5000.json"
MANIFEST = HERE / "live_x_cnf_manifest.json"


def edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_cnf(path: Path, variable_count: int, clauses: list[list[int]]) -> None:
    with path.open("w", newline="\n") as stream:
        stream.write(f"p cnf {variable_count} {len(clauses)}\n")
        for clause in clauses:
            stream.write(" ".join(map(str, clause)) + " 0\n")


def hom_cnf(n: int, edges: set[tuple[int, int]]) -> tuple[int, list[list[int]]]:
    def var(v: int, colour: int) -> int:
        return 1 + 5 * v + colour

    clauses: list[list[int]] = []
    for v in range(n):
        clauses.append([var(v, c) for c in range(5)])
        for a in range(5):
            for b in range(a + 1, 5):
                clauses.append([-var(v, a), -var(v, b)])
    for u, v in sorted(edges):
        for a in range(5):
            for b in range(5):
                if (a - b) % 5 not in (1, 4):
                    clauses.append([-var(u, a), -var(v, b)])
    return 5 * n, clauses


def core_q2_cnf(
    n: int,
    edges: set[tuple[int, int]],
    side: list[int],
    complement: int,
) -> tuple[int, list[list[int]]]:
    def var(v: int, cls: int) -> int:
        return 1 + 5 * v + cls

    pattern = [complement ^ s for s in (0, 0, 1, 0, 1)]
    clauses: list[list[int]] = []
    for v in range(n):
        for i in range(5):
            if side[v] != pattern[i]:
                clauses.append([-var(v, i)])
        for i in range(5):
            for j in range(i + 1, 5):
                clauses.append([-var(v, i), -var(v, j)])

    # At least two selected vertices in every class.  For a variable set X,
    # the clauses X\{x}, one per x, are exactly the threshold |X| >= 2.
    for i in range(5):
        allowed = [var(v, i) for v in range(n) if side[v] == pattern[i]]
        for omitted in allowed:
            clauses.append([lit for lit in allowed if lit != omitted])

    all_pairs = {(u, v) for u in range(n) for v in range(u + 1, n)}
    for u, v in sorted(all_pairs - edges):
        for i in range(5):
            j = (i + 1) % 5
            clauses.append([-var(u, i), -var(v, j)])
            clauses.append([-var(v, i), -var(u, j)])
    return 5 * n, clauses


def main() -> int:
    data = json.loads(SOURCE.read_text())
    hit = data["hit"]
    blue = {edge(*e) for e in hit["supportEdges"]}
    bad = {edge(atom["u"], atom["v"]) for atom in hit["selectedAtoms"]}
    edges = blue | bad
    n = 25
    left = int(data["left"])
    support_n = max(v for e in edges for v in e) + 1
    side = [0 if v < left else 1 for v in range(support_n)] + [0] * (n - support_n)

    outputs = []
    jobs = [("live_x_c5_hom.cnf", *hom_cnf(n, edges))]
    for complement in (0, 1):
        jobs.append(
            (
                f"live_x_core_q2_c{complement}.cnf",
                *core_q2_cnf(n, edges, side, complement),
            )
        )
    for filename, variables, clauses in jobs:
        path = HERE / filename
        write_cnf(path, variables, clauses)
        outputs.append(
            {
                "file": filename,
                "variables": variables,
                "clauses": len(clauses),
                "sha256": digest(path),
            }
        )

    payload = {
        "schema": "wave4-live-x-c5-core-cnf-v1",
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": digest(SOURCE),
        "projection": {"n": n, "support_n": support_n, "isolates_added": n - support_n},
        "counts": {"blue": len(blue), "bad": len(bad), "edges": len(edges)},
        "cnfs": outputs,
    }
    MANIFEST.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"manifest": str(MANIFEST.relative_to(ROOT)), "sha256": digest(MANIFEST)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
