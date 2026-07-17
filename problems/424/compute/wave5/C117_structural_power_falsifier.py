#!/usr/bin/env python3
"""Exact sparse-template stress test for the C112 structural power target."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations
from typing import Iterable

import sympy


OTHER = 0
GENERATED = 1
SPLITLESS = 2
HARD = 3
STATE_NAME = {
    OTHER: "other_hole",
    GENERATED: "generated",
    SPLITLESS: "structural_splitless",
    HARD: "hard",
}
ALPHA_GATE = 1.0 / (2.0 * math.log(2.0))

BASE_FACTORS = {3: 1, 13: 1, 43: 1, 557: 1, 2213: 1}
BASE_N = math.prod(prime**exponent for prime, exponent in BASE_FACTORS.items())
BASE_H = BASE_N - 1

KNOWN_HARD = {
    38_624_780: (12, 4),
    908_368_614: (16, 9),
    2_067_138_956: (8, 0),
    2_796_867_114: (16, 8),
    2_934_744_174: (18, 14),
}


def allowed(value: int) -> bool:
    return value >= 2 and value % 3 != 1


def hard_shape(product: int) -> str | None:
    if product % 3 == 1:
        return "R"
    if product % 9 == 3 and (product // 3) % 3 == 1:
        return "3R"
    return None


def seed_root(value: int) -> int:
    if value < 3 or value % 2 == 0:
        raise ValueError(("seed_root_requires_odd", value))
    lowbit = (value - 1) & -(value - 1)
    return 1 + (value - 1) // lowbit


def normalize_factors(items: Iterable[tuple[int, int]]) -> dict[int, int]:
    result: dict[int, int] = {}
    for prime, exponent in items:
        if exponent <= 0:
            continue
        result[int(prime)] = result.get(int(prime), 0) + int(exponent)
    return dict(sorted(result.items()))


def product_from_factors(factors: dict[int, int]) -> int:
    return math.prod(prime**exponent for prime, exponent in factors.items())


def divisors_from_factors(factors: dict[int, int]) -> tuple[int, ...]:
    divisors = [1]
    for prime, exponent in sorted(factors.items()):
        old = tuple(divisors)
        power = 1
        for _ in range(exponent):
            power *= prime
            divisors.extend(value * power for value in old)
    return tuple(sorted(divisors))


def pairs_from_product_factors(
    factors: dict[int, int],
) -> tuple[tuple[int, int], ...]:
    product = product_from_factors(factors)
    return tuple(
        (left, product // left)
        for left in divisors_from_factors(factors)
        if 2 <= left < product // left
        and allowed(left)
        and allowed(product // left)
    )


class ClosureClassifier:
    def __init__(self) -> None:
        self.state_cache: dict[int, int] = {2: GENERATED, 3: GENERATED}
        self.pair_cache: dict[int, tuple[tuple[int, int], ...]] = {}
        self.factorint_calls = 0

    def factor_pairs(self, value: int) -> tuple[tuple[int, int], ...]:
        cached = self.pair_cache.get(value)
        if cached is not None:
            return cached
        self.factorint_calls += 1
        factors = {int(p): int(e) for p, e in sympy.factorint(value + 1).items()}
        pairs = pairs_from_product_factors(factors)
        self.pair_cache[value] = pairs
        return pairs

    def state(self, value: int) -> int:
        cached = self.state_cache.get(value)
        if cached is not None:
            return cached
        if not allowed(value):
            self.state_cache[value] = OTHER
            return OTHER
        pairs = self.factor_pairs(value)
        for left, right in pairs:
            if self.state(left) == GENERATED and self.state(right) == GENERATED:
                self.state_cache[value] = GENERATED
                return GENERATED
        if not pairs:
            result = SPLITLESS
        elif value % 2 == 0 and hard_shape(value + 1) is not None:
            result = HARD
        else:
            result = OTHER
        self.state_cache[value] = result
        return result

    def classify_source(
        self, factors: dict[int, int], detailed: bool = False
    ) -> dict[str, object]:
        product = product_from_factors(factors)
        source = product - 1
        pairs = pairs_from_product_factors(factors)
        endpoint_states: list[tuple[int, int, int, int]] = []
        generated_witness = None
        for left, right in pairs:
            left_state = self.state(left)
            right_state = self.state(right)
            endpoint_states.append((left, right, left_state, right_state))
            if left_state == GENERATED and right_state == GENERATED:
                generated_witness = (left, right)
                break
        if generated_witness is not None:
            return {
                "h": source,
                "N": product,
                "state": STATE_NAME[GENERATED],
                "d": len(pairs),
                "generated_witness": list(generated_witness),
            }
        if not pairs:
            source_state = SPLITLESS
        elif source % 2 == 0 and hard_shape(product) is not None:
            source_state = HARD
        else:
            source_state = OTHER
        if source_state != HARD:
            return {
                "h": source,
                "N": product,
                "state": STATE_NAME[source_state],
                "d": len(pairs),
                "generated_witness": None,
            }

        pair_rows = []
        structural_count = 0
        root_counts: Counter[str] = Counter()
        endpoint_counts: Counter[str] = Counter()
        pair_type_counts: Counter[str] = Counter()
        for left, right, left_state, right_state in endpoint_states:
            endpoints = []
            states = []
            structural = False
            for endpoint, endpoint_state in ((left, left_state), (right, right_state)):
                state_name = STATE_NAME[endpoint_state]
                endpoint_counts[state_name] += 1
                states.append(state_name)
                if endpoint_state == GENERATED:
                    root = None
                    root_state = None
                else:
                    root = seed_root(endpoint)
                    root_state_code = self.state(root)
                    if root_state_code == GENERATED:
                        raise AssertionError(("hole_has_generated_seed_root", endpoint, root))
                    root_state = STATE_NAME[root_state_code]
                    root_counts[root_state] += 1
                    structural = structural or root_state_code == SPLITLESS
                if detailed:
                    endpoints.append({
                        "value": endpoint,
                        "state": state_name,
                        "root": root,
                        "root_state": root_state,
                    })
            pair_type_counts["+".join(sorted(states))] += 1
            structural_count += int(structural)
            if detailed:
                pair_rows.append({
                    "pair": [left, right],
                    "endpoints": endpoints,
                    "counted_in_s": structural,
                })

        d_value = len(pairs)
        s_value = structural_count
        ratio_b8 = math.log(s_value + 8) / math.log(d_value) if d_value > 1 else None
        ratio_b0 = (
            math.log(max(1, s_value)) / math.log(d_value) if d_value > 1 else None
        )
        result: dict[str, object] = {
            "h": source,
            "N": product,
            "state": STATE_NAME[HARD],
            "shape": hard_shape(product),
            "d": d_value,
            "s": s_value,
            "deficit": d_value - s_value,
            "target_3_4": {
                "lhs": (s_value + 8) ** 4,
                "rhs": d_value**3,
                "falsifier": (s_value + 8) ** 4 < d_value**3,
            },
            "ratios": {
                "B0": ratio_b0,
                "B8": ratio_b8,
                "B8_minus_alpha_gate": (
                    None if ratio_b8 is None else ratio_b8 - ALPHA_GATE
                ),
            },
            "taxonomy": {
                "endpoint_states": dict(sorted(endpoint_counts.items())),
                "missing_root_states": dict(sorted(root_counts.items())),
                "pair_types": dict(sorted(pair_type_counts.items())),
                "structural_pairs": s_value,
                "nonstructural_pairs": d_value - s_value,
            },
        }
        if detailed:
            result["pairs"] = pair_rows
        return result


@dataclass(frozen=True)
class Candidate:
    family: str
    template: str
    factors: tuple[tuple[int, int], ...]
    parent_N: int | None = None

    @property
    def factor_dict(self) -> dict[int, int]:
        return dict(self.factors)

    @property
    def N(self) -> int:
        return product_from_factors(self.factor_dict)


class CandidateBuilder:
    def __init__(self, min_source: int, max_bits: int) -> None:
        self.min_source = min_source
        self.max_bits = max_bits
        self.candidates: list[Candidate] = []
        self.seen_N: set[int] = set()
        self.generation: dict[str, Counter[str]] = defaultdict(Counter)

    def add(
        self,
        family: str,
        template: str,
        factors: dict[int, int],
        parent_N: int | None = None,
    ) -> bool:
        stats = self.generation[family]
        stats["offered"] += 1
        normalized = normalize_factors(factors.items())
        product = product_from_factors(normalized)
        if product - 1 <= self.min_source:
            stats["too_small"] += 1
            return False
        if product.bit_length() > self.max_bits:
            stats["too_large"] += 1
            return False
        if hard_shape(product) is None:
            stats["wrong_shape"] += 1
            return False
        if product in self.seen_N:
            stats["duplicate"] += 1
            return False
        self.seen_N.add(product)
        self.candidates.append(
            Candidate(family, template, tuple(normalized.items()), parent_N)
        )
        stats["accepted"] += 1
        return True


def merge_factors(*factor_maps: dict[int, int]) -> dict[int, int]:
    return normalize_factors(
        (prime, exponent)
        for factor_map in factor_maps
        for prime, exponent in factor_map.items()
    )


def random_distinct(
    rng: random.Random, pool: list[int], count: int, excluded: set[int] | None = None
) -> list[int]:
    excluded = excluded or set()
    available = [prime for prime in pool if prime not in excluded]
    return rng.sample(available, count)


def fill_random_family(
    builder: CandidateBuilder,
    family: str,
    budget: int,
    sampler,
) -> None:
    start = builder.generation[family]["accepted"]
    attempts = 0
    while builder.generation[family]["accepted"] - start < budget:
        attempts += 1
        if attempts > max(100, 100 * budget):
            break
        template, factors = sampler()
        builder.add(family, template, factors)


def build_candidates(args: argparse.Namespace) -> tuple[CandidateBuilder, list[int], list[int]]:
    rng = random.Random(args.seed)
    plus = [
        int(p) for p in sympy.primerange(5, args.prime_limit + 1) if int(p) % 3 == 1
    ]
    minus = [
        int(p) for p in sympy.primerange(5, args.prime_limit + 1) if int(p) % 3 == 2
    ]
    if len(plus) < 12 or len(minus) < 12:
        raise ValueError("prime limit leaves pools too small")
    rng.shuffle(plus)
    rng.shuffle(minus)
    builder = CandidateBuilder(args.min_source, args.max_bits)

    usable_plus = [p for p in plus if p not in BASE_FACTORS]
    power_patterns = (2, 3, 4)
    for prime in usable_plus:
        for exponent in power_patterns:
            if builder.generation["base_prime_power"]["accepted"] >= args.base_power_budget:
                break
            builder.add(
                "base_prime_power",
                f"N0*p^{exponent}",
                merge_factors(BASE_FACTORS, {prime: exponent}),
            )
        if builder.generation["base_prime_power"]["accepted"] >= args.base_power_budget:
            break

    multi_patterns = (
        ((1, 1), "N0*p*q"),
        ((1, 1, 1), "N0*p*q*r"),
        ((2, 1), "N0*p^2*q"),
        ((1, 1, 1, 1), "N0*p*q*r*t"),
    )

    def sample_base_multi() -> tuple[str, dict[int, int]]:
        exponents, label = rng.choice(multi_patterns)
        primes = random_distinct(rng, usable_plus, len(exponents))
        return label, merge_factors(BASE_FACTORS, dict(zip(primes, exponents)))

    fill_random_family(
        builder, "base_multi_plus", args.base_multi_budget, sample_base_multi
    )

    squarefree_specs = (
        ("squarefree_R", 2, 4),
        ("squarefree_R", 2, 5),
        ("squarefree_R", 4, 2),
        ("squarefree_R", 4, 3),
        ("squarefree_R", 6, 1),
        ("squarefree_3R", 2, 3),
        ("squarefree_3R", 2, 4),
        ("squarefree_3R", 4, 1),
        ("squarefree_3R", 4, 2),
        ("squarefree_3R", 6, 0),
    )

    def sample_squarefree() -> tuple[str, dict[int, int]]:
        family, minus_count, plus_count = rng.choice(squarefree_specs)
        factors = {prime: 1 for prime in random_distinct(rng, minus, minus_count)}
        factors.update({prime: 1 for prime in random_distinct(rng, plus, plus_count)})
        if family == "squarefree_3R":
            factors[3] = 1
        return f"{family}:m{minus_count}:p{plus_count}", factors

    fill_random_family(
        builder, "squarefree", args.squarefree_budget, sample_squarefree
    )

    minus_patterns = ((2,), (1, 1), (1, 3), (2, 2), (1, 1, 2))
    plus_patterns = ((2,), (3,), (2, 1), (4,), (2, 2), (3, 1, 1))

    def sample_prime_power() -> tuple[str, dict[int, int]]:
        minus_exponents = rng.choice(minus_patterns)
        plus_exponents = rng.choice(plus_patterns)
        minus_primes = random_distinct(rng, minus, len(minus_exponents))
        plus_primes = random_distinct(rng, plus, len(plus_exponents))
        factors = dict(zip(minus_primes, minus_exponents))
        factors.update(dict(zip(plus_primes, plus_exponents)))
        mode = rng.choice(("R", "3R"))
        if mode == "3R":
            factors[3] = 1
        label = (
            f"prime_power_{mode}:m{','.join(map(str, minus_exponents))}:"
            f"p{','.join(map(str, plus_exponents))}"
        )
        return label, factors

    fill_random_family(
        builder, "prime_power", args.prime_power_budget, sample_prime_power
    )

    recurrent_core = {3: 1, 13: 1, 43: 1, 557: 1}
    composite_q_patterns = (
        ((1, 1, 1), (), "q=m1*m2*m3"),
        ((3,), (), "q=m^3"),
        ((1,), (2,), "q=m*p^2"),
        ((1, 2), (1,), "q=m1*m2^2*p"),
        ((1, 1, 1), (1,), "q=m1*m2*m3*p"),
    )

    def sample_composite_q() -> tuple[str, dict[int, int]]:
        minus_exponents, plus_exponents, label = rng.choice(composite_q_patterns)
        minus_primes = random_distinct(
            rng, minus, len(minus_exponents), set(recurrent_core)
        )
        plus_primes = random_distinct(
            rng, plus, len(plus_exponents), set(recurrent_core)
        )
        q_factors = dict(zip(minus_primes, minus_exponents))
        q_factors.update(dict(zip(plus_primes, plus_exponents)))
        return label, merge_factors(recurrent_core, q_factors)

    fill_random_family(
        builder, "composite_q", args.composite_q_budget, sample_composite_q
    )

    known_base_factors = {
        source + 1: {int(p): int(e) for p, e in sympy.factorint(source + 1).items()}
        for source in KNOWN_HARD
    }
    if args.extra_seed_claim:
        with open(args.extra_seed_claim, "r", encoding="ascii") as handle:
            seed_claim = json.load(handle)
        for record in seed_claim["verification_records"]:
            if record["state"] != "hard":
                raise ValueError(("nonhard_extra_seed", record["N"]))
            known_base_factors[int(record["N"])] = {
                int(prime): int(exponent)
                for prime, exponent in record["factors"].items()
            }
    known_products = list(sorted(known_base_factors))
    sorted_plus = sorted(plus)
    sorted_minus = sorted(minus)

    slot_specs = [
        (base_product, old_prime, exponent)
        for base_product in known_products
        for old_prime, exponent in known_base_factors[base_product].items()
        if old_prime != 3
    ]
    slot_start = builder.generation["hard_slot_sweep"]["accepted"]
    slot_index = 0
    while (
        builder.generation["hard_slot_sweep"]["accepted"] - slot_start
        < args.slot_sweep_budget
    ):
        added_this_layer = 0
        for base_product, old_prime, exponent in slot_specs:
            pool = sorted_plus if old_prime % 3 == 1 else sorted_minus
            if slot_index >= len(pool):
                continue
            new_prime = pool[slot_index]
            factors = dict(known_base_factors[base_product])
            factors.pop(old_prime)
            if new_prime in factors:
                continue
            factors[new_prime] = exponent
            added_this_layer += int(builder.add(
                "hard_slot_sweep",
                f"base={base_product - 1}:slot={old_prime}^{exponent}->{new_prime}^{exponent}",
                factors,
                base_product,
            ))
            if (
                builder.generation["hard_slot_sweep"]["accepted"] - slot_start
                >= args.slot_sweep_budget
            ):
                break
        slot_index += 1
        if added_this_layer == 0 and slot_index >= max(len(sorted_plus), len(sorted_minus)):
            break

    fiber_specs = [
        (base_product, operation)
        for base_product in known_products
        for operation in ("plus_square", "plus_pair", "neutral_minus_pair", "plus_cube")
    ]
    fiber_start = builder.generation["cross_seed_fiber"]["accepted"]
    fiber_index = 0
    while (
        builder.generation["cross_seed_fiber"]["accepted"] - fiber_start
        < args.fiber_sweep_budget
    ):
        added_this_layer = 0
        for base_product, operation in fiber_specs:
            factors = dict(known_base_factors[base_product])
            if operation in ("plus_square", "plus_pair", "plus_cube"):
                pool = sorted_plus
            else:
                pool = sorted_minus
            if fiber_index >= len(pool):
                continue
            variable = pool[fiber_index]
            if variable in factors:
                continue
            if operation == "plus_square":
                factors[variable] = 2
            elif operation == "plus_cube":
                factors[variable] = 3
            elif operation == "plus_pair":
                fixed_choices = [p for p in sorted_plus if p not in factors and p != variable]
                if not fixed_choices:
                    continue
                factors[variable] = 1
                factors[fixed_choices[0]] = 1
            else:
                fixed_choices = [p for p in sorted_minus if p not in factors and p != variable]
                if not fixed_choices:
                    continue
                factors[variable] = 1
                factors[fixed_choices[0]] = 1
            added_this_layer += int(builder.add(
                "cross_seed_fiber",
                f"base={base_product - 1}:op={operation}:p={variable}",
                factors,
                base_product,
            ))
            if (
                builder.generation["cross_seed_fiber"]["accepted"] - fiber_start
                >= args.fiber_sweep_budget
            ):
                break
        fiber_index += 1
        if added_this_layer == 0 and fiber_index >= max(len(sorted_plus), len(sorted_minus)):
            break

    def substituted_known_factors() -> tuple[int, dict[int, int], list[tuple[int, int]]]:
        base_product = rng.choice(known_products)
        factors = dict(known_base_factors[base_product])
        replaceable = [prime for prime in factors if prime != 3]
        replacement_count = rng.randint(1, min(3, len(replaceable)))
        old_primes = rng.sample(replaceable, replacement_count)
        old_rows = [(prime, factors.pop(prime)) for prime in old_primes]
        replacements = []
        for old_prime, exponent in old_rows:
            pool = plus if old_prime % 3 == 1 else minus
            choices = [prime for prime in pool if prime not in factors]
            new_prime = rng.choice(choices)
            factors[new_prime] = exponent
            replacements.append((old_prime, new_prime))
        return base_product, factors, replacements

    def sample_shape_substitution() -> tuple[str, dict[int, int]]:
        base_product, factors, replacements = substituted_known_factors()
        labels = ",".join(f"{old}->{new}" for old, new in replacements)
        return f"base={base_product - 1}:sub={labels}", factors

    fill_random_family(
        builder,
        "hard_shape_substitution",
        args.shape_substitution_budget,
        sample_shape_substitution,
    )

    def sample_shape_expansion() -> tuple[str, dict[int, int]]:
        base_product, factors, replacements = substituted_known_factors()
        operation = rng.choice(
            ("split", "power_raise", "neutral_minus_pair", "plus_square", "split_raise")
        )
        if operation in ("split", "split_raise"):
            splittable = [prime for prime, exponent in factors.items() if prime != 3 and exponent == 1]
            target = rng.choice(splittable)
            factors.pop(target)
            if target % 3 == 1 and rng.randrange(2):
                new_primes = random_distinct(rng, plus, 2, set(factors))
            elif target % 3 == 1:
                new_primes = random_distinct(rng, minus, 2, set(factors))
            else:
                first = random_distinct(rng, minus, 1, set(factors))[0]
                second = random_distinct(rng, plus, 1, set(factors) | {first})[0]
                new_primes = [first, second]
            for prime in new_primes:
                factors[prime] = 1
            if operation == "split_raise":
                raised = rng.choice(new_primes)
                factors[raised] += 1 if raised % 3 == 1 else 2
        elif operation == "power_raise":
            target = rng.choice([prime for prime in factors if prime != 3])
            factors[target] += 1 if target % 3 == 1 else 2
        elif operation == "neutral_minus_pair":
            for prime in random_distinct(rng, minus, 2, set(factors)):
                factors[prime] = 1
        else:
            prime = random_distinct(rng, plus, 1, set(factors))[0]
            factors[prime] = 2
        labels = ",".join(f"{old}->{new}" for old, new in replacements)
        return f"base={base_product - 1}:sub={labels}:op={operation}", factors

    fill_random_family(
        builder,
        "hard_shape_expansion",
        args.shape_expansion_budget,
        sample_shape_expansion,
    )

    def sample_extremal_lift() -> tuple[str, dict[int, int]]:
        base_product = rng.choice(known_products)
        base_factors = known_base_factors[base_product]
        pattern = rng.choice(((2,), (1, 1), (3,), (2, 1)))
        primes = random_distinct(rng, plus, len(pattern), set(base_factors))
        return (
            f"base={base_product - 1}:plus={','.join(map(str, pattern))}",
            merge_factors(base_factors, dict(zip(primes, pattern))),
        )

    fill_random_family(
        builder, "extremal_base_lift", args.extremal_lift_budget, sample_extremal_lift
    )
    return builder, plus, minus


def score_key(record: dict[str, object]) -> tuple[float, int, int, int]:
    ratio = record["ratios"]["B8"]  # type: ignore[index]
    return (float("inf") if ratio is None else float(ratio), -int(record["d"]), int(record["s"]), int(record["N"]))


def lightweight_record(candidate: Candidate, audit: dict[str, object]) -> dict[str, object]:
    return {
        "family": candidate.family,
        "template": candidate.template,
        "parent_N": candidate.parent_N,
        "factors": {str(p): e for p, e in candidate.factors},
        **audit,
    }


def evaluate_candidates(
    candidates: list[Candidate],
    classifier: ClosureClassifier,
    min_d: int,
    max_pairs: int,
    family_stats: dict[str, Counter[str]],
    digest: hashlib._Hash,
    progress_every: int,
) -> list[dict[str, object]]:
    hard_records: list[dict[str, object]] = []
    for index, candidate in enumerate(candidates, 1):
        stats = family_stats[candidate.family]
        factors = candidate.factor_dict
        pairs = pairs_from_product_factors(factors)
        d_value = len(pairs)
        stats["evaluated"] += 1
        stats["min_d"] = d_value if "min_d" not in stats else min(stats["min_d"], d_value)
        stats["max_d"] = max(stats["max_d"], d_value)
        if d_value < min_d:
            stats["below_min_d"] += 1
            continue
        if d_value > max_pairs:
            stats["above_max_pairs"] += 1
            continue
        audit = classifier.classify_source(factors)
        state_name = str(audit["state"])
        stats[state_name] += 1
        digest.update(
            json.dumps(
                [candidate.family, candidate.N, state_name, audit.get("d"), audit.get("s")],
                separators=(",", ":"),
            ).encode("ascii")
        )
        if state_name == "hard":
            record = lightweight_record(candidate, audit)
            hard_records.append(record)
            stats["target_falsifiers"] += int(audit["target_3_4"]["falsifier"])  # type: ignore[index]
            stats["max_hard_d"] = max(stats["max_hard_d"], d_value)
            stats["max_hard_deficit"] = max(
                stats["max_hard_deficit"], int(audit["deficit"])
            )
        if progress_every and index % progress_every == 0:
            print(
                f"evaluated={index}/{len(candidates)} hard={len(hard_records)} "
                f"states={len(classifier.state_cache)}",
                file=sys.stderr,
                flush=True,
            )
    return hard_records


def mutate_hard_records(
    args: argparse.Namespace,
    builder: CandidateBuilder,
    hard_records: list[dict[str, object]],
    plus: list[int],
    minus: list[int],
) -> list[Candidate]:
    if not hard_records or args.mutation_budget <= 0:
        return []
    rng = random.Random(args.seed ^ 0xC117)
    parents = sorted(hard_records, key=score_key)[: min(32, len(hard_records))]
    start = len(builder.candidates)
    attempts = 0
    while len(builder.candidates) - start < args.mutation_budget:
        attempts += 1
        if attempts > 200 * args.mutation_budget:
            break
        parent = rng.choice(parents)
        factors = {int(p): int(e) for p, e in parent["factors"].items()}  # type: ignore[union-attr]
        replaceable = [prime for prime in factors if prime != 3]
        old_prime = rng.choice(replaceable)
        exponent = factors.pop(old_prime)
        pool = plus if old_prime % 3 == 1 else minus
        choices = [prime for prime in pool if prime not in factors]
        if not choices:
            continue
        new_prime = rng.choice(choices)
        factors[new_prime] = exponent
        builder.add(
            "hard_shape_mutation",
            f"replace_{old_prime}_by_{new_prime}",
            factors,
            int(parent["N"]),
        )
    return builder.candidates[start:]


def select_extremals(
    hard_records: list[dict[str, object]], limit: int
) -> list[dict[str, object]]:
    selected: dict[int, dict[str, object]] = {}
    by_d: dict[int, dict[str, object]] = {}
    by_family: dict[str, dict[str, object]] = {}
    for record in hard_records:
        d_value = int(record["d"])
        current = by_d.get(d_value)
        if current is None or (int(record["s"]), int(record["N"])) < (
            int(current["s"]),
            int(current["N"]),
        ):
            by_d[d_value] = record
        family = str(record["family"])
        current = by_family.get(family)
        if current is None or score_key(record) < score_key(current):
            by_family[family] = record
    for record in sorted(hard_records, key=score_key)[:limit]:
        selected[int(record["N"])] = record
    for record in by_d.values():
        selected[int(record["N"])] = record
    for record in by_family.values():
        selected[int(record["N"])] = record
    falsifiers = [
        record
        for record in hard_records
        if bool(record["target_3_4"]["falsifier"])  # type: ignore[index]
    ]
    for record in falsifiers:
        selected[int(record["N"])] = record
    return sorted(selected.values(), key=score_key)


def self_test() -> dict[str, object]:
    classifier = ClosureClassifier()
    rows = []
    for source, expected in KNOWN_HARD.items():
        factors = {int(p): int(e) for p, e in sympy.factorint(source + 1).items()}
        audit = classifier.classify_source(factors)
        actual = (int(audit["d"]), int(audit["s"]))
        if audit["state"] != "hard" or actual != expected:
            raise AssertionError(("known_hard_mismatch", source, expected, audit))
        if classifier.state(source) != HARD:
            raise AssertionError(("full_recursive_source_mismatch", source))
        rows.append({"h": source, "d": actual[0], "s": actual[1]})
    if seed_root(557) != 140 or seed_root(2213) != 554:
        raise AssertionError("seed-root formula")
    return {
        "status": "PASS",
        "known_hard": rows,
        "recursive_state_entries": len(classifier.state_cache),
    }


def run_search(args: argparse.Namespace) -> dict[str, object]:
    tests = self_test()
    builder, plus, minus = build_candidates(args)
    classifier = ClosureClassifier()
    family_stats: dict[str, Counter[str]] = defaultdict(Counter)
    candidate_digest = hashlib.sha256()
    initial_candidates = list(builder.candidates)
    hard_records = evaluate_candidates(
        initial_candidates,
        classifier,
        args.min_d,
        args.max_pairs,
        family_stats,
        candidate_digest,
        args.progress_every,
    )
    mutations = mutate_hard_records(args, builder, hard_records, plus, minus)
    hard_records.extend(
        evaluate_candidates(
            mutations,
            classifier,
            args.min_d,
            args.max_pairs,
            family_stats,
            candidate_digest,
            args.progress_every,
        )
    )

    selected = select_extremals(hard_records, args.extremal_limit)
    detailed_records = []
    for record in selected:
        factors = {int(p): int(e) for p, e in record["factors"].items()}  # type: ignore[union-attr]
        candidate = Candidate(
            str(record["family"]),
            str(record["template"]),
            tuple(sorted(factors.items())),
            record.get("parent_N"),  # type: ignore[arg-type]
        )
        detailed_records.append(
            lightweight_record(candidate, classifier.classify_source(factors, detailed=True))
        )

    by_d = []
    for d_value in sorted({int(record["d"]) for record in hard_records}):
        subset = [record for record in hard_records if int(record["d"]) == d_value]
        best = min(subset, key=lambda record: (int(record["s"]), int(record["N"])))
        by_d.append({
            "d": d_value,
            "hard_count": len(subset),
            "min_s": int(best["s"]),
            "max_deficit": max(int(record["deficit"]) for record in subset),
            "best_h": int(best["h"]),
            "best_N": int(best["N"]),
            "best_family": str(best["family"]),
            "best_template": str(best["template"]),
            "best_ratio_B8": float(best["ratios"]["B8"]),  # type: ignore[index]
            "target_falsifier_count": sum(
                int(record["target_3_4"]["falsifier"]) for record in subset  # type: ignore[index]
            ),
        })

    detail_digest = hashlib.sha256(
        json.dumps(detailed_records, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    all_falsifiers = [
        record
        for record in hard_records
        if bool(record["target_3_4"]["falsifier"])  # type: ignore[index]
    ]
    generation = {
        family: dict(sorted(stats.items()))
        for family, stats in sorted(builder.generation.items())
    }
    evaluation = {
        family: dict(sorted(stats.items()))
        for family, stats in sorted(family_stats.items())
    }
    largest_source = max((candidate.N - 1 for candidate in builder.candidates), default=None)
    largest_hard = max((int(record["h"]) for record in hard_records), default=None)
    return {
        "schema": "C117-structural-power-falsifier-v1",
        "acceptance": {
            "exact_recursive_closure": True,
            "source_divisors_from_explicit_prime_powers": True,
            "target_3_4_falsifier_iff": "(s+8)^4 < d^3",
            "floating_point_used_for_acceptance": False,
            "alpha_gate": ALPHA_GATE,
            "finite_nonfalsification_is_theorem": False,
        },
        "parameters": {
            key: value
            for key, value in vars(args).items()
            if key != "output"
        },
        "self_test": tests,
        "prime_pools": {"plus": len(plus), "minus": len(minus)},
        "generation": generation,
        "evaluation": evaluation,
        "summary": {
            "initial_candidates": len(initial_candidates),
            "mutation_candidates": len(mutations),
            "evaluated_candidates": sum(stats["evaluated"] for stats in family_stats.values()),
            "hard_candidates": len(hard_records),
            "target_3_4_falsifiers": len(all_falsifiers),
            "largest_source_tested": largest_source,
            "largest_hard_source": largest_hard,
            "maximum_hard_d": max((int(record["d"]) for record in hard_records), default=None),
            "maximum_hard_deficit": max((int(record["deficit"]) for record in hard_records), default=None),
            "minimum_ratio_B8": min(
                (float(record["ratios"]["B8"]) for record in hard_records if record["ratios"]["B8"] is not None),  # type: ignore[index]
                default=None,
            ),
        },
        "extremal_by_d": by_d,
        "falsifiers": sorted(all_falsifiers, key=score_key),
        "verification_records": detailed_records,
        "digests": {
            "evaluated_stream_sha256": candidate_digest.hexdigest(),
            "verification_records_sha256": detail_digest,
        },
        "classifier_cache": {
            "state_entries": len(classifier.state_cache),
            "factor_pair_entries": len(classifier.pair_cache),
            "factorint_calls": classifier.factorint_calls,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=424117)
    parser.add_argument("--prime-limit", type=int, default=2000)
    parser.add_argument("--min-source", type=int, default=4_000_000_000)
    parser.add_argument("--max-bits", type=int, default=63)
    parser.add_argument("--min-d", type=int, default=12)
    parser.add_argument("--max-pairs", type=int, default=512)
    parser.add_argument("--base-power-budget", type=int, default=300)
    parser.add_argument("--base-multi-budget", type=int, default=1200)
    parser.add_argument("--squarefree-budget", type=int, default=1800)
    parser.add_argument("--prime-power-budget", type=int, default=1800)
    parser.add_argument("--composite-q-budget", type=int, default=1200)
    parser.add_argument("--slot-sweep-budget", type=int, default=12000)
    parser.add_argument("--fiber-sweep-budget", type=int, default=12000)
    parser.add_argument("--shape-substitution-budget", type=int, default=2400)
    parser.add_argument("--shape-expansion-budget", type=int, default=3000)
    parser.add_argument("--extremal-lift-budget", type=int, default=1200)
    parser.add_argument("--mutation-budget", type=int, default=600)
    parser.add_argument("--extremal-limit", type=int, default=24)
    parser.add_argument("--progress-every", type=int, default=250)
    parser.add_argument("--extra-seed-claim")
    parser.add_argument("--output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_search(args)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with open(args.output, "w", encoding="ascii", newline="\n") as handle:
            handle.write(payload)
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
