from itertools import product
import json


def subsets(n):
    return [
        {i for i in range(n) if mask >> i & 1}
        for mask in range(1, 1 << n)
    ]


def distances(adjacency, start):
    distance = {start: 0}
    queue = [start]
    for vertex in queue:
        for neighbor in adjacency[vertex]:
            if neighbor not in distance:
                distance[neighbor] = distance[vertex] + 1
                queue.append(neighbor)
    return distance


def analyze(neighborhoods, right_count):
    left = list(neighborhoods)
    right = list(range(right_count))
    adjacency = {vertex: set() for vertex in left}
    adjacency.update({vertex: set() for vertex in right})
    for vertex, neighbors in neighborhoods.items():
        for neighbor in neighbors:
            adjacency[vertex].add(neighbor)
            adjacency[neighbor].add(vertex)
    if len(distances(adjacency, left[0])) != len(left) + right_count:
        return None
    pairs = []
    for shore in (left, right):
        for index, first in enumerate(shore):
            first_distance = distances(adjacency, first)
            for second in shore[index + 1:]:
                if first_distance.get(second) == 4:
                    pairs.append((first, second))
    return adjacency, pairs


def n15_gate():
    right_sets = subsets(6)
    shore = set(range(5))
    valid = 0
    maximum = -1
    witness = None
    for endpoint_a in right_sets:
        if 0 not in endpoint_a:
            continue
        for endpoint_b in right_sets:
            if 1 not in endpoint_b:
                continue
            if len(endpoint_a) + len(endpoint_b) != 9:
                continue
            neighborhoods = {
                "v": set(shore),
                "m": set(shore),
                "a": endpoint_a,
                "b": endpoint_b,
            }
            neighborhoods.update({f"w{i}": {5} for i in range(5)})
            analyzed = analyze(neighborhoods, 6)
            if analyzed is None:
                continue
            adjacency, pairs = analyzed
            if any(
                distances(adjacency, "v").get(f"w{i}") != 4
                or distances(adjacency, "m").get(f"w{i}") != 4
                for i in range(5)
            ):
                continue
            valid += 1
            if len(pairs) > maximum:
                maximum = len(pairs)
                witness = {
                    key: sorted(value)
                    for key, value in neighborhoods.items()
                }
    return {"validModels": valid, "maxDistanceFourPairs": maximum,
            "witness": witness}


def n16_10_6_gate():
    right_sets = subsets(6)
    shore = set(range(5))
    valid = 0
    maximum = -1
    witness = None

    for endpoint_a in right_sets:
        if 0 not in endpoint_a:
            continue
        for endpoint_b in right_sets:
            if 1 not in endpoint_b:
                continue
            if len(endpoint_a) + len(endpoint_b) != 8:
                continue
            neighborhoods = {
                "v": set(shore),
                "m": set(shore),
                "a": endpoint_a,
                "b": endpoint_b,
            }
            neighborhoods.update({f"u{i}": {5} for i in range(6)})
            analyzed = analyze(neighborhoods, 6)
            if analyzed is None:
                continue
            adjacency, pairs = analyzed
            if any(
                distances(adjacency, "v").get(f"u{i}") != 4
                or distances(adjacency, "m").get(f"u{i}") != 4
                for i in range(6)
            ):
                continue
            valid += 1
            if len(pairs) > maximum:
                maximum = len(pairs)
                witness = {
                    "case": "k6",
                    "neighbors": {
                        key: sorted(value)
                        for key, value in neighborhoods.items()
                    },
                }

    for endpoint_a in right_sets:
        if 0 not in endpoint_a:
            continue
        for endpoint_b in right_sets:
            if 1 not in endpoint_b:
                continue
            for exceptional in right_sets:
                if (len(endpoint_a) + len(endpoint_b)
                        + len(exceptional) != 9):
                    continue
                neighborhoods = {
                    "v": set(shore),
                    "m": set(shore),
                    "a": endpoint_a,
                    "b": endpoint_b,
                    "c": exceptional,
                }
                neighborhoods.update({f"u{i}": {5} for i in range(5)})
                analyzed = analyze(neighborhoods, 6)
                if analyzed is None:
                    continue
                adjacency, pairs = analyzed
                if any(
                    distances(adjacency, "v").get(f"u{i}") != 4
                    or distances(adjacency, "m").get(f"u{i}") != 4
                    for i in range(5)
                ):
                    continue
                if (distances(adjacency, "v").get("c") == 4
                        or distances(adjacency, "m").get("c") == 4):
                    continue
                valid += 1
                if len(pairs) > maximum:
                    maximum = len(pairs)
                    witness = {
                        "case": "k5",
                        "neighbors": {
                            key: sorted(value)
                            for key, value in neighborhoods.items()
                        },
                    }
    return {"validModels": valid, "maxDistanceFourPairs": maximum,
            "witness": witness}


def n16_9_7_gate():
    shore = set(range(5))
    right = list(range(7))
    disjoint_endpoint_pairs = []
    for mask_a in range(1 << 7):
        endpoint_a = {r for r in right if mask_a >> r & 1}
        if 0 not in endpoint_a:
            continue
        remaining = [r for r in right if r not in endpoint_a]
        for mask_b in range(1 << len(remaining)):
            endpoint_b = {
                remaining[j]
                for j in range(len(remaining))
                if mask_b >> j & 1
            }
            if 1 in endpoint_b:
                disjoint_endpoint_pairs.append((endpoint_a, endpoint_b))

    valid = 0
    with_w_root_distance_four = 0
    maximum = -1
    witness = None
    for kinds in product((1, 2, 3), repeat=5):
        w_neighbors = [
            {5} if kind == 1 else {6} if kind == 2 else {5, 6}
            for kind in kinds
        ]
        w_degree_sum = sum(map(len, w_neighbors))
        for endpoint_a, endpoint_b in disjoint_endpoint_pairs:
            if len(endpoint_a) + len(endpoint_b) + w_degree_sum != 14:
                continue
            neighborhoods = {
                "v": set(shore),
                "m": set(shore),
                "a": endpoint_a,
                "b": endpoint_b,
            }
            neighborhoods.update({
                f"w{i}": w_neighbors[i] for i in range(5)
            })
            analyzed = analyze(neighborhoods, 7)
            if analyzed is None:
                continue
            adjacency, pairs = analyzed
            if any(
                distances(adjacency, "v").get(f"w{i}") != 4
                or distances(adjacency, "m").get(f"w{i}") != 4
                for i in range(5)
            ):
                continue
            if distances(adjacency, "a").get("b") != 4:
                continue
            valid += 1
            if any(
                distances(adjacency, f"w{i}").get(root) == 4
                for i in range(5) for root in ("a", "b")
            ):
                with_w_root_distance_four += 1
            if len(pairs) > maximum:
                maximum = len(pairs)
                witness = {
                    key: sorted(value)
                    for key, value in neighborhoods.items()
                }
    return {
        "validModels": valid,
        "maxDistanceFourPairs": maximum,
        "modelsWithWRootDistanceFour": with_w_root_distance_four,
        "witness": witness,
    }


print(json.dumps({
    "scope": "derived bipartite neighborhood models, not full circuit enumeration",
    "n15_9_6": n15_gate(),
    "n16_10_6": n16_10_6_gate(),
    "n16_9_7": n16_9_7_gate(),
}, sort_keys=True, indent=2))
