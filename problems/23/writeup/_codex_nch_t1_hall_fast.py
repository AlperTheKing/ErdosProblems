r"""Fast exact Terminal-Hall sweeps for NCH T=1 terminals.

For fixed terminal T={t}, Terminal-Hall is
    D_T(U) <= |U|  for all U subset V\T,
where D_T(U) is the weighted count of rows whose nonterminal support is inside U.
This script computes max_U (D_T(U)-|U|) exactly by integer zeta transform.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from math import gcd
from pathlib import Path

from _codex_nch_sanity_gate import named_graphs, gamma_min_structs, side_string, frac_s


def lcm(a: int, b: int) -> int:
    return a // gcd(a, b) * b


def terminal_rows_scaled(cyc, n: int, terminal: int):
    free = [v for v in range(n) if v != terminal]
    pos = {v: i for i, v in enumerate(free)}
    den = 1
    row_terms = []
    for rows in cyc.values():
        denom = len(rows)
        den = lcm(den, denom)
        for P in rows:
            if terminal not in P:
                continue
            mask = 0
            for v in P:
                if v != terminal:
                    mask |= 1 << pos[v]
            row_terms.append((mask, denom))
    weights = [0] * (1 << len(free))
    for mask, denom in row_terms:
        weights[mask] += den // denom
    return free, den, weights, len(row_terms)


def zeta_subset_sums(vals: list[int], k: int) -> None:
    for i in range(k):
        bit = 1 << i
        for mask in range(1 << k):
            if mask & bit:
                vals[mask] += vals[mask ^ bit]


def check_terminal(cyc, n: int, terminal: int):
    free, den, vals, row_count = terminal_rows_scaled(cyc, n, terminal)
    k = len(free)
    zeta_subset_sums(vals, k)
    worst_num = None
    worst_mask = 0
    for mask, demand_scaled in enumerate(vals):
        margin_num = mask.bit_count() * den - demand_scaled
        if worst_num is None or margin_num < worst_num:
            worst_num = margin_num
            worst_mask = mask
    worst_U = [free[i] for i in range(k) if (worst_mask >> i) & 1]
    return {
        "terminal": terminal,
        "free": k,
        "den": den,
        "row_terms": row_count,
        "worst_margin": frac_s(F(worst_num, den)),
        "worst_margin_num": worst_num,
        "worst_U_size": len(worst_U),
        "worst_U": worst_U,
        "violation": worst_num < 0,
    }


def analyze(args):
    out = {"graphs": [], "verdict": "PASS"}
    targets = named_graphs(args.max_myc_cycle)
    for name, n, edges in targets:
        if args.only and name != args.only:
            continue
        best_cut, structs = gamma_min_structs(name, n, edges)
        graph_rec = {
            "name": name,
            "n": n,
            "maxcut": best_cut,
            "gamma_min_connected_cuts": len(structs),
            "cuts": [],
            "violations": [],
        }
        for side_int, _side, st, gamma in structs:
            M, ell, _T, _mu, cyc = st
            cut_rec = {
                "side": side_string(n, side_int),
                "gamma": gamma,
                "bad_edges": len(M),
                "ell_values": sorted(set(ell.values())),
                "terminals": [],
                "worst_margin": None,
                "worst_terminal": None,
            }
            terminals = range(n)
            for t in terminals:
                rec = check_terminal(cyc, n, t)
                cut_rec["terminals"].append(rec if args.keep_terminals else {k: rec[k] for k in ("terminal", "worst_margin", "worst_margin_num", "worst_U_size", "violation")})
                if cut_rec["worst_margin"] is None or rec["worst_margin_num"] < cut_rec["worst_margin_num"]:
                    cut_rec["worst_margin"] = rec["worst_margin"]
                    cut_rec["worst_margin_num"] = rec["worst_margin_num"]
                    cut_rec["worst_terminal"] = rec["terminal"]
                    cut_rec["worst_U_size"] = rec["worst_U_size"]
                if rec["violation"]:
                    out["verdict"] = "FAIL"
                    if len(graph_rec["violations"]) < 5:
                        graph_rec["violations"].append({"side": cut_rec["side"], "terminal": t, "rec": rec})
            graph_rec["cuts"].append(cut_rec)
            print(name, "side", cut_rec["side"], "gamma", gamma, "worst", cut_rec["worst_margin"], "terminal", cut_rec["worst_terminal"], flush=True)
        out["graphs"].append(graph_rec)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-myc-cycle", type=int, default=11)
    ap.add_argument("--only", default="")
    ap.add_argument("--summary", default="")
    ap.add_argument("--keep-terminals", action="store_true")
    args = ap.parse_args()
    out = analyze(args)
    print("VERDICT", out["verdict"])
    if args.summary:
        Path(args.summary).write_text(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
