"""Dump the boundary-driven extracted core W on H?AFBo] (the 12 Tail<0 witnesses), to give Codex a
   concrete example of the BOUNDARY-DRIVEN phase (complement to its retained-driven N26 W=(1,2,3,4)).
   For each witness: P, the neutral dGamma<0 parity-interval W (vertex set), which path-indices in W,
   off-path vertices in W, and the added/removed/retained bad-edge length changes.
"""
from _crux_extract import all_max_cuts, parity_interval_switches
from _wf_deficit_farkas import deltas, flip, gamma_of
from _h import dec, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side

def ell_map(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None: return None
    M, ell = st[0], st[1]
    return {frozenset(e): ell[e] for e in M}

n, E = dec("H?AFBo]")
adj=[set() for _ in range(n)]
for x,y in E: adj[x].add(y); adj[y].add(x)
mc, cuts = all_max_cuts(n, adj, E)
structs=[]
for side in cuts:
    if not Bconn(n,adj,side): continue
    st=struct_for_side(n,adj,side)
    if st is None: continue
    structs.append((side,st,sum(st[2])))
gmin=min(g for (_,_,g) in structs)
dumped=set()
for (side,st,G) in structs:
    if G<=gmin: continue
    M,ell,T,cyc=st[0],st[1],st[2],st[4]
    if not M: continue
    em0=ell_map(n,adj,side)
    for f in M:
        if ell[f]%2==0: continue
        for P in cyc[f]:
            if len(P)!=ell[f]: continue
            _,_,Z,_,_=Zr_row(n,adj,side,M,ell,T,cyc,f,P)
            mintail=min(sum((2*r+1)*Z[r] for r in range(k,n)) for k in range(n))
            if mintail>=0: continue
            key=(tuple(side),tuple(P))
            if key in dumped: continue
            # find a neutral dGamma<0 W
            for W in parity_interval_switches(n,adj,side,P):
                if not W: continue
                dB,dM=deltas(n,adj,side,W)
                if dB!=dM: continue
                s2=flip(side,W)
                if not Bconn(n,adj,s2): continue
                g1=gamma_of(n,adj,s2)
                if g1 is None or g1-G>=0: continue
                em1=ell_map(n,adj,s2)
                k0=set(em0); k1=set(em1)
                added=k1-k0; removed=k0-k1; retained=k0&k1
                dumped.add(key)
                Win=sorted(W)
                pidx=[i for i in range(len(P)) if P[i] in W]
                offp=[v for v in Win if v not in set(P)]
                print("side=%s f=%s P=%s"%(''.join(map(str,side)),f,tuple(P)))
                print("  W=%s  path-indices-in-W=%s  off-path-in-W=%s  dGamma=%s"%(Win,pidx,offp,str(g1-G)))
                print("  added bad (old-cut->bad): %s"%[(tuple(sorted(e)),em1[e]) for e in added])
                print("  removed bad (bad->cut):   %s"%[(tuple(sorted(e)),em0[e]) for e in removed])
                print("  retained changed: %s"%[(tuple(sorted(h)),em0[h],em1[h]) for h in retained if em0[h]!=em1[h]])
                break
print("dumped %d distinct witnesses"%len(dumped))
