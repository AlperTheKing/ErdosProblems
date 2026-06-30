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

def relation(det):
    C=tuple(sorted(det['cross_m']))
    E=tuple(sorted(det['bdy_b']))
    nf={f:set() for f in C}
    ne={e:set() for e in E}
    for e,fs in det['witnesses'].items():
        for f in fs:
            nf[f].add(e); ne[e].add(f)
    return C,E,nf,ne

def comparable_family(sets):
    vals=list(sets)
    for i in range(len(vals)):
        for j in range(i+1,len(vals)):
            if not (vals[i] <= vals[j] or vals[j] <= vals[i]):
                return False
    return True

def induced_2k2(C,E,nf):
    for i,a in enumerate(C):
        for b in C[i+1:]:
            Na=nf[a]; Nb=nf[b]
            for e1 in Na-Nb:
                for e2 in Nb-Na:
                    return (a,b,e1,e2)
    return None

def complement_rectangles(C,E,nf):
    # Connected components of missing relation in bipartite complement.
    miss_adj={('f',f):set() for f in C}
    miss_adj.update({('e',e):set() for e in E})
    for f in C:
        for e in E:
            if e not in nf[f]:
                miss_adj[('f',f)].add(('e',e)); miss_adj[('e',e)].add(('f',f))
    seen=set(); comps=[]
    for node in miss_adj:
        if node in seen or not miss_adj[node]: continue
        stack=[node]; seen.add(node); fs=set(); es=set()
        while stack:
            u=stack.pop()
            if u[0]=='f': fs.add(u[1])
            else: es.add(u[1])
            for w in miss_adj[u]:
                if w not in seen: seen.add(w); stack.append(w)
        complete=True
        for f in fs:
            for e in es:
                if e in nf[f]: complete=False
        comps.append((len(fs),len(es),complete))
    return tuple(sorted(comps))

def collect():
    records=[]
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,edges=dec(g6); adj=adj_from_edges(n,edges)
            for side in maxcut_all(n,adj):
                scan(g6,n,adj,side,records)
    n,edges,_=h_blowup(2); adj=adj_from_edges(n,edges)
    for side in maxcut_all(n,adj): scan('H2-allmax',n,adj,side,records)
    for t in [2,3,4]:
        n,edges,side=h_blowup(t); scan('H%d-inh'%t,n,adj_from_edges(n,edges),side,records)
    return records

def scan(name,n,adj,side,records):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    R=residuals(n,adj,side)
    if R is None: return
    for v,rv in enumerate(R):
        if rv>=0: continue
        got=best_mask(n,adj,side,st,v,1)
        if got is None: continue
        _key,seed,mask,psi=got
        det=terminal_shadow_details(n,adj,side,st,mask)
        if det is None: continue
        C,E,nf,ne=relation(det)
        rec={
            'name':name,'n':n,'side':''.join(map(str,side)),'v':v,'S':tuple(i for i in range(n) if (mask>>i)&1),'psi':psi,
            'C':C,'E':E,'nf':nf,'chainF':comparable_family([nf[f] for f in C]),'chainE':comparable_family([ne[e] for e in E]),
            'ind2k2':induced_2k2(C,E,nf),'missrect':complement_rectangles(C,E,nf),
        }
        records.append(rec)

def main():
    recs=collect()
    print('records',len(recs))
    print('chainF',Counter(r['chainF'] for r in recs))
    print('chainE',Counter(r['chainE'] for r in recs))
    print('has2K2',Counter(r['ind2k2'] is not None for r in recs))
    print('missing complement rectangle components',Counter(r['missrect'] for r in recs).most_common(30))
    bad=[r for r in recs if not r['chainF']]
    print('first non-chainF')
    if bad:
        r=bad[0]
        print(r['name'],r['n'],r['side'],r['v'],r['S'],'psi',r['psi'],'2k2',r['ind2k2'],'missrect',r['missrect'])
        C=sorted(r['C'], key=lambda f:(len(r['nf'][f]),f))
        E=sorted(r['E'])
        for f in C:
            print('F',f,'deg',len(r['nf'][f]),''.join('1' if e in r['nf'][f] else '0' for e in E))
        print('E order',E)
    # report any non-rectangular missing component
    nonrect=[r for r in recs if any(not c[2] for c in r['missrect'])]
    print('nonrect missing comps',len(nonrect))
    if nonrect:
        r=nonrect[0]; print('first nonrect',r['name'],r['n'],r['v'],r['S'],r['missrect'])

if __name__=='__main__': main()
