"""VERIFY the NO-DESCENT nested-chord witnesses on SMALL layouts (n<=22, exact maxcut_all).
For each layout: build, check tri-free; enumerate ALL connected-B max cuts; for the PARITY cut (if it is a
connected-B GLOBAL max cut) find unique-path interval-Hall failures; then decide:
  (1) is parity a GLOBAL max cut?  (2) is parity GAMMA-MIN among connected-B max cuts?
  (3) does ANY connected-B max cut have Gamma < Gamma(parity)?  (multi-flip descent target)
  (4) does any SINGLE cut-tight Bconn flip lower Gamma?
Decisive: if a parity cut is connected-B GLOBAL max + GAMMA-MIN + IH-failure  => route DEAD.
          if it is global max + IH-failure but NOT gamma-min => only single-flip lemma is weak.
          if it is NOT global max => witness is an ARTIFACT (not reduction-relevant)."""
from fractions import Fraction as F
from _h import maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side

def build(pend, chords):
    E=[(i,i+1) for i in range(pend)]
    nint=pend+1; ext=list(range(pend+1, pend+1+nint)); det=[0]+ext+[pend]
    for a,b in zip(det,det[1:]): E.append((min(a,b),max(a,b)))
    for (a,b) in chords: E.append((min(a,b),max(a,b)))
    E.append((0,pend))
    n=pend+1+nint
    return n, sorted(set((min(a,b),max(a,b)) for a,b in E))
def tri_free(n,adj):
    for u in range(n):
        for v in adj[u]:
            if v>u and (adj[u]&adj[v]): return False
    return True
def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])
def gamma_of(n,adj,s):
    G=0
    for u in range(n):
        for v in adj[u]:
            if v>u and s[u]==s[v]:
                d=bdist_restr(adj,s,u,v)
                if d<0: return None
                G+=(d+1)**2
    return G
def ih_fails(n,adj,s):
    st=struct_for_side(n,adj,s)
    if st is None: return False,None
    M,elld,T,mu,cyc=st
    S=[F(0)]*n
    for g in M:
        kk=len(cyc[g])
        for P in cyc[g]:
            for v in P: S[v]+=F(1,kk)
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
                if dem>cap: return True,(f,(a,b),float(dem),cap)
    return False,None

def analyze(name,pend,chords):
    n,E=build(pend,chords); adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    if not tri_free(n,adj): print(f"  {name} n={n}: NOT triangle-free (skip)",flush=True); return
    if n>23: print(f"  {name} n={n}: too big for exact maxcut (skip)",flush=True); return
    allcuts=maxcut_all(n,adj); mcsize=cutsize(n,adj,list(allcuts[0]))
    s=[v%2 for v in range(n)]
    parity_is_max = cutsize(n,adj,s)==mcsize
    parity_bconn = Bconn(n,adj,s)
    # connected-B max cuts and their Gamma
    cbmax=[list(m) for m in allcuts if Bconn(n,adj,list(m))]
    gammas=[(gamma_of(n,adj,c),c) for c in cbmax]
    gammas=[(g,c) for (g,c) in gammas if g is not None]
    gmin=min(g for g,_ in gammas) if gammas else None
    fails,info=ih_fails(n,adj,s) if (parity_is_max and parity_bconn) else (False,None)
    Gpar=gamma_of(n,adj,s) if (parity_is_max and parity_bconn) else None
    is_gmin = (Gpar is not None and gmin is not None and Gpar==gmin)
    # single cut-tight Bconn flip lowering Gamma
    single=None
    if Gpar is not None:
        for v in range(n):
            s2=s[:]; s2[v]^=1
            if cutsize(n,adj,s2)==mcsize and Bconn(n,adj,s2):
                g2=gamma_of(n,adj,s2)
                if g2 is not None and g2<Gpar: single=v; break
    print(f"  {name} n={n} maxcut={mcsize} #connB-maxcuts={len(cbmax)} : parity_is_GLOBALmax={parity_is_max} "
          f"Bconn={parity_bconn} IH-FAIL={fails} Gamma(parity)={Gpar} gamma_MIN={gmin} parity_is_gmin={is_gmin} "
          f"single-flip-descent={single}",flush=True)
    if fails and is_gmin:
        print(f"     *** ROUTE-DEAD CANDIDATE: parity is connected-B GLOBAL max + GAMMA-MIN + IH-FAIL {info} ***",flush=True)
    elif fails and parity_is_max and not is_gmin:
        print(f"     note: global-max + IH-fail but NOT gamma-min (lower-Gamma max cut exists; single-flip={single}) {info}",flush=True)
    elif fails and not parity_is_max:
        print(f"     note: IH-fail but parity NOT global max => artifact (not reduction-relevant)",flush=True)

if __name__=="__main__":
    print("=== exact verification of nested/overlap NO-DESCENT witnesses (n<=22) ===",flush=True)
    # small nested / overlap layouts (pend chosen so n<=22)
    for name,pend,chords in [
        ("nested-p10",10,[(0,8),(2,6)]),
        ("nested-p10b",10,[(0,6),(2,6)]),
        ("overlap-p10",10,[(0,6),(4,10)]),
        ("nested-p8",8,[(0,6),(2,6)]),
        ("nested-small",8,[(0,4),(2,6)]),
        ("chain-p8",8,[(0,4),(4,8)]),
        ("disjoint-p10",10,[(0,4),(6,10)]),
    ]:
        analyze(name,pend,chords)
