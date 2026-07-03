"""Emit exact BANK0 hom-branch block traces.

For each pure all-length-5, B-connected gamma-min maximum cut whose graph admits a
row-monotone C5 homomorphism, emit/check the finite data used by the global C5-label
AM-GM finish:

  labels lambda : V -> Z5,
  class sizes n_i,
  edge counts e_i between classes i and i+1,
  bad-edge count m,
  exact inequalities m <= e_i <= n_i n_{i+1} for all i,
  exact Bank0 margin N^2 - 25m >= 0.

This is a trace/verification artifact for the hom-positive branch only.  No-hom
pure-l5 cuts are counted and left to CROSS/OSC/corridor certificates.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import subprocess
from collections import Counter

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski, union_disjoint
    from _codex_bank0_row_monotone_hom_probe import c5_hom_with_rows
    from _codex_rowcap_non5_half_gate import adj_of
    from _h import Bconn, GENG, dec
    from _satzmu_conn import struct_for_side
    from _stark1 import gmins


def norm(e):
    u, v = e
    return (u, v) if u < v else (v, u)


def side_str(side):
    return "".join(map(str, side))


def c5blow(t):
    n = 5 * t
    edges = []
    for i in range(5):
        for a in range(t):
            for b in range(t):
                edges.append((i * t + a, ((i + 1) % 5) * t + b))
    return n, edges


def bridge(block1, block2, u, v):
    n, edges = union_disjoint(block1, block2)
    return n, edges + [(u, block1[0] + v)]


def named_graphs():
    return [
        ("Grotzsch", mycielski(5, Cn(5))),
        ("M(C7)", mycielski(7, Cn(7))),
        ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
        ("C5[2]", c5blow(2)),
        ("C5[3]", c5blow(3)),
    ]


def trace_cut(name, n, edges, side):
    adj = adj_of(n, edges)
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M_raw, ell_raw, _T, _mu, cyc_raw = st
    if not M_raw:
        return None
    if any(ell_raw[g] != 5 for g in M_raw):
        return None

    rows = []
    for _g, Ps in cyc_raw.items():
        for P in Ps:
            if len(P) == 5:
                rows.append(tuple(P))

    labels = c5_hom_with_rows(n, edges, rows=rows)
    if labels is None:
        return {
            "kind": "pure_no_hom_or_no_mono_hom",
            "name": name,
            "side": side_str(side),
            "n": n,
            "m": len(M_raw),
            "rows": len(rows),
        }

    edges_n = [norm(e) for e in edges]
    m = len(M_raw)
    class_sizes = [0] * 5
    for c in labels:
        class_sizes[c] += 1

    edge_pair_counts = [0] * 5
    edge_label_failures = []
    for u, v in edges_n:
        d = (labels[v] - labels[u]) % 5
        if d == 1:
            edge_pair_counts[labels[u]] += 1
        elif d == 4:
            edge_pair_counts[labels[v]] += 1
        else:
            edge_label_failures.append((u, v, labels[u], labels[v]))

    product_bounds = [class_sizes[i] * class_sizes[(i + 1) % 5] for i in range(5)]
    template_margins = [edge_pair_counts[i] - m for i in range(5)]
    product_margins = [product_bounds[i] - edge_pair_counts[i] for i in range(5)]
    bank0_margin = n * n - 25 * m

    row_failures = []
    for P in rows:
        plus = all((labels[P[j + 1]] - labels[P[j]]) % 5 == 1 for j in range(4))
        minus = all((labels[P[j + 1]] - labels[P[j]]) % 5 == 4 for j in range(4))
        if not (plus or minus):
            row_failures.append(P)

    ok = (
        not edge_label_failures
        and not row_failures
        and all(x >= 0 for x in template_margins)
        and all(x >= 0 for x in product_margins)
        and bank0_margin >= 0
    )

    return {
        "kind": "hom_trace",
        "ok": ok,
        "name": name,
        "side": side_str(side),
        "n": n,
        "m": m,
        "rows": len(rows),
        "labels": labels,
        "class_sizes": class_sizes,
        "edge_pair_counts": edge_pair_counts,
        "product_bounds": product_bounds,
        "template_margins": template_margins,
        "product_margins": product_margins,
        "bank0_margin": bank0_margin,
        "min_template_margin": min(template_margins),
        "min_product_margin": min(product_margins),
        "edge_label_failures": edge_label_failures[:5],
        "row_failures": row_failures[:5],
    }


def all_jobs(args):
    jobs = []
    if not args.skip_named:
        for name, (n, edges) in named_graphs():
            _adj, cuts = gmins(n, edges)
            for side_s in cuts:
                jobs.append((name, n, edges, [int(c) for c in side_s]))
    if not args.skip_census:
        seen = 0
        for nn in range(args.min_n, args.max_n + 1):
            out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True,
                                 text=True, check=True).stdout
            for g6 in out.split():
                n, edges = dec(g6)
                _adj, cuts = gmins(n, edges)
                for side_s in cuts:
                    jobs.append((f"cen:{g6}", n, edges, [int(c) for c in side_s]))
                seen += 1
                if args.max_graphs is not None and seen >= args.max_graphs:
                    return jobs
    return jobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=8)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--skip-named", action="store_true")
    ap.add_argument("--skip-census", action="store_true")
    ap.add_argument("--max-graphs", type=int, default=None)
    ap.add_argument("--trace-limit", type=int, default=20)
    ap.add_argument("--output", default=None)
    ap.add_argument("--jsonl-output", default=None)
    args = ap.parse_args()

    acc = Counter()
    first = {}
    traces = []
    worst_template = None
    worst_bank0 = None

    jsonl = open(args.jsonl_output, "w", encoding="utf-8") if args.jsonl_output else None
    try:
        for job in all_jobs(args):
            res = trace_cut(*job)
            if res is None:
                continue
            if jsonl is not None:
                jsonl.write(json.dumps(res, sort_keys=True) + "\n")
            acc[res["kind"]] += 1
            first.setdefault(res["kind"], res)
            if res["kind"] == "hom_trace":
                if not res["ok"]:
                    acc["hom_trace_fail"] += 1
                    first.setdefault("hom_trace_fail", res)
                key_t = (res["min_template_margin"], res["name"], res["side"])
                key_b = (res["bank0_margin"], res["name"], res["side"])
                if worst_template is None or key_t < worst_template:
                    worst_template = key_t
                if worst_bank0 is None or key_b < worst_bank0:
                    worst_bank0 = key_b
                if len(traces) < args.trace_limit:
                    traces.append(res)
    finally:
        if jsonl is not None:
            jsonl.close()

    summary = {
        "jobs_scanned": sum(acc.values()),
        "counts": dict(acc),
        "worst_template_margin": worst_template,
        "worst_bank0_margin": worst_bank0,
        "first_no_hom_or_no_mono": first.get("pure_no_hom_or_no_mono_hom"),
        "first_hom_trace_fail": first.get("hom_trace_fail"),
        "verdict": "FAIL" if acc["hom_trace_fail"] else "PASS",
        "traces": traces,
        "jsonl_output": args.jsonl_output,
    }

    print("=== BANK0 hom-branch block trace ===")
    print("counts:", dict(acc))
    print("worst_template_margin:", worst_template)
    print("worst_bank0_margin:", worst_bank0)
    print("first_hom_trace_fail:", first.get("hom_trace_fail"))
    print("first_no_hom_or_no_mono:", first.get("pure_no_hom_or_no_mono_hom"))
    print("VERDICT:", summary["verdict"])

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, sort_keys=True)
        print("wrote:", args.output)
    if args.jsonl_output:
        print("wrote_jsonl:", args.jsonl_output)


if __name__ == "__main__":
    main()



