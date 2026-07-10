"""Parallel exact stress test of the safe-chord diameter-two invariant."""

from __future__ import annotations

import argparse
import json
import random
from concurrent.futures import ProcessPoolExecutor, as_completed

import _claude_d3_local_obstruction as d3
import _codex_k4_subdivision_obstruction_search as g6util
import _codex_random_active_component_search as random_gate
from _codex_safe_component_signature_probe import inspect


def worker(seed, trials, want, mlo, mhi):
    rng = random.Random(seed)
    d3.NODE_CAP = 5_000_000
    stats = {
        "supports": 0,
        "localAborts": 0,
        "circuits": 0,
        "maxDiameter": 0,
    }
    for _ in range(trials):
        generated = random_gate.random_support(rng, rng.randint(mlo, mhi))
        if generated is None:
            continue
        n, support = generated
        stats["supports"] += 1
        witness, aborted, _pairs = d3.check_F((g6util.graph6(n, support),))
        if aborted:
            stats["localAborts"] += 1
            continue
        if witness is None:
            continue
        atoms = [tuple(pair) for pair, _mask in witness[1]]
        supports = [mask for _pair, mask in witness[1]]
        if not random_gate.exact_minimal_circuit(supports, len(support)):
            continue
        result = inspect(n, support, atoms)
        stats["circuits"] += 1
        stats["maxDiameter"] = max(
            stats["maxDiameter"], result["maxSafeDiameter"])
        if result["maxSafeDiameter"] > 2:
            return {
                "seed": seed,
                "n": n,
                "support": support,
                "atoms": atoms,
                "probe": result,
                "stats": stats,
            }
        if stats["circuits"] >= want:
            break
    return {"seed": seed, "stats": stats}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=32)
    parser.add_argument("--tasks", type=int, default=64)
    parser.add_argument("--trials", type=int, default=100000)
    parser.add_argument("--want", type=int, default=100)
    parser.add_argument("--mlo", type=int, default=9)
    parser.add_argument("--mhi", type=int, default=50)
    args = parser.parse_args()
    totals = {
        "supports": 0,
        "localAborts": 0,
        "circuits": 0,
        "maxDiameter": 0,
    }
    first = None
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [
            pool.submit(
                worker, 880000 + i, args.trials, args.want, args.mlo, args.mhi)
            for i in range(args.tasks)
        ]
        for future in as_completed(futures):
            row = future.result()
            for key in ("supports", "localAborts", "circuits"):
                totals[key] += row["stats"][key]
            totals["maxDiameter"] = max(
                totals["maxDiameter"], row["stats"]["maxDiameter"])
            if "probe" in row and first is None:
                first = row
                for pending in futures:
                    pending.cancel()
    print(json.dumps({
        "parameters": vars(args),
        "totals": totals,
        "firstDiameterAboveTwo": first,
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
