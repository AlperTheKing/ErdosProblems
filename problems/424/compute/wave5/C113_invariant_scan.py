#!/usr/bin/env python3
"""Exact prefix tests for C113 moving-token packing invariants."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


GENERATED = 1
SPLITLESS = 2
HARD = 3


def require(condition: bool, message: object) -> None:
    if not condition:
        raise RuntimeError(message)


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def full_spf(limit: int) -> list[int]:
    spf = list(range(limit + 1))
    for p in range(2, math.isqrt(limit) + 1):
        if spf[p] != p:
            continue
        for multiple in range(p * p, limit + 1, p):
            if spf[multiple] == multiple:
                spf[multiple] = p
    return spf


def divisors(n: int, spf: list[int]) -> list[int]:
    result = [1]
    while n > 1:
        p = spf[n]
        old = tuple(result)
        power = 1
        while n % p == 0:
            n //= p
            power *= p
            result.extend(value * power for value in old)
    return result


def admissible_pairs(n: int, spf: list[int]) -> list[tuple[int, int]]:
    product = n + 1
    pairs = []
    for left in divisors(product, spf):
        if left < 2 or left * left >= product:
            continue
        right = product // left
        if allowed(left) and allowed(right):
            pairs.append((left, right))
    return sorted(pairs)


def seed_root(endpoint: int) -> int:
    require(endpoint > 1 and endpoint % 2 == 1, ("endpoint", endpoint))
    shifted = endpoint - 1
    return 1 + shifted // (shifted & -shifted)


def ceil_sqrt(n: int) -> int:
    root = math.isqrt(n)
    return root if root * root == n else root + 1


def failure_row(
    h: int,
    root: int,
    d: int,
    pairs: list[tuple[int, int]],
    missing_by_pair: list[list[tuple[int, int, int]]],
    **values: int,
) -> dict[str, object]:
    return {
        "X": h,
        "root": root,
        "d": d,
        "q": d - 1,
        "values": values,
        "pairs": [
            {
                "pair": list(pair),
                "missing": [
                    {"endpoint": endpoint, "root": witness, "root_state": state}
                    for endpoint, witness, state in missing
                ],
            }
            for pair, missing in zip(pairs, missing_by_pair, strict=True)
        ],
    }


def expanded_certificate(
    root: int,
    certificate: dict[str, int],
    spf: list[int],
    state: bytearray,
) -> dict[str, object]:
    source = certificate["source"]
    pairs = admissible_pairs(source, spf)
    rows = []
    for left, right in pairs:
        missing = []
        for endpoint in (left, right):
            if state[endpoint] == GENERATED:
                continue
            witness = seed_root(endpoint)
            missing.append(
                {"endpoint": endpoint, "root": witness, "root_state": int(state[witness])}
            )
        rows.append({"pair": [left, right], "missing": missing})
    endpoint = certificate["endpoint"]
    chain_ratio = (endpoint - 1) // (root - 1)
    require(chain_ratio > 0 and chain_ratio & (chain_ratio - 1) == 0, (root, endpoint))
    return {
        "root": root,
        "j": (root - 1).bit_length() - 1,
        "q": certificate["d"] - 1,
        "source": source,
        "endpoint": endpoint,
        "chain_depth": chain_ratio.bit_length() - 1,
        "pairs": rows,
    }


def run(limit: int) -> dict[str, object]:
    spf = full_spf(limit + 1)
    state = bytearray(limit + 1)
    reducible_even = bytearray(limit + 1)
    maximum_d: dict[int, int] = {}
    certificates: dict[int, dict[str, int]] = {}
    source_failures: dict[str, dict[str, object] | None] = {
        "lower_witness_roots_supply_weight": None,
        "lower_missing_endpoints_supply_weight": None,
        "proper_divisors_of_root_plus_one_supply_weight": None,
        "other_pair_small_factors_below_root_supply_weight": None,
    }
    totals = {
        "generated": 0,
        "structural_splitless": 0,
        "hard": 0,
        "maximum_pair_count": 0,
        "root_upgrade_events": 0,
    }

    for n in range(2, limit + 1):
        pairs: list[tuple[int, int]] = []
        current = 0
        if n in (2, 3):
            current = GENERATED
        elif allowed(n):
            pairs = admissible_pairs(n, spf)
            if any(state[a] == GENERATED and state[b] == GENERATED for a, b in pairs):
                current = GENERATED
            elif not pairs:
                current = SPLITLESS
            elif n % 2 == 0:
                product = n + 1
                seed_three_easy = (
                    product % 3 == 0
                    and product // 3 != 3
                    and allowed(product // 3)
                )
                if not seed_three_easy:
                    current = HARD
        state[n] = current
        if n % 2 == 0 and pairs and current != GENERATED:
            reducible_even[n] = 1
        if current == GENERATED:
            totals["generated"] += 1
        elif current == SPLITLESS:
            totals["structural_splitless"] += 1
        elif current == HARD:
            totals["hard"] += 1
            d = len(pairs)
            totals["maximum_pair_count"] = max(totals["maximum_pair_count"], d)
            missing_by_pair: list[list[tuple[int, int, int]]] = []
            reducible: dict[int, int] = {}
            all_missing: list[tuple[int, int]] = []
            for left, right in pairs:
                missing = []
                for endpoint in (left, right):
                    if state[endpoint] == GENERATED:
                        continue
                    witness = seed_root(endpoint)
                    require(state[witness] != GENERATED, (n, endpoint, witness))
                    missing.append((endpoint, witness, int(state[witness])))
                    all_missing.append((endpoint, witness))
                    if state[witness] != SPLITLESS:
                        reducible.setdefault(witness, endpoint)
                require(missing, ("unblocked", n, left, right))
                missing_by_pair.append(missing)

            all_roots = {witness for _, witness in all_missing}
            all_endpoints = {endpoint for endpoint, _ in all_missing}
            for root, endpoint in reducible.items():
                old_d = maximum_d.get(root, 0)
                if d <= old_d:
                    continue
                totals["root_upgrade_events"] += 1
                q = d - 1
                weight = ceil_sqrt(q)
                lower_roots = sum(witness < root for witness in all_roots)
                lower_endpoints = sum(value < root for value in all_endpoints)
                proper_divisors = len(divisors(root + 1, spf)) - 1
                target_pair_index = next(
                    index
                    for index, missing in enumerate(missing_by_pair)
                    if any(value == endpoint and witness == root for value, witness, _ in missing)
                )
                lower_small_factors = sum(
                    index != target_pair_index and left < root
                    for index, (left, _) in enumerate(pairs)
                )
                row = failure_row(
                    n,
                    root,
                    d,
                    pairs,
                    missing_by_pair,
                    weight=weight,
                    lower_roots=lower_roots,
                    lower_endpoints=lower_endpoints,
                    proper_divisors=proper_divisors,
                    lower_small_factors=lower_small_factors,
                    target_pair_index=target_pair_index,
                )
                if lower_roots < weight and source_failures["lower_witness_roots_supply_weight"] is None:
                    source_failures["lower_witness_roots_supply_weight"] = row
                if lower_endpoints < weight and source_failures["lower_missing_endpoints_supply_weight"] is None:
                    source_failures["lower_missing_endpoints_supply_weight"] = row
                if proper_divisors < weight and source_failures["proper_divisors_of_root_plus_one_supply_weight"] is None:
                    source_failures["proper_divisors_of_root_plus_one_supply_weight"] = row
                if lower_small_factors < weight and source_failures["other_pair_small_factors_below_root_supply_weight"] is None:
                    source_failures["other_pair_small_factors_below_root_supply_weight"] = row
                maximum_d[root] = d
                certificates[root] = {"source": n, "endpoint": endpoint, "d": d}

        if n % 2 and allowed(n) and current != GENERATED:
            parent = (n + 1) // 2
            require(allowed(parent) and state[parent] != GENERATED, (n, parent))

    bins: dict[int, list[tuple[int, int]]] = {}
    for root, d in maximum_d.items():
        if d < 2:
            continue
        bins.setdefault((root - 1).bit_length() - 1, []).append((root, d - 1))

    deadline_failures: dict[str, dict[str, int] | None] = {
        "moving_sqrt_excluding_least": None,
        "linear_excluding_least": None,
        "full_cap_excluding_least": None,
    }
    extrema: dict[str, dict[str, int] | None] = {
        "minimum_moving_sqrt_slack": None,
        "minimum_linear_slack": None,
        "minimum_full_cap_slack": None,
    }
    bin_rows = []
    nonleast_small_factor_failure = None
    gap_token_map_failure = None
    residue_gap_token_map_failure = None
    residue_gap_local_shortage = None
    residue_gap_degree_over_two = None
    maximum_residue_gap_degree = 0
    gap_token_maps = []
    for j, roots in sorted(bins.items()):
        roots.sort()
        root_set = {root for root, _ in roots}
        sqrt_prefix = 0
        linear_prefix = 0
        cap_prefix = 0
        extra_adjacency: dict[tuple[int, int], list[int]] = {}
        residue_extra_adjacency: dict[tuple[int, int], list[int]] = {}
        extra_gap_rows: dict[int, list[int]] = {}
        residue_gap_rows: dict[int, list[int]] = {}
        for index, (root, q) in enumerate(roots):
            if index == 0:
                continue
            certificate = certificates[root]
            source_pairs = admissible_pairs(certificate["source"], spf)
            endpoint = certificate["endpoint"]
            target_pair_index = next(
                pair_index
                for pair_index, pair in enumerate(source_pairs)
                if endpoint in pair
            )
            lower_small_factors = sum(
                pair_index != target_pair_index and left < root
                for pair_index, (left, _) in enumerate(source_pairs)
            )
            required_weight = min(ceil_sqrt(q), j)
            if lower_small_factors < required_weight and nonleast_small_factor_failure is None:
                nonleast_small_factor_failure = {
                    "X": limit,
                    "j": j,
                    "root": root,
                    "q": q,
                    "weight": required_weight,
                    "source": certificate["source"],
                    "endpoint": endpoint,
                    "target_pair": list(source_pairs[target_pair_index]),
                    "lower_small_factors": lower_small_factors,
                    "pairs": [list(pair) for pair in source_pairs],
                }
            candidate_gaps = sorted({
                root - left + 1
                for pair_index, (left, _) in enumerate(source_pairs)
                if pair_index != target_pair_index
                and (1 << j) + 2 <= root - left + 1 < root
                and root - left + 1 not in root_set
            })
            extra_gap_rows[root] = candidate_gaps
            residue_gaps = []
            for pair_index, (left, _) in enumerate(source_pairs):
                if pair_index == target_pair_index:
                    continue
                gap = (
                    root - left + 1
                    if left % 3 == root % 3
                    else root - 2 * left + 2
                )
                require(gap % 3 == 1, (root, left, gap))
                if (1 << j) + 2 <= gap < root:
                    residue_gaps.append(gap)
            residue_gaps = sorted(set(residue_gaps))
            residue_gap_rows[root] = residue_gaps
            extra_demand = max(required_weight - 2, 0)
            if len(residue_gaps) < extra_demand and residue_gap_local_shortage is None:
                residue_gap_local_shortage = {
                    "X": limit,
                    "j": j,
                    "root": root,
                    "q": q,
                    "extra_demand": extra_demand,
                    "candidate_gaps": residue_gaps,
                }
            for copy in range(extra_demand):
                token = (root, copy)
                extra_adjacency[token] = sorted(
                    slot
                    for gap in candidate_gaps
                    for slot in (gap - 2, gap - 1)
                )
                residue_extra_adjacency[token] = sorted(
                    slot
                    for gap in residue_gaps
                    for slot in (gap - 2, gap - 1)
                )
            sqrt_prefix += min(ceil_sqrt(q), j)
            linear_prefix += q
            cap_prefix += j
            rhs = root - (1 << j)
            values = {
                "X": limit,
                "j": j,
                "index": index + 1,
                "root": root,
                "q": q,
                "rhs": rhs,
            }
            for name, lhs in (
                ("moving_sqrt_excluding_least", sqrt_prefix),
                ("linear_excluding_least", linear_prefix),
                ("full_cap_excluding_least", cap_prefix),
            ):
                if lhs > rhs and deadline_failures[name] is None:
                    deadline_failures[name] = {**values, "lhs": lhs}
                extremum_name = "minimum_" + name.removesuffix("_excluding_least") + "_slack"
                row = {**values, "lhs": lhs, "slack": rhs - lhs}
                previous = extrema[extremum_name]
                if previous is None or row["slack"] < previous["slack"]:
                    extrema[extremum_name] = row
        slot_owner: dict[int, tuple[int, int]] = {}

        def augment(token: tuple[int, int], seen: set[int]) -> bool:
            for slot in extra_adjacency[token]:
                if slot in seen:
                    continue
                seen.add(slot)
                previous = slot_owner.get(slot)
                if previous is None or augment(previous, seen):
                    slot_owner[slot] = token
                    return True
            return False

        matched = 0
        for token in extra_adjacency:
            if augment(token, set()):
                matched += 1
                continue
            if gap_token_map_failure is None:
                root = token[0]
                gap_token_map_failure = {
                    "X": limit,
                    "j": j,
                    "root": root,
                    "token_copy": token[1],
                    "candidate_gaps": extra_gap_rows[root],
                    "candidate_slots": extra_adjacency[token],
                    "extra_tokens": len(extra_adjacency),
                    "matched_before_failure": matched,
                }
            break
        residue_slot_owner: dict[int, tuple[int, int]] = {}
        gap_users: dict[int, list[int]] = {}
        for root, gaps in residue_gap_rows.items():
            for gap in gaps:
                gap_users.setdefault(gap, []).append(root)
        for gap, users in gap_users.items():
            maximum_residue_gap_degree = max(maximum_residue_gap_degree, len(users))
            if len(users) > 2 and residue_gap_degree_over_two is None:
                residue_gap_degree_over_two = {
                    "X": limit,
                    "j": j,
                    "gap": gap,
                    "degree": len(users),
                    "roots": users,
                }

        def residue_augment(token: tuple[int, int], seen: set[int]) -> bool:
            for slot in residue_extra_adjacency[token]:
                if slot in seen:
                    continue
                seen.add(slot)
                previous = residue_slot_owner.get(slot)
                if previous is None or residue_augment(previous, seen):
                    residue_slot_owner[slot] = token
                    return True
            return False

        residue_matched = 0
        for token in residue_extra_adjacency:
            if residue_augment(token, set()):
                residue_matched += 1
                continue
            if residue_gap_token_map_failure is None:
                root = token[0]
                residue_gap_token_map_failure = {
                    "X": limit,
                    "j": j,
                    "root": root,
                    "token_copy": token[1],
                    "candidate_gaps": residue_gap_rows[root],
                    "candidate_slots": residue_extra_adjacency[token],
                    "extra_tokens": len(residue_extra_adjacency),
                    "matched_before_failure": residue_matched,
                }
            break
        if j <= 12:
            gap_token_maps.append({
                "j": j,
                "extra_token_count": len(extra_adjacency),
                "matched_count": matched,
                "residue_matched_count": residue_matched,
                "assignments": [
                    {"root": token[0], "copy": token[1], "slot": slot}
                    for slot, token in sorted(slot_owner.items())
                ],
            })
        bin_rows.append(
            {
                "j": j,
                "root_count": len(roots),
                "least_root": roots[0][0],
                "greatest_root": roots[-1][0],
                "moving_sqrt_load_excluding_least": sqrt_prefix,
                "linear_load_excluding_least": linear_prefix,
                "full_cap_load_excluding_least": cap_prefix,
            }
        )

    low_certificates = [
        expanded_certificate(root, certificate, spf, state)
        for root, certificate in sorted(certificates.items())
        if root <= 4096 and certificate["d"] >= 2
    ]

    active_bins: dict[int, list[int]] = {}
    for root in range(2, (limit + 1) // 2 + 1, 2):
        if reducible_even[root] and state[2 * root - 1] != GENERATED:
            active_bins.setdefault((root - 1).bit_length() - 1, []).append(root)
    active_failure = None
    active_extremum = None
    active_rows = []
    for j, roots in sorted(active_bins.items()):
        for index, root in enumerate(roots[1:], start=1):
            lhs = index * j
            rhs = root - (1 << j)
            row = {
                "classification_limit": limit,
                "j": j,
                "index": index + 1,
                "root": root,
                "lhs": lhs,
                "rhs": rhs,
                "slack": rhs - lhs,
            }
            if lhs > rhs and active_failure is None:
                active_failure = row
            if active_extremum is None or row["slack"] < active_extremum["slack"]:
                active_extremum = row
        active_rows.append(
            {
                "j": j,
                "root_count": len(roots),
                "least_root": roots[0],
                "greatest_root": roots[-1],
            }
        )

    return {
        "schema": "C113-moving-token-invariant-scan-v1",
        "limit": limit,
        "arithmetic": "exact integers only",
        "totals": totals,
        "source_invariant_first_failures": source_failures,
        "deadline_first_failures_at_limit": deadline_failures,
        "deadline_extrema_at_limit": extrema,
        "nonleast_max_certificate_small_factor_failure": nonleast_small_factor_failure,
        "pair_factor_gap_token_map": {
            "definition": "baseline r-1,r-2; extra pair factor a uses absent gap r-a+1",
            "first_failure": gap_token_map_failure,
            "low_bin_assignments": gap_token_maps,
        },
        "residue_forced_pair_factor_gap_token_map": {
            "definition": "baseline r-1,r-2; extra factor a uses the 1 mod 3 gap among r-a+1,r-2a+2",
            "first_failure": residue_gap_token_map_failure,
            "first_local_shortage": residue_gap_local_shortage,
            "first_gap_degree_over_two": residue_gap_degree_over_two,
            "maximum_gap_degree": maximum_residue_gap_degree,
        },
        "bins": bin_rows,
        "low_root_certificates": low_certificates,
        "active_reducible_full_cap": {
            "definition": "reducible even r with U(r)=2*r-1 missing",
            "maximum_root": (limit + 1) // 2,
            "first_failure": active_failure,
            "minimum_slack": active_extremum,
            "bins": active_rows,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(1_000 <= args.limit <= 10_000_000, ("limit", args.limit))
    payload = run(args.limit)
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("ascii")
    args.output.write_bytes(encoded)
    print(hashlib.sha256(encoded).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
