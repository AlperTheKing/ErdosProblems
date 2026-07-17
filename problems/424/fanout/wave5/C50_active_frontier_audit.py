#!/usr/bin/env python3
"""Exact audit of the active C46 seed-3 transport frontier.

The least grounded set is reconstructed in increasing order.  Every
generating factor pair is required to have distinct inputs (a < b).
Results are written as JSON to stdout so this lane creates no data files.
"""

from __future__ import annotations

import argparse
import json
import math
from array import array
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def spf_sieve(limit: int) -> array:
    spf = array("I", range(limit + 1))
    for p in range(2, math.isqrt(limit) + 1):
        if spf[p] != p:
            continue
        for multiple in range(p * p, limit + 1, p):
            if spf[multiple] == multiple:
                spf[multiple] = p
    return spf


def divisors(n: int, spf: array) -> list[int]:
    result = [1]
    while n > 1:
        p = spf[n]
        old_length = len(result)
        power = 1
        while n % p == 0:
            n //= p
            power *= p
            for i in range(old_length):
                result.append(result[i] * power)
    return result


def admissible_pairs(n: int, spf: array) -> Iterable[tuple[int, int]]:
    product = n + 1
    for a in divisors(product, spf):
        if a < 2:
            continue
        b = product // a
        if a < b and allowed(a) and allowed(b):
            yield a, b


def structural_parent(n: int) -> int | None:
    if n > 3 and n % 2:
        return (n + 1) // 2
    if n % 2 == 0 and (n + 1) % 3 == 0:
        q = (n + 1) // 3
        if allowed(q) and q != 3:
            return q
    return None


@dataclass
class Chain:
    start: int
    source_parent: int
    terminal_child: int | None
    terminal_parent: int | None
    frontier_state: int | None
    frontier_next: int | None
    frontier_kind: str | None
    root: int = 0
    leaf: int = 0

    @property
    def end(self) -> int:
        return self.terminal_child if self.terminal_child is not None else 0


def build_ground(limit: int) -> dict:
    spf = spf_sieve(limit + 1)
    member = bytearray(limit + 1)
    splitless = bytearray(limit + 1)
    q_event = bytearray(limit + 1)
    r3_event = bytearray(limit + 1)
    member[2] = member[3] = 1
    starts: list[tuple[int, int]] = []

    for n in range(4, limit + 1):
        if not allowed(n):
            continue
        has_pair = False
        generated = False
        for a, b in admissible_pairs(n, spf):
            has_pair = True
            if member[a] and member[b]:
                generated = True
                break
        if generated:
            member[n] = 1
            if n % 2:
                q = (n + 1) // 2
                if allowed(q) and not member[q]:
                    q_event[n] = 1
            elif (n + 1) % 3 == 0:
                q = (n + 1) // 3
                if q % 2 and allowed(q) and not member[q]:
                    r3_event[n] = 1
                    starts.append((n, q))
        elif not has_pair:
            splitless[n] = 1

    return {
        "spf": spf,
        "member": member,
        "splitless": splitless,
        "q_event": q_event,
        "r3_event": r3_event,
        "starts": starts,
    }


def trace_one(start: int, member: bytearray, limit: int) -> tuple[Chain, list[int]]:
    x = start
    path = [x]
    while True:
        if x % 2:
            following = 3 * x - 1
            if following > limit:
                return (
                    Chain(start, (start + 1) // 3, None, None, x, following, "odd"),
                    path,
                )
            if not member[following]:
                raise AssertionError(("seed-3 closure failure", x, following))
            x = following
            path.append(x)
            continue

        parent = 3 * x // 2
        child = 3 * x - 1
        if parent <= limit and member[parent]:
            x = parent
            path.append(x)
            continue
        if parent <= limit and not member[parent]:
            if child <= limit and not member[child]:
                raise AssertionError(("bad terminal membership", x, parent, child))
            if child != 2 * parent - 1:
                raise AssertionError(("bad terminal identity", x, parent, child))
            kind = None if child <= limit else "even_target_outside"
            frontier_state = None if child <= limit else x
            frontier_next = None if child <= limit else parent
            return (
                Chain(
                    start,
                    (start + 1) // 3,
                    child,
                    parent,
                    frontier_state,
                    frontier_next,
                    kind,
                ),
                path,
            )
        return (
            Chain(
                start,
                (start + 1) // 3,
                None,
                None,
                x,
                parent,
                "even_parent_outside",
            ),
            path,
        )


def trace_chains(data: dict, limit: int) -> tuple[list[Chain], dict]:
    member = data["member"]
    chains: list[Chain] = []
    terminal_children: set[int] = set()
    visited_owner: dict[int, int] = {}

    for start, source_parent in data["starts"]:
        chain, path = trace_one(start, member, limit)
        if chain.source_parent != source_parent:
            raise AssertionError(("bad source parent", start, source_parent))
        for state in path:
            old_owner = visited_owner.setdefault(state, start)
            if old_owner != start:
                raise AssertionError(("chain collision", old_owner, start, state))
        if chain.terminal_child is not None:
            if chain.terminal_child in terminal_children:
                raise AssertionError(("terminal collision", chain.terminal_child))
            terminal_children.add(chain.terminal_child)
        chains.append(chain)

    return chains, {
        "visited_states": len(visited_owner),
        "terminal_children_distinct": True,
        "state_collisions": 0,
    }


def root_of(n: int, member: bytearray, cache: dict[int, int]) -> int:
    path = []
    while n not in cache:
        path.append(n)
        parent = structural_parent(n)
        if parent is None:
            cache[n] = n
            break
        if member[parent]:
            raise AssertionError(("generated structural parent", n, parent))
        n = parent
    root = cache[n]
    for value in path:
        cache[value] = root
    return root


def least_obstruction_leaf(
    n: int,
    member: bytearray,
    splitless: bytearray,
    spf: array,
    cache: dict[int, int],
) -> int:
    path = []
    while n not in cache:
        path.append(n)
        if splitless[n]:
            cache[n] = n
            break
        missing = [
            x
            for a, b in admissible_pairs(n, spf)
            for x in (a, b)
            if not member[x]
        ]
        if not missing:
            raise AssertionError(("hole without blocker", n))
        n = min(missing)
    leaf = cache[n]
    for value in path:
        cache[value] = leaf
    return leaf


def event_overlap(chains: list[Chain], key: str, limit: int) -> dict:
    groups: dict[int, list[Chain]] = defaultdict(list)
    for chain in chains:
        groups[getattr(chain, key)].append(chain)

    first_collision = None
    global_max = {"multiplicity": 0, "cutoff": None, key: None}
    for value, rows in groups.items():
        events = []
        by_start = {}
        for row in rows:
            end = row.terminal_child if row.terminal_child is not None else limit + 1
            events.append((row.start, 1, row.start))
            events.append((end, -1, row.start))
            by_start[row.start] = row
        events.sort(key=lambda event: (event[0], event[1]))
        active: set[int] = set()
        for cutoff, sign, start in events:
            if cutoff > limit:
                break
            if sign < 0:
                active.remove(start)
                continue
            active.add(start)
            if len(active) >= 2 and (
                first_collision is None or cutoff < first_collision["cutoff"]
            ):
                first_collision = {
                    "cutoff": cutoff,
                    key: value,
                    "starts": sorted(active)[:2],
                }
            if len(active) > global_max["multiplicity"]:
                global_max = {
                    "multiplicity": len(active),
                    "cutoff": cutoff,
                    key: value,
                }

    if global_max["cutoff"] is not None:
        value = global_max[key]
        cutoff = global_max["cutoff"]
        active_at_max = sorted(
            row.start
            for row in groups[value]
            if row.start <= cutoff
            and (row.terminal_child is None or cutoff < row.terminal_child)
        )
        if len(active_at_max) != global_max["multiplicity"]:
            raise AssertionError(("overlap reconstruction", key, value, cutoff))
        global_max["sample_starts"] = active_at_max[:20]
        global_max["sample_truncated"] = len(active_at_max) > 20
    return {
        "number_of_images": len(groups),
        "first_collision": first_collision,
        "maximum_active_fiber": global_max,
    }


def witness(chain: Chain, member: bytearray, limit: int) -> dict:
    replay, path = trace_one(chain.start, member, limit)
    return {
        "start": chain.start,
        "source_parent": chain.source_parent,
        "terminal_child": replay.terminal_child,
        "terminal_parent": replay.terminal_parent,
        "frontier_state": replay.frontier_state,
        "frontier_next": replay.frontier_next,
        "frontier_kind": replay.frontier_kind,
        "path": path,
        "root": chain.root,
        "leaf": chain.leaf,
    }


def record_violation(audit: dict, cutoff: int, lhs: int, rhs: int, counts: dict) -> None:
    if lhs <= rhs:
        return
    row = {
        "cutoff": cutoff,
        "lhs": lhs,
        "rhs": rhs,
        "excess": lhs - rhs,
        **counts,
    }
    if audit["first_failure"] is None:
        audit["first_failure"] = row
    audit["last_failure"] = row
    if audit["maximum_excess"] is None or row["excess"] > audit["maximum_excess"]["excess"]:
        audit["maximum_excess"] = row


def sweep(data: dict, chains: list[Chain], limit: int) -> dict:
    splitless = data["splitless"]
    q_event = data["q_event"]
    r3_event = data["r3_event"]
    terminal_event = bytearray(limit + 1)
    for chain in chains:
        if chain.terminal_child is not None and chain.terminal_child <= limit:
            terminal_event[chain.terminal_child] = 1
            if not q_event[chain.terminal_child]:
                raise AssertionError(("terminal is not Q", chain.terminal_child))

    names = [
        "A<=E(floor((X+1)/3))",
        "R3<=E(floor((X+1)/3))",
        "A<=E(floor((X+1)/9))",
        "R3<=E(floor((X+1)/9))",
        "A<=E(floor((X+1)/27))",
        "R3<=E(floor((X+1)/27))",
        "A<=Q-T (equiv R3<=Q)",
        "fresh_R3_top_third<=A",
    ]
    audits = {
        name: {"first_failure": None, "last_failure": None, "maximum_excess": None}
        for name in names
    }
    checkpoints = {10**k for k in range(2, 8) if 10**k <= limit}
    checkpoints.add(limit)
    checkpoint_rows = []

    e_total = q_total = r3_total = terminal_total = 0
    scale_state = {
        3: {"pointer": 0, "E": 0, "R3": 0},
        9: {"pointer": 0, "E": 0, "R3": 0},
        27: {"pointer": 0, "E": 0, "R3": 0},
    }
    for x in range(2, limit + 1):
        e_total += splitless[x]
        q_total += q_event[x]
        r3_total += r3_event[x]
        terminal_total += terminal_event[x]
        active = r3_total - terminal_total

        for denominator, state in scale_state.items():
            argument = (x + 1) // denominator
            while state["pointer"] < argument:
                state["pointer"] += 1
                state["E"] += splitless[state["pointer"]]
                state["R3"] += r3_event[state["pointer"]]

        e3 = scale_state[3]["E"]
        e9 = scale_state[9]["E"]
        e27 = scale_state[27]["E"]
        fresh = r3_total - scale_state[3]["R3"]
        counts = {
            "A": active,
            "R3": r3_total,
            "T": terminal_total,
            "Q": q_total,
            "E_third": e3,
            "E_ninth": e9,
            "E_27th": e27,
            "fresh": fresh,
        }
        record_violation(audits[names[0]], x, active, e3, counts)
        record_violation(audits[names[1]], x, r3_total, e3, counts)
        record_violation(audits[names[2]], x, active, e9, counts)
        record_violation(audits[names[3]], x, r3_total, e9, counts)
        record_violation(audits[names[4]], x, active, e27, counts)
        record_violation(audits[names[5]], x, r3_total, e27, counts)
        record_violation(audits[names[6]], x, active, q_total - terminal_total, counts)
        record_violation(audits[names[7]], x, fresh, active, counts)

        if x in checkpoints:
            checkpoint_rows.append({"X": x, "E": e_total, **counts})

    return {"audits": audits, "checkpoints": checkpoint_rows}


def fixed_dilation_audit(chains: list[Chain], member: bytearray, limit: int) -> dict:
    result = {}
    for dilation in (3, 9, 27, 81, 243, 729, 1230, 1845, 2187):
        failure = None
        exact_tests = 0
        unresolved_before_failure = 0
        for chain in chains:
            horizon = dilation * chain.start
            if chain.terminal_child is not None:
                exact_tests += 1
                failed = chain.terminal_child > horizon
            elif horizon <= limit:
                exact_tests += 1
                failed = True
            else:
                unresolved_before_failure += 1
                continue
            if failed:
                failure = {
                    "cutoff": chain.start,
                    "dilation": dilation,
                    "horizon": horizon,
                    "chain": witness(chain, member, limit),
                }
                break
        result[str(dilation)] = {
            "exact_tests_until_failure": exact_tests,
            "unresolved_earlier_starts": unresolved_before_failure,
            "first_certified_failure": failure,
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10_000_000)
    args = parser.parse_args()
    if args.limit < 100:
        raise SystemExit("--limit must be at least 100")

    data = build_ground(args.limit)
    chains, transport_checks = trace_chains(data, args.limit)
    member = data["member"]
    splitless = data["splitless"]
    spf = data["spf"]

    root_cache: dict[int, int] = {}
    leaf_cache: dict[int, int] = {}
    for chain in chains:
        chain.root = root_of(chain.source_parent, member, root_cache)
        chain.leaf = least_obstruction_leaf(
            chain.source_parent, member, splitless, spf, leaf_cache
        )
        if not splitless[chain.leaf]:
            raise AssertionError(("nonsplitless leaf", chain.leaf))

    final_active = [
        chain
        for chain in chains
        if chain.terminal_child is None or chain.terminal_child > args.limit
    ]
    frontier_states = [chain.frontier_state for chain in final_active]
    if len(frontier_states) != len(set(frontier_states)):
        raise AssertionError("duplicate final frontier state")
    if any(state is None or 3 * state <= args.limit for state in frontier_states):
        raise AssertionError("frontier state outside (X/3,X]")

    first_hard_root = next(
        (chain for chain in chains if not splitless[chain.root]), None
    )
    first_immediate_q_failure = next(
        (
            chain
            for chain in chains
            if not member[2 * chain.source_parent - 1]
        ),
        None,
    )
    smallest_active = min(final_active, key=lambda chain: chain.start)
    unresolved = [chain for chain in final_active if chain.terminal_child is None]
    smallest_unresolved = min(unresolved, key=lambda chain: chain.start)
    known_terminals = [chain for chain in chains if chain.terminal_child is not None]
    largest_known_ratio = max(
        known_terminals,
        key=lambda chain: chain.terminal_child / chain.start,
    )

    root_overlap = event_overlap(chains, "root", args.limit)
    leaf_overlap = event_overlap(chains, "leaf", args.limit)
    for overlap, key in ((root_overlap, "root"), (leaf_overlap, "leaf")):
        collision = overlap["first_collision"]
        if collision is not None:
            collision["chains"] = [
                witness(next(c for c in chains if c.start == start), member, args.limit)
                for start in collision["starts"]
            ]
        maximum = overlap["maximum_active_fiber"]
        maximum["sample_chains"] = [
            witness(next(c for c in chains if c.start == start), member, args.limit)
            for start in maximum.get("sample_starts", [])
        ]

    output = {
        "schema_version": 1,
        "limit": args.limit,
        "algorithm": "SPF divisors and increasing least-grounded recursion",
        "distinct_input_rule": "every admissible pair satisfies 2<=a<b",
        "transport_checks": transport_checks,
        "sweep": sweep(data, chains, args.limit),
        "component_root_charge": {
            "first_hard_root": (
                witness(first_hard_root, member, args.limit)
                if first_hard_root is not None
                else None
            ),
            **root_overlap,
        },
        "least_blocker_leaf_charge": leaf_overlap,
        "immediate_Q_charge": {
            "rule": "start 3q-1 maps to 2q-1 when that child is generated",
            "first_failure": (
                {
                    **witness(first_immediate_q_failure, member, args.limit),
                    "candidate_Q_child": 2 * first_immediate_q_failure.source_parent - 1,
                }
                if first_immediate_q_failure is not None
                else None
            ),
        },
        "fixed_dilation_terminal_charge": fixed_dilation_audit(
            chains, member, args.limit
        ),
        "final_frontier": {
            "active": len(final_active),
            "frontier_type_counts": dict(
                Counter(chain.frontier_kind for chain in final_active)
            ),
            "minimum_frontier_state": min(frontier_states),
            "frontier_interval": f"({args.limit}/3,{args.limit}]",
            "smallest_active_start": witness(
                smallest_active, member, args.limit
            ),
            "smallest_unresolved_start": witness(
                smallest_unresolved, member, args.limit
            ),
            "unresolved_terminal_ratio_lower_bound": {
                "numerator": args.limit,
                "denominator": smallest_unresolved.start,
                "strict": True,
            },
            "largest_known_terminal_ratio": {
                "numerator": largest_known_ratio.terminal_child,
                "denominator": largest_known_ratio.start,
                "chain": witness(largest_known_ratio, member, args.limit),
            },
        },
    }
    json.dump(output, fp=__import__("sys").stdout, indent=2, sort_keys=True)
    print()


if __name__ == "__main__":
    main()
