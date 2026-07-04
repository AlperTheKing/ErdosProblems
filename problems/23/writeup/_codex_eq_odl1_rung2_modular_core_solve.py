#!/usr/bin/env python3
"""Solve an exported EQ-ODL1 Rung-2 sparse core by modular reconstruction."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import _codex_eq_odl1_rung2_modular_replay as replay


def parse_fraction(text: str) -> Fraction:
    if text == "0":
        return Fraction(0)
    if "/" in text:
        a, b = text.split("/", 1)
        return Fraction(int(a), int(b))
    return Fraction(int(text), 1)


def read_core(path: Path):
    n = None
    terms: list[tuple[int, int, Fraction]] = []
    rhs_items: dict[int, Fraction] = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            typ = rec.get("type")
            if typ == "meta":
                n = int(rec["dimension"])
            elif typ == "rhs":
                rhs_items[int(rec["row"])] = parse_fraction(rec["value"])
            elif typ == "term":
                terms.append((int(rec["row"]), int(rec["col"]), parse_fraction(rec["value"])))
    if n is None:
        raise ValueError("missing meta row")
    rhs = [rhs_items[i] for i in range(n)]
    return n, terms, rhs


def verify_core(n: int, terms: list[tuple[int, int, Fraction]], rhs: list[Fraction], sol: list[Fraction]):
    residual = rhs[:]
    for i, j, coeff in terms:
        residual[i] -= coeff * sol[j]
    return {
        "core_nonzero_residuals": sum(1 for x in residual if x),
        "core_min_residual": replay.fmt_fraction(min(residual) if residual else Fraction(0)),
        "core_max_residual": replay.fmt_fraction(max(residual) if residual else Fraction(0)),
        "solution_negative_count": sum(1 for x in sol if x < 0),
        "solution_min": replay.fmt_fraction(min(sol) if sol else Fraction(0)),
        "solution_max": replay.fmt_fraction(max(sol) if sol else Fraction(0)),
    }


def load_crt(path: Path, n: int):
    rec = json.loads(path.read_text(encoding="utf-8"))
    residues = [int(x) for x in rec["residues"]]
    if len(residues) != n:
        raise ValueError(f"CRT residue dimension mismatch: {len(residues)} != {n}")
    return residues, int(rec["modulus"]), [int(p) for p in rec.get("used_primes", [])], [int(p) for p in rec.get("skipped_primes", [])]


def store_crt(path: Path, residues: list[int] | None, modulus: int, used_primes: list[int], skipped_primes: list[int]) -> None:
    if residues is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(
        {
            "schema": "eq_odl1_rung2_modular_crt_state_v1",
            "modulus": str(modulus),
            "modulus_bits": modulus.bit_length(),
            "used_primes": used_primes,
            "skipped_primes": skipped_primes,
            "residues": [str(x) for x in residues],
        },
        indent=2,
        sort_keys=True,
    )
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(data, encoding="utf-8")
    tmp.replace(path)


def store_solution(path: Path, sol: list[Fraction]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for j, val in enumerate(sol):
            f.write(json.dumps({"col": j, "num": val.numerator, "den": val.denominator}) + "\n")
def try_reconstruct(residues: list[int] | None, modulus: int):
    if residues is None:
        return None
    candidates = [replay.rational_reconstruct(a, modulus) for a in residues]
    if all(x is not None for x in candidates):
        return [x for x in candidates if x is not None]
    return None


def run(args):
    n, terms, rhs = read_core(args.core)
    out: dict[str, object] = {
        "schema": "eq_odl1_rung2_modular_core_solve_v1",
        "core": str(args.core),
        "dimension": n,
        "terms": len(terms),
        "prime_count_requested": args.prime_count,
    }
    residues: list[int] | None = None
    modulus = 1
    used_primes: list[int] = []
    skipped_primes: list[int] = []
    if args.resume_crt:
        residues, modulus, used_primes, skipped_primes = load_crt(args.resume_crt, n)
        out["resumed_crt"] = str(args.resume_crt)
        out["resumed_modulus_bits"] = modulus.bit_length()
        if not args.no_reconstruct:
            resumed = try_reconstruct(residues, modulus)
            if resumed is not None:
                check = verify_core(n, terms, rhs, resumed)
                out["resume_reconstruction_check"] = check
                if check["core_nonzero_residuals"] == 0:
                    out["modular"] = {
                        "used_primes": used_primes,
                        "skipped_primes": skipped_primes,
                        "modulus_bits": modulus.bit_length(),
                        "reconstructed": True,
                    }
                    out["exact_check"] = check
                    if args.store_solution:
                        store_solution(args.store_solution, resumed)
                        out["solution"] = str(args.store_solution)
                    return out

    used_set = set(used_primes) | set(skipped_primes)
    recon: list[Fraction] | None = None
    for p in replay.prime_list(args.prime_count):
        if p in used_set:
            continue
        sol_p = replay.solve_mod_prime(n, terms, rhs, p)
        if sol_p is None:
            skipped_primes.append(p)
            used_set.add(p)
            continue
        if residues is None:
            residues = sol_p
            modulus = p
        else:
            old_modulus = modulus
            residues = [replay.crt_pair(a, old_modulus, b, p)[0] for a, b in zip(residues, sol_p)]
            modulus *= p
        used_primes.append(p)
        used_set.add(p)
        if args.store_crt and args.checkpoint_every > 0 and len(used_primes) % args.checkpoint_every == 0:
            store_crt(args.store_crt, residues, modulus, used_primes, skipped_primes)
        if args.no_reconstruct:
            continue
        recon = try_reconstruct(residues, modulus)
        if recon is not None:
            check = verify_core(n, terms, rhs, recon)
            out["last_reconstruction_check"] = check
            if check["core_nonzero_residuals"] == 0:
                break
            recon = None
    if args.store_crt:
        store_crt(args.store_crt, residues, modulus, used_primes, skipped_primes)
    partial_count = None
    if residues is not None and not args.no_reconstruct:
        partial_count = sum(1 for a in residues if replay.rational_reconstruct(a, modulus) is not None)
    out["modular"] = {
        "used_primes": used_primes,
        "skipped_primes": skipped_primes,
        "modulus_bits": modulus.bit_length(),
        "reconstructed": recon is not None,
        "partial_reconstruction_count": partial_count,
    }
    if recon is not None:
        out["exact_check"] = verify_core(n, terms, rhs, recon)
        if args.store_solution:
            args.store_solution.parent.mkdir(parents=True, exist_ok=True)
            with args.store_solution.open("w", encoding="utf-8") as f:
                for j, val in enumerate(recon):
                    f.write(json.dumps({"col": j, "num": val.numerator, "den": val.denominator}) + "\n")
            out["solution"] = str(args.store_solution)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--core", type=Path, required=True)
    ap.add_argument("--prime-count", type=int, default=8, help="total prime prefix to use, including resumed primes")
    ap.add_argument("--no-reconstruct", action="store_true")
    ap.add_argument("--resume-crt", type=Path)
    ap.add_argument("--store-crt", type=Path)
    ap.add_argument("--checkpoint-every", type=int, default=0, help="write CRT checkpoint every k new used primes; 0 means final only")
    ap.add_argument("--store-solution", type=Path)
    ap.add_argument("--summary", type=Path, default=Path("tmp/eq_odl1_rung2_modular_core_solve_v1.json"))
    args = ap.parse_args()
    out = run(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"dimension": out["dimension"], "terms": out["terms"], "modular": out.get("modular"), "exact_check": out.get("exact_check")}, sort_keys=True))


if __name__ == "__main__":
    main()











