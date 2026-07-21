#!/usr/bin/env python3
"""Generate an independent exact CNF for the fixed irregular order-19 lift."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Iterable, Sequence


N = 19
ROOT_BLOCKS: tuple[tuple[int, ...], ...] = (
    (1, 13, 14, 15, 16, 17, 18),
    (0, 9, 12, 17, 18),
    (9, 10, 12, 16, 18),
    (6, 8, 10, 12, 16),
    (6, 8, 10, 11, 15),
    (6, 8, 9, 11, 15),
    (2, 3, 4, 5, 14),
    (2, 3, 4, 5, 11),
    (2, 3, 4, 5, 13),
    (13,),
    (7,),
    (7,),
    (7,),
    (14,),
    (1,),
    (1,),
    (17,),
    (0,),
    (0,),
)

SOURCE_UNREACHABLE: tuple[tuple[int, ...], ...] = (
    (1, 17, 18),
    (0, 14, 15),
    (6, 7, 8),
    (6, 7, 8),
    (6, 7, 8),
    (6, 7, 8),
    (3, 4, 5),
    (10, 11, 12),
    (3, 4, 5),
    (1, 2, 5),
    (2, 3, 4),
    (4, 5, 7),
    (1, 2, 3),
    (0, 8, 9),
    (0, 6, 13),
    (0, 4, 5),
    (0, 2, 3),
    (0, 1, 16),
    (0, 1, 2),
)


def canonical_json_sha256(value: object) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(data).hexdigest().upper()


def co_block_pairs() -> frozenset[tuple[int, int]]:
    return frozenset(
        (a, b)
        for block in ROOT_BLOCKS
        for a, b in itertools.combinations(block, 2)
    )


def reconstruct_canonical_missing_graph() -> tuple[
    frozenset[tuple[int, int]], dict[str, object]
]:
    """Lexicographically reconstruct the promised 9-cycle plus ten leaves.

    Missing pairs are forbidden inside every root block.  Rotation is fixed
    by starting the core cycle at zero, and reflection is quotiented by
    requiring the second vertex to be smaller than the last.
    """

    forbidden = co_block_pairs()

    def allowed(a: int, b: int) -> bool:
        return tuple(sorted((a, b))) not in forbidden

    compatible_cycles: list[tuple[int, ...]] = []
    for tail in itertools.permutations(range(1, 9)):
        cycle = (0,) + tail
        if cycle[1] > cycle[-1]:
            continue
        if all(allowed(cycle[i], cycle[(i + 1) % 9]) for i in range(9)):
            compatible_cycles.append(cycle)
    if not compatible_cycles:
        raise AssertionError("no compatible core 9-cycle")
    cycle = compatible_cycles[0]

    capacities = [2] + [1] * 8
    leaves = tuple(range(9, 19))
    leaf_parent: list[int] = []

    def assign_leaf(index: int) -> bool:
        if index == len(leaves):
            return True
        leaf = leaves[index]
        for parent in range(9):
            if capacities[parent] and allowed(leaf, parent):
                capacities[parent] -= 1
                leaf_parent.append(parent)
                if assign_leaf(index + 1):
                    return True
                leaf_parent.pop()
                capacities[parent] += 1
        return False

    if not assign_leaf(0):
        raise AssertionError("no compatible leaf assignment")

    cycle_edges = {
        tuple(sorted((cycle[i], cycle[(i + 1) % 9])))
        for i in range(9)
    }
    leaf_edges = {
        tuple(sorted((leaf, parent)))
        for leaf, parent in zip(leaves, leaf_parent, strict=True)
    }
    missing = frozenset(cycle_edges | leaf_edges)
    if len(missing) != 19:
        raise AssertionError("missing graph must have exactly 19 edges")

    metadata: dict[str, object] = {
        "compatible_core_cycles": len(compatible_cycles),
        "canonical_core_cycle": list(cycle),
        "canonical_leaf_parent_for_9_through_18": leaf_parent,
        "forbidden_co_block_pairs": len(forbidden),
    }
    return missing, metadata


def transpose_blocks(blocks: Sequence[Sequence[int]]) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(u for u, block in enumerate(blocks) if v in block)
        for v in range(N)
    )


class CNFBuilder:
    def __init__(self) -> None:
        self.names: dict[str, int] = {}
        self.variable_map: dict[int, str] = {}
        self.clauses: list[tuple[int, ...]] = []
        self.section_starts: dict[str, int] = {}
        self.section_ranges: dict[str, tuple[int, int]] = {}
        self.current_section: str | None = None

    def var(self, name: str) -> int:
        identifier = self.names.get(name)
        if identifier is None:
            identifier = len(self.names) + 1
            self.names[name] = identifier
            self.variable_map[identifier] = name
        return identifier

    def begin(self, section: str) -> None:
        if self.current_section is not None:
            raise AssertionError("a clause section is already open")
        self.current_section = section
        self.section_starts[section] = len(self.clauses) + 1

    def end(self) -> None:
        if self.current_section is None:
            raise AssertionError("no clause section is open")
        name = self.current_section
        self.section_ranges[name] = (self.section_starts[name], len(self.clauses))
        self.current_section = None

    def add(self, *literals: int) -> None:
        if self.current_section is None:
            raise AssertionError("clauses must belong to a named section")
        if not literals or any(type(literal) is not int or literal == 0 for literal in literals):
            raise ValueError("a CNF clause must contain nonzero integer literals")
        self.clauses.append(tuple(literals))


class FixedIncidenceLift:
    def __init__(self) -> None:
        self.builder = CNFBuilder()
        self.missing_edges, self.reconstruction = reconstruct_canonical_missing_graph()

        if transpose_blocks(ROOT_BLOCKS) != SOURCE_UNREACHABLE:
            raise AssertionError("listed W rows are not the transpose of listed root blocks")

        self.arc = [
            [self.builder.var(f"arc({v},{w})") for w in range(N)]
            for v in range(N)
        ]
        self.missing = {
            (a, b): self.builder.var(f"missing({a},{b})")
            for a in range(N)
            for b in range(a + 1, N)
        }
        self.path = [
            [
                [self.builder.var(f"path({v},{u},{w})") for w in range(N)]
                for u in range(N)
            ]
            for v in range(N)
        ]
        self.reach = [
            [self.builder.var(f"reach({v},{w})") for w in range(N)]
            for v in range(N)
        ]
        self.second = [
            [self.builder.var(f"second({v},{w})") for w in range(N)]
            for v in range(N)
        ]
        self.unreachable = [
            [self.builder.var(f"unreachable({v},{w})") for w in range(N)]
            for v in range(N)
        ]

    def _comparator(self, left: int, right: int, name: str) -> tuple[int, int]:
        """Return biconditional `(left OR right, left AND right)` wires."""

        high = self.builder.var(f"{name}.high")
        low = self.builder.var(f"{name}.low")
        self.builder.add(-left, high)
        self.builder.add(-right, high)
        self.builder.add(left, right, -high)
        self.builder.add(-low, left)
        self.builder.add(-low, right)
        self.builder.add(-left, -right, low)
        return high, low

    def _sort_descending(self, inputs: Sequence[int], name: str) -> list[int]:
        wires = list(inputs)
        counter = 0
        for outer in range(len(wires)):
            for index in range(len(wires) - 1 - outer):
                wires[index], wires[index + 1] = self._comparator(
                    wires[index], wires[index + 1], f"{name}.cmp{counter}"
                )
                counter += 1
        return wires

    def build(self) -> None:
        b = self.builder

        b.begin("loop_forbidden")
        for v in range(N):
            b.add(-self.arc[v][v])
        b.end()

        b.begin("pair_exactly_one_state")
        for (a, c), missing in self.missing.items():
            forward = self.arc[a][c]
            reverse = self.arc[c][a]
            b.add(forward, reverse, missing)
            b.add(-forward, -reverse)
            b.add(-forward, -missing)
            b.add(-reverse, -missing)
        b.end()

        b.begin("canonical_missing_graph_pins")
        for pair, variable in self.missing.items():
            b.add(variable if pair in self.missing_edges else -variable)
        b.end()

        b.begin("path_biconditional")
        for v in range(N):
            for u in range(N):
                for w in range(N):
                    path = self.path[v][u][w]
                    first = self.arc[v][u]
                    second = self.arc[u][w]
                    b.add(-path, first)
                    b.add(-path, second)
                    b.add(path, -first, -second)
        b.end()

        b.begin("reach_biconditional")
        for v in range(N):
            for w in range(N):
                reach = self.reach[v][w]
                witnesses = [self.path[v][u][w] for u in range(N)]
                for path in witnesses:
                    b.add(-path, reach)
                b.add(-reach, *witnesses)
        b.end()

        b.begin("second_biconditional")
        for v in range(N):
            for w in range(N):
                second = self.second[v][w]
                if v == w:
                    b.add(-second)
                else:
                    arc = self.arc[v][w]
                    reach = self.reach[v][w]
                    b.add(-second, -arc)
                    b.add(-second, reach)
                    b.add(second, arc, -reach)
        b.end()

        b.begin("unreachable_biconditional")
        for v in range(N):
            for w in range(N):
                unreachable = self.unreachable[v][w]
                if v == w:
                    b.add(-unreachable)
                else:
                    arc = self.arc[v][w]
                    reach = self.reach[v][w]
                    b.add(-unreachable, -arc)
                    b.add(-unreachable, -reach)
                    b.add(unreachable, arc, reach)
        b.end()

        b.begin("fixed_W_pins")
        for v in range(N):
            fixed = set(SOURCE_UNREACHABLE[v])
            for w in range(N):
                variable = self.unreachable[v][w]
                b.add(variable if w in fixed else -variable)
        b.end()

        b.begin("outdegree_exactly_8")
        for v in range(N):
            direct = [self.arc[v][w] for w in range(N) if w != v]
            sorted_direct = self._sort_descending(direct, f"outdegree({v})")
            b.add(sorted_direct[7])
            b.add(-sorted_direct[8])
        b.end()

        b.begin("strict_second_degree_at_most_7")
        for v in range(N):
            second = [self.second[v][w] for w in range(N) if w != v]
            sorted_second = self._sort_descending(second, f"second_degree({v})")
            b.add(-sorted_second[7])
        b.end()

        if b.current_section is not None:
            raise AssertionError("unterminated clause section")

    def manifest(self, cnf_sha256: str) -> dict[str, object]:
        degrees = [0] * N
        for a, c in self.missing_edges:
            degrees[a] += 1
            degrees[c] += 1
        return {
            "schema": "ssnc-irregular19-fixed-incidence-cnf-v1",
            "n": N,
            "arc_semantics": "arc(v,w) is true iff the directed arc v->w is present",
            "missing_semantics": "for a<b exactly one of arc(a,b), arc(b,a), missing(a,b) is true",
            "path_semantics": "path(v,u,w) iff arc(v,u) and arc(u,w)",
            "reach_semantics": "reach(v,w) iff some u has path(v,u,w)",
            "second_semantics": "off diagonal: second(v,w) iff not arc(v,w) and reach(v,w)",
            "unreachable_semantics": "off diagonal: unreachable(v,w) iff not arc(v,w) and not reach(v,w)",
            "missing_edges": [list(edge) for edge in sorted(self.missing_edges)],
            "missing_degrees": degrees,
            "root_blocks_by_target": [list(block) for block in ROOT_BLOCKS],
            "unreachable_targets_by_source": [list(row) for row in SOURCE_UNREACHABLE],
            "reconstruction": self.reconstruction,
            "counts": {
                "variables": len(self.builder.names),
                "clauses": len(self.builder.clauses),
                "semantic_variables_before_sorting": 8474,
                "missing_edges": len(self.missing_edges),
                "unreachable_pins_true": sum(map(len, SOURCE_UNREACHABLE)),
            },
            "clause_sections_1_based_inclusive": {
                name: list(bounds) for name, bounds in self.builder.section_ranges.items()
            },
            "variable_map": {
                str(identifier): name
                for identifier, name in self.builder.variable_map.items()
            },
            "hashes": {
                "cnf_sha256": cnf_sha256,
                "root_blocks_sha256": canonical_json_sha256(ROOT_BLOCKS),
                "source_W_sha256": canonical_json_sha256(SOURCE_UNREACHABLE),
                "missing_edges_sha256": canonical_json_sha256(sorted(self.missing_edges)),
            },
        }


def dimacs_text(builder: CNFBuilder) -> str:
    lines = [f"p cnf {len(builder.names)} {len(builder.clauses)}"]
    lines.extend(" ".join(map(str, clause)) + " 0" for clause in builder.clauses)
    return "\n".join(lines) + "\n"


def write_instance(output_dir: Path) -> dict[str, object]:
    model = FixedIncidenceLift()
    model.build()
    output_dir.mkdir(parents=True, exist_ok=True)
    cnf = dimacs_text(model.builder)
    cnf_sha256 = hashlib.sha256(cnf.encode("ascii")).hexdigest().upper()
    manifest = model.manifest(cnf_sha256)
    (output_dir / "irregular19.cnf").write_text(cnf, encoding="ascii", newline="\n")
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
        newline="\n",
    )
    return manifest


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    manifest = write_instance(args.output_dir)
    print(
        json.dumps(
            {
                "status": "GENERATED_UNSOLVED",
                "output_dir": str(args.output_dir),
                "counts": manifest["counts"],
                "hashes": manifest["hashes"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
