from __future__ import annotations

import hashlib
import importlib.util
import json
import time
import os
from concurrent.futures import ProcessPoolExecutor
from collections import Counter, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEAD = HERE.parents[1] / "lead" / "r29_lead_gate.py"


def load_candidate():
    spec = importlib.util.spec_from_file_location("untrusted_r29", LEAD)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.build()


def edge(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def canonical_input(data: dict) -> bytes:
    obj = {
        "n": data["n"],
        "blue": [list(x) for x in sorted(data["blue"])],
        "bad": [list(x) for x in sorted(data["bad"])],
        "rows": [list(x) for x in data["rows"]],
        "selector_start": data["selectorStart"],
        "selector_stop": data["selectorStop"],
    }
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("ascii")


def adjacency(n: int, edges) -> list[list[int]]:
    ans = [[] for _ in range(n)]
    for a, b in edges:
        ans[a].append(b)
        ans[b].append(a)
    for xs in ans:
        xs.sort()
    return ans


def shortest_rows(adj: list[list[int]], source: int, target: int):
    dist = [-1] * len(adj)
    dist[source] = 0
    q = deque([source])
    while q:
        x = q.popleft()
        if dist[x] == 4:
            continue
        for y in adj[x]:
            if dist[y] < 0:
                dist[y] = dist[x] + 1
                q.append(y)
    out = []

    def rec(path):
        x = path[-1]
        if len(path) == 5:
            if x == target:
                out.append(tuple(path))
            return
        for y in adj[x]:
            if dist[y] == dist[x] + 1:
                rec(path + [y])

    rec([source])
    return sorted(out)


def score_from_first_principles(n, blue, bad, rows):
    selected = set()
    support = set()
    row_count = [0] * n
    pair_count = Counter()
    for row in rows:
        selected.update(row)
        for x in row:
            row_count[x] += 1
            for y in row:
                pair_count[x, y] += 1
        for a, b in zip(row, row[1:]):
            support.add(edge(a, b))

    active_adj = [[] for _ in range(n)]
    active_edges = []
    for a, b in blue:
        if a in selected and b in selected and (a, b) not in support:
            active_edges.append((a, b))
            active_adj[a].append(b)
            active_adj[b].append(a)

    component = [-1] * n
    cid = 0
    for start in selected:
        if component[start] >= 0:
            continue
        component[start] = cid
        q = [start]
        for x in q:
            for y in active_adj[x]:
                if component[y] < 0:
                    component[y] = cid
                    q.append(y)
        cid += 1
    demanded = set()
    for a, b in bad:
        if a in selected and b in selected and component[a] == component[b]:
            demanded.add(component[a])
    degree = [0] * n
    for a, b in active_edges:
        if component[a] in demanded:
            degree[a] += 1
            degree[b] += 1
    collision_by_owner = [0] * n
    for (x, _), count in pair_count.items():
        if count >= 2:
            collision_by_owner[x] += 2 * (count - 1)
    collision = 0
    hit_need = 0
    for x in selected:
        if component[x] not in demanded:
            continue
        collision += collision_by_owner[x]
        hit_need += max(0, degree[x] - max(0, n - 5 * row_count[x]))
    return collision + hit_need, collision, hit_need


def audit_family(index: int):
    data = load_candidate()
    rows0 = list(data["rows"])
    old = rows0[index]
    atom = edge(old[0], old[-1])
    family = shortest_rows(adjacency(data["n"], data["blue"]), atom[0], atom[1])
    assert old in family and len(family) == 680
    best = None
    count = 0
    witness = None
    enumerated = 0
    for replacement in family:
        if replacement == old:
            continue
        trial = rows0.copy()
        trial[index] = replacement
        value = score_from_first_principles(data["n"], data["blue"], data["bad"], trial)
        enumerated += 1
        if best is None or value[0] < best:
            best, count = value[0], 1
            witness = {"row_index": index, "old_row": list(old), "new_row": list(replacement),
                       "score": value[0], "collision": value[1], "hit_need": value[2]}
        elif value[0] == best:
            count += 1
    return best, count, witness, enumerated, len(family)


def main():
    started = time.time()
    data = load_candidate()
    raw = canonical_input(data)
    input_sha = hashlib.sha256(raw).hexdigest()
    rows0 = list(data["rows"])
    baseline = score_from_first_principles(data["n"], data["blue"], data["bad"], rows0)
    minimum = None
    multiplicity = 0
    witness = None
    enumerated = 0
    family_sizes = Counter()
    indices = range(data["selectorStart"], data["selectorStop"])
    workers = min(61, os.cpu_count() or 1)  # Windows ProcessPool hard limit.
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for best, count, candidate_witness, done, family_size in pool.map(audit_family, indices, chunksize=1):
            enumerated += done
            family_sizes[family_size] += 1
            if minimum is None or best < minimum:
                minimum, multiplicity, witness = best, count, candidate_witness
            elif best == minimum:
                multiplicity += count
    assert enumerated == 459004
    result = {
        "baseline": {"score": baseline[0], "collision": baseline[1], "hit_need": baseline[2]},
        "minimum": minimum,
        "multiplicity": multiplicity,
        "sharp_witness": witness,
        "enumerated": enumerated,
        "family_sizes": {str(k): v for k, v in sorted(family_sizes.items())},
        "input_sha256": input_sha,
        "elapsed_seconds_integer": int(time.time() - started),
        "arithmetic": "integer-only",
        "workers": workers,
    }
    output_preimage = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("ascii")
    result["output_sha256"] = hashlib.sha256(output_preimage).hexdigest()
    (HERE / "result.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
