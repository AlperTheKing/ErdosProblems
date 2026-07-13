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


p103 = load(
    "p103_relations",
    ROOT / "problems/864/compute/p103/audit_relation_matroid.py",
)


def sparse_rank(rows, prime=PRIME):
    # Reduce against every previously chosen pivot before storing a new row.
    # Stopping at the first column without a pivot is incorrect when the row
    # still contains lower-indexed old pivots: it can overstate the rank.
    pivots = []
    for source in rows:
        row = {column: value % prime for column, value in source.items() if value % prime}
        for pivot, pivot_row in pivots:
            value = row.get(pivot, 0)
            if not value:
                continue
            for column, coefficient in pivot_row.items():
                row[column] = (row.get(column, 0) - value * coefficient) % prime
                if row[column] == 0:
                    del row[column]
        if row:
            pivot = max(row)
            inverse = pow(row[pivot], -1, prime)
            pivots.append(
                (
                    pivot,
                    {
                        column: (coefficient * inverse) % prime
                        for column, coefficient in row.items()
                    },
                )
            )
    return len(pivots)


def add_relation(row, offset, mark_index, terms, weight=1):
    for mark, sign in terms:
        column = offset + mark_index[mark]
        row[column] = row.get(column, 0) + weight * sign


def relation_rows(B, h, b):
    folds, triangles = p103.fold_system(B, h)
    mark_index = {mark: index for index, mark in enumerate(B)}
    fold_count = len(folds)
    p = len(B)
    rows = []
    for f0, fz, fx in triangles:
        a, c, r, s = folds[f0]
        same_a, z, u, w = folds[fz]
        x, same_c, same_u, y = folds[fx]
        assert (same_a, same_c, same_u) == (a, c, u)

        # These are the formal mark relations q(Fz)-q(Fx) and q(F0)-q(Fz).
        relation_1 = ((a, 1), (z, 1), (y, 1), (x, -1), (c, -1), (w, -1))
        relation_2 = ((c, 1), (u, 1), (w, 1), (z, -1), (r, -1), (s, -1))
        phase = a + c + b
        row = {f0: 1, fz: 1, fx: 1}
        add_relation(row, fold_count, mark_index, relation_1)
        add_relation(row, fold_count + p, mark_index, relation_2)
        add_relation(row, fold_count + 2 * p, mark_index, relation_1, phase)
        add_relation(row, fold_count + 3 * p, mark_index, relation_2, phase)
        rows.append(row)
    return folds, triangles, rows


def audit_row(B, h, b):
    folds, triangles, rows = relation_rows(B, h, b)
    rank = sparse_rank(rows)
    return {
        "p": len(B),
        "C_S": len(folds),
        "T_F": len(triangles),
        "ambient_dimension": len(folds) + 4 * len(B),
        "weighted_rank": rank,
        "weighted_nullity": len(triangles) - rank,
    }


def p88_worker(gamma):
    B = tuple(mark + gamma for mark in p103.P88)
    h = 3286 + gamma
    support = p103.audit_row(B, h, 1)
    if support["nullity_gf2"] == 0:
        row = {
            "p": len(B),
            "C_S": support["C_S"],
            "T_F": support["T_F"],
            "ambient_dimension": support["C_S"] + 4 * len(B),
            "weighted_rank": support["T_F"],
            "weighted_nullity": 0,
        }
    else:
        row = audit_row(B, h, 1)
    return gamma, support["nullity_gf2"] > 0, row


def p88_scan(workers):
    failures = 0
    first_failure = None
    minimum_slack = None
    minimum_row = None
    dependent_support_rows = 0
    if workers == 1:
        records = map(p88_worker, range(2085))
    else:
        pool = ProcessPoolExecutor(max_workers=workers)
        records = pool.map(p88_worker, range(2085), chunksize=4)
    for gamma, support_dependent, row in records:
        # Changing b translates the weighted blocks by the unweighted blocks,
        # so b=1 and b=2 have the same rank.
        dependent_support_rows += support_dependent
        slack = row["weighted_rank"] - row["T_F"]
        if minimum_slack is None or slack < minimum_slack:
            minimum_slack = slack
            minimum_row = {"gamma": gamma, **row}
        if slack < 0:
            failures += 1
            if first_failure is None:
                first_failure = {"gamma": gamma, **row}
    if workers != 1:
        pool.shutdown()
    return {
        "fold_systems": 2085,
        "represented_b_rows": 4170,
        "support_dependent_systems": dependent_support_rows,
        "weighted_rank_failures": failures,
        "minimum_rank_slack": minimum_slack,
        "minimum_rank_slack_row": minimum_row,
        "first_failure": first_failure,
    }


def named_rows():
    p75 = (
        3, 5, 69, 169, 211, 223, 251, 329, 373, 403, 409, 501, 505, 519,
        631, 639, 689, 715, 775, 863, 883, 915, 931, 953, 977, 987,
    )
    archive = json.loads(
        (ROOT / "problems/864/compute/p94/c84_archived_audit.json").read_text(
            encoding="ascii"
        )
    )
    rows = {"P75": audit_row(p75, 988, 1)}
    for kind in ("translation", "insertion"):
        record = archive[kind]["max_ratio_row"]
        rows[f"P94_{kind}_maximum"] = audit_row(
            tuple(record["B"]), record["h"], record["b"]
        )
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-p88", action="store_true")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        raise ValueError("workers must be in [1,64]")
    result = {
        "schema_version": 1,
        "field": f"GF({PRIME})",
        "vector": "support incidence plus L1,L2,d*L1,d*L2 in four mark blocks",
        "conditional_consequence": "full row rank implies T_F <= C_S + 4p",
        "named_rows": named_rows(),
    }
    if not args.skip_p88:
        result["P88_positive_defect_translations"] = p88_scan(args.workers)
    rendered = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="ascii")
    print(rendered)


if __name__ == "__main__":
    main()
