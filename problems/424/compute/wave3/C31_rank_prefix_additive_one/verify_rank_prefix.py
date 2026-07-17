#!/usr/bin/env python3
"""Independent exact C31 rank-prefix and local seed-2-chain audit."""

from __future__ import annotations

import argparse
import json
from array import array
from collections import Counter
from pathlib import Path

INF = 65535


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def spf_sieve(limit: int) -> array:
    spf = array("I", range(limit + 1))
    for p in range(2, int(limit**0.5) + 1):
        if spf[p] != p:
            continue
        for m in range(p * p, limit + 1, p):
            if spf[m] == m:
                spf[m] = p
    return spf


def divisors(n: int, spf: array) -> list[int]:
    out = [1]
    while n > 1:
        p = spf[n]
        old = len(out)
        power = 1
        while n % p == 0:
            n //= p
            power *= p
            for i in range(old):
                out.append(out[i] * power)
    return out


def pairs_for(n: int, spf: array) -> list[tuple[int, int]]:
    product = n + 1
    out = []
    for a in divisors(product, spf):
        if a < 2:
            continue
        b = product // a
        if a < b and allowed(a) and allowed(b):
            out.append((a, b))
    return out


def hard_shape(n: int, pairs: list[tuple[int, int]]) -> bool:
    if n % 2 or not pairs:
        return False
    if (n + 1) % 3:
        return True
    q = (n + 1) // 3
    return not (allowed(q) and q != 3)


def seed2_target(q: int, rank_cap: int, cutoff: int, member: bytearray,
                 depth: array) -> tuple[int, int] | None:
    """First healed boundary in at most two seed-2 steps."""
    c1 = 2 * q - 1
    if c1 <= cutoff and member[c1]:
        return c1, q
    if c1 <= cutoff and allowed(c1) and not member[c1] and depth[c1] <= rank_cap:
        c2 = 2 * c1 - 1
        if c2 <= cutoff and member[c2]:
            return c2, c1
    return None


def augment(source: int, edges: list[list[int]], match_t: list[int],
            seen: list[int], stamp: int) -> bool:
    for target in edges[source]:
        if seen[target] == stamp:
            continue
        seen[target] = stamp
        owner = match_t[target]
        if owner < 0 or augment(owner, edges, match_t, seen, stamp):
            match_t[target] = source
            return True
    return False


def audit(limit: int) -> dict:
    spf = spf_sieve(limit + 1)
    member = bytearray(limit + 1)
    depth = array("H", [INF]) * (limit + 1)
    member[2] = member[3] = 1
    source_records: list[dict] = []
    target_records: list[dict] = []
    target_index: dict[int, int] = {}

    max_rank = 64
    hard_by_rank = [0] * max_rank
    healed_by_rank = [0] * max_rank
    strict_failures: list[dict] = []
    plus_one_failures: list[dict] = []
    maximum_excess = 0
    maximum_event = None
    available: list[list[int]] = [[] for _ in range(max_rank)]
    greedy_matches: list[dict] = []
    greedy_unmatched: list[dict] = []
    hard_scan = 0
    healed_le2 = 0
    low_rank_max_deficit = 0
    low_rank_max_event = None
    low_rank_last_positive = None

    for n in range(4, limit + 1):
        if not allowed(n):
            continue
        pairs = pairs_for(n, spf)
        generated = any(member[a] and member[b] for a, b in pairs)
        if generated:
            member[n] = 1
            if n % 2:
                q = (n + 1) // 2
                if allowed(q) and not member[q]:
                    r = depth[q]
                    if r == INF or r >= max_rank:
                        raise AssertionError(("bad target rank", n, q, r))
                    idx = len(target_records)
                    target_records.append({"child": n, "parent": q, "rank": r})
                    target_index[n] = idx
                    healed_by_rank[r] += 1
                    if r <= 2:
                        healed_le2 += 1
                    available[r].append(idx)
            continue

        if not pairs:
            depth[n] = 0
        else:
            blockers = []
            for a, b in pairs:
                missing = [depth[x] for x in (a, b) if not member[x]]
                if not missing or any(x == INF for x in missing):
                    raise AssertionError(("invalid blocker", n, a, b, missing))
                blockers.append(min(missing))
            depth[n] = 1 + max(blockers)

        if not hard_shape(n, pairs):
            continue

        r = depth[n]
        if r >= max_rank:
            raise AssertionError(("bad source rank", n, r))
        missing_endpoints = sorted({
            q for a, b in pairs for q in (a, b) if not member[q]
        })
        critical_endpoints = sorted({
            q for a, b in pairs
            if min(depth[x] for x in (a, b) if not member[x]) == r - 1
            for q in (a, b) if not member[q] and depth[q] == r - 1
        })

        all_targets = sorted({
            hit[0]
            for q in missing_endpoints
            for hit in [seed2_target(q, r, n, member, depth)]
            if hit is not None
        })
        critical_targets = sorted({
            hit[0]
            for q in critical_endpoints
            for hit in [seed2_target(q, r, n, member, depth)]
            if hit is not None
        })
        for child in all_targets:
            if child not in target_index:
                raise AssertionError(("unregistered target", n, child))
        record = {
            "value": n,
            "rank": r,
            "pairs": pairs,
            "missing_endpoints": missing_endpoints,
            "critical_endpoints": critical_endpoints,
            "all_chain_targets": all_targets,
            "critical_chain_targets": critical_targets,
        }
        source_records.append(record)
        hard_by_rank[r] += 1
        hard_scan += 1
        low_deficit = hard_scan - healed_le2
        if low_deficit > low_rank_max_deficit:
            low_rank_max_deficit = low_deficit
            low_rank_max_event = {"X": n, "H": hard_scan, "Q_le2": healed_le2}
        if low_deficit > 0:
            low_rank_last_positive = {"X": n, "deficit": low_deficit}

        hcum = qcum = 0
        for d in range(max_rank):
            hcum += hard_by_rank[d]
            qcum += healed_by_rank[d]
            excess = hcum - qcum
            if excess > maximum_excess:
                maximum_excess = excess
                maximum_event = {"X": n, "rank": d, "H": hcum, "Q": qcum}
            if excess > 0:
                strict_failures.append({"X": n, "rank": d, "excess": excess})
            if excess > 1:
                plus_one_failures.append({"X": n, "rank": d, "excess": excess})

        chosen = None
        for d in range(r, -1, -1):
            if available[d]:
                chosen = available[d].pop()
                break
        if chosen is None:
            greedy_unmatched.append({"value": n, "rank": r})
        else:
            greedy_matches.append({
                "source": n,
                "source_rank": r,
                **target_records[chosen],
            })

    def local_matching(field: str) -> dict:
        edges = [[target_index[c] for c in rec[field]] for rec in source_records]
        match_t = [-1] * len(target_records)
        seen = [0] * len(target_records)
        matched = 0
        unmatched = []
        for s in range(len(source_records)):
            if augment(s, edges, match_t, seen, s + 1):
                matched += 1
            else:
                unmatched.append({
                    "value": source_records[s]["value"],
                    "rank": source_records[s]["rank"],
                    "degree": len(edges[s]),
                })
        return {
            "matched": matched,
            "unmatched": len(source_records) - matched,
            "unmatched_prefix": unmatched[:100],
            "zero_degree": sum(not row for row in edges),
            "edge_count": sum(map(len, edges)),
        }

    strict_unique = []
    seen_fail = set()
    for item in strict_failures:
        key = (item["X"], item["rank"])
        if key not in seen_fail:
            seen_fail.add(key)
            strict_unique.append(item)

    combined_records = source_records + target_records
    result = {
        "schema_version": 1,
        "limit": limit,
        "rank_definition": (
            "splitless hole=0; reducible hole=1+max over admissible pairs "
            "of min obstruction depth among missing endpoints"
        ),
        "hard_definition": (
            "even reducible hole outside the admissible nonseed factor-3 class"
        ),
        "target_definition": (
            "event child=2q-1<=X generated, parent q missing; target rank=rank(q)"
        ),
        "hard_total": len(source_records),
        "healed_total": len(target_records),
        "maximum_rank": max([0] + [x["rank"] for x in combined_records]),
        "rank_prefix": {
            "maximum_excess": maximum_excess,
            "maximum_event": maximum_event,
            "strict_failure_events": len(strict_failures),
            "strict_failure_prefix": strict_unique[:20],
            "plus_one_failure_events": len(plus_one_failures),
        },
        "all_hard_vs_healed_rank_le2": {
            "maximum_deficit": low_rank_max_deficit,
            "maximum_event": low_rank_max_event,
            "last_positive_event": low_rank_last_positive,
            "terminal_deficit": hard_scan - healed_le2,
        },
        "online_rank_greedy": {
            "matched": len(greedy_matches),
            "unmatched": len(greedy_unmatched),
            "unmatched_prefix": greedy_unmatched[:100],
            "sample_matches": greedy_matches[:30],
        },
        "critical_two_step_matching": local_matching("critical_chain_targets"),
        "all_endpoint_two_step_matching": local_matching("all_chain_targets"),
        "first_sources": source_records[:50],
        "rank_histogram_hard": dict(sorted(Counter(
            x["rank"] for x in source_records
        ).items())),
        "rank_histogram_healed": dict(sorted(Counter(
            x["rank"] for x in target_records
        ).items())),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.limit < 100:
        raise ValueError("limit must be at least 100")
    result = audit(args.limit)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "limit": result["limit"],
        "hard_total": result["hard_total"],
        "healed_total": result["healed_total"],
        "rank_prefix": result["rank_prefix"],
        "online_rank_greedy": result["online_rank_greedy"],
        "critical_two_step_matching": result["critical_two_step_matching"],
        "all_endpoint_two_step_matching": result["all_endpoint_two_step_matching"],
    }, indent=2))


if __name__ == "__main__":
    main()




