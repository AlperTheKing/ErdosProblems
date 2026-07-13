import argparse
import hashlib
import heapq
import json
from pathlib import Path


def generate(limit):
    if limit < 1:
        return [], {}, {}
    heap = []
    queued = set()
    accepted = []
    accepted_set = set()
    parent = {}
    depth = {}

    def enqueue(value, witness=None):
        if value > limit or value in queued or value in accepted_set:
            return
        queued.add(value)
        heapq.heappush(heap, value)
        if witness is not None and value not in parent:
            parent[value] = witness

    if limit >= 2:
        enqueue(2)
        depth[2] = 0
    if limit >= 3:
        enqueue(3)
        depth[3] = 0

    while heap:
        value = heapq.heappop(heap)
        queued.remove(value)
        if value in accepted_set:
            continue
        for old in accepted:
            candidate = old * value - 1
            if candidate > limit:
                break
            enqueue(candidate, (old, value))
        accepted.append(value)
        accepted_set.add(value)
        if value not in depth:
            left, right = parent[value]
            depth[value] = 1 + max(depth[left], depth[right])

    return accepted, parent, depth


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    values, parent, depth = generate(args.limit)
    payload = {
        "schema_version": 1,
        "algorithm": "exact distinct-pair product heap",
        "limit": args.limit,
        "count": len(values),
        "maximum": values[-1] if values else None,
        "sha256": hashlib.sha256(
            (",".join(map(str, values)) + "\n").encode("ascii")
        ).hexdigest(),
        "values": values,
        "parents": {str(value): pair for value, pair in parent.items()},
        "depths": {str(value): depth[value] for value in values},
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="ascii")
    print(json.dumps({key: value for key, value in payload.items() if key not in {"values", "parents", "depths"}}, indent=2))


if __name__ == "__main__":
    main()

