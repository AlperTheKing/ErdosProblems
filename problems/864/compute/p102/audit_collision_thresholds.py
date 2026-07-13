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

p46 = load("p46_p102", ROOT / "problems/864/compute/p46/carry_statistics.py")
p84 = load("p84_p102", ROOT / "problems/864/compute/p84/audit_phase_fourier.py")

def slacks(B, h, b):
    differences = {y - x for i, x in enumerate(B) for y in B[i + 1:]}
    folds = p84.canonical_folds(B, h)
    graph = {(a, c) for a, c, _u, _v in folds}
    by_u = {}
    for a, c, u, _v in folds:
        by_u.setdefault(u, []).append((a, c))
    increments = []
    for u, matching in sorted(by_u.items()):
        left = {a for a, _c in matching}
        right = {c for _a, c in matching}
        induced = sum((a, c) in graph for a in left for c in right)
        collisions = sum(a + c + b in differences for a, c in matching)
        increments.append(len(matching) + collisions - (induced - len(matching)))
    prefix = minimum_prefix = 0
    for increment in increments:
        prefix += increment
        minimum_prefix = min(minimum_prefix, prefix)
    suffix = minimum_suffix = 0
    for increment in reversed(increments):
        suffix += increment
        minimum_suffix = min(minimum_suffix, suffix)
    return minimum_prefix, minimum_suffix, prefix

def audit_rows(rows):
    count = prefix_failures = suffix_failures = total_failures = 0
    minima = [0, 0, 0]
    first = None
    for B, h, b in rows:
        count += 1
        values = slacks(B, h, b)
        prefix_failures += values[0] < 0
        suffix_failures += values[1] < 0
        total_failures += values[2] < 0
        minima = [min(x, y) for x, y in zip(minima, values)]
        if first is None and min(values) < 0:
            first = {"B": B, "h": h, "b": b, "slacks": values}
    return {"rows": count, "prefix_failures": prefix_failures, "suffix_failures": suffix_failures, "total_failures": total_failures, "minimum_slacks": minima, "first_failure": first}

def width_rows():
    for width in range(1, 31):
        for ruler in p46.sidon_rulers(width):
            z = tuple(sorted(width - x for x in ruler))
            for gamma in range(width):
                B = tuple(gamma + x for x in z)
                h = gamma + width + 1
                for b in (1, 2):
                    yield B, h, b

P88 = (0,122,163,328,351,488,499,528,553,681,837,838,920,941,1051,1070,1117,1322,1340,1414,1449,1520,1608,1613,1617,1715,1853,1866,1925,2057,2074,2153,2173,2240,2320,2380,2475,2521,2564,2596,2598,2654,2788,2815,2839,2901,2950,2958,3026,3070,3076,3131,3170,3184,3200,3212,3215,3222,3248,3285)

def p88_rows():
    for gamma in range(2085):
        B = tuple(x + gamma for x in P88)
        h = 3286 + gamma
        for b in (1, 2):
            yield B, h, b

result = {"schema_version": 1, "arithmetic": "exact Python integers", "width_30_unrestricted": audit_rows(width_rows()), "P88_positive_defect_translations": audit_rows(p88_rows())}
output = Path(__file__).with_name("collision_thresholds.json")
output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
print(json.dumps(result, indent=2))
