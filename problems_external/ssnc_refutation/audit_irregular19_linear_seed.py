"""Independent finite audit of IRREGULAR19_INCIDENCE_SEED.json.

The stored orientation is deliberately ignored.  Only the missing graph and
declared root-incidence data are read.  The audit checks the coarse seed and
then emits the singleton-fibre contradictions forced by saturation.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path


SEED = Path(__file__).with_name("IRREGULAR19_INCIDENCE_SEED.json")
raw = SEED.read_bytes()
data = json.loads(raw)

n = data["n"]
missing = {tuple(sorted(edge)) for edge in data["missing_graph"]["edges"]}
blocks = [tuple(block) for block in data["incidence"]["root_blocks_by_target"]]
declared_rows = [
    tuple(row) for row in data["incidence"]["declared_unreachable_targets_by_source"]
]

degrees = [sum(v in edge for edge in missing) for v in range(n)]
mu = data["missing_graph"]["expected_degree_by_vertex"]
expected_sizes = data["incidence"]["expected_target_sizes"]
transpose_rows = [tuple(u for u, block in enumerate(blocks) if v in block) for v in range(n)]

assert sha256(raw).hexdigest().upper() == (
    "B4BFB3000D9F14E7C763764DDF474FECD166DE12CC7F96B9D593F8801DF5EF69"
)
assert degrees == mu
assert [len(block) for block in blocks] == expected_sizes
assert expected_sizes == [2 * degree - 1 for degree in mu]
assert transpose_rows == declared_rows
assert all(len(row) == 3 for row in transpose_rows)
assert all(u not in blocks[u] for u in range(n))

missing_inside = {
    u: tuple(edge for edge in sorted(missing) if set(edge) <= set(blocks[u]))
    for u in range(n)
}
assert not any(missing_inside.values())

intersection_histogram: Counter[int] = Counter()
maximum_intersection = 0
for u in range(n):
    for w in range(u + 1, n):
        size = len(set(blocks[u]) & set(blocks[w]))
        intersection_histogram[size] += 1
        maximum_intersection = max(maximum_intersection, size)


singletons = {u: block[0] for u, block in enumerate(blocks) if len(block) == 1}
root_to_targets: dict[int, list[int]] = defaultdict(list)
for target, root in singletons.items():
    root_to_targets[root].append(target)
duplicates = {
    root: tuple(targets)
    for root, targets in root_to_targets.items()
    if len(targets) >= 2
}

two_cycles = []
for u, v in singletons.items():
    if u < v and singletons.get(v) == u:
        two_cycles.append((u, v))

print(f"seed_sha256={sha256(raw).hexdigest().upper()}")
print(f"missing_degrees={degrees}")
print(f"block_sizes={[len(block) for block in blocks]}")
print(f"source_sizes={[len(row) for row in transpose_rows]}")
print(f"missing_inside_blocks={sum(map(len, missing_inside.values()))}")
print(f"intersection_histogram={dict(sorted(intersection_histogram.items()))}")
print(f"maximum_intersection={maximum_intersection}")
print(f"singleton_map={singletons}")
print(f"duplicate_singleton_roots={duplicates}")
print(f"singleton_two_cycles={two_cycles}")

assert duplicates
assert (15, 18) in two_cycles

# For a singleton two-cycle u<->v, the two exact row-potential equations sum
# to M_u + M_v = e_u + e_v.  Print the nonzero residual for the fixed seed.
for u, v in two_cycles:
    residual = [0] * n
    for a, b in missing:
        if a == u:
            residual[b] += 1
        if b == u:
            residual[a] += 1
        if a == v:
            residual[b] += 1
        if b == v:
            residual[a] += 1
    residual[u] -= 1
    residual[v] -= 1
    sparse = {i: value for i, value in enumerate(residual) if value}
    print(f"potential_residual_{u}_{v}={sparse}")
    assert sparse

print("certificate=UNSAT_SINGLETON")

