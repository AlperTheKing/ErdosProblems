#!/usr/bin/env python3
"""Find a genuine size-four hive face carrying the U(2,4) tight-row set.

This is a bounded diagnostic for the proposed graphic/cographic
classification of tight-rhombus coarsenings.  It is not a KTT search.
"""

from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "r4_reeve"))
from hive4 import _affine_rank, _dot, build_hive4, vertices  # noqa: E402


TARGET = {
    (-1, -1, 1),
    (-1, 0, 0),
    (-1, 1, -1),
    (0, -1, 1),
}


def partitions4(n):
    def rec(rem, k, cap, out):
        if k == 0:
            if rem == 0:
                yield tuple(out)
            return
        for x in range(min(rem, cap), -1, -1):
            if x * k < rem:
                break
            out.append(x)
            yield from rec(rem - x, k - 1, x, out)
            out.pop()

    yield from rec(n, 4, n, [])


def main(max_weight=30):
    pools = {n: tuple(partitions4(n)) for n in range(max_weight + 1)}
    checked = candidates = 0
    for total in range(max_weight + 1):
        for nu in pools[total]:
            for left_weight in range(total + 1):
                for lam in pools[left_weight]:
                    for mu in pools[total - left_weight]:
                        checked += 1
                        h = build_hive4(lam, mu, nu)
                        if not h["ok"]:
                            continue
                        by_normal = {}
                        for i, row in enumerate(h["A"]):
                            row = tuple(row)
                            if row in TARGET:
                                by_normal.setdefault(row, []).append(i)
                        if set(by_normal) != TARGET:
                            raise AssertionError("target normal missing from atlas")

                        # A common equality point requires these right-hand-side
                        # relations because v1=v2+v4 and v3=v2-v4.  Duplicate
                        # rows must also define the same hyperplane.
                        rhs = {v: {h["b"][i] for i in inds}
                               for v, inds in by_normal.items()}
                        if any(len(values) != 1 for values in rhs.values()):
                            continue
                        v1 = (-1, -1, 1)
                        v2 = (-1, 0, 0)
                        v3 = (-1, 1, -1)
                        v4 = (0, -1, 1)
                        b = {v: next(iter(values)) for v, values in rhs.items()}
                        if b[v1] != b[v2] + b[v4] or b[v3] != b[v2] - b[v4]:
                            continue
                        candidates += 1

                        verts = vertices(h["A"], h["b"])
                        if _affine_rank(verts) != 3:
                            continue
                        face = [x for x in verts if all(
                            _dot(row, x) == h["b"][i]
                            for i, row in enumerate(h["A"])
                            if tuple(row) in TARGET)]
                        if _affine_rank(face) != 1:
                            continue
                        active = [i for i, row in enumerate(h["A"])
                                  if all(_dot(row, x) == h["b"][i] for x in face)]
                        print("status=PASS")
                        print("checked=%d" % checked)
                        print("rhs_candidates=%d" % candidates)
                        print("lambda=%r" % (lam,))
                        print("mu=%r" % (mu,))
                        print("nu=%r" % (nu,))
                        print("face_vertices=%r" % (face,))
                        print("active_rows=%r" % (active,))
                        print("active_normals=%r" %
                              (tuple(tuple(h["A"][i]) for i in active),))
                        return 0
    print("status=NO_WITNESS")
    print("max_weight=%d" % max_weight)
    print("checked=%d" % checked)
    print("rhs_candidates=%d" % candidates)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
