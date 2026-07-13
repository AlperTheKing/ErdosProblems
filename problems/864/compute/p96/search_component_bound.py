import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module

p46 = load("p46_component", ROOT / "problems/864/compute/p46/carry_statistics.py")
p84 = load("p84_component", ROOT / "problems/864/compute/p84/audit_phase_fourier.py")

def component_data(folds):
    ac = {(a, c): i for i, (a, c, _u, _v) in enumerate(folds)}
    au = {(a, u): i for i, (a, _c, u, _v) in enumerate(folds)}
    cu = {(c, u): i for i, (_a, c, u, _v) in enumerate(folds)}
    triangles = []
    vertices = sorted({x for edge in folds for x in edge})
    for a, c in ac:
        for u in vertices:
            ids = (ac.get((a, c)), au.get((a, u)), cu.get((c, u)))
            if None in ids or ids[0] == ids[1] == ids[2]:
                continue
            assert len(set(ids)) == 3
            triangles.append(ids)
    parent = list(range(len(folds)))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(x, y):
        x, y = find(x), find(y)
        if x != y:
            parent[y] = x
    for edge in triangles:
        union(edge[0], edge[1])
        union(edge[0], edge[2])
    component_vertices = {}
    component_edges = {}
    for vertex in range(len(folds)):
        root = find(vertex)
        component_vertices[root] = component_vertices.get(root, 0) + 1
    for edge in triangles:
        root = find(edge[0])
        component_edges[root] = component_edges.get(root, 0) + 1
    maximum = max((component_edges.get(root, 0) - count for root, count in component_vertices.items()), default=0)
    return len(triangles), maximum

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=30)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    holes = nonzero = failures = 0
    max_excess = None
    witness = None
    for width in range(1, args.max_width + 1):
        for ruler in p46.sidon_rulers(width):
            p = len(ruler)
            baseline = (3 * p * p - p + 2) // 2
            max_gamma = baseline - width - 2
            if max_gamma < 0:
                continue
            forbidden = p46.forbidden_three_minus_one(ruler)
            z = tuple(sorted(width - x for x in ruler))
            for b in (1, 2):
                for gamma in range(max_gamma + 1):
                    if 2 * width + 2 * gamma + b in forbidden:
                        continue
                    holes += 1
                    B = tuple(gamma + x for x in z)
                    h = gamma + width + 1
                    folds = p84.canonical_folds(B, h)
                    triangles, excess = component_data(folds)
                    if triangles:
                        nonzero += 1
                    if excess > 0:
                        failures += 1
                    if max_excess is None or excess > max_excess:
                        max_excess = excess
                        witness = {"B": B, "p": p, "h": h, "b": b, "C_S": len(folds), "T_F": triangles, "max_component_excess": excess}
    result = {"max_width": args.max_width, "literal_holes": holes, "nonzero_triangle_rows": nonzero, "failures": failures, "maximum_component_excess": max_excess, "witness": witness}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
