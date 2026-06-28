"""(ZMU-HALF) candidate: zero-mu B-edge uv with BOTH T(u),T(v)>0 => max(T(u),T(v)) <= N/2.
[=> A-alltie: if T(u)=N>N/2 then can't have T(v)>0, so T(v)=0.]
Test EXACT: ALL connected cuts N<=9 (odd-cycle bad edges); loads-cut census N<=11; Mycielskians N=11,15,23;
blow-ups N<=26. Report worst max(T(u),T(v))/N AMONG zero-mu edges with both T>0, and any HALF-violation."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads, Bconn, geos
from _superphi import blow as sblow

def struct(n,adj,side):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if not M: return None
    T=[F(0)]*n; ell={}; cyc={}
    for f in M:
        Ps=geos(adj,side,f[0],f[1])
        if not Ps: return None
        cyc[f]=Ps; ell[f]=len(Ps[0])
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

def worst_half(n,adj,side):
    st=struct(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    w=F(-1); rec=None; viol=0
    for (a,b),val in mu.items():
        if val!=0: continue
        if T[a]>0 and T[b]>0:
            m=max(T[a],T[b])
            if 2*m>n: viol+=1;
            if m>w: w=m; rec=(a,b,str(T[a]),str(T[b]),(2*m>n))
    return w,rec,viol

def mycielski(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    N2=2*n+1; E2=list(E)
    for u in range(n):
        for v in adj[u]:
            if v>u: E2.append((u,n+v)); E2.append((v,n+u))
    for u in range(n): E2.append((n+u,2*n))
    return N2,E2

if __name__=="__main__":
    print("=== (ZMU-HALF) zero-mu edge both T>0 => max(T)<=N/2 ===")
    for nn in [7,8,9]:
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        gw=F(-1); grec=None; tviol=0
        for g6 in outg:
            n,E=dec(g6); adj=[set() for _ in range(n)]
            for x,y in E: adj[x].add(y); adj[y].add(x)
            for mask in range(1<<(n-1)):
                side=[(mask>>i)&1 for i in range(n)]
                if not Bconn(n,adj,side): continue
                r=worst_half(n,adj,side)
                if r is None: continue
                w,rec,viol=r; tviol+=viol
                if w>gw: gw=w; grec=(g6,rec)
        print(f"  ALL conn cuts N={nn}: HALF-viol={tviol} worst-max-both-pos={float(gw)} ratio={float(gw)/nn:.4f} {grec}",flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        gw=F(-1); grec=None; tviol=0
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            r=worst_half(info['n'],info['adj'],info['side'])
            if r is None: continue
            w,rec,viol=r; tviol+=viol
            if w>gw: gw=w; grec=(g6,rec)
        print(f"  loads-cut census N={nn}: HALF-viol={tviol} worst={float(gw)} ratio={float(gw)/nn:.4f} {grec}",flush=True)
    C5=(5,[(i,(i+1)%5) for i in range(5)]); C7=(7,[(i,(i+1)%7) for i in range(7)])
    n1,E1=mycielski(*C5); n2,E2=mycielski(n1,E1); m1,F1=mycielski(*C7)
    extra=[("Grotzsch11",(n1,E1)),("MycGrotzsch23",(n2,E2)),("MycC7_15",(m1,F1))]
    for g6,t in [("I?BD@g]Qo",2),("I?ABCc]}?",2),("G?bF`w",3),("J???E?pNu\\?",2)]:
        nn,EE=sblow(g6,t)
        if nn<=26: extra.append((f"{g6}[{t}]",(nn,EE)))
    for name,(nn,EE) in extra:
        info=loads(nn,EE)
        if info is None: continue
        r=worst_half(info['n'],info['adj'],info['side'])
        if r is None: print(f"  {name}: no both-pos zero-mu edge"); continue
        w,rec,viol=r
        print(f"  {name} N={nn}: HALF-viol={viol} worst={float(w)} ratio={float(w)/nn:.4f} {rec}",flush=True)
