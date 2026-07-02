"""Exact diagnostics for the C5 full-mask two-bank flow form.

For an all-length-5 K-component row Q, the full-mask target is

    I(Q) <= N + eta,        eta = N^2/25 - |M|.

Claude's 2026-07-02 HDX gate gave the exact identity

    I(Q) - halfdeg(Q) = sum_e a_Q(e) (F(e)-1),

where F(e) is the cycle-edge traffic of the component and
a_Q(e)=|e cap V(Q)|/2.  Hence the full-mask target is equivalent to

    flow_excess <= eta + outside_bank,

with outside_bank = N - halfdeg(Q).

This script records exact witnesses for:
  * HDX failures: flow_excess > eta;
  * true two-bank tightness: eta + outside_bank - flow_excess minimal;
  * the explicit edge-flow identity.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import subprocess
from collections import Counter
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski, union_disjoint
    from _codex_dwhall_uniform_probe import components, supports_and_p
    from _codex_rowcap_non5_half_gate import adj_of
    from _h import Bconn, GENG, dec
    from _satzmu_conn import struct_for_side
    from _stark1 import gmins


def norm(e):
    u, v = e
    return (u, v) if u < v else (v, u)


def fmt(x):
    if isinstance(x, F):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    if isinstance(x, (tuple, list)):
        return "[" + ", ".join(fmt(y) for y in x) + "]"
    return str(x)


def record_min(slot, rec, key):
    if slot[0] is None or rec[key] < slot[0][key]:
        slot[0] = rec


def record_max(slot, rec, key):
    if slot[0] is None or rec[key] > slot[0][key]:
        slot[0] = rec


def cycle_edges_of_row(g, row):
    cyc = [norm((row[i], row[i + 1])) for i in range(len(row) - 1)]
    cyc.append(norm(g))
    return cyc


def edge_flow_for_component(comp, cyc):
    flow = Counter()
    for g in comp:
        rows = cyc[g]
        den = F(len(rows))
        for row in rows:
            for e in cycle_edges_of_row(g, row):
                flow[e] += F(1, den)
    return flow


def row_edge_weight(row, e):
    q = set(row)
    return F(int(e[0] in q) + int(e[1] in q), 2)


def analyze_cut(name, n, edges, side, acc):
    adj = adj_of(n, edges)
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M_raw, ell_raw, _T, _mu, cyc_raw = st
    if not M_raw:
        return

    M = [norm(g) for g in M_raw]
    ell = {norm(g): ell_raw[g] for g in M_raw}
    cyc = {norm(g): [tuple(P) for P in rows] for g, rows in cyc_raw.items()}
    supp, p = supports_and_p(n, M, cyc)
    comp_of = components(M, supp)

    deg = [len(adj[v]) for v in range(n)]
    m = len(M)
    eta = F(n * n, 25) - m
    tau = F(5 * m, n)

    acc["cuts"] += 1
    seen_comps = {}
    for f in M:
        comp = tuple(comp_of[f])
        if not comp or any(ell[g] != 5 for g in comp):
            continue
        if comp not in seen_comps:
            seen_comps[comp] = edge_flow_for_component(comp, cyc)
        flow = seen_comps[comp]

        for row in cyc[f]:
            if len(row) != 5:
                continue
            svals = tuple(sum((p[g][v] for g in comp), F(0)) for v in row)
            row_sum = sum(svals, F(0))
            halfdeg = F(sum(deg[v] for v in row), 2)
            outside_bank = F(n) - halfdeg
            flow_excess = row_sum - halfdeg
            hdx_margin = eta - flow_excess
            twobank_margin = eta + outside_bank - flow_excess
            full_margin = F(n) + eta - row_sum

            explicit = F(0)
            for e in edges:
                val = flow.get(norm(e), F(0))
                aq = row_edge_weight(row, e)
                if aq:
                    explicit += aq * (val - 1)
            identity_gap = explicit - flow_excess

            rec = {
                "name": name,
                "n": n,
                "m": m,
                "eta": eta,
                "tau": tau,
                "f": f,
                "row": tuple(row),
                "side": "".join(map(str, side)),
                "comp_size": len(comp),
                "row_sum": row_sum,
                "halfdeg": halfdeg,
                "outside_bank": outside_bank,
                "flow_excess": flow_excess,
                "hdx_margin": hdx_margin,
                "twobank_margin": twobank_margin,
                "full_margin": full_margin,
                "identity_gap": identity_gap,
                "s": svals,
                "deg": tuple(deg[v] for v in row),
                "active": tuple(i for i, s in enumerate(svals) if s > tau),
            }

            acc["rows"] += 1
            acc["by_comp_size"][len(comp)] += 1
            if row_sum > n:
                acc["over_rows"] += 1
                acc["over_active_counts"][len(rec["active"])] += 1
                acc["over_outside_bank"][outside_bank] += 1
                acc["over_halfdeg"][halfdeg] += 1
                record_min(acc["min_hdx_over"], rec, "hdx_margin")
                record_min(acc["min_twobank_over"], rec, "twobank_margin")
                record_min(acc["min_hdx_over_by_active"].setdefault(len(rec["active"]), [None]), rec, "hdx_margin")
                record_min(acc["min_twobank_over_by_active"].setdefault(len(rec["active"]), [None]), rec, "twobank_margin")
            if identity_gap != 0:
                acc["identity_fails"] += 1
                if acc["first_identity_fail"] is None:
                    acc["first_identity_fail"] = rec
            if hdx_margin < 0:
                acc["hdx_fails"] += 1
                if acc["first_hdx_fail"] is None:
                    acc["first_hdx_fail"] = rec
                if row_sum > n:
                    acc["hdx_over_fails"] += 1
                    if acc["first_hdx_over_fail"] is None:
                        acc["first_hdx_over_fail"] = rec
            if twobank_margin < 0:
                acc["twobank_fails"] += 1
                if acc["first_twobank_fail"] is None:
                    acc["first_twobank_fail"] = rec
            record_min(acc["min_twobank"], rec, "twobank_margin")
            record_min(acc["min_hdx"], rec, "hdx_margin")
            record_max(acc["max_flow_excess"], rec, "flow_excess")
            record_max(acc["max_outside_bank"], rec, "outside_bank")


def run_gmins(name, n, edges, max_cuts, acc):
    _adj, cuts = gmins(n, edges)
    if max_cuts is not None:
        cuts = cuts[:max_cuts]
    for side_s in cuts:
        analyze_cut(name, n, edges, [int(c) for c in side_s], acc)


def bridge(block1, block2, u, v):
    n, edges = union_disjoint(block1, block2)
    return n, edges + [(u, block1[0] + v)]


def print_rec(label, rec):
    print(label + ":")
    if rec is None:
        print("  none")
        return
    keys = (
        "twobank_margin",
        "hdx_margin",
        "full_margin",
        "identity_gap",
        "name",
        "n",
        "m",
        "eta",
        "tau",
        "row_sum",
        "halfdeg",
        "outside_bank",
        "flow_excess",
        "comp_size",
        "active",
        "s",
        "deg",
        "f",
        "row",
        "side",
    )
    for k in keys:
        print(f"  {k}: {fmt(rec[k])}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=8)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--max-cuts", type=int, default=None)
    ap.add_argument("--skip-census", action="store_true")
    ap.add_argument("--skip-named", action="store_true")
    args = ap.parse_args()

    acc = {
        "cuts": 0,
        "rows": 0,
        "over_rows": 0,
        "identity_fails": 0,
        "hdx_fails": 0,
        "hdx_over_fails": 0,
        "twobank_fails": 0,
        "first_identity_fail": None,
        "first_hdx_fail": None,
        "first_hdx_over_fail": None,
        "first_twobank_fail": None,
        "by_comp_size": Counter(),
        "over_active_counts": Counter(),
        "over_outside_bank": Counter(),
        "over_halfdeg": Counter(),
        "min_twobank": [None],
        "min_twobank_over": [None],
        "min_hdx": [None],
        "min_hdx_over": [None],
        "min_hdx_over_by_active": {},
        "min_twobank_over_by_active": {},
        "max_flow_excess": [None],
        "max_outside_bank": [None],
    }

    if not args.skip_named:
        named = [
            ("Grotzsch", mycielski(5, Cn(5))),
            ("M(C7)", mycielski(7, Cn(7))),
            ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
        ]
        for name, (n, edges) in named:
            run_gmins(name, n, edges, args.max_cuts, acc)

    if not args.skip_census:
        for nn in range(args.min_n, args.max_n + 1):
            out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True, check=True).stdout
            for g6 in out.split():
                n, edges = dec(g6)
                run_gmins(f"cen:{g6}", n, edges, args.max_cuts, acc)

    print("=== C5 full-mask two-bank probe ===")
    for k in ("cuts", "rows", "over_rows", "identity_fails", "hdx_fails", "hdx_over_fails", "twobank_fails"):
        print(f"{k}: {acc[k]}")
    print("by_comp_size:", dict(sorted(acc["by_comp_size"].items())))
    print("over_active_counts:", dict(sorted(acc["over_active_counts"].items())))
    print("over_outside_bank:", {fmt(k): v for k, v in sorted(acc["over_outside_bank"].items())})
    print("over_halfdeg:", {fmt(k): v for k, v in sorted(acc["over_halfdeg"].items())})
    print_rec("min_twobank", acc["min_twobank"][0])
    print_rec("min_twobank_over", acc["min_twobank_over"][0])
    print_rec("min_hdx", acc["min_hdx"][0])
    print_rec("min_hdx_over", acc["min_hdx_over"][0])
    for active, slot in sorted(acc["min_hdx_over_by_active"].items()):
        print_rec(f"min_hdx_over_active_{active}", slot[0])
    for active, slot in sorted(acc["min_twobank_over_by_active"].items()):
        print_rec(f"min_twobank_over_active_{active}", slot[0])
    print_rec("max_flow_excess", acc["max_flow_excess"][0])
    print_rec("max_outside_bank", acc["max_outside_bank"][0])
    print_rec("first_identity_fail", acc["first_identity_fail"])
    print_rec("first_hdx_fail", acc["first_hdx_fail"])
    print_rec("first_hdx_over_fail", acc["first_hdx_over_fail"])
    print_rec("first_twobank_fail", acc["first_twobank_fail"])


if __name__ == "__main__":
    main()
