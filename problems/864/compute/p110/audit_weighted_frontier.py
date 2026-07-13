import argparse
import importlib.util
import itertools
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PRIME = 1_000_003
P98_SOURCE = (0, 6, 22, 24, 56, 95, 137, 146, 172, 173, 201, 258, 273, 306, 311, 365, 369)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


weighted = load(
    "p103_weighted_p110",
    ROOT / "problems/864/compute/p103/audit_weighted_relations.py",
)
sys.path.insert(0, str(ROOT / "problems/864/compute/p86"))
import dense_loose_search as p86


def normalized(values):
    values = tuple(values)
    low = min(values)
    return tuple(sorted(value - low for value in values))


def p98_subsets():
    seen = set()
    size = len(P98_SOURCE)
    for mask in range(1, 1 << size):
        if mask.bit_count() < 3:
            continue
        raw = tuple(P98_SOURCE[index] for index in range(size) if mask & (1 << index))
        for oriented in (
            normalized(raw),
            normalized(raw[-1] - value for value in raw),
        ):
            if oriented in seen:
                continue
            seen.add(oriented)
            yield oriented, oriented[-1] + 1


def p94_deletions():
    payload = json.loads(
        (ROOT / "problems/864/compute/p94/c84_archived_audit.json").read_text(
            encoding="ascii"
        )
    )
    row = payload["translation"]["max_ratio_row"]
    B = tuple(row["B"])
    h = row["h"]
    for count in (1, 2):
        for deleted in itertools.combinations(range(len(B) - 1), count):
            deleted = set(deleted)
            yield tuple(value for index, value in enumerate(B) if index not in deleted), h


def p105_source():
    payload = json.loads(
        (ROOT / "problems/864/compute/p105/corrected_c84_falsifier.json").read_text(
            encoding="ascii"
        )
    )
    row = payload["subset_search"]["source_subset"]
    return tuple(row["B"]), row["h"]


def p105_translations():
    B, h = p105_source()
    for gamma in range(1560):
        yield tuple(value + gamma for value in B), h + gamma


def p105_deletions():
    B, h = p105_source()
    for count in (1, 2, 3):
        for deleted in itertools.combinations(range(len(B) - 1), count):
            deleted = set(deleted)
            yield tuple(value for index, value in enumerate(B) if index not in deleted), h


def p86_bases():
    bases, _manifests = p86.load_archives()
    for base in bases:
        yield base.values, base.values[-1] + 1


def p86_translations():
    bases, _manifests = p86.load_archives()
    for base in bases:
        B = base.values
        p = len(B)
        width = B[-1]
        baseline = (3 * p * p - p + 2) // 2
        max_gamma = min(width - 1, baseline - width - 2)
        for gamma in range(max_gamma + 1):
            yield tuple(value + gamma for value in B), width + gamma + 1


def embedded_rows():
    paths = (
        ROOT / "problems/864/compute/p98/transformed_parent.json",
        ROOT / "problems/864/compute/p98/tight_mutations.json",
        ROOT / "problems/864/compute/p98/unrestricted_corrected_H31_H40.json",
        ROOT / "problems/864/compute/p98/cpsat_H31_H32.json",
        ROOT / "problems/864/compute/p98/cpsat_H33_H40.json",
        ROOT / "problems/864/compute/p105/corrected_c84_falsifier.json",
        ROOT / "problems/864/compute/p106/p105_minimal_hall.json",
    )
    seen = set()

    def walk(value):
        if isinstance(value, dict):
            B = value.get("B")
            h = value.get("h")
            if (
                isinstance(B, list)
                and len(B) >= 3
                and all(isinstance(mark, int) for mark in B)
                and isinstance(h, int)
            ):
                key = (tuple(B), h)
                if key not in seen:
                    seen.add(key)
                    yield key
            for child in value.values():
                yield from walk(child)
        elif isinstance(value, list):
            for child in value:
                yield from walk(child)

    for path in paths:
        yield from walk(json.loads(path.read_text(encoding="ascii")))


def rank_rows(rows, column_limit=None):
    if column_limit is None:
        return weighted.sparse_rank(rows, PRIME)
    return weighted.sparse_rank(
        ({column: value for column, value in row.items() if column < column_limit} for row in rows),
        PRIME,
    )


def audit_system(system):
    B, h = system
    folds, triangles = weighted.p103.fold_system(B, h)
    C = len(folds)
    T = len(triangles)
    p = len(B)
    dimension_failure = T > C + 4 * p
    support_rank = None
    unweighted_rank = None
    weighted_rank = None
    if not dimension_failure:
        _folds, _triangles, rows = weighted.relation_rows(B, h, 1)
        assert (_folds, _triangles) == (folds, triangles)
        support_bits = [sum(1 << fold for fold in ids) for ids in triangles]
        support_rank_gf2 = weighted.p103.gf2_rank(support_bits)
        support_rank = support_rank_gf2
        unweighted_rank = support_rank
        weighted_rank = support_rank
        if support_rank_gf2 < T:
            support_rank = rank_rows(rows, C)
            unweighted_rank = support_rank
            weighted_rank = support_rank
        if support_rank < T:
            unweighted_rank = rank_rows(rows, C + 2 * p)
            weighted_rank = unweighted_rank
            if unweighted_rank < T:
                weighted_rank = rank_rows(rows)

    labels = [a + c + 1 for a, c, _u, _v in folds]
    minimum_classes = [0, 0, 0]
    base_multiplicity = {}
    for ids in triangles:
        role = min(range(3), key=lambda index: labels[ids[index]])
        minimum_classes[role] += 1
        key = (role, ids[role])
        base_multiplicity[key] = base_multiplicity.get(key, 0) + 1
    return {
        "B": B,
        "h": h,
        "p": p,
        "C_S": C,
        "T_F": T,
        "ambient_dimension": C + 4 * p,
        "dimension_failure": dimension_failure,
        "support_rank": support_rank,
        "unweighted_rank": unweighted_rank,
        "weighted_rank": weighted_rank,
        "minimum_classes": minimum_classes,
        "maximum_same_minimum_fold": max(base_multiplicity.values(), default=0),
    }


def empty_summary():
    return {
        "systems": 0,
        "with_triangles": 0,
        "support_dependent": 0,
        "unweighted_dependent": 0,
        "dimension_failures": 0,
        "weighted_failures": 0,
        "maximum_T_F": 0,
        "maximum_same_minimum_fold": 0,
        "maximum_dimension_excess": 0,
        "smallest_dimension_failure": None,
        "strongest_dimension_failure": None,
        "first_weighted_failure": None,
    }


def add_row(summary, row):
    summary["systems"] += 1
    summary["with_triangles"] += row["T_F"] > 0
    summary["support_dependent"] += (
        row["support_rank"] is None or row["support_rank"] < row["T_F"]
    )
    summary["unweighted_dependent"] += (
        row["unweighted_rank"] is None or row["unweighted_rank"] < row["T_F"]
    )
    summary["dimension_failures"] += row["dimension_failure"]
    failed = row["dimension_failure"] or row["weighted_rank"] < row["T_F"]
    summary["weighted_failures"] += failed
    summary["maximum_T_F"] = max(summary["maximum_T_F"], row["T_F"])
    summary["maximum_same_minimum_fold"] = max(
        summary["maximum_same_minimum_fold"], row["maximum_same_minimum_fold"]
    )
    if row["dimension_failure"]:
        excess = row["T_F"] - row["ambient_dimension"]
        if summary["smallest_dimension_failure"] is None or (
            row["p"], row["h"], row["B"]
        ) < (
            summary["smallest_dimension_failure"]["p"],
            summary["smallest_dimension_failure"]["h"],
            summary["smallest_dimension_failure"]["B"],
        ):
            summary["smallest_dimension_failure"] = row
        if excess > summary["maximum_dimension_excess"]:
            summary["maximum_dimension_excess"] = excess
            summary["strongest_dimension_failure"] = row
    if failed and summary["first_weighted_failure"] is None:
        summary["first_weighted_failure"] = row


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
    summary = empty_summary()
    for system in chunk:
        add_row(summary, audit_system(system))
    return summary


def merge(left, right):
    for key in (
        "systems",
        "with_triangles",
        "support_dependent",
        "unweighted_dependent",
        "dimension_failures",
        "weighted_failures",
    ):
        left[key] += right[key]
    for key in ("maximum_T_F", "maximum_same_minimum_fold", "maximum_dimension_excess"):
        left[key] = max(left[key], right[key])
    for key in ("smallest_dimension_failure", "strongest_dimension_failure"):
        candidate = right[key]
        if candidate is None:
            continue
        current = left[key]
        if key == "smallest_dimension_failure":
            better = current is None or (candidate["p"], candidate["h"], candidate["B"]) < (
                current["p"], current["h"], current["B"]
            )
        else:
            better = current is None or (
                candidate["T_F"] - candidate["ambient_dimension"]
                > current["T_F"] - current["ambient_dimension"]
            )
        if better:
            left[key] = candidate
    if left["first_weighted_failure"] is None:
        left["first_weighted_failure"] = right["first_weighted_failure"]
    return left


def audit_domain(values, workers):
    summary = empty_summary()
    chunks = chunked(values)
    if workers == 1:
        records = map(audit_chunk, chunks)
        for record in records:
            merge(summary, record)
        return summary
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for record in pool.map(audit_chunk, chunks, chunksize=1):
            merge(summary, record)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--domains",
        nargs="+",
        choices=(
            "embedded",
            "p98_subsets",
            "p94_deletions",
            "p105_translations",
            "p105_deletions",
            "p86_bases",
            "p86_translations",
        ),
        default=("embedded", "p98_subsets", "p94_deletions", "p105_translations", "p105_deletions"),
    )
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        raise ValueError("workers must be in [1,64]")
    generators = {
        "embedded": embedded_rows,
        "p98_subsets": p98_subsets,
        "p94_deletions": p94_deletions,
        "p105_translations": p105_translations,
        "p105_deletions": p105_deletions,
        "p86_bases": p86_bases,
        "p86_translations": p86_translations,
    }
    result = {
        "schema_version": 1,
        "field": f"GF({PRIME})",
        "weighted_vector": "support,L1,L2,dL1,dL2",
        "domains": {},
    }
    for name in args.domains:
        result["domains"][name] = audit_domain(generators[name](), args.workers)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
