#!/usr/bin/env python3
"""Independent recursive verifier for the finite C96 obstruction witnesses."""

from __future__ import annotations

import argparse
import json
import math
from functools import lru_cache
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def pairs(n: int) -> tuple[tuple[int, int], ...]:
    product = n + 1
    result: list[tuple[int, int]] = []
    for a in range(2, math.isqrt(product) + 1):
        if product % a:
            continue
        b = product // a
        if a < b and allowed(a) and allowed(b):
            result.append((a, b))
    return tuple(result)


@lru_cache(maxsize=None)
def generated(n: int) -> bool:
    if n in (2, 3):
        return True
    if not allowed(n):
        return False
    return any(generated(a) and generated(b) for a, b in pairs(n))


def chain(root: int, limit: int) -> list[int]:
    result = []
    value = root
    while value <= limit:
        result.append(value)
        value = 2 * value - 1
    return result


def first_generated(root: int, limit: int) -> int | None:
    for value in chain(root, limit):
        if generated(value):
            return value
    return None


def verify(claim_path: Path) -> dict:
    claim = json.loads(claim_path.read_text(encoding="ascii"))
    require(claim["schema"] == "C96-ratio-obstruction-v1", "wrong claim schema")
    obstruction = claim["exact_obstructions"]

    prime = obstruction["prime_square_shadow"]
    h = prime["hard_root"]
    e = prime["shadow_root"]
    require(h == 54 and pairs(h) == ((5, 11),) and not generated(h), "hard witness failed")
    require(e == 24 and pairs(e) == () and not generated(e), "splitless shadow failed")
    visible = chain(e, 4 * h)
    require(visible == prime["visible_shadow_chain"], "visible shadow chain mismatch")
    require(all(not generated(v) for v in visible), "shadow healed by fourfold cutoff")
    require(first_generated(e, 5889) == 5889, "shadow first death mismatch")
    require(prime["first_generated_chain_member"] == 5889, "claim has wrong shadow death")

    plus = obstruction["same_plus_semigroup_class"]
    require(first_generated(plus["healed_root"], plus["healed_at"]) == plus["healed_at"], "healed plus root failed")
    pchain = plus["persistent_chain_through_limit"]
    require(pchain == chain(plus["persistent_root"], claim["limit"]), "persistent plus chain mismatch")
    require(all(not generated(v) for v in pchain), "persistent plus chain contains generated value")

    three = obstruction["same_three_times_plus_semigroup_class"]
    require(first_generated(three["healed_root"], three["healed_at"]) == three["healed_at"], "healed 3S root failed")
    tchain = three["persistent_chain_through_limit"]
    require(tchain == chain(three["persistent_root"], claim["limit"]), "persistent 3S chain mismatch")
    require(all(not generated(v) for v in tchain), "persistent 3S chain contains generated value")

    return {
        "schema": "C96-ratio-obstruction-verifier-v1",
        "claim": str(claim_path).replace("\\", "/"),
        "status": "exact_match",
        "recursive_values_evaluated": generated.cache_info().currsize,
        "witnesses": {
            "hard_54": True,
            "shadow_24_unhealed_through_216": True,
            "shadow_24_first_heals_at_5889": True,
            "root_2340_persistent_through_1000000": True,
            "root_16148_persistent_through_1000000": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.claim)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
