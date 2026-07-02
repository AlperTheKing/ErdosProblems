"""Two protected UNIT-FLAT5 cell amalgamation stress.

The disjoint glued-cell stress shows independent protected cells are harmless.
The path-reuse stress shows a second UNIT core inside one base cell is killed
by negative maxcut slack.  This script sits between them: take two copies of
the known N=10 protected cell and identify a side-compatible blue path of
copy 2 with a blue path of copy 1.

For each amalgamated intended cut, the script checks triangle-freeness, the
protected-cell peel classifier, and the minimum switch slack sigma.  It is a
finite guardrail for:

  overlapping protected cells sharing a blue path are not connected maximum
  cuts unless the cells remain validly separated by the peel classifier.
"""

from __future__ import annotations

import argparse
import contextlib
import io
from collections import Counter, defaultdict, deque

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_rowcap_non5_half_gate import adj_of
    from _codex_slack_cage_multi_protected_cell_stress import bad_count
    from _codex_slack_cage_overlap_attempt_search import cut_edges_by_side, min_sigma, triangle_free
    from _codex_slack_cage_unit_atom_boundary_dump import build_base_case, norm_edge
    from _codex_slack_cage_unit_peel_gate import check_side
    from _h import Bconn, maxcut_all


def blue_paths_exact_len(n, B, edge_len):
    adj = defaultdict(list)
    for u, v in B:
        adj[u].append(v)
        adj[v].append(u)
    out = set()

    def rec(path):
        if len(path) == edge_len + 1:
            out.add(tuple(path))
            return
        for v in adj[path[-1]]:
            if v in path:
                continue
            rec(path + [v])

    for s in range(n):
        rec([s])
    return sorted(out)


def canonical_path_pair(p, q):
    a = (tuple(p), tuple(q))
    b = (tuple(reversed(p)), tuple(reversed(q)))
    return min(a, b)


def build_amalgam(base, p1, p2):
    """Identify copy-2 path p2 with copy-1 path p1 coordinatewise."""

    n0 = base["n"]
    edges0 = [norm_edge(u, v) for u, v in base["edges"]]
    side0 = [int(c) for c in base["side"]]

    # Map original copy-1 vertices to themselves.  Copy-2 vertices are either
    # identified with p1 coordinates or become fresh vertices.
    image = {}
    for v in range(n0):
        image[("a", v)] = v
    for v2, v1 in zip(p2, p1):
        image[("b", v2)] = v1

    next_id = n0
    for v in range(n0):
        key = ("b", v)
        if key not in image:
            image[key] = next_id
            next_id += 1

    n = next_id
    side = [None] * n
    for v in range(n0):
        side[image[("a", v)]] = side0[v]
    for v in range(n0):
        img = image[("b", v)]
        if side[img] is None:
            side[img] = side0[v]
        elif side[img] != side0[v]:
            return None

    edges = set()
    for u, v in edges0:
        edges.add(norm_edge(image[("a", u)], image[("a", v)]))
        edges.add(norm_edge(image[("b", u)], image[("b", v)]))

    # Reject loops created by identifying adjacent vertices.
    if any(u == v for u, v in edges):
        return None
    return n, sorted(edges), side, image


def cheap_conn_maxcut_summary(n, edges, side, exact_maxcut=False):
    rec = {"bad_intended": bad_count(edges, side)}
    if not exact_maxcut:
        return rec
    adj = adj_of(n, edges)
    all_max = maxcut_all(n, adj)
    conn = [s for s in all_max if Bconn(n, adj, s)]
    intended_key = "".join(str(int(c)) for c in side)
    conn_keys = {"".join(str(int(c)) for c in s) for s in conn}
    rec.update(
        {
            "max_bad": bad_count(edges, all_max[0]) if all_max else None,
            "conn_maxcuts": len(conn),
            "intended_conn_max": intended_key in conn_keys,
        }
    )
    return rec


def analyze(base, p1, p2, exact_maxcut=False, lazy_sigma=False, no_sigma=False):
    built = build_amalgam(base, p1, p2)
    if built is None:
        return {"invalid_side": True, "p1": p1, "p2": p2}
    n, edges, side, _image = built
    rec = {
        "p1": tuple(p1),
        "p2": tuple(p2),
        "n": n,
        "invalid_side": False,
        "triangle_free": triangle_free(n, edges),
    }
    if not rec["triangle_free"]:
        return rec
    rec.update(cheap_conn_maxcut_summary(n, edges, side, exact_maxcut=exact_maxcut))
    acc = check_side("two-cell-amalgam", n, edges, side)
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
    needs_sigma = (
        not no_sigma
        and (
        not lazy_sigma
        or acc["bad_cell"]
        or acc["overlap_fail"]
        or acc["missing_cell"]
        or dict(acc["atom_count_hist"]) != {0: 1}
        )
    )
    if needs_sigma:
        rec["min_sigma"], rec["min_sigma_sets"] = min_sigma(n, edges, side)
    else:
        rec["min_sigma"], rec["min_sigma_sets"] = None, []
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-len", type=int, default=2, help="minimum blue path edge length")
    ap.add_argument("--max-len", type=int, default=4, help="maximum blue path edge length")
    ap.add_argument("--exact-maxcut", action="store_true", help="also enumerate maxcuts for interesting cases")
    ap.add_argument("--lazy-sigma", action="store_true", help="only compute min sigma for classifier-interesting amalgams")
    ap.add_argument("--no-sigma", action="store_true", help="skip all subset sigma searches; classifier-only survey")
    ap.add_argument("--limit-print", type=int, default=10)
    args = ap.parse_args()

    base = build_base_case()
    B, _M = cut_edges_by_side(base["edges"], base["side"])
    stats = Counter()
    interesting = []

    for edge_len in range(args.min_len, args.max_len + 1):
        paths = blue_paths_exact_len(base["n"], B, edge_len)
        seen = set()
        local = Counter()
        for p1 in paths:
            for p2 in paths:
                # Side-compatible coordinatewise, including reversed p2.
                for q2 in (p2, tuple(reversed(p2))):
                    if any(base["side"][a] != base["side"][b] for a, b in zip(p1, q2)):
                        continue
                    key = canonical_path_pair(p1, q2)
                    if key in seen:
                        continue
                    seen.add(key)
                    rec = analyze(base, p1, q2, exact_maxcut=False, lazy_sigma=args.lazy_sigma, no_sigma=args.no_sigma)
                    stats["attempts"] += 1
                    local["attempts"] += 1
                    if rec.get("invalid_side"):
                        stats["invalid_side"] += 1
                        local["invalid_side"] += 1
                        continue
                    if not rec.get("triangle_free"):
                        stats["non_triangle_free"] += 1
                        local["non_triangle_free"] += 1
                        continue
                    stats["triangle_free"] += 1
                    local["triangle_free"] += 1
                    if rec.get("min_sigma") is not None and rec["min_sigma"] < 0:
                        stats["negative_sigma"] += 1
                        local["negative_sigma"] += 1
                    if rec.get("bad_cell"):
                        stats["bad_cell"] += 1
                        local["bad_cell"] += 1
                    if rec.get("overlap_fail"):
                        stats["overlap_fail"] += 1
                        local["overlap_fail"] += 1
                    # Interesting means the classifier sees overlapping cells,
                    # or the intended cut is not already killed by negative sigma.
                    if rec.get("overlap_fail") or (
                        rec.get("min_sigma") is not None and rec.get("min_sigma", -1) >= 0
                    ):
                        if args.exact_maxcut and rec.get("triangle_free"):
                            rec = analyze(
                                base,
                                p1,
                                q2,
                                exact_maxcut=True,
                                lazy_sigma=args.lazy_sigma,
                                no_sigma=args.no_sigma,
                            )
                        interesting.append(rec)
        print(f"len={edge_len} paths={len(paths)} local={dict(sorted(local.items()))}", flush=True)

    print("=== two protected-cell path amalgamation stress ===")
    print("stats:", dict(sorted(stats.items())))
    print("interesting_count:", len(interesting))
    for rec in interesting[: args.limit_print]:
        short = {
            k: rec.get(k)
            for k in (
                "p1",
                "p2",
                "n",
                "bad_intended",
                "max_bad",
                "conn_maxcuts",
                "intended_conn_max",
                "min_sigma",
                "min_sigma_sets",
                "atom_count_hist",
                "cell_comp_hist",
                "missing_cell",
                "bad_cell",
                "overlap_fail",
            )
            if k in rec
        }
        print("interesting:", short)

    fail = [
        rec
        for rec in interesting
        if rec.get("triangle_free")
        and (rec.get("min_sigma") if rec.get("min_sigma") is not None else -1) >= 0
        and rec.get("overlap_fail")
        and not rec.get("bad_cell")
        and not rec.get("missing_cell")
    ]
    print("VERDICT:", "PASS_TWO_CELL_AMALGAM_STRESS" if not fail else "FAIL_TWO_CELL_AMALGAM_STRESS")


if __name__ == "__main__":
    main()
