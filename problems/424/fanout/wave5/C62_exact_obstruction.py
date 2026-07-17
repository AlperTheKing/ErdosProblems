#!/usr/bin/env python3
"""Pure-integer replay of the C62 chain-local Hall obstruction at X=74."""

from __future__ import annotations

import json
from pathlib import Path


X = 74
INITIAL = {2, 3, 21, 32, 35, 62, 63, 68}
EXPECTED_T = {
    2, 3, 5, 9, 14, 17, 21, 26, 27, 32, 33, 35, 41, 44, 50, 51,
    53, 62, 63, 65, 68, 69,
}


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def admissible_pairs(n: int) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    for a in range(2, n + 1):
        if a * a >= n + 1:
            break
        if (n + 1) % a == 0:
            b = (n + 1) // a
            if allowed(a) and allowed(b):
                out.append((a, b))
    return out


def closure_prefix(initial: set[int], limit: int) -> set[int]:
    current = set(initial)
    changed = True
    while changed:
        changed = False
        old = sorted(current)
        for i, a in enumerate(old):
            for b in old[i + 1 :]:
                n = a * b - 1
                if n > limit:
                    break
                if n not in current:
                    current.add(n)
                    changed = True
    return {n for n in current if n <= limit}


def hard_shape(n: int) -> bool:
    ps = admissible_pairs(n)
    if n % 2 or not ps:
        return False
    if (n + 1) % 3:
        return True
    q = (n + 1) // 3
    return not (allowed(q) and q != 3)


def chain_root(n: int) -> int:
    while n % 2:
        n = (n + 1) // 2
    return n


def chain(root: int, limit: int) -> list[int]:
    out = [root]
    while 2 * out[-1] - 1 <= limit:
        out.append(2 * out[-1] - 1)
    return out


def healed_nonhard_roots(tset: set[int], limit: int) -> list[int]:
    out = []
    for root in range(2, limit + 1, 2):
        if not allowed(root) or root in tset or hard_shape(root):
            continue
        row = chain(root, limit)
        if row[-1] in tset:
            out.append(root)
    return out


def descent_reach(source: int, tset: set[int], limit: int) -> set[int]:
    """Full chain-local descent closure used in the obstruction lemma.

    From an absent even root r, inspect every absent member of its seed-2
    chain through X.  For every admissible factorization of that member,
    descend to the seed-2 chain root of every absent endpoint.  This includes
    all missing-factor descents, all seed-3 descents, and all unary descents
    with a present cofactor.
    """
    reached = {source}
    todo = [source]
    while todo:
        root = todo.pop()
        for n in chain(root, limit):
            if n in tset:
                break
            for a, b in admissible_pairs(n):
                for q in (a, b):
                    if q not in tset:
                        child_root = chain_root(q)
                        if child_root not in reached:
                            reached.add(child_root)
                            todo.append(child_root)
    return reached


def main() -> None:
    if any(not allowed(n) for n in INITIAL):
        raise RuntimeError("initial set contains a forbidden residue")
    for n in INITIAL - {2, 3}:
        if not admissible_pairs(n):
            raise RuntimeError(("initial nonseed is structurally splitless", n))

    tset = closure_prefix(INITIAL, X)
    if tset != EXPECTED_T:
        raise RuntimeError(("unexpected closure prefix", sorted(tset)))
    values = {n for n in range(2, X + 1) if allowed(n)}
    holes = values - tset
    splitless = {n for n in values - {2, 3} if not admissible_pairs(n)}
    if splitless & tset:
        raise RuntimeError(("splitless value entered T", sorted(splitless & tset)))

    hard_holes = sorted(n for n in holes if hard_shape(n))
    if hard_holes != [54, 74]:
        raise RuntimeError(("unexpected hard holes", hard_holes))

    boundary_parents = sorted(
        m for m in holes if 2 * m - 1 <= X and 2 * m - 1 in tset
    )
    if boundary_parents != [11, 18]:
        raise RuntimeError(("unexpected seed-2 boundaries", boundary_parents))
    healed = healed_nonhard_roots(tset, X)
    if healed != [6, 18]:
        raise RuntimeError(("unexpected healed roots", healed))

    reach = {h: descent_reach(h, tset, X) for h in hard_holes}
    reachable_targets = {h: sorted(reach[h] & set(healed)) for h in hard_holes}
    if reachable_targets != {54: [6], 74: [6]}:
        raise RuntimeError(("unexpected reachable targets", reachable_targets))

    payload = {
        "cutoff": X,
        "initial_generators": sorted(INITIAL),
        "T_prefix": sorted(tset),
        "holes_prefix": sorted(holes),
        "hard_unhealed_roots": hard_holes,
        "boundary_parents": boundary_parents,
        "healed_nonhard_roots": healed,
        "descent_reach": {str(h): sorted(reach[h]) for h in hard_holes},
        "reachable_healed_targets": {
            str(h): reachable_targets[h] for h in hard_holes
        },
        "hall_set": hard_holes,
        "hall_neighborhood": sorted(set().union(*map(set, reachable_targets.values()))),
        "SCB_counts": {"H": len(hard_holes), "Q": len(boundary_parents)},
    }
    if len(payload["hall_neighborhood"]) >= len(hard_holes):
        raise RuntimeError("chain-local Hall obstruction did not replay")
    if payload["SCB_counts"] != {"H": 2, "Q": 2}:
        raise RuntimeError("SCB equality did not replay")

    output = Path(__file__).with_name("C62_exact_obstruction.json")
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
