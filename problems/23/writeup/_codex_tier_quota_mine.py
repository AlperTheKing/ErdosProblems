r"""Mine quota subsets for the two-stage TIER-SDR gate.

For the stage1 graph E -- F1 (all exits against longer crossing bad edges),
a first-stage F0 matching using exits U extends iff every Y subset E satisfies
|Y\U| <= |N_F1(Y)|, equivalently |Y cap U| >= |Y|-|N(Y)|.
This diagnostic records the positive-deficit subsets Y.
"""

import subprocess
from collections import Counter
from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _codex_bundle_moat_gate import best_moat_completion
from _codex_k2t_lenbundle_switch_gate import h_blowup, length_bundle_half_switches
from _codex_k2t_switch_probe import adj_from_edges, flip_side, gamma_of
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_length_tier_matching_gate import max_matching


def residuals(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, _ell, T, _mu, cyc = st
    if not M:
        return None
    K2 = build_K2(n, M, cyc)
    return [F(n) * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]


def best_seed_moat_mask(n, adj, side, st, v, max_add):
    gamma0 = gamma_of(n, adj, side)
    _M, ell, _T, _mu, cyc = st
    best = None
    for seed in length_bundle_half_switches(ell, cyc, v):
        if not ((seed >> v) & 1):
            continue
        cand = best_moat_completion(n, adj, side, st, seed, max_add)
        if cand is None:
            continue
        added, _negpsi, mask, psi = cand
        gamma2 = gamma_of(n, adj, flip_side(side, mask))
        if gamma2 is None or gamma2 >= gamma0:
            continue
        key = (added, -psi, mask)
        if best is None or key < best[0]:
            best = (key, seed, mask, psi)
    return None if best is None else best[1:]


def quota_profile(st, det):
    _M, ell, _T, _mu, _cyc = st
    F_edges = tuple(sorted(det['cross_m']))
    E_edges = tuple(sorted(det['bdy_b']))
    witnesses = {e: set(fs) for e, fs in det['witnesses'].items()}
    lamb = {e: min(ell[f] for f in witnesses[e]) for e in E_edges}
    min_len = min(ell[f] for f in F_edges)
    F0 = tuple(f for f in F_edges if ell[f] == min_len)
    F1 = tuple(f for f in F_edges if ell[f] > min_len)
    E0 = tuple(e for e in E_edges if lamb[e] == min(lamb.values()))
    adj0 = {f: {e for e in E0 if f in witnesses[e]} for f in F0}
    m0 = max_matching(F0, adj0)
    used = set(m0)
    # max_matching returns map right->left for left=F0, right=E0
    used = set(m0.keys())
    pos_defs=[]
    e_list=list(E_edges)
    for bits in range(1,1<<len(e_list)):
        Y={e_list[i] for i in range(len(e_list)) if (bits>>i)&1}
        N={f for f in F1 if any(f in witnesses[e] for e in Y)}
        d=len(Y)-len(N)
        if d>0:
            hit=len(Y & used)
            pos_defs.append((d,len(Y),len(N),hit,tuple(sorted(Y))))
    pos_defs.sort(reverse=True)
    return dict(F0=len(F0),F1=len(F1),E=len(E_edges),E0=len(E0),used=len(used),defs=tuple(pos_defs[:8]),num_defs=len(pos_defs))


def scan_cut(n, adj, side, acc, examples):
    if not Bconn(n, adj, side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    R=residuals(n,adj,side)
    if R is None: return
    for v,rv in enumerate(R):
        if rv>=0: continue
        got=best_seed_moat_mask(n,adj,side,st,v,1)
        if got is None: continue
        _seed,mask,_psi=got
        det=terminal_shadow_details(n,adj,side,st,mask)
        if det is None: continue
        q=quota_profile(st,det)
        key=(q['F0'],q['F1'],q['E'],q['E0'],q['num_defs'],tuple((d,sz,n) for d,sz,n,hit,Y in q['defs']))
        acc[key]+=1
        if key not in examples:
            examples[key]=q


def main():
    acc=Counter(); examples={}
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,edges=dec(g6); adj=adj_from_edges(n,edges)
            for side in maxcut_all(n,adj):
                scan_cut(n,adj,side,acc,examples)
    n,edges,_=h_blowup(2); adj=adj_from_edges(n,edges)
    for side in maxcut_all(n,adj): scan_cut(n,adj,side,acc,examples)
    print('profiles',len(acc),'total',sum(acc.values()))
    for key,count in acc.most_common():
        print('count',count,'key',key)
        print(' ex',examples[key])

if __name__=='__main__':
    main()
