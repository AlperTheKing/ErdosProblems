#!/usr/bin/env python3
"""Independent CPU oracle for the Wolfe--Pike K64 CUDA gate.

This module deliberately imports neither the CUDA implementation nor either
certificate verifier.  It validates two starters in Z_n, applies Wolfe's
high/low merger for a supplied bit mask, and reports the exact Hamilton-cycle
signature of the n+1 cyclic orbit representatives of the resulting P1F.

For K64, n=31, a mask has 15 bits and the signature has 32 entries:
M_* with M_0, followed by M_0 with M_d for d=1,...,31.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


Pair = tuple[int, int]


@dataclass(frozen=True)
class StarterInfo:
    modulus: int
    missing: int
    pairs: tuple[Pair, ...]


@dataclass(frozen=True)
class MergeResult:
    starter_modulus: int
    mask: int
    pairs: tuple[Pair, ...]
    holes_in_order: tuple[int, int]
    terminal_lift: int


def pair_key(pair: Iterable[int]) -> Pair:
    x, y = pair
    if x == y:
        raise ValueError(f"degenerate pair {(x, y)}")
    return (x, y) if x < y else (y, x)


def canonical_pairs(pairs: Iterable[Pair]) -> tuple[Pair, ...]:
    return tuple(sorted(pair_key(pair) for pair in pairs))


def canonical_pairs_sha256(pairs: Iterable[Pair]) -> str:
    payload = json.dumps(canonical_pairs(pairs), separators=(",", ":"))
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def unsigned_cyclic_difference(pair: Pair, modulus: int) -> int:
    x, y = pair
    return min((x - y) % modulus, (y - x) % modulus)


def validate_starter(pairs: Sequence[Pair], modulus: int) -> StarterInfo:
    if modulus < 3 or modulus % 2 == 0:
        raise ValueError("starter modulus must be odd and at least 3")
    expected_pairs = (modulus - 1) // 2
    if len(pairs) != expected_pairs:
        raise ValueError(f"expected {expected_pairs} pairs, got {len(pairs)}")

    normalized = tuple((int(x), int(y)) for x, y in pairs)
    vertices = [vertex for pair in normalized for vertex in pair]
    if any(vertex < 0 or vertex >= modulus for vertex in vertices):
        raise ValueError("starter vertex outside its residue system")
    if len(set(vertices)) != modulus - 1:
        raise ValueError("starter pairs are not vertex-disjoint")

    missing_set = set(range(modulus)) - set(vertices)
    if len(missing_set) != 1:
        raise ValueError(f"starter has {len(missing_set)} missing vertices")
    directed_differences = {
        difference
        for x, y in normalized
        for difference in ((x - y) % modulus, (y - x) % modulus)
    }
    if directed_differences != set(range(1, modulus)):
        raise ValueError("pairs do not realize every nonzero signed difference")
    return StarterInfo(modulus, missing_set.pop(), normalized)


def validate_compatible(
    starter1: Sequence[Pair], starter2: Sequence[Pair], modulus: int
) -> tuple[StarterInfo, StarterInfo, tuple[tuple[int, int, int], ...]]:
    """Validate that the two coloured matchings form one alternating path.

    The path trace contains (starter_number, x, y), beginning at the missing
    vertex of starter 1 and ending at the missing vertex of starter 2.
    """

    info1 = validate_starter(starter1, modulus)
    info2 = validate_starter(starter2, modulus)
    if info1.missing == info2.missing:
        raise ValueError("compatible starters must have different endpoints")

    tagged: list[tuple[int, Pair]] = [
        (1, pair) for pair in info1.pairs
    ] + [(2, pair) for pair in info2.pairs]
    keys = [pair_key(pair) for _, pair in tagged]
    if len(set(keys)) != len(keys):
        raise ValueError("the two starters share an unordered edge")

    incident: list[list[int]] = [[] for _ in range(modulus)]
    for edge_id, (_, (x, y)) in enumerate(tagged):
        incident[x].append(edge_id)
        incident[y].append(edge_id)
    expected_degrees = [2] * modulus
    expected_degrees[info1.missing] = 1
    expected_degrees[info2.missing] = 1
    if [len(edges) for edges in incident] != expected_degrees:
        raise ValueError("starter union does not have Hamilton-path degrees")

    used: set[int] = set()
    trace: list[tuple[int, int, int]] = []
    x = info1.missing
    for _ in range(modulus - 1):
        available = [edge_id for edge_id in incident[x] if edge_id not in used]
        if len(available) != 1:
            raise ValueError("starter union closes a proper cycle")
        edge_id = available[0]
        starter_number, pair = tagged[edge_id]
        y = pair[1] if pair[0] == x else pair[0]
        used.add(edge_id)
        trace.append((starter_number, x, y))
        x = y
    if len(used) != modulus - 1 or x != info2.missing:
        raise ValueError("starter union is not one spanning alternating path")
    if any(trace[i][0] == trace[i + 1][0] for i in range(len(trace) - 1)):
        raise AssertionError("internal error: path does not alternate starters")
    return info1, info2, tuple(trace)


def merge_starters(
    starter1: Sequence[Pair],
    starter2: Sequence[Pair],
    modulus: int,
    s1_high_mask: int,
) -> MergeResult:
    """Apply Algorithm 1 with bit d-1 saying S1's difference-d pair is high."""

    info1, info2, path = validate_compatible(starter1, starter2, modulus)
    bits = (modulus - 1) // 2
    if s1_high_mask < 0 or s1_high_mask >= 1 << bits:
        raise ValueError(f"mask must fit in {bits} bits")

    doubled = 2 * modulus
    a = info1.missing + modulus
    output: list[Pair] = []
    for starter_number, x, y in path:
        if x != a % modulus:
            raise AssertionError("path/lift mismatch in merger")
        difference = unsigned_cyclic_difference((x, y), modulus)
        lifts = (y, y + modulus)
        targets = {(a - difference) % doubled, (a + difference) % doubled}
        intersection = set(lifts) & targets
        if len(intersection) != 1:
            raise AssertionError("the signed-difference lift is not unique")
        y_hat = intersection.pop()
        other_lift = lifts[1] if lifts[0] == y_hat else lifts[0]

        s1_is_high = bool(s1_high_mask & (1 << (difference - 1)))
        is_low = (not s1_is_high) if starter_number == 1 else s1_is_high
        b = y_hat if is_low else other_lift
        next_a = other_lift if b == y_hat else y_hat
        output.append((a, b))
        a = next_a

    result = MergeResult(
        starter_modulus=modulus,
        mask=s1_high_mask,
        pairs=tuple(output),
        holes_in_order=(info1.missing, a),
        terminal_lift=a,
    )
    validate_even_starter(result)
    if a % modulus != info2.missing:
        raise AssertionError("merger did not terminate above S2's missing vertex")
    return result


def validate_even_starter(result: MergeResult) -> None:
    modulus = 2 * result.starter_modulus
    expected_pairs = result.starter_modulus - 1
    if len(result.pairs) != expected_pairs:
        raise ValueError("wrong number of merged pairs")
    vertices = [vertex for pair in result.pairs for vertex in pair]
    if any(vertex < 0 or vertex >= modulus for vertex in vertices):
        raise ValueError("merged vertex outside its residue system")
    if len(set(vertices)) != 2 * expected_pairs:
        raise ValueError("merged pairs are not vertex-disjoint")
    holes = set(range(modulus)) - set(vertices)
    if holes != set(result.holes_in_order):
        raise ValueError(f"reported holes disagree with actual holes: {holes}")
    directed_differences = {
        difference
        for x, y in result.pairs
        for difference in ((x - y) % modulus, (y - x) % modulus)
    }
    expected = set(range(1, modulus)) - {result.starter_modulus}
    if directed_differences != expected:
        raise ValueError("merger output is not an even starter")


def validate_factor(factor: Sequence[Pair], order: int) -> None:
    if len(factor) != order // 2:
        raise ValueError("wrong number of edges in factor")
    vertices = [vertex for pair in factor for vertex in pair]
    if len(vertices) != order or set(vertices) != set(range(order)):
        raise ValueError("factor is not a perfect matching")


def developed_factor(result: MergeResult, shift: int) -> tuple[Pair, ...]:
    residue_modulus = 2 * result.starter_modulus
    infinity0, infinity1 = residue_modulus, residue_modulus + 1
    hole0, hole1 = result.holes_in_order
    factor = tuple(
        ((x + shift) % residue_modulus, (y + shift) % residue_modulus)
        for x, y in result.pairs
    ) + (
        (infinity0, (hole0 + shift) % residue_modulus),
        (infinity1, (hole1 + shift) % residue_modulus),
    )
    validate_factor(factor, residue_modulus + 2)
    return factor


def fixed_factor(result: MergeResult) -> tuple[Pair, ...]:
    half = result.starter_modulus
    infinity0, infinity1 = 2 * half, 2 * half + 1
    factor = tuple((x, x + half) for x in range(half)) + (
        (infinity0, infinity1),
    )
    validate_factor(factor, 2 * half + 2)
    return factor


def component_sizes(
    factor1: Sequence[Pair], factor2: Sequence[Pair], order: int
) -> tuple[int, ...]:
    validate_factor(factor1, order)
    validate_factor(factor2, order)
    adjacency: list[list[int]] = [[] for _ in range(order)]
    for x, y in tuple(factor1) + tuple(factor2):
        adjacency[x].append(y)
        adjacency[y].append(x)
    if any(len(neighbours) != 2 for neighbours in adjacency):
        raise AssertionError("factor union is not 2-regular")

    unseen = set(range(order))
    sizes: list[int] = []
    while unseen:
        seed = min(unseen)
        stack = [seed]
        component: set[int] = set()
        while stack:
            vertex = stack.pop()
            if vertex in component:
                continue
            component.add(vertex)
            stack.extend(adjacency[vertex])
        unseen -= component
        sizes.append(len(component))
    return tuple(sorted(sizes, reverse=True))


def orbit_signature(result: MergeResult) -> dict[str, object]:
    """Return an exact, comparison-friendly cyclic-orbit score."""

    half = result.starter_modulus
    order = 2 * half + 2
    factor0 = developed_factor(result, 0)
    signatures = [component_sizes(fixed_factor(result), factor0, order)]
    signatures.extend(
        component_sizes(factor0, developed_factor(result, shift), order)
        for shift in range(1, half + 1)
    )
    pass_mask = sum(
        1 << index
        for index, components in enumerate(signatures)
        if components == (order,)
    )
    return {
        "orbit_count": half + 1,
        "hamilton_count": pass_mask.bit_count(),
        "pass_mask_hex": f"0x{pass_mask:0{(half + 4) // 4}x}",
        "component_excess": sum(len(components) - 1 for components in signatures),
        "component_sizes": [list(components) for components in signatures],
    }


def patterned_starter(center: int, modulus: int) -> tuple[Pair, ...]:
    """The standard reflection starter, useful for deterministic sentinels."""

    return tuple(
        ((center + x) % modulus, (center - x) % modulus)
        for x in range(1, (modulus + 1) // 2)
    )


def prf_mask(domain: bytes, index: int, lane: int, bits: int) -> int:
    payload = domain + index.to_bytes(8, "little") + lane.to_bytes(4, "little")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "little") & (
        (1 << bits) - 1
    )


def warmup_sample_masks(pair_id: int, bits: int = 15) -> tuple[int, ...]:
    """Four precommitted masks: rotating basis/complement plus two PRF masks."""

    full = (1 << bits) - 1
    mode = pair_id % (bits + 2)
    basis = 0 if mode == bits else full if mode == bits + 1 else 1 << mode
    return (
        basis,
        basis ^ full,
        prf_mask(b"K64-P1F-WARMUP-v1", pair_id, 0, bits),
        prf_mask(b"K64-P1F-WARMUP-v1", pair_id, 1, bits),
    )


def benchmark_sample_record(block: int, bits: int = 15) -> tuple[int, tuple[int, ...]]:
    """One pair per 1024-record block and four masks, fixed before results exist."""

    if block < 0 or block >= 1 << 16:
        raise ValueError("block must lie in 0..2^16-1")
    offset = prf_mask(b"K64-P1F-BENCH-PAIR-v1", block, 0, 10)
    pair_id = (block << 10) | offset
    full = (1 << bits) - 1
    mode = block % (bits + 2)
    basis = 0 if mode == bits else full if mode == bits + 1 else 1 << mode
    masks = (
        basis,
        basis ^ full,
        prf_mask(b"K64-P1F-BENCH-MASK-v1", pair_id, 0, bits),
        prf_mask(b"K64-P1F-BENCH-MASK-v1", pair_id, 1, bits),
    )
    return pair_id, masks


def protocol_summary() -> dict[str, object]:
    return {
        "version": "K64-P1F-GATE-SAMPLE-v1",
        "warmup": {
            "required_distinct_pair_ids": 1 << 16,
            "gpu_masks_per_pair": 1 << 15,
            "cpu_exhaustive_pair_ids": list(range(8)),
            "cpu_exhaustive_assignments": 8 * (1 << 15),
            "cpu_masks_for_every_pair": 4,
            "cpu_stratified_assignments": 4 * (1 << 16),
        },
        "benchmark": {
            "minimum_pair_ids": 1 << 26,
            "sample_blocks": 1 << 16,
            "records_per_block": 1 << 10,
            "sampled_pairs": 1 << 16,
            "masks_per_sampled_pair": 4,
            "sampled_assignments": 4 * (1 << 16),
        },
        "comparison_fields": [
            "canonical starter-pair SHA-256 and global pair_id",
            "merged canonical-pairs SHA-256 and holes",
            "32-bit orbit pass mask",
            "component_excess and all 32 component-size lists",
        ],
        "rule": (
            "All sample pair IDs and masks are derived from fixed SHA-256 domains, "
            "never from GPU output. Any mismatch is a gate failure."
        ),
    }


PIKE_S1: tuple[Pair, ...] = (
    (0, 1), (7, 11), (12, 17), (20, 26), (16, 25), (8, 18), (10, 22),
    (2, 4), (3, 6), (14, 21), (15, 23), (13, 24), (5, 19),
)
PIKE_S2: tuple[Pair, ...] = (
    (1, 2), (6, 10), (16, 21), (12, 18), (7, 25), (5, 15), (8, 23),
    (24, 26), (19, 22), (4, 11), (9, 17), (3, 14), (0, 13),
)
PIKE_S1_HIGH_DIFFERENCES = (1, 4, 5, 6, 9, 10, 12)
PIKE_EXPECTED_SHA256 = "2d5b0f843c9e7988c0b001d0700e241ea125a48c00383b2f8fe2b1cb825ca96d"


def self_test() -> dict[str, object]:
    pike_mask = sum(1 << (difference - 1) for difference in PIKE_S1_HIGH_DIFFERENCES)
    pike = merge_starters(PIKE_S1, PIKE_S2, 27, pike_mask)
    pike_digest = canonical_pairs_sha256(pike.pairs)
    if pike_digest != PIKE_EXPECTED_SHA256:
        raise AssertionError(f"Pike merger digest mismatch: {pike_digest}")
    pike_score = orbit_signature(pike)
    if pike_score["hamilton_count"] != 28:
        raise AssertionError("published K56 merger does not pass all 28 orbits")

    k64_s1 = patterned_starter(0, 31)
    k64_s2 = patterned_starter(1, 31)
    k64_vectors: list[dict[str, object]] = []
    for mask in (0, (1 << 15) - 1, 0x2AAA, 0x5555):
        merged = merge_starters(k64_s1, k64_s2, 31, mask)
        score = orbit_signature(merged)
        k64_vectors.append(
            {
                "mask": mask,
                "holes": list(merged.holes_in_order),
                "pairs_sha256": canonical_pairs_sha256(merged.pairs),
                "hamilton_count": score["hamilton_count"],
                "pass_mask_hex": score["pass_mask_hex"],
                "component_excess": score["component_excess"],
            }
        )
    return {
        "pike_k56": {
            "mask": pike_mask,
            "pairs_sha256": pike_digest,
            "holes": list(pike.holes_in_order),
            "hamilton_count": pike_score["hamilton_count"],
            "pass_mask_hex": pike_score["pass_mask_hex"],
        },
        "patterned_k64": k64_vectors,
    }


def score_record(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    modulus = int(payload["modulus"])
    starter1 = tuple(tuple(map(int, pair)) for pair in payload["starter1"])
    starter2 = tuple(tuple(map(int, pair)) for pair in payload["starter2"])
    mask = int(payload["mask"])
    merged = merge_starters(starter1, starter2, modulus, mask)
    return {
        "modulus": modulus,
        "mask": mask,
        "holes": list(merged.holes_in_order),
        "canonical_pairs_sha256": canonical_pairs_sha256(merged.pairs),
        "canonical_pairs": [list(pair) for pair in canonical_pairs(merged.pairs)],
        "score": orbit_signature(merged),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, help="score one JSON starter-pair/mask record")
    parser.add_argument("--protocol", action="store_true", help="print sampling protocol")
    parser.add_argument("--sample-block", type=int, help="print one benchmark sample record")
    args = parser.parse_args()

    if args.record is not None:
        output = score_record(args.record)
    elif args.protocol:
        output = protocol_summary()
    elif args.sample_block is not None:
        pair_id, masks = benchmark_sample_record(args.sample_block)
        output = {"block": args.sample_block, "pair_id": pair_id, "masks": list(masks)}
    else:
        output = self_test()
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
