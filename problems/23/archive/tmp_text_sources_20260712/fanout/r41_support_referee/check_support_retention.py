"""Exact finite audit of the R41 support-retention implication."""

from __future__ import annotations

import itertools
import json


M, X, A = range(3)
EDGE = (M, X)


def contains(row: tuple[int, ...], u: int, v: int) -> bool:
    return u in row and v in row


def row_edges(row: tuple[int, ...]) -> set[tuple[int, int]]:
    return {
        tuple(sorted((u, v)))
        for u, v in zip(row, row[1:])
        if u != v
    }


def support(rows: tuple[tuple[int, ...], ...]) -> set[tuple[int, int]]:
    return set().union(*(row_edges(row) for row in rows)) if rows else set()


def pair_count(rows: tuple[tuple[int, ...], ...], u: int, v: int) -> int:
    """Lean semantics: count selected row slots, not vertex occurrences."""
    return sum(contains(row, u, v) for row in rows)


def raw_occurrence_product(rows: tuple[tuple[int, ...], ...], u: int, v: int) -> int:
    """Deliberately wrong semantics used only to exhibit a countermodel."""
    return sum(row.count(u) * row.count(v) for row in rows)


def replace_one(
    rows: tuple[tuple[int, ...], ...], index: int, replacement: tuple[int, ...]
) -> tuple[tuple[int, ...], ...]:
    return rows[:index] + (replacement,) + rows[index + 1 :]


def active_edges(
    blue: set[tuple[int, int]], rows: tuple[tuple[int, ...], ...]
) -> set[tuple[int, int]]:
    selected = set().union(*map(set, rows)) if rows else set()
    return {e for e in blue if set(e) <= selected and e not in support(rows)}


def exhaustive_theorem_check() -> dict:
    universe = tuple(
        itertools.chain.from_iterable(
            itertools.product(range(3), repeat=length) for length in range(1, 4)
        )
    )
    checked = 0
    qualifying = 0
    duplicate_row_cases = 0
    repeated_vertex_cases = 0
    component_change_cases = 0
    for rows in itertools.product(universe, repeat=2):
        for old_index in range(2):
            old = rows[old_index]
            if EDGE not in row_edges(old) or pair_count(rows, M, X) < 2:
                continue
            # This is the minimal geometric hypothesis used by the proof.
            if any(
                contains(row, M, X) and EDGE not in row_edges(row)
                for row in rows
            ):
                continue
            for replacement in universe:
                checked += 1
                target = replace_one(rows, old_index, replacement)
                assert EDGE in support(target)
                assert EDGE not in active_edges({EDGE}, target)
                qualifying += 1
                duplicate_row_cases += rows[0] == rows[1]
                repeated_vertex_cases += any(len(set(row)) < len(row) for row in rows)
                old_components = len(active_edges({EDGE, (M, A), (X, A)}, rows))
                new_components = len(active_edges({EDGE, (M, A), (X, A)}, target))
                component_change_cases += old_components != new_components
    return {
        "modelsChecked": checked,
        "qualifyingModels": qualifying,
        "failures": 0,
        "duplicateGeometricRowModels": duplicate_row_cases,
        "repeatedVertexModels": repeated_vertex_cases,
        "activeEdgeSetSizeChangedModels": component_change_cases,
    }


def countermodels() -> dict:
    # Dropping inducedness/cooccurrence-to-support: the retained row contains
    # both endpoints, but only nonconsecutively.
    rows = ((M, X), (M, A, X))
    target = replace_one(rows, 0, (A,))
    no_inducedness = {
        "oldRows": rows,
        "targetRows": target,
        "pairCount": pair_count(rows, M, X),
        "targetSupport": sorted(support(target)),
        "targetActive": sorted(active_edges({EDGE}, target)),
    }
    assert EDGE not in support(target) and EDGE in active_edges({EDGE}, target)

    # Dropping one-slot replacement: both witnesses can be removed together.
    rows = ((M, X), (M, X))
    target = ((A,), (A,))
    multi_replace = {
        "oldRows": rows,
        "targetRows": target,
        "pairCount": pair_count(rows, M, X),
        "targetSupport": sorted(support(target)),
    }
    assert EDGE not in support(target)

    # Confusing row count with raw occurrences permits one malformed row to
    # manufacture multiplicity two.  Actual pairCount remains one.
    rows = ((M, M, X),)
    target = ((A,),)
    occurrence_semantics = {
        "oldRows": rows,
        "targetRows": target,
        "pairCount": pair_count(rows, M, X),
        "rawOccurrenceProduct": raw_occurrence_product(rows, M, X),
        "targetSupport": sorted(support(target)),
    }
    assert pair_count(rows, M, X) == 1
    assert raw_occurrence_product(rows, M, X) == 2
    assert EDGE not in support(target)
    return {
        "withoutCooccurrenceToSupport": no_inducedness,
        "withoutOneSlotReplacement": multi_replace,
        "withWrongOccurrenceSemantics": occurrence_semantics,
    }


def detour_monotonicity_check() -> dict:
    """Exhaust the exact two-edge support update over small backgrounds."""
    x, m, y, v, a = range(5)
    old_row = (x, m, y)
    new_row = (x, v, y)
    old_edges = {tuple(sorted((x, m))), tuple(sorted((m, y)))}
    new_edges = {tuple(sorted((x, v))), tuple(sorted((v, y)))}
    blue = old_edges | new_edges
    universe = tuple(
        itertools.chain.from_iterable(
            itertools.product(range(5), repeat=length) for length in range(1, 4)
        )
    )
    checked = 0
    equal = 0
    strict = 0
    for background in universe:
        old_rows = (old_row, (v,), background)
        # All four square edges must be induced in every selected row.  This
        # is the direct local consequence used from genuine shortest rows.
        if any(
            contains(row, *edge) and edge not in row_edges(row)
            for row in old_rows
            for edge in blue
        ):
            continue
        old_support = support(old_rows)
        if not new_edges.isdisjoint(old_support):
            continue
        target_rows = (new_row, (v,), background)
        target_support = support(target_rows)
        disappearing = sum(edge not in support(old_rows[1:]) for edge in old_edges)
        assert len(target_support) == len(old_support) + 2 - disappearing
        assert len(target_support) >= len(old_support)
        pair_counts = [pair_count(old_rows, *edge) for edge in old_edges]
        is_equal = len(target_support) == len(old_support)
        assert is_equal == all(count == 1 for count in pair_counts)
        if is_equal:
            equal += 1
            for edge in old_edges:
                assert pair_count(target_rows, *edge) == 0
                assert pair_count(target_rows, edge[1], edge[0]) == 0
        else:
            strict += 1
        checked += 1
    assert checked and equal and strict
    return {
        "modelsChecked": checked,
        "equalityCases": equal,
        "strictGrowthCases": strict,
        "failures": 0,
        "rawOrderedFreeHalvesPerEqualityTransition": 8,
    }


def main() -> None:
    result = {
        "detourMonotonicityAudit": detour_monotonicity_check(),
        "theoremAudit": exhaustive_theorem_check(),
        "sharpCountermodels": countermodels(),
        "status": "PASS",
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
