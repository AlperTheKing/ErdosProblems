"""Fast exact finite-field cross-check for CODEX_R10_BLOWUP_FACE.py.

All operations are exact in F_p.  This is used as an independent lower-rank
cross-check while the rational/character computation runs; the rational
producer remains authoritative for characteristic-zero ranks.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "CODEX_R10_BLOWUP_FACE.py"
PRIME = 1_000_003


def load_source():
    spec = importlib.util.spec_from_file_location("codex_blowup_face_source", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SOURCE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def row_basis(rows, width: int):
    pivots: dict[int, dict[int, int]] = {}
    originals = []
    for source in rows:
        row = {
            column: int(value) % PRIME
            for column, value in enumerate(source)
            if int(value) % PRIME
        }
        while row:
            pivot = min(row)
            if pivot not in pivots:
                inverse = pow(row[pivot], PRIME - 2, PRIME)
                pivots[pivot] = {
                    column: value * inverse % PRIME
                    for column, value in row.items()
                    if value * inverse % PRIME
                }
                originals.append(tuple(int(value) for value in source))
                break
            factor = row[pivot]
            for column, value in pivots[pivot].items():
                new_value = (row.get(column, 0) - factor * value) % PRIME
                if new_value:
                    row[column] = new_value
                else:
                    row.pop(column, None)
    assert all(pivot < width for pivot in pivots)
    return originals


def equation_rank(module, entry_ids, kernel_rows, qdim: int) -> int:
    equations = module.gram_kernel_equations(entry_ids, kernel_rows)
    return module.modular_rank(equations, qdim, PRIME)


def main() -> None:
    module = load_source()
    edges = module.gamma_11_edges()
    cuts = module.interval_cuts(edges)
    partitions = module.enumerate_blowups(edges)

    multiplier_monomials = module.monomials(module.N, module.MULTIPLIER_DEGREE)
    _, _, _, monomial_action = module.orbit_partition(
        multiplier_monomials, module.exponent_image
    )
    pair_ids, pair_reps = module.pair_orbits(
        module.cut_action_table(cuts), monomial_action
    )
    forced = set()
    for partition in partitions:
        vertices = set(sum(partition, ()))
        supported = [
            index
            for index, exponent in enumerate(multiplier_monomials)
            if module.support(exponent) <= vertices
        ]
        for cut_index, (mask, _mono) in enumerate(cuts):
            if module.cut_is_identically_tight(
                partition, module.cut_side(mask)
            ):
                continue
            forced.update(
                int(pair_ids[cut_index, monomial_index])
                for monomial_index in supported
            )
    print(
        f"MODULAR_F1 supports={len(partitions)} "
        f"forced={len(forced)}/{len(pair_reps)}"
    )

    masks, blocks = module.parity_blocks(module.N, module.TARGET_DEGREE)
    _, reps, members, _ = module.orbit_partition(masks, module.exponent_image)
    total_span = 0
    total_rank = 0
    total_qdim = 0
    for orbit_id, rep_index in enumerate(reps):
        representative = masks[rep_index]
        basis = blocks[representative]
        group = module.stabilizer(representative)
        entry_ids, entry_reps = module.entry_orbits(basis, group)
        candidates = set()
        for member_index in members[orbit_id]:
            member = masks[member_index]
            element = next(
                element
                for element in module.GROUP
                if module.exponent_image(representative, element) == member
            )
            acted_basis = [
                module.exponent_image(item, element) for item in basis
            ]
            for partition in partitions:
                candidates.update(
                    module.plateau_coefficient_rows(
                        acted_basis, member, partition
                    )
                )
        selected = row_basis(sorted(candidates), len(basis))
        rank = equation_rank(module, entry_ids, selected, len(entry_reps))
        total_span += len(selected)
        total_rank += rank
        total_qdim += len(entry_reps)
        print(
            f"BLOCK orbit={orbit_id} pweight={sum(representative)} "
            f"order={len(basis)} candidates={len(candidates)} "
            f"span_mod={len(selected)} qdim={len(entry_reps)} "
            f"face_rank_mod={rank}"
        )
    print(
        f"MODULAR_F2 span={total_span} rank={total_rank} "
        f"qdim={total_qdim} face_dim={total_qdim-total_rank}"
    )
    print("MODULAR_CROSSCHECK_ONLY")


if __name__ == "__main__":
    main()
