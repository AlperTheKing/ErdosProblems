"""Refined: among zero-mu B-edges with BOTH T(u),T(v)>0, does T(u)+T(v) <= N hold? (cleaner than HALF)
Also record the distribution of (T(u),T(v)) to find the true extremal relation.
Test: loads-cut census N<=11 + Mycielskians + blow-ups + ALL connected cuts N<=9."""
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

def worst(n,adj,side):
    st=struct(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    w=F(-1); rec=None; viol=0; both=[]
    for (a,b),val in mu.items():
        if val!=0: continue
        if T[a]>0 and T[b]>0:
            s=T[a]+T[b]; both.append((str(T[a]),str(T[b])))
            if s>n: viol+=1
            if s>w: w=s; rec=(a,b,str(T[a]),str(T[b]))
    return w,rec,viol,both

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
    print("=== zero-mu both-pos: T(u)+T(v) <= N ? and (T(u),T(v)) distribution ===")
    allpairs=set()
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        gw=F(-1); grec=None; tviol=0
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            r=worst(info['n'],info['adj'],info['side'])
            if r is None: continue
            w,rec,viol,both=r; tviol+=viol
            for p in both: allpairs.add((p[0],p[1],nn))
            if w>gw: gw=w; grec=(g6,rec)
        print(f"  loads-cut N={nn}: both-pos-SUM-viol(>N)={tviol} worst T(u)+T(v)={float(gw)} ratio={float(gw)/nn:.4f} {grec}",flush=True)
    C5=(5,[(i,(i+1)%5) for i in range(5)]); C7=(7,[(i,(i+1)%7) for i in range(7)])
    n1,E1=mycielski(*C5); n2,E2=mycielski(n1,E1); m1,F1=mycielski(*C7)
    extra=[("MycGrotzsch23",(n2,E2)),("MycC7_15",(m1,F1))]
    for g6,t in [("I?BD@g]Qo",2),("I?ABCc]}?",2),("G?bF`w",3),("J???E?pNu\\?",2)]:
        nn,EE=sblow(g6,t)
        if nn<=26: extra.append((f"{g6}[{t}]",(nn,EE)))
    for name,(nn,EE) in extra:
        info=loads(nn,EE)
        if info is None: continue
        r=worst(info['n'],info['adj'],info['side'])
        if r is None: print(f"  {name}: none"); continue
        w,rec,viol,both=r
        print(f"  {name} N={nn}: both-pos-SUM-viol={viol} worst={float(w)} ratio={float(w)/nn:.4f} {rec}",flush=True)
    # ALL connected cuts N<=9 both-pos
    for nn in [8,9]:
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        gw=F(-1); grec=None; tviol=0
        for g6 in outg:
            n,E=dec(g6); adj=[set() for _ in range(n)]
            for x,y in E: adj[x].add(y); adj[y].add(x)
            for mask in range(1<<(n-1)):
                side=[(mask>>i)&1 for i in range(n)]
                if not Bconn(n,adj,side): continue
                r=worst(n,adj,side)
                if r is None: continue
                w,rec,viol,both=r; tviol+=viol
                if w>gw: gw=w; grec=(g6,rec)
        print(f"  ALL conn cuts N={nn}: both-pos-SUM-viol={tviol} worst={float(gw)} ratio={float(gw)/nn:.4f} {grec}",flush=True)
