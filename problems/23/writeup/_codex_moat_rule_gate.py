"""Gate the one-vertex neutralizer rule for moat completions."""

import argparse
import random
import subprocess

from _bdef_construct import Cn, add_edges, is_triangle_free, mycielski, union_disjoint
from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _wf_deficit_farkas import odd_blowup
from _codex_bundle_moat_gate import brute_maxcut_sides, best_moat_completion, connected
from _codex_k2t_lenbundle_switch_gate import h_blowup, length_bundle_half_switches
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta, residuals


def relation(n, adj, side, seed, full):
    extra = [i for i in range(n) if ((full >> i) & 1) and not ((seed >> i) & 1)]
    if len(extra) != 1:
        return None
    z = extra[0]
    zmask = 1 << z
    d_seed = boundary_delta(n, adj, side, seed)
    d_z = boundary_delta(n, adj, side, zmask)
    d_full = boundary_delta(n, adj, side, full)
    ib = im = 0
    for u in range(n):
        if ((seed >> u) & 1) and z in adj[u]:
            if side[u] == side[z]:
                im += 1
            else:
                ib += 1
    ok = (d_full == 0 and d_z == 0 and im == 0 and d_seed == 2 * ib)
    return ok, d_seed, d_z, d_full, ib, im, z


def scan_cut(name, n, adj, side, acc, max_add):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    R = residuals(n, adj, side)
    if R is None:
        return
    for v, r in enumerate(R):
        if r >= 0:
            continue
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
            continue
        added, _negpsi, full, _psi = best
        acc['selected'] += 1
        if added == 0:
            acc['added0'] += 1
            if boundary_delta(n, adj, side, best_seed) != 0:
                acc['bad_added0'] += 1
                acc.setdefault('first_bad', (name, ''.join(map(str, side)), v, 'added0-delta', boundary_delta(n, adj, side, best_seed)))
            continue
        acc['added1'] += 1
        rel = relation(n, adj, side, best_seed, full)
        if rel is None or not rel[0]:
            acc['bad_rule'] += 1
            if 'first_bad' not in acc:
                acc['first_bad'] = (name, ''.join(map(str, side)), v, rel)
        else:
            key = rel[1:6]
            acc['rule_hist'][key] = acc['rule_hist'].get(key, 0) + 1


def scan_graph_allmax(name, n, edges, acc, max_add):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc, max_add)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--min-n', type=int, default=5)
    parser.add_argument('--max-n', type=int, default=11)
    parser.add_argument('--h2-allmax', action='store_true')
    parser.add_argument('--h-blowups', type=int, default=4)
    parser.add_argument('--random', type=int, default=200)
    args = parser.parse_args()
    acc = {'selected': 0, 'added0': 0, 'added1': 0, 'bad_added0': 0, 'bad_rule': 0, 'rule_hist': {}}

    for n in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, '-tc', str(n)], capture_output=True, text=True).stdout.split():
            nn, edges = dec(g6)
            scan_graph_allmax(g6, nn, edges, acc, 1)
        print('census', n, acc, flush=True)

    if args.h2_allmax:
        n, edges, _side = h_blowup(2)
        adj = adj_from_edges(n, edges)
        _best, sides = brute_maxcut_sides(n, adj)
        for side in sides:
            scan_cut('H2-allmax', n, adj, side, acc, 1)
        print('after H2', acc, flush=True)

    for t in range(2, args.h_blowups + 1):
        n, edges, side = h_blowup(t)
        scan_cut('H%d' % t, n, adj_from_edges(n, edges), side, acc, 1)

    for sizes in [(2, 1, 2, 1, 2), (2, 1, 2, 1, 3), (3, 2, 3, 2, 3), (2, 2, 2, 2, 2)]:
        n, edges = odd_blowup(5, list(sizes))
        if n <= 13:
            scan_graph_allmax('blow%s' % (sizes,), n, edges, acc, 1)

    isl = (5, Cn(5))
    g15 = mycielski(7, Cn(7))
    n, edges = union_disjoint(isl, g15)
    n, edges = add_edges((n, edges), [(0, 5)])
    scan_graph_allmax('isl', n, edges, acc, 1)

    rng = random.Random(13579)
    made = tries = 0
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
        scan_graph_allmax('rand%d' % made, n, edges, acc, 1)
    print('random made', made)
    print('FINAL', acc)
    print('VERDICT', 'PASS' if acc['bad_added0'] == 0 and acc['bad_rule'] == 0 else 'FAIL')


if __name__ == '__main__':
    main()
