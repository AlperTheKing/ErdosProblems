import argparse
import importlib.util
import json
from collections import defaultdict
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
    "p124_weighted",
    ROOT / "problems/864/compute/p103/audit_weighted_relations.py",
)
frontier = load(
    "p124_frontier",
    ROOT / "problems/864/compute/p110/audit_weighted_frontier.py",
)


def sign(value):
    if value == 0:
        raise AssertionError("P83 signed difference vanished")
    return 1 if value > 0 else -1


def chamber_key(folds, triangle):
    f0, fz, fx = triangle
    a, c, r, _s = folds[f0]
    same_a, z, u, w = folds[fz]
    x, same_c, same_u, y = folds[fx]
    assert (same_a, same_c, same_u) == (a, c, u)
    X = x - a
    Z = z - c
    R = r - u
    assert R + X == y - folds[f0][3]
    assert R + Z == w - folds[f0][3]
    assert Z - X == w - y
    return tuple(map(sign, (X, Z, R, R + X, R + Z, Z - X)))


def truncated_rank(rows, limit):
    return weighted.sparse_rank(
        ({column: value for column, value in row.items() if column < limit} for row in rows),
        PRIME,
    )


def audit_system(system, retain_classes=False):
    B, h = system
    folds, triangles, rows = weighted.relation_rows(B, h, 1)
    C = len(folds)
    p = len(B)
    groups = defaultdict(list)
    for index, triangle in enumerate(triangles):
        groups[chamber_key(folds, triangle)].append(index)

    records = []
    failure = None
    for key in sorted(groups):
        indices = groups[key]
        support_rank = weighted.p103.gf2_rank(
            [sum(1 << fold for fold in triangles[index]) for index in indices]
        )
        relation_rank = support_rank
        if support_rank < len(indices):
            relation_rank = truncated_rank((rows[index] for index in indices), C + 2 * p)
        record = {
            "signs": key,
            "triangles": len(indices),
            "support_rank": support_rank,
            "relation_rank": relation_rank,
        }
        if retain_classes:
            records.append(record)
        if relation_rank < len(indices) and failure is None:
            failure = record

    result = {
        "B": B if retain_classes else None,
        "h": h,
        "p": p,
        "C_S": C,
        "T_F": len(triangles),
        "chambers": len(groups),
        "support_dependent_chambers": sum(
            record["support_rank"] < record["triangles"] for record in records
        ) if retain_classes else None,
        "failure": failure,
    }
    if retain_classes:
        result["classes"] = records
    return result


def dense_rows(path):
    payload = json.loads(path.read_text(encoding="ascii"))
    for record in payload["failures"]:
        yield tuple(record["B"]), record["h"]


def chunked(values, size=128):
    chunk = []
    for value in values:
        chunk.append(value)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def audit_chunk(chunk):
    out = {
        "systems": 0,
        "systems_with_triangles": 0,
        "chambers": 0,
        "support_dependent_chambers": 0,
        "relation_failures": 0,
        "first_failure": None,
    }
    for system in chunk:
        row = audit_system(system, retain_classes=True)
        out["systems"] += 1
        out["systems_with_triangles"] += row["T_F"] > 0
        out["chambers"] += row["chambers"]
        out["support_dependent_chambers"] += row["support_dependent_chambers"]
        if row["failure"] is not None:
            out["relation_failures"] += 1
            if out["first_failure"] is None:
                out["first_failure"] = {
                    "B": row["B"],
                    "h": row["h"],
                    **row["failure"],
                }
    return out


def merge(left, right):
    for key in (
        "systems",
        "systems_with_triangles",
        "chambers",
        "support_dependent_chambers",
        "relation_failures",
    ):
        left[key] += right[key]
    if left["first_failure"] is None:
        left["first_failure"] = right["first_failure"]
    return left


def audit_domain(values, workers):
    summary = {
        "systems": 0,
        "systems_with_triangles": 0,
        "chambers": 0,
        "support_dependent_chambers": 0,
        "relation_failures": 0,
        "first_failure": None,
    }
    chunks = chunked(values)
    if workers == 1:
        for row in map(audit_chunk, chunks):
            merge(summary, row)
        return summary
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for row in pool.map(audit_chunk, chunks, chunksize=1):
            merge(summary, row)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--dense", type=Path)
    parser.add_argument(
        "--domains",
        nargs="*",
        choices=(
            "embedded",
            "p98_subsets",
            "p94_deletions",
            "p105_translations",
            "p105_deletions",
            "p86_bases",
            "p86_translations",
        ),
        default=(),
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        raise ValueError("workers must be in [1,64]")

    generators = {
        "embedded": frontier.embedded_rows,
        "p98_subsets": frontier.p98_subsets,
        "p94_deletions": frontier.p94_deletions,
        "p105_translations": frontier.p105_translations,
        "p105_deletions": frontier.p105_deletions,
        "p86_bases": frontier.p86_bases,
        "p86_translations": frontier.p86_translations,
    }
    result = {
        "schema_version": 1,
        "field": f"GF({PRIME})",
        "candidate": "within each sign chamber of X,Z,R,R+X,R+Z,Z-X, (support,L1,L2) rows are independent",
        "conditional_consequence": "T_F <= 24(C_S+2p)",
        "domains": {},
    }
    if args.dense:
        records = [audit_system(system, retain_classes=True) for system in dense_rows(args.dense)]
        result["dense"] = {
            "systems": len(records),
            "chambers": sum(row["chambers"] for row in records),
            "support_dependent_chambers": sum(
                row["support_dependent_chambers"] for row in records
            ),
            "relation_failures": sum(row["failure"] is not None for row in records),
            "records": records,
        }
    for name in args.domains:
        result["domains"][name] = audit_domain(generators[name](), args.workers)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps({key: value for key, value in result.items() if key != "dense"}, indent=2))
    if "dense" in result:
        print(json.dumps({key: value for key, value in result["dense"].items() if key != "records"}, indent=2))


if __name__ == "__main__":
    main()
