#!/usr/bin/env python3
"""Canonical rank-independent certificate for nonsaturated rhombus triples.

Capture lemma.  Use boundary-distance coordinates (x,y,n-x-y).  Each coordinate
has range at most two on one unit rhombus, hence at most six on a connected
union of three rhombi.  Remove every empty boundary strip but retain one strip
next to a side which the union did not originally touch.  This preserves which
rhombus vertices are boundary/interior, and leaves every boundary distance at
most 6+1=7.  The resulting board has side at most 7+7+7=21.  Therefore checking
boards 3..21 exhausts all connected overlap types in every rank.

Disconnected triples are handled symbolically in the theorem report: either a
+-1 diagonal minor proves saturation, or a two-row component has equal mod-2
support and the integral midpoint subdivision used here applies.
"""

from collections import Counter
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import uniform_codim3_fast_gate as base  # noqa: E402
import uniform_codim3_local_classify as local  # noqa: E402
import uniform_codim3_local_classify_v2 as cert  # noqa: E402


def main():
    index_hist = Counter()
    parity_hist = Counter()
    canonical = set()
    violations = []
    checked = 0
    for n in range(3, 22):
        normals, _ = base.hive_normals(n)
        for ids in local.connected_triples(normals):
            rows = tuple(normals[i] for i in ids)
            if base.gram_data(rows)[-1] == 0:
                continue
            checked += 1
            q = base.saturation_index(rows)
            index_hist[q] += 1
            if q == 1:
                continue
            key = (q, local.canonical_columns(rows))
            canonical.add(key)
            try:
                parity, new_rays, cells = cert.subdivision(rows, q)
                parity_hist[(q, len(parity))] += 1
                if any(any(abs(x) > 1 for x in ray) or cert.norm2(ray) > 4 for ray in new_rays):
                    raise AssertionError("new ray exceeds 0,+-1 or norm-square four")
                if any(base.saturation_index(cell) != 1 for cell in cells):
                    raise AssertionError("a subdivision cell is nonsaturated")
            except Exception as exc:
                violations.append((n, ids, q, str(exc)))
    canon_text = "\n".join(str(x) for x in sorted(canonical)).encode("ascii")
    out = {
        "capture_bound": 21,
        "connected_rank3_triples_checked": checked,
        "index_histogram": dict(sorted(index_hist.items())),
        "canonical_nonsaturated_types": dict(Counter(str(q) for q, _ in canonical)),
        "parity_support_histogram": {str(k): v for k, v in sorted(parity_hist.items())},
        "violations": violations,
        "sha256_canonical_types": hashlib.sha256(canon_text).hexdigest(),
        "status": "PASS" if not violations and set(index_hist) <= {1, 2, 4} else "FAIL",
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
