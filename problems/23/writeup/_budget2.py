r"""Pin the counting lemma for ZMU-SUM-both (no unicode prints).
For zero-mu both-pos edge uv: F_u,F_v disjoint (support-disjointness).
Test:
 (CU) T(u)+T(v) <= |U_u union U_v|     [=> <= N]
 (BU) T(u) <= |U_u| and T(v) <= |U_v|   (per-side budget, in both-pos regime)
 (BU2) T(u) <= |U_u| - |U_u cap U_v| + something? -- examine when overlap reduces loads.
Also a sharper per-side budget hypothesis:
 (BUD-S) T(u) <= |U_u \ {v}|? trivially v notin U_u. Try T(u) <= |U_u| and separately count overlap.
Loads-cut census N<=11 + ALL connected cuts N<=9. Exact."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads, Bconn, geos

def struct(n,adj,side):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if not M: return None
    T=[F(0)]*n; ell={}; cyc={}; pf={}; supp={}
    for f in M:
        Ps=geos(adj,side,f[0],f[1])
        if not Ps: return None
        cyc[f]=Ps; ell[f]=len(Ps[0])
        if ell[f]<3: return None
        k=len(Ps); s=set()
        for x in range(n):
            c=sum(1 for P in Ps if x in P)
            if c: pf[(f,x)]=F(c,k); s.add(x)
        supp[f]=s
        sh=F(ell[f],k)
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
    return M,ell,T,mu,cyc,pf,supp

def probe(n,adj,side):
    st=struct(n,adj,side)
    if st is None: return []
    M,ell,T,mu,cyc,pf,supp=st
    out=[]
    for (a,b),val in mu.items():
        if val!=0: continue
        if not (T[a]>0 and T[b]>0): continue
        Fu=[f for f in M if pf.get((f,a),0)>0]; Fv=[f for f in M if pf.get((f,b),0)>0]
        Uu=set().union(*[supp[f] for f in Fu]) if Fu else set()
        Uv=set().union(*[supp[f] for f in Fv]) if Fv else set()
        union=Uu|Uv
        out.append((T[a]+T[b]<=len(union), T[a]<=len(Uu), T[b]<=len(Uv), len(union)<=n))
    return out

if __name__=="__main__":
    cu=bu=bv=un=tot=0
    for nn in range(10,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            for (c,bU,bV,u) in probe(info['n'],info['adj'],info['side']):
                tot+=1; cu+=c; bu+=bU; bv+=bV; un+=u
    print(f"loads-cut both-pos zero-mu (N=10,11): total={tot}")
    print(f"  (CU) T(u)+T(v) <= |U_u cup U_v| : {cu}/{tot}")
    print(f"  (BU) T(u) <= |U_u| : {bu}/{tot}    T(v) <= |U_v| : {bv}/{tot}")
    print(f"  |U_u cup U_v| <= N : {un}/{tot}")
    # all connected cuts N<=9
    cu2=bu2=tot2=0
    for nn in [8,9]:
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj=[set() for _ in range(n)]
            for x,y in E: adj[x].add(y); adj[y].add(x)
            for mask in range(1<<(n-1)):
                side=[(mask>>i)&1 for i in range(n)]
                if not Bconn(n,adj,side): continue
                for (c,bU,bV,u) in probe(n,adj,side):
                    tot2+=1; cu2+=c; bu2+=bU
    print(f"ALL conn cuts N<=9 both-pos zero-mu: total={tot2} (CU)={cu2}/{tot2} (BU)={bu2}/{tot2}")
