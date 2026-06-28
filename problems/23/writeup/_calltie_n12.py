"""Full dissection of the N=12 leaf caveat: the ONLY census instance realizing the C-alltie hypothesis.
Examine each gamma-min cut where (O nonempty, T(z)=0, z B-adj v, T(v)=N) occurs, show Kcomp(v) and how it meets O."""
from fractions import Fraction as F
from _h import dec, maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side, kcomponents

g6='J?AADBWM_}?'; n0,E0=dec(g6); n=12; E=list(E0)+[(8,11)]
adj=[set() for _ in range(n)]
for x,y in E: adj[x].add(y); adj[y].add(x)
print('Edges:',sorted((min(a,b),max(a,b)) for a,b in E))
print('degrees:',[len(adj[v]) for v in range(n)])
cuts=maxcut_all(n,adj); cand=[]
for side in cuts:
    if not Bconn(n,adj,side): continue
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if not M: continue
    G=0; ok=True
    for (u,v) in M:
        d=bdist_restr(adj,side,u,v)
        if d<0: ok=False; break
        G+=(d+1)**2
    if ok: cand.append((tuple(side),G))
gm=min(G for _,G in cand)
print('num gamma-min connected cuts:',sum(1 for _,G in cand if G==gm),'Gamma_min=',gm)
for side,G in cand:
    if G!=gm: continue
    st=struct_for_side(n,adj,list(side))
    if st is None: continue
    M,ell,T,mu,cyc=st; N=n
    O=set(v for v in range(N) if T[v]>N)
    if not O: continue
    comp,find=kcomponents(n,cyc)
    cases=[(v,z) for v in range(N) if T[v]==N for z in adj[v] if side[z]!=side[v] and T[z]==0]
    if not cases: continue
    print()
    print('side=',side)
    print('  M(bad edges)=',M)
    print('  ell=',{f:ell[f] for f in M})
    print('  T=',[str(T[v]) for v in range(N)])
    print('  O=',sorted(O),'sat=',[v for v in range(N) if T[v]==N],'dead=',[v for v in range(N) if T[v]==0])
    Kcomps={}
    for v in range(N): Kcomps.setdefault(find(v),set()).add(v)
    print('  K-components:',[sorted(c) for c in Kcomps.values()])
    for v,z in cases:
        Cv=comp[find(v)]
        print(f'   case v={v}(sat,T=N) z={z}(dead,T=0): Kcomp(v)={sorted(Cv)} meetsO={bool(Cv&O)}')
