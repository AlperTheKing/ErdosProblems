import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parents[1] / "p86"
sys.path.insert(0, str(HERE))
import dense_loose_search as p86


def score(values, h):
    edges, _ = p86.fold_edges(values, h)
    ac = {(a, c): i for i, (a, c, _u, _v) in enumerate(edges)}
    au = {(a, u): i for i, (a, _c, u, _v) in enumerate(edges)}
    cu = {(c, u): i for i, (_a, c, u, _v) in enumerate(edges)}
    triangles = []
    for a, c in ac:
        for u in values:
            ids = (ac.get((a, c)), au.get((a, u)), cu.get((c, u)))
            if None in ids or ids[0] == ids[1] == ids[2]:
                continue
            assert len(set(ids)) == 3
            triangles.append(ids)
    parent = list(range(len(edges)))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(x, y):
        x, y = find(x), find(y)
        if x != y:
            parent[y] = x
    for ids in triangles:
        union(ids[0], ids[1])
        union(ids[0], ids[2])
    vertices = {}
    triangle_counts = {}
    for vertex in range(len(edges)):
        root = find(vertex)
        vertices[root] = vertices.get(root, 0) + 1
    for ids in triangles:
        root = find(ids[0])
        triangle_counts[root] = triangle_counts.get(root, 0) + 1
    maximum_excess = max(
        (triangle_counts.get(root, 0) - count for root, count in vertices.items()),
        default=0,
    )
    return len(edges), len(triangles), maximum_excess


def translation_worker(values):
    z = tuple(values)
    p, width = len(z), z[-1]
    baseline = (3 * p * p - p + 2) // 2
    max_gamma = min(width - 1, baseline - width - 2)
    if max_gamma < 0:
        return {"tested": 0, "holes": 0, "failures": 0, "component_failures": 0, "max_component_excess": 0, "best": None}
    sum_mask, difference_mask = p86.masks_for_ruler(z)
    tested = holes = failures = component_failures = 0
    max_component_excess = 0
    best = None
    for gamma in range(max_gamma + 1):
        h = width + gamma + 1
        if (sum_mask & (sum_mask >> h)).bit_count() == 0:
            continue
        for b in (1, 2):
            tested += 1
            shift = 2 * gamma + b
            if ((sum_mask << shift) & difference_mask) != 0:
                continue
            holes += 1
            B = tuple(x + gamma for x in z)
            c_s, t_f, component_excess = score(B, h)
            if t_f > c_s:
                failures += 1
            if component_excess > 0:
                component_failures += 1
            max_component_excess = max(max_component_excess, component_excess)
            key = (Fraction(t_f, c_s), t_f, -p) if c_s else (Fraction(0), 0, -p)
            if best is None or key > best[0]:
                best = (key, {"B": B, "p": p, "h": h, "b": b, "C_S": c_s, "T_F": t_f})
    return {"tested": tested, "holes": holes, "failures": failures, "component_failures": component_failures, "max_component_excess": max_component_excess, "best": best[1] if best else None}


def insertion_worker(values):
    z = tuple(values)
    p, width = len(z), z[-1]
    new_p = p + 1
    baseline = (3 * new_p * new_p - new_p + 2) // 2
    max_g = min(width, (baseline - 1) // 2 - width)
    if max_g < 1:
        return {"tested": 0, "holes": 0, "failures": 0, "component_failures": 0, "max_component_excess": 0, "best": None}
    tested = holes = failures = component_failures = 0
    max_component_excess = 0
    best = None
    for g in range(1, max_g + 1):
        c_base = tuple(value + g for value in z)
        h0 = width + g
        existing = set(p86.unordered_sum_map(c_base))
        occupied = set(c_base)
        for x in range(1, h0):
            if x in occupied:
                continue
            tested += 1
            if not p86.insertion_is_sidon(c_base, existing, x):
                continue
            c = tuple(sorted(c_base + (x,)))
            B = tuple(2 * value - 1 for value in c)
            h = 2 * h0
            holes += 1
            c_s, t_f, component_excess = score(B, h)
            if t_f > c_s:
                failures += 1
            if component_excess > 0:
                component_failures += 1
            max_component_excess = max(max_component_excess, component_excess)
            key = (Fraction(t_f, c_s), t_f, -new_p) if c_s else (Fraction(0), 0, -new_p)
            if best is None or key > best[0]:
                best = (key, {"B": B, "p": new_p, "h": h, "b": 1, "C_S": c_s, "T_F": t_f})
    return {"tested": tested, "holes": holes, "failures": failures, "component_failures": component_failures, "max_component_excess": max_component_excess, "best": best[1] if best else None}


def best_row(rows):
    candidates = [row["best"] for row in rows if row["best"] is not None]
    return max(candidates, key=lambda row: (Fraction(row["T_F"], row["C_S"]) if row["C_S"] else 0, row["T_F"]))


def run(worker, payloads, workers):
    if workers == 1:
        return [worker(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(worker, payloads, chunksize=1))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        raise ValueError("workers must be in [1,64]")
    bases, _ = p86.load_archives()
    translation_rows = run(translation_worker, [base.values for base in bases], args.workers)
    insertion_bases = [
        base for base in bases
        if len(base.values) <= 40
        and any("/p46/" in source or "/p53/" in source for source in base.sources)
    ]
    insertion_rows = run(insertion_worker, [base.values for base in insertion_bases], args.workers)
    result = {
        "schema_version": 1,
        "arithmetic": "exact Python integers and Fraction rankings",
        "workers": args.workers,
        "translation": {
            "bases": len(bases),
            "tested": sum(row["tested"] for row in translation_rows),
            "literal_holes": sum(row["holes"] for row in translation_rows),
            "failures": sum(row["failures"] for row in translation_rows),
            "component_failures": sum(row["component_failures"] for row in translation_rows),
            "maximum_component_excess": max(row["max_component_excess"] for row in translation_rows),
            "max_ratio_row": best_row(translation_rows),
        },
        "insertion": {
            "bases": len(insertion_bases),
            "tested": sum(row["tested"] for row in insertion_rows),
            "literal_holes": sum(row["holes"] for row in insertion_rows),
            "failures": sum(row["failures"] for row in insertion_rows),
            "component_failures": sum(row["component_failures"] for row in insertion_rows),
            "maximum_component_excess": max(row["max_component_excess"] for row in insertion_rows),
            "max_ratio_row": best_row(insertion_rows),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))
    assert result["translation"]["failures"] == 0
    assert result["insertion"]["failures"] == 0


if __name__ == "__main__":
    main()
