#!/usr/bin/env python3
"""Independent CNF encoding of the rooted t=5 support constraints.

This module intentionally does not import the CP-SAT generator or any of its
helpers.  It reconstructs the support-level claim directly from the published
rooted specification.  The default encoding omits connectivity and all label
symmetry breaking, so UNSAT is a certificate for a strict relaxation of the
generator model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


V, M, A, B = 0, 1, 2, 3
X, Y = 0, 1


@dataclass
class Encoding:
    cnf: CNF
    pool: IDPool
    edge: dict[tuple[int, int], int]
    d2_left: dict[tuple[int, int], int]
    d2_right: dict[tuple[int, int], int]
    d4_left: dict[tuple[int, int], int]
    d4_right: dict[tuple[int, int], int]


def pair(a: int, b: int) -> tuple[int, int]:
    if a == b:
        raise ValueError("pair endpoints must differ")
    return (a, b) if a < b else (b, a)


def add_equiv_and(cnf: CNF, out: int, terms: list[int]) -> None:
    """Add out <-> conjunction(terms), where terms may be signed literals."""
    if not terms:
        cnf.append([out])
        return
    for term in terms:
        cnf.append([-out, term])
    cnf.append([out] + [-term for term in terms])


def add_equiv_or(cnf: CNF, out: int, terms: list[int]) -> None:
    """Add out <-> disjunction(terms), where terms may be signed literals."""
    if not terms:
        cnf.append([-out])
        return
    for term in terms:
        cnf.append([-term, out])
    cnf.append([-out] + terms)


def add_cardinality(
    cnf: CNF,
    pool: IDPool,
    lits: list[int],
    kind: str,
    bound: int,
) -> None:
    if kind == "eq":
        enc = CardEnc.equals(lits=lits, bound=bound, vpool=pool, encoding=EncType.seqcounter)
    elif kind == "ge":
        enc = CardEnc.atleast(lits=lits, bound=bound, vpool=pool, encoding=EncType.seqcounter)
    else:
        raise ValueError(kind)
    cnf.extend(enc.clauses)


def build_encoding(left_n: int, right_n: int, include_connectivity: bool) -> Encoding:
    if left_n < 7 or right_n < 5:
        raise ValueError("rooted t=5 support requires left >= 7 and right >= 5")

    cnf = CNF()
    pool = IDPool()
    edge = {
        (u, r): pool.id(("edge", u, r))
        for u in range(left_n)
        for r in range(right_n)
    }

    # Exactly 24 support edges and the two prescribed length-four blue rows.
    add_cardinality(cnf, pool, list(edge.values()), "eq", 24)
    for key in ((A, X), (V, X), (M, X), (V, Y), (M, Y), (B, Y)):
        cnf.append([edge[key]])

    # Both rooted owners have blue degree five; every support vertex is used.
    add_cardinality(cnf, pool, [edge[V, r] for r in range(right_n)], "eq", 5)
    add_cardinality(cnf, pool, [edge[M, r] for r in range(right_n)], "eq", 5)
    for u in range(left_n):
        cnf.append([edge[u, r] for r in range(right_n)])
    for r in range(right_n):
        cnf.append([edge[u, r] for u in range(left_n)])

    d2_left: dict[tuple[int, int], int] = {}
    for u in range(left_n):
        for w in range(u + 1, left_n):
            witnesses = []
            for r in range(right_n):
                z = pool.id(("d2L-witness", u, w, r))
                add_equiv_and(cnf, z, [edge[u, r], edge[w, r]])
                witnesses.append(z)
            out = pool.id(("d2L", u, w))
            add_equiv_or(cnf, out, witnesses)
            d2_left[u, w] = out

    d2_right: dict[tuple[int, int], int] = {}
    for r in range(right_n):
        for s in range(r + 1, right_n):
            witnesses = []
            for u in range(left_n):
                z = pool.id(("d2R-witness", r, s, u))
                add_equiv_and(cnf, z, [edge[u, r], edge[u, s]])
                witnesses.append(z)
            out = pool.id(("d2R", r, s))
            add_equiv_or(cnf, out, witnesses)
            d2_right[r, s] = out

    def l2(u: int, w: int) -> int:
        return d2_left[pair(u, w)]

    def r2(r: int, s: int) -> int:
        return d2_right[pair(r, s)]

    d4_left: dict[tuple[int, int], int] = {}
    for u in range(left_n):
        for w in range(u + 1, left_n):
            via = []
            for z in range(left_n):
                if z in (u, w):
                    continue
                t = pool.id(("d4L-via", u, w, z))
                add_equiv_and(cnf, t, [l2(u, z), l2(z, w)])
                via.append(t)
            path4 = pool.id(("d4L-path", u, w))
            add_equiv_or(cnf, path4, via)
            out = pool.id(("d4L", u, w))
            add_equiv_and(cnf, out, [path4, -l2(u, w)])
            d4_left[u, w] = out

    d4_right: dict[tuple[int, int], int] = {}
    for r in range(right_n):
        for s in range(r + 1, right_n):
            via = []
            for z in range(right_n):
                if z in (r, s):
                    continue
                t = pool.id(("d4R-via", r, s, z))
                add_equiv_and(cnf, t, [r2(r, z), r2(z, s)])
                via.append(t)
            path4 = pool.id(("d4R-path", r, s))
            add_equiv_or(cnf, path4, via)
            out = pool.id(("d4R", r, s))
            add_equiv_and(cnf, out, [path4, -r2(r, s)])
            d4_right[r, s] = out

    def ld4(u: int, w: int) -> int:
        return d4_left[pair(u, w)]

    cnf.append([ld4(A, B)])
    add_cardinality(cnf, pool, [ld4(V, u) for u in range(left_n) if u != V], "ge", 5)
    add_cardinality(cnf, pool, [ld4(M, u) for u in range(left_n) if u != M], "ge", 5)
    add_cardinality(cnf, pool, list(d4_left.values()) + list(d4_right.values()), "ge", 25)

    if include_connectivity:
        # Independent bounded-reachability encoding.  reach[z,k] means that z
        # is reachable from rooted left vertex V by a walk of length at most k.
        n = left_n + right_n
        reach = {(z, k): pool.id(("reach", z, k)) for z in range(n) for k in range(n)}
        for z in range(n):
            cnf.append([reach[z, 0]] if z == V else [-reach[z, 0]])
        for k in range(1, n):
            for z in range(n):
                alternatives = [reach[z, k - 1]]
                if z < left_n:
                    for r in range(right_n):
                        t = pool.id(("reach-step", z, k, left_n + r))
                        add_equiv_and(cnf, t, [reach[left_n + r, k - 1], edge[z, r]])
                        alternatives.append(t)
                else:
                    r = z - left_n
                    for u in range(left_n):
                        t = pool.id(("reach-step", z, k, u))
                        add_equiv_and(cnf, t, [reach[u, k - 1], edge[u, r]])
                        alternatives.append(t)
                add_equiv_or(cnf, reach[z, k], alternatives)
        for z in range(n):
            cnf.append([reach[z, n - 1]])

    return Encoding(cnf, pool, edge, d2_left, d2_right, d4_left, d4_right)


def canonical_json_sha(payload: dict) -> str:
    body = dict(payload)
    body.pop("canonicalSha256", None)
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", type=int, required=True)
    parser.add_argument("--right", type=int, required=True)
    parser.add_argument("--connectivity", action="store_true")
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--cnf", type=Path)
    parser.add_argument("--artifact", type=Path)
    parser.add_argument("--result", type=Path)
    args = parser.parse_args()

    artifact_check = None
    if args.artifact is not None:
        artifact = json.loads(args.artifact.read_text(encoding="utf-8"))
        artifact_check = {
            "left": artifact.get("left"),
            "right": artifact.get("right"),
            "terminal": artifact.get("supportTerminalStatus"),
            "storedSha256": artifact.get("canonicalSha256"),
            "recomputedSha256": canonical_json_sha(artifact),
        }
        artifact_check["shaMatches"] = (
            artifact_check["storedSha256"] == artifact_check["recomputedSha256"]
        )
        if (artifact_check["left"], artifact_check["right"]) != (args.left, args.right):
            raise SystemExit("artifact shore sizes do not match command line")

    enc = build_encoding(args.left, args.right, args.connectivity)
    if args.cnf is not None:
        args.cnf.parent.mkdir(parents=True, exist_ok=True)
        enc.cnf.to_file(str(args.cnf))

    with Solver(name=args.solver, bootstrap_with=enc.cnf.clauses) as solver:
        sat = solver.solve()
        model_edges = None
        if sat:
            truth = set(lit for lit in solver.get_model() if lit > 0)
            model_edges = [[u, r] for (u, r), var in sorted(enc.edge.items()) if var in truth]

    result = {
        "schema": "independent-rooted-t5-cnf-v1",
        "left": args.left,
        "right": args.right,
        "connectivityEncoded": args.connectivity,
        "labelSymmetryEncoded": False,
        "variables": enc.pool.top,
        "clauses": len(enc.cnf.clauses),
        "solver": args.solver,
        "status": "SAT" if sat else "UNSAT",
        "modelEdges": model_edges,
        "artifactCheck": artifact_check,
    }
    raw = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("ascii")
    result["canonicalSha256"] = hashlib.sha256(raw).hexdigest()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.result is not None:
        args.result.parent.mkdir(parents=True, exist_ok=True)
        args.result.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
