"""Verify BANK0 hom-branch JSONL trace records.

Input records are emitted by _codex_bank0_hom_block_trace.py --jsonl-output.
This verifier independently reconstructs each graph/cut and rechecks hom-trace
records exactly using integer arithmetic.

It intentionally treats pure_no_hom_or_no_mono_hom records as routing records for
the CROSS/OSC branch, not as certificates for nonexistence.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
from collections import Counter

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski, union_disjoint
    from _codex_rowcap_non5_half_gate import adj_of
    from _h import Bconn, dec
    from _satzmu_conn import struct_for_side


def norm(e):
    u, v = e
    return (u, v) if u < v else (v, u)


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


def graph_by_name(name):
    if name.startswith("cen:"):
        return dec(name[4:])
    named = {
        "Grotzsch": mycielski(5, Cn(5)),
        "M(C7)": mycielski(7, Cn(7)),
        "C7|Grotzsch": bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0),
        "C5[2]": c5blow(2),
        "C5[3]": c5blow(3),
    }
    if name not in named:
        raise ValueError(f"unknown graph name {name!r}")
    return named[name]


def side_from_string(s):
    return [int(c) for c in s]


def verify_hom_trace(rec):
    n, edges = graph_by_name(rec["name"])
    edges_n = [norm(e) for e in edges]
    side = side_from_string(rec["side"])
    if n != rec["n"]:
        return False, "n mismatch"
    if len(side) != n:
        return False, "side length mismatch"
    adj = adj_of(n, edges)
    if not Bconn(n, adj, side):
        return False, "B not connected"
    st = struct_for_side(n, adj, side)
    if st is None:
        return False, "struct_for_side none"
    M_raw, ell_raw, _T, _mu, cyc_raw = st
    if len(M_raw) != rec["m"]:
        return False, "m mismatch"
    if any(ell_raw[g] != 5 for g in M_raw):
        return False, "non-l5 bad edge"

    labels = list(rec["labels"])
    if len(labels) != n:
        return False, "labels length mismatch"
    if any(c not in (0, 1, 2, 3, 4) for c in labels):
        return False, "label out of range"

    rows = []
    for _g, Ps in cyc_raw.items():
        for P in Ps:
            if len(P) == 5:
                rows.append(tuple(P))
    if len(rows) != rec["rows"]:
        return False, "row count mismatch"

    class_sizes = [0] * 5
    for c in labels:
        class_sizes[c] += 1
    if class_sizes != rec["class_sizes"]:
        return False, "class_sizes mismatch"

    edge_pair_counts = [0] * 5
    for u, v in edges_n:
        d = (labels[v] - labels[u]) % 5
        if d == 1:
            edge_pair_counts[labels[u]] += 1
        elif d == 4:
            edge_pair_counts[labels[v]] += 1
        else:
            return False, f"edge label failure {(u, v, labels[u], labels[v])}"
    if edge_pair_counts != rec["edge_pair_counts"]:
        return False, "edge_pair_counts mismatch"

    m = rec["m"]
    product_bounds = [class_sizes[i] * class_sizes[(i + 1) % 5] for i in range(5)]
    template_margins = [edge_pair_counts[i] - m for i in range(5)]
    product_margins = [product_bounds[i] - edge_pair_counts[i] for i in range(5)]
    bank0_margin = n * n - 25 * m

    checks = [
        (product_bounds, "product_bounds"),
        (template_margins, "template_margins"),
        (product_margins, "product_margins"),
    ]
    for got, key in checks:
        if got != rec[key]:
            return False, f"{key} mismatch"
    if bank0_margin != rec["bank0_margin"]:
        return False, "bank0 margin mismatch"
    if min(template_margins) != rec["min_template_margin"]:
        return False, "min template mismatch"
    if min(product_margins) != rec["min_product_margin"]:
        return False, "min product mismatch"

    for P in rows:
        plus = all((labels[P[j + 1]] - labels[P[j]]) % 5 == 1 for j in range(4))
        minus = all((labels[P[j + 1]] - labels[P[j]]) % 5 == 4 for j in range(4))
        if not (plus or minus):
            return False, f"row monotonicity failure {P}"

    if not all(x >= 0 for x in template_margins):
        return False, "negative template margin"
    if not all(x >= 0 for x in product_margins):
        return False, "negative product margin"
    if bank0_margin < 0:
        return False, "negative Bank0 margin"
    if not rec.get("ok", False):
        return False, "record ok flag false"

    return True, "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    counts = Counter()
    first_fail = None
    with open(args.jsonl, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if args.limit is not None and line_no > args.limit:
                break
            rec = json.loads(line)
            kind = rec.get("kind")
            counts[kind] += 1
            if kind == "hom_trace":
                ok, msg = verify_hom_trace(rec)
                if ok:
                    counts["verified_hom_trace"] += 1
                else:
                    counts["fail"] += 1
                    if first_fail is None:
                        first_fail = {"line": line_no, "msg": msg, "record": rec}
            elif kind == "pure_no_hom_or_no_mono_hom":
                counts["routing_record"] += 1
            else:
                counts["unknown_kind"] += 1
                if first_fail is None:
                    first_fail = {"line": line_no, "msg": f"unknown kind {kind}", "record": rec}

    print("=== BANK0 hom-trace JSONL verifier ===")
    print("counts:", dict(counts))
    print("first_fail:", first_fail)
    print("VERDICT:", "FAIL" if counts["fail"] or counts["unknown_kind"] else "PASS")


if __name__ == "__main__":
    main()
