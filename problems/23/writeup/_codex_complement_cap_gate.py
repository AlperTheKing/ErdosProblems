from collections import Counter
from fractions import Fraction as F
import subprocess

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_bundle_moat_gate import best_moat_completion
from _codex_k2t_lenbundle_switch_gate import h_blowup, length_bundle_half_switches
from _codex_k2t_switch_probe import adj_from_edges, flip_side, gamma_of
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _csmspec import build_K2


def residuals(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None: return None
    M, _ell, T, _mu, cyc = st
    if not M: return None
    K2 = build_K2(n, M, cyc)
    return [F(n)*T[v] - sum(K2[v][w]*T[w] for w in range(n)) for v in range(n)]

def best_mask(n, adj, side, st, v, max_add=1):
    gamma0=gamma_of(n,adj,side)
    M,ell,T,mu,cyc=st
    best=None
    for seed in length_bundle_half_switches(ell,cyc,v):
        if not ((seed>>v)&1): continue
        cand=best_moat_completion(n,adj,side,st,seed,max_add)
        if cand is None: continue
        added,negpsi,mask,psi=cand
        gamma2=gamma_of(n,adj,flip_side(side,mask))
        if gamma2 is None or gamma2>=gamma0: continue
        key=(added,-psi,mask)
        if best is None or key<best[0]: best=(key,seed,mask,psi)
    return best

def cap_stats(det, ell):
    C=tuple(sorted(det['cross_m']))
    E=tuple(sorted(det['bdy_b']))
    wit_of_f={f:set() for f in C}
    witnesses={e:set(fs) for e,fs in det['witnesses'].items()}
    for e,fs in witnesses.items():
        for f in fs: wit_of_f.setdefault(f,set()).add(e)
    lamb={e:min(ell[f] for f in witnesses[e]) for e in E}
    thresholds=sorted({ell[f]+1 for f in C} | {lamb[e]+1 for e in E})
    best=None; hist=Counter(); arg=None; checked=0
    for t in thresholds:
        Et=tuple(sorted(e for e in E if lamb[e]<t))
        Ft=tuple(sorted(f for f in C if ell[f]<t))
        if not Et: continue
        if len(Et)>18: continue
        for bits in range(1,1<<len(Et)):
            Z={Et[i] for i in range(len(Et)) if (bits>>i)&1}
            A={f for f in Ft if wit_of_f[f].isdisjoint(Z)}
            slack=len(Et)-len(Z)-len(A)
            checked+=1; hist[slack]+=1
            if best is None or slack<best:
                best=slack; arg=(t,len(Et),len(Ft),len(Z),len(A),tuple(sorted(Z)),tuple(sorted(A)))
    return best,hist,arg,checked

def scan(name,n,adj,side,records):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    R=residuals(n,adj,side)
    if R is None: return
    M,ell,T,mu,cyc=st
    for v,rv in enumerate(R):
        if rv>=0: continue
        got=best_mask(n,adj,side,st,v,1)
        if got is None: continue
        _key,seed,mask,psi=got
        det=terminal_shadow_details(n,adj,side,st,mask)
        if det is None: continue
        best,hist,arg,checked=cap_stats(det,ell)
        records.append((best,hist,arg,checked,name,n,''.join(map(str,side)),v,tuple(i for i in range(n) if (mask>>i)&1),psi))

def main():
    records=[]
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,edges=dec(g6); adj=adj_from_edges(n,edges)
            for side in maxcut_all(n,adj): scan(g6,n,adj,side,records)
    n,edges,_=h_blowup(2); adj=adj_from_edges(n,edges)
    for side in maxcut_all(n,adj): scan('H2-allmax',n,adj,side,records)
    for t in [2,3,4]:
        n,edges,side=h_blowup(t); scan('H%d-inh'%t,n,adj_from_edges(n,edges),side,records)
    global_hist=Counter(); worst=None; skipped=0; checked=0
    for rec in records:
        best,hist,arg,cnt,*meta=rec
        checked+=cnt; global_hist.update(hist)
        if best is None: skipped+=1
        elif worst is None or best<worst[0]: worst=(best,arg,meta)
    print('records',len(records),'checked',checked,'skipped',skipped)
    print('slack_hist',sorted(global_hist.items())[:20], '...', sorted(global_hist.items())[-10:])
    print('worst',worst)
    bad=[r for r in records if r[0] is not None and r[0]<0]
    print('fail',len(bad))
    zero=[r for r in records if r[0]==0]
    print('zero_slack_records',len(zero))
    if zero:
        for z in zero[:10]: print('zero',z[2],z[4:])

if __name__=='__main__': main()
