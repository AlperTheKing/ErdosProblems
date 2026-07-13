#!/usr/bin/env python3
"""Exact probes for the {2,3,5} affine subsystem in Erdos 424."""

from __future__ import annotations

import argparse
from collections import Counter


MULTIPLIERS = (2, 3, 5)
SEEDS = (2, 3, 5)


def generate(limit: int) -> bytearray:
    """Return the exact membership vector through ``limit``."""
    member = bytearray(limit + 1)
    for seed in SEEDS:
        if seed <= limit:
            member[seed] = 1
    for n in range(2, limit + 1):
        if member[n]:
            continue
        successor = n + 1
        for k in MULTIPLIERS:
            if successor % k == 0:
                parent = successor // k
                if parent != k and member[parent]:
                    member[n] = 1
                    break
    return member


def parent_mask(member: bytearray, n: int) -> int:
    mask = 0
    for bit, k in enumerate(MULTIPLIERS):
        if (n + 1) % k == 0:
            parent = (n + 1) // k
            if parent != k and member[parent]:
                mask |= 1 << bit
    return mask


def residue_stats(member: bytearray, modulus: int, start: int) -> list[tuple[int, int, int, int]]:
    """Return (residue, hits, samples, last_miss) rows."""
    limit = len(member) - 1
    rows = []
    for residue in range(modulus):
        first = start + ((residue - start) % modulus)
        hits = samples = 0
        last_miss = -1
        for n in range(first, limit + 1, modulus):
            samples += 1
            if member[n]:
                hits += 1
            else:
                last_miss = n
        rows.append((residue, hits, samples, last_miss))
    return rows


def gap_stats(member: bytearray, start: int) -> tuple[int, int, Counter[int]]:
    limit = len(member) - 1
    last = None
    max_gap = -1
    max_gap_end = -1
    gaps: Counter[int] = Counter()
    for n in range(max(0, start), limit + 1):
        if member[n]:
            if last is not None:
                gap = n - last
                gaps[gap] += 1
                if gap > max_gap:
                    max_gap = gap
                    max_gap_end = n
            last = n
    return max_gap, max_gap_end, gaps


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10_000_000)
    parser.add_argument("--start", type=int, default=1_000)
    parser.add_argument("--moduli", type=int, nargs="*", default=[30, 60, 90, 120, 180, 210, 360, 420, 840])
    args = parser.parse_args()

    member = generate(args.limit)
    prefix = 0
    checkpoints = {10**j for j in range(1, 10) if 10**j <= args.limit}
    print(f"limit={args.limit}")
    for n, value in enumerate(member):
        prefix += value
        if n in checkpoints:
            print(f"count[{n}]={prefix} density={prefix / n:.12f}")

    masks = Counter(parent_mask(member, n) for n in range(max(6, args.start), args.limit + 1) if member[n])
    print("parent_masks=" + ",".join(f"{mask}:{count}" for mask, count in sorted(masks.items())))

    max_gap, max_gap_end, gaps = gap_stats(member, args.start)
    print(f"max_gap={max_gap} interval=({max_gap_end - max_gap},{max_gap_end})")
    print("largest_gap_counts=" + ",".join(f"{gap}:{gaps[gap]}" for gap in sorted(gaps)[-20:]))

    for modulus in args.moduli:
        rows = residue_stats(member, modulus, args.start)
        full = [r for r, hits, samples, _ in rows if hits == samples]
        near = sorted(rows, key=lambda row: (row[2] - row[1], row[0]))[:10]
        print(f"modulus={modulus} full={len(full)}/{modulus} residues={full}")
        print("  near=" + ";".join(f"{r}:{hits}/{samples}:last_miss={last}" for r, hits, samples, last in near))


if __name__ == "__main__":
    main()
