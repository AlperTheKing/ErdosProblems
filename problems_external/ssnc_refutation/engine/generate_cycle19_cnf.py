#!/usr/bin/env python3
"""Proof-capable CNF generator for the fixed K_19 - C_19 SSNC cell.

The production instance has one Boolean per present undirected edge.  A true
edge variable orients the edge from its smaller endpoint to its larger
endpoint.  All path, two-step reachability, and unreachable indicators are
defined biconditionally.  The only symmetry break is 0 -> 2.

The calibration subcommand does not run the production instance.  It pins a
known regular orientation, omits the counterexample row/column sums, solves
the now fully determined definitional CNF, and compares every semantic
indicator with an independent scalar computation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver


N = 19
CARDINALITY_ENCODING = EncType.seqcounter
CARDINALITY_ENCODING_NAME = "sequential-counter"
SCHEMA = "ssnc-fixed-cycle19-cnf-v1"


def is_missing_pair(v: int, w: int) -> bool:
    if v == w:
        return False
    return (v - w) % N in (1, N - 1)


def is_present_pair(v: int, w: int) -> bool:
    return v != w and not is_missing_pair(v, w)


def normalized_missing_edges() -> list[tuple[int, int]]:
    return sorted({tuple(sorted((v, (v + 1) % N))) for v in range(N)})


@dataclass(frozen=True)
class AuxRange:
    scope: str
    first: int
    last: int


class Cycle19CNF:
    """Deterministic semantic-variable allocation and CNF construction."""

    def __init__(
        self,
        *,
        enforce_unreachable_equalities: bool = True,
        orientation_pin: Sequence[Sequence[bool]] | None = None,
    ) -> None:
        self.enforce_unreachable_equalities = enforce_unreachable_equalities
        self.orientation_pin = orientation_pin
        self.pool = IDPool(start_from=1)
        self.clauses: list[list[int]] = []
        self.variable_names: dict[int, str] = {}
        self.aux_ranges: list[AuxRange] = []

        self.edge_vars: dict[tuple[int, int], int] = {}
        self.path_vars: dict[tuple[int, int, int], int] = {}
        self.reach2_vars: dict[tuple[int, int], int] = {}
        self.unreachable_vars: dict[tuple[int, int], int] = {}

        self._allocate_semantic_variables()
        self.semantic_top = self.pool.top
        self._add_biconditional_definitions()
        self._add_outdegree_constraints()
        if enforce_unreachable_equalities:
            self._add_unreachable_equalities()
        self.clauses.append([self.arc_lit(0, 2)])
        if orientation_pin is not None:
            self._add_orientation_pin(orientation_pin)
        self._assert_complete_variable_map()

    def _new_semantic_var(self, name: str) -> int:
        var = self.pool.id(name)
        if var in self.variable_names:
            raise AssertionError(f"duplicate variable id {var}: {name}")
        self.variable_names[var] = name
        return var

    def _allocate_semantic_variables(self) -> None:
        for v in range(N):
            for w in range(v + 1, N):
                if is_present_pair(v, w):
                    self.edge_vars[(v, w)] = self._new_semantic_var(
                        f"edge({v},{w})"
                    )

        for v in range(N):
            for w in range(N):
                if not is_present_pair(v, w):
                    continue
                for u in range(N):
                    if u == v or not is_present_pair(w, u):
                        continue
                    self.path_vars[(v, w, u)] = self._new_semantic_var(
                        f"path({v},{w},{u})"
                    )

        for v in range(N):
            for u in range(N):
                if u != v:
                    self.reach2_vars[(v, u)] = self._new_semantic_var(
                        f"reach2({v},{u})"
                    )

        for v in range(N):
            for u in range(N):
                if u != v:
                    self.unreachable_vars[(v, u)] = self._new_semantic_var(
                        f"unreachable({v},{u})"
                    )

    def arc_lit(self, v: int, w: int) -> int:
        """Return the signed literal meaning v -> w."""

        if not is_present_pair(v, w):
            raise ValueError(f"no orientation variable for pair ({v},{w})")
        a, b = sorted((v, w))
        var = self.edge_vars[(a, b)]
        return var if (v, w) == (a, b) else -var

    def _add_biconditional_definitions(self) -> None:
        # path(v,w,u) <-> (v->w and w->u)
        for (v, w, u), path_var in self.path_vars.items():
            first = self.arc_lit(v, w)
            second = self.arc_lit(w, u)
            self.clauses.extend(
                [
                    [-path_var, first],
                    [-path_var, second],
                    [path_var, -first, -second],
                ]
            )

        # reach2(v,u) <-> OR_w path(v,w,u)
        for (v, u), reach_var in self.reach2_vars.items():
            paths = [
                self.path_vars[(v, w, u)]
                for w in range(N)
                if (v, w, u) in self.path_vars
            ]
            if not paths:
                self.clauses.append([-reach_var])
                continue
            self.clauses.extend([[-path_var, reach_var] for path_var in paths])
            self.clauses.append([-reach_var, *paths])

        # unreachable(v,u) <-> (not v->u and not reach2(v,u)).  On a fixed
        # missing edge, the direct-arc conjunct is the constant true.
        for (v, u), unreachable_var in self.unreachable_vars.items():
            reach_var = self.reach2_vars[(v, u)]
            if is_present_pair(v, u):
                direct = self.arc_lit(v, u)
                self.clauses.extend(
                    [
                        [-unreachable_var, -direct],
                        [-unreachable_var, -reach_var],
                        [unreachable_var, direct, reach_var],
                    ]
                )
            else:
                if not is_missing_pair(v, u):
                    raise AssertionError((v, u))
                self.clauses.extend(
                    [
                        [-unreachable_var, -reach_var],
                        [unreachable_var, reach_var],
                    ]
                )

    def _add_cardinality(self, scope: str, literals: Sequence[int], bound: int) -> None:
        before = self.pool.top
        encoded = CardEnc.equals(
            lits=list(literals),
            bound=bound,
            vpool=self.pool,
            encoding=CARDINALITY_ENCODING,
        )
        self.clauses.extend(encoded.clauses)
        after = self.pool.top
        if after > before:
            self.aux_ranges.append(AuxRange(scope=scope, first=before + 1, last=after))
            for offset, var in enumerate(range(before + 1, after + 1), start=1):
                self.variable_names[var] = f"aux:{scope}:{offset}"

    def _add_outdegree_constraints(self) -> None:
        for v in range(N):
            outgoing = [self.arc_lit(v, w) for w in range(N) if is_present_pair(v, w)]
            if len(outgoing) != 16:
                raise AssertionError((v, len(outgoing)))
            self._add_cardinality(f"outdegree({v})=8", outgoing, 8)

    def _add_unreachable_equalities(self) -> None:
        for v in range(N):
            row = [self.unreachable_vars[(v, u)] for u in range(N) if u != v]
            self._add_cardinality(f"source-unreachable({v})=3", row, 3)
        for u in range(N):
            column = [self.unreachable_vars[(v, u)] for v in range(N) if v != u]
            self._add_cardinality(f"target-roots({u})=3", column, 3)

    def _add_orientation_pin(self, pin: Sequence[Sequence[bool]]) -> None:
        if len(pin) != N or any(len(row) != N for row in pin):
            raise ValueError("orientation pin must be a 19 by 19 Boolean matrix")
        for (v, w), var in self.edge_vars.items():
            forward = bool(pin[v][w])
            backward = bool(pin[w][v])
            if forward == backward:
                raise ValueError(f"pin does not orient present edge ({v},{w})")
            self.clauses.append([var if forward else -var])
        for v in range(N):
            if pin[v][v]:
                raise ValueError(f"pin contains loop at {v}")
            for w in range(v + 1, N):
                if is_missing_pair(v, w) and (pin[v][w] or pin[w][v]):
                    raise ValueError(f"pin orients missing edge ({v},{w})")

    def _assert_complete_variable_map(self) -> None:
        expected = set(range(1, self.pool.top + 1))
        actual = set(self.variable_names)
        if actual != expected:
            missing = sorted(expected - actual)
            extra = sorted(actual - expected)
            raise AssertionError(f"variable-map mismatch: missing={missing}, extra={extra}")

    @property
    def counts(self) -> dict[str, int]:
        return {
            "orientation": len(self.edge_vars),
            "path": len(self.path_vars),
            "reach2": len(self.reach2_vars),
            "unreachable": len(self.unreachable_vars),
            "semantic": self.semantic_top,
            "auxiliary": self.pool.top - self.semantic_top,
            "variables": self.pool.top,
            "clauses": len(self.clauses),
        }

    def dimacs_bytes(self) -> bytes:
        lines = [f"p cnf {self.pool.top} {len(self.clauses)}\n"]
        lines.extend(" ".join(map(str, clause)) + " 0\n" for clause in self.clauses)
        return "".join(lines).encode("ascii")

    def variable_map(self) -> dict[str, str]:
        return {str(var): self.variable_names[var] for var in range(1, self.pool.top + 1)}


def orientation_from_steps(steps: Iterable[int]) -> list[list[bool]]:
    step_set = {step % N for step in steps}
    out = [[False] * N for _ in range(N)]
    for v in range(N):
        for step in step_set:
            out[v][(v + step) % N] = True
    validate_regular_orientation(out)
    return out


def reverse_directed_triangle(
    orientation: Sequence[Sequence[bool]], triangle: tuple[int, int, int]
) -> list[list[bool]]:
    out = [list(row) for row in orientation]
    local_degrees = [
        sum(bool(out[v][w]) for w in triangle if w != v) for v in triangle
    ]
    if local_degrees != [1, 1, 1]:
        raise ValueError(f"not a directed triangle: {triangle}")
    for index, v in enumerate(triangle):
        for w in triangle[index + 1 :]:
            out[v][w], out[w][v] = out[w][v], out[v][w]
    validate_regular_orientation(out)
    return out


def validate_regular_orientation(out: Sequence[Sequence[bool]]) -> None:
    if len(out) != N or any(len(row) != N for row in out):
        raise ValueError("orientation must be 19 by 19")
    for v in range(N):
        if out[v][v]:
            raise ValueError(f"loop at {v}")
        if sum(bool(value) for value in out[v]) != 8:
            raise ValueError(f"outdegree is not 8 at {v}")
        for w in range(v + 1, N):
            if is_missing_pair(v, w):
                if out[v][w] or out[w][v]:
                    raise ValueError(f"oriented missing edge ({v},{w})")
            elif bool(out[v][w]) == bool(out[w][v]):
                raise ValueError(f"present edge ({v},{w}) is not oriented exactly once")
    if not out[0][2]:
        raise ValueError("orientation violates the safe symmetry 0 -> 2")


def calibration_orientation(name: str) -> list[list[bool]]:
    even = orientation_from_steps({2, 4, 6, 8, 10, 12, 14, 16})
    if name == "circulant-even":
        return even
    if name == "triangle-switch":
        return reverse_directed_triangle(even, (0, 3, 6))
    raise ValueError(f"unknown calibration template: {name}")


def scalar_indicators(
    orientation: Sequence[Sequence[bool]], builder: Cycle19CNF
) -> tuple[
    dict[tuple[int, int, int], bool],
    dict[tuple[int, int], bool],
    dict[tuple[int, int], bool],
]:
    paths = {
        key: bool(orientation[key[0]][key[1]] and orientation[key[1]][key[2]])
        for key in builder.path_vars
    }
    reach2 = {
        (v, u): any(
            orientation[v][w] and orientation[w][u] for w in range(N)
        )
        for v, u in builder.reach2_vars
    }
    unreachable = {
        (v, u): bool(not orientation[v][u] and not reach2[(v, u)])
        for v, u in builder.unreachable_vars
    }
    return paths, reach2, unreachable


def calibrate(name: str, *, solver_name: str = "cadical195") -> dict[str, object]:
    orientation = calibration_orientation(name)
    builder = Cycle19CNF(
        enforce_unreachable_equalities=False,
        orientation_pin=orientation,
    )
    expected_paths, expected_reach2, expected_unreachable = scalar_indicators(
        orientation, builder
    )

    with Solver(name=solver_name, bootstrap_with=builder.clauses) as solver:
        if not solver.solve():
            raise AssertionError(f"pinned calibration template is UNSAT: {name}")
        model = solver.get_model()
    truth = {literal for literal in model if literal > 0}

    mismatches: list[str] = []
    for key, var in builder.path_vars.items():
        if (var in truth) != expected_paths[key]:
            mismatches.append(f"path{key}")
    for key, var in builder.reach2_vars.items():
        if (var in truth) != expected_reach2[key]:
            mismatches.append(f"reach2{key}")
    for key, var in builder.unreachable_vars.items():
        if (var in truth) != expected_unreachable[key]:
            mismatches.append(f"unreachable{key}")
    if mismatches:
        raise AssertionError(f"derived-indicator mismatch: {mismatches[:20]}")

    second_sizes = []
    unreachable_rows = []
    unreachable_columns = []
    for v in range(N):
        second_sizes.append(
            sum(
                expected_reach2[(v, u)] and not orientation[v][u]
                for u in range(N)
                if u != v
            )
        )
        unreachable_rows.append(
            sum(expected_unreachable[(v, u)] for u in range(N) if u != v)
        )
    for u in range(N):
        unreachable_columns.append(
            sum(expected_unreachable[(v, u)] for v in range(N) if v != u)
        )

    return {
        "status": "CALIBRATION_PASS",
        "template": name,
        "solver": solver_name,
        "derived_indicators_checked": (
            len(builder.path_vars)
            + len(builder.reach2_vars)
            + len(builder.unreachable_vars)
        ),
        "mismatches": 0,
        "counts": builder.counts,
        "second_sizes": second_sizes,
        "unreachable_rows": unreachable_rows,
        "unreachable_columns": unreachable_columns,
    }


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def build_manifest(builder: Cycle19CNF, dimacs: bytes) -> dict[str, object]:
    variable_map = builder.variable_map()
    variable_map_bytes = json.dumps(
        variable_map, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    generator_bytes = Path(__file__).read_bytes()
    return {
        "schema": SCHEMA,
        "n": N,
        "missing_edges": [list(edge) for edge in normalized_missing_edges()],
        "edge_variable_semantics": (
            "edge(a,b), a<b, is true iff the arc is a->b; false iff b->a"
        ),
        "cardinality_encoding": CARDINALITY_ENCODING_NAME,
        "constraints": {
            "outdegree": 8,
            "source_unreachable": 3,
            "target_unreachable": 3,
            "symmetry_unit": "0->2",
            "path_biconditional": True,
            "reach2_biconditional": True,
            "unreachable_biconditional": True,
            "root_triangle_constraints": False,
        },
        "counts": builder.counts,
        "hashes": {
            "dimacs_sha256": sha256(dimacs),
            "variable_map_sha256": sha256(variable_map_bytes),
            "generator_sha256": sha256(generator_bytes),
        },
        "auxiliary_ranges": [
            {"scope": item.scope, "first": item.first, "last": item.last}
            for item in builder.aux_ranges
        ],
        "variable_map": variable_map,
    }


def write_instance(output: Path, manifest_path: Path | None = None) -> dict[str, object]:
    builder = Cycle19CNF(enforce_unreachable_equalities=True)
    dimacs = builder.dimacs_bytes()
    manifest = build_manifest(builder, dimacs)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(dimacs)
    if manifest_path is None:
        manifest_path = output.with_suffix(output.suffix + ".manifest.json")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate", help="write DIMACS and manifest")
    generate_parser.add_argument("--output", type=Path, required=True)
    generate_parser.add_argument("--manifest", type=Path)

    calibration_parser = subparsers.add_parser(
        "calibrate", help="pin and independently audit regular orientations"
    )
    calibration_parser.add_argument(
        "--template",
        choices=("circulant-even", "triangle-switch", "all"),
        default="all",
    )
    calibration_parser.add_argument("--solver", default="cadical195")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "generate":
        manifest = write_instance(args.output, args.manifest)
        print(
            json.dumps(
                {
                    "status": "GENERATED",
                    "output": str(args.output),
                    "manifest": str(
                        args.manifest
                        if args.manifest is not None
                        else args.output.with_suffix(args.output.suffix + ".manifest.json")
                    ),
                    "counts": manifest["counts"],
                    "hashes": manifest["hashes"],
                },
                sort_keys=True,
            )
        )
        return

    templates = (
        ("circulant-even", "triangle-switch")
        if args.template == "all"
        else (args.template,)
    )
    for template in templates:
        print(json.dumps(calibrate(template, solver_name=args.solver), sort_keys=True))


if __name__ == "__main__":
    main()
