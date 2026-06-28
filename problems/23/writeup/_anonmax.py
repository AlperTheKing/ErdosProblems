"""Does A-alltie need MAX cut (or just connected cut)?  Test A-alltie on EVERY connected cut
where every bad edge still closes an odd cycle (ell>=... any), B connected, M nonempty.
If it fails on some non-max connected cut, then 'max cut' (not just gamma-min) is essential.
Census N=7..9. Exact."""
import subprocess, itertools
from fractions import Fraction as F
from _h import dec, GENG, Bconn, bdist_restr, geos

def struct(n,adj,side):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if not M: return None
    T=[F(0)]*n; ell={}; cyc={}
    for f in M:
        Ps=geos(adj,side,f[0],f[1])
        if not Ps: return None
        cyc[f]=Ps; ell[f]=len(Ps[0]); sh=F(ell[f],len(Ps))
        if ell[f]<3: return None  # bad edge must close odd cycle >=3 (here >=5 generally; allow >=3)
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
            if T[x]==N and T[y]!=0: v.append((x,y,float(T[x]),float(T[y])))
    return v

if __name__=="__main__":
    print("=== A-alltie on ALL connected cuts (not necessarily max), bad edges close odd cycle ===")
    for nn in range(7,10):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        viol=0; wit=None; ncuts=0
        for g6 in outg:
            n,E=dec(g6)
            adj=[set() for _ in range(n)]
            for x,y in E: adj[x].add(y); adj[y].add(x)
            for mask in range(1<<(n-1)):
                side=[(mask>>i)&1 for i in range(n)]
                if not Bconn(n,adj,side): continue
                ncuts+=1
                av=Aviol(n,adj,side)
                if av:
                    viol+=len(av)
                    if wit is None: wit=(g6,side,av[:2])
        print(f"  N={nn}: connected cuts tested={ncuts}  A-viol={viol}  {wit or ''}",flush=True)
