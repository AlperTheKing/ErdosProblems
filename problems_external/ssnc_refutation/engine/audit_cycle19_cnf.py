#!/usr/bin/env python3
"""Independent semantic auditor for the fixed K_19-C_19 SAT instance.

This module deliberately defines the graph semantics without importing the
CNF generator.  The generator-facing adapter is kept separate from the
matrix/set oracles so that a generator defect cannot silently redefine the
property being audited.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from pysat.card import CardEnc, EncType
from pysat.formula import CNF
from pysat.solvers import Solver


N = 19


class AuditError(ValueError):
    """Raised when an artifact violates the frozen audit contract."""


def is_cycle_missing_pair(a: int, b: int, n: int = N) -> bool:
    return a != b and ((a - b) % n in (1, n - 1))


def present_edges(n: int = N) -> list[tuple[int, int]]:
    return [
        (a, b)
        for a in range(n)
        for b in range(a + 1, n)
        if not is_cycle_missing_pair(a, b, n)
    ]


def orientation_from_bits(bits: Sequence[int], n: int = N) -> list[list[int]]:
    edges = present_edges(n)
    if len(bits) != len(edges):
        raise AuditError(f"expected {len(edges)} orientation bits, got {len(bits)}")
    adjacency = [[0] * n for _ in range(n)]
    for bit, (a, b) in zip(bits, edges, strict=True):
        if bit not in (0, 1, False, True):
            raise AuditError("orientation bits must be Boolean")
        tail, head = (a, b) if int(bit) else (b, a)
        adjacency[tail][head] = 1
    return adjacency


def adjacency_from_arcs(arcs: Iterable[tuple[int, int]], n: int = N) -> list[list[int]]:
    adjacency = [[0] * n for _ in range(n)]
    for tail, head in arcs:
        if not (0 <= tail < n and 0 <= head < n):
            raise AuditError(f"arc outside vertex range: {(tail, head)}")
        adjacency[tail][head] = 1
    return adjacency


def validate_fixed_support(adjacency: Sequence[Sequence[int]], n: int = N) -> None:
    if len(adjacency) != n or any(len(row) != n for row in adjacency):
        raise AuditError(f"adjacency must be {n} by {n}")
    for a in range(n):
        if adjacency[a][a] != 0:
            raise AuditError(f"loop at {a}")
        for b in range(a + 1, n):
            pair_sum = int(bool(adjacency[a][b])) + int(bool(adjacency[b][a]))
            expected = 0 if is_cycle_missing_pair(a, b, n) else 1
            if pair_sum != expected:
                kind = "missing cycle edge" if expected == 0 else "present edge"
                raise AuditError(f"bad {kind} orientation on {(a, b)}: sum={pair_sum}")


@dataclass(frozen=True)
class Ledger:
    out_neighbors: tuple[tuple[int, ...], ...]
    second_neighbors: tuple[tuple[int, ...], ...]
    unreachable: tuple[tuple[int, ...], ...]
    reach2: tuple[tuple[bool, ...], ...]
    p: tuple[tuple[tuple[bool, ...], ...], ...]

    @property
    def out_degrees(self) -> tuple[int, ...]:
        return tuple(map(len, self.out_neighbors))

    @property
    def second_degrees(self) -> tuple[int, ...]:
        return tuple(map(len, self.second_neighbors))

    @property
    def unreachable_row_sums(self) -> tuple[int, ...]:
        return tuple(map(len, self.unreachable))

    @property
    def unreachable_column_sums(self) -> tuple[int, ...]:
        n = len(self.unreachable)
        return tuple(sum(target in self.unreachable[source] for source in range(n)) for target in range(n))


def triple_loop_oracle(adjacency: Sequence[Sequence[int]]) -> Ledger:
    """Literal matrix/triple-loop semantics, with no graph-library shortcuts."""
    n = len(adjacency)
    if any(len(row) != n for row in adjacency):
        raise AuditError("adjacency must be square")
    out = tuple(tuple(w for w in range(n) if adjacency[v][w]) for v in range(n))
    p_mut = [[[False] * n for _ in range(n)] for _ in range(n)]
    reach_mut = [[False] * n for _ in range(n)]
    for v in range(n):
        for u in range(n):
            for w in range(n):
                value = bool(adjacency[v][u] and adjacency[u][w])
                p_mut[v][u][w] = value
                reach_mut[v][w] = reach_mut[v][w] or value
    second: list[tuple[int, ...]] = []
    unreachable: list[tuple[int, ...]] = []
    for v in range(n):
        second.append(
            tuple(
                w
                for w in range(n)
                if w != v and not adjacency[v][w] and reach_mut[v][w]
            )
        )
        unreachable.append(
            tuple(
                w
                for w in range(n)
                if w != v and not adjacency[v][w] and not reach_mut[v][w]
            )
        )
    return Ledger(
        out_neighbors=out,
        second_neighbors=tuple(second),
        unreachable=tuple(unreachable),
        reach2=tuple(tuple(row) for row in reach_mut),
        p=tuple(tuple(tuple(row) for row in plane) for plane in p_mut),
    )


def set_oracle(adjacency: Sequence[Sequence[int]]) -> tuple[tuple[frozenset[int], ...], ...]:
    """Independent set-composition implementation used to cross-check the matrix oracle."""
    n = len(adjacency)
    out = tuple(frozenset(w for w in range(n) if adjacency[v][w]) for v in range(n))
    second = []
    unreachable = []
    universe = frozenset(range(n))
    for v in range(n):
        two_step = frozenset(w for u in out[v] for w in out[u])
        eligible = universe - frozenset((v,)) - out[v]
        second.append(two_step & eligible)
        unreachable.append(eligible - two_step)
    return out, tuple(second), tuple(unreachable)


def target_predicate(ledger: Ledger) -> bool:
    return (
        ledger.out_degrees == (8,) * N
        and ledger.unreachable_row_sums == (3,) * N
        and ledger.unreachable_column_sums == (3,) * N
    )


def strict_ssnc_failure(ledger: Ledger) -> bool:
    return all(second < out for second, out in zip(ledger.second_degrees, ledger.out_degrees, strict=True))


def reflect_swap_0_2(adjacency: Sequence[Sequence[int]]) -> list[list[int]]:
    """Relabel old vertex i as 2-i mod 19; this swaps vertices 0 and 2."""
    n = len(adjacency)
    image = [(2 - i) % n for i in range(n)]
    relabelled = [[0] * n for _ in range(n)]
    for old_tail in range(n):
        for old_head in range(n):
            relabelled[image[old_tail]][image[old_head]] = int(bool(adjacency[old_tail][old_head]))
    return relabelled


def normalize_symmetry_0_to_2(adjacency: Sequence[Sequence[int]]) -> list[list[int]]:
    if adjacency[0][2]:
        return [list(map(int, row)) for row in adjacency]
    if not adjacency[2][0]:
        raise AuditError("the present pair {0,2} is not oriented")
    return reflect_swap_0_2(adjacency)


def lit_truth(literal: int, assignment: Mapping[int, bool]) -> bool:
    if literal == 0:
        raise AuditError("zero is a clause terminator, not a literal")
    variable = abs(literal)
    if variable not in assignment:
        raise AuditError(f"unassigned variable {variable}")
    value = bool(assignment[variable])
    return value if literal > 0 else not value


def clause_truth(clause: Sequence[int], assignment: Mapping[int, bool]) -> bool:
    return any(lit_truth(literal, assignment) for literal in clause)


@dataclass(frozen=True)
class Dimacs:
    variables: int
    clauses: tuple[tuple[int, ...], ...]
    comments: tuple[str, ...]


def parse_dimacs_text(text: str) -> Dimacs:
    """Strict parser supporting clauses split over lines, including an empty clause."""
    header: tuple[int, int] | None = None
    comments: list[str] = []
    clauses: list[tuple[int, ...]] = []
    current: list[int] = []
    for line_number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("c"):
            if current:
                raise AuditError(f"comment interrupts clause at line {line_number}")
            comments.append(stripped[1:].strip())
            continue
        fields = stripped.split()
        if fields[0] == "p":
            if current or clauses or header is not None or len(fields) != 4 or fields[1] != "cnf":
                raise AuditError(f"invalid or misplaced DIMACS header at line {line_number}")
            try:
                variables, declared_clauses = int(fields[2]), int(fields[3])
            except ValueError as exc:
                raise AuditError(f"noninteger DIMACS header at line {line_number}") from exc
            if variables < 0 or declared_clauses < 0:
                raise AuditError("negative DIMACS count")
            header = variables, declared_clauses
            continue
        if header is None:
            raise AuditError(f"clause before DIMACS header at line {line_number}")
        for field in fields:
            try:
                literal = int(field)
            except ValueError as exc:
                raise AuditError(f"noninteger token at line {line_number}: {field!r}") from exc
            if literal == 0:
                clauses.append(tuple(current))
                current = []
            else:
                if abs(literal) > header[0]:
                    raise AuditError(f"literal {literal} exceeds declared variable count")
                current.append(literal)
    if header is None:
        raise AuditError("missing DIMACS header")
    if current:
        raise AuditError("unterminated final clause")
    if len(clauses) != header[1]:
        raise AuditError(f"declared {header[1]} clauses but parsed {len(clauses)}")
    return Dimacs(header[0], tuple(clauses), tuple(comments))


def parse_dimacs(path: Path) -> Dimacs:
    return parse_dimacs_text(path.read_text(encoding="ascii"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def randomized_oracle_audit(samples: int, seed: int) -> dict[str, int | str]:
    rng = random.Random(seed)
    edges = present_edges()
    for sample in range(samples):
        adjacency = orientation_from_bits([rng.randrange(2) for _ in edges])
        validate_fixed_support(adjacency)
        ledger = triple_loop_oracle(adjacency)
        set_out, set_second, set_unreachable = set_oracle(adjacency)
        if tuple(map(frozenset, ledger.out_neighbors)) != set_out:
            raise AuditError(f"out-neighbor oracle disagreement at sample {sample}")
        if tuple(map(frozenset, ledger.second_neighbors)) != set_second:
            raise AuditError(f"second-neighbor oracle disagreement at sample {sample}")
        if tuple(map(frozenset, ledger.unreachable)) != set_unreachable:
            raise AuditError(f"unreachable oracle disagreement at sample {sample}")
        for v in range(N):
            eligible = N - 1 - ledger.out_degrees[v]
            if ledger.second_degrees[v] + ledger.unreachable_row_sums[v] != eligible:
                raise AuditError(f"partition identity failed at sample {sample}, vertex {v}")
        normalized = normalize_symmetry_0_to_2(adjacency)
        validate_fixed_support(normalized)
        if not normalized[0][2]:
            raise AuditError(f"symmetry normalization failed at sample {sample}")
        before = ledger
        after = triple_loop_oracle(normalized)
        if sorted(before.out_degrees) != sorted(after.out_degrees):
            raise AuditError(f"symmetry changed outdegree multiset at sample {sample}")
        if sorted(before.second_degrees) != sorted(after.second_degrees):
            raise AuditError(f"symmetry changed second-degree multiset at sample {sample}")
        if sorted(before.unreachable_row_sums) != sorted(after.unreachable_row_sums):
            raise AuditError(f"symmetry changed unreachable multiset at sample {sample}")
    return {"samples": samples, "seed": seed, "status": "ORACLE_AUDIT_OK"}


FROZEN_PREINSPECTION_ORACLE_SHA256 = (
    "FD7A593B13A08B2ADE164E5D10B86DA8203998DDD90AADB2769AB7757549F503"
)
FROZEN_PREINSPECTION_TEST_SHA256 = (
    "843A1204ADACB5842E39139C9EDB50F07CCA367184B15CD6109103149BAECC4D"
)


def load_json_strict(path: Path) -> dict[str, object]:
    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise AuditError(f"duplicate JSON key {key!r}")
            result[key] = value
        return result

    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates)
    if not isinstance(value, dict):
        raise AuditError("manifest top level must be an object")
    return value


def canonical_variable_map_hash(variable_map: Mapping[str, str]) -> str:
    payload = json.dumps(
        dict(variable_map), sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def _first_formula_difference(
    actual: Sequence[Sequence[int]], expected: Sequence[Sequence[int]]
) -> str:
    common = min(len(actual), len(expected))
    for index in range(common):
        if tuple(actual[index]) != tuple(expected[index]):
            return f"clause {index}: actual={tuple(actual[index])}, expected={tuple(expected[index])}"
    if len(actual) != len(expected):
        return f"clause count actual={len(actual)}, expected={len(expected)}"
    return "none"


def _assert_formula_exact(
    actual: Sequence[Sequence[int]], expected: Sequence[Sequence[int]], label: str
) -> None:
    difference = _first_formula_difference(actual, expected)
    if difference != "none":
        raise AuditError(f"{label} mismatch: {difference}")


def _parse_variable_map(
    manifest: Mapping[str, object], dimacs: Dimacs
) -> tuple[
    dict[tuple[int, int], int],
    dict[tuple[int, int, int], int],
    dict[tuple[int, int], int],
    dict[tuple[int, int], int],
    dict[int, str],
]:
    raw_map = manifest.get("variable_map")
    _expect(isinstance(raw_map, dict), "manifest variable_map must be an object")
    variable_map = {str(key): value for key, value in raw_map.items()}
    _expect(
        all(isinstance(value, str) for value in variable_map.values()),
        "every variable-map value must be a string",
    )
    expected_keys = {str(index) for index in range(1, dimacs.variables + 1)}
    _expect(set(variable_map) == expected_keys, "variable-map IDs are not exactly 1..nvars")
    by_id = {index: variable_map[str(index)] for index in range(1, dimacs.variables + 1)}
    _expect(len(set(by_id.values())) == len(by_id), "variable-map names are not unique")

    edges: dict[tuple[int, int], int] = {}
    paths: dict[tuple[int, int, int], int] = {}
    reach: dict[tuple[int, int], int] = {}
    unreachable: dict[tuple[int, int], int] = {}
    semantic_ids: set[int] = set()
    for variable, name in by_id.items():
        match = re.fullmatch(r"edge\((\d+),(\d+)\)", name)
        if match:
            edges[tuple(map(int, match.groups()))] = variable
            semantic_ids.add(variable)
            continue
        match = re.fullmatch(r"path\((\d+),(\d+),(\d+)\)", name)
        if match:
            paths[tuple(map(int, match.groups()))] = variable
            semantic_ids.add(variable)
            continue
        match = re.fullmatch(r"reach2\((\d+),(\d+)\)", name)
        if match:
            reach[tuple(map(int, match.groups()))] = variable
            semantic_ids.add(variable)
            continue
        match = re.fullmatch(r"unreachable\((\d+),(\d+)\)", name)
        if match:
            unreachable[tuple(map(int, match.groups()))] = variable
            semantic_ids.add(variable)
            continue
        _expect(name.startswith("aux:"), f"unknown variable-map name {name!r}")

    expected_edges = set(present_edges())
    expected_paths = {
        (v, w, u)
        for v in range(N)
        for w in range(N)
        for u in range(N)
        if u != v
        and v != w
        and w != u
        and not is_cycle_missing_pair(v, w)
        and not is_cycle_missing_pair(w, u)
    }
    expected_pairs = {(v, u) for v in range(N) for u in range(N) if v != u}
    _expect(set(edges) == expected_edges, "edge variable domain differs from K19-C19")
    _expect(set(paths) == expected_paths, "path variable domain is not the nonconstant off-diagonal domain")
    _expect(set(reach) == expected_pairs, "reach2 variable domain is not all off-diagonal pairs")
    _expect(set(unreachable) == expected_pairs, "unreachable variable domain is not all off-diagonal pairs")
    expected_semantic = len(edges) + len(paths) + len(reach) + len(unreachable)
    _expect(len(semantic_ids) == expected_semantic, "semantic variable IDs overlap")
    counts = manifest.get("counts")
    _expect(isinstance(counts, dict), "manifest counts missing")
    expected_counts = {
        "orientation": len(edges),
        "path": len(paths),
        "reach2": len(reach),
        "unreachable": len(unreachable),
        "semantic": expected_semantic,
        "variables": dimacs.variables,
        "clauses": len(dimacs.clauses),
    }
    for key, value in expected_counts.items():
        _expect(counts.get(key) == value, f"manifest count {key} disagrees")
    _expect(
        semantic_ids == set(range(1, expected_semantic + 1)),
        "semantic IDs are not the initial contiguous range",
    )
    return edges, paths, reach, unreachable, by_id


def _arc_lit(edge_vars: Mapping[tuple[int, int], int], v: int, w: int) -> int:
    if v == w or is_cycle_missing_pair(v, w):
        raise AuditError(f"arc literal requested for structural false pair {(v, w)}")
    a, b = sorted((v, w))
    variable = edge_vars[(a, b)]
    return variable if v == a else -variable


def _expected_definitions(
    edge_vars: Mapping[tuple[int, int], int],
    path_vars: Mapping[tuple[int, int, int], int],
    reach_vars: Mapping[tuple[int, int], int],
    unreachable_vars: Mapping[tuple[int, int], int],
) -> list[list[int]]:
    clauses: list[list[int]] = []
    for v in range(N):
        for w in range(N):
            for u in range(N):
                key = (v, w, u)
                if key not in path_vars:
                    continue
                path = path_vars[key]
                first = _arc_lit(edge_vars, v, w)
                second = _arc_lit(edge_vars, w, u)
                clauses.extend(([-path, first], [-path, second], [path, -first, -second]))
    for v in range(N):
        for u in range(N):
            if v == u:
                continue
            reach = reach_vars[(v, u)]
            inputs = [path_vars[(v, w, u)] for w in range(N) if (v, w, u) in path_vars]
            _expect(bool(inputs), f"empty off-diagonal reach gate {(v, u)}")
            clauses.extend([[-path, reach] for path in inputs])
            clauses.append([-reach, *inputs])
    for v in range(N):
        for u in range(N):
            if v == u:
                continue
            unreachable = unreachable_vars[(v, u)]
            reach = reach_vars[(v, u)]
            if is_cycle_missing_pair(v, u):
                clauses.extend(([-unreachable, -reach], [unreachable, reach]))
            else:
                direct = _arc_lit(edge_vars, v, u)
                clauses.extend(
                    (
                        [-unreachable, -direct],
                        [-unreachable, -reach],
                        [unreachable, direct, reach],
                    )
                )
    return clauses


def _expected_cardinality_blocks(
    manifest: Mapping[str, object],
    by_id: Mapping[int, str],
    edge_vars: Mapping[tuple[int, int], int],
    unreachable_vars: Mapping[tuple[int, int], int],
) -> list[dict[str, object]]:
    expected_scopes: list[tuple[str, list[int], int]] = []
    for v in range(N):
        expected_scopes.append(
            (
                f"outdegree({v})=8",
                [
                    _arc_lit(edge_vars, v, w)
                    for w in range(N)
                    if v != w and not is_cycle_missing_pair(v, w)
                ],
                8,
            )
        )
    for v in range(N):
        expected_scopes.append(
            (
                f"source-unreachable({v})=3",
                [unreachable_vars[(v, u)] for u in range(N) if u != v],
                3,
            )
        )
    for u in range(N):
        expected_scopes.append(
            (
                f"target-roots({u})=3",
                [unreachable_vars[(v, u)] for v in range(N) if v != u],
                3,
            )
        )

    raw_ranges = manifest.get("auxiliary_ranges")
    _expect(isinstance(raw_ranges, list), "auxiliary_ranges must be a list")
    _expect(len(raw_ranges) == len(expected_scopes), "expected exactly 57 cardinality scopes")
    blocks: list[dict[str, object]] = []
    counts = manifest["counts"]
    _expect(isinstance(counts, dict), "manifest counts missing")
    previous_last = int(counts["semantic"])
    for raw_range, (scope, literals, bound) in zip(raw_ranges, expected_scopes, strict=True):
        _expect(isinstance(raw_range, dict), "auxiliary range entry must be an object")
        first = int(raw_range.get("first", -1))
        last = int(raw_range.get("last", -1))
        _expect(raw_range.get("scope") == scope, f"cardinality scope mismatch for {scope}")
        _expect(first == previous_last + 1 and last >= first, f"noncontiguous auxiliary range for {scope}")
        encoded = CardEnc.equals(
            lits=literals, bound=bound, top_id=first - 1, encoding=EncType.seqcounter
        )
        _expect(encoded.nv == last, f"auxiliary high ID mismatch for {scope}")
        used_aux = {
            abs(literal)
            for clause in encoded.clauses
            for literal in clause
            if abs(literal) >= first
        }
        _expect(
            used_aux == set(range(first, last + 1)),
            f"unused or out-of-range auxiliaries in {scope}",
        )
        for offset, variable in enumerate(range(first, last + 1), start=1):
            _expect(
                by_id[variable] == f"aux:{scope}:{offset}",
                f"auxiliary map mismatch at {variable}",
            )
        blocks.append(
            {
                "scope": scope,
                "literals": literals,
                "bound": bound,
                "first": first,
                "last": last,
                "clauses": [list(clause) for clause in encoded.clauses],
            }
        )
        previous_last = last
    _expect(
        previous_last == int(counts["variables"]),
        "auxiliary ranges do not cover all variables",
    )
    return blocks


def _orientation_assumptions(
    adjacency: Sequence[Sequence[int]], edge_vars: Mapping[tuple[int, int], int]
) -> list[int]:
    return [
        variable if adjacency[a][b] else -variable
        for (a, b), variable in sorted(edge_vars.items())
    ]


def _definition_calibration(
    definition_clauses: Sequence[Sequence[int]],
    edge_vars: Mapping[tuple[int, int], int],
    path_vars: Mapping[tuple[int, int, int], int],
    reach_vars: Mapping[tuple[int, int], int],
    unreachable_vars: Mapping[tuple[int, int], int],
    samples: int,
    seed: int,
    solver_name: str,
) -> dict[str, int]:
    rng = random.Random(seed)
    comparisons = 0
    forced_opposites = 0
    semantic_groups = (list(path_vars.items()), list(reach_vars.items()), list(unreachable_vars.items()))
    with Solver(name=solver_name, bootstrap_with=definition_clauses) as solver:
        for sample in range(samples):
            adjacency = orientation_from_bits([rng.randrange(2) for _ in present_edges()])
            ledger = triple_loop_oracle(adjacency)
            pins = _orientation_assumptions(adjacency, edge_vars)
            _expect(solver.solve(assumptions=pins), f"definition-only formula rejected sample {sample}")
            model = {literal for literal in solver.get_model() if literal > 0}
            expected_values: list[tuple[int, bool]] = []
            for key, variable in path_vars.items():
                expected_values.append((variable, ledger.p[key[0]][key[1]][key[2]]))
            for key, variable in reach_vars.items():
                expected_values.append((variable, ledger.reach2[key[0]][key[1]]))
            unreachable_sets = tuple(set(row) for row in ledger.unreachable)
            for key, variable in unreachable_vars.items():
                expected_values.append((variable, key[1] in unreachable_sets[key[0]]))
            for variable, expected in expected_values:
                _expect((variable in model) == expected, f"definition model mismatch at variable {variable}")
            comparisons += len(expected_values)
            for group_index, group in enumerate(semantic_groups):
                for offset in (0, len(group) // 2, len(group) - 1):
                    key, variable = group[(sample + offset + group_index) % len(group)]
                    if len(key) == 3:
                        expected = ledger.p[key[0]][key[1]][key[2]]
                    elif group_index == 1:
                        expected = ledger.reach2[key[0]][key[1]]
                    else:
                        expected = key[1] in unreachable_sets[key[0]]
                    opposite = -variable if expected else variable
                    _expect(
                        not solver.solve(assumptions=[*pins, opposite]),
                        f"semantic variable {variable} was not uniquely forced",
                    )
                    forced_opposites += 1
    return {"samples": samples, "indicator_comparisons": comparisons, "forced_opposites": forced_opposites}


def _cardinality_calibration(
    blocks: Sequence[Mapping[str, object]],
    unreachable_vars: Mapping[tuple[int, int], int],
    solver_name: str,
) -> dict[str, object]:
    degree_boundary_checks = 0
    for block in blocks[:N]:
        literals = list(block["literals"])
        clauses = list(block["clauses"])
        for true_count in (7, 8, 9):
            assumptions = []
            for index, literal in enumerate(literals):
                desired_literal_truth = index < true_count
                variable_truth = desired_literal_truth if literal > 0 else not desired_literal_truth
                assumptions.append(abs(literal) if variable_truth else -abs(literal))
            with Solver(name=solver_name, bootstrap_with=clauses) as solver:
                actual = solver.solve(assumptions=assumptions)
            _expect(actual == (true_count == 8), f"signed degree cardinality failure in {block['scope']}")
            degree_boundary_checks += 1

    row_clauses = [clause for block in blocks[N : 2 * N] for clause in block["clauses"]]
    column_clauses = [clause for block in blocks[2 * N :] for clause in block["clauses"]]

    cyclic = [{(v + 1) % N, (v + 2) % N, (v + 3) % N} for v in range(N)]
    skew = [set(row) for row in cyclic]
    skew[0].remove(3)
    skew[0].add(4)
    transpose = [{v for v in range(N) if u in skew[v]} for u in range(N)]

    fixtures = (
        ("cyclic", cyclic, True, True),
        ("row-only", skew, True, False),
        ("column-only", transpose, False, True),
    )
    fixture_results: dict[str, dict[str, bool]] = {}
    for name, supports, expected_rows, expected_columns in fixtures:
        pins = [
            variable if u in supports[v] else -variable
            for (v, u), variable in sorted(unreachable_vars.items())
        ]
        with Solver(name=solver_name, bootstrap_with=row_clauses) as solver:
            rows_sat = solver.solve(assumptions=pins)
        with Solver(name=solver_name, bootstrap_with=column_clauses) as solver:
            columns_sat = solver.solve(assumptions=pins)
        _expect(rows_sat == expected_rows, f"row ledger fixture failed: {name}")
        _expect(columns_sat == expected_columns, f"column ledger fixture failed: {name}")
        fixture_results[name] = {"rows": rows_sat, "columns": columns_sat}
    return {"degree_boundary_checks": degree_boundary_checks, "ledger_fixtures": fixture_results}


def _circulant_orientation(mask: int) -> list[list[int]]:
    inverse_pairs = [(step, N - step) for step in range(2, 10)]
    steps = {pair[(mask >> index) & 1] for index, pair in enumerate(inverse_pairs)}
    return adjacency_from_arcs((v, (v + step) % N) for v in range(N) for step in steps)


def _full_pinned_calibration(
    clauses: Sequence[Sequence[int]],
    edge_vars: Mapping[tuple[int, int], int],
    random_samples: int,
    seed: int,
    solver_name: str,
) -> dict[str, int]:
    orientations = [normalize_symmetry_0_to_2(_circulant_orientation(mask)) for mask in range(256)]
    rng = random.Random(seed)
    orientations.extend(
        normalize_symmetry_0_to_2(
            orientation_from_bits([rng.randrange(2) for _ in present_edges()])
        )
        for _ in range(random_samples)
    )
    expected_sat = 0
    actual_sat = 0
    with Solver(name=solver_name, bootstrap_with=clauses) as solver:
        for index, adjacency in enumerate(orientations):
            validate_fixed_support(adjacency)
            ledger = triple_loop_oracle(adjacency)
            expected = bool(adjacency[0][2] and target_predicate(ledger))
            actual = solver.solve(assumptions=_orientation_assumptions(adjacency, edge_vars))
            _expect(actual == expected, f"full pinned raw CNF/oracle disagreement at orientation {index}")
            expected_sat += int(expected)
            actual_sat += int(actual)
    return {
        "circulant_templates": 256,
        "random_orientations": random_samples,
        "expected_sat": expected_sat,
        "actual_sat": actual_sat,
    }


def _mutation_rejection_audit(
    expected: Sequence[Sequence[int]],
    definition_count: int,
    blocks: Sequence[Mapping[str, object]],
) -> int:
    mutations: list[list[list[int]]] = []
    dropped_path_reverse = [list(clause) for clause in expected]
    del dropped_path_reverse[2]
    mutations.append(dropped_path_reverse)

    flipped_signed_input = [list(clause) for clause in expected]
    flipped_signed_input[0][1] *= -1
    mutations.append(flipped_signed_input)

    dropped_reach_reverse = [list(clause) for clause in expected]
    reach_reverse = next(
        index for index, clause in enumerate(dropped_reach_reverse) if index >= 3 * 4560 and len(clause) > 3
    )
    del dropped_reach_reverse[reach_reverse]
    mutations.append(dropped_reach_reverse)

    weakened_z = [list(clause) for clause in expected]
    weakened_z[definition_count - 1][0] *= -1
    mutations.append(weakened_z)

    duplicated_row_axis = [list(clause) for clause in expected]
    block_start = definition_count + sum(len(block["clauses"]) for block in blocks[: 2 * N])
    column_length = len(blocks[2 * N]["clauses"])
    row_source = [list(clause) for clause in blocks[N]["clauses"]]
    duplicated_row_axis[block_start : block_start + column_length] = row_source
    mutations.append(duplicated_row_axis)

    extra_symmetry = [list(clause) for clause in expected]
    extra_symmetry.append([-2])
    mutations.append(extra_symmetry)

    caught = 0
    for index, mutation in enumerate(mutations):
        try:
            _assert_formula_exact(mutation, expected, f"mutation-{index}")
        except AuditError:
            caught += 1
    _expect(caught == len(mutations), "formula comparator failed to reject a mutation")
    return caught


def audit_raw_artifacts(
    cnf_path: Path,
    manifest_path: Path,
    generator_path: Path,
    *,
    solver_name: str = "cadical195",
    definition_samples: int = 32,
    full_random_samples: int = 32,
) -> dict[str, object]:
    dimacs = parse_dimacs(cnf_path)
    manifest = load_json_strict(manifest_path)
    _expect(manifest.get("schema") == "ssnc-fixed-cycle19-cnf-v1", "wrong manifest schema")
    _expect(manifest.get("n") == N, "wrong manifest order")
    expected_missing = [list(edge) for edge in sorted({tuple(sorted((v, (v + 1) % N))) for v in range(N)})]
    _expect(manifest.get("missing_edges") == expected_missing, "missing cycle list is wrong")
    expected_constraints = {
        "outdegree": 8,
        "source_unreachable": 3,
        "target_unreachable": 3,
        "symmetry_unit": "0->2",
        "path_biconditional": True,
        "reach2_biconditional": True,
        "unreachable_biconditional": True,
        "root_triangle_constraints": False,
    }
    _expect(manifest.get("constraints") == expected_constraints, "manifest constraint contract differs")
    hashes = manifest.get("hashes")
    _expect(isinstance(hashes, dict), "manifest hashes missing")
    _expect(hashes.get("dimacs_sha256") == sha256(cnf_path), "DIMACS hash mismatch")
    _expect(hashes.get("generator_sha256") == sha256(generator_path), "generator hash mismatch")
    raw_map = manifest.get("variable_map")
    _expect(isinstance(raw_map, dict), "manifest variable map missing")
    _expect(
        hashes.get("variable_map_sha256") == canonical_variable_map_hash(raw_map),
        "variable-map hash mismatch",
    )

    edge_vars, path_vars, reach_vars, unreachable_vars, by_id = _parse_variable_map(manifest, dimacs)
    definitions = _expected_definitions(edge_vars, path_vars, reach_vars, unreachable_vars)
    blocks = _expected_cardinality_blocks(manifest, by_id, edge_vars, unreachable_vars)
    symmetry = [_arc_lit(edge_vars, 0, 2)]
    expected_formula = [
        *definitions,
        *(clause for block in blocks for clause in block["clauses"]),
        symmetry,
    ]
    _assert_formula_exact(dimacs.clauses, expected_formula, "raw DIMACS reconstruction")

    parsed_by_pysat = CNF(from_file=str(cnf_path))
    _assert_formula_exact(parsed_by_pysat.clauses, dimacs.clauses, "independent parser")
    _expect(parsed_by_pysat.nv == dimacs.variables, "independent parser variable count mismatch")
    used_variables = {abs(literal) for clause in dimacs.clauses for literal in clause}
    _expect(used_variables == set(range(1, dimacs.variables + 1)), "some mapped variables are unused")
    _expect(
        not any(any(-literal in clause for literal in clause) for clause in dimacs.clauses),
        "DIMACS contains a tautological clause",
    )
    _expect(
        not any(len(set(clause)) != len(clause) for clause in dimacs.clauses),
        "DIMACS contains a repeated literal",
    )
    unit_clauses = [clause for clause in dimacs.clauses if len(clause) == 1]
    _expect(unit_clauses == [(symmetry[0],)], f"unexpected unit clauses: {unit_clauses[:10]}")

    definition_result = _definition_calibration(
        definitions,
        edge_vars,
        path_vars,
        reach_vars,
        unreachable_vars,
        definition_samples,
        1945603,
        solver_name,
    )
    cardinality_result = _cardinality_calibration(blocks, unreachable_vars, solver_name)
    pinned_result = _full_pinned_calibration(
        dimacs.clauses,
        edge_vars,
        full_random_samples,
        1900321,
        solver_name,
    )
    mutation_rejections = _mutation_rejection_audit(expected_formula, len(definitions), blocks)

    return {
        "status": "RAW_ARTIFACT_AUDIT_PASS",
        "scope": "fixed-K19-minus-C19-only",
        "hashes": {
            "cnf": sha256(cnf_path),
            "manifest": sha256(manifest_path),
            "generator": sha256(generator_path),
            "frozen_preinspection_oracle": FROZEN_PREINSPECTION_ORACLE_SHA256,
            "frozen_preinspection_tests": FROZEN_PREINSPECTION_TEST_SHA256,
        },
        "counts": {
            "variables": dimacs.variables,
            "clauses": len(dimacs.clauses),
            "semantic_definition_clauses": len(definitions),
            "cardinality_blocks": len(blocks),
            "cardinality_clauses": sum(len(block["clauses"]) for block in blocks),
            "unit_clauses": len(unit_clauses),
        },
        "definition_calibration": definition_result,
        "cardinality_calibration": cardinality_result,
        "full_pinned_calibration": pinned_result,
        "mutation_rejections": mutation_rejections,
        "independent_parser_agreement": True,
        "formula_byte_order_reconstruction": True,
        "unpinned_production_solve": False,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oracle-samples", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=19031996)
    parser.add_argument("--dimacs", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--generator", type=Path)
    parser.add_argument("--artifact-audit", action="store_true")
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--definition-samples", type=int, default=32)
    parser.add_argument("--full-random-samples", type=int, default=32)
    args = parser.parse_args(argv)
    result: dict[str, object] = randomized_oracle_audit(args.oracle_samples, args.seed)
    if args.dimacs is not None:
        dimacs = parse_dimacs(args.dimacs)
        result["dimacs"] = {
            "path": str(args.dimacs),
            "sha256": sha256(args.dimacs),
            "variables": dimacs.variables,
            "clauses": len(dimacs.clauses),
            "tautologies": sum(
                any(-literal in clause for literal in clause)
                for clause in dimacs.clauses
            ),
            "duplicate_literal_clauses": sum(
                len(set(clause)) != len(clause) for clause in dimacs.clauses
            ),
        }
    if args.artifact_audit:
        if args.dimacs is None or args.manifest is None or args.generator is None:
            parser.error("--artifact-audit requires --dimacs, --manifest, and --generator")
        result["artifact"] = audit_raw_artifacts(
            args.dimacs,
            args.manifest,
            args.generator,
            solver_name=args.solver,
            definition_samples=args.definition_samples,
            full_random_samples=args.full_random_samples,
        )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
