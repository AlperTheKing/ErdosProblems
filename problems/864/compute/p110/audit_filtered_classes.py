import argparse
import importlib.util
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PRIME = 1_000_003


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


weighted = load(
    "p103_weighted_filtered_p110",
    ROOT / "problems/864/compute/p103/audit_weighted_relations.py",
)


def rank(rows, limit=None):
    if limit is None:
        return weighted.sparse_rank(rows, PRIME)
    return weighted.sparse_rank(
        ({column: value for column, value in row.items() if column < limit} for row in rows),
        PRIME,
    )


def minimum_weight_row(row, C, p, minimum_label):
    out = {column: value for column, value in row.items() if column < C + 2 * p}
    for column, value in row.items():
        if C <= column < C + p:
            out[column + 2 * p] = minimum_label * value
        elif C + p <= column < C + 2 * p:
            out[column + 2 * p] = minimum_label * value
    return out


def audit_system(record):
    B = tuple(record["B"])
    h = record["h"]
    folds, triangles, rows = weighted.relation_rows(B, h, 1)
    C = len(folds)
    p = len(B)
    labels = [a + c + 1 for a, c, _u, _v in folds]
    classes = []
    for role in range(3):
        indices = [
            index
            for index, ids in enumerate(triangles)
            if min(range(3), key=lambda position: labels[ids[position]]) == role
        ]
        class_rows = [rows[index] for index in indices]
        support_rank_gf2 = weighted.p103.gf2_rank(
            [sum(1 << fold for fold in triangles[index]) for index in indices]
        )
        support_rank = support_rank_gf2
        if support_rank_gf2 < len(indices):
            support_rank = rank(class_rows, C)
        unweighted_rank = support_rank
        original_weighted_rank = support_rank
        minimum_weighted_rank = support_rank
        if support_rank < len(indices):
            unweighted_rank = rank(class_rows, C + 2 * p)
            original_weighted_rank = unweighted_rank
            minimum_weighted_rank = unweighted_rank
        if unweighted_rank < len(indices):
            original_weighted_rank = rank(class_rows)
            minimum_rows = [
                minimum_weight_row(rows[index], C, p, labels[triangles[index][role]])
                for index in indices
            ]
            minimum_weighted_rank = rank(minimum_rows)
        multiplicity = {}
        for index in indices:
            fold = triangles[index][role]
            multiplicity[fold] = multiplicity.get(fold, 0) + 1
        classes.append(
            {
                "minimum_role": role,
                "triangles": len(indices),
                "ambient_dimension": C + 4 * p,
                "support_rank": support_rank,
                "unweighted_rank": unweighted_rank,
                "original_weighted_rank": original_weighted_rank,
                "minimum_weighted_rank": minimum_weighted_rank,
                "maximum_same_base": max(multiplicity.values(), default=0),
            }
        )
    return {
        "sha256": record["sha256"],
        "p": p,
        "h": h,
        "C_S": C,
        "T_F": len(triangles),
        "classes": classes,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=16)
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        raise ValueError("workers must be in [1,64]")
    payload = json.loads(args.input.read_text(encoding="ascii"))
    if args.workers == 1:
        systems = [audit_system(record) for record in payload["failures"]]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            systems = list(pool.map(audit_system, payload["failures"], chunksize=1))
    result = {
        "schema_version": 1,
        "field": f"GF({PRIME})",
        "systems": len(systems),
        "class_rows": 3 * len(systems),
        "support_failures": sum(
            row["support_rank"] < row["triangles"]
            for system in systems
            for row in system["classes"]
        ),
        "unweighted_failures": sum(
            row["unweighted_rank"] < row["triangles"]
            for system in systems
            for row in system["classes"]
        ),
        "original_weighted_failures": sum(
            row["original_weighted_rank"] < row["triangles"]
            for system in systems
            for row in system["classes"]
        ),
        "minimum_weighted_failures": sum(
            row["minimum_weighted_rank"] < row["triangles"]
            for system in systems
            for row in system["classes"]
        ),
        "maximum_same_base": max(
            row["maximum_same_base"] for system in systems for row in system["classes"]
        ),
        "records": systems,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps({key: value for key, value in result.items() if key != "records"}, indent=2))


if __name__ == "__main__":
    main()
