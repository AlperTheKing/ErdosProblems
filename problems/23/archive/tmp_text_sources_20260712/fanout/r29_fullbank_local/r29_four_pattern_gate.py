"""Exact R29 all-anchor audit for the implemented R23 four-pattern matcher."""

from __future__ import annotations

import importlib.util
import json
from collections import Counter, deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    r29 = load(
        "r29_lead_gate",
        ROOT / "tmp" / "fanout" / "r29_gate" / "lead" / "r29_lead_gate.py",
    )
    data = r29.build()
    rows = list(data["rows"])
    for i, meta in enumerate(data["selectorMeta"]):
        rows[data["selectorStart"] + i] = meta["anchorRow"]
    rows = tuple(rows)

    state = r29.scoped_state(data, rows)
    assert state["score"] == 23115

    # Independently check the already published pre-attachment flow balance.
    cert_path = (
        ROOT / "tmp" / "fanout" / "r29_gate" / "d05" / "retry2"
        / "cut_certificate.json"
    )
    cert = json.loads(cert_path.read_text())
    received = Counter()
    for label, amount in cert["flow_certificate_by_source_mask_to_owner"].items():
        mask, owner = map(int, label.split("->"))
        assert mask & (1 << owner)
        received[owner] += amount
    assert received == Counter({0: 6651, 1: 6651, 2: 6623})
    received_before = dict(sorted(received.items()))

    selected = {x for row in rows for x in row}
    adj = [set() for _ in range(data["n"])]
    for x, y in data["blue"]:
        adj[x].add(y)
        adj[y].add(x)
    component_id = [-1] * data["n"]
    components = []
    attachments = []
    for root in range(data["n"]):
        if root in selected or component_id[root] >= 0:
            continue
        cid = len(components)
        component_id[root] = cid
        vertices, attachment = set(), set()
        todo = deque([root])
        while todo:
            x = todo.popleft()
            vertices.add(x)
            for y in adj[x]:
                if y in selected:
                    attachment.add(y)
                elif component_id[y] < 0:
                    component_id[y] = cid
                    todo.append(y)
        components.append(vertices)
        attachments.append(attachment)

    pair_count = Counter()
    for row in rows:
        for x in row:
            for y in row:
                pair_count[x, y] += 1

    owners = (0, 1, 2)
    eligible = {}
    for owner in owners:
        cids = [
            cid for cid, attachment in enumerate(attachments)
            if any(pair_count[owner, a] > 0 for a in attachment)
        ]
        eligible[owner] = set().union(*(components[cid] for cid in cids))
    assert all(len(eligible[o]) == 676 for o in owners)
    assert eligible[0] == eligible[1] == eligible[2]

    sign = {e: 1 for e in data["blue"]}
    sign.update({e: -1 for e in data["bad"]})
    signed_degree = [0] * data["n"]
    for (x, y), s in sign.items():
        signed_degree[x] += s
        signed_degree[y] += s

    repair = []
    outside = sorted(eligible[2])
    for x in outside:
        for y in outside:
            if x == y:
                continue
            assert pair_count[x, y] == 0
            union = components[component_id[x]] | components[component_id[y]]
            loss = (
                sum((u in union) != (v in union) for u, v in data["blue"])
                - sum((u in union) != (v in union) for u, v in data["bad"])
            )
            assert loss >= 0
            repair.extend(((x, y, 0), (x, y, 1)))
            if len(repair) >= 28:
                break
        if len(repair) >= 28:
            break
    repair = repair[:28]
    assert len(repair) == len(set(repair)) == 28
    received[2] += 28
    assert received == Counter({0: 6651, 1: 6651, 2: 6651})

    payload = {
        "n": data["n"],
        "score": state["score"],
        "activeVertices": len(state["activeVertices"]),
        "preAttachmentReceived": received_before,
        "postAttachmentReceived": dict(sorted(received.items())),
        "outsideComponentCount": len(components),
        "eligibleOutsidePerHub": len(outside),
        "repairHalfSlots": repair,
    }
    output = Path(__file__).with_name("result.json")
    output.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
