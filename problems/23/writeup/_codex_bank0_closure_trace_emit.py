#!/usr/bin/env python3
"""Emit exact Bank0 sibling-closure traces for pure length-5 no-hom cuts.

This is a finite gate/prototype for the reconciled Bank0 L2 closure machinery:

  C1 row-interval closure;
  C2 row-family closure for a fixed oriented first-exit door;
  C3 blue-detour closure in the row-edge-deleted blue graph;
  C4 terminal-prefix completion using the existing corridor primitive.

For each pure all-length-5, B-connected gamma-min maximum cut outside the
C5-hom branch, it enumerates closed packets U and checks for positive pressure

    Pi(U) = 5 * s(U) - N * |U|,

where s(v) = sum_f p_f(v).  The expected census gate is that no minimal positive
closed packet appears on N <= 11.

This is not yet the final proof emitter; it is an exact traceable census gate.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import subprocess
from collections import Counter, deque
from fractions import Fraction as F
from pathlib import Path

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski, union_disjoint
    from _codex_bank0_row_monotone_hom_probe import c5_hom_with_rows
    from _codex_bankl_lcb_skeleton import terminal_prefix_closure
    from _codex_rowcap_non5_half_gate import adj_of
    from _h import Bconn, GENG, dec
    from _satzmu_conn import struct_for_side
    from _stark1 import gmins


def norm(e: tuple[int, int]) -> tuple[int, int]:
    u, v = e
    return (u, v) if u < v else (v, u)


def frac_s(x: F) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def side_str(side: list[int]) -> str:
    return "".join(map(str, side))


def named_graphs():
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

    return [
        ("Grotzsch", mycielski(5, Cn(5))),
        ("M(C7)", mycielski(7, Cn(7))),
        ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
        ("C5[2]", c5blow(2)),
        ("C5[3]", c5blow(3)),
    ]


def pure_l5_context(name: str, n: int, edges: list[tuple[int, int]], side: list[int], assume_no_hom: bool = False):
    adj = adj_of(n, edges)
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, _T, _mu, cyc = st
    if not M or any(ell[g] != 5 for g in M):
        return None

    rows = []
    for _g, paths in cyc.items():
        for P in paths:
            if len(P) == 5:
                rows.append(tuple(P))
    if not assume_no_hom:
        labels = c5_hom_with_rows(n, edges, rows=rows)
        if labels is not None:
            return None

    blue_edges = {norm((u, v)) for u, v in edges if side[u] != side[v]}
    row_blue_edges = {
        norm((P[i], P[i + 1]))
        for paths in cyc.values()
        for P in paths
        for i in range(len(P) - 1)
    }
    s = [F(0) for _ in range(n)]
    for g in M:
        den = F(len(cyc[g]))
        counts: dict[int, int] = {}
        for P in cyc[g]:
            for v in set(P):
                counts[v] = counts.get(v, 0) + 1
        for v, c in counts.items():
            s[v] += F(c, den)
    return {
        "name": name,
        "n": n,
        "edges": [norm(e) for e in edges],
        "side": side,
        "adj": adj,
        "st": st,
        "M": M,
        "cyc": cyc,
        "rows": rows,
        "blue_edges": blue_edges,
        "row_blue_edges": row_blue_edges,
        "s": s,
    }


def pressure(ctx: dict, U: int) -> F:
    n = ctx["n"]
    total = F(0)
    for v in range(n):
        if (U >> v) & 1:
            total += ctx["s"][v]
    return 5 * total - n * U.bit_count()


def mask_of(vertices) -> int:
    out = 0
    for v in vertices:
        out |= 1 << int(v)
    return out


def vertices_of(mask: int, n: int) -> list[int]:
    return [v for v in range(n) if (mask >> v) & 1]


def shortest_blue_path(n: int, blue_edges: set[tuple[int, int]], start: int, end: int, deleted: set[tuple[int, int]]):
    adj = [[] for _ in range(n)]
    for e in blue_edges:
        if e in deleted:
            continue
        u, v = e
        adj[u].append(v)
        adj[v].append(u)
    prev = {start: None}
    q = deque([start])
    while q:
        u = q.popleft()
        if u == end:
            break
        for v in adj[u]:
            if v not in prev:
                prev[v] = u
                q.append(v)
    if end not in prev:
        return None
    path = []
    cur = end
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path


def c1_row_interval(ctx: dict, U: int) -> tuple[int, list[dict]]:
    out = U
    events = []
    for P in ctx["rows"]:
        idxs = [i for i, v in enumerate(P) if (out >> v) & 1]
        if len(idxs) < 2:
            continue
        lo, hi = min(idxs), max(idxs)
        add = mask_of(P[lo : hi + 1])
        new = add & ~out
        if new:
            out |= add
            events.append({"rule": "C1", "row": list(P), "lo": lo, "hi": hi, "add": vertices_of(new, ctx["n"])})
    return out, events


def c2_row_family(ctx: dict, U: int) -> tuple[int, list[dict]]:
    out = U
    events = []
    for f, paths in ctx["cyc"].items():
        requests: set[tuple[int, tuple[int, int], int]] = set()
        for P0 in paths:
            for tau in f:
                P = list(P0)
                if P[0] != tau:
                    P = list(reversed(P))
                if P[0] != tau or not ((out >> tau) & 1):
                    continue
                r = 0
                while r + 1 < len(P) and ((out >> P[r + 1]) & 1):
                    r += 1
                if r + 1 >= len(P):
                    continue
                if r == 0 and not ((out >> P[0]) & 1):
                    continue
                exit_edge = norm((P[r], P[r + 1]))
                requests.add((tau, exit_edge, r))
        for tau, exit_edge, r in sorted(requests):
            for P0 in paths:
                P = list(P0)
                if P[0] != tau:
                    P = list(reversed(P))
                if P[0] != tau or r + 1 >= len(P):
                    continue
                if norm((P[r], P[r + 1])) != exit_edge:
                    continue
                add = mask_of(P[: r + 1])
                new = add & ~out
                if new:
                    out |= add
                    events.append({
                        "rule": "C2",
                        "bad_edge": list(f),
                        "tau": tau,
                        "exit": list(exit_edge),
                        "r": r,
                        "add": vertices_of(new, ctx["n"]),
                    })
    return out, events


def c3_blue_detour(ctx: dict, U: int) -> tuple[int, list[dict]]:
    out = U
    events = []
    n = ctx["n"]
    for P in ctx["rows"]:
        row_edges = {norm((P[i], P[i + 1])) for i in range(len(P) - 1)}
        for i in range(len(P) - 1):
            x, y = P[i], P[i + 1]
            if not (((out >> x) & 1) and ((out >> y) & 1)):
                continue
            e = norm((x, y))
            path = shortest_blue_path(n, ctx["blue_edges"], x, y, row_edges)
            if path is None or len(path) <= 2:
                # If deleting the whole row is too strong, also record the
                # single-edge detour used in the theta witness.
                path = shortest_blue_path(n, ctx["blue_edges"], x, y, {e})
            if path is None or len(path) <= 2:
                continue
            add = mask_of(path[1:-1])
            new = add & ~out
            if new:
                out |= add
                events.append({"rule": "C3", "edge": [x, y], "path": path, "add": vertices_of(new, n)})
    return out, events


def c4_terminal_prefix(ctx: dict, U: int) -> tuple[int, list[dict]]:
    out = U
    events = []
    for P in ctx["rows"]:
        idxs = [i for i, v in enumerate(P) if (out >> v) & 1]
        if not idxs:
            continue
        lo, hi = min(idxs), max(idxs)
        is_prefix = idxs == list(range(0, hi + 1))
        is_suffix = idxs == list(range(lo, len(P)))
        if is_prefix or is_suffix:
            continue
        add = mask_of(P[: hi + 1]) | mask_of(P[lo:])
        new = add & ~out
        if new:
            out |= add
            events.append({
                "rule": "C4_row_terminal_shadow",
                "row": list(P),
                "lo": lo,
                "hi": hi,
                "add": vertices_of(new, ctx["n"]),
            })

    before = out
    seed = set(vertices_of(out, ctx["n"]))
    closed = terminal_prefix_closure(seed, ctx["cyc"], ctx["n"])
    out = mask_of(closed)
    new = out & ~before
    if new:
        events.append({"rule": "C4", "add": vertices_of(new, ctx["n"])})
    return out, events


def close_packet(ctx: dict, seed_mask: int, keep_trace: bool = False) -> tuple[int, list[dict]]:
    U = seed_mask
    trace: list[dict] = []
    for iteration in range(64):
        before = U
        for fn in (c1_row_interval, c2_row_family, c3_blue_detour, c4_terminal_prefix):
            U2, events = fn(ctx, U)
            if events and keep_trace:
                trace.extend({"iteration": iteration, **ev} for ev in events)
            U = U2
        if U == before:
            break
    else:
        raise RuntimeError("closure did not converge")
    return U, trace


def analyze_context(ctx: dict, trace_limit: int = 3) -> dict:
    n = ctx["n"]
    closure_cache: dict[int, int] = {}
    closed: set[int] = set()
    for seed in range(1 << n):
        cl, _trace = close_packet(ctx, seed)
        closure_cache[seed] = cl
        closed.add(cl)

    positive = sorted((U for U in closed if pressure(ctx, U) > 0), key=lambda U: (U.bit_count(), U))
    minimal = []
    closed_list = sorted(closed, key=lambda U: (U.bit_count(), U))
    for U in positive:
        proper_positive = False
        for W in closed_list:
            if W == U or W == 0:
                continue
            if (W & U) == W and pressure(ctx, W) > 0:
                proper_positive = True
                break
        if not proper_positive:
            minimal.append(U)

    trace_records = []
    for U in minimal[:trace_limit]:
        # Choose a smallest seed whose closure is U for a compact trace.
        seeds = [s for s, cl in closure_cache.items() if cl == U]
        seed = min(seeds, key=lambda x: (x.bit_count(), x))
        _cl, trace = close_packet(ctx, seed, keep_trace=True)
        trace_records.append({
            "seed": vertices_of(seed, n),
            "closed": vertices_of(U, n),
            "Pi": frac_s(pressure(ctx, U)),
            "trace": trace,
        })

    return {
        "schema": "bank0_closure_trace_v1",
        "name": ctx["name"],
        "n": n,
        "m": len(ctx["M"]),
        "side": side_str(ctx["side"]),
        "rows": len(ctx["rows"]),
        "s": [frac_s(x) for x in ctx["s"]],
        "closed_count": len(closed),
        "positive_closed_count": len(positive),
        "minimal_positive_count": len(minimal),
        "min_positive": None if not positive else {
            "vertices": vertices_of(positive[0], n),
            "Pi": frac_s(pressure(ctx, positive[0])),
        },
        "minimal_positive_traces": trace_records,
        "verdict": "PASS_NO_POSITIVE_PACKET" if not minimal else "FAIL_POSITIVE_PACKET",
    }


def iter_jobs(args):
    if args.input_jsonl:
        with Path(args.input_jsonl).open("r", encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                rec = json.loads(line)
                if rec.get("kind") != "pure_no_hom_or_no_mono_hom":
                    continue
                name = rec["name"]
                if name.startswith("cen:"):
                    n, edges = dec(name[4:])
                else:
                    lookup = dict(named_graphs())
                    if name not in lookup:
                        raise ValueError(f"cannot reconstruct graph name {name!r}")
                    n, edges = lookup[name]
                yield name, n, edges, [int(c) for c in rec["side"]]
        return

    if not args.skip_named:
        for name, (n, edges) in named_graphs():
            _adj, cuts = gmins(n, edges)
            for side_s in cuts:
                yield name, n, edges, [int(c) for c in side_s]
    if not args.skip_census:
        seen = 0
        for nn in range(args.min_n, args.max_n + 1):
            out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True, check=True).stdout
            for g6 in out.split():
                n, edges = dec(g6)
                _adj, cuts = gmins(n, edges)
                for side_s in cuts:
                    yield f"cen:{g6}", n, edges, [int(c) for c in side_s]
                seen += 1
                if args.max_graphs is not None and seen >= args.max_graphs:
                    return


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=8)
    ap.add_argument("--max-n", type=int, default=9)
    ap.add_argument("--max-graphs", type=int, default=None)
    ap.add_argument("--limit-cuts", type=int, default=None)
    ap.add_argument("--skip-records", type=int, default=0)
    ap.add_argument("--progress-every", type=int, default=0)
    ap.add_argument("--skip-named", action="store_true")
    ap.add_argument("--skip-census", action="store_true")
    ap.add_argument("--input-jsonl", default="")
    ap.add_argument("--output", default="tmp/bank0_closure_trace_v1.jsonl")
    ap.add_argument("--summary", default="tmp/bank0_closure_trace_v1_summary.json")
    args = ap.parse_args()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    acc: Counter[str] = Counter()
    first_fail = None
    matched_records = 0
    skipped_records = 0
    with out_path.open("w", encoding="utf-8", newline="\n") as out:
        for name, n, edges, side in iter_jobs(args):
            ctx = pure_l5_context(name, n, edges, side, assume_no_hom=bool(args.input_jsonl))
            if ctx is None:
                continue
            matched_records += 1
            if matched_records <= args.skip_records:
                skipped_records += 1
                continue
            rec = analyze_context(ctx)
            out.write(json.dumps(rec, sort_keys=True) + "\n")
            acc["records"] += 1
            acc[f"verdict:{rec['verdict']}"] += 1
            acc[f"N:{n}"] += 1
            if rec["minimal_positive_count"]:
                acc["fails"] += 1
                first_fail = first_fail or rec
            if args.progress_every and acc["records"] % args.progress_every == 0:
                print(json.dumps({
                    "records": acc["records"],
                    "matched_records": matched_records,
                    "skipped_records": skipped_records,
                    "fails": acc["fails"],
                }, sort_keys=True), flush=True)
            if args.limit_cuts is not None and acc["records"] >= args.limit_cuts:
                break
    summary = {
        "schema": "bank0_closure_trace_summary_v1",
        "output": str(out_path),
        "counts": dict(sorted(acc.items())),
        "matched_records": matched_records,
        "skipped_records": skipped_records,
        "skip_records_arg": args.skip_records,
        "limit_cuts_arg": args.limit_cuts,
        "input_jsonl": args.input_jsonl or None,
        "first_fail": first_fail,
        "verdict": "FAIL" if acc["fails"] else "PASS",
    }
    Path(args.summary).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if acc["fails"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()




