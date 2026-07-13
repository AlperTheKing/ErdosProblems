"""Exact incremental audit of every R29 Hamming-one selector replacement."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from r29_lead_gate import adjacency, build, canonical_bytes, scoped_state, shortest_rows


def pair_counter(row: tuple[int, ...]) -> Counter:
    return Counter((x, y) for x in row for y in row)


def main() -> None:
    data = build()
    baseline_rows = data["rows"]
    baseline = scoped_state(data, baseline_rows)
    assert baseline["score"] == 30811
    active = baseline["activeVertices"]

    counts = Counter()
    vertex_row_count = Counter()
    for row in baseline_rows:
        counts.update((x, y) for x in row for y in row)
        vertex_row_count.update(row)

    # The only positive owners are fixed hubs, fixed circuit vertices, and the
    # 52 leaves.  A one-row move cannot change hub/circuit selection or cable
    # support.  Each leaf retains at least 25 of its 26 selected lock arms, so
    # it remains joined to the permanent anchor/cable active component.
    positive = {
        v for v in active
        if baseline["collision"].get(v, 0) + baseline["hitNeed"].get(v, 0) > 0
    }
    assert {0, 1, 2} <= positive
    assert set(range(3, 55)) <= positive
    assert len(positive) == 68

    adj = adjacency(data["n"], data["blue"])
    minimum = None
    multiplicity = 0
    witnesses = []
    delta_hist = Counter()
    checked = 0
    premise = Counter()
    start, stop = data["selectorStart"], data["selectorStop"]
    for selector_index, (atom, old_row) in enumerate(
        zip(data["atoms"][start:stop], baseline_rows[start:stop])
    ):
        family = shortest_rows(adj, *atom)
        assert len(family) == 680 and old_row in family
        old_pairs = pair_counter(old_row)
        old_set = set(old_row)
        for replacement_index, new_row in enumerate(family):
            if new_row == old_row:
                continue
            checked += 1
            new_set = set(new_row)
            added_vertices = new_set - old_set
            assert added_vertices
            premise["qMinusPNonempty"] += 1
            assert all(vertex_row_count[v] == 1 for v in added_vertices)
            premise["newVerticesBaselineMultiplicityOne"] += 1

            delta = 0
            new_pairs = pair_counter(new_row)
            for key in old_pairs.keys() | new_pairs.keys():
                owner = key[0]
                if owner not in active:
                    continue
                before = counts[key]
                after = before - old_pairs[key] + new_pairs[key]
                delta += 2 * (max(0, after - 1) - max(0, before - 1))
            # HitNeed is fixed at the three hubs; all other changed row loads
            # remain far below N, while cable/circuit active degrees are fixed.
            score = baseline["score"] + delta
            delta_hist[delta] += 1
            if minimum is None or score < minimum:
                minimum = score
                multiplicity = 1
                witnesses = [{
                    "selectorIndex": selector_index,
                    "replacementIndex": replacement_index,
                    "atom": list(atom),
                    "oldRow": list(old_row),
                    "newRow": list(new_row),
                    "delta": delta,
                }]
            elif score == minimum:
                multiplicity += 1
                if len(witnesses) < 10:
                    witnesses.append({
                        "selectorIndex": selector_index,
                        "replacementIndex": replacement_index,
                        "atom": list(atom),
                        "oldRow": list(old_row),
                        "newRow": list(new_row),
                        "delta": delta,
                    })

    assert checked == 459004
    assert minimum is not None
    for witness in witnesses:
        index = start + witness["selectorIndex"]
        changed = list(baseline_rows)
        changed[index] = tuple(witness["newRow"])
        full = scoped_state(data, tuple(changed))
        assert full["score"] == minimum
        assert positive <= full["activeVertices"]

    payload = {
        "baseline": baseline["score"],
        "checked": checked,
        "minimum": minimum,
        "minimumDelta": minimum - baseline["score"],
        "minimumMultiplicity": multiplicity,
        "deltaHistogram": dict(sorted(delta_hist.items())),
        "premises": dict(premise),
        "witnesses": witnesses,
        "inputSha256": hashlib.sha256(canonical_bytes(data)).hexdigest(),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["resultSha256"] = hashlib.sha256(encoded).hexdigest()
    out = Path(__file__).with_name("hamming_result.json")
    out.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
