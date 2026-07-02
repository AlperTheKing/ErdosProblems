"""Xi2 square-surplus gate for Slack-CAGE zero-slack core switches.

This implements the square-surplus object from the GPT-Pro canonical-cage
plan on the existing finite cage-core family:

  Xi2(S) = sum_{g in delta_M(S)} ell(g)^2
           - min_{bijections e -> g witnessed by counted rows}
             sum_{e in delta_B(S)} ell(g)^2.

It is a stress tool, not a proof.  It checks whether zero-slack cages in
positive proper-counted prebank cases are either Flat5 bank atoms or have
positive Xi2 square surplus.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import itertools
import subprocess
from collections import Counter
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _h import GENG, dec
    from _stark1 import gmins
    from _codex_slack_cage_prebank_classifier import classify_case, subset_tw
    from _codex_slack_cage_switch_gate import (
        build_data,
        counted_rows,
        delta,
        first_exit_edges,
        flip_blue,
        gamma_of,
        shortest_distance,
        sigma_of,
    )
    from _codex_slack_cage_banked_flat_gate import is_flat5_switch


def ell_in_blue(n, blue_edges, edge):
    d = shortest_distance(n, blue_edges, edge[0], edge[1])
    return None if d is None else d + 1


def xi2_for_switch(n, B, Mset, counted, S):
    S = frozenset(S)
    C = sorted(delta(Mset, S))
    E = sorted(delta(B, S))
    if len(C) != len(E):
        return None, {"reason": "not_zero_sized", "C": C, "E": E}

    ell = {g: ell_in_blue(n, B, g) for g in C}
    if any(v is None for v in ell.values()):
        return None, {"reason": "old_length_missing", "C": C, "E": E}

    witnesses = {e: set() for e in E}
    for g, P, pset in counted:
        g = tuple(sorted(g))
        if g not in ell:
            continue
        if not (pset & S and not pset <= S):
            continue
        for e in first_exit_edges(P, S):
            if e in witnesses:
                witnesses[e].add(g)

    if any(not gs for gs in witnesses.values()):
        return None, {"reason": "unwitnessed_exit", "C": C, "E": E, "witnesses": witnesses}

    best = None
    best_assign = None
    for perm in itertools.permutations(C):
        ok = True
        cost = 0
        assign = []
        for e, g in zip(E, perm):
            if g not in witnesses[e]:
                ok = False
                break
            cost += ell[g] * ell[g]
            assign.append((e, g))
        if ok and (best is None or cost < best):
            best = cost
            best_assign = assign
    if best is None:
        return None, {"reason": "no_bijection", "C": C, "E": E, "witnesses": witnesses}

    old_sum = sum(ell[g] * ell[g] for g in C)
    return old_sum - best, {"C": C, "E": E, "ell": ell, "assignment": best_assign}


def analyze_graph(g6):
    n, edges = dec(g6)
    _adj, cuts = gmins(n, edges)
    out = []
    for cut_idx, side_s in enumerate(cuts):
        side = [int(c) for c in side_s]
        data = build_data(n, edges, side)
        if data is None:
            continue
        E, B, M, Mset, cyc = data
        eta = F(n * n, 25) - len(M)
        subsets = [frozenset(i for i in range(n) if (mask >> i) & 1) for mask in range(1 << n)]
        sigmas = {U: sigma_of(U, B, Mset) for U in subsets}
        tws = {U: subset_tw(n, M, cyc, U) for U in subsets}
        old_gamma = gamma_of(n, Mset, B)
        for f in M:
            for Q in cyc[f]:
                Q = tuple(Q)
                for U in subsets:
                    if not U or len(U) == n:
                        continue
                    rows = counted_rows(Q, U, M, cyc)
                    if not rows:
                        continue
                    lhs = sum(tws[U][v] for v in Q)
                    prebank = lhs - len(U) - sigmas[U]
                    if prebank <= 0:
                        continue
                    _switches, zero, strict, flat = classify_case(n, E, B, Mset, Q, U, rows)
                    zero_data = []
                    for sig, dg, Stuple in zero:
                        S = frozenset(Stuple)
                        xi2, info = xi2_for_switch(n, B, Mset, rows, S)
                        flat5 = is_flat5_switch(n, E, B, Mset, Stuple)
                        zero_data.append(
                            {
                                "S": tuple(sorted(S)),
                                "DeltaGamma": dg,
                                "Xi2": xi2,
                                "Flat5": flat5,
                                "info": info,
                            }
                        )
                    out.append(
                        {
                            "g6": g6,
                            "cut": cut_idx,
                            "side": "".join(map(str, side)),
                            "n": n,
                            "m": len(M),
                            "eta": eta,
                            "f": f,
                            "Q": Q,
                            "U": tuple(sorted(U)),
                            "lhs": lhs,
                            "sigma": sigmas[U],
                            "prebank": prebank,
                            "margin": eta - prebank,
                            "old_gamma": old_gamma,
                            "zero": zero_data,
                            "strict_count": len(strict),
                            "flat_count": len(flat),
                        }
                    )
    return out


def fmt(x):
    if isinstance(x, F):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    return str(x)


def print_case(label, rec):
    print(label)
    for key in ("g6", "cut", "side", "n", "m", "eta", "Q", "U", "lhs", "sigma", "prebank", "margin"):
        print(f"  {key}: {fmt(rec[key])}")
    for z in rec["zero"]:
        xi = z["Xi2"]
        print(
            "  zero:",
            {
                "S": z["S"],
                "DeltaGamma": z["DeltaGamma"],
                "Xi2": xi,
                "Flat5": z["Flat5"],
                "reason": z["info"].get("reason"),
            },
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--graph", default=None)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    if args.graph:
        graphs = [args.graph]
    else:
        graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
        if args.limit is not None:
            graphs = graphs[: args.limit]

    cases = []
    for idx, g6 in enumerate(graphs):
        cases.extend(analyze_graph(g6))
        if not args.graph and idx and idx % 1000 == 0:
            print(f"progress graphs={idx}/{len(graphs)} cases={len(cases)}", flush=True)

    stats = Counter()
    bad = []
    for c in cases:
        for z in c["zero"]:
            stats["zero"] += 1
            if z["Flat5"]:
                stats["flat5"] += 1
            if z["Xi2"] is None:
                stats["xi2_none"] += 1
            elif z["Xi2"] > 0:
                stats["xi2_positive"] += 1
            elif z["Xi2"] == 0:
                stats["xi2_zero"] += 1
            else:
                stats["xi2_negative"] += 1
            if (not z["Flat5"]) and (z["Xi2"] is None or z["Xi2"] <= 0):
                bad.append((c, z))

    print("=== Slack-CAGE Xi2 gate ===")
    print("graphs:", len(graphs))
    print("positive_cases:", len(cases))
    print("stats:", dict(stats))
    if cases:
        print_case("first_case:", cases[0])
    if bad:
        c, z = bad[0]
        print_case("first_bad_case:", c)
        print("first_bad_zero:", z)
    print("VERDICT:", "PASS_XI2_CORE" if cases and not bad else "CHECK")


if __name__ == "__main__":
    main()
