"""Enumerate protected-cell overlap attempts for UNIT-FLAT5 atoms.

The N<=11 census shows one protected UNIT cell per cut.  The glued stress
shows disjoint cells are harmless.  This script attacks the missing overlap
case locally: start from the known N=10 protected cell and try to create a
second UNIT-FLAT5 atom by reusing a 3-edge blue path already inside that cell.

For each blue path R=(x1,x2,x3,t), a UNIT atom consists of two leaves on the
same cut side as t, each blue-adjacent to x1 and bad-adjacent to t.  We test
two overlap patterns:

  one_existing_one_new: one leaf is an existing base vertex; one is new.
  two_new: both leaves are new but the shared path lies in the base cell.

The intended cut is then checked exactly for triangle-freeness, connected-B
maximum status, min sigma, and the protected-cell peel gate.  This is a finite
guardrail for the structural claim that overlapping protected cells are killed
by maxcut balance or lose the protected-cell conditions.
"""

from __future__ import annotations

import argparse
import contextlib
import io
from collections import Counter, defaultdict, deque

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_rowcap_non5_half_gate import adj_of
    from _codex_slack_cage_multi_protected_cell_stress import bad_count
    from _codex_slack_cage_unit_atom_boundary_dump import build_base_case, norm_edge
    from _codex_slack_cage_unit_peel_gate import check_side
    from _h import Bconn, maxcut_all


def edge_set(edges):
    return {norm_edge(u, v) for u, v in edges}


def cut_edges_by_side(edges, side):
    B = set()
    M = set()
    for u, v in edges:
        (M if side[u] == side[v] else B).add(norm_edge(u, v))
    return B, M


def triangle_free(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for u in range(n):
        for v in adj[u]:
            if v <= u:
                continue
            if adj[u] & adj[v]:
                return False
    return True


def blue_paths_len3(n, B):
    adj = defaultdict(list)
    for u, v in B:
        adj[u].append(v)
        adj[v].append(u)
    paths = set()
    for x1 in range(n):
        for x2 in adj[x1]:
            for x3 in adj[x2]:
                if x3 in (x1, x2):
                    continue
                for t in adj[x3]:
                    if len({x1, x2, x3, t}) < 4:
                        continue
                    # Canonicalize only by exact orientation; the UNIT
                    # terminal side depends on t, so keep both directions.
                    paths.add((x1, x2, x3, t))
    return sorted(paths)


def maxcut_summary(n, edges, side):
    adj = adj_of(n, edges)
    all_max = maxcut_all(n, adj)
    conn = [s for s in all_max if Bconn(n, adj, s)]
    intended_key = "".join(str(int(c)) for c in side)
    conn_keys = {"".join(str(int(c)) for c in s) for s in conn}
    return {
        "maxcuts": len(all_max),
        "conn_maxcuts": len(conn),
        "bad_intended": bad_count(edges, side),
        "max_bad": bad_count(edges, all_max[0]) if all_max else None,
        "intended_conn_max": intended_key in conn_keys,
    }


def min_sigma(n, edges, side):
    B, M = cut_edges_by_side(edges, side)
    best = None
    examples = []
    for mask in range(1, (1 << n) - 1):
        dB = 0
        dM = 0
        for u, v in B:
            if ((mask >> u) & 1) ^ ((mask >> v) & 1):
                dB += 1
        for u, v in M:
            if ((mask >> u) & 1) ^ ((mask >> v) & 1):
                dM += 1
        sig = dB - dM
        if best is None or sig < best:
            best = sig
            examples = [tuple(i for i in range(n) if (mask >> i) & 1)]
        elif sig == best and len(examples) < 4:
            examples.append(tuple(i for i in range(n) if (mask >> i) & 1))
    return best, examples


def add_one_existing_one_new(base, path, leaf):
    n0 = base["n"]
    x1, _x2, _x3, t = path
    new = n0
    side = list(base["side"]) + [base["side"][t]]
    edges = edge_set(base["edges"])
    edges.add(norm_edge(leaf, t))
    edges.add(norm_edge(new, x1))
    edges.add(norm_edge(new, t))
    return n0 + 1, sorted(edges), side


def add_two_new(base, path):
    n0 = base["n"]
    x1, _x2, _x3, t = path
    a = n0
    b = n0 + 1
    side = list(base["side"]) + [base["side"][t], base["side"][t]]
    edges = edge_set(base["edges"])
    edges.add(norm_edge(a, x1))
    edges.add(norm_edge(a, t))
    edges.add(norm_edge(b, x1))
    edges.add(norm_edge(b, t))
    return n0 + 2, sorted(edges), side


def summarize_attempt(kind, base, path, leaf=None):
    if kind == "one_existing_one_new":
        n, edges, side = add_one_existing_one_new(base, path, leaf)
    elif kind == "two_new":
        n, edges, side = add_two_new(base, path)
    else:
        raise ValueError(kind)

    tri = triangle_free(n, edges)
    rec = {
        "kind": kind,
        "path": path,
        "leaf": leaf,
        "n": n,
        "triangle_free": tri,
    }
    if not tri:
        return rec
    rec.update(maxcut_summary(n, edges, side))
    rec["min_sigma"], rec["min_sigma_sets"] = min_sigma(n, edges, side)
    acc = check_side(f"overlap-{kind}", n, edges, side)
    rec.update(
        {
            "atom_count_hist": dict(sorted(acc["atom_count_hist"].items())),
            "cell_comp_hist": dict(sorted(acc["cell_comp_hist"].items(), key=lambda kv: str(kv[0]))),
            "missing_cell": acc["missing_cell"],
            "bad_cell": acc["bad_cell"],
            "overlap_fail": acc["overlap_fail"],
            "first_bad_cell": acc["first_bad_cell"],
            "first_overlap_fail": acc["first_overlap_fail"],
        }
    )
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit-print", type=int, default=8)
    args = ap.parse_args()

    base = build_base_case()
    B, _M = cut_edges_by_side(base["edges"], base["side"])
    paths = blue_paths_len3(base["n"], B)
    attempts = []

    edges = edge_set(base["edges"])
    for path in paths:
        x1, _x2, _x3, t = path
        for leaf in range(base["n"]):
            if leaf in path:
                continue
            if base["side"][leaf] != base["side"][t]:
                continue
            if norm_edge(leaf, x1) not in B:
                continue
            if norm_edge(leaf, t) in edges:
                continue
            attempts.append(summarize_attempt("one_existing_one_new", base, path, leaf))
        attempts.append(summarize_attempt("two_new", base, path))

    stats = Counter()
    badish = []
    for rec in attempts:
        stats["attempts"] += 1
        stats[f"kind_{rec['kind']}"] += 1
        if not rec["triangle_free"]:
            stats["non_triangle_free"] += 1
            continue
        stats["triangle_free"] += 1
        if rec["intended_conn_max"]:
            stats["intended_conn_max"] += 1
        if rec["min_sigma"] is not None and rec["min_sigma"] < 0:
            stats["negative_sigma"] += 1
        if rec.get("bad_cell"):
            stats["bad_cell"] += 1
        if rec.get("overlap_fail"):
            stats["overlap_fail"] += 1
        if rec["intended_conn_max"] or rec.get("overlap_fail"):
            badish.append(rec)

    print("=== protected-cell overlap attempt search ===")
    print("base_paths_len3:", len(paths))
    print("stats:", dict(sorted(stats.items())))
    print("interesting_count:", len(badish))
    for rec in badish[: args.limit_print]:
        short = {
            k: rec[k]
            for k in (
                "kind",
                "path",
                "leaf",
                "n",
                "bad_intended",
                "max_bad",
                "conn_maxcuts",
                "intended_conn_max",
                "min_sigma",
                "atom_count_hist",
                "cell_comp_hist",
                "missing_cell",
                "bad_cell",
                "overlap_fail",
            )
            if k in rec
        }
        print("interesting:", short)
        if rec.get("first_bad_cell"):
            print("  first_bad_cell:", rec["first_bad_cell"])
        if rec.get("first_overlap_fail"):
            print("  first_overlap_fail:", rec["first_overlap_fail"])

    # The intended local structural claim survives this search iff no
    # triangle-free overlap attempt is a connected maximum cut with a protected
    # overlap component not already caught by bad_cell/negative sigma.
    fail = [
        rec
        for rec in attempts
        if rec["triangle_free"]
        and rec.get("intended_conn_max")
        and not rec.get("bad_cell")
        and not rec.get("missing_cell")
        and rec.get("overlap_fail")
    ]
    print("VERDICT:", "PASS_OVERLAP_ATTEMPT_SEARCH" if not fail else "FAIL_OVERLAP_ATTEMPT_SEARCH")


if __name__ == "__main__":
    main()
