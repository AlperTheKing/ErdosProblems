"""Exact-gate Codex's SWITCH-DESCENT bridge (block 172) -- the gamma-minimality bridge for interval Hall.
For a connected-B MAX cut (not nec. gamma-min), if a unique row f has an interval [a,b] with interval-Hall
failure (sum_{[a,b]} d_i > cap), then SOME switch W in the family {singleton {x_i}; path-interval {x_a..x_b};
path-interval + off-path components with span contained in [a,b]} keeps the cut a connected-B MAX cut and strictly
DECREASES Gamma=sum_f ell(f)^2. If this holds, gamma-min cuts cannot have interval-Hall failure => UPO.
Battery: GPT-Pro k-chord failure family (k=3->N=26, k=4,5), census N<=10 max cuts. Reports no-descent failures."""
from fractions import Fraction as F
from _h import maxcut_all, Bconn, bdist_restr, dec, GENG
from _satzmu_conn import struct_for_side
import subprocess

def gamma_of(n,adj,s):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and s[u]==s[v]]
    G=0
    for (u,v) in M:
        d=bdist_restr(adj,s,u,v)
        if d<0: return None
        G+=(d+1)**2
    return G

def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])

def kchord(k):
    """path 0..4k, detour 0-(4k+1)-...-(N-1)-(4k) of length>4k, k chords (4j,4j+4) for j=0..k-1 plus (0,4k)."""
    pathend=4*k
    E=[(i,i+1) for i in range(pathend)]
    # detour: need length > 4k (the path). path length = 4k. detour: 0 - a1 - a2 - ... - 4k with > 4k edges.
    # use 4k+1 internal new vertices so detour length = 4k+2 > 4k.
    ext=list(range(pathend+1, pathend+1+(4*k+1)))
    det=[0]+ext+[pathend]
    for a,b in zip(det,det[1:]): E.append((min(a,b),max(a,b)))
    for j in range(k): E.append((4*j,4*j+4))
    E.append((0,pathend))
    E=sorted(set((min(a,b),max(a,b)) for a,b in E))
    n=pathend+1+(4*k+1)
    return n,E

def test_cut(n,adj,s,acc,name):
    if not Bconn(n,adj,s): return
    base_cut=cutsize(n,adj,s); base_G=gamma_of(n,adj,s)
    if base_G is None: return
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
        compinfo=[]
        for r,C in cd.items():
            A=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
            if A: compinfo.append((min(A),max(A),C))
        for a in range(L):
            for b in range(a,L):
                dem=sum(dvec[i] for i in range(a,b+1))
                cap=sum(len(C) for (lo,hi,C) in compinfo if not (hi<a or lo>b))
                if dem<=cap: continue
                acc['fail']+=1
                # switch family
                cands=[]
                for i in range(a,b+1): cands.append(({P_f[i]},'singleton'))
                cands.append((set(P_f[a:b+1]),'pathint'))
                W=set(P_f[a:b+1])
                for (lo,hi,C) in compinfo:
                    if a<=lo and hi<=b: W=W|C
                cands.append((W,'pathint+comps'))
                found=None
                for (Wset,lab) in cands:
                    s2=s[:]
                    for v in Wset: s2[v]^=1
                    if cutsize(n,adj,s2)!=base_cut: continue
                    if not Bconn(n,adj,s2): continue
                    g2=gamma_of(n,adj,s2)
                    if g2 is None: continue
                    if g2<base_G: found=(lab, base_G-g2); break
                if found: acc['lab'][found[0]]=acc['lab'].get(found[0],0)+1
                else:
                    acc['nodesc']+=1
                    if acc['first'] is None: acc['first']=(name,''.join(map(str,s)),f,P_f,(a,b),str(dem),cap)
    return

if __name__=="__main__":
    print("=== SWITCH-DESCENT bridge gate (block 172): interval-Hall failure => Gamma-descent switch (exact) ===",flush=True)
    acc={'fail':0,'nodesc':0,'lab':{},'first':None}
    # k-chord failure family: parity cut
    for k in (3,4,5):
        n,E=kchord(k); adj=[set() for _ in range(n)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        s=[v%2 for v in range(n)]
        f0=acc['fail']; nd0=acc['nodesc']
        test_cut(n,adj,s,acc,f"kchord{k}-parity")
        print(f"  kchord k={k} N={n} parity: interval-failures={acc['fail']-f0} no-descent={acc['nodesc']-nd0}",flush=True)
    # census N<=10 connected-B max cuts (expect 0 failures)
    for nn in range(7,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        f0=acc['fail']; nd0=acc['nodesc']; cnt=0
        for g6 in outg:
            n,E=dec(g6); adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            mc=max(cutsize(n,adj,sx) for sx in maxcut_all(n,adj))
            for sx in maxcut_all(n,adj):
                if cutsize(n,adj,sx)==mc: test_cut(n,adj,sx,acc,g6); cnt+=1
        print(f"  census N={nn}: max-cuts={cnt} interval-failures={acc['fail']-f0} no-descent={acc['nodesc']-nd0}",flush=True)
    print(f"\n  TOTAL interval-failures={acc['fail']} NO-DESCENT={acc['nodesc']}",flush=True)
    print(f"  descent switch-label distribution: {acc['lab']}",flush=True)
    print(f"  === {'NO-DESCENT WITNESS: '+str(acc['first']) if acc['first'] else 'EVERY interval-Hall failure has a Gamma-descent switch => gamma-minimality bridge HOLDS'} ===",flush=True)
