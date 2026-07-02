"""Exact flat-bank gate for positive Slack-CAGE prebank cases.

For each positive proper-counted prebank case, enumerate the existing
minimal cage cores and test whether at least one is a flat length-5 bank atom:

  sigma(S) = 0
  DeltaGamma(S) = 0
  every crossing counted row has length 5
  peeling S from U strictly decreases prebank_Q(U)

This is not a proof of Slack-CAGE.  It is a focused falsifier for the
prebank-first decomposition:

  positive proper prebank = flat C5 bank + non-flat Gamma-drop cage.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import subprocess
from collections import Counter
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _h import GENG, dec
    from _stark1 import gmins
    from _codex_slack_cage_prebank_classifier import classify_case, subset_tw
    from _codex_slack_cage_switch_gate import build_data, counted_rows, sigma_of


def prebank_of(n, B, M, Mset, cyc, Q, U):
    tw = subset_tw(n, M, cyc, U)
    lhs = sum(tw[v] for v in Q)
    return lhs - len(U) - sigma_of(U, B, Mset), lhs


def flat_bank_witnesses(n, E, B, M, Mset, cyc, Q, U, counted):
    pre_u, _lhs = prebank_of(n, B, M, Mset, cyc, Q, U)
    _switches, zero, _strict, flat = classify_case(n, E, B, Mset, Q, U, counted)
    out = []
    for sig, dg, Stuple in flat:
        S = frozenset(Stuple)
        U2 = frozenset(set(U) - set(S))
        pre_u2, _lhs2 = prebank_of(n, B, M, Mset, cyc, Q, U2)
        crossing = []
        for g, P, pset in counted:
            if pset & S and not pset <= S:
                crossing.append((g, tuple(P), len(P)))
        lengths = sorted({L for _g, _P, L in crossing})
        drop = pre_u - pre_u2
        is_flat_bank = (
            sig == 0
            and dg == 0
            and crossing
            and all(L == 5 for _g, _P, L in crossing)
            and drop > 0
        )
        out.append(
            {
                "S": tuple(sorted(S)),
                "sigma": sig,
                "DeltaGamma": dg,
                "crossing_lengths": lengths,
                "crossing": crossing,
                "pre_after_peel": pre_u2,
                "drop": drop,
                "is_flat_bank": is_flat_bank,
            }
        )
    return out


def analyze_graph(g6):
    n, edges = dec(g6)
    adj, cuts = gmins(n, edges)
    cases = []
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
                    banks = flat_bank_witnesses(n, E, B, M, Mset, cyc, Q, U, rows)
                    cases.append(
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
                            "flat_banks": banks,
                        }
                    )
    return cases


def fmt_frac(x):
    if isinstance(x, F):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    return str(x)


def print_case(label, rec):
    print(label)
    for key in ("g6", "cut", "side", "n", "m", "eta", "f", "Q", "U", "lhs", "sigma", "prebank", "margin"):
        print(f"  {key}: {fmt_frac(rec[key])}")
    for b in rec["flat_banks"]:
        print(
            "  bank:",
            {
                "S": b["S"],
                "DeltaGamma": b["DeltaGamma"],
                "crossing_lengths": b["crossing_lengths"],
                "drop": fmt_frac(b["drop"]),
                "pre_after_peel": fmt_frac(b["pre_after_peel"]),
                "is_flat_bank": b["is_flat_bank"],
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

    no_flat_bank = [c for c in cases if not any(b["is_flat_bank"] for b in c["flat_banks"])]
    strict_drop = [
        c
        for c in cases
        if any(b["DeltaGamma"] is not None and b["DeltaGamma"] < 0 for b in c["flat_banks"])
    ]
    value_counts = Counter(str(c["prebank"]) for c in cases)
    print("=== Slack-CAGE flat-bank gate ===")
    print("graphs:", len(graphs))
    print("cases:", len(cases))
    print("no_flat_bank:", len(no_flat_bank))
    print("strict_drop_among_flat_list:", len(strict_drop))
    print("prebank_values:", dict(value_counts))
    if cases:
        print_case("first_case:", cases[0])
    if no_flat_bank:
        print_case("first_no_flat_bank:", no_flat_bank[0])
    print("VERDICT:", "PASS_FLAT_BANK" if cases and not no_flat_bank else "CHECK")


if __name__ == "__main__":
    main()
