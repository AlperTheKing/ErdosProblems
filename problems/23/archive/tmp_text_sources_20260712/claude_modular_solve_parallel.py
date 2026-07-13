#!/usr/bin/env python3
"""PARALLEL 384-prime modular solve (Claude) — batched ProcessPool over INDEPENDENT primes.

The stock _codex_eq_odl1_rung2_modular_core_solve.py solves the 384 prime systems
SEQUENTIALLY on one thread (the dominant cost, ~1.5h/row). Each prime's solve_mod_prime
is fully independent, so this companion runs them across N workers, CRT-combines in prime
order, writes the CRT state via the stock store_crt, then hands it to the stock solver via
--resume-crt for the PROVEN reconstruction + solution store + verify.

EXACTNESS: reuses replay.solve_mod_prime / crt_pair and the stock read_core/store_crt +
resume-reconstruct verbatim — only the ORDER (parallel vs serial) of independent pure-function
solves changes. Validated to match the sequential solver's exact solution before use.

Usage: python claude_modular_solve_parallel.py --core CORE --prime-count 384 --workers 48 \
         --store-solution SOL --summary SUM [--store-crt STATE]
"""
from __future__ import annotations
import argparse, json, sys, subprocess, time
from fractions import Fraction
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

WRITEUP = str(Path(__file__).resolve().parent.parent / "problems" / "23" / "writeup")
if WRITEUP not in sys.path:
    sys.path.insert(0, WRITEUP)

import _codex_eq_odl1_rung2_modular_replay as replay
import _codex_eq_odl1_rung2_modular_core_solve as mcs

# ---- worker: load core once per process, solve one prime ----
_CORE = {}

def _init(core_path: str):
    n, terms, rhs = mcs.read_core(Path(core_path))
    _CORE["n"] = n
    _CORE["terms"] = terms
    _CORE["rhs"] = rhs

def _solve(p: int):
    r = replay.solve_mod_prime(_CORE["n"], _CORE["terms"], _CORE["rhs"], p)
    return (p, r)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--core", type=Path, required=True)
    ap.add_argument("--prime-count", type=int, default=384)
    ap.add_argument("--workers", type=int, default=48)
    ap.add_argument("--batch", type=int, default=0, help="primes per parallel wave; 0 = workers")
    ap.add_argument("--store-solution", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--store-crt", type=Path, default=None)
    args = ap.parse_args()

    t0 = time.time()
    n, terms, rhs = mcs.read_core(args.core)
    primes = replay.prime_list(args.prime_count)
    batch = args.batch or args.workers

    residues = None
    modulus = 1
    used_primes: list[int] = []
    skipped_primes: list[int] = []
    reconstructed = False
    recon_solution = None

    # solve in waves of `batch`, combine in prime order, early-exit when reconstruction succeeds
    with ProcessPoolExecutor(max_workers=args.workers, initializer=_init, initargs=(str(args.core),)) as pool:
        for start in range(0, len(primes), batch):
            wave = primes[start:start + batch]
            results = dict(pool.map(_solve, wave))  # {p: residues|None}
            for p in wave:                           # combine in deterministic prime order
                sol_p = results[p]
                if sol_p is None:
                    skipped_primes.append(p)
                    continue
                if residues is None:
                    residues = sol_p
                    modulus = p
                else:
                    old = modulus
                    residues = [replay.crt_pair(a, old, b, p)[0] for a, b in zip(residues, sol_p)]
                    modulus = old * p
                used_primes.append(p)
            # try reconstruction after each wave (matches sequential early-exit semantics)
            if residues is not None:
                cands = [replay.rational_reconstruct(a, modulus) for a in residues]
                if all(c is not None for c in cands):
                    recon_solution = cands
                    reconstructed = True
                    break

    # write CRT state (stock format) and hand to the stock solver for reconstruct+store+verify
    state_path = args.store_crt or args.store_solution.with_suffix(".crtstate.json")
    mcs.store_crt(state_path, residues, modulus, used_primes, skipped_primes)

    rc = subprocess.run([sys.executable, "-B", f"{WRITEUP}/_codex_eq_odl1_rung2_modular_core_solve.py",
                         "--core", str(args.core), "--prime-count", str(args.prime_count),
                         "--resume-crt", str(state_path),
                         "--store-solution", str(args.store_solution), "--summary", str(args.summary)]).returncode

    print(json.dumps({
        "parallel_solve": True, "workers": args.workers, "primes_solved": len(used_primes),
        "primes_skipped": len(skipped_primes), "reconstructed_in_parallel": reconstructed,
        "seconds": round(time.time() - t0, 1), "resume_rc": rc,
        "core": str(args.core), "solution": str(args.store_solution), "summary": str(args.summary),
    }))


if __name__ == "__main__":
    main()
