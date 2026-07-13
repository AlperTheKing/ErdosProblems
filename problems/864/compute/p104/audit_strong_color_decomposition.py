import argparse
import importlib.util
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


p46 = load("p46_p104", ROOT / "problems/864/compute/p46/carry_statistics.py")
p84 = load("p84_p104", ROOT / "problems/864/compute/p84/audit_phase_fourier.py")

P88 = (
    0, 122, 163, 328, 351, 488, 499, 528, 553, 681, 837, 838, 920, 941,
    1051, 1070, 1117, 1322, 1340, 1414, 1449, 1520, 1608, 1613, 1617,
    1715, 1853, 1866, 1925, 2057, 2074, 2153, 2173, 2240, 2320, 2380,
    2475, 2521, 2564, 2596, 2598, 2654, 2788, 2815, 2839, 2901, 2950,
    2958, 3026, 3070, 3076, 3131, 3170, 3184, 3200, 3212, 3215, 3222,
    3248, 3285,
)


def component_excess(vertex_count, edges):
    adjacency = [[] for _ in range(vertex_count)]
    for edge_id, (left, right) in enumerate(edges):
        adjacency[left].append((right, edge_id))
        adjacency[right].append((left, edge_id))
    seen = set()
    excesses = []
    for start in range(vertex_count):
        if start in seen or not adjacency[start]:
            continue
        stack = [start]
        seen.add(start)
        vertices = edge_ids = 0
        while stack:
            vertex = stack.pop()
            vertices += 1
            edge_ids += len(adjacency[vertex])
            for neighbor, _edge_id in adjacency[vertex]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        excesses.append(edge_ids // 2 - vertices)
    return max(excesses, default=-1)


def audit_row(B, h, b):
    folds = p84.canonical_folds(B, h)
    differences = {y - x for i, x in enumerate(B) for y in B[i + 1:]}
    low_edges = {(a, c): (u, a + c + b in differences) for a, c, u, _v in folds}
    by_color = defaultdict(list)
    for a, c, u, _v in folds:
        by_color[u].append((a, c))

    worst_bound = None
    worst_pseudoforest = None
    positive_color_excess = 0
    for color, matching in by_color.items():
        left = {a: i for i, (a, _c) in enumerate(matching)}
        right = {c: len(left) + i for i, (_a, c) in enumerate(matching)}
        induced = []
        induced_without_collided_matching = []
        matching_set = set(matching)
        collided_matching = {
            edge for edge in matching if low_edges[edge][1]
        }
        for edge in low_edges:
            a, c = edge
            if a not in left or c not in right:
                continue
            encoded = (left[a], right[c])
            induced.append(encoded)
            if edge not in collided_matching:
                induced_without_collided_matching.append(encoded)
        bound_residual = len(induced) - 2 * len(matching) - len(collided_matching)
        positive_color_excess += max(0, len(induced) - 2 * len(matching))
        pseudoforest_residual = component_excess(
            2 * len(matching), induced_without_collided_matching
        )
        key = (bound_residual, color, len(matching), len(induced), len(collided_matching))
        if worst_bound is None or key > worst_bound:
            worst_bound = key
        pkey = (pseudoforest_residual, color, len(matching), len(induced), len(collided_matching))
        if worst_pseudoforest is None or pkey > worst_pseudoforest:
            worst_pseudoforest = pkey

    return {
        "folds": len(folds),
        "collisions": sum(collided for _color, collided in low_edges.values()),
        "positive_color_excess": positive_color_excess,
        "pooled_residual": positive_color_excess - sum(
            collided for _color, collided in low_edges.values()
        ),
        "worst_bound": worst_bound,
        "worst_pseudoforest": worst_pseudoforest,
    }


def scan(max_width, include_p88):
    rows = bound_failures = pseudoforest_failures = pooled_failures = 0
    worst_bound = None
    worst_pseudoforest = None

    def consume(B, h, b, source):
        nonlocal rows, bound_failures, pseudoforest_failures, pooled_failures
        nonlocal worst_bound, worst_pseudoforest
        rows += 1
        result = audit_row(B, h, b)
        bound = result["worst_bound"]
        pseudo = result["worst_pseudoforest"]
        if bound is not None and bound[0] > 0:
            bound_failures += 1
        if pseudo is not None and pseudo[0] > 0:
            pseudoforest_failures += 1
        if result["pooled_residual"] > 0:
            pooled_failures += 1
        bound_record = (bound[0] if bound else -10**9, source, b, result)
        pseudo_record = (pseudo[0] if pseudo else -10**9, source, b, result)
        if worst_bound is None or bound_record[0] > worst_bound[0]:
            worst_bound = bound_record
        if worst_pseudoforest is None or pseudo_record[0] > worst_pseudoforest[0]:
            worst_pseudoforest = pseudo_record

    for width in range(1, max_width + 1):
        for ruler in p46.sidon_rulers(width):
            reflected = tuple(sorted(width - x for x in ruler))
            for gamma in range(width):
                B = tuple(gamma + x for x in reflected)
                h = gamma + width + 1
                for b in (1, 2):
                    consume(B, h, b, {"domain": "width", "width": width, "gamma": gamma, "B": B})

    if include_p88:
        for gamma in range(2085):
            B = tuple(x + gamma for x in P88)
            h = 3286 + gamma
            for b in (1, 2):
                consume(B, h, b, {"domain": "P88", "gamma": gamma})

    return {
        "rows": rows,
        "bound_failures": bound_failures,
        "pseudoforest_failures": pseudoforest_failures,
        "pooled_failures": pooled_failures,
        "worst_bound": worst_bound,
        "worst_pseudoforest": worst_pseudoforest,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=30)
    parser.add_argument("--skip-p88", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = scan(args.max_width, not args.skip_p88)
    encoded = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="ascii")
    print(encoded)


if __name__ == "__main__":
    main()
