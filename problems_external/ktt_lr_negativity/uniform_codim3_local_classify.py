#!/usr/bin/env python3
"""Rank-independent local classification of nonsaturated rhombus triples.

Each hive row is a signed unit-rhombus stencil, restricted to the interior
vertices.  If the support-overlap graph of three rows is connected, the union
of their full rhombi has range at most six in each of the three triangular
boundary-distance coordinates.  Delete the three empty boundary strips; the
same restricted signed column matrix is then realized on a board of side at
most 6+6+6=18.  Hence sizes 3..18 exhaust every connected local overlap type,
independently of rank.

If the overlap graph is disconnected and the rows have rank three, any
nonsaturation must already occur in its two-row component.  For two primitive
0,+-1 rows, nonsaturation is equivalent to equality of their supports mod 2;
then their half-sum is an integral 0,+-1 vector with squared norm at most four.

The exact census below checks the connected part.  Its expected conclusion is:
index 1 or 2 only, and every index-two type has two equal mod-2 rows.  The lone
index-four type on the size-four board also has all three supports equal and is
listed separately (its overlap graph is connected, so it is found here).
"""

from itertools import combinations, permutations
from collections import Counter
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import uniform_codim3_fast_gate as base  # noqa: E402


def canonical_columns(rows):
    candidates = []
    for perm in permutations(range(3)):
        cols = [
            tuple(rows[perm[i]][j] for i in range(3))
            for j in range(len(rows[0]))
            if any(rows[i][j] for i in range(3))
        ]
        candidates.append(tuple(sorted(cols)))
    return min(candidates)


def mod2_equal_pairs(rows):
    supports = [{j for j, x in enumerate(row) if x} for row in rows]
    return [(i, j) for i, j in combinations(range(3), 2) if supports[i] == supports[j]]


def connected_triples(normals):
    supports = [{j for j, x in enumerate(row) if x} for row in normals]
    nbr = [set() for _ in normals]
    for i, j in combinations(range(len(normals)), 2):
        if supports[i] & supports[j]:
            nbr[i].add(j)
            nbr[j].add(i)
    triples = set()
    # Every connected graph on three vertices has a vertex incident to two
    # edges, so choosing two neighbours of a centre enumerates it exactly.
    for centre, ns in enumerate(nbr):
        for i, j in combinations(ns, 2):
            triples.add(tuple(sorted((centre, i, j))))
    return sorted(triples)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=18)
    args = ap.parse_args()
    types = {}
    per_n = []
    violations = []
    for n in range(3, args.max_n + 1):
        normals, _ = base.hive_normals(n)
        idx_hist = Counter()
        local_count = 0
        for ids in connected_triples(normals):
            rows = tuple(normals[i] for i in ids)
            if base.gram_data(rows)[-1] == 0:
                continue
            local_count += 1
            q = base.saturation_index(rows)
            idx_hist[q] += 1
            if q > 1:
                pairs = mod2_equal_pairs(rows)
                key = (q, canonical_columns(rows))
                types.setdefault(key, {"first_n": n, "ids": ids, "rows": rows, "equal_pairs": pairs})
                if q not in (2, 4) or not pairs:
                    violations.append({"n": n, "q": q, "ids": ids, "rows": rows, "equal_pairs": pairs})
                if q == 2 and len(pairs) != 1:
                    violations.append({"n": n, "q": q, "ids": ids, "reason": "index2_pair_count", "equal_pairs": pairs})
                if q == 4 and not (n == 4 and len(pairs) == 3):
                    violations.append({"n": n, "q": q, "ids": ids, "reason": "unexpected_index4", "equal_pairs": pairs})
        per_n.append({"n": n, "connected_rank3": local_count, "index_histogram": dict(sorted(idx_hist.items()))})
    print(json.dumps({
        "max_n": args.max_n,
        "capture_bound": 18,
        "per_n": per_n,
        "nonsaturated_canonical_types": dict(Counter(str(q) for q, _ in types)),
        "violations": violations,
        "status": "PASS" if args.max_n >= 18 and not violations else "INCOMPLETE_OR_FAIL",
        "types": [
            {"index": q, "columns": cols, **witness}
            for (q, cols), witness in sorted(types.items())
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
