"""Does A-alltie need gamma-minimality? Test A-alltie on EVERY connected-B max cut (not only gamma-min).
A max cut already maximizes |B|; among those with B connected, take ALL (incl. non-min-Gamma).
If A-alltie fails on a non-min-Gamma max cut, gamma-minimality is ESSENTIAL. Exact."""
import subprocess
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr, geos

def struct(n,adj,side):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if not M: return None
    T=[F(0)]*n; ell={}; cyc={}
    for f in M:
        Ps=geos(adj,side,f[0],f[1])
        if not Ps: return None
        cyc[f]=Ps; ell[f]=len(Ps[0]); sh=F(ell[f],len(Ps))
        T=[T[i]+(sh*sum(1 for P in Ps if i in P)) for i in range(n)]
    mu={}
    for u in range(n):
        for v in adj[u]:
            if side[u]!=side[v] and u<v: mu[(u,v)]=F(0)
    for f in M:
        Ps=cyc[f]; w=F(ell[f],len(Ps))
        for P in Ps:
            for i in range(len(P)-1):
                a,b=P[i],P[i+1]; e=(min(a,b),max(a,b))
                if e in mu: mu[e]+=w
    return M,ell,T,mu,cyc

def Aviol(n,adj,side):
    st=struct(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    v=[]
    for (a,b),val in mu.items():
        if val!=0: continue
        for (x,y) in [(a,b),(b,a)]:
            if T[x]==N and T[y]!=0: v.append((x,y,float(T[y])))
    return v

if __name__=="__main__":
    print("=== A-alltie on ALL connected-B max cuts (incl. NON-gamma-min) ===")
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nonmin_viol=0; min_viol=0; wit=None
        for g6 in outg:
            n,E=dec(g6)
            adj=[set() for _ in range(n)]
            for x,y in E: adj[x].add(y); adj[y].add(x)
            cuts=maxcut_all(n,adj)
            cand=[]
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
            if not cand: continue
            gm=min(G for _,G in cand)
            for side,G in cand:
                av=Aviol(n,adj,side)
                if av:
                    if G==gm: min_viol+=len(av)
                    else:
                        nonmin_viol+=len(av)
                        if wit is None: wit=(g6,G,gm,av[:2])
        print(f"  N={nn}: A-viol on gamma-MIN cuts={min_viol}  on NON-min max cuts={nonmin_viol}  {wit or ''}",flush=True)
