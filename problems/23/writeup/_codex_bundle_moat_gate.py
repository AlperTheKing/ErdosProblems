"""Gate the widened length-bundle + moat-completion selector.

The plain length-bundle selector is false on non-inherited max cuts of
H?AFBo][2].  The rescued witnesses are supersets of a length-bundle seed:

    seed A through v, plus a small moat C, S = A union C,

with S neutral, B-connected after flipping, terminal-shadow valid, and
Psi(S)>0.

This script searches bounded-size completions of length-bundle seeds.
It is a construction gate, not a proof.
"""

import argparse
import itertools
import random
import subprocess

from _bdef_construct import Cn, add_edges, is_triangle_free, mycielski, union_disjoint
from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _wf_deficit_farkas import odd_blowup
from _codex_k2t_lenbundle_switch_gate import h_blowup, length_bundle_half_switches
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta, flip_side, residuals
from _codex_k2t_terminal_shadow_gate import terminal_shadow_psi


def connected(adj):
    if not adj:
        return True
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen) == len(adj)


def mask_tuple(n, mask):
    return tuple(i for i in range(n) if (mask >> i) & 1)


def completion_candidates(n, seed, max_add):
    outside = [i for i in range(n) if not ((seed >> i) & 1)]
    for k in range(max_add + 1):
        for add in itertools.combinations(outside, k):
            mask = seed
            for x in add:
                mask |= 1 << x
            yield k, mask


def best_moat_completion(n, adj, side, st, seed, max_add):
    best = None
    for added, mask in completion_candidates(n, seed, max_add):
        if mask == 0 or mask == (1 << n) - 1:
            continue
        if boundary_delta(n, adj, side, mask) != 0:
            continue
        if not Bconn(n, adj, flip_side(side, mask)):
            continue
        psi = terminal_shadow_psi(n, adj, side, st, mask)
        if psi is None or psi <= 0:
            continue
        cand = (added, -psi, mask, psi)
        if best is None or cand < best:
            best = cand
    return best


def scan_cut(name, n, adj, side, acc, max_add):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    R = residuals(n, adj, side)
    if R is None:
        return

    cut_has_neg = False
    for v, r in enumerate(R):
        if r >= 0:
            continue
        cut_has_neg = True
        acc["negative"] += 1
        best = None
        best_seed = None
        for seed in length_bundle_half_switches(st[1], st[4], v):
            if not ((seed >> v) & 1):
                continue
            cand = best_moat_completion(n, adj, side, st, seed, max_add)
            if cand is None:
                continue
            if best is None or cand < best:
                best = cand
                best_seed = seed
        if best is None:
            acc["fail"] += 1
            if acc["first_fail"] is None:
                acc["first_fail"] = (name, n, "".join(map(str, side)), v, str(r))
            continue
        added, negpsi, mask, psi = best
        acc["covered"] += 1
        acc["added_hist"][added] = acc["added_hist"].get(added, 0) + 1
        acc["psi_hist"][psi] = acc["psi_hist"].get(psi, 0) + 1
        if len(acc["examples"]) < acc["example_limit"]:
            acc["examples"].append(
                (
                    name,
                    n,
                    "".join(map(str, side)),
                    v,
                    str(r),
                    "seed",
                    mask_tuple(n, best_seed),
                    "S",
                    mask_tuple(n, mask),
                    "added",
                    added,
                    "psi",
                    psi,
                )
            )
    if cut_has_neg:
        acc["bad_cuts"] += 1


def scan_graph_allmax(name, n, edges, acc, max_add):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc, max_add)


def brute_maxcut_sides(n, adj):
    best = -1
    sides = []
    # Fix vertex 0 to break complement symmetry.
    for bits in range(1 << (n - 1)):
        side = [0] + [(bits >> (i - 1)) & 1 for i in range(1, n)]
        value = sum(1 for u in range(n) for v in adj[u] if v > u and side[u] != side[v])
        if value > best:
            best = value
            sides = [side]
        elif value == best:
            sides.append(side)
    return best, sides


def new_acc(example_limit):
    return dict(
        bad_cuts=0,
        negative=0,
        covered=0,
        fail=0,
        first_fail=None,
        added_hist={},
        psi_hist={},
        examples=[],
        example_limit=example_limit,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--max-add", type=int, default=3)
    parser.add_argument("--h2-allmax", action="store_true")
    parser.add_argument("--h-blowups", type=int, default=3)
    parser.add_argument("--random", type=int, default=0)
    parser.add_argument("--examples", type=int, default=16)
    args = parser.parse_args()

    acc = new_acc(args.examples)
    for n in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split():
            nn, edges = dec(g6)
            scan_graph_allmax(g6, nn, edges, acc, args.max_add)
        print("census N=%d negative=%d covered=%d fail=%d" % (n, acc["negative"], acc["covered"], acc["fail"]), flush=True)

    if args.h2_allmax:
        n, edges, _side = h_blowup(2)
        adj = adj_from_edges(n, edges)
        best, sides = brute_maxcut_sides(n, adj)
        print("H?AFBo][2] maxcut=%d sides=%d" % (best, len(sides)), flush=True)
        for side in sides:
            scan_cut("H?AFBo][2]-allmax", n, adj, side, acc, args.max_add)
        print("after H2 allmax negative=%d covered=%d fail=%d" % (acc["negative"], acc["covered"], acc["fail"]), flush=True)

    for t in range(2, args.h_blowups + 1):
        n, edges, side = h_blowup(t)
        scan_cut("H?AFBo][%d]" % t, n, adj_from_edges(n, edges), side, acc, args.max_add)

    for sizes in [(2, 1, 2, 1, 2), (2, 1, 2, 1, 3), (3, 2, 3, 2, 3), (2, 2, 2, 2, 2)]:
        n, edges = odd_blowup(5, list(sizes))
        if n <= 13:
            scan_graph_allmax("blow%s" % (sizes,), n, edges, acc, args.max_add)

    isl = (5, Cn(5))
    g15 = mycielski(7, Cn(7))
    n, edges = union_disjoint(isl, g15)
    n, edges = add_edges((n, edges), [(0, 5)])
    scan_graph_allmax("isl", n, edges, acc, args.max_add)

    if args.random:
        rng = random.Random(13579)
        made = 0
        tries = 0
        while made < args.random and tries < 100000:
            tries += 1
            n = rng.choice([11, 12])
            p = rng.uniform(0.14, 0.32)
            edges = [(i, j) for i in range(n) for j in range(i + 1, n) if rng.random() < p]
            if not edges or not is_triangle_free(n, edges):
                continue
            adj = adj_from_edges(n, edges)
            if any(not adj[v] for v in range(n)) or not connected(adj):
                continue
            made += 1
            scan_graph_allmax("rand%d" % made, n, edges, acc, args.max_add)
        print("random graphs scanned:", made, flush=True)

    print("=" * 72)
    print("bad cuts:", acc["bad_cuts"])
    print("negative:", acc["negative"])
    print("covered:", acc["covered"])
    print("fail:", acc["fail"], acc["first_fail"] or "")
    print("added histogram:", dict(sorted(acc["added_hist"].items())))
    print("Psi histogram:", dict(sorted(acc["psi_hist"].items())))
    print("examples:")
    for ex in acc["examples"]:
        print("  ", ex)
    print("VERDICT:", "PASS" if acc["fail"] == 0 else "FAIL")


if __name__ == "__main__":
    main()
