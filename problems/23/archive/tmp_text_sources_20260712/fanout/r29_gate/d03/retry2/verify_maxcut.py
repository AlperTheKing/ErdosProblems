"""Clean-room exact certificate for the candidate R29 graph's maximum cut."""
from __future__ import annotations

import hashlib
import json
from itertools import product
from pathlib import Path

OUT = Path(__file__).resolve().parent


def E(a: int, b: int) -> tuple[int, int]:
    assert a != b
    return (a, b) if a < b else (b, a)


def add(cls: set[tuple[int, int]], *pairs: tuple[int, int]) -> None:
    for a, b in pairs:
        e = E(a, b)
        assert e not in cls
        cls.add(e)


def cut_count(edges: set[tuple[int, int]], bits: list[int]) -> int:
    return sum(bits[a] != bits[b] for a, b in edges)


def traffic_quotient() -> dict:
    # Four core bits and the numbers of 1-leaves on the two 26-leaf sides.
    best = -1
    witnesses: list[list[int]] = []
    cases = 0
    for r, cl, cr, anchor in product(range(2), repeat=4):
        for nl in range(27):
            for nr in range(27):
                cases += 1
                core = (r != cl) + (r != cr)
                stars = nl * (cl != 1) + (26 - nl) * (cl != 0)
                stars += nr * (cr != 1) + (26 - nr) * (cr != 0)
                complete = nl * (26 - nr) + (26 - nl) * nr
                opposite = (nl if anchor == 0 else 26 - nl)
                opposite += (nr if anchor == 0 else 26 - nr)
                # Each leaf has 26 internally-disjoint length-3 arms to anchor.
                arms = 26 * (3 * opposite + 2 * (52 - opposite))
                value = core + stars + complete + arms
                state = [r, cl, cr, anchor, nl, nr]
                if value > best:
                    best, witnesses = value, [state]
                elif value == best:
                    witnesses.append(state)
    assert cases == 11664 and best == 4110
    return {"cases": cases, "maximum": best, "maximizers": witnesses}


def build() -> tuple[dict[str, set[tuple[int, int]]], list[int], dict]:
    classes = {k: set() for k in ("traffic", "selectors", "seeds", "circuit", "cable")}
    T, S, W, C, D = (classes[k] for k in classes)
    r, cl, cr = 0, 1, 2
    left, right, anchor = list(range(3, 29)), list(range(29, 55)), 55
    bits = [0, 1, 1] + [0] * 52 + [1]
    add(T, (r, cl), (r, cr))
    for leaf in left: add(T, (cl, leaf))
    for leaf in right: add(T, (cr, leaf))
    for u in left:
        for v in right: add(T, (u, v))

    arms: list[list[tuple[int, int, int]]] = []
    nxt = 56
    for leaves in (left, right):
        region = []
        for leaf in leaves:
            for _ in range(26):
                x, y = nxt, nxt + 1
                nxt += 2
                bits += [1, 0]
                add(T, (leaf, x), (x, y), (y, anchor))
                region.append((leaf, x, y))
        arms.append(region)
    assert nxt == 2760

    ql, qr = 2760, 2761
    bits += [0, 0]
    for q, region in zip((ql, qr), arms):
        first, second = region[:338], region[338:]
        for j in range(338):
            xf = first[j][1]
            yfnext = first[(j + 1) % 338][2]
            xd = second[j][1]
            ydnext = second[(j + 1) % 338][2]
            cycle = (q, xf, yfnext, xd, ydnext, q)
            for a, b in zip(cycle, cycle[1:]): add(S, (a, b))

    off = 2762
    bits += [i % 2 for i in range(26)] + [1]
    support = {E(i, (i + 1) % 26) for i in range(26)} | {E(26, 0)}
    atoms = {E(i, (i + 4) % 26) for i in range(26)} | {E(26, 3), E(26, 23)}
    seq = [(9 * k) % 26 for k in range(13)]
    active = {E(seq[i], seq[i + 1]) for i in range(12)}
    for a, b in sorted(support | active | atoms): add(C, (off + a, off + b))
    nxt = off + 27
    for a, b in sorted(atoms):
        internal = list(range(nxt, nxt + 5))
        nxt += 5
        for step in range(1, 6): bits.append(bits[off + a] ^ (step & 1))
        path = [off + a] + internal + [off + b]
        for u, v in zip(path, path[1:]): add(C, (u, v))
    assert nxt == 2929

    zl, zr = 2929, 2930
    bits += [0, 0]
    add(D, (r, anchor), (anchor, off + 2), (cl, zl), (zl, anchor), (cr, zr), (zr, anchor))
    nxt = 2931
    for seed in (anchor, zl, zr):
        internal = list(range(nxt, nxt + 4))
        nxt += 4
        for step in range(1, 5): bits.append(bits[seed] ^ (step & 1))
        cycle = [seed] + internal + [seed]
        for u, v in zip(cycle, cycle[1:]): add(W, (u, v))
    assert nxt == 2943 and len(bits) == 2943

    expected_sizes = {"traffic": 4786, "selectors": 3380, "seeds": 15, "circuit": 235, "cable": 6}
    actual_sizes = {k: len(v) for k, v in classes.items()}
    assert actual_sizes == expected_sizes, (actual_sizes, expected_sizes)
    names = list(classes)
    for i, a in enumerate(names):
        for b in names[i + 1:]: assert classes[a].isdisjoint(classes[b])
    union = set().union(*classes.values())
    assert len(union) == 8422

    attained = {k: cut_count(v, bits) for k, v in classes.items()}
    bounds = {"traffic": 4110, "selectors": 2704, "seeds": 12, "circuit": 207, "cable": 6}
    assert attained == bounds and sum(attained.values()) == 7039
    quotient = traffic_quotient()

    graph_obj = {
        "format": "r29-candidate-graph-v1",
        "n": 2943,
        "classes": {k: [list(e) for e in sorted(v)] for k, v in classes.items()},
    }
    raw = (json.dumps(graph_obj, sort_keys=True, separators=(",", ":")) + "\n").encode()
    (OUT / "graph_classes.json").write_bytes(raw)
    cut_raw = ("".join(map(str, bits)) + "\n").encode()
    (OUT / "attaining_cut_bits.txt").write_bytes(cut_raw)
    meta = {
        "arithmetic": "integer-only",
        "n": 2943,
        "edge_count": len(union),
        "class_edge_counts": expected_sizes,
        "class_upper_bounds": bounds,
        "attaining_class_counts": attained,
        "maxcut": 7039,
        "traffic_quotient": quotient,
        "sha256": {
            "graph_classes.json": hashlib.sha256(raw).hexdigest(),
            "attaining_cut_bits.txt": hashlib.sha256(cut_raw).hexdigest(),
        },
        "falsifiers": [
            "any repeated edge within or between the five classes",
            "any class size differing from 4786,3380,15,235,6",
            "traffic quotient count !=11664 or maximum !=4110",
            "any selector or seed component not an edge-disjoint 5-cycle",
            "circuit core exceeding 39 cut edges or an atom gadget exceeding 6",
            "attaining cut class counts differing from 4110,2704,12,207,6",
        ],
        "proof_gaps": [
            "No machine-checked Lean formalization; the certificate is an exact executable audit plus a human-checkable decomposition proof.",
            "Identity with any graph outside the supplied candidate constructor requires comparing canonical graph hashes.",
        ],
    }
    return classes, bits, meta


if __name__ == "__main__":
    _, _, result = build()
    out = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode()
    (OUT / "certificate.json").write_bytes(out)
    print(json.dumps(result, sort_keys=True))
