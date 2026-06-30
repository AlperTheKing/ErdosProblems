"""Gate whether selected moat-completed seeds can be chosen at Lmax through v."""

import random
import subprocess
from collections import Counter

from _bdef_construct import Cn, add_edges, is_triangle_free, mycielski, union_disjoint
from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _wf_deficit_farkas import odd_blowup
from _codex_bundle_moat_gate import brute_maxcut_sides, best_moat_completion, connected
from _codex_k2t_lenbundle_switch_gate import h_blowup, length_bundle_half_switches
from _codex_k2t_switch_probe import adj_from_edges, residuals


def bundle_candidates_by_L(ell, cyc, v):
    out = []
    for L in sorted(set(ell.values())):
        for rev in (False, True):
            hits = []
            for f, paths0 in cyc.items():
                if ell[f] != L:
                    continue
                for path0 in paths0:
                    path = list(reversed(path0)) if rev else list(path0)
                    if v in path:
                        hits.append(path)
            if not hits:
                continue
            pref = suff = 0
            for path in hits:
                i = path.index(v)
                for x in path[:i+1]: pref |= 1 << x
                for x in path[i:]: suff |= 1 << x
            out.append((L, pref))
            out.append((L, suff))
    return out


def scan_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side): return
    st = struct_for_side(n, adj, side)
    if st is None: return
    M, ell, T, mu, cyc = st
    R = residuals(n, adj, side)
    if R is None: return
    for v, r in enumerate(R):
        if r >= 0: continue
        acc['neg'] += 1
        cands = bundle_candidates_by_L(ell, cyc, v)
        Lmax = max((L for L, seed in cands if (seed >> v) & 1), default=None)
        best = None
        best_seed = None
        best_L = None
        for L, seed in cands:
            if not ((seed >> v) & 1): continue
            cand = best_moat_completion(n, adj, side, st, seed, 1)
            if cand is None: continue
            if best is None or cand < best:
                best = cand; best_seed = seed; best_L = L
        if best is None:
            acc['noswitch'] += 1
            continue
        acc['selected'] += 1
        acc['hist'][(Lmax, best_L, best[0])] += 1
        if best_L != Lmax:
            acc['not_lmax'] += 1
            if acc.get('first') is None:
                acc['first'] = (name, ''.join(map(str, side)), v, str(r), Lmax, best_L, best[0])


def scan_graph(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, acc)


def main():
    acc = {'neg':0,'selected':0,'noswitch':0,'not_lmax':0,'hist':Counter(),'first':None}
    for nn in range(5, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6); scan_graph(g6, n, edges, acc)
        print('census', nn, acc['neg'], acc['selected'], acc['not_lmax'], flush=True)
    n, edges, _ = h_blowup(2)
    adj = adj_from_edges(n, edges)
    _best, sides = brute_maxcut_sides(n, adj)
    for side in sides: scan_cut('H2-allmax', n, adj, side, acc)
    for t in range(2, 5):
        n, edges, side = h_blowup(t); scan_cut('H%d'%t, n, adj_from_edges(n, edges), side, acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(2,2,2,2,2)]:
        n, edges = odd_blowup(5, list(sizes))
        if n <= 13: scan_graph('blow', n, edges, acc)
    isl=(5,Cn(5)); g15=mycielski(7,Cn(7)); n,edges=union_disjoint(isl,g15); n,edges=add_edges((n,edges),[(0,5)]); scan_graph('isl',n,edges,acc)
    rng=random.Random(13579); made=tries=0
    while made<100 and tries<100000:
        tries+=1; n=rng.choice([11,12]); p=rng.uniform(0.14,0.32)
        edges=[(i,j) for i in range(n) for j in range(i+1,n) if rng.random()<p]
        if not edges or not is_triangle_free(n,edges): continue
        adj=adj_from_edges(n,edges)
        if any(not adj[v] for v in range(n)) or not connected(adj): continue
        made+=1; scan_graph('rand',n,edges,acc)
    print('FINAL', {k:v for k,v in acc.items() if k!='hist'})
    print('hist')
    for k,c in acc['hist'].most_common(): print(c,k)
    print('VERDICT', 'PASS' if acc['not_lmax']==0 and acc['noswitch']==0 else 'FAIL')

if __name__=='__main__': main()
