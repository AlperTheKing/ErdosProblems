#!/usr/bin/env python3
"""Corrected exact certificate for all connected nonsaturated triple types.

The capture proof is in ``uniform_codim3_local_classify.py``: sizes 3..18
exhaust every connected three-rhombus overlap after deleting empty boundary
strips.  Disconnected triples reduce to a two-row component; a 2x2 0,+-1
minor is either odd (hence +-1) or the two supports agree mod 2 (index two).

For every nonsaturated connected type this checker also certifies a normal-cone
subdivision into saturated simplicial cones whose ray generators still have
squared Euclidean norm at most four.  Thus the universal saturated Gram lemma
applies to every cell.
"""

from collections import Counter
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import uniform_codim3_fast_gate as base  # noqa: E402
import uniform_codim3_index2_gate as idx2  # noqa: E402
import uniform_codim3_local_classify as local  # noqa: E402


def halfsum(rows, which):
    return tuple(sum(rows[i][j] for i in which) // 2 for j in range(len(rows[0])))


def norm2(v):
    return sum(x * x for x in v)


def subdivision(rows, q):
    if q == 2:
        a = idx2.parity_vector(rows)
        which = tuple(i for i, x in enumerate(a) if x)
        h = halfsum(rows, which)
        assert all(sum(rows[i][j] for i in which) % 2 == 0 for j in range(len(h)))
        if len(which) == 2:
            i, j = which
            k = next(x for x in range(3) if x not in which)
            cells = ((rows[k], rows[i], h), (rows[k], h, rows[j]))
        elif len(which) == 3:
            cells = ((rows[0], rows[1], h), (rows[0], h, rows[2]), (h, rows[1], rows[2]))
        else:
            raise AssertionError("impossible parity support")
        return which, (h,), cells
    if q == 4:
        h01, h02, h12 = halfsum(rows, (0, 1)), halfsum(rows, (0, 2)), halfsum(rows, (1, 2))
        cells = (
            (rows[0], h01, h02),
            (rows[1], h01, h12),
            (rows[2], h02, h12),
            (h01, h02, h12),
        )
        return (2, 2, 2), (h01, h02, h12), cells
    raise AssertionError(f"unhandled index {q}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=18)
    args = ap.parse_args()
    hist = Counter()
    parity_hist = Counter()
    type_keys = set()
    violations = []
    first = {}
    for n in range(3, args.max_n + 1):
        normals, _ = base.hive_normals(n)
        for ids in local.connected_triples(normals):
            rows = tuple(normals[i] for i in ids)
            if base.gram_data(rows)[-1] == 0:
                continue
            q = base.saturation_index(rows)
            hist[q] += 1
            if q == 1:
                continue
            key = (q, local.canonical_columns(rows))
            type_keys.add(key)
            first.setdefault(key, (n, ids, rows))
            try:
                parity, new_rays, cells = subdivision(rows, q)
                parity_hist[(q, len(parity))] += 1
                if any(any(abs(x) > 1 for x in ray) or norm2(ray) > 4 for ray in new_rays):
                    raise AssertionError("new ray is not a 0,+-1 norm<=4 vector")
                if any(base.saturation_index(cell) != 1 for cell in cells):
                    raise AssertionError("subdivision cell is not saturated")
            except Exception as exc:
                violations.append({"n": n, "ids": ids, "index": q, "error": str(exc), "rows": rows})
    examples = []
    for key in sorted(type_keys):
        q, cols = key
        n, ids, rows = first[key]
        parity, new_rays, cells = subdivision(rows, q)
        examples.append({
            "index": q,
            "canonical_columns": cols,
            "first_n": n,
            "ids": ids,
            "parity_support": parity,
            "new_rays": new_rays,
            "cell_count": len(cells),
        })
    print(json.dumps({
        "max_n": args.max_n,
        "capture_bound": 18,
        "rank3_connected_index_histogram": dict(sorted(hist.items())),
        "nonsaturated_type_histogram": dict(Counter(str(q) for q, _ in type_keys)),
        "parity_support_histogram": {str(k): v for k, v in sorted(parity_hist.items())},
        "violations": violations,
        "status": "PASS" if args.max_n >= 18 and not violations else "INCOMPLETE_OR_FAIL",
        "examples": examples,
    }, indent=2))


if __name__ == "__main__":
    main()
