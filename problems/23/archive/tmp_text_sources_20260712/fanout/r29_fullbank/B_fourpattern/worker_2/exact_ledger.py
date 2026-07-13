"""Tiny exact half-slot ledger; no floats and no graph-specific dependencies."""
from collections import defaultdict


def shore_reach(shore, relation, capacities):
    """Capacity of the deduplicated union of cells reachable from shore."""
    cells = {cell for owner in shore for cell in relation.get(owner, ())}
    return sum(capacities[cell] for cell in cells)


def expand_sources(capacities):
    """Canonical globally unique atomic source IDs (ordered cell, half-bit)."""
    return {
        (cell[0], cell[1], half)
        for cell, capacity in capacities.items()
        for half in range(capacity)
    }


def audit(demand, relation, capacities, shores):
    assert all(isinstance(x, int) and x >= 0 for x in demand.values())
    assert all(capacity in (1, 2) for capacity in capacities.values())
    assert all(cell in capacities for cells in relation.values() for cell in cells)
    source_ids = expand_sources(capacities)
    assert len(source_ids) == sum(capacities.values())
    out = []
    for shore in shores:
        shore = frozenset(shore)
        d = sum(demand.get(v, 0) for v in shore)
        r = shore_reach(shore, relation, capacities)
        out.append((tuple(sorted(shore)), d, r, r - d))
    return out


if __name__ == "__main__":
    # One shared cell witnessed by two owners is counted once in shore reach.
    demand = {0: 1, 1: 1}
    relation = defaultdict(set, {0: {(2, 3)}, 1: {(2, 3)}})
    capacities = {(2, 3): 2}
    assert audit(demand, relation, capacities, [{0}, {1}, {0, 1}])[-1] == (
        (0, 1), 2, 2, 0
    )
    print("PASS: exact shared-source deduplication")
