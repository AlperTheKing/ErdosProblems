"""Glued protected UNIT-FLAT5 cell stress.

The full N<=11 census only shows one selected protected UNIT cell per cut.
This generated family glues several copies of the known N=10 protected atom
I?AAD@wF_ by blue cut bridges, producing a connected-B cut with several
independent protected cells.

It is a bookkeeping guardrail for the protected-cell peel gate, not a proof
that the glued side is exhaustive.
"""

from __future__ import annotations

import argparse
import contextlib
import io
from collections import Counter

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_rowcap_non5_half_gate import adj_of
    from _codex_slack_cage_unit_atom_boundary_dump import build_base_case, norm_edge
    from _codex_slack_cage_prebank_classifier import subset_tw
    from _codex_slack_cage_switch_gate import all_subsets, build_data, delta, gamma_of, sigma_of
    from _codex_slack_cage_unit_peel_gate import (
        check_side,
        components_from_overlaps,
        count_boundary,
        count_inside,
        shortest_b_path_avoiding,
    )
    from _codex_slack_cage_unit_protector_gate import outside_endpoint
    from _h import Bconn, maxcut_all


def build_glued_protected_cells(k: int):
    base = build_base_case()
    bn = base["n"]
    edges = []
    side = []
    for i in range(k):
        off = i * bn
        edges.extend(norm_edge(u + off, v + off) for u, v in base["edges"])
        side.extend(base["side"])

    # Blue bridges between consecutive copies.  Vertex 0 is on side 0 in the
    # base cut, vertex 5 is on side 1, so each bridge is a cut/blue edge.
    for i in range(k - 1):
        edges.append(norm_edge(i * bn + 0, (i + 1) * bn + 5))

    return bn * k, sorted(set(edges)), "".join(str(int(c)) for c in side)


def bad_count(edges, side):
    return sum(1 for u, v in edges if side[u] == side[v])


def build_nested_overlap_guardrail():
    """Try to reuse the base protector path as a second UNIT core.

    This creates an apparent overlapping-cell attempt, but the intended cut is
    not maxcut and the original protected cell gains bad boundary.
    """

    base = build_base_case()
    edges = set(base["edges"])
    side = list(base["side"])
    side.append(1)
    # Existing vertex 8 becomes one new bad leaf for the protector path
    # 8-2-7-0-5.  Vertex 10 is a second new leaf.
    edges.add(norm_edge(10, 2))  # blue
    edges.add(norm_edge(10, 5))  # bad
    edges.add(norm_edge(8, 5))  # bad
    return 11, sorted(edges), "".join(str(int(c)) for c in side)


def check_nested_overlap_guardrail():
    n, edges, side = build_nested_overlap_guardrail()
    acc = check_side("nested-overlap", n, edges, side)
    data = build_data(n, edges, [int(c) for c in side])
    min_sigma = None
    min_sets = []
    gamma = None
    m_edges = None
    if data is not None:
        _E, B, _M, Mset, _cyc = data
        m_edges = sorted(Mset)
        gamma = gamma_of(n, Mset, B)
        sigs = [(sigma_of(S, B, Mset), tuple(sorted(S))) for S in all_subsets(n) if S and len(S) < n]
        min_sigma = min(v for v, _S in sigs)
        min_sets = [S for v, S in sigs if v == min_sigma][:8]
    adj = adj_of(n, edges)
    all_max = maxcut_all(n, adj)
    conn_max = [s for s in all_max if Bconn(n, adj, s)]
    intended = [int(c) for c in side]
    intended_key = side
    conn_keys = {"".join(str(int(c)) for c in s) for s in conn_max}
    return {
        "n": n,
        "side": side,
        "acc": acc,
        "bad_intended": bad_count(edges, intended),
        "max_bad": bad_count(edges, all_max[0]) if all_max else None,
        "conn_maxcuts": len(conn_max),
        "intended_conn_max": intended_key in conn_keys,
        "M": m_edges,
        "Gamma": gamma,
        "min_sigma": min_sigma,
        "min_sigma_sets": min_sets,
    }


def targeted_atoms(k: int):
    base = build_base_case()
    bn = base["n"]
    n, edges, side = build_glued_protected_cells(k)
    data = build_data(n, edges, [int(c) for c in side])
    if data is None:
        raise RuntimeError("targeted glued side did not build")
    _E, B, M, Mset, cyc = data

    atoms = []
    for i in range(k):
        off = i * bn
        Q = tuple(v + off for v in base["Q"])
        U = frozenset(v + off for v in base["U"])
        tw = subset_tw(n, M, cyc, U)
        pre = sum(tw[v] for v in Q) - len(U) - sigma_of(U, B, Mset)
        bdy = sorted(delta(B, U))
        outs = [outside_endpoint(e, U) for e in bdy]
        outs = [x for x in outs if x is not None]
        path = None
        if len(outs) == 2:
            path = shortest_b_path_avoiding(n, B, outs[0], outs[1], set(U))
        cell = None if path is None else frozenset(set(U) | set(path))
        atoms.append(
            {
                "name": f"glued-protected-k{k}#copy{i}",
                "n": n,
                "m": len(M),
                "side": side,
                "Q": Q,
                "U": U,
                "pre": pre,
                "doors": tuple(bdy),
                "path": path,
                "cell": cell,
                "cell_size": None if cell is None else len(cell),
                "cell_bad_inside": None if cell is None else count_inside(Mset, cell),
                "cell_bad_boundary": None if cell is None else count_boundary(Mset, cell),
                "cell_blue_boundary": None if cell is None else count_boundary(B, cell),
            }
        )
    return atoms


def check_targeted(k: int):
    atoms = targeted_atoms(k)
    missing = [a for a in atoms if a["cell"] is None]
    bad = [
        a
        for a in atoms
        if a["cell"] is not None
        and (a["pre"] != 1 or a["cell_size"] < 10 or a["cell_bad_inside"] != 2 or a["cell_bad_boundary"] != 0)
    ]
    comps = components_from_overlaps(atoms)
    comp_hist = Counter([tuple(sorted(len(c) for c in comps))])
    return {
        "atoms": atoms,
        "missing": missing,
        "bad": bad,
        "comps": comps,
        "cell_comp_hist": comp_hist,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-k", type=int, default=8)
    ap.add_argument("--targeted", action="store_true")
    ap.add_argument("--nested-overlap", action="store_true")
    args = ap.parse_args()

    print("=== glued protected UNIT-FLAT5 cell stress ===")
    if args.nested_overlap:
        res = check_nested_overlap_guardrail()
        acc = res["acc"]
        print("nested-overlap n:", res["n"])
        print("side:", res["side"])
        print("atom_count_hist:", dict(sorted(acc["atom_count_hist"].items())))
        print("cell_comp_hist:", dict(sorted(acc["cell_comp_hist"].items(), key=lambda kv: str(kv[0]))))
        print("missing:", acc["missing_cell"], "bad_cell:", acc["bad_cell"], "overlap_fail:", acc["overlap_fail"])
        print("first_bad_cell:", acc["first_bad_cell"] or "")
        print("bad_intended:", res["bad_intended"], "max_bad:", res["max_bad"])
        print("conn_maxcuts:", res["conn_maxcuts"], "intended_conn_max:", res["intended_conn_max"])
        print("M:", res["M"])
        print("Gamma:", res["Gamma"])
        print("min_sigma:", res["min_sigma"], "min_sigma_sets:", res["min_sigma_sets"])
        print(
            "VERDICT:",
            "PASS_NESTED_OVERLAP_GUARDRAIL"
            if acc["bad_cell"] and res["min_sigma"] is not None and res["min_sigma"] < 0 and not res["intended_conn_max"]
            else "FAIL_NESTED_OVERLAP_GUARDRAIL",
        )
        return

    any_fail = False
    for k in range(1, args.max_k + 1):
        n, edges, side = build_glued_protected_cells(k)
        if args.targeted:
            res = check_targeted(k)
            print(
                f"k={k} n={n} targeted_atoms={len(res['atoms'])} "
                f"cell_comp_hist={dict(sorted(res['cell_comp_hist'].items(), key=lambda kv: str(kv[0])))} "
                f"missing={len(res['missing'])} bad_cell={len(res['bad'])}",
                flush=True,
            )
            fail = bool(res["missing"] or res["bad"])
            if fail:
                print("  first_missing_cell:", res["missing"][0] if res["missing"] else "", flush=True)
                print("  first_bad_cell:", res["bad"][0] if res["bad"] else "", flush=True)
        else:
            acc = check_side(f"glued-protected-k{k}", n, edges, side)
            print(
                f"k={k} n={n} cuts={acc['cuts']} atom_hist={dict(sorted(acc['atom_count_hist'].items()))} "
                f"cell_comp_hist={dict(sorted(acc['cell_comp_hist'].items(), key=lambda kv: str(kv[0])))} "
                f"missing={acc['missing_cell']} bad_cell={acc['bad_cell']} overlap_fail={acc['overlap_fail']}",
                flush=True,
            )
            fail = bool(acc["missing_cell"] or acc["bad_cell"] or acc["overlap_fail"])
            if fail:
                print("  first_missing_cell:", acc["first_missing_cell"] or "", flush=True)
                print("  first_bad_cell:", acc["first_bad_cell"] or "", flush=True)
                print("  first_overlap_fail:", acc["first_overlap_fail"] or "", flush=True)
        if fail:
            any_fail = True
            break

    print("VERDICT:", "FAIL_GLUED_PROTECTED_CELL_STRESS" if any_fail else "PASS_GLUED_PROTECTED_CELL_STRESS")


if __name__ == "__main__":
    main()
