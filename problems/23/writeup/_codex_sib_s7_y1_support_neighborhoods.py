"""Finite one-step neighborhood inventory for observed y=1 SIB-S7 supports.

This is an organizational gate for the next FJ/Sturm coverage step.  Claude's
recommended finite target is the observed active-set clusters plus one-step
neighbors.  This script makes that list explicit and ranks the neighborhood
systems at the known rational family point whenever the known point lies on the
neighboring face.

It is not a closure certificate: neighbors not compatible with the sample still
need separate exact feasibility or Sturm/Groebner exclusion.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
INV_PATH = HERE / "_codex_sib_s7_y1_fj_support_inventory.py"
spec = importlib.util.spec_from_file_location("inv", INV_PATH)
inv = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(inv)

ALL_LABELS = tuple(sorted(inv.SLACKS))


def fixed_labels(row: dict) -> set[str]:
    out = {row["cap"]}
    if row["branch"] in inv.SLACKS:
        out.add(row["branch"])
    return out


def equations(branch: str, cap: str, active: tuple[str, ...]) -> list[sp.Expr]:
    row = {"branch": branch, "cap": cap, "active": active}
    return inv.unique_equations(row)


def rank_at_sample(eqs: list[sp.Expr], sample: dict) -> int | None:
    if any(sp.factor(expr.subs(sample)) != 0 for expr in eqs):
        return None
    J = sp.Matrix([[sp.diff(expr, var) for var in inv.VARS] for expr in eqs])
    return J.subs(sample).rank()


def main() -> None:
    total = 0
    sample_compatible = 0
    needs_witness = 0
    printed_needs: list[tuple[str, str, str, tuple[str, ...]]] = []

    for row in inv.SUPPORTS:
        name = row["name"]
        branch = row["branch"]
        cap = row["cap"]
        sample = row["sample"]
        fixed = fixed_labels(row)
        active = set(row["active"])
        movable_active = sorted(active - fixed)
        inactive = sorted(set(ALL_LABELS) - active - fixed)

        rows: list[tuple[str, tuple[str, ...]]] = []
        for label in movable_active:
            rows.append((f"drop:{label}", tuple(sorted(active - {label}))))
        for label in inactive:
            rows.append((f"add:{label}", tuple(sorted(active | {label}))))

        compat = 0
        incompatible = 0
        ranks: dict[int, int] = {}
        for move, new_active in rows:
            total += 1
            eqs = equations(branch, cap, new_active)
            rank = rank_at_sample(eqs, sample)
            if rank is None:
                incompatible += 1
                needs_witness += 1
                if True:
                    printed_needs.append((name, branch, cap, (move, *new_active)))
            else:
                compat += 1
                sample_compatible += 1
                ranks[rank] = ranks.get(rank, 0) + 1
        print(
            f"SUPPORT {name}: neighbors={len(rows)} sample_compatible={compat} "
            f"needs_witness={incompatible} compatible_rank_counts={sorted(ranks.items())}"
        )

    print(f"TOTAL neighbors={total} sample_compatible={sample_compatible} needs_witness={needs_witness}")
    print("FIRST_NEEDS_WITNESS:")
    for item in printed_needs:
        name, branch, cap, data = item
        print(f"  {name} branch={branch} cap={cap} move={data[0]} active={data[1:]}")
    print("PASS y=1 observed plus one-step support-neighborhood inventory generated")


if __name__ == "__main__":
    main()

