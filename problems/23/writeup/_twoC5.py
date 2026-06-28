from fractions import Fraction as F
from _h import maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side

def twoC5(cross):
    E=[(i,(i+1)%5) for i in range(5)] + [(5+i,5+(i+1)%5) for i in range(5)]
    E=E+cross
    return 10,E

def Acheck(n,adj,side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    c=0; v=0; wit=[]
    for e,val in mu.items():
        if val!=0: continue
        a0,b0=e
        for (a,b) in ((a0,b0),(b0,a0)):
            if T[a]==N:
                c+=1
                if T[b]!=0: v+=1; wit.append((a,b,str(T[a]),str(T[b])))
    return c,v,wit,[str(t) for t in T]

crosses=[
    [(0,5)],
    [(0,5),(1,6)],
    [(0,5),(2,7)],
    [(0,5),(1,7),(2,8)],
    [(0,5),(1,6),(2,7),(3,8),(4,9)],
    [(0,6),(1,7),(2,8),(3,9),(4,5)],
]
for cross in crosses:
    n,E=twoC5(cross)
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    tf=all(not(adj[a]&adj[b]) for a in range(n) for b in adj[a])
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
        if ok: cand.append((side,G))
    if not cand:
        print(f"cross={cross} tf={tf}: no connected max cut"); continue
    gm=min(G for _,G in cand)
    gmv=0; nmv=0; gmc=0; nmc=0; ex=None
    for side,G in cand:
        r=Acheck(n,adj,side)
        if r is None: continue
        c,v,wit,Ts=r
        if G==gm: gmc+=c; gmv+=v
        else: nmc+=c; nmv+=v
        if c>0 and ex is None: ex=("gmin" if G==gm else "NONMIN",G,Ts,wit)
    print(f"cross={cross} tf={tf} #cuts={len(cand)} gm={gm}: GMIN cases={gmc} viol={gmv} | NONMIN cases={nmc} viol={nmv}")
    if ex: print(f"     example: {ex}")
