#!/usr/bin/env python3
"""Full-board PySAT encoding for queen domination on an n x n board.

Primary variable ``1 + r*n + c`` means that square ``(r, c)`` contains a
queen. Every square contributes a clause containing its full closed queen
neighborhood. By default the global constraint is ``sum(x[r,c]) <= k``;
``--exact`` changes it to equality. Certified target-specific parity pruning
and sound D4 lex leaders are explicit optional flags.

Cardinality constraints support PySAT's Sinz sequential counter or modular
totalizer. Q_26 always has exactly 676 primary square variables; documented
auxiliary variables follow them in DIMACS.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterable

from pysat.card import CardEnc, EncType
from pysat.formula import CNF
from pysat.solvers import Solver

# CaDiCaL proof-enabled instances in the Windows PySAT build can terminate
# abnormally when delete() runs after get_proof(). A direct proof worker keeps
# that solver alive until main has durably emitted its result, then exits with
# os._exit so native teardown cannot destroy the proof artifact.
_RETAINED_PROOF_SOLVERS: list[Solver] = []



def square_var(n: int, row: int, col: int) -> int:
    """Return the 1-based DIMACS variable for a board square."""
    return 1 + row * n + col


def closed_neighborhood(n: int, row: int, col: int) -> list[int]:
    """Return sorted square variables attacking or equal to (row, col)."""
    variables: set[int] = set()
    for r in range(n):
        for c in range(n):
            if (
                r == row
                or c == col
                or r - c == row - col
                or r + c == row + col
            ):
                variables.add(square_var(n, r, c))
    return sorted(variables)


def hilbert_distance(point: tuple[int, int], bits: int) -> int:
    """Match hilbertcurve.HilbertCurve(bits, 2).distance_from_point."""
    coordinates = list(point)
    q = 1 << (bits - 1)
    while q > 1:
        mask = q - 1
        for index in range(2):
            if coordinates[index] & q:
                coordinates[0] ^= mask
            else:
                swap = (coordinates[0] ^ coordinates[index]) & mask
                coordinates[0] ^= swap
                coordinates[index] ^= swap
        q >>= 1
    coordinates[1] ^= coordinates[0]
    correction = 0
    q = 1 << (bits - 1)
    while q > 1:
        if coordinates[1] & q:
            correction ^= q - 1
        q >>= 1
    coordinates[0] ^= correction
    coordinates[1] ^= correction
    bit_strings = [format(value, f"0{bits}b") for value in coordinates]
    interleaved = "".join(
        bit_string[index] for index in range(bits) for bit_string in bit_strings
    )
    return int(interleaved, 2)


def ordered_square_variables(n: int, ordering: str) -> list[int]:
    indices = list(range(n * n))
    if ordering == "row-major":
        return [index + 1 for index in indices]
    if ordering != "hilbert":
        raise ValueError(f"unknown literal ordering: {ordering}")
    bits = n.bit_length()
    indices.sort(
        key=lambda index: (
            hilbert_distance(divmod(index, n), bits),
            -len(closed_neighborhood(n, *divmod(index, n))),
        )
    )
    return [index + 1 for index in indices]

def d4_ordering(n: int, symmetry: str) -> list[int]:
    """Return Rostami--Bright's flattened board after a D4 symmetry."""
    transforms = {
        "rotate90": lambda r, c: (c, n - 1 - r),
        "rotate180": lambda r, c: (n - 1 - r, n - 1 - c),
        "rotate270": lambda r, c: (n - 1 - c, r),
        "flip_horizontal": lambda r, c: (r, n - 1 - c),
        "flip_vertical": lambda r, c: (n - 1 - r, c),
        "flip_main_diag": lambda r, c: (c, r),
        "flip_anti_diag": lambda r, c: (n - 1 - c, n - 1 - r),
    }
    if symmetry not in transforms:
        raise ValueError(f"unknown D4 symmetry: {symmetry}")
    transform = transforms[symmetry]
    return [
        square_var(n, *transform(row, col))
        for row in range(n)
        for col in range(n)
    ]


def add_d4_lex_leaders(cnf: CNF, n: int) -> dict[str, int]:
    """Add the official existential encoding of X <=lex g(X), g in D4.

    Queen domination and exact cardinality are D4 invariant. The two parity
    caps are invariant as a pair, though a symmetry may swap color classes.
    Every finite D4 orbit has a lexicographically least member, so the clauses
    preserve satisfiability. With a live prefix, the three clauses disallow
    X[i]=1,Y[i]=0, force the next prefix on equality, and allow it to become
    inactive after X[i]=0,Y[i]=1. This is the scheme in the official
    TahaRostami/Gamma/AddSymBreak.py.
    """
    primary_order = list(range(1, n * n + 1))
    symmetries = (
        "rotate90",
        "rotate180",
        "rotate270",
        "flip_horizontal",
        "flip_vertical",
        "flip_main_diag",
        "flip_anti_diag",
    )
    before_variables = cnf.nv
    before_clauses = len(cnf.clauses)
    next_variable = cnf.nv + 1
    for symmetry in symmetries:
        transformed_order = d4_ordering(n, symmetry)
        prefix = list(range(next_variable, next_variable + n * n + 1))
        next_variable += n * n + 1
        cnf.append([prefix[0]])
        cnf.append([prefix[-1]])
        for index, (x_var, y_var) in enumerate(
            zip(primary_order, transformed_order), start=1
        ):
            cnf.append([prefix[index], y_var, -prefix[index - 1]])
            cnf.append([prefix[index], -x_var, -prefix[index - 1]])
            cnf.append([y_var, -x_var, -prefix[index - 1]])
    return {
        "auxiliary_variables": cnf.nv - before_variables,
        "clauses": len(cnf.clauses) - before_clauses,
    }



def build_cnf(
    n: int,
    k: int,
    encoding: str = "seqcounter",
    ordering: str = "row-major",
    exact: bool = False,
    balanced_parity: bool = False,
    d4_lex: bool = False,
) -> tuple[CNF, dict[str, Any]]:
    """Build the full-board queen-domination formula."""
    if n <= 0:
        raise ValueError("n must be positive")
    if not 0 <= k <= n * n:
        raise ValueError("k must satisfy 0 <= k <= n*n")

    primary = n * n
    cnf = CNF()
    for row in range(n):
        for col in range(n):
            cnf.append(closed_neighborhood(n, row, col))

    domination_clauses = len(cnf.clauses)
    encoding_types = {
        "seqcounter": EncType.seqcounter,
        "mtotalizer": EncType.mtotalizer,
    }
    if encoding not in encoding_types:
        raise ValueError(f"unknown cardinality encoding: {encoding}")
    ordered_variables = ordered_square_variables(n, ordering)

    cardinality_builder = CardEnc.equals if exact else CardEnc.atmost
    card = cardinality_builder(
        lits=ordered_variables,
        bound=k,
        top_id=primary,
        encoding=encoding_types[encoding],
    )
    cnf.extend(card.clauses)
    cardinality_auxiliaries = cnf.nv - primary
    parity_clauses = 0
    parity_auxiliaries = 0
    parity_cap = None
    if balanced_parity:
        if not exact or k % 2 == 0:
            raise ValueError("balanced parity requires exact odd cardinality")
        parity_cap = (k + 1) // 2
        before_variables = cnf.nv
        before_clauses = len(cnf.clauses)
        for parity in (0, 1):
            parity_variables = [
                square_var(n, row, col)
                for row in range(n)
                for col in range(n)
                if (row + col) % 2 == parity
            ]
            parity_card = CardEnc.atmost(
                lits=parity_variables,
                bound=parity_cap,
                top_id=cnf.nv,
                encoding=encoding_types[encoding],
            )
            cnf.extend(parity_card.clauses)
        parity_auxiliaries = cnf.nv - before_variables
        parity_clauses = len(cnf.clauses) - before_clauses

    d4_stats = {"auxiliary_variables": 0, "clauses": 0}
    if d4_lex:
        d4_stats = add_d4_lex_leaders(cnf, n)

    metadata = {
        "n": n,
        "k": k,
        "encoding": f"pysat.card.CardEnc.{'equals' if exact else 'atmost'}/EncType.{encoding}",
        "cardinality_encoding": encoding,
        "cardinality_relation": "equals" if exact else "atmost",
        "exact_cardinality": exact,
        "balanced_parity": balanced_parity,
        "parity_cap_per_class": parity_cap,
        "parity_class_sizes": [
            sum((row + col) % 2 == parity for row in range(n) for col in range(n))
            for parity in (0, 1)
        ],
        "parity_clauses": parity_clauses,
        "parity_auxiliary_variables": parity_auxiliaries,
        "balanced_parity_basis": (
            "Weakley 2022 Proposition 11 + Theorem 18; Q26 APPROACH_REGISTRY.md"
            if balanced_parity
            else None
        ),
        "d4_lex_leader": d4_lex,
        "d4_lex_clauses": d4_stats["clauses"],
        "d4_lex_auxiliary_variables": d4_stats["auxiliary_variables"],
        "d4_lex_basis": (
            "D4 orbit lex minimum; TahaRostami/Gamma/AddSymBreak.py"
            if d4_lex
            else None
        ),
        "literal_ordering": ordering,
        "hilbert_bits": n.bit_length() if ordering == "hilbert" else None,
        "primary_square_variables": primary,
        "auxiliary_variables": cnf.nv - primary,
        "total_variables": cnf.nv,
        "domination_clauses": domination_clauses,
        "cardinality_clauses": len(card.clauses),
        "cardinality_auxiliary_variables": cardinality_auxiliaries,
        "total_clauses": len(cnf.clauses),
    }
    return cnf, metadata


def selected_squares(model: Iterable[int], n: int) -> list[list[int]]:
    positive = {literal for literal in model if 0 < literal <= n * n}
    return [[v // n, v % n] for v in range(n * n) if v + 1 in positive]


def verify_model(
    n: int,
    k: int,
    queens: Iterable[Iterable[int]],
    exact: bool = False,
    balanced_parity: bool = False,
) -> tuple[bool, str]:
    """Check a returned witness without consulting the CNF encoding."""
    points = [tuple(point) for point in queens]
    if len(points) > k:
        return False, f"model has {len(points)} queens, exceeding k={k}"
    if exact and len(points) != k:
        return False, f"model has {len(points)} queens, expected exactly k={k}"
    if len(set(points)) != len(points):
        return False, "model contains duplicate coordinates"
    if any(len(point) != 2 for point in points):
        return False, "a coordinate does not have two entries"
    if any(not (0 <= r < n and 0 <= c < n) for r, c in points):
        return False, "a coordinate is outside the board"

    if balanced_parity:
        cap = (k + 1) // 2
        counts = [
            sum((row + col) % 2 == parity for row, col in points)
            for parity in (0, 1)
        ]
        if max(counts) > cap:
            return False, f"parity counts {counts} exceed per-class cap {cap}"
    for row in range(n):
        for col in range(n):
            if not any(
                r == row
                or c == col
                or r - c == row - col
                or r + c == row + col
                for r, c in points
            ):
                return False, f"square ({row},{col}) is not dominated"
    return True, "all board squares dominated"


def configure_seed(solver: Solver, solver_name: str, seed: int | None) -> None:
    if seed is None:
        return
    normalized = solver_name.lower()
    if normalized in {"g42", "g421", "glucose42", "glucose421"}:
        solver.configure({"rnd-seed": seed})
    elif normalized in {
        "cd15",
        "cd153",
        "cd19",
        "cd195",
        "cdl15",
        "cdl153",
        "cdl19",
        "cdl195",
        "cadical153",
        "cadical195",
    }:
        solver.configure({"seed": seed})
    else:
        raise ValueError(
            f"--seed is supported here only for CaDiCaL 1.5/1.9 and Glucose 4.2, not {solver_name!r}"
        )


def write_proof(path: Path, proof: Iterable[str] | None) -> int:
    line_count = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="ascii", newline="\n") as handle:
        for line in proof or ():
            handle.write(line.rstrip("\r\n"))
            handle.write("\n")
            line_count += 1
    return line_count


def _solve_formula_direct(
    cnf: CNF,
    metadata: dict[str, Any],
    solver_name: str,
    seed: int | None,
    proof_path: Path | None,
) -> dict[str, Any]:
    with_proof = proof_path is not None
    started = time.perf_counter()
    try:
        solver = Solver(
            name=solver_name,
            bootstrap_with=cnf.clauses,
            use_timer=True,
            with_proof=with_proof,
        )
    except Exception as exc:
        if with_proof:
            raise RuntimeError(
                f"solver {solver_name!r} does not support proof tracing in this PySAT build"
            ) from exc
        raise
    retain_solver = False

    try:
        configure_seed(solver, solver_name, seed)
        satisfiable = solver.solve()

        result: dict[str, Any] = dict(metadata)
        result.update(
            {
                "solver": solver_name,
                "seed": seed,
                "wall_seconds": time.perf_counter() - started,
                "solver_seconds": solver.time(),
                "status": "SAT" if satisfiable is True else "UNSAT" if satisfiable is False else "UNKNOWN",
                "accum_stats": solver.accum_stats(),
            }
        )
        if satisfiable is True:
            queens = selected_squares(solver.get_model(), metadata["n"])
            verified, detail = verify_model(
                metadata["n"],
                metadata["k"],
                queens,
                exact=metadata["exact_cardinality"],
                balanced_parity=metadata["balanced_parity"],
            )
            result.update(
                {
                    "queens": queens,
                    "queen_count": len(queens),
                    "independent_model_check": verified,
                    "independent_model_check_detail": detail,
                }
            )
            if not verified:
                raise RuntimeError(f"SAT backend returned an invalid model: {detail}")
        elif satisfiable is False and proof_path is not None:
            proof_lines = write_proof(proof_path, solver.get_proof())
            result.update({"proof_path": str(proof_path), "proof_lines": proof_lines})
            _RETAINED_PROOF_SOLVERS.append(solver)
            retain_solver = True
        return result
    finally:
        if not retain_solver:
            solver.delete()























def solve_formula(
    cnf: CNF,
    metadata: dict[str, Any],
    solver_name: str,
    seed: int | None,
    timeout: float | None,
    proof_path: Path | None,
) -> dict[str, Any]:
    """Solve directly, or in a child process when a hard timeout is set.

    Some PySAT backends remain inside a C call after ``interrupt()`` on
    Windows.  A spawned worker gives ``--timeout`` hard wall-clock semantics.
    """
    if timeout is None:
        result = _solve_formula_direct(cnf, metadata, solver_name, seed, proof_path)
        result["timeout_seconds"] = None
        return result

    started = time.perf_counter()
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--n",
        str(metadata["n"]),
        "--k",
        str(metadata["k"]),
        "--encoding",
        metadata["cardinality_encoding"],
        "--ordering",
        metadata["literal_ordering"],
        "--solver",
        solver_name,
        "--_solve-direct",
    ]
    if metadata["exact_cardinality"]:
        command.append("--exact")
    if metadata["balanced_parity"]:
        command.append("--balanced-parity")
    if metadata["d4_lex_leader"]:
        command.append("--d4-lex")
    if seed is not None:
        command.extend(["--seed", str(seed)])
    if proof_path is not None:
        command.extend(["--proof", str(proof_path)])
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        result: dict[str, Any] = dict(metadata)
        result.update(
            {
                "solver": solver_name,
                "seed": seed,
                "timeout_seconds": timeout,
                "wall_seconds": time.perf_counter() - started,
                "solver_seconds": None,
                "status": "UNKNOWN",
                "timeout_enforcement": "terminated solver subprocess",
            }
        )
        return result
    if completed.returncode != 0:
        raise RuntimeError(
            f"solver subprocess exited {completed.returncode}: {completed.stderr.strip()}"
        )
    result = json.loads(completed.stdout)
    result["timeout_seconds"] = timeout
    return result



















































def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=26, help="board side length (default: 26)")
    parser.add_argument("--k", type=int, default=13, help="maximum queen count (default: 13)")
    parser.add_argument(
        "--encoding",
        choices=("seqcounter", "mtotalizer"),
        default="seqcounter",
        help="at-most-k cardinality encoding (default: seqcounter)",
    )
    parser.add_argument(
        "--ordering",
        choices=("row-major", "hilbert"),
        default="row-major",
        help="primary-literal order for the cardinality encoding",
    )
    parser.add_argument(
        "--exact",
        action="store_true",
        help="require exactly k queens instead of at most k",
    )
    parser.add_argument(
        "--balanced-parity",
        action="store_true",
        help="Q26 exact-13 only: cap each square parity at 7 (Weakley Prop. 11 + Thm. 18)",
    )
    parser.add_argument(
        "--d4-lex",
        action="store_true",
        help="add sound D4 lex-leader clauses on primary square variables",
    )
    parser.add_argument(
        "--solver",
        default="cadical195",
        help="PySAT solver name/alias (default: cadical195)",
    )
    parser.add_argument("--seed", type=int, help="CaDiCaL/Glucose random seed")
    parser.add_argument(
        "--timeout",
        type=float,
        help="interrupt solving after this many seconds; status becomes UNKNOWN",
    )
    parser.add_argument("--dimacs", type=Path, help="write the full CNF in DIMACS format")
    parser.add_argument("--model-json", type=Path, help="write metadata/status/model JSON")
    parser.add_argument(
        "--proof",
        type=Path,
        help="request a backend proof trace and write it after UNSAT (backend-dependent)",
    )
    parser.add_argument(
        "--encode-only",
        action="store_true",
        help="build/export CNF but do not invoke a SAT solver",
    )
    parser.add_argument("--_solve-direct", action="store_true", help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.timeout is not None and args.timeout <= 0:
        raise SystemExit("--timeout must be positive")
    if args.balanced_parity and not (args.exact and args.n == 26 and args.k == 13):
        raise SystemExit(
            "--balanced-parity is certified only with --exact --n 26 --k 13"
        )


    cnf, metadata = build_cnf(
        args.n,
        args.k,
        args.encoding,
        args.ordering,
        exact=args.exact,
        balanced_parity=args.balanced_parity,
        d4_lex=args.d4_lex,
    )





    if args.dimacs is not None:
        args.dimacs.parent.mkdir(parents=True, exist_ok=True)
        cnf.to_file(str(args.dimacs))

    if args.encode_only:
        result: dict[str, Any] = dict(metadata)
        result["status"] = "ENCODED"
    elif args._solve_direct:
        result = _solve_formula_direct(
            cnf=cnf,
            metadata=metadata,
            solver_name=args.solver,
            seed=args.seed,
            proof_path=args.proof,
        )
        result["timeout_seconds"] = None
    else:
        result = solve_formula(
            cnf=cnf,
            metadata=metadata,
            solver_name=args.solver,
            seed=args.seed,
            timeout=args.timeout,
            proof_path=args.proof,
        )

    serialized = json.dumps(result, indent=2, sort_keys=True)
    print(serialized)
    if args.model_json is not None:
        args.model_json.parent.mkdir(parents=True, exist_ok=True)
        args.model_json.write_text(serialized + "\n", encoding="utf-8")

    if args._solve_direct and args.proof is not None and result["status"] == "UNSAT":
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(0)

    if result["status"] == "UNKNOWN":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
