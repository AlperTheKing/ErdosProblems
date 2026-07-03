"""Strong BANK0 row-monotone C5-hom probe.

Claude B0-3 asks for counterexamples at N=10..11 where a C5-homomorphism
exists but no row-monotone C5-homomorphism exists.

This script checks pure all-length-5, B-connected gamma-min maximum cuts.
For each such cut:
  1. search any graph C5-hom lambda: V -> Z5;
  2. if one exists, search a hom satisfying every certified row P in cyc[f]:
       lambda(P[j+1])-lambda(P[j]) is constantly +1 or constantly -1 mod 5.

All tests are finite exact combinatorics: no floats, no LP.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import subprocess
from collections import Counter
from multiprocessing import Pool

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski, union_disjoint
    from _codex_rowcap_non5_half_gate import adj_of
    from _h import Bconn, GENG, dec
    from _satzmu_conn import struct_for_side
    from _stark1 import gmins


def norm(e):
    u, v = e
    return (u, v) if u < v else (v, u)


def c5_hom_with_rows(n, edges, rows=()):
    """Return labels for a C5-hom satisfying row monotonicity, or None."""
    edges = [norm(e) for e in edges]
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    rows = [tuple(P) for P in rows]
    rows_by_v = [[] for _ in range(n)]
    for idx, P in enumerate(rows):
        for v in P:
            rows_by_v[v].append(idx)

    lab = [None] * n
    # Degree plus row-incidence order gives enough pruning for N<=11.
    order = sorted(range(n), key=lambda v: (-(len(adj[v]) + len(rows_by_v[v])), v))

    def edge_ok(v, c):
        for w in adj[v]:
            if lab[w] is not None and (lab[w] - c) % 5 not in (1, 4):
                return False
        return True

    def row_ok_idx(idx):
        P = rows[idx]
        ok_sign = False
        for step in (1, 4):
            base = None
            good = True
            for j, v in enumerate(P):
                if lab[v] is None:
                    continue
                b = (lab[v] - step * j) % 5
                if base is None:
                    base = b
                elif base != b:
                    good = False
                    break
            if good:
                ok_sign = True
                break
        return ok_sign

    def local_rows_ok(v):
        return all(row_ok_idx(idx) for idx in rows_by_v[v])

    def bt(k):
        if k == len(order):
            return True
        v = order[k]
        cands = [0] if k == 0 else range(5)
        for c in cands:
            if edge_ok(v, c):
                lab[v] = c
                if local_rows_ok(v) and bt(k + 1):
                    return True
                lab[v] = None
        return False

    return lab[:] if bt(0) else None


def check_cut(name, n, edges, side):
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
    for g, Ps in cyc_raw.items():
        for P in Ps:
            if len(P) == 5:
                rows.append(tuple(P))

    any_hom = c5_hom_with_rows(n, edges, rows=())
    if any_hom is None:
        return {
            "kind": "pure_no_hom",
            "name": name,
            "side": "".join(map(str, side)),
            "m": len(M_raw),
            "rows": len(rows),
        }

    mono_hom = c5_hom_with_rows(n, edges, rows=rows)
    if mono_hom is None:
        return {
            "kind": "counterexample",
            "name": name,
            "side": "".join(map(str, side)),
            "m": len(M_raw),
            "rows": len(rows),
            "any_hom": any_hom,
        }

    return {
        "kind": "pure_hom_mono",
        "name": name,
        "side": "".join(map(str, side)),
        "m": len(M_raw),
        "rows": len(rows),
    }


def graph_jobs_for_g6(g6):
    n, edges = dec(g6)
    _adj, cuts = gmins(n, edges)
    return [(f"cen:{g6}", n, edges, [int(c) for c in side_s]) for side_s in cuts]


def run_job(job):
    name, n, edges, side = job
    return check_cut(name, n, edges, side)


def named_jobs():
    def bridge(block1, block2, u, v):
        n, edges = union_disjoint(block1, block2)
        return n, edges + [(u, block1[0] + v)]

    def c5blow(t):
        n = 5 * t
        edges = []
        for i in range(5):
            for a in range(t):
                for b in range(t):
                    edges.append((i * t + a, ((i + 1) % 5) * t + b))
        return n, edges

    graphs = [
        ("Grotzsch", mycielski(5, Cn(5))),
        ("M(C7)", mycielski(7, Cn(7))),
        ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
        ("C5[2]", c5blow(2)),
        ("C5[3]", c5blow(3)),
    ]
    jobs = []
    for name, (n, edges) in graphs:
        _adj, cuts = gmins(n, edges)
        jobs.extend((name, n, edges, [int(c) for c in side_s]) for side_s in cuts)
    return jobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=8)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--skip-named", action="store_true")
    ap.add_argument("--skip-census", action="store_true")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--max-graphs", type=int, default=None)
    ap.add_argument("--stop-on-counterexample", action="store_true")
    args = ap.parse_args()

    jobs = []
    if not args.skip_named:
        jobs.extend(named_jobs())
    if not args.skip_census:
        seen_graphs = 0
        for nn in range(args.min_n, args.max_n + 1):
            out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True,
                                 text=True, check=True).stdout
            for g6 in out.split():
                jobs.extend(graph_jobs_for_g6(g6))
                seen_graphs += 1
                if args.max_graphs is not None and seen_graphs >= args.max_graphs:
                    break
            if args.max_graphs is not None and seen_graphs >= args.max_graphs:
                break

    acc = Counter()
    first = {}

    def consume(res):
        if res is None:
            return False
        acc[res["kind"]] += 1
        first.setdefault(res["kind"], res)
        return res["kind"] == "counterexample"

    if args.workers <= 1:
        for job in jobs:
            if consume(run_job(job)) and args.stop_on_counterexample:
                break
    else:
        with Pool(args.workers) as pool:
            for res in pool.imap_unordered(run_job, jobs, chunksize=32):
                if consume(res) and args.stop_on_counterexample:
                    pool.terminate()
                    break

    pure = sum(acc.values())
    print("=== BANK0 row-monotone hom probe ===")
    print("jobs:", len(jobs))
    print("pure_l5_cuts:", pure)
    for k in ("pure_hom_mono", "pure_no_hom", "counterexample"):
        print(f"{k}:", acc[k])
    for k in ("counterexample", "pure_no_hom", "pure_hom_mono"):
        print(f"first_{k}:", first.get(k))
    verdict = "FAIL" if acc["counterexample"] else "PASS"
    print("VERDICT:", verdict)


if __name__ == "__main__":
    main()
