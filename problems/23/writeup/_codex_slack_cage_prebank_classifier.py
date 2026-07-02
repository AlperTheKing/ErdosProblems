"""Classify positive proper-counted Slack-CAGE prebank cases.

For each connected-B gamma-min cut in a small census, find cases with

  prebank_Q(U) = D_Q(U) - |U| - sigma(U) > 0

where U is proper and contains at least one counted row.  For those cases,
enumerate GPT-Pro cage-switch core sets inside U and report whether a zero
slack switch with DeltaGamma <= 0 exists, and whether any strict drop exists.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import subprocess
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _h import GENG, dec
    from _stark1 import gmins
    from _codex_slack_cage_switch_gate import (
        all_subsets,
        build_data,
        counted_rows,
        delta,
        flip_blue,
        gamma_of,
        is_minimal_core,
        sigma_of,
    )


def subset_tw(n, M, cyc, U):
    tw = [F(0) for _ in range(n)]
    for g in M:
        den = len(cyc[g])
        for P in cyc[g]:
            if frozenset(P) <= U:
                mass = F(1, den)
                for v in P:
                    tw[v] += mass
    return tw


def classify_case(n, E, B, Mset, Q, U, counted):
    old_gamma = gamma_of(n, Mset, B)
    switches = []
    for S in all_subsets(n):
        if not S <= U:
            continue
        if not is_minimal_core(n, E, B, Q, U, counted, S):
            continue
        sig = sigma_of(S, B, Mset)
        BS = flip_blue(E, B, S)
        MS = E - BS
        new_gamma = gamma_of(n, MS, BS)
        dg = None if new_gamma is None or old_gamma is None else new_gamma - old_gamma
        switches.append((sig, dg, tuple(sorted(S))))
    zero = [s for s in switches if s[0] == 0]
    strict = [s for s in zero if s[1] is not None and s[1] < 0]
    flat = [s for s in zero if s[1] == 0]
    return switches, zero, strict, flat


def run_graph(g6, max_cases):
    n, edges = dec(g6)
    adj, cuts = gmins(n, edges)
    out = []
    for cut_idx, side_s in enumerate(cuts):
        side = [int(c) for c in side_s]
        data = build_data(n, edges, side)
        if data is None:
            continue
        E, B, M, Mset, cyc = data
        eta = F(n * n, 25) - len(M)
        subsets = all_subsets(n)
        sigmas = {U: sigma_of(U, B, Mset) for U in subsets}
        tws = {U: subset_tw(n, M, cyc, U) for U in subsets}
        allmask_size = n
        for f in M:
            for Q in cyc[f]:
                for U in subsets:
                    if not U or len(U) == allmask_size:
                        continue
                    rows = counted_rows(Q, U, M, cyc)
                    if not rows:
                        continue
                    lhs = sum(tws[U][v] for v in Q)
                    prebank = lhs - len(U) - sigmas[U]
                    if prebank <= 0:
                        continue
                    margin = eta - prebank
                    switches, zero, strict, flat = classify_case(n, E, B, Mset, Q, U, rows)
                    rec = {
                        "g6": g6,
                        "cut": cut_idx,
                        "side": "".join(map(str, side)),
                        "n": n,
                        "m": len(M),
                        "eta": eta,
                        "f": f,
                        "Q": tuple(Q),
                        "U": tuple(sorted(U)),
                        "lhs": lhs,
                        "sigma": sigmas[U],
                        "prebank": prebank,
                        "margin": margin,
                        "counted": [(g, tuple(P)) for g, P, _pset in rows],
                        "zero": zero,
                        "strict": strict,
                        "flat": flat,
                        "switches": switches,
                    }
                    out.append(rec)
                    if max_cases is not None and len(out) >= max_cases:
                        return out
    return out


def parse_tuple(s):
    if s is None:
        return None
    text = s.strip()
    if text.startswith("(") and text.endswith(")"):
        text = text[1:-1]
    if not text:
        return tuple()
    return tuple(int(part.strip()) for part in text.split(",") if part.strip())


def run_target(g6, cut_index, Q, U):
    n, edges = dec(g6)
    adj, cuts = gmins(n, edges)
    if cut_index < 0 or cut_index >= len(cuts):
        raise SystemExit(f"cut index {cut_index} outside 0..{len(cuts)-1}")

    side = [int(c) for c in cuts[cut_index]]
    data = build_data(n, edges, side)
    if data is None:
        raise SystemExit("target cut did not build connected-B Slack-CAGE data")

    E, B, M, Mset, cyc = data
    Q = tuple(Q)
    U = frozenset(U)
    eta = F(n * n, 25) - len(M)
    sigma = sigma_of(U, B, Mset)
    tw = subset_tw(n, M, cyc, U)
    lhs = sum(tw[v] for v in Q)
    prebank = lhs - len(U) - sigma
    margin = eta - prebank
    rows = counted_rows(Q, U, M, cyc)
    f = None
    for g in M:
        if Q in [tuple(P) for P in cyc[g]]:
            f = g
            break
    switches, zero, strict, flat = classify_case(n, E, B, Mset, Q, U, rows)
    return {
        "g6": g6,
        "cut": cut_index,
        "side": "".join(map(str, side)),
        "n": n,
        "m": len(M),
        "eta": eta,
        "f": f,
        "Q": Q,
        "U": tuple(sorted(U)),
        "lhs": lhs,
        "sigma": sigma,
        "prebank": prebank,
        "margin": margin,
        "counted": [(g, tuple(P)) for g, P, _pset in rows],
        "zero": zero,
        "strict": strict,
        "flat": flat,
        "switches": switches,
    }


def fmt(x):
    if isinstance(x, F):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    if isinstance(x, tuple):
        return "(" + ",".join(fmt(v) for v in x) + ")"
    return str(x)


def print_case(label, rec):
    print(label)
    for key in ("g6", "cut", "side", "n", "m", "eta", "f", "Q", "U", "lhs", "sigma", "prebank", "margin"):
        print(f"  {key}: {fmt(rec[key])}")
    print("  counted:", rec["counted"])
    print("  zero:", rec["zero"])
    print("  strict:", rec["strict"])
    print("  flat:", rec["flat"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--max-cases-per-graph", type=int, default=None)
    ap.add_argument("--g6", default=None)
    ap.add_argument("--cut-index", type=int, default=0)
    ap.add_argument("--Q", default=None)
    ap.add_argument("--U", default=None)
    args = ap.parse_args()

    if args.g6 is not None:
        Q = parse_tuple(args.Q)
        U = parse_tuple(args.U)
        if Q is None or U is None:
            raise SystemExit("--g6 target mode requires --Q and --U")
        rec = run_target(args.g6, args.cut_index, Q, U)
        print("=== targeted positive prebank classifier ===")
        print_case("target_case:", rec)
        print(
            "VERDICT:",
            "PASS_BALANCED_TARGET" if rec["flat"] and not rec["strict"] else "CHECK_TARGET",
        )
        return

    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    if args.limit is not None:
        graphs = graphs[: args.limit]

    cases = []
    for idx, g6 in enumerate(graphs):
        found = run_graph(g6, args.max_cases_per_graph)
        cases.extend(found)
        if idx and idx % 1000 == 0:
            print(f"progress graphs={idx}/{len(graphs)} cases={len(cases)}", flush=True)

    no_zero = [c for c in cases if not c["zero"]]
    no_flat = [c for c in cases if not c["flat"]]
    strict = [c for c in cases if c["strict"]]
    print("=== positive proper-counted prebank classifier ===")
    print("n:", args.n)
    print("graphs:", len(graphs))
    print("cases:", len(cases))
    print("no_zero:", len(no_zero))
    print("no_flat:", len(no_flat))
    print("strict_drop_cases:", len(strict))
    values = {}
    for c in cases:
        values[str(c["prebank"])] = values.get(str(c["prebank"]), 0) + 1
    print("prebank_values:", values)
    if cases:
        print_case("first_case:", cases[0])
    if no_zero:
        print_case("first_no_zero:", no_zero[0])
    if strict:
        print_case("first_strict:", strict[0])
    print("VERDICT:", "PASS_BALANCED" if cases and not no_flat and not strict else "CHECK")


if __name__ == "__main__":
    main()
