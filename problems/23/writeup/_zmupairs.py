"""For zero-mu B-edges uv, collect (T(u),T(v)) pairs across ALL connected cuts (N<=8) to see the
geodesic relation. Question: is the real fact 'zero-mu edge uv => min(T(u),T(v)) determines / one of them is
forced when the other is large'? Print distribution. Also test: zero-mu uv with BOTH T(u),T(v)>0 -- when?"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn, geos

def struct(n,adj,side):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if not M: return None
    T=[F(0)]*n; ell={}; cyc={}
    for f in M:
        Ps=geos(adj,side,f[0],f[1])
        if not Ps: return None
        cyc[f]=Ps; ell[f]=len(Ps[0]);
        if ell[f]<3: return None
        sh=F(ell[f],len(Ps))
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

if __name__=="__main__":
    bothpos=0; total=0
    examples=[]
    for nn in [7,8]:
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6)
            adj=[set() for _ in range(n)]
            for x,y in E: adj[x].add(y); adj[y].add(x)
            for mask in range(1<<(n-1)):
                side=[(mask>>i)&1 for i in range(n)]
                if not Bconn(n,adj,side): continue
                st=struct(n,adj,side)
                if st is None: continue
                M,ell,T,mu,cyc=st; N=n
                for (a,b),val in mu.items():
                    if val!=0: continue
                    total+=1
                    if T[a]>0 and T[b]>0:
                        bothpos+=1
                        if len(examples)<12: examples.append((g6,(a,b),str(T[a]),str(T[b]),N))
    print(f"zero-mu B-edges total={total}, with BOTH endpoints T>0 = {bothpos}")
    print("examples of zero-mu edge with both T>0 (T(u),T(v),N):")
    for e in examples: print("  ",e)
