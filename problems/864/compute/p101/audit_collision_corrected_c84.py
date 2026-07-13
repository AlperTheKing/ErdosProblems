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

p46 = load("p46_p101", ROOT / "problems/864/compute/p46/carry_statistics.py")
p84 = load("p84_p101", ROOT / "problems/864/compute/p84/audit_phase_fourier.py")

def audit_row(B, h, b):
    differences = {y - x for i, x in enumerate(B) for y in B[i + 1:]}
    folds = p84.canonical_folds(B, h)
    ac = {(a, c): i for i, (a, c, _u, _v) in enumerate(folds)}
    au = {(a, u): i for i, (a, _c, u, _v) in enumerate(folds)}
    cu = {(c, u): i for i, (_a, c, u, _v) in enumerate(folds)}
    triangles = []
    for a, c in ac:
        for u in B:
            ids = (ac.get((a, c)), au.get((a, u)), cu.get((c, u)))
            if None in ids or ids[0] == ids[1] == ids[2]:
                continue
            assert len(set(ids)) == 3
            triangles.append(ids)
    collision = [a + c + b in differences for a, c, _u, _v in folds]
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
    for ids in triangles:
        union(ids[0], ids[1])
        union(ids[0], ids[2])
    vertices = {}
    edges = {}
    collisions = {}
    for vertex in range(len(folds)):
        root = find(vertex)
        vertices[root] = vertices.get(root, 0) + 1
        collisions[root] = collisions.get(root, 0) + int(collision[vertex])
    for ids in triangles:
        root = find(ids[0])
        edges[root] = edges.get(root, 0) + 1
    component_residual = max((edges.get(root, 0) - count - collisions[root] for root, count in vertices.items()), default=0)
    return {
        "C_S": len(folds),
        "T_F": len(triangles),
        "collided_fold_labels": sum(collision),
        "total_residual": len(triangles) - len(folds) - sum(collision),
        "max_component_residual": component_residual,
    }

def scan_width_30():
    rows = total_failures = component_failures = 0
    worst_total = 0
    worst_component = 0
    for width in range(1, 31):
        for ruler in p46.sidon_rulers(width):
            z = tuple(sorted(width - x for x in ruler))
            for gamma in range(width):
                B = tuple(gamma + x for x in z)
                h = gamma + width + 1
                for b in (1, 2):
                    rows += 1
                    row = audit_row(B, h, b)
                    total_failures += row["total_residual"] > 0
                    component_failures += row["max_component_residual"] > 0
                    worst_total = max(worst_total, row["total_residual"])
                    worst_component = max(worst_component, row["max_component_residual"])
    return {"rows": rows, "total_failures": total_failures, "component_failures": component_failures, "max_total_residual": worst_total, "max_component_residual": worst_component}

P88 = (
    0, 122, 163, 328, 351, 488, 499, 528, 553, 681, 837, 838, 920, 941,
    1051, 1070, 1117, 1322, 1340, 1414, 1449, 1520, 1608, 1613, 1617,
    1715, 1853, 1866, 1925, 2057, 2074, 2153, 2173, 2240, 2320, 2380,
    2475, 2521, 2564, 2596, 2598, 2654, 2788, 2815, 2839, 2901, 2950,
    2958, 3026, 3070, 3076, 3131, 3170, 3184, 3200, 3212, 3215, 3222,
    3248, 3285,
)

def scan_p88_translations():
    rows = total_failures = component_failures = 0
    worst_total = None
    worst_component = None
    for gamma in range(2085):
        B = tuple(x + gamma for x in P88)
        h = 3286 + gamma
        for b in (1, 2):
            rows += 1
            row = audit_row(B, h, b)
            total_failures += row["total_residual"] > 0
            component_failures += row["max_component_residual"] > 0
            total_key = row["total_residual"]
            component_key = row["max_component_residual"]
            if worst_total is None or total_key > worst_total[0]:
                worst_total = (total_key, {"gamma": gamma, "b": b, **row})
            if worst_component is None or component_key > worst_component[0]:
                worst_component = (component_key, {"gamma": gamma, "b": b, **row})
    return {
        "rows": rows,
        "total_failures": total_failures,
        "component_failures": component_failures,
        "worst_total": worst_total[1],
        "worst_component": worst_component[1],
    }

result = {
    "schema_version": 1,
    "arithmetic": "exact Python integers",
    "inequality": "T_F <= C_S + number of folds whose low sum plus b is a represented positive difference",
    "width_30_unrestricted": scan_width_30(),
    "P88_positive_defect_translations": scan_p88_translations(),
}
output = Path(__file__).with_name("collision_corrected_c84.json")
output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
print(json.dumps(result, indent=2))
