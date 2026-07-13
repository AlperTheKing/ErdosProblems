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

p46 = load("p46_p100", ROOT / "problems/864/compute/p46/carry_statistics.py")
p84 = load("p84_p100", ROOT / "problems/864/compute/p84/audit_phase_fourier.py")
p96 = load("p96_p100", ROOT / "problems/864/compute/p96/search_component_bound.py")
p99 = load("p99_p100", ROOT / "problems/864/compute/p99/search_color_threshold_bound.py")

rows = total_failures = component_failures = prefix_failures = suffix_failures = 0
max_difference = 0
max_component_excess = 0
min_prefix = 0
min_suffix = 0
witness = None
for width in range(1, 31):
    for ruler in p46.sidon_rulers(width):
        z = tuple(sorted(width - x for x in ruler))
        for gamma in range(width):
            rows += 1
            B = tuple(gamma + x for x in z)
            h = gamma + width + 1
            folds = p84.canonical_folds(B, h)
            triangles, component_excess = p96.component_data(folds)
            prefix, suffix, total = p99.threshold_slacks(folds)
            difference = triangles - len(folds)
            total_failures += difference > 0
            component_failures += component_excess > 0
            prefix_failures += prefix < 0
            suffix_failures += suffix < 0
            max_difference = max(max_difference, difference)
            max_component_excess = max(max_component_excess, component_excess)
            min_prefix = min(min_prefix, prefix)
            min_suffix = min(min_suffix, suffix)
            if witness is None and (difference > 0 or component_excess > 0 or prefix < 0 or suffix < 0):
                witness = {"B": B, "h": h, "C_S": len(folds), "T_F": triangles, "component_excess": component_excess, "prefix": prefix, "suffix": suffix}
result = {
    "schema_version": 1,
    "arithmetic": "exact Python integers",
    "scope": "all endpoint translations gamma=0..width-1 of every integer Sidon ruler of width at most 30; no defect or hole filter",
    "rows": rows,
    "T_F_gt_C_S_failures": total_failures,
    "component_failures": component_failures,
    "prefix_failures": prefix_failures,
    "suffix_failures": suffix_failures,
    "max_T_F_minus_C_S": max_difference,
    "max_component_excess": max_component_excess,
    "min_prefix_slack": min_prefix,
    "min_suffix_slack": min_suffix,
    "first_failure": witness,
}
output = Path(__file__).with_name("unrestricted_ordered_c84_w30.json")
output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
print(json.dumps(result, indent=2))
