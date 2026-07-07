#!/usr/bin/env python3
"""Parallel modular solve using native C++ one-prime elimination.

Only replaces the slow per-prime residue computation. CRT state storage and
rational reconstruction are delegated to the stock exact Python solver.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

WRITEUP = str(Path(__file__).resolve().parent.parent / "problems" / "23" / "writeup")
if WRITEUP not in sys.path:
    sys.path.insert(0, WRITEUP)

import _codex_eq_odl1_rung2_modular_core_solve as mcs
import _codex_eq_odl1_rung2_modular_replay as replay


def solve_native(exe: str, core: str, p: int):
    proc = subprocess.run([exe, core, str(p)], text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"native solver rc={proc.returncode} p={p} stderr={proc.stderr[-1000:]}")
    rec = json.loads(proc.stdout)
    if not rec.get("ok"):
        return p, None
    return p, [int(x) for x in rec["residues"]]


def solve_native_args(args):
    return solve_native(*args)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--core", type=Path, required=True)
    ap.add_argument("--prime-count", type=int, default=384)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--batch", type=int, default=0)
    ap.add_argument("--native-exe", type=Path, default=Path("tmp/codex_mod_prime_solve.exe"))
    ap.add_argument("--store-solution", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--store-crt", type=Path, default=None)
    args = ap.parse_args()

    t0 = time.time()
    n, _terms, _rhs = mcs.read_core(args.core)
    primes = replay.prime_list(args.prime_count)
    batch = args.batch or args.workers
    residues = None
    modulus = 1
    used_primes: list[int] = []
    skipped_primes: list[int] = []
    reconstructed = False

    exe = str(args.native_exe.resolve())
    core = str(args.core.resolve())
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for start in range(0, len(primes), batch):
            wave = primes[start:start + batch]
            results = dict(pool.map(solve_native_args, [(exe, core, p) for p in wave]))
            for p in wave:
                sol_p = results[p]
                if sol_p is None:
                    skipped_primes.append(p)
                    continue
                if len(sol_p) != n:
                    raise RuntimeError(f"native residue dimension mismatch p={p}: {len(sol_p)} != {n}")
                if residues is None:
                    residues = sol_p
                    modulus = p
                else:
                    old = modulus
                    residues = [replay.crt_pair(a, old, b, p)[0] for a, b in zip(residues, sol_p)]
                    modulus = old * p
                used_primes.append(p)
            if residues is not None:
                cands = [replay.rational_reconstruct(a, modulus) for a in residues]
                if all(c is not None for c in cands):
                    reconstructed = True
                    break

    state_path = args.store_crt or args.store_solution.with_suffix(".crtstate.json")
    mcs.store_crt(state_path, residues, modulus, used_primes, skipped_primes)
    rc = subprocess.run([
        sys.executable,
        "-B",
        f"{WRITEUP}/_codex_eq_odl1_rung2_modular_core_solve.py",
        "--core",
        str(args.core),
        "--prime-count",
        str(args.prime_count),
        "--resume-crt",
        str(state_path),
        "--store-solution",
        str(args.store_solution),
        "--summary",
        str(args.summary),
    ]).returncode
    print(json.dumps({
        "cpp_parallel_solve": True,
        "workers": args.workers,
        "primes_solved": len(used_primes),
        "primes_skipped": len(skipped_primes),
        "reconstructed_in_parallel": reconstructed,
        "seconds": round(time.time() - t0, 1),
        "resume_rc": rc,
        "core": str(args.core),
        "solution": str(args.store_solution),
        "summary": str(args.summary),
    }, sort_keys=True))
    if rc != 0:
        raise SystemExit(rc)


if __name__ == "__main__":
    main()
