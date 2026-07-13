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


p46 = load("p46_p103", ROOT / "problems/864/compute/p46/carry_statistics.py")
p84 = load("p84_p103", ROOT / "problems/864/compute/p84/audit_phase_fourier.py")


P88 = (
    0, 122, 163, 328, 351, 488, 499, 528, 553, 681, 837, 838, 920, 941,
    1051, 1070, 1117, 1322, 1340, 1414, 1449, 1520, 1608, 1613, 1617,
    1715, 1853, 1866, 1925, 2057, 2074, 2153, 2173, 2240, 2320, 2380,
    2475, 2521, 2564, 2596, 2598, 2654, 2788, 2815, 2839, 2901, 2950,
    2958, 3026, 3070, 3076, 3131, 3170, 3184, 3200, 3212, 3215, 3222,
    3248, 3285,
)


def fold_system(B, h):
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
    return folds, triangles


def gf2_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    return len(pivots)


def audit_row(B, h, b):
    differences = {y - x for i, x in enumerate(B) for y in B[i + 1 :]}
    folds, triangles = fold_system(B, h)
    rows = [sum(1 << i for i in ids) for ids in triangles]
    rank = gf2_rank(rows)
    collided = sum(a + c + b in differences for a, c, _u, _v in folds)
    nullity = len(triangles) - rank
    return {
        "C_S": len(folds),
        "T_F": len(triangles),
        "rank_gf2": rank,
        "nullity_gf2": nullity,
        "V_b": collided,
        "matroid_slack": collided - nullity,
        "scalar_slack": len(folds) + collided - len(triangles),
    }


def update_summary(summary, row, witness):
    summary["rows"] += 1
    if row["T_F"]:
        summary["nonzero_triangle_rows"] += 1
    if row["nullity_gf2"]:
        summary["support_dependent_rows"] += 1
        summary["maximum_support_nullity"] = max(
            summary["maximum_support_nullity"], row["nullity_gf2"]
        )
    if row["matroid_slack"] < 0:
        summary["matroid_failures"] += 1
        if summary["first_matroid_failure"] is None:
            summary["first_matroid_failure"] = {**witness, **row}
    if row["scalar_slack"] < 0:
        summary["scalar_failures"] += 1
        if summary["first_scalar_failure"] is None:
            summary["first_scalar_failure"] = {**witness, **row}
    if summary["minimum_matroid_slack"] is None or row["matroid_slack"] < summary["minimum_matroid_slack"]:
        summary["minimum_matroid_slack"] = row["matroid_slack"]
        summary["minimum_matroid_slack_witness"] = {**witness, **row}


def empty_summary():
    return {
        "rows": 0,
        "nonzero_triangle_rows": 0,
        "support_dependent_rows": 0,
        "maximum_support_nullity": 0,
        "matroid_failures": 0,
        "scalar_failures": 0,
        "minimum_matroid_slack": None,
        "minimum_matroid_slack_witness": None,
        "first_matroid_failure": None,
        "first_scalar_failure": None,
    }


def scan_width(max_width):
    summary = empty_summary()
    for width in range(1, max_width + 1):
        for ruler in p46.sidon_rulers(width):
            reflected = tuple(sorted(width - x for x in ruler))
            for gamma in range(width):
                B = tuple(gamma + x for x in reflected)
                h = gamma + width + 1
                for b in (1, 2):
                    update_summary(
                        summary,
                        audit_row(B, h, b),
                        {"width": width, "ruler": ruler, "gamma": gamma, "b": b},
                    )
    return summary


def scan_p88():
    summary = empty_summary()
    for gamma in range(2085):
        B = tuple(x + gamma for x in P88)
        h = 3286 + gamma
        for b in (1, 2):
            update_summary(
                summary,
                audit_row(B, h, b),
                {"gamma": gamma, "b": b},
            )
    return summary


def named_rows():
    archive = json.loads(
        (ROOT / "problems/864/compute/p94/c84_archived_audit.json").read_text(
            encoding="ascii"
        )
    )
    result = {}
    for kind in ("translation", "insertion"):
        record = archive[kind]["max_ratio_row"]
        result[f"P94_{kind}_maximum"] = audit_row(
            tuple(record["B"]), record["h"], record["b"]
        )
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=30)
    parser.add_argument("--skip-p88", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = {
        "schema_version": 1,
        "field": "GF(2)",
        "relation_vector": "incidence vector of the three supporting folds",
        "candidate": "triangle-relation nullity <= V_b",
        "named_literal_hole_rows": named_rows(),
        "width_scan": scan_width(args.max_width),
    }
    if not args.skip_p88:
        result["P88_positive_defect_translations"] = scan_p88()
    rendered = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="ascii")
    print(rendered)


if __name__ == "__main__":
    main()
