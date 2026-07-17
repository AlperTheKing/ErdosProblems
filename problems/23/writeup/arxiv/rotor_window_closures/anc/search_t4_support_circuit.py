"""Search a sharp abstract t=4 support circuit around the forced K2,3 core.

This is deliberately only a support-family gate, not a graph realization.
Eight fixed atoms are the four v-b_i and four m-b_i rows sharing their final
tail edges.  Eight mutable four-edge rows must complete a 16/15
inclusion-minimal defect-one family.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import random
from hashlib import sha256
from itertools import combinations
from pathlib import Path


N_EDGES = 15
ALL = (1 << N_EDGES) - 1
V = tuple(range(0, 4))
M = tuple(range(4, 8))
T = tuple(range(8, 12))
I0, I1, I2 = 12, 13, 14


def bits(items):
    out = 0
    for item in items:
        out |= 1 << item
    return out


FIXED = tuple(bits((V[0], I0, I2, T[i])) for i in range(4)) + tuple(
    bits((M[0], I1, I2, T[i])) for i in range(4)
)
FOUR_SETS = tuple(bits(c) for c in combinations(range(N_EDGES), 4))
RARE = (V[1], V[2], V[3], M[1], M[2], M[3])
CORE = tuple(e for e in range(N_EDGES) if e not in RARE)


def audit(rows):
    """Return (largest proper deficiency, witness mask, full union)."""
    unions = [0] * (1 << len(rows))
    worst = -10**9
    witness = 0
    full_mask = (1 << len(rows)) - 1
    for mask in range(1, full_mask + 1):
        lsb = mask & -mask
        i = lsb.bit_length() - 1
        unions[mask] = unions[mask ^ lsb] | rows[i]
        if mask != full_mask:
            defect = mask.bit_count() - unions[mask].bit_count()
            if defect > worst:
                worst = defect
                witness = mask
    return worst, witness, unions[full_mask]


def edge_degrees(rows):
    return tuple(sum((row >> e) & 1 for row in rows) for e in range(N_EDGES))


def worker(args):
    seed, rounds = args
    rng = random.Random(seed)
    for step in range(rounds):
        # Each of the six owner-star edges not used by the fixed rows appears
        # four times.  The fourth coordinate is randomized over the already
        # present core, so every candidate has full support and no private edge.
        offset = rng.randrange(len(RARE))
        mutable = []
        for j in range(8):
            rare = tuple(RARE[(offset + j + k) % len(RARE)] for k in range(3))
            mutable.append(bits(rare + (rng.choice(CORE),)))
        current = tuple(FIXED + tuple(mutable))
        worst, _, union = audit(current)
        if worst <= 0 and union == ALL:
            degrees = edge_degrees(current)
            if min(degrees) >= 2:
                return {"seed": seed, "step": step, "rows": current,
                        "degrees": degrees, "worstProperDefect": worst}
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--seeds", type=int, default=64)
    parser.add_argument("--rounds", type=int, default=200)
    parser.add_argument("--output", type=Path, required=True)
    ns = parser.parse_args()
    assert 1 <= ns.workers <= 8
    with mp.Pool(ns.workers) as pool:
        for hit in pool.imap_unordered(worker, ((s, ns.rounds) for s in range(ns.seeds))):
            if hit is None:
                continue
            rows = tuple(hit["rows"])
            worst, witness, union = audit(rows)
            assert worst <= 0 and union == ALL and min(edge_degrees(rows)) >= 2
            payload = {
                "schema": "T4_SUPPORT_CIRCUIT_K23_V1",
                "scope": "abstract support family; not a graph cage",
                "edges": {
                    "vStar": V, "mStar": M, "sharedTail": T,
                    "internal": (I0, I1, I2),
                },
                "rows": [sorted(e for e in range(N_EDGES) if (row >> e) & 1)
                         for row in rows],
                "fixedRows": 8,
                "edgeDegrees": list(edge_degrees(rows)),
                "fullAtoms": 16,
                "fullSupport": union.bit_count(),
                "fullDefect": 16 - union.bit_count(),
                "worstProperDefect": worst,
                "worstProperMask": witness,
                "seed": hit["seed"],
                "step": hit["step"],
            }
            canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
            payload["canonicalSha256"] = sha256(canonical.encode("ascii")).hexdigest()
            ns.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
            print("HIT", payload["canonicalSha256"], "seed", hit["seed"], "step", hit["step"])
            pool.terminate()
            return
    print("NO_HIT")


if __name__ == "__main__":
    main()
