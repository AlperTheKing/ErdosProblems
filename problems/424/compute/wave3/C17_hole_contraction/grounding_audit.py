#!/usr/bin/env python3
"""Audit whether a finite forward-closed certificate is grounded from 2 and 3."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path


def allowed(value: int) -> bool:
    return value >= 2 and value % 3 != 1


def admissible_pairs(n: int) -> list[tuple[int, int]]:
    product = n + 1
    result = []
    for left in range(2, math.isqrt(product) + 1):
        if product % left:
            continue
        right = product // left
        if left < right and allowed(left) and allowed(right):
            result.append((left, right))
    return result


def audit(certificate_path: Path) -> dict:
    raw = certificate_path.read_bytes()
    certificate = json.loads(raw)
    limit = int(certificate["limit"])
    members = set(map(int, certificate["members"]))
    values = [n for n in range(2, limit + 1) if allowed(n)]
    pairs = {n: admissible_pairs(n) for n in values}

    if 2 not in members or 3 not in members:
        raise AssertionError("certificate omits a seed")
    if any(n not in values for n in members):
        raise AssertionError("certificate contains a disallowed value")

    closure_violations = []
    for n in values:
        for left, right in pairs[n]:
            if left in members and right in members and n not in members:
                closure_violations.append((left, right, n))
    if closure_violations:
        raise AssertionError(closure_violations[:5])

    unsupported = []
    for n in sorted(members - {2, 3}):
        if not any(left in members and right in members for left, right in pairs[n]):
            unsupported.append(n)

    grounded = {2, 3}
    rank = {2: 0, 3: 0}
    witness = {}
    for n in values:
        if n in grounded or n not in members:
            continue
        candidates = [
            (1 + max(rank[left], rank[right]), left, right)
            for left, right in pairs[n]
            if left in grounded and right in grounded
        ]
        if candidates:
            best = min(candidates)
            rank[n] = best[0]
            witness[n] = (best[1], best[2])
            grounded.add(n)

    # Recompute the least closure independently, without consulting membership.
    least = {2, 3}
    for n in values:
        if n in least:
            continue
        if any(left in least and right in least for left, right in pairs[n]):
            least.add(n)
    if grounded != least:
        raise AssertionError("grounded core differs from the least closure")

    half = (limit + 1) // 2
    third = (limit + 1) // 3
    reducible = {n for n in values if pairs[n]}

    def contraction_row(member_set: set[int]) -> dict:
        holes = set(values) - member_set
        r = len(holes & reducible)
        m_half = sum(n <= half for n in holes)
        m_third = sum(n <= third for n in holes)
        return {
            "member_count": len(member_set),
            "hole_count": len(holes),
            "R": r,
            "Mhalf": m_half,
            "Mthird": m_third,
            "excess": r - m_half - m_third,
        }

    rank_counts = Counter(rank.values())
    rank_histogram = [rank_counts[i] for i in range(max(rank_counts) + 1)]
    witness_sample = [
        {
            "n": n,
            "left": witness[n][0],
            "right": witness[n][1],
            "rank": rank[n],
        }
        for n in sorted(witness)[:32]
    ]
    ungrounded = sorted(members - grounded)

    return {
        "schema_version": 1,
        "source": str(certificate_path).replace("\\", "/"),
        "source_sha256": hashlib.sha256(raw).hexdigest().upper(),
        "limit": limit,
        "forward_closed": True,
        "grounded": not ungrounded,
        "certificate_member_count": len(members),
        "grounded_member_count": len(grounded),
        "ungrounded_member_count": len(ungrounded),
        "locally_unsupported_member_count": len(unsupported),
        "first_ungrounded_members": ungrounded[:32],
        "first_locally_unsupported_members": unsupported[:32],
        "certificate_contraction": contraction_row(members),
        "grounded_core_contraction": contraction_row(grounded),
        "grounded_rank_histogram": rank_histogram,
        "grounded_witness_sample": witness_sample,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    result = audit(args.certificate)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(
        f"limit={result['limit']} grounded={result['grounded']} "
        f"members={result['certificate_member_count']} "
        f"grounded_members={result['grounded_member_count']} "
        f"ungrounded={result['ungrounded_member_count']}"
    )


if __name__ == "__main__":
    main()
