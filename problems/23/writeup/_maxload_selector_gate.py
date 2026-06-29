"""Exact-gate Codex's MAX-LOAD SELECTOR (block 174): for each interval-Hall failure at I=[a,b] of unique row f,
let m=max_{i in [a,b]} d_i (d_i=S(x_i)-1), H={x_i: d_i=m}. Test:
  STRONG: EVERY x in H has a cut-tight, B-connected, Gamma-decreasing singleton flip.
  WEAK:   AT LEAST ONE x in H does.
Battery: k-chord family k=3,6,9,12 chord-len 5,7. Exact. Reports failures of each version."""
from fractions import Fraction as F
from _h import Bconn, bdist_restr
from _satzmu_conn import struct_for_side

def gamma_of(n,adj,s):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]; G=0
    for (u,v) in M:
        d=bdist_restr(adj,s,u,v)
        if d<0: return None
        G+=(d+1)**2
    return G
def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])
def kchord(k, clen=4):
    pend=clen*k; E=[(i,i+1) for i in range(pend)]
    nint=pend+1; ext=list(range(pend+1, pend+1+nint)); det=[0]+ext+[pend]
    for a,b in zip(det,det[1:]): E.append((min(a,b),max(a,b)))
    for j in range(k): E.append((clen*j, clen*j+clen))
    E.append((0,pend))
    return pend+1+nint, sorted(set((min(a,b),max(a,b)) for a,b in E))

def descends(n,adj,s,x,base_cut,G0):
    s2=s[:]; s2[x]^=1
    if cutsize(n,adj,s2)!=base_cut or not Bconn(n,adj,s2): return False
    g2=gamma_of(n,adj,s2)
    return g2 is not None and g2<G0

def check(n,adj,s,acc):
    base_cut=cutsize(n,adj,s); G0=gamma_of(n,adj,s)
    if G0 is None: return
    st=struct_for_side(n,adj,s)
    if st is None: return
    M,ell,T,mu,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        dvec=[S[v]-1 for v in P_f]
        rest=[v for v in range(n) if v not in Pset]; par={v:v for v in rest}
        def find(x):
            while par[x]!=x: par[x]=par[par[x]]; x=par[x]
            return x
        for u in rest:
            for w in adj[u]:
                if w not in Pset and s[u]!=s[w]: par[find(u)]=find(w)
        cd={}
        for v in rest: cd.setdefault(find(v),set()).add(v)
        comps=[]
        for r,C in cd.items():
            A=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
            if A: comps.append((min(A),max(A),len(C)))
        for a in range(L):
            for b in range(a,L):
                dem=sum(dvec[i] for i in range(a,b+1))
                cap=sum(c for (lo,hi,c) in comps if not (hi<a or lo>b))
                if dem<=cap: continue
                acc['fail']+=1
                m=max(dvec[i] for i in range(a,b+1))
                H=[P_f[i] for i in range(a,b+1) if dvec[i]==m]
                desc=[descends(n,adj,s,x,base_cut,G0) for x in H]
                if not any(desc): acc['weakfail']+=1
                if not all(desc): acc['strongfail']+=1
                if (not all(desc)) and acc['first'] is None:
                    acc['first']=(f,(a,b),str(m),H,desc)
    return

if __name__=="__main__":
    print("=== MAX-LOAD SELECTOR gate (block 174): max-d_i vertex in failing interval descends (exact) ===",flush=True)
    acc={'fail':0,'weakfail':0,'strongfail':0,'first':None}
    for clen in (4,6):
        for k in (3,6,9,12):
            n,E=kchord(k,clen); adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            s=[v%2 for v in range(n)]
            check(n,adj,s,acc)
    print(f"  total interval-Hall failures = {acc['fail']}",flush=True)
    print(f"  WEAK (no max-load vertex descends) failures = {acc['weakfail']}",flush=True)
    print(f"  STRONG (some but not all max-load descend) failures = {acc['strongfail']}",flush=True)
    print(f"  === {'OBSTRUCTION: '+str(acc['first']) if acc['first'] else 'EVERY max-load vertex in every failing interval has a Gamma-descent flip (STRONG holds)'} ===",flush=True)
