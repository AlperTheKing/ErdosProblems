"""Independent exact R29 blue-geodesic audit; no lead imports."""
from __future__ import annotations

from collections import Counter, deque
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def E(a: int, b: int) -> tuple[int, int]:
    if a == b:
        raise ValueError("loop")
    return (a, b) if a < b else (b, a)


def construct() -> tuple[int, set[tuple[int, int]], list[tuple[str, tuple[int, int]]]]:
    blue: set[tuple[int, int]] = set()
    atoms: list[tuple[str, tuple[int, int]]] = []
    root, lc, rc, anchor = 0, 1, 2, 55
    left, right = range(3, 29), range(29, 55)
    blue |= {E(root, lc), E(root, rc)}
    blue |= {E(lc, u) for u in left} | {E(rc, v) for v in right}
    atoms += [("double-star", E(u, v)) for u in left for v in right]

    cursor = 56
    regions: list[list[tuple[int, int, int]]] = []
    for leaves in (left, right):
        arms = []
        for leaf in leaves:
            for _ in range(26):
                x, y = cursor, cursor + 1
                cursor += 2
                arms.append((leaf, x, y))
                blue |= {E(leaf, x), E(x, y), E(y, anchor)}
        regions.append(arms)
    if cursor != 2760:
        raise AssertionError(cursor)

    for q, arms in zip((2760, 2761), regions):
        fixed, detour = arms[:338], arms[338:]
        for j in range(338):
            xf = fixed[j][1]
            yf1 = fixed[(j + 1) % 338][2]
            xd = detour[j][1]
            yd1 = detour[(j + 1) % 338][2]
            path = (q, xf, yf1, xd, yd1)
            blue |= {E(a, b) for a, b in zip(path, path[1:])}
            atoms.append(("selector", E(q, yd1)))

    off, w = 2762, 26
    circuit_support = {E(i, (i + 1) % 26) for i in range(26)} | {E(w, 0)}
    seq = [(9 * k) % 26 for k in range(13)]
    circuit_support |= {E(seq[i], seq[i + 1]) for i in range(12)}
    blue |= {E(off + a, off + b) for a, b in circuit_support}
    circuit_atoms = sorted({E(i, (i + 4) % 26) for i in range(26)} | {E(w, 3), E(w, 23)})
    cursor = off + 27
    for a, b in circuit_atoms:
        internal = tuple(range(cursor, cursor + 5))
        cursor += 5
        path = (off + a,) + internal + (off + b,)
        blue |= {E(u, v) for u, v in zip(path, path[1:])}
        atoms.append(("circuit", E(off + a, off + b)))
    if cursor != 2929:
        raise AssertionError(cursor)

    zl, zr = 2929, 2930
    blue |= {E(root, anchor), E(anchor, off + 2), E(lc, zl), E(zl, anchor),
             E(rc, zr), E(zr, anchor)}
    cursor = 2931
    for seed in (anchor, zl, zr):
        internal = tuple(range(cursor, cursor + 4))
        cursor += 4
        path = (seed,) + internal
        blue |= {E(u, v) for u, v in zip(path, path[1:])}
        atoms.append(("cable-seed", E(seed, internal[-1])))
    return cursor, blue, atoms


def adjacency(n: int, edges: set[tuple[int, int]]) -> list[tuple[int, ...]]:
    a = [set() for _ in range(n)]
    for u, v in edges:
        a[u].add(v); a[v].add(u)
    return [tuple(sorted(x)) for x in a]


def distances(a: list[tuple[int, ...]], start: int) -> list[int]:
    d = [-1] * len(a); d[start] = 0; q = deque([start])
    while q:
        u = q.popleft()
        for v in a[u]:
            if d[v] == -1:
                d[v] = d[u] + 1; q.append(v)
    return d


def enumerate_rows(a: list[tuple[int, ...]], s: int, t: int) -> tuple[list[tuple[int, ...]], int]:
    ds, dt = distances(a, s), distances(a, t)
    L = ds[t]
    rows: list[tuple[int, ...]] = []
    def go(u: int, path: tuple[int, ...]) -> None:
        if u == t:
            rows.append(path); return
        for v in a[u]:
            if ds[v] == ds[u] + 1 and ds[v] + dt[v] == L:
                go(v, path + (v,))
    go(s, (s,))
    return rows, L


def main() -> None:
    n, blue, typed_atoms = construct()
    if n != 2943 or len(blue) != 7039 or len(typed_atoms) != 1383:
        raise AssertionError((n, len(blue), len(typed_atoms)))
    if len({atom for _, atom in typed_atoms}) != 1383:
        raise AssertionError("duplicate atoms")
    adj = adjacency(n, blue)
    blue_hash = hashlib.sha256()
    for u, v in sorted(blue):
        blue_hash.update(f"{u},{v}\n".encode())
    histogram, by_class, distance_hist = Counter(), {}, Counter()
    row_hash = hashlib.sha256(); atom_hash = hashlib.sha256()
    total_rows = 0; gamma = 0; samples = {}; discrepancies = []
    for kind, atom in typed_atoms:
        rows, length = enumerate_rows(adj, *atom)
        count = len(rows); total_rows += count
        histogram[count] += 1; distance_hist[length] += 1
        by_class.setdefault(kind, Counter())[count] += 1
        # Gamma definition used by R29: sum of squared row cardinalities of one
        # chosen shortest row per bad atom. Enumeration proves cardinality 5.
        if not rows:
            discrepancies.append({"atom": atom, "error": "no blue path"})
        else:
            gamma += len(rows[0]) ** 2
            samples.setdefault(kind, {"atom": list(atom), "row": list(rows[0]), "count": count})
        atom_hash.update(f"{kind}:{atom[0]},{atom[1]}\n".encode())
        for row in rows:
            if len(row) != length + 1 or row[0] != atom[0] or row[-1] != atom[1]:
                discrepancies.append({"atom": atom, "row": row, "error": "malformed"})
            row_hash.update((",".join(map(str, row)) + "\n").encode())
    expected_hist = Counter({1: 707, 680: 676})
    if histogram != expected_hist:
        discrepancies.append({"error": "histogram", "actual": dict(histogram), "expected": dict(expected_hist)})
    result = {
        "arithmetic": "integer-only",
        "constructor_counts": {"vertices": n, "blue_edges": len(blue), "bad_atoms": len(typed_atoms)},
        "distance_histogram": dict(sorted(distance_hist.items())),
        "row_count_histogram": dict(sorted(histogram.items())),
        "class_histograms": {k: dict(sorted(v.items())) for k, v in sorted(by_class.items())},
        "total_materialized_rows": total_rows,
        "gamma": gamma,
        "gamma_formula": "sum over atoms of (#vertices in any shortest row)^2",
        "samples": samples,
        "discrepancies": discrepancies,
        "sha256": {"blue_edge_stream": blue_hash.hexdigest(), "typed_atom_stream": atom_hash.hexdigest(),
                   "all_shortest_row_stream": row_hash.hexdigest()},
    }
    (OUT / "audit_result.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
