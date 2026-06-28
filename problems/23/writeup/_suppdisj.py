"""SUPPORT-DISJOINTNESS lemma (claimed PROVABLE from bipartite layer geometry):
  if mu(uv)=0 (B-edge) then for EVERY bad edge f, NOT both p_f(u)>0 and p_f(v)>0.
Proof idea: p_f(x)>0 => x on f-interval (d_a(x)+d_b(x)=L). If u,v both on interval and uv in B,
then concatenating shortest a->u, edge uv, shortest v->b gives a shortest a-b path using uv => mu(uv)>0.
EXACT test: ALL connected cuts N<=9 (odd-cycle bad edges) + loads-cut census N<=11 + Mycielskians + blow-ups."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads, Bconn, geos
from _superphi import blow as sblow

def struct(n,adj,side):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if not M: return None
    T=[F(0)]*n; ell={}; cyc={}; pf={}
    for f in M:
        Ps=geos(adj,side,f[0],f[1])
        if not Ps: return None
        cyc[f]=Ps; ell[f]=len(Ps[0])
        if ell[f]<3: return None
        k=len(Ps); sh=F(ell[f],k)
        for x in range(n):
            c=sum(1 for P in Ps if x in P)
            if c: pf[(f,x)]=F(c,k)
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
    return M,ell,T,mu,cyc,pf

def viol(n,adj,side):
    st=struct(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc,pf=st
    bad=[]
    for (a,b),val in mu.items():
        if val!=0: continue
        for f in M:
            if pf.get((f,a),0)>0 and pf.get((f,b),0)>0:
                bad.append((a,b,f,str(pf[(f,a)]),str(pf[(f,b)])))
    return bad

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
    print("=== SUPPORT-DISJOINTNESS on zero-mu edges ===")
    for nn in [7,8,9]:
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tv=0; wit=None
        for g6 in outg:
            n,E=dec(g6); adj=[set() for _ in range(n)]
            for x,y in E: adj[x].add(y); adj[y].add(x)
            for mask in range(1<<(n-1)):
                side=[(mask>>i)&1 for i in range(n)]
                if not Bconn(n,adj,side): continue
                b=viol(n,adj,side)
                if b: tv+=len(b); wit=wit or (g6,b[0])
        print(f"  ALL conn cuts N={nn}: support-disjointness violations={tv} {wit or ''}",flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tv=0; wit=None
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            b=viol(info['n'],info['adj'],info['side'])
            if b: tv+=len(b); wit=wit or (g6,b[0])
        print(f"  loads-cut census N={nn}: viol={tv} {wit or ''}",flush=True)
    C5=(5,[(i,(i+1)%5) for i in range(5)]); C7=(7,[(i,(i+1)%7) for i in range(7)])
    n1,E1=mycielski(*C5); n2,E2=mycielski(n1,E1); m1,F1=mycielski(*C7)
    extra=[("Grotzsch11",(n1,E1)),("MycGrotzsch23",(n2,E2)),("MycC7_15",(m1,F1))]
    for g6,t in [("I?BD@g]Qo",2),("I?ABCc]}?",2),("G?bF`w",3),("J???E?pNu\\?",2)]:
        nn,EE=sblow(g6,t)
        if nn<=26: extra.append((f"{g6}[{t}]",(nn,EE)))
    for name,(nn,EE) in extra:
        info=loads(nn,EE)
        if info is None: continue
        b=viol(info['n'],info['adj'],info['side'])
        print(f"  {name} N={nn}: viol={len(b)} {b[:1]}",flush=True)
