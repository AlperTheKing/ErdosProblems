#!/usr/bin/env python3
import argparse
import hashlib
import json
from collections import Counter
from functools import lru_cache
from math import gcd
from pathlib import Path

Q = 360


def offsets_for(k):
    states = {(0, 0, 0): {0}}
    for total in range(1, 6 * k + 1):
        for a in range(3 * k + 1):
            for b in range(2 * k + 1):
                c = total - a - b
                if c < 0 or c > k:
                    continue
                values = set()
                if a:
                    values.update(2 * d for d in states[(a - 1, b, c)])
                if b:
                    values.update(3 * d + 1 for d in states[(a, b - 1, c)])
                if c:
                    values.update(5 * d + 3 for d in states[(a, b, c - 1)])
                states[(a, b, c)] = values
    return sorted(states[(3 * k, 2 * k, k)])


def make_layer(k):
    scale = Q**k
    offsets = offsets_for(k)
    counts = Counter((8 * scale + d + 1) % 3 for d in offsets)
    residue = 2 if counts[2] >= counts[0] else 0
    selected = [d for d in offsets if (8 * scale + d + 1) % 3 == residue]
    hs = [8 * scale + d + 1 for d in selected]
    left = [2 * h - 1 if residue == 2 else 4 * h - 3 for h in hs]
    right = [3 * h - 1 for h in hs]
    return {"residue": residue, "offsets": selected, "left": left, "right": right}


def factor(n):
    result = []
    p = 2
    while p * p <= n:
        if n % p:
            p = 3 if p == 2 else p + 2
            continue
        exponent = 0
        while n % p == 0:
            n //= p
            exponent += 1
        result.append([p, exponent])
        p = 3 if p == 2 else p + 2
    if n > 1:
        result.append([n, 1])
    return result


def offset_word(k, target):
    @lru_cache(maxsize=None)
    def solve(a, b, c, value):
        if a == b == c == 0:
            return () if value == 0 else None
        candidates = []
        if a and value % 2 == 0:
            candidates.append((2, a - 1, b, c, value // 2))
        if b and value >= 1 and (value - 1) % 3 == 0:
            candidates.append((3, a, b - 1, c, (value - 1) // 3))
        if c and value >= 3 and (value - 3) % 5 == 0:
            candidates.append((5, a, b, c - 1, (value - 3) // 5))
        for multiplier, pa, pb, pc, parent in candidates:
            prefix = solve(pa, pb, pc, parent)
            if prefix is not None:
                return prefix + (multiplier,)
        return None

    word = solve(3 * k, 2 * k, k, target)
    if word is None:
        raise AssertionError("offset has no word witness")
    value = 0
    for multiplier in word:
        value = multiplier * value + multiplier - 2
    if value != target:
        raise AssertionError("word evaluation mismatch")
    return list(word)


def full_histogram(K, layers):
    products = Counter()
    for i in range((K + 2) // 3, (2 * K) // 3 + 1):
        for u in layers[i]["left"]:
            products.update(u * v for v in layers[K - i]["right"])
    return {
        "edges": sum(products.values()),
        "support": len(products),
        "histogram": {str(m): count for m, count in sorted(Counter(products.values()).items())},
    }


def replay_witness(witness, layers):
    K = witness["K"]
    product = witness["product"]
    representations = []
    for i in range((K + 2) // 3, (2 * K) // 3 + 1):
        right_index = {v: index for index, v in enumerate(layers[K - i]["right"])}
        for x, u in enumerate(layers[i]["left"]):
            if product % u:
                continue
            v = product // u
            if v in right_index:
                y = right_index[v]
                representations.append({
                    "layer": i,
                    "left_index": x,
                    "right_index": y,
                    "left_offset": layers[i]["offsets"][x],
                    "right_offset": layers[K - i]["offsets"][y],
                    "u": u,
                    "v": v,
                })
    if representations != witness["fibre"]:
        raise AssertionError("witness fibre mismatch")
    first, second = witness["pair_indices"]
    edge1 = representations[first]
    edge2 = representations[second]
    g = gcd(edge1["u"], edge2["u"])
    a = edge1["u"] // g
    b = edge2["u"] // g
    if gcd(a, b) != 1:
        raise AssertionError("reduced quotients are not coprime")
    if edge1["v"] % b or edge2["v"] % a:
        raise AssertionError("swap divisibility failure")
    c = edge1["v"] // b
    if edge2["v"] // a != c or g * a * b * c != product:
        raise AssertionError("normal-form replay failure")
    normal = witness["normal_form"]
    if [g, a, b, c] != [normal["g"], normal["a"], normal["b"], normal["c"]]:
        raise AssertionError("normal-form values mismatch")
    if factor(a) != normal["factor_a"] or factor(b) != normal["factor_b"]:
        raise AssertionError("factorization mismatch")
    words = []
    for edge in representations:
        words.append({
            "left": offset_word(edge["layer"], edge["left_offset"]),
            "right": offset_word(K - edge["layer"], edge["right_offset"]),
        })
    return {
        "K": K,
        "product": product,
        "multiplicity": len(representations),
        "normal_form": {"g": g, "a": a, "b": b, "c": c},
        "omega_a": len(factor(a)),
        "omega_b": len(factor(b)),
        "word_witnesses": words,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    audit_path = Path(args.audit)
    audit = json.loads(audit_path.read_text(encoding="ascii"))
    layers = {1: make_layer(1), 2: make_layer(2)}
    if [(layers[k]["residue"], len(layers[k]["offsets"])) for k in (1, 2)] != [
        (2, 36),
        (2, 7779),
    ]:
        raise AssertionError("layer census mismatch")

    small = {str(K): full_histogram(K, layers) for K in (2, 3)}
    submitted = {str(row["K"]): row for row in audit["summaries"]}
    for K in (2, 3):
        if small[str(K)]["edges"] != submitted[str(K)]["edges"]:
            raise AssertionError("small edge count mismatch")
        if small[str(K)]["support"] != submitted[str(K)]["support"]:
            raise AssertionError("small support mismatch")
        if small[str(K)]["histogram"] != submitted[str(K)]["histogram"]:
            raise AssertionError("small histogram mismatch")

    first = replay_witness(audit["first_non_atomic_witness"], layers)
    bilateral = replay_witness(audit["first_bilateral_non_atomic_witness"], layers)
    if first["omega_a"] <= 1 and first["omega_b"] <= 1:
        raise AssertionError("first witness is atomic")
    if bilateral["omega_a"] <= 1 or bilateral["omega_b"] <= 1:
        raise AssertionError("bilateral witness is not bilateral")

    result = {
        "audit_sha256": hashlib.sha256(audit_path.read_bytes()).hexdigest().upper(),
        "layers": {str(k): {"selected_residue": layers[k]["residue"],
                             "selected_size": len(layers[k]["offsets"])} for k in (1, 2)},
        "independent_full_small_census": small,
        "first_non_atomic_replay": first,
        "first_bilateral_replay": bilateral,
    }
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
