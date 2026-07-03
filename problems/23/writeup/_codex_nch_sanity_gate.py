r"""NCH sanity-first gate for Groetzsch/Mycielski terminal attachments.

This is a falsifier gate for the NCH-def pruning inequality from
BRANCH_A_ASSEMBLY_AUDIT_GPTPRO.md:

    s_H(T_Q) <= |H| - |T|

for concrete non-C5-hom all-l5 components H attached through a small terminal
set T.  The row weight used here is the audit's terminal-row weight:

    s_H(T) = sum_g (1 / |cyc[g]|) * sum_{P in cyc[g]} |V(P) cap T|.

For small components the script also checks the Terminal-Hall formulation

    D_T(U) <= |U|,  U subset H \ T,

where D_T(U) counts rows whose non-terminal interior is contained in U, weighted
by |P cap T|.  Exact Fraction arithmetic only; no floating claims.
"""

from __future__ import annotations

import argparse
import json
from collections import deque
from fractions import Fraction as F
from itertools import combinations

from _bdef_construct import Cn, mycielski
from _h import Bconn
from _satzmu_conn import struct_for_side


def adj_of(n: int, edges: list[tuple[int, int]]) -> list[set[int]]:
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def enumerate_maxcuts_gray(n: int, edges: list[tuple[int, int]]) -> tuple[int, list[int]]:
    """Enumerate complement classes of cuts, with vertex 0 fixed on side 0."""
    adj_bits = [0] * n
    deg = [0] * n
    for u, v in edges:
        adj_bits[u] |= 1 << v
        adj_bits[v] |= 1 << u
        deg[u] += 1
        deg[v] += 1

    all_bits = (1 << n) - 1
    total = 1 << (n - 1)
    side = 0
    val = 0
    prev_g = 0
    best = 0
    best_sides = [0]

    for i in range(1, total):
        g = i ^ (i >> 1)
        diff_bit = g ^ prev_g
        bit_index = diff_bit.bit_length() - 1
        v = bit_index + 1
        if (side >> v) & 1:
            cut_incident = (adj_bits[v] & (~side) & all_bits).bit_count()
        else:
            cut_incident = (adj_bits[v] & side).bit_count()
        val += deg[v] - 2 * cut_incident
        side ^= 1 << v
        prev_g = g

        if val > best:
            best = val
            best_sides = [side]
        elif val == best:
            best_sides.append(side)

    return best, best_sides


def side_list(n: int, side_int: int) -> list[int]:
    return [(side_int >> v) & 1 for v in range(n)]


def side_string(n: int, side_int: int) -> str:
    return "".join(str((side_int >> v) & 1) for v in range(n))


def gamma_min_structs(name: str, n: int, edges: list[tuple[int, int]]):
    adj = adj_of(n, edges)
    best_cut, sides = enumerate_maxcuts_gray(n, edges)
    candidates = []
    for side_int in sides:
        side = side_list(n, side_int)
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        _M, ell, _T, _mu, _cyc = st
        gamma = sum(L * L for L in ell.values())
        candidates.append((side_int, side, st, gamma))
    if not candidates:
        return best_cut, []
    min_gamma = min(gamma for *_rest, gamma in candidates)
    return best_cut, [rec for rec in candidates if rec[-1] == min_gamma]


def terminal_weight(cyc, terminals: tuple[int, ...]) -> F:
    Tset = set(terminals)
    total = F(0)
    for rows in cyc.values():
        denom = len(rows)
        total += sum(len(Tset & set(P)) for P in rows) * F(1, denom)
    return total


def hall_demand(cyc, terminals: tuple[int, ...], U_mask: int, free_vertices: list[int]) -> F:
    Tset = set(terminals)
    U = {free_vertices[i] for i in range(len(free_vertices)) if (U_mask >> i) & 1}
    total = F(0)
    for rows in cyc.values():
        denom = len(rows)
        for P in rows:
            Pset = set(P)
            hit = len(Pset & Tset)
            if not hit:
                continue
            if (Pset - Tset) <= U:
                total += F(hit, denom)
    return total


def check_terminal_hall(cyc, n: int, terminals: tuple[int, ...], max_free: int):
    free = [v for v in range(n) if v not in set(terminals)]
    if len(free) > max_free:
        return {"checked": False, "reason": f"free_vertices={len(free)}>{max_free}"}
    worst_margin = None
    worst_mask = None
    violations = []
    for mask in range(1 << len(free)):
        demand = hall_demand(cyc, terminals, mask, free)
        size = mask.bit_count()
        margin = F(size) - demand
        if worst_margin is None or margin < worst_margin:
            worst_margin = margin
            worst_mask = mask
        if margin < 0 and len(violations) < 5:
            violations.append({
                "U": [free[i] for i in range(len(free)) if (mask >> i) & 1],
                "demand": frac_s(demand),
                "margin": frac_s(margin),
            })
    return {
        "checked": True,
        "worst_margin": frac_s(worst_margin if worst_margin is not None else F(0)),
        "worst_U": [free[i] for i in range(len(free)) if worst_mask is not None and ((worst_mask >> i) & 1)],
        "violations": violations,
    }


def frac_s(x: F) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def frac_json(x: F) -> dict[str, int]:
    return {"num": x.numerator, "den": x.denominator}


def named_graphs(max_myc_cycle: int) -> list[tuple[str, int, list[tuple[int, int]]]]:
    out = []
    c5 = (5, Cn(5))
    out.append(("Grotzsch_MycC5", *mycielski(*c5)))
    for k in range(7, max_myc_cycle + 1, 2):
        out.append((f"MycC{k}", *mycielski(k, Cn(k))))
    grotzsch = mycielski(*c5)
    out.append(("MycGrotzsch", *mycielski(*grotzsch)))
    return out


def analyze_graph(name: str, n: int, edges: list[tuple[int, int]], args):
    best_cut, structs = gamma_min_structs(name, n, edges)
    rec = {
        "name": name,
        "n": n,
        "edges": len(edges),
        "maxcut": best_cut,
        "gamma_min_connected_cuts": len(structs),
        "terminal_set_checks": 0,
        "sH_violations": [],
        "th_violations": [],
        "terminal_hall_checked": 0,
        "terminal_hall_skipped": 0,
        "max_sH_minus_bound": None,
        "max_sH_case": None,
        "all_l5_cuts": 0,
        "cuts": [],
    }
    for side_int, _side, st, gamma in structs:
        M, ell, _T, _mu, cyc = st
        all_l5 = all(L == 5 for L in ell.values())
        if all_l5:
            rec["all_l5_cuts"] += 1
        cut_rec = {
            "side": side_string(n, side_int),
            "gamma": gamma,
            "bad_edges": len(M),
            "ell_values": sorted(set(ell.values())),
            "all_l5": all_l5,
            "checked_terminals": 0,
        }
        for k in range(1, args.max_terminal_size + 1):
            for terminals in combinations(range(n), k):
                sH = terminal_weight(cyc, terminals)
                bound = F(n - k)
                margin = bound - sH
                rec["terminal_set_checks"] += 1
                cut_rec["checked_terminals"] += 1
                gap = sH - bound
                if rec["max_sH_minus_bound"] is None or gap > F(rec["max_sH_minus_bound"]["num"], rec["max_sH_minus_bound"]["den"]):
                    rec["max_sH_minus_bound"] = frac_json(gap)
                    rec["max_sH_case"] = {
                        "side": cut_rec["side"],
                        "T": list(terminals),
                        "sH": frac_s(sH),
                        "bound": frac_s(bound),
                        "margin": frac_s(margin),
                    }
                if margin < 0 and len(rec["sH_violations"]) < 5:
                    rec["sH_violations"].append({
                        "side": cut_rec["side"],
                        "T": list(terminals),
                        "sH": frac_s(sH),
                        "bound": frac_s(bound),
                        "margin": frac_s(margin),
                    })
                if args.hall_max_free >= 0:
                    hall = check_terminal_hall(cyc, n, terminals, args.hall_max_free)
                    if hall.get("checked"):
                        rec["terminal_hall_checked"] += 1
                        if hall["violations"] and len(rec["th_violations"]) < 5:
                            rec["th_violations"].append({
                                "side": cut_rec["side"],
                                "T": list(terminals),
                                "hall": hall,
                            })
                    else:
                        rec["terminal_hall_skipped"] += 1
        rec["cuts"].append(cut_rec)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-terminal-size", type=int, default=2)
    ap.add_argument("--max-myc-cycle", type=int, default=7)
    ap.add_argument("--hall-max-free", type=int, default=13,
                    help="sweep Terminal-Hall only if |H\\T| <= this; set -1 to disable")
    ap.add_argument("--summary", default="")
    args = ap.parse_args()

    results = []
    for name, n, edges in named_graphs(args.max_myc_cycle):
        rec = analyze_graph(name, n, edges, args)
        results.append(rec)
        max_case = rec["max_sH_case"] or {}
        print(
            f"{name}: n={n} cuts={rec['gamma_min_connected_cuts']} "
            f"all_l5={rec['all_l5_cuts']} terminal_checks={rec['terminal_set_checks']} "
            f"sH_viol={len(rec['sH_violations'])} TH_checked={rec['terminal_hall_checked']} "
            f"TH_skipped={rec['terminal_hall_skipped']} TH_viol={len(rec['th_violations'])} "
            f"max_gap={frac_s(F(rec['max_sH_minus_bound']['num'], rec['max_sH_minus_bound']['den'])) if rec['max_sH_minus_bound'] else 'NA'} "
            f"case={max_case}",
            flush=True,
        )
    total_sH = sum(len(r["sH_violations"]) for r in results)
    total_th = sum(len(r["th_violations"]) for r in results)
    verdict = "FAIL" if total_sH or total_th else "PASS"
    summary = {
        "verdict": verdict,
        "total_sH_violation_records": total_sH,
        "total_TH_violation_records": total_th,
        "results": results,
    }
    print("VERDICT:", verdict)
    if args.summary:
        with open(args.summary, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
